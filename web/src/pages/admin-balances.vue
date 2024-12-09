<template>
    <Layout>
        <h1>bot balances</h1>
        <ul>
            <li class="list-header">
                <div>token</div>
                <div class="amount">total held</div>
                <div class="amount">available</div>
            </li>
            <li v-for="edge in $page.allBotBalance.edges">
                <div class="currency">
                    <HexEmoji :hex="edge.node.EvmCurrency.emoji_code"></HexEmoji>
                    {{ edge.node.EvmCurrency.name }}/
                    {{ edge.node.EvmCurrency.short_name }}
                </div>
                <div class="amount">
                    <Amount :amount="edge.node.bot_holdings" :decimals="edge.node.EvmCurrency.decimals"></Amount>
                </div>
                <div class="amount">
                    <Amount :amount="edge.node.bot_balance" :decimals="edge.node.EvmCurrency.decimals"></Amount>
                </div>
            </li>
        </ul>

        <a href="https://polygonscan.com/address/0x7aFe73563Cd6EFB90AaE52201cAECfa35262014d"
           target="_blank">
            Bot wallet 0x7aF...14d
        </a>
    </Layout>
</template>

<script setup>
import Amount from '../components/Amount.vue';
import HexEmoji from '../components/HexEmoji.vue';
</script>

<style lang="scss" scoped>
.list-header {
    font-weight: bold
}
ul {
  padding: 0;
  overflow-x: auto;
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  column-gap: 2rem;

  li {
    white-space: nowrap;
    display: grid;
    grid-template-columns: subgrid;
    grid-column: span 3;
    padding: 0.5rem;
    background: #f4f4f4;
    width: 100%;

    .amount {
        text-align: right;
    }

    &:nth-child(odd) {
        background: #dadada;
    }
  }
}
</style>

<page-query>
{
  allBotBalance {
    edges {
      node {
        id
        bot_holdings
        bot_balance
        EvmCurrency {
          name
          short_name
          decimals
          emoji_code
        }
      }
    }
  }
}
</page-query>