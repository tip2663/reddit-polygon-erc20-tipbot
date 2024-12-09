import os
import aiomysql

async def run(conn : aiomysql.Connection):
    async with conn.cursor() as cursor:
        # accounts 
        await cursor.execute("""
            CREATE TABLE account (
                id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                reddit_user_name VARCHAR(255) NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            );
        """)
        # tokens
        await cursor.execute("""
            CREATE TABLE evm_currency (
                contract_address VARCHAR(42) NOT NULL PRIMARY KEY,
                decimals INT NOT NULL DEFAULT 18,
                chain VARCHAR(255) DEFAULT 'polygon',
                name VARCHAR(255) NOT NULL,
                short_name VARCHAR(255) NOT NULL,
                emoji VARCHAR(255) DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            );
        """)
        # balance
        await cursor.execute("""
            CREATE TABLE balance (
                account_id INT NOT NULL,
                contract_address VARCHAR(42) NOT NULL,
                balance DECIMAL(65) UNSIGNED NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (account_id, contract_address),
                FOREIGN KEY (account_id) REFERENCES account(id),
                FOREIGN KEY (contract_address) REFERENCES evm_currency(contract_address)
            );
        """)
        # deposit
        await cursor.execute("""
            CREATE TABLE deposit (
                id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                account_id INT NOT NULL,
                tx_hash VARCHAR(66) NOT NULL UNIQUE,
                token_contract_address VARCHAR(42) NOT NULL,
                deposit_from_address VARCHAR(42) NOT NULL,
                amount DECIMAL(65) UNSIGNED NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES account(id),
                FOREIGN KEY (token_contract_address) REFERENCES evm_currency(contract_address)
            );
        """)
        # withdrawal
        await cursor.execute("""
            CREATE TABLE withdrawal (
                id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                account_id INT NOT NULL,
                tx_hash VARCHAR(66) NOT NULL UNIQUE,
                token_contract_address VARCHAR(42) NOT NULL,
                withdraw_to_address VARCHAR(42) NOT NULL,
                amount DECIMAL(65) UNSIGNED NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES account(id),
                FOREIGN KEY (token_contract_address) REFERENCES evm_currency(contract_address)
            );
        """)
        # transfer
        await cursor.execute("""
            CREATE TABLE transfer (
                id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                from_account_id INT NOT NULL,
                to_account_id INT NOT NULL,
                token_contract_address VARCHAR(42) NOT NULL,
                amount DECIMAL(65) UNSIGNED NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (from_account_id) REFERENCES account(id),
                FOREIGN KEY (to_account_id) REFERENCES account(id),
                FOREIGN KEY (token_contract_address) REFERENCES evm_currency(contract_address)
            );
        """)
        # ledger
        await cursor.execute("""
            CREATE TABLE ledger (
                id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                account_id INT NOT NULL,
                type ENUM('DEPOSIT', 'WITHDRAWAL', 'SEND', 'RECEIVE') NOT NULL,
                deposit_id INT NULL, /* Must be set if type is DEPOSIT */
                withdrawal_id INT NULL, /* Must be set if type is WITHDRAWAL */
                transfer_id INT NULL, /* Must be set if type is either SEND or RECEIVE */
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES account(id),
                FOREIGN KEY (deposit_id) REFERENCES deposit(id),
                FOREIGN KEY (withdrawal_id) REFERENCES withdrawal(id),
                FOREIGN KEY (transfer_id) REFERENCES transfer(id)
            );
        """)

        await cursor.execute("""
            CREATE PROCEDURE Deposit(
                IN p_account_id INT,
                IN p_tx_hash VARCHAR(66),
                IN p_token_contract_address VARCHAR(42),
                IN p_deposit_from_address VARCHAR(42),
                IN p_amount DECIMAL(65) UNSIGNED
            )
            BEGIN
                DECLARE deposit_id INT;
                             
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
                
                COMMIT;
            END
        """)

        # Stored Procedure for Withdrawal
        await cursor.execute("""
            CREATE PROCEDURE Withdraw(
                IN p_account_id INT,
                IN p_tx_hash VARCHAR(66),
                IN p_token_contract_address VARCHAR(42),
                IN p_withdraw_to_address VARCHAR(42),
                IN p_amount DECIMAL(65) UNSIGNED
            )
            BEGIN
                DECLARE withdrawal_id INT;
                DECLARE current_balance DECIMAL(65) UNSIGNED;

                DECLARE EXIT HANDLER FOR SQLEXCEPTION
                BEGIN
                    -- Error encountered, roll back the transaction
                    ROLLBACK;
                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error encountered, transaction rolled back';
                END;

                START TRANSACTION;

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

                -- Insert the withdrawal record
                INSERT INTO withdrawal (account_id, tx_hash, token_contract_address, withdraw_to_address, amount)
                VALUES (p_account_id, p_tx_hash, p_token_contract_address, p_withdraw_to_address, p_amount);

                -- Get the last inserted withdrawal ID
                SET withdrawal_id = LAST_INSERT_ID();

                -- Update the balance
                UPDATE balance SET balance=balance-p_amount WHERE account_id=p_account_id AND contract_address=p_token_contract_address;

                -- Insert a ledger entry
                INSERT INTO ledger (account_id, type, withdrawal_id)
                VALUES (p_account_id, 'WITHDRAWAL', withdrawal_id);

                COMMIT;
            END;
        """)

        # Stored Procedure for Transfer
        await cursor.execute("""
            CREATE PROCEDURE Transfer(
                IN p_from_account_id INT,
                IN p_to_account_id INT,
                IN p_token_contract_address VARCHAR(42),
                IN p_amount DECIMAL(65) UNSIGNED
            )
            BEGIN
                DECLARE transfer_id INT;
                DECLARE sender_balance DECIMAL(65) UNSIGNED;

                DECLARE EXIT HANDLER FOR SQLEXCEPTION
                BEGIN
                    -- Error encountered, roll back the transaction
                    ROLLBACK;
                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error encountered, transaction rolled back';
                END;
                -- Start transaction
                START TRANSACTION;

                -- Check the current balance for sender
                SELECT balance INTO sender_balance
                FROM balance
                WHERE account_id = p_from_account_id AND contract_address = p_token_contract_address
                FOR UPDATE;

                -- If no balance record is found, initialize it to 0
                IF sender_balance IS NULL THEN
                    SET sender_balance = 0;
                END IF;

                -- Raise an error if insufficient funds
                IF sender_balance < p_amount THEN
                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient funds';
                END IF;

                -- Insert the transfer record
                INSERT INTO transfer (from_account_id, to_account_id, token_contract_address, amount)
                VALUES (p_from_account_id, p_to_account_id, p_token_contract_address, p_amount);

                -- Get the last inserted transfer ID
                SET transfer_id = LAST_INSERT_ID();

                -- Update the balance for the sender
                UPDATE balance SET balance=balance-p_amount WHERE account_id=p_from_account_id AND contract_address=p_token_contract_address;


                -- Update the balance for the receiver
                INSERT INTO balance (account_id, contract_address, balance)
                VALUES (p_to_account_id, p_token_contract_address, p_amount)
                ON DUPLICATE KEY UPDATE balance = balance + p_amount;

                -- Insert a ledger entry for the sender
                INSERT INTO ledger (account_id, type, transfer_id)
                VALUES (p_from_account_id, 'SEND', transfer_id);

                -- Insert a ledger entry for the receiver
                INSERT INTO ledger (account_id, type, transfer_id)
                VALUES (p_to_account_id, 'RECEIVE', transfer_id);

                -- Commit transaction
                COMMIT;
            END;
        """)
        await conn.commit()