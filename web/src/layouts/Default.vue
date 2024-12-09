<template>
  <div class="layout">
    <header class="header">
      <strong>
        <g-link to="/">{{ $static.metadata.siteName }}</g-link>
      </strong>
    </header>
    <p class="data-info">
      This site operates on historical data, which is updated at regular intervals.
      This latest snapshot was taken on {{ formatDate($static.today.edges[0].node.now) }}.
    </p>
    <nav class="main-nav">
      <g-link class="ledger nav__link" to="/">bot ledger</g-link>
      <g-link class="leaderboards nav__link" to="/leaderboards/">leaderboards</g-link>
      <g-link class="account-search nav__link" to="/accounts/">account search</g-link>
    </nav>
    <main>
      <slot />
    </main>
    <footer class="footer">
      <div>
        Bot is enabled on:
        <ul>
          <li v-for="edge in $static.allSubreddits.edges" :key="edge.node.name">
            <a :href="`https://reddit.com/r/${edge.node.name}`" target="_blank">r/{{ edge.node.name }}</a>
          </li>
        </ul>
      </div>
      <div>
        We welcome donations to <a href="https://polygonscan.com/address/0xreplaceme">0xreplaceme</a> if you want to help support the project!
      </div>
      <ul class="disclaimer">
        <li>The information displayed on this site is for entertainment and transparency purposes only and is based on publicly available Reddit interactions with the tipping bot <a href="https://reddit.com/u/replaceme" target="_blank">u/replaceme</a> service.</li>
        <li>We do not endorse or guarantee the accuracy, reliability, or validity of any transaction or balance shown. Use of the site as well as bot interaction is at your own risk.</li>
        <li>The site does not handle any real-time cryptocurrency transactions or withdrawals. All operations must be conducted through Reddit.</li>
        <li>We are not affiliated with, endorsed by, or in any way connected to Reddit. The information provided is based solely on public data. </li>
        <li>In case of help, concerns, please reach out to u/replaceme via Reddit DM.</li>
      </ul>
      <div>Copyright &#169; {{ thisYear }} replaceme developers</div>
    </footer>
  </div>
</template>

<script>
import moment from 'moment'
export default {
  data() {
    return ({
      thisYear: new Date().getFullYear(),
    })
  },
  metaInfo: {
    viewport: "width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"
  },
  methods: {
  formatDate(a) {
  return moment.unix(a).utc().format('YYYY-MM-DD HH:mm:ss UTC')}
  }
}
</script>

<static-query>
query {
  metadata {
    siteName
  }
  allSubreddits {
    edges {
      node {
      name
      }
    }
  }
  today: allToday{
  edges{
  node{
  now
  }
  }
  }
}
</static-query>

<style scoped lang="scss">
body {
  font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  margin: 0;
  padding: 0;
  line-height: 1.5;
}

.layout {
  max-width: 760px;
  margin: 0 auto;
  padding-left: 20px;
  padding-right: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  height: 5rem;

  a {
    color: black;
  }
}

.data-info {
  min-height: 2rem;
}

.main-nav {
  justify-content: center;
  align-items: center;
  margin-top: 2rem;
  display: flex;
  gap: 0.5rem;
  flex-direction: column;
  text-align: center;

  @media (min-width: 1024px) {
    flex-direction: row;
    align-items: stretch;
  }

  .nav__link {
    width: 100%;
    display: block;
    padding: 0.5rem;
    background: #dadada;
  }
}



footer {
  text-align: center;
}

.disclaimer {
  margin: 1rem;
  text-align:left;
}
</style>
