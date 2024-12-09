<template>
  <Layout>
    <h1>Single interaction</h1>
    <p>Permanent link to a single bot interaction. Suitable for sharing.</p>
    <main>
        <LedgerListItem 
        tagname="div"
        :item="$page.ledger"
        :showLink="false" 
        ></LedgerListItem>
    </main>
  </Layout>
</template>

<script setup>
import LedgerListItem from '~/components/LedgerListItem.vue';
</script>

<style lang="scss" scoped>
main {
margin-top: 1rem;
margin-bottom: 1rem;
display: grid;
grid-template-columns: 1fr 1fr 1fr;
column-gap: 1rem;
overflow-x: auto;
background: #f4f4f4;
}
</style>

<page-query>
query ($path: String!) {
  ledger(path:$path){
        id
        path
        type
        mysqlId
        created_at_utc
        withdrawal {
          amount
          withdraw_to_address
          tx_hash
          EvmCurrency {	
            short_name
            decimals
            emoji_code
          }
          account {
            reddit_user_name
            route_slug
          }
        }
        deposit {
          id
          mysqlId
          amount
          deposit_from_address
          tx_hash
          EvmCurrency {	
            short_name
            decimals
            emoji_code
          }
          account {
            reddit_user_name
            route_slug
          }
        }
        transfer {
          amount
          EvmCurrency {	
            short_name
            decimals
            emoji_code
          }
          from_account_id
          to_account_id
          account {
            mysqlId
            reddit_user_name
            route_slug
          }
        }
      }
    }
</page-query>