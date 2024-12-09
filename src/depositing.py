import aiomysql
from dataclasses import dataclass
from typing import Optional

@dataclass
class PendingDeposit:
    contract_address: str
    from_address: str
    author_id: str

class Depositing:
    def __init__(self, pool, address: str):
        self.pool = pool
        self._address = address
    
    def get_deposit_address(self):
        return self._address

    async def initiate_deposit(self, reply_to_comment_reddit_id: str, comment_author_id: str, comment_id: str, contract_address: str, from_address: str):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    INSERT INTO reddit_deposits (
                        reply_to_comment_reddit_id,
                        reddit_author_id,
                        initiator_comment_reddit_id,
                        contract_address,
                        from_address
                    ) VALUES (%s, %s, %s, %s, %s)
                """, (reply_to_comment_reddit_id, comment_author_id, comment_id, contract_address, from_address))
                await conn.commit()

    async def find_pending_deposit_by_reply_to_id(self, parent_comment_reddit_id: str) -> PendingDeposit | None:
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("""
                    SELECT 
                        contract_address, 
                        from_address,
                        reddit_author_id AS author_id 
                    FROM reddit_deposits
                    WHERE reply_to_comment_reddit_id = %s AND completion_comment_reddit_id IS NULL
                """, (parent_comment_reddit_id,))
                result = await cursor.fetchone()
                if result:
                    return PendingDeposit(**result)
                return None

    async def finalize_deposit(self, reply_to_comment_reddit_id: str, completion_comment_reddit_id: str, completion_tx_hash: str):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    UPDATE reddit_deposits
                    SET 
                        completion_comment_reddit_id = %s,
                        completed_at = CURRENT_TIMESTAMP,
                        completion_tx_hash = %s
                    WHERE 
                        reply_to_comment_reddit_id = %s
                        AND completion_comment_reddit_id IS NULL
                """, (completion_comment_reddit_id, completion_tx_hash, reply_to_comment_reddit_id))
                await conn.commit()
