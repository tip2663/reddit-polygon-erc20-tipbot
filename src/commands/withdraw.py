from .abstract_command import AbstractCommand
import asyncpraw
import re
from accounting import Accounting
from depositing import Depositing
import web3
from format_amount import format_amount

WITHDRAW_REGEX_PATTERN = re.compile('(?:^|\s+)!withdraw (\d*\.\d+|\d+)( \S+)?', flags=re.IGNORECASE)
def match_withdraw_command(text:str):
    match = re.search(WITHDRAW_REGEX_PATTERN, text)
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

class WithdrawCommand(AbstractCommand):
    
    def __init__(self, reddit: asyncpraw.Reddit, sub_name:str, bot_name: str, default_currency_shortname: str, accounting: Accounting, depositing:Depositing, w3: web3.AsyncWeb3, pk: str):
        super().__init__(reddit,sub_name, bot_name)
        self._accounting = accounting
        self._default_currency_shortname = default_currency_shortname
        self._w3 = w3
        self._depositing = depositing
        self._pk = pk
    

    async def handle_comment(self, comment: asyncpraw.models.Comment):
        if (deposit := match_withdraw_command(comment.body)) is not None:
            [currency_short_name, amount] = deposit
            if not currency_short_name:
                currency_short_name = self._default_currency_shortname
            currency_short_name = currency_short_name.upper()

            await comment.author.load()
            author_name = comment.author.name
            if author_name == self.bot_name:
                return True # bot cant deposit.
            
            address = await self._accounting.find_user_address(author_name)
            if address is None:
                await comment.reply("Sorry but I do not know your wallet address. You can save your address using !register <0x...>")
                return True

            currency = await self._accounting.find_currency_by_short_name(currency_short_name, self.sub_name)
            if currency is not None:
                fmt_name = ''
                if currency.emoji:
                    fmt_name = f"{currency.emoji}{currency.short_name}"
                else:
                    fmt_name = currency.short_name
                if currency.contract_address and currency.abi:
                    if (remaining_time := await self._accounting.get_remaining_withdrawal_wait_time(author_name)) is None:
                        amount = _amount_with_decimals(amount, currency.decimals)
                        if amount == 0:
                            # Lets not even bother replying to trolls like these lol
                            return True # command handled
                        balance = await self._accounting.get_balance_by_short_name(author_name, currency_short_name)
                        if balance:
                            if balance.balance >= amount:
                                fee = (amount * currency.fee_factor) // currency.fee_divisor # integer math fee
                                amount_after_fee = amount - fee
                                withdrawal_id = await self._accounting.begin_withdrawal(author_name, balance.currency.contract_address, address, amount, fee)
                                try:
                                    contract_instance = self._w3.eth.contract(address=currency.contract_address,abi=currency.abi)
                                    nonce = await self._w3.eth.get_transaction_count(self._depositing.get_deposit_address())
                                    tx = await contract_instance.functions.transfer(address, amount_after_fee).build_transaction({
                                        'chainId': 137, #polygon
                                        'from': self._depositing.get_deposit_address(),
                                        'nonce': nonce
                                        })
                                    signed_tx = self._w3.eth.account.sign_transaction(tx,private_key=self._pk)
                                    txn_hash = self._w3.to_hex(self._w3.keccak(signed_tx.rawTransaction)) 
                                    await self._w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                                    await self._w3.eth.wait_for_transaction_receipt(txn_hash)
                                except Exception as e:
                                    await self._accounting.rollback_withdrawal(withdrawal_id)
                                    await comment.reply(f'There has been an issue while processing your {fmt_name} withdrawal. Your funds have been restored.')
                                    raise e
                                await self._accounting.complete_withdrawal(withdrawal_id=withdrawal_id, txn_hash=txn_hash)
                                await comment.reply(f'You have withdrawn {format_amount(amount_after_fee, currency.decimals)}{fmt_name}. A withdrawal fee of {currency.fee_percentage_str} ({format_amount(fee, currency.decimals)}{fmt_name}) has been applied automatically. [View on polygonscan](https://polygonscan.com/tx/{txn_hash})')
                            else:
                                await comment.reply(f'Sorry, the withdrawal of {format_amount(amount, currency.decimals)}{fmt_name} exceeds your balance. Your balance is {format_amount(balance.balance, currency.decimals)}{fmt_name}.')
                        else:
                            await comment.reply(f'Sorry, the withdrawal of {format_amount(amount, currency.decimals)}{fmt_name} exceeds your balance. Your balance is 0{fmt_name}.')
                    else:
                        hours = remaining_time['hours']
                        minutes = remaining_time['minutes']
                        await comment.reply(f'Sorry, you can only withdraw once a day. Please try again in {hours} hours and {minutes} minutes.')
                else:
                    await comment.reply(f'Sorry, I do not have on-chain data for {fmt_name}')
            else:
                await comment.reply(f'Sorry, the token {currency_short_name} is unsupported on {self.sub_name}!')
            return True
        else:
            return False