import aiomysql

async def run(conn : aiomysql.Connection):
    async with conn.cursor() as cursor:
        await cursor.execute("""
            CREATE OR REPLACE PROCEDURE Withdraw(
                IN p_account_id INT,
                IN p_token_contract_address VARCHAR(42),
                IN p_withdraw_to_address VARCHAR(42),
                IN p_amount DECIMAL(65) UNSIGNED,
                IN p_bot_amount DECIMAL(65) UNSIGNED,
                IN p_bypass_recent_withdrawals BOOLEAN
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

                -- Check for recent withdrawals within the past day if flag is not set to ignore
                IF NOT p_bypass_recent_withdrawals THEN
                    -- Check for pending withdrawals
                    SELECT COUNT(*) INTO pending_withdrawals
                    FROM withdrawal
                    WHERE account_id = p_account_id AND tx_hash IS NULL AND rolled_back <> 1;

                    -- If there are pending withdrawals, raise an error
                    IF pending_withdrawals > 0 THEN
                        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'There is already a pending withdrawal for this account';
                    END IF;
                             
                    -- Check for recent withdrawals within the past day
                    SELECT COUNT(*) INTO recent_withdrawals
                    FROM withdrawal
                    WHERE account_id = p_account_id AND rolled_back <> 1 AND tx_hash IS NOT NULL AND created_at >= NOW() - INTERVAL 1 DAY;

                    -- If there has been a withdrawal in the past day, raise an error
                    IF recent_withdrawals > 0 THEN
                        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Withdrawals are only allowed once per day';
                    END IF;
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
        await conn.commit()