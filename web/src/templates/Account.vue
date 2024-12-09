<template>
    <Layout>
        <h1> User {{ $page.account.reddit_user_name }} </h1>

        <section class="balances">
        <h3> Balances </h3>
        <ul>
            <li v-for="balance of $page.account.balance">
                <HexEmoji :hex="balance.EvmCurrency.emoji_code"></HexEmoji>
                <Amount :amount="balance.balance" :decimals="balance.EvmCurrency.decimals"></Amount>
                {{ balance.EvmCurrency.name }}/{{ balance.EvmCurrency.short_name }}
            </li>
        </ul>
        </section>

        <section class="interactions">
        <h3> Interactions </h3>
        <Pager :info="$page.allLedger.pageInfo" />
        <ul>
            <LedgerListItem v-for="edge in $page.allLedger.edges" :item="edge.node" :key="edge.node.id">
            </LedgerListItem>
        </ul>
        <Pager :info="$page.allLedger.pageInfo" />
        </section>
    </Layout>
</template>

<script setup>
import HexEmoji from '~/components/HexEmoji.vue';
import Amount from '~/components/Amount.vue';
import { Pager } from 'gridsome'
import LedgerListItem from '~/components/LedgerListItem.vue';
</script>

<script>
export default {
  metaInfo(){
    return {
    title: this.$page.account.reddit_user_name
    }
  },
}
</script>

<style scoped lang="scss">
.interactions {
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
}
</style>

<page-query>
query($page: Int, $id: ID!) {
  account(id: $id) {
    reddit_user_name
    balance {
      balance
      EvmCurrency {
        name
        decimals
        short_name
        emoji_code
      }
    }
  }
  allLedger(
    perPage: 50
    page: $page
    sort:{by: "mysqlId", order: DESC}
    filter: {
      type: { in: ["SEND", "RECEIVE", "WITHDRAWAL", "DEPOSIT"] }
      account: { id: { eq: $id } }
    }
  ) @paginate {
    pageInfo {
      totalPages
      currentPage
    }
    edges {
      node {
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
  }
}

</page-query>