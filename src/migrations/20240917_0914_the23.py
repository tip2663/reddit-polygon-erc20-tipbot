import aiomysql

async def run(conn : aiomysql.Connection):
    async with conn.cursor() as cursor:
        # bitcone
        await cursor.execute("""
            INSERT INTO sub_currencies (subreddit, contract_address) VALUES 
            ('the23', '0xbA777aE3a3C91fCD83EF85bfe65410592Bdd0f7c');
        """)
        # godl
        await cursor.execute("""
            INSERT INTO sub_currencies (subreddit, contract_address) VALUES 
            ('the23', '0x7aB889dcEAc8cFa825F51DD75812891DC33801d9');
        """)
        await conn.commit()