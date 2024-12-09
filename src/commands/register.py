from .abstract_command import AbstractCommand
import asyncpraw
import re
from accounting import Accounting
import web3

REGISTER_REGEX_PATTERN = re.compile('(?:^|\s+)!register (0x[a-f0-9]{40})', flags=re.IGNORECASE)
def match_register_command(text:str):
    match = re.search(REGISTER_REGEX_PATTERN, text)
    if match:
        address = match.group(1)
        return address

class RegisterCommand(AbstractCommand):
    
    def __init__(self, reddit: asyncpraw.Reddit, sub_name:str, bot_name: str, accounting: Accounting):
        super().__init__(reddit,sub_name, bot_name)
        self._accounting = accounting
    

    async def handle_comment(self, comment: asyncpraw.models.Comment):
        if (address := match_register_command(comment.body)) is not None:
            await comment.author.load()
            author_name = comment.author.name
            if author_name == self.bot_name:
                return True # bot cant register.
            if web3.Web3.is_address(address):
                address = web3.Web3.to_checksum_address(address)
                if (other_user := await self._accounting.find_user_by_adress(address)) is not None:
                    await comment.reply(f'That address is already registered to {other_user}. If you believe this to be a mistake, please reach out to modmail.')
                else:
                    await self._accounting.overwrite_user_address(address, author_name)
                    await comment.reply('Your provided address has been registered.')
            else:
                await comment.reply('I do not recognize this as an address.')
            return True
        else:
            return False