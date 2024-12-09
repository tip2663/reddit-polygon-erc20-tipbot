import os
import aiomysql

async def run(conn : aiomysql.Connection):
    async with conn.cursor() as cursor:
        # bitcone
        await cursor.execute("""
            INSERT INTO evm_currency (contract_address, chain, name, short_name, emoji)
            VALUES
            ( '0xbA777aE3a3C91fCD83EF85bfe65410592Bdd0f7c', 'polygon', 'BitCone', 'CONE', '🗼');
        """)
        await conn.commit()