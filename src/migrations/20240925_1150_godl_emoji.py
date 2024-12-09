import aiomysql

async def run(conn : aiomysql.Connection):
    async with conn.cursor() as cursor:
        # godl has star token
        await cursor.execute("""
            UPDATE evm_currency
            SET 
            emoji='⭐️' 
            WHERE contract_address='0x7aB889dcEAc8cFa825F51DD75812891DC33801d9'
        """)
        await conn.commit()
