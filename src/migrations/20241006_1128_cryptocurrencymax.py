import aiomysql

async def run(conn : aiomysql.Connection):
    async with conn.cursor() as cursor:
        tokens = [
            '0xbA777aE3a3C91fCD83EF85bfe65410592Bdd0f7c', # bitcone
            '0x7aB889dcEAc8cFa825F51DD75812891DC33801d9', # godl
            '0x4Bf8A8B2c3eB55Ca2A15c726e58DD68B9fe96845', # lic
            '0xa52410B8b3Ce16d3f0E607ce8f86b3b4AC30fE2F', # bruh
        ]
        for token in tokens:
            await cursor.execute("""
                INSERT INTO sub_currencies (subreddit, contract_address) VALUES 
                ('cryptocurrencymax', %s);
            """, (token,))

        await conn.commit()
