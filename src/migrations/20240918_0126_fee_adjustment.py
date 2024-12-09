import aiomysql

async def run(conn : aiomysql.Connection):
    async with conn.cursor() as cursor:
        # all currencies, which right now are godl and cone, have withdrawal fee of 5%
        await cursor.execute("""
            UPDATE evm_currency SET fee_divisor=100, fee_percentage_str='5%';
        """)
        await conn.commit()
