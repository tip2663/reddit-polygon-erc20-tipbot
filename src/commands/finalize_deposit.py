from .abstract_command import AbstractCommand
import asyncpraw
import re
import web3
from accounting import Accounting, Currency
from depositing import Depositing
from format_amount import format_amount

TRANSFER_TOPIC='0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
TX_REGEX_PATTERN = re.compile('(0x[a-f0-9]{64})', flags=re.IGNORECASE)
def match_finalize_deposit_command(text:str):
    match = re.search(TX_REGEX_PATTERN, text)
    if match:
        tx_hash = match.group(1)
        return tx_hash

class FinalizeDepositCommand(AbstractCommand):
    
    def __init__(self, reddit: asyncpraw.Reddit, sub_name:str, bot_name: str, accounting: Accounting, depositing : Depositing, w3: web3.AsyncWeb3):
        super().__init__(reddit,sub_name, bot_name)
        self._accounting = accounting
        self._depositing = depositing
        self._w3 = w3

    async def handle_comment(self, comment: asyncpraw.models.Comment):
        if (tx_hash := match_finalize_deposit_command(comment.body)) is not None:
            tx_hash = tx_hash.lower()

            await comment.author.load()
            author_name = comment.author.name
            if author_name == self.bot_name:
                return True # bot cant deposit.

            parent = await comment.parent()
            await parent.load()
            parent_id = parent.id

            pending_deposit = await self._depositing.find_pending_deposit_by_reply_to_id(parent_id)

            if pending_deposit is not None:
                currency = await self._accounting.get_currency_by_contract_address(pending_deposit.contract_address)
                if comment.author.id == pending_deposit.author_id:
                    receipt = await self._w3.eth.get_transaction_receipt(tx_hash)
                    if receipt:
                        from_matches =  'from' in receipt and receipt['from'].lower() == pending_deposit.from_address.lower() 
                        to_matches = 'to' in receipt and receipt['to'].lower() == pending_deposit.contract_address.lower()
                        if from_matches and to_matches:
                            if 'logs' in receipt:
                                for log in receipt['logs']:
                                    if 'topics' in log and len(log['topics']) == 3:
                                        [event, from_addr, to_addr] = log['topics']
                                        
                                        if event.hex() == TRANSFER_TOPIC:
                                            from_addr = f"0x{from_addr.hex()[-40:]}"
                                            to_addr = f"0x{to_addr.hex()[-40:]}"
                                            amount = int(log['data'].hex(), 16)
                                            if to_addr.lower() == self._depositing.get_deposit_address().lower():
                                                try:
                                                    await self._accounting.register_deposit(
                                                        reddit_user_name=author_name,
                                                        tx_hash=tx_hash,
                                                        token_contract_address=pending_deposit.contract_address,
                                                        deposit_from_address=web3.Web3.to_checksum_address(from_addr),
                                                        amount=amount)
                                                except Exception as e:
                                                    await comment.reply("There has been an error registering your deposit. This one is on me.")
                                                    raise e

                                                try:
                                                    await self._depositing.finalize_deposit(reply_to_comment_reddit_id=parent_id, completion_comment_reddit_id=comment.id, completion_tx_hash=tx_hash)
                                                except Exception as e:
                                                    await comment.reply("There has been an error finalizing your deposit. This one is on me.")
                                                    raise e
                                                await comment.reply(f"You successfully deposited {format_amount(amount, currency.decimals)} {currency.emoji} {currency.short_name}!")
                        else:
                            await comment.reply("There has been an issue registering the deposit transaction. Please make sure that the transaction is from your registered address into the bot's wallet. If you believe this to be an error, please reach out to modmail.")
            return True
        else:
            return False