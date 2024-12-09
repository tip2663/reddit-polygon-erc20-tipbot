import os
import traceback
import asyncpraw
import aiomysql
import asyncio
import web3
from web3.middleware import async_geth_poa_middleware

from migrator import run_migrations
from accounting import Accounting
from depositing import Depositing

from commands.balance import BalanceCommand
from commands.tip import TipCommand
from commands.deposit import DepositCommand
from commands.finalize_deposit import FinalizeDepositCommand
from commands.register import RegisterCommand
from commands.withdraw import WithdrawCommand

async def run_bot_on_sub(reddit: asyncpraw.Reddit, sub_name: str, currency_shortname:str, accounting: Accounting, depositing: Depositing, w3: web3.AsyncWeb3, pk:str):
    assert len(sub_name) > 0
    sub = await reddit.subreddit(sub_name)
    bot_name = os.environ["BOT_NAME"]

    cmd_balance = BalanceCommand(reddit=reddit, sub_name=sub_name, bot_name=bot_name, accounting=accounting)
    cmd_tip = TipCommand(reddit=reddit, sub_name=sub_name, bot_name=bot_name, accounting=accounting, default_currency_shortname=currency_shortname)
    cmd_deposit = DepositCommand(reddit=reddit, sub_name=sub_name, bot_name=bot_name, depositing=depositing, accounting=accounting, default_currency_shortname=currency_shortname)
    cmd_finalize_deposit = FinalizeDepositCommand(reddit=reddit, sub_name=sub_name, bot_name=bot_name, depositing=depositing, accounting=accounting, w3=w3)
    cmd_register = RegisterCommand(reddit=reddit, sub_name=sub_name, bot_name=bot_name,accounting=accounting)
    cmd_withdraw = WithdrawCommand(reddit=reddit, sub_name=sub_name, bot_name=bot_name, accounting=accounting,default_currency_shortname=currency_shortname, w3=w3, depositing=depositing, pk=pk)
    handler_chain = cmd_balance(cmd_tip)(cmd_deposit)(cmd_finalize_deposit)(cmd_register)(cmd_withdraw)

    async def comments():
        async for comment in sub.stream.comments(skip_existing=True):
            try:
                await handler_chain.comment(comment)
            except Exception as e:
                print('[ERR] comments stream ',e,comment)
                traceback.print_exc()

    print(f"Listening on r/{sub_name} with default currency {currency_shortname}.")
    await comments()

async def main():
    await run_migrations()

    client_id = os.environ['CLIENT_ID']
    client_secret = os.environ['CLIENT_SECRET']
    refresh_token = os.environ['REFRESH_TOKEN']
    user_agent = os.environ['USER_AGENT'] 

    db_host = os.environ['MYSQL_HOST']
    db_user = os.environ['MYSQL_USER']
    db_password = os.environ['MYSQL_PASSWORD']
    db_name = os.environ['MYSQL_DATABASE']

    reddit = asyncpraw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=refresh_token,
        user_agent=user_agent)
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
    subs_currencies = [ tuple(sub_currency.split(':')) for sub_currency in os.environ['ENABLED_SUBS'].split(',')]

    watchers = [run_bot_on_sub(reddit, subreddit, currency_shortname, accounting, depositing, w3, pk) for (subreddit, currency_shortname) in subs_currencies]
    await asyncio.gather(*watchers)


if __name__ == '__main__':
    asyncio.run(main())
