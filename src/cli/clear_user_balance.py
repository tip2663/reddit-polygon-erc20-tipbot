import sys
import os

import aiomysql
import asyncio
import web3
from web3.middleware import async_geth_poa_middleware

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from accounting import Accounting

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
    sender_addr = os.environ['BOT_WALLET_ADDRESS']
    w3 = web3.AsyncWeb3(web3.AsyncWeb3.AsyncHTTPProvider(os.environ['POLYGON_HTTP_RPC_URL']))
    w3.middleware_onion.inject(async_geth_poa_middleware, layer=0) # see http://web3py.readthedocs.io/en/stable/middleware.html#proof-of-authority
    w3.chain_id = 137 # polygon
    pk = os.environ['BOT_WALLET_PRIV_KEY']
    w3.eth.default_account = w3.eth.account.from_key(pk)

    username = input('Enter the username to clear balances of: ')

    address = await accounting.find_user_address(username)
    balances = await accounting.get_balances(username)
    for balance in balances:
        if not balance:
            continue
        fee = int((balance.balance * balance.currency.fee_factor) // balance.currency.fee_divisor) # integer math fee
        amount_after_fee = int(balance.balance - fee)
        withdrawal_id = await accounting.begin_withdrawal(username, balance.currency.contract_address, address, int(balance.balance), fee, bypass_recent_withdrawals=True)
        try:
            contract_instance = w3.eth.contract(address=balance.currency.contract_address,abi=balance.currency.abi)
            nonce = await w3.eth.get_transaction_count(sender_addr)
            tx = await contract_instance.functions.transfer(address, amount_after_fee).build_transaction({
                'chainId': 137, #polygon
                'from': sender_addr,
                'nonce': nonce
                })
            signed_tx = w3.eth.account.sign_transaction(tx,private_key=pk)
            txn_hash = w3.to_hex(w3.keccak(signed_tx.rawTransaction)) 
            await w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            await w3.eth.wait_for_transaction_receipt(txn_hash)
            print(f'withdrawal of {balance.balance} {balance.currency.name} complete')
        except Exception as e:
            await accounting.rollback_withdrawal(withdrawal_id)
            print(f'There has been an issue while processing the {balance.currency.name} withdrawal. Funds have been restored.')
            raise e
    print('User balances cleared.')

if __name__ == '__main__':
    asyncio.run(main())