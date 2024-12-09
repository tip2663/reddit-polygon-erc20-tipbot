<template>
  <Layout>
    <h1>Leaderboards</h1>
    <ul>
      <li v-for="edge in $page.allEvmCurrency.edges">
        <h2>
        <g-link :to="`leaderboards/${edge.node.slug}/`">
            <HexEmoji :hex="edge.node.emoji_code"></HexEmoji>
            {{ edge.node.name }}/{{ edge.node.short_name }}
        </g-link>
        </h2>
      </li>
    </ul>
  </Layout>
</template>
<script>
import HexEmoji from '~/components/HexEmoji.vue'
export default {
  components: {
    HexEmoji
  },
  metaInfo:{
    title:'Leaderboards'
  },
}
</script>
<page-query>
query {
  allEvmCurrency {
    edges {
      node {
        slug
        name
        short_name
        emoji_code
      }
    }
  }
}
</page-query>