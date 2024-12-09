import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import aiomysql
import asyncio
import web3
from web3.middleware import async_geth_poa_middleware

from accounting import Accounting
from depositing import Depositing

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

async def main():
    db_host = os.environ['MYSQL_HOST']
    db_user = os.environ['MYSQL_USER']
    db_password = os.environ['MYSQL_PASSWORD']
    db_name = os.environ['MYSQL_DATABASE']

    pool = await aiomysql.create_pool(
            host=db_host, 
            user=db_user, 
            password=db_password, 
            db=db_name
        )
    accounting = Accounting(pool)
    depositing = Depositing(pool, os.environ['BOT_WALLET_ADDRESS'])

    w3 = web3.AsyncWeb3(web3.AsyncWeb3.AsyncHTTPProvider(os.environ['POLYGON_HTTP_RPC_URL']))
    w3.middleware_onion.inject(async_geth_poa_middleware, layer=0) # see http://web3py.readthedocs.io/en/stable/middleware.html#proof-of-authority
    w3.chain_id = 137 # polygon
    pk = os.environ['BOT_WALLET_PRIV_KEY']
    w3.eth.default_account = w3.eth.account.from_key(pk)

    short_name = input('Enter the currency shortname').upper()

    # this is because accounting.currency_by_short_name checks if sub has currency enabled.
    # here we assume the23 to have all tokens enabled.
    subreddit = 'the23'

    currency = await accounting.find_currency_by_short_name(short_name=short_name, subreddit_name=subreddit)
    if currency is None:
        print("currency not found")
        return
    
    amount_str = input(f'Enter the amount of {currency.short_name} to send.')
    amount = _amount_with_decimals(amount_str, currency.decimals)
    address = input('Enter which address to send funds to.')
    if input(f'Im sending {amount} {currency.short_name} to {address} (y)?') != 'y':
        print('ok then not')
        return

    contract_instance = w3.eth.contract(address=currency.contract_address,abi=currency.abi)
    nonce = await w3.eth.get_transaction_count(depositing.get_deposit_address())
    tx = await contract_instance.functions.transfer(address, amount).build_transaction({
        'chainId': 137, #polygon
        'from': depositing.get_deposit_address(),
        'nonce': nonce
        })
    signed_tx = w3.eth.account.sign_transaction(tx,private_key=pk)
    txn_hash = w3.to_hex(w3.keccak(signed_tx.rawTransaction)) 
    print(f'sending {txn_hash}')
    await w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print('waiting for receipt')
    await w3.eth.wait_for_transaction_receipt(txn_hash)
    print('ok')


if __name__ == '__main__':
    print("Feeless direct transfer of tokens from the bot wallet to addresses. Txns are not stored in ledger. Used to fix users that fucked up transfers. Do not fuck up using this or bot funds are lost.")
    asyncio.run(main())