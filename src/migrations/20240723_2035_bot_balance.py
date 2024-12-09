import os
import aiomysql

async def run(conn : aiomysql.Connection):
    async with conn.cursor() as cursor:
        # bitcone
        await cursor.execute("""
            ALTER TABLE evm_currency ADD COLUMN bot_balance DECIMAL(65) UNSIGNED NOT NULL DEFAULT 0;
        """)
        await conn.commit()