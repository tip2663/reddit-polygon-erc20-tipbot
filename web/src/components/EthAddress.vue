<template>
    <span>
        {{ formatted }}
    </span>
</template>
<script setup>
import {computed} from 'vue';
const props = defineProps(['address'])

const formatted = computed(() => {
    const addr = `${props.address}`
    return `${addr.slice(0,5)}...${addr.slice(addr.length - 5, addr.length-1)}`
})
</script>