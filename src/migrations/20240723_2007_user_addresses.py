import os
import aiomysql

async def run(conn : aiomysql.Connection):
    async with conn.cursor() as cursor:
        # bitcone
        await cursor.execute("""
            ALTER TABLE account ADD COLUMN IF NOT EXISTS eth_address VARCHAR(42) NULL;
        """)
        await cursor.execute("""
            CREATE OR REPLACE PROCEDURE Deposit(
                IN p_account_id INT,
                IN p_tx_hash VARCHAR(66),
                IN p_token_contract_address VARCHAR(42),
                IN p_deposit_from_address VARCHAR(42),
                IN p_amount DECIMAL(65) UNSIGNED
            )
            BEGIN
                DECLARE deposit_id INT;
                DECLARE eth_address VARCHAR(42);

                DECLARE EXIT HANDLER FOR SQLEXCEPTION
                BEGIN
                    -- Error encountered, roll back the transaction
                    ROLLBACK;
                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error encountered, transaction rolled back';
                END;

                START TRANSACTION;

                -- Insert the deposit record
                INSERT INTO deposit (account_id, tx_hash, token_contract_address, deposit_from_address, amount)
                VALUES (p_account_id, p_tx_hash, p_token_contract_address, p_deposit_from_address, p_amount);

                -- Get the last inserted deposit ID
                SET deposit_id = LAST_INSERT_ID();

                -- Upsert the balance
                INSERT INTO balance (account_id, contract_address, balance)
                VALUES (p_account_id, p_token_contract_address, p_amount)
                ON DUPLICATE KEY UPDATE balance = balance + p_amount;

                -- Insert a ledger entry
                INSERT INTO ledger (account_id, type, deposit_id)
                VALUES (p_account_id, 'DEPOSIT', deposit_id);

                -- Check if eth_address is NULL and update it
                SELECT eth_address INTO eth_address
                FROM account
                WHERE id = p_account_id
                FOR UPDATE;

                IF eth_address IS NULL THEN
                    UPDATE account
                    SET eth_address = p_deposit_from_address
                    WHERE id = p_account_id;
                END IF;

                COMMIT;
            END;
        """)
        await conn.commit()