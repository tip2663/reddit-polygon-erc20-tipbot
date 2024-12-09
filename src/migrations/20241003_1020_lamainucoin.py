import aiomysql

async def run(conn : aiomysql.Connection):
    async with conn.cursor() as cursor:
        lic_addr = '0x4Bf8A8B2c3eB55Ca2A15c726e58DD68B9fe96845'
        cone_addr = '0xbA777aE3a3C91fCD83EF85bfe65410592Bdd0f7c'
        godl_addr = '0x7aB889dcEAc8cFa825F51DD75812891DC33801d9'
        # lic for lamainucoin
        await cursor.execute("""
            INSERT INTO sub_currencies (subreddit, contract_address) VALUES 
            ('lamainucoin', %s);
        """, (lic_addr,))
        # cone for lamainucoin
        await cursor.execute("""
            INSERT INTO sub_currencies (subreddit, contract_address) VALUES 
            ('lamainucoin', %s);
        """, (cone_addr,))
        # godl for lamainucoin
        await cursor.execute("""
            INSERT INTO sub_currencies (subreddit, contract_address) VALUES 
            ('lamainucoin', %s);
        """, (godl_addr,))
        await conn.commit()
