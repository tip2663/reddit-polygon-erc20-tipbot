<template>
    <Layout>
    <div class="account-search">
        <h1>Account Search</h1>
        <form @submit.prevent="submitSearch" class="search-form">
            <input
                type="text"
                placeholder="Search username..."
                v-model="search"
                class="search" >
            <button>Search</button>
        </form>
    </div>
    </Layout>
</template>

<style >
.search-form {
    display: flex;
    align-items: center;
    margin: 1rem 0;
}
.search-form input {
    flex: 1;
}
</style>

<script>
export default {
    data() {
        return {
            search: ''
        }
    },
    metaInfo:{
        title:'Accounts'
    },
    methods: {
        submitSearch(){
            this.$router.push(`${this.$data.search.toLowerCase()}`)
        }
    }
}
</script>