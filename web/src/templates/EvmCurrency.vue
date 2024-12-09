<template>
    <Layout>
        <h1>
          <HexEmoji :hex="$page.allEvmCurrency.edges[0].node.emoji_code"></HexEmoji>
          {{ $page.allEvmCurrency.edges[0].node.name }}/{{ $page.allEvmCurrency.edges[0].node.short_name }}
        </h1>
        <h2>7 days leader board</h2>
        <ul class="leaderboard">
          <LeaderboardItem v-for="edge in $page.allSevenDaysLeaderboard.edges" :item="edge.node" :currency="$page.allEvmCurrency.edges[0].node"></LeaderboardItem>
        </ul>
        <h2>30 days leader board</h2>
        <ul class="leaderboard">
          <LeaderboardItem v-for="edge in $page.allThirtyDaysLeaderboard.edges" :item="edge.node" :currency="$page.allEvmCurrency.edges[0].node"></LeaderboardItem>
        </ul>
        <h2>All time leader board</h2>
        <ul class="leaderboard">
          <LeaderboardItem v-for="edge in $page.allTotalLeaderboard.edges" :item="edge.node" :currency="$page.allEvmCurrency.edges[0].node"></LeaderboardItem>
        </ul>
    </Layout>
</template>

<style lang="scss" scoped>
.leaderboard {
  display: grid;
  grid-template-columns: 0fr 1fr 1fr;
  column-gap: 1rem;
  overflow-x: auto;
  margin-top: 1rem;
  margin-bottom: 1rem;

  li {
      background: #f4f4f4;
      width: 100%;

      &:nth-child(odd) {
          background: #dadada;
      }
  }
}
</style>

<script>
import HexEmoji from '../components/HexEmoji.vue';
import LeaderboardItem from '../components/LeaderboardItem.vue';

export default {
  components:{
    HexEmoji,
    LeaderboardItem
  },
  metaInfo(){
    return {
      title: `${this.$route.params['path'].toUpperCase()} Leaderboard`
    }
  }
}
</script>

<page-query>
query($slug: String!) {
  allEvmCurrency (filter:{slug:{eq:$slug}}) {
    edges {
      node {
        name
        short_name
        emoji_code
        decimals
      }
    }
  }
  allTotalLeaderboard(filter:{slug:{eq:$slug}}, sortBy:"rank", sort:{order:ASC}) {
    edges {
      node {
        id
        slug
        total
        rank
        account {
          reddit_user_name
          route_slug
        }
      }
    }
  }
  allSevenDaysLeaderboard(filter:{slug:{eq:$slug}},sortBy:"rank", sort:{order:ASC}) {
    edges {
      node {
        id
        slug
        total
        rank
        account {
          reddit_user_name
          route_slug
        }
      }
    }
  }
  allThirtyDaysLeaderboard(filter:{slug:{eq:$slug}},sortBy:"rank", sort:{order:ASC}) {
    edges {
      node {
        id
        slug
        total
        rank
        account {
          reddit_user_name
          route_slug
        }
      }
    }
  }
}
</page-query>