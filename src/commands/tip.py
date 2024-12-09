from .abstract_command import AbstractCommand
import asyncpraw
import re
from accounting import Accounting
from format_amount import format_amount

TIP_REGEX_PATTERN = re.compile('(?:^|\s+)!tip (\d*\.\d+|\d+)( \S+)?', flags=re.IGNORECASE)
def match_tip_command(text:str):
    match = re.search(TIP_REGEX_PATTERN, text)
    if match:
        amount = match.group(1)
        currency = match.group(2)
        if currency:
            currency = currency.lstrip()
        return [currency,amount]

def _amount_with_decimals(amount_str: str, decimals: int) -> int:
    amount_str_split = amount_str.split('.')
    integer_part = amount_str_split[0]
    if len(amount_str_split) ==1 :
        # no decimal part.
        return int(amount_str + ('0' * decimals))
    else:
        decimal_part = amount_str_split[1]
        decimal_part = decimal_part.ljust(decimals,'0')[:decimals]

        if integer_part == '':
            int(decimal_part)
        else:
            return int(f"{integer_part}{decimal_part}")


class TipCommand(AbstractCommand):
    
    def __init__(self, reddit: asyncpraw.Reddit, sub_name:str, bot_name: str, default_currency_shortname: str, accounting: Accounting):
        super().__init__(reddit,sub_name, bot_name)
        self._accounting = accounting
        self._default_currency_shortname = default_currency_shortname

    async def handle_comment(self, comment: asyncpraw.models.Comment):
        if (tip := match_tip_command(comment.body)) is not None:
            await comment.author.load()                  
            author_name = comment.author.name
            if author_name == self.bot_name:
                return True # bot cant tip.
            
            parent = await comment.parent()
            await parent.load()
            await parent.author.load()
            parent_author_name = parent.author.name

            if author_name == parent_author_name:
                await comment.reply("You cannot tip yourself.")
            elif parent_author_name == self.bot_name:
                await comment.reply("Thanks, but no funds were transferred: I don't take tips!")
            else:
                [short_name, amount] = tip
                if not short_name:
                    short_name = self._default_currency_shortname
                short_name = short_name.upper()

                is_ghat = False
                # workaround for ghat tips
                if short_name == "GHAT" or short_name == "GHATS":
                    short_name = "GODL"
                    is_ghat = True

                currency = await self._accounting.find_currency_by_short_name(short_name=short_name, subreddit_name=self.sub_name)
                if currency is not None:
                    if is_ghat:
                        amount = _amount_with_decimals(amount, 10) # godl has 18 decimals so ghat has 10
                    else:
                        amount = _amount_with_decimals(amount, currency.decimals)
                    if amount == 0:
                        # Lets not even bother replying to trolls like these lol
                        return True # command handled
                    try:
                        print(f"{author_name}, {parent_author_name}, {currency.contract_address}, {amount}")
                        success = await self._accounting.transfer(author_name, parent_author_name, currency.contract_address, amount)
                        if success:
                            if is_ghat:
                                await comment.reply(f"{author_name} has tipped {parent_author_name} {format_amount(amount, 10)} ghat✨ (equal to {format_amount(amount, currency.decimals)} GODL{currency.emoji})!")
                            else:
                                await comment.reply(f"{author_name} has tipped {parent_author_name} {format_amount(amount, currency.decimals)} {short_name}{currency.emoji}!")
                        else:
                            await comment.reply(f"I am sorry, your tip did not go through due to insufficient funds. You can check your !balance to see how much you can tip others.")
                    except Exception as e:
                        await comment.reply(f"I am sorry, your tip did not go through. Something went wrong on my side.")
                        raise e
                else:
                    await comment.reply(f"Sorry, the currency {short_name} is not supported on this sub.")

            return True # command handled
        else:
            return False