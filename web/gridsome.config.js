// This is where project configuration and plugin options are located.
// Learn more: https://gridsome.org/docs/config

const { slugify } = require("gridsome/lib/utils");

// Changes here require a server restart.
// To restart press CTRL + C in terminal and run `gridsome develop`

module.exports = {
  siteName: 'tipbot | offchain-scan ',
  permalinks:{
    slugify(a) {
      // do not slugify
      return a
    }
  },
  plugins: [
  {
      use: 'gridsome-source-mysql',
      options: {
        connection: {
          host: process.env['DB_HOST'],
          port: parseInt(process.env['DB_PORT']),
          user: process.env['DB_USER'],
          password: process.env['DB_PASS'],
          database: process.env['DB_NAME'],
          connectionLimit : 10
        },
        debug: true, // Default false on production
        ignoreImages: true, // Do not download any images
        // imageDirectory: 'sql_images',
        // regex: /()_\d(.(jpg|png|svg|jpeg))/i, // Default false
        queries: [ // required
          {
            name: 'Today',
            sql: `SELECT 1 as id, UNIX_TIMESTAMP() as now`
          },
          {
            name: 'Subreddits',
            sql: `SELECT subreddit AS id, subreddit AS name FROM sub_currencies WHERE subreddit <> 'tipcoin' GROUP BY subreddit `
          },
          {
            name:'EvmCurrency',
            sql: `SELECT *, CONCAT('',HEX(ORD(emoji))) as emoji_code, contract_address as id, LOWER(short_name) as slug FROM evm_currency`,
            route: 'leaderboards/:path',
            path: 'slug',
            subs: [{
              name: 'TotalLeaderboard',
              sql: `SELECT
              CONCAT('total_leaderboard,',e.contract_address,',',t.from_account_id) as id,
              e.contract_address as EvmCurrency_id,
              LOWER(e.short_name) as slug,
              t.from_account_id as account_id,
              CAST(SUM(t.amount) AS CHAR) as total,
              ROW_NUMBER() OVER (ORDER BY SUM(t.amount) DESC) AS rank
              FROM evm_currency e
              INNER JOIN transfer t
              ON t.token_contract_address = e.contract_address
              WHERE e.contract_address=?
              GROUP BY t.from_account_id
              HAVING SUM(t.amount) > 0
              ORDER BY SUM(t.amount) DESC
              LIMIT 10`,
              args(parentRow){
                return parentRow.contract_address
              },
            },
            {
              name: 'SevenDaysLeaderboard',
              sql: `SELECT
              CONCAT('weekly_leaderboard,',e.contract_address,',',t.from_account_id) as id,
              e.contract_address as EvmCurrency_id,
              LOWER(e.short_name) as slug,
              t.from_account_id as account_id,
              CAST(SUM(t.amount) AS CHAR) as total,
              ROW_NUMBER() OVER (ORDER BY SUM(t.amount) DESC) AS rank
              FROM evm_currency e
              INNER JOIN transfer t
              ON t.token_contract_address = e.contract_address
              WHERE e.contract_address=?
                AND t.created_at >= NOW() - INTERVAL 7 DAY
              GROUP BY t.from_account_id
              HAVING SUM(t.amount) > 0
              ORDER BY SUM(t.amount) DESC
              LIMIT 10`,
              args(parentRow){
                return parentRow.contract_address
              },
            },
            {
              name: 'ThirtyDaysLeaderboard',
              sql: `SELECT
              CONCAT('monthly_leaderboard,',e.contract_address,',',t.from_account_id) as id,
              e.contract_address as EvmCurrency_id,
              LOWER(e.short_name) as slug,
              t.from_account_id as account_id,
              CAST(SUM(t.amount) AS CHAR) as total,
              ROW_NUMBER() OVER (ORDER BY SUM(t.amount) DESC) AS rank
              FROM evm_currency e
              INNER JOIN transfer t
              ON t.token_contract_address = e.contract_address
              WHERE e.contract_address=?
                AND t.created_at >= NOW() - INTERVAL 30 DAY
              GROUP BY t.from_account_id
              HAVING SUM(t.amount) > 0
              ORDER BY SUM(t.amount) DESC
              LIMIT 10`,
              args(parentRow){
                return parentRow.contract_address
              }
            }
          ]},
          {
            name: 'Balance',
            sql: `SELECT CONCAT('',balance) as balance, CONCAT(account_id,'-',contract_address) AS id, contract_address as EvmCurrency_id FROM balance`,
          },
          {
            name: 'Transfer',
            sql: `
            SELECT 
              id,
              CONCAT('',amount) as amount,
              CONCAT(from_account_id,',',to_account_id) AS account_ids,
              from_account_id,
              to_account_id,
              token_contract_address as EvmCurrency_id
            FROM transfer`
          },
          {
            name: 'Withdrawal',
            sql: `
              SELECT 
                id,
                account_id,
                tx_hash,
                CONCAT('',amount) as amount,
                withdraw_to_address,
                token_contract_address as EvmCurrency_id
              FROM withdrawal`
          },
          {
            name: 'Deposit',
            sql: `
              SELECT 
                id,
                account_id,
                tx_hash,
                CONCAT('',amount) as amount,
                deposit_from_address,
                token_contract_address as EvmCurrency_id
              FROM deposit`
          },
          {
            name: 'Ledger',
            route: '/tx/:path',
            path: 'mysqlId',
            sql: `SELECT *, created_at AS created_at_utc FROM ledger ORDER BY id ASC`
          },
          {
            name: 'Account',
            route: '/accounts/:path',
            path: 'route_slug',
            sql: `
            SELECT 
              a.id,
              a.reddit_user_name,
              LOWER(a.reddit_user_name) AS route_slug,
              GROUP_CONCAT(CONCAT(b.account_id, '-', b.contract_address)) AS balance_ids,
              GROUP_CONCAT(CONCAT(l.id)) AS ledger_ids
            FROM 
                account a
            LEFT JOIN 
                balance b ON a.id = b.account_id
            LEFT JOIN 
                ledger l ON a.id = l.account_id
            GROUP BY 
                a.id, a.reddit_user_name;
            `
          },
          {
            name: 'BotBalance',
            sql: `
            SELECT 
              e.contract_address as id,
              e.contract_address as EvmCurrency_id,
              CONCAT('', e.bot_balance) as bot_balance,
              CONCAT('', SUM(b.balance) + e.bot_balance)  as bot_holdings
            FROM evm_currency e
            INNER JOIN balance b
            ON b.contract_address = e.contract_address
            GROUP BY b.contract_address
            `
          }
        ]
      }
    }
  ]
}
