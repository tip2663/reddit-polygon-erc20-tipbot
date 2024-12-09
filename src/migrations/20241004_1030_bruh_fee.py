import aiomysql

async def run(conn : aiomysql.Connection):
    async with conn.cursor() as cursor:
        bruh_address = "0xa52410B8b3Ce16d3f0E607ce8f86b3b4AC30fE2F"
        await cursor.execute("""
            UPDATE evm_currency
            SET
                fee_divisor=100,
                fee_factor=5,
                fee_percentage_str="5%%"
            WHERE
                contract_address=%s;
            """, (bruh_address,))
        await conn.commit()
