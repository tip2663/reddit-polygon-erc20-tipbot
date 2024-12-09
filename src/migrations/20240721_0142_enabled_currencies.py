import aiomysql

async def run(conn : aiomysql.Connection):
    async with conn.cursor() as cursor:
        # bitcone
        await cursor.execute("""
            CREATE TABLE sub_currencies (
                subreddit VARCHAR(255) NOT NULL,
                contract_address VARCHAR(42) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (contract_address) REFERENCES evm_currency(contract_address),
                PRIMARY KEY (subreddit, contract_address)
            );
        """)
        await cursor.execute("""
            INSERT INTO sub_currencies (subreddit, contract_address) VALUES 
            ('tipcoin', '0xbA777aE3a3C91fCD83EF85bfe65410592Bdd0f7c');
        """)
        await conn.commit()