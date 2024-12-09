import os
import aiomysql

async def run(conn : aiomysql.Connection):
    async with conn.cursor() as cursor:
        # bitcone
        await cursor.execute("""
            CREATE TABLE reddit_deposits (
                reply_to_comment_reddit_id VARCHAR(255) PRIMARY KEY NOT NULL,
                reddit_author_id VARCHAR(255) NOT NULL,
                initiator_comment_reddit_id VARCHAR(255) NOT NULL,
                from_address VARCHAR(42) NOT NULL,
                contract_address VARCHAR(42) NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                completion_comment_reddit_id VARCHAR(255) NULL,
                completed_at TIMESTAMP DEFAULT NULL,
                completion_tx_hash VARCHAR(66) NULL,
                FOREIGN KEY (contract_address) REFERENCES evm_currency(contract_address)
            );
        """)
        await conn.commit()