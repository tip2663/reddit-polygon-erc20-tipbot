# 🌟 Polygon tipping bot for reddit

> MIT License, use at your own risk. No warranty whatsoever. Especially theres' no covering for lost funds or exposed private keys.
> We recommend to run this project on isolated hardware to keep the private keys from being sniffed.

Furthermore, Running this bot requires expert knowledge of docker, python and SQL.

This project is a Reddit bot designed to facilitate cryptocurrency transactions directly within Reddit threads. It leverages various commands to interact with users, allowing them to check balances, deposit funds, register, tip other users, and withdraw funds. The bot is built using Python and runs within a Docker environment, connecting to a MariaDB database for transaction and user data storage.

## 📚 Table of Contents

1. [Software Architecture](#software-architecture)
2. [Setup Instructions](#setup-instructions)
3. [Environment Variables](#environment-variables)
4. [Database Migration System](#database-migration-system)
5. [Bot Commands](#bot-commands)
6. [Running the Bot](#running-the-bot)
7. [Adding new currencies on subreddits and their tokens](#adding-new-currencies-on-subreddits-and-their-tokens)
8. [Web frontend](#web-frontend)


## 🏗️ Software Architecture

The bot is structured into several key components:

- **Commands**: These are the user-facing operations that can be triggered by Reddit comments.
- **Accounting**: Handles the balance and transaction records for users.
- **Depositing**: Manages the process of depositing cryptocurrency into the bot's wallet.
- **Database**: A MariaDB instance is used to store user and transaction data.
- **Web3 Integration**: The bot interacts with the Polygon blockchain using Web3.py.

The bot listens for specific commands in Reddit comments, processes these commands, interacts with the blockchain and database, and responds to the user accordingly.

## 🛠️ Setup Instructions

1. **Clone the Repository**:
    ```sh
    git clone https://github.com/your-repo/your-bot-repo.git
    cd your-bot-repo
    ```

2. **Create `.env` File**:
    Create a `.env` file in the root directory and populate it with the necessary environment variables (see below).

3. **Build and Run with Docker Compose**:
    ```sh
    docker-compose up --build
    ```

## 🌐 Environment Variables

Create a `.env` file in the root of your project directory with the following variables:

```env
# these are for your reddit bot.
CLIENT_ID=your-client-id
CLIENT_SECRET=your-client-secret
REFRESH_TOKEN=your-refresh-token
USER_AGENT=some-user-agent

# we need a polygon rpc provider such as alchemy.
POLYGON_HTTP_RPC_URL=https://some-polygon-mainnet-rpc.example.com
BOT_WALLET_PRIV_KEY=your-private-key
BOT_WALLET_ADDRESS=your-wallet-address

# we need the bot name such that it does not react to its own commands and rejects tips to it.
BOT_NAME=your-bot-name
ENABLED_SUBS=somesub:CONE,anothersub:CONE # read note below

# these are for the generated ledger website deployment. You don't need them if you don't run the web container.
SURGE_TOKEN=replaceme
SURGE_DOMAIN=replaceme
```

The `ENABLED_SUBS` environment variable maps the 'native' token using their shortname to a sub. Note that the token must be enabled on the sub also for this to work (see section 7.).  The format is `<subreddit>:<currency shortname>`. Note that the currency shortname must be registered in the `evm_currency` SQL table. The bot should be added as a moderator to the sub you're listening on to ensure its frequent replies are not flagged as spam.

## 🗄️ Database Migration System

The bot uses a simple database migration system that ensures the schema is up-to-date. When the bot starts, it checks the database schema and applies any necessary migrations to ensure compatibility with the latest bot version. This process is automatic and ensures the database is always in a consistent state.

## 🤖 Bot Commands

The bot listens for specific commands in Reddit comments. Here’s a list of available commands and how users can interact with the bot:

- **`!balance`**: Checks the user's balance.
    - *Usage*: `!balance`
    - *Response*: The bot replies with the user's current balance.

- **`!deposit`**: Provides the user with the deposit address.
    - *Usage*: `!deposit` or `!deposit <currency shortname>`
    - *Response*: The bot replies with the deposit address for the user to send cryptocurrency to.

- **`!register`**: Registers the user with the bot.
    - *Usage*: `!register <0xAddress>`
    - *Response*: The bot replies confirming the user is registered.

- **`!tip`**: Sends a tip to another user.
    - *Usage*: `!tip <amount>` or `!tip <amount> <currency shortname>`
    - *Response*: The bot processes the tip and confirms the transaction.

- **`!withdraw`**: Withdraws funds from the bot to the user's wallet.
    - *Usage*: `!withdraw <amount>` or ``!withdraw <amount> <currency shortname>`
    - *Response*: The bot processes the withdrawal and confirms the transaction.

## 🚀 Running the Bot

Once you have set up the environment variables and the Docker environment, you can run the bot using Docker Compose:

```sh
docker-compose up --build
```

This command builds the Docker images and starts the containers for both the bot and the MariaDB database.

## Adding new currencies on subreddits and their tokens

The process of adding new currencies is currently not as streamlined as one would hope it to be.
In the folder src/migrations you will find all database migrations we've done so far.
In these, you will find that currencies and subreddits are registered directly through the database.
Expert knowledge of SQL is currently required to register new subs and tokens.

The migration files are executed in lexical order upon container start. Them being executed is logged in the `migrations` table which the program ensures is present, such that they are not run twice.

## Web frontend

Within the docker compose environment there is a service called `web` which periodically runs a static site generator from the `web/` directory as an off-chain ledger and automatically publishes it to surge.sh for free deployments.
If you do not wish to have this functionality you can simply remove the service.

# Administration tooling
There's 3 admin tools included right now.

`dbdump.sh` in the project root generates a simple backup tar.gz file of a database snapshot. Recommended to run periodically to mitigate lost funds.

`cli/clear_user_bnalance.py` must be run from within the bot container. Tooling to transfer all of a user's funds to a specified address, taking into account withdrawal fees. This administrative tool is to refund users who wish to opt out of the bot or who otherwise are unable to interact with the bot anymore.

`cli/direct_token_transfer.py` allows for direct sending of tokens out of the bots wallet. Make sure that the bot wallet is covered with all balances even after transfer. The intended usage for this command is to refund failed deposits.
