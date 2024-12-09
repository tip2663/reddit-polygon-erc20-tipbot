<template>
  <Layout>
    <h1>Bot Ledger</h1>
    <Pager :info="$page.allLedger.pageInfo" />
    <ul>
      <LedgerListItem 
        v-for="edge in $page.allLedger.edges" 
        :item="edge.node"
        :key="edge.node.id"></LedgerListItem>
    </ul>
    <Pager :info="$page.allLedger.pageInfo" />
  </Layout>
</template>

<script>
import { Pager } from 'gridsome'
import LedgerListItem from '~/components/LedgerListItem.vue';
export default {
  components: {
    Pager,
    LedgerListItem
  },
  metaInfo:{
    title:'Bot Ledger'
  },
}
</script>

<style scoped lang="scss">
nav {
  display: flex;
  justify-content: center;
  gap: 1rem;

  a {
    display: block
  }
}

ul {
  padding: 0;
  overflow-x: auto;
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  column-gap: 2rem;
  li {
      background: #f4f4f4;
      width: 100%;

      &:nth-child(odd) {
          background: #dadada;
      }
  }
}
</style>

<page-query>
query ($page: Int) {
  allLedger(
    perPage: 50,
    page: $page,
    filter:{
      type: {
        in: ["SEND", "WITHDRAWAL", "DEPOSIT"]
      }
    } 
  ) @paginate {
    pageInfo {
      totalPages
      currentPage
    }
    edges {
      node {
        id
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
  }
}
</page-query>