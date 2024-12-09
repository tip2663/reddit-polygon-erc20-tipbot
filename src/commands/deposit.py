from .abstract_command import AbstractCommand
import asyncpraw
import re
from accounting import Accounting
from depositing import Depositing

DEPOSIT_REGEX_PATTERN = re.compile('(?:^|\s+)!deposit( \S+)?', flags=re.IGNORECASE)
def match_deposit_command(text:str):
    match = re.search(DEPOSIT_REGEX_PATTERN, text)
    if match:
        currency = match.group(1)
        if currency:
            currency = currency.lstrip()
        return [currency]

def explorer_address_url(addr:str) -> str:
    return f"https://polygonscan.com/address/{addr}"

class DepositCommand(AbstractCommand):
    
    def __init__(self, reddit: asyncpraw.Reddit, sub_name:str, bot_name: str, default_currency_shortname: str, accounting: Accounting, depositing : Depositing):
        super().__init__(reddit,sub_name, bot_name)
        self._accounting = accounting
        self._depositing = depositing
        self._default_currency_shortname = default_currency_shortname
    

    async def handle_comment(self, comment: asyncpraw.models.Comment):
        if (deposit := match_deposit_command(comment.body)) is not None:
            [currency_short_name] = deposit
            if not currency_short_name:
                currency_short_name = self._default_currency_shortname
            currency_short_name = currency_short_name.upper()

            await comment.author.load()
            author_name = comment.author.name
            if author_name == self.bot_name:
                return True # bot cant deposit.
            
            address = await self._accounting.find_user_address(author_name)
            if address is None:
                await comment.reply('I could not determine your vault address. Please !register <0x...> with your address and try again!')
                return True

            currency = await self._accounting.find_currency_by_short_name(currency_short_name, self.sub_name)
            if currency is not None:
                if currency.contract_address is None:
                    await comment.reply(f'Sorry, I do not have on-chain data for {currency.short_name}')
                    return True
                reply_to_comment = await comment.reply('\n'.join([
                f"Your deposit of [{currency.short_name}]({explorer_address_url(currency.contract_address)}) has been initiated.",
                f"You may now send {currency.short_name} from [your provided address]({explorer_address_url(address)})",
                f"to the [deposit wallet - {self._depositing.get_deposit_address()}]({explorer_address_url(self._depositing.get_deposit_address())}).\n",
                f"Reply with the transaction hash that includes the token transfer to this comment.",
                f"Make sure to reply once your deposit has been made and the transaction is no longer pending.\n",
                f"Notice: a fee of {currency.fee_percentage_str} is placed upon a later !withdraw command.\n",
                f"^(Network congestion and gas fees apply. Make sure that you are sending from the correct blockchain.)"
                ]))
                if reply_to_comment is not None:
                    try:
                        await self._depositing.initiate_deposit(
                            reply_to_comment_reddit_id=reply_to_comment.id,
                            comment_author_id=comment.author.id,
                            comment_id=comment.id,
                            contract_address=currency.contract_address,
                            from_address=address)
                    except Exception as e:
                        await reply_to_comment.delete() # failsafe: dont send instructions if the deposit initiation failed.
                        raise e
            else:
                await comment.reply(f'Sorry, the token {currency_short_name} is unsupported on {self.sub_name}!')
            return True
        else:
            return False