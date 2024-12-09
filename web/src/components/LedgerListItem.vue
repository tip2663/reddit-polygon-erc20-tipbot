<template>
    <v-component :is="tagname" class="ledger-item"  :class="[item.withdrawal && 'withdrawal', item.deposit && 'deposit', item.transfer && 'transfer']">
        <template v-if="item.withdrawal">
            <div class="ledger-header">
                <div>
                    withdraw
                </div>
                <div>
                    <a :href="`https://polygonscan.com/tx/${item.withdrawal.tx_hash}`" target="_blank">
                        onchain tx</a>
                </div>
            </div>
            <div class="ledger-content">
                <div class="ledger-from">
                    <g-link :to="`accounts/${item.withdrawal.account.route_slug}/`">{{
                        item.withdrawal.account.reddit_user_name }}</g-link>
                </div>

                <div class="ledger-amount">
                    <Amount :amount="item.withdrawal.amount" :decimals="item.withdrawal.EvmCurrency.decimals">
                    </Amount>
                    <HexEmoji :hex="item.withdrawal.EvmCurrency.emoji_code"></HexEmoji>
                    {{ item.withdrawal.EvmCurrency.short_name }}
                </div>
                <div class="ledger-to">
                    <EthAddress :address="item.withdrawal.withdraw_to_address"></EthAddress>
                </div>
            </div>
            <div class="ledger-footer">
                <div>
                    <g-link v-if="showLink" :to="`/tx/${item.mysqlId}/`" >link</g-link>
                </div>
                <div>
                    {{ formatDate(item.created_at_utc) }}
                </div>
            </div>
        </template>
        <template v-if="item.transfer">
            <div class="ledger-header">
                <div>
                    tipper
                </div>
                <div>
                    tipped
                </div>
            </div>
            <div class="ledger-content">
                <div class="ledger-from">
                    <g-link :to="`accounts/${item.transfer.account[0].route_slug}/`">{{
                        item.transfer.account[0].reddit_user_name }}</g-link>
                </div>
                <div class="ledger-amount">
                    <Amount :amount="item.transfer.amount" :decimals="item.transfer.EvmCurrency.decimals">
                    </Amount>
                    <HexEmoji :hex="item.transfer.EvmCurrency.emoji_code"></HexEmoji>
                    {{ item.transfer.EvmCurrency.short_name }}
                </div>
                <div class="ledger-to">
                    <g-link :to="`accounts/${item.transfer.account[1].route_slug}/`">{{
                        item.transfer.account[1].reddit_user_name }}</g-link>
                </div>
            </div>
            <div class="ledger-footer">
                <div>
                    <g-link v-if="showLink" :to="`/tx/${item.mysqlId}/`">link</g-link>
                </div>
                <div>
                    {{ formatDate(item.created_at_utc) }}
                </div>
            </div>
        </template>
        <template v-if="item.deposit">
            <div class="ledger-header">
                deposit
                <a :href="`https://polygonscan.com/tx/${item.deposit.tx_hash}`" target="_blank">onchain tx</a>
            </div>
            <div class="ledger-content">
                <div class="ledger-from">
                    <EthAddress :address="item.deposit.deposit_from_address"></EthAddress>
                </div>
                <div class="ledger-amount">
                    <Amount :amount="item.deposit.amount" :decimals="item.deposit.EvmCurrency.decimals">
                    </Amount>
                    <HexEmoji :hex="item.deposit.EvmCurrency.emoji_code"></HexEmoji>
                    {{ item.deposit.EvmCurrency.short_name }}
                </div>
                <div class="ledger-to">
                    <g-link :to="`accounts/${item.deposit.account.route_slug}/`">{{
                        item.deposit.account.reddit_user_name }}</g-link>
                </div>
            </div>
            <div class="ledger-footer">
                <div>
                    <g-link v-if="showLink" :to="`/tx/${item.mysqlId}/`">link</g-link>
                </div>
                <div>
                    {{ formatDate(item.created_at_utc) }}
                </div>
            </div>
        </template>
        <div v-if="!item.transfer && !item.withdrawal && !item.deposit" style="background:black;color:white">
            {{ edge }}
        </div>

    </v-component>
</template>

<script setup>
import HexEmoji from '~/components/HexEmoji.vue';
import Amount from '~/components/Amount.vue';
import EthAddress from '~/components/EthAddress.vue';
import moment from 'moment'
const props = defineProps({
    item: Object,
    tagname: {
        type: String,
        required: false,
        default: 'li'
    },
    showLink: {
        type:Boolean,
        required: false,
        default:true
    }
})
const formatDate = a => moment(a).utc().format('YYYY-MM-DD HH:mm:ss UTC')
</script>

<style scoped lang="scss">
a {
    text-decoration: none
}

a.active {
    color: inherit;
    pointer-events: none;
}



.ledger-item {
    display: grid;
    grid-template-columns: subgrid;
    grid-column: span 3;
    white-space: nowrap;

    .ledger-footer {
        grid-column: span 3;
        color: #666;
        font-size: 0.8rem;
        display: flex;
        justify-content: space-between;
    }

    .ledger-header {
        grid-column: span 3;
        color: #666;
        font-size: 0.8rem;
        display: flex;
        justify-content: space-between;
    }

    &.deposit {
        .ledger-header {
            font-weight: bold;
            color: #22aa22;
        }
    }

    &.withdrawal {
        .ledger-header {
            font-weight: bold;
            color: #aa2222;
        }
    }

    .ledger-content {
        grid-column: span 3;
        display: grid;
        grid-template-columns: subgrid;
        padding: 0 0.5rem;

        .ledger-to {
            text-align: right;
        }

        .ledger-amount {
            //flex: 1;
            text-align: right;
            white-space: nowrap;
        }
    }
}
</style>