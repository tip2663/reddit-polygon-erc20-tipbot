from typing import List
from .abstract_command import AbstractCommand
import asyncpraw
import re
from accounting import Accounting, TokenBalance
from depositing import Depositing
from format_amount import format_amount

BALANCE_REGEX_PATTERN = re.compile('(?:^|\s+)!balance(?:$|\s+)', flags=re.IGNORECASE)
def match_balance_command(text:str):
    match = re.search(BALANCE_REGEX_PATTERN, text)
    if match:
        return True
    else:
        return False

def _format_balances(balances : List[TokenBalance]) -> str:
    msg = 'Your off-chain balances:\n\n'
    msg += '\n\n'.join([
        f"{balance.currency.emoji or ''} {format_amount(balance.balance, balance.currency.decimals)} {balance.currency.short_name.upper()}"
        for balance in balances
        ])
    return msg

class BalanceCommand(AbstractCommand):
    
    def __init__(self, reddit: asyncpraw.Reddit, sub_name:str, bot_name: str, accounting: Accounting):
        super().__init__(reddit,sub_name, bot_name)
        self._accounting = accounting
    
    async def handle_comment(self, comment: asyncpraw.models.Comment):
        if (match_balance_command(comment.body)):
            await comment.author.load()
            author_name = comment.author.name
            if author_name == self.bot_name:
                return True # bot cant fetch their own balance.

            balances = await self._accounting.get_balances(author_name)

            if balances:
                reply = _format_balances(balances)
                await comment.reply(reply)
            else:
                await comment.reply('I do not have record of your off-chain balances. You receive balances by a humble !tip from other users or you can deposit some with !deposit <currency> after a !register <0xyour_address> to enjoy the tipping fun!')
            return True
        else:
            return False