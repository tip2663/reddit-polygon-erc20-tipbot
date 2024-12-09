import os
import aiomysql

async def run(conn : aiomysql.Connection):
    async with conn.cursor() as cursor:
        # bitcone
        await cursor.execute("""
            ALTER TABLE withdrawal ADD COLUMN rolled_back BOOLEAN NOT NULL DEFAULT FALSE;
            ALTER TABLE withdrawal ADD COLUMN fee DECIMAL(65) UNSIGNED NOT NULL DEFAULT 0;
            ALTER TABLE ledger MODIFY COLUMN type ENUM('DEPOSIT', 'WITHDRAWAL', 'SEND', 'RECEIVE', 'WITHDRAWAL_ROLLBACK') NOT NULL;
        """)
        await cursor.execute("""
            CREATE OR REPLACE PROCEDURE Withdraw(
                IN p_account_id INT,
                IN p_token_contract_address VARCHAR(42),
                IN p_withdraw_to_address VARCHAR(42),
                IN p_amount DECIMAL(65) UNSIGNED,
                IN p_bot_amount DECIMAL(65) UNSIGNED
            )
            BEGIN
                DECLARE withdrawal_id INT;
                DECLARE current_balance DECIMAL(65) UNSIGNED;
                DECLARE pending_withdrawals INT;
                DECLARE recent_withdrawals INT;

                DECLARE EXIT HANDLER FOR SQLEXCEPTION
                BEGIN
                    -- Error encountered, roll back the transaction
                    ROLLBACK;
                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error encountered, transaction rolled back';
                END; 
                             
                START TRANSACTION;

                -- Check for pending withdrawals
                SELECT COUNT(*) INTO pending_withdrawals
                FROM withdrawal
                WHERE account_id = p_account_id AND tx_hash IS NULL;

                -- If there are pending withdrawals, raise an error
                IF pending_withdrawals > 0 THEN
                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'There is already a pending withdrawal for this account';
                END IF;

                -- Check for recent withdrawals within the past week
                SELECT COUNT(*) INTO recent_withdrawals
                FROM withdrawal
                WHERE account_id = p_account_id AND tx_hash IS NOT NULL AND created_at >= NOW() - INTERVAL 1 WEEK;

                -- If there has been a withdrawal in the past week, raise an error
                IF recent_withdrawals > 0 THEN
                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Withdrawals are only allowed once per week';
                END IF;

                -- Check the current balance
                SELECT balance INTO current_balance
                FROM balance
                WHERE account_id = p_account_id AND contract_address = p_token_contract_address
                FOR UPDATE;

                -- If no balance record is found, initialize it to 0
                IF current_balance IS NULL THEN
                    SET current_balance = 0;
                END IF;

                -- Raise an error if insufficient funds
                IF current_balance < p_amount THEN
                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient funds';
                END IF;

                -- Insert the withdrawal record with tx_hash as NULL
                INSERT INTO withdrawal (account_id, tx_hash, token_contract_address, withdraw_to_address, amount, fee)
                VALUES (p_account_id, NULL, p_token_contract_address, p_withdraw_to_address, p_amount, p_bot_amount);

                -- Get the last inserted withdrawal ID
                SET withdrawal_id = LAST_INSERT_ID();

                -- Update the balance
                UPDATE balance SET balance = balance - p_amount WHERE account_id = p_account_id AND contract_address = p_token_contract_address;
                             
                -- Insert a ledger entry
                INSERT INTO ledger (account_id, type, withdrawal_id)
                VALUES (p_account_id, 'WITHDRAWAL', withdrawal_id);

                SELECT withdrawal_id;
                COMMIT;
            END;
        """)
        await cursor.execute("""
            CREATE OR REPLACE PROCEDURE CompleteWithdrawal(
                    IN p_withdrawal_id INT,
                    IN p_tx_hash VARCHAR(66)
                )
                BEGIN
                    DECLARE pending_withdrawal INT;

                    DECLARE EXIT HANDLER FOR SQLEXCEPTION
                    BEGIN
                        -- Error encountered, roll back the transaction
                        ROLLBACK;
                        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error encountered, transaction rolled back';
                    END; 

                    START TRANSACTION;

                    -- Check if the withdrawal ID exists and is pending
                    SELECT COUNT(*)
                    INTO pending_withdrawal
                    FROM withdrawal
                    WHERE id = p_withdrawal_id AND tx_hash IS NULL AND rolled_back = FALSE;

                    -- If no matching pending withdrawal is found, raise an error
                    IF pending_withdrawal = 0 THEN
                        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No matching pending withdrawal found';
                    END IF;
                    
                    -- Update the bot balance only if withdrawal succeeded
                    UPDATE evm_currency
                    SET bot_balance = bot_balance + (SELECT fee FROM withdrawal WHERE id = p_withdrawal_id)
                    WHERE contract_address = (SELECT token_contract_address FROM withdrawal WHERE id = p_withdrawal_id);

                    -- Update the withdrawal record with the provided tx_hash
                    UPDATE withdrawal SET tx_hash = p_tx_hash WHERE id = p_withdrawal_id;

                    COMMIT;
                END;
        """)
        await cursor.execute("""
            CREATE OR REPLACE PROCEDURE RollbackWithdrawal(
                IN p_withdrawal_id INT
            )
            BEGIN
                DECLARE pending_withdrawal INT DEFAULT 0;

                DECLARE EXIT HANDLER FOR SQLEXCEPTION
                BEGIN
                    -- Error encountered, roll back the transaction
                    ROLLBACK;
                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error encountered, transaction rolled back';
                END;

                START TRANSACTION;

                -- Check if the withdrawal ID exists and is pending, and retrieve required values
                SELECT COUNT(*)
                INTO pending_withdrawal
                FROM withdrawal
                WHERE id = p_withdrawal_id AND tx_hash IS NULL AND rolled_back = FALSE;

                -- If no matching pending withdrawal is found, raise an error
                IF pending_withdrawal != 1 THEN
                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No matching pending withdrawal found';
                ELSE
                    -- Update the withdrawal record
                    UPDATE withdrawal
                    SET rolled_back = TRUE
                    WHERE id = p_withdrawal_id AND tx_hash IS NULL AND rolled_back = FALSE;

                    -- Reward back the balance
                    UPDATE balance
                    SET balance = balance + (SELECT amount FROM withdrawal WHERE id = p_withdrawal_id)
                    WHERE account_id = (SELECT account_id FROM withdrawal WHERE id = p_withdrawal_id) 
                    AND contract_address = (SELECT token_contract_address FROM withdrawal WHERE id = p_withdrawal_id);

                    -- Insert a ledger entry for the rollback
                    INSERT INTO ledger (account_id, type, withdrawal_id)
                    VALUES (
                      (SELECT account_id FROM withdrawal WHERE id = p_withdrawal_id),
                      'WITHDRAWAL_ROLLBACK',
                      p_withdrawal_id
                    );

                    COMMIT;
                END IF;
            END;
        """)
        await conn.commit()