from dataclasses import dataclass
import datetime
from operator import attrgetter
from typing import List, Optional
import aiomysql

@dataclass
class Currency:
    contract_address: str
    decimals: int
    name: str
    short_name: str
    emoji: Optional[str] = None
    abi: Optional[str] = None
    fee_factor: int = 5
    fee_divisor: int = 1000
    fee_percentage_str: str = '0.5%'


@dataclass
class TokenBalance:
    balance: int
    currency: Currency

    def __repr__(self):
        emoji_str = f" {self.emoji}" if self.emoji else ""
        return f"{self.name} ({self.short_name}{emoji_str}): {self.balance} at address {self.contract_address}"


class Accounting:
    def __init__(self, pool):
        self.pool = pool

    async def _get_or_create_account_id(self, reddit_user_name: str) -> int:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # Start a transaction
                await conn.begin()
                try:
                    await cursor.execute("""
                        INSERT INTO account (reddit_user_name)
                        VALUES (%s)
                        ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id);
                    """, (reddit_user_name,))

                    # Retrieve the ID using LAST_INSERT_ID()
                    await cursor.execute("SELECT LAST_INSERT_ID()")
                    result = await cursor.fetchone()
                    user_id = result[0]

                    # Commit the transaction
                    await conn.commit()
                    return user_id
                except Exception as e:
                    # Rollback in case of error
                    await conn.rollback()
                    raise e
                
    async def get_remaining_withdrawal_wait_time(self, reddit_user_name):
        """
        Returns the remaining wait time for withdrawals in hours, and minutes.
        If no wait time is needed, returns None.
        """
        account_id = await self._get_or_create_account_id(reddit_user_name)
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                SELECT TIMESTAMPDIFF(SECOND, MAX(created_at), NOW()) AS elapsed_seconds
                FROM withdrawal
                WHERE account_id = %s
                AND tx_hash IS NOT NULL
                AND rolled_back = FALSE
                AND created_at >= NOW() - INTERVAL 1 DAY;
            """, (account_id,))
            
            result = await cursor.fetchone()
            
            if result and result[0] is not None:
                elapsed_seconds = result[0]
                wait_time_duration = 86400  # 1 day in seconds
                
                # Calculate the remaining time
                remaining_seconds = wait_time_duration - elapsed_seconds
                
                if remaining_seconds > 0:
                    # Convert remaining seconds to days, hours, minutes
                    hours = remaining_seconds // 3600
                    minutes = (remaining_seconds % 3600) // 60
                    return {
                        'hours': hours,
                        'minutes': minutes
                    }
                else:
                    return None
            else:
                return None

    async def begin_withdrawal(self, reddit_user_name: str, token_contract_address: str, withdraw_to_address: str, amount: int, fee_amount: int, bypass_recent_withdrawals=False) -> int:
        account_id = await self._get_or_create_account_id(reddit_user_name)
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.callproc('Withdraw', (account_id, token_contract_address, withdraw_to_address, amount, fee_amount,bypass_recent_withdrawals))
                (wid,) = await cursor.fetchone()
                return wid
    
    async def complete_withdrawal(self, withdrawal_id: int, txn_hash: str):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.callproc('CompleteWithdrawal', (withdrawal_id, txn_hash))
                await conn.commit()
    
    async def rollback_withdrawal(self, withdrawal_id: int):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.callproc('RollbackWithdrawal', (withdrawal_id,))
                await conn.commit()

    async def register_deposit(self, reddit_user_name: str, tx_hash: str, token_contract_address: str, deposit_from_address: str, amount: int):
        account_id = await self._get_or_create_account_id(reddit_user_name)
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.callproc('Deposit', (account_id, tx_hash, token_contract_address, deposit_from_address, amount))
                await conn.commit()


    async def transfer(self, from_reddit_user_name: str, to_reddit_user_name: str, token_contract_address: str, amount: int) -> bool:
        """
        Returns boolean indicating wether the transfer succeeded.
        """
        from_account_id = await self._get_or_create_account_id(from_reddit_user_name)
        to_account_id = await self._get_or_create_account_id(to_reddit_user_name)
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await cursor.callproc('Transfer', (from_account_id, to_account_id, token_contract_address, amount))
                    await conn.commit()
                    return True
                except aiomysql.OperationalError as e:
                    if e.args[0] == 1644:
                        return False
                    else:
                        raise e
    
    
    async def get_balances(self, reddit_user_name: str) -> List[TokenBalance]:
        account_id = await self._get_or_create_account_id(reddit_user_name)
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    SELECT b.balance, b.contract_address, e.name, e.short_name, e.emoji, e.decimals, e.contract_abi, e.fee_factor, e.fee_divisor, e.fee_percentage_str
                    FROM balance b
                    JOIN evm_currency e ON b.contract_address = e.contract_address
                    WHERE b.account_id = %s;
                """, (account_id,))
                
                rows = await cursor.fetchall()
                balances = [
                    TokenBalance(
                        balance=row[0],
                        currency=Currency(
                            contract_address=row[1],
                            name=row[2],
                            short_name=row[3],
                            emoji=row[4],
                            decimals=row[5],
                            abi=row[6],
                            fee_factor=row[7],
                            fee_divisor=row[8],
                            fee_percentage_str=row[9]
                        )
                    )
                    for row in rows
                ]
                # Sort balances by token name
                sorted_balances = sorted(balances, key=attrgetter('currency.short_name'))
                return sorted_balances
    
    async def find_user_address(self,reddit_user_name:str) -> str | None:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                        SELECT eth_address FROM account WHERE reddit_user_name = %s;
                    """, (reddit_user_name,))
                row = await cursor.fetchone()
                if row:
                    return row[0]
                else:
                    return None
    
    async def find_user_by_adress(self,address:str) -> str | None:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                        SELECT reddit_user_name FROM account WHERE eth_address = %s;
                    """, (address,))
                row = await cursor.fetchone()
                if row:
                    return row[0]
                else:
                    return None

    async def overwrite_user_address(self,new_address:str, reddit_user_name:str):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                        INSERT INTO account (reddit_user_name, eth_address)
                        VALUES (%s, %s)
                        ON DUPLICATE KEY UPDATE eth_address = VALUES(eth_address);
                    """, (reddit_user_name,new_address))
                await conn.commit()

    async def get_balance_by_short_name(self, reddit_user_name:str, short_name:str) -> TokenBalance | None:
        account_id = await self._get_or_create_account_id(reddit_user_name)
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    SELECT b.balance, b.contract_address, e.name, e.short_name, e.emoji, e.decimals, e.contract_abi, e.fee_factor, e.fee_divisor, e.fee_percentage_str
                    FROM balance b
                    JOIN evm_currency e ON b.contract_address = e.contract_address
                    WHERE b.account_id = %s AND e.short_name = %s;
                """, (account_id,short_name))
                
                row = await cursor.fetchone()
                if row:
                    balance = TokenBalance(
                        balance=row[0],
                        currency=Currency(
                            contract_address=row[1],
                            name=row[2],
                            short_name=row[3],
                            emoji=row[4],
                            decimals=row[5],
                            abi=row[6],
                            fee_factor=row[7],
                            fee_divisor=row[8],
                            fee_percentage_str=row[9]
                        )
                    )
                    return balance
                else:
                    return None
    
    async def find_currency_by_short_name(self, short_name: str, subreddit_name: str) -> Currency | None:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    SELECT e.contract_address, e.name, e.short_name, e.emoji, e.decimals, e.contract_abi, e.fee_factor, e.fee_divisor, e.fee_percentage_str
                    FROM evm_currency e
                    INNER JOIN sub_currencies s ON e.contract_address = s.contract_address
                    WHERE e.short_name = %s AND s.subreddit = %s;
                """, (short_name,subreddit_name))
                
                row = await cursor.fetchone()
                if row:
                        return Currency(
                            contract_address=row[0],
                            name=row[1],
                            short_name=row[2],
                            emoji=row[3],
                            decimals=row[4],
                            abi=row[5],
                            fee_factor=row[6],
                            fee_divisor=row[7],
                            fee_percentage_str=row[8]
                        )
                else:
                    return None

    async def get_currency_by_contract_address(self,contract_address:str) -> Currency | None:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    SELECT e.contract_address, e.name, e.short_name, e.emoji, e.decimals, e.contract_abi, e.fee_factor, e.fee_divisor, e.fee_percentage_str
                    FROM evm_currency e
                    WHERE e.contract_address = %s;
                """, (contract_address,))
                
                row = await cursor.fetchone()
                if row:
                        return Currency(
                            contract_address=row[0],
                            name=row[1],
                            short_name=row[2],
                            emoji=row[3],
                            decimals=row[4],
                            abi=row[5],
                            fee_factor=row[6],
                            fee_divisor=row[7],
                            fee_percentage_str=row[8]
                        )
                else:
                    return None