import aiomysql

async def run(conn : aiomysql.Connection):
    async with conn.cursor() as cursor:
        # bitcone, integer math for 0.5% fee
        await cursor.execute("""
            ALTER TABLE evm_currency ADD COLUMN fee_factor INT UNSIGNED NOT NULL DEFAULT 5;
            ALTER TABLE evm_currency ADD COLUMN fee_divisor INT UNSIGNED NOT NULL DEFAULT 1000;
            ALTER TABLE evm_currency ADD COLUMN fee_percentage_str VARCHAR(255) NOT NULL DEFAULT "0.5%";
        """)
        await conn.commit()