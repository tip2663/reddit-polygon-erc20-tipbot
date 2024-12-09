import aiomysql

async def run(conn : aiomysql.Connection):
    async with conn.cursor() as cursor:
        bruh_address = "0xa52410B8b3Ce16d3f0E607ce8f86b3b4AC30fE2F"
        tokens = [
            '0xbA777aE3a3C91fCD83EF85bfe65410592Bdd0f7c', # bitcone
            '0x7aB889dcEAc8cFa825F51DD75812891DC33801d9', # godl
            '0x4Bf8A8B2c3eB55Ca2A15c726e58DD68B9fe96845', # lic
            bruh_address
        ]
        for token in tokens:
            await cursor.execute("""
                INSERT INTO sub_currencies (subreddit, contract_address) VALUES 
                ('cryptofans', %s);
            """, (token,))

        other_subs = ['the23','toesling','lamainucoin','animeavatartrading']
        for sub in other_subs:
            await cursor.execute("""
                INSERT INTO sub_currencies (subreddit, contract_address) VALUES 
                (%s, %s);
            """, (sub,bruh_address))
        await conn.commit()
