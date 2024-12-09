<template>
    <li>
        <div class="rank">#{{ item.rank }}</div>
        <div class="user">
            <g-link :to="`accounts/${item.account.route_slug}/`">
                {{ item.account.reddit_user_name }}
            </g-link>
        </div>
        <div class="total">
            <Amount :amount="item.total" :decimals="currency.decimals"></Amount>
            <HexEmoji :hex="currency.emoji_code"></HexEmoji>
            {{ currency.short_name }}
        </div>
    </li>
</template>

<style lang="scss" scoped>
li {
    display: grid;
    grid-template-columns: subgrid;
    grid-column: span 3;
    white-space: nowrap;
    padding: 0.5rem;

    .total {
        text-align: right;
    }
}
</style>

<script setup>
import Amount from './Amount.vue';
import HexEmoji from './HexEmoji.vue';
const props = defineProps(['item', 'currency'])
</script>