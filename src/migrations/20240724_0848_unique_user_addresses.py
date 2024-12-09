import os
import aiomysql

async def run(conn : aiomysql.Connection):
    async with conn.cursor() as cursor:
        # bitcone
        await cursor.execute("""
            ALTER TABLE account MODIFY COLUMN eth_address VARCHAR(42) UNIQUE NULL;
        """)
        await conn.commit()