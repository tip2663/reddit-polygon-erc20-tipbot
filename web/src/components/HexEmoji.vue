<template>
    <span>
        {{ emoji }}
    </span>
</template>
  
<script setup>
import {computed} from 'vue';
const props = defineProps(['hex'])
const emoji = computed(() => decodeURIComponent(`${props.hex}`.match(/.{1,2}/g).map(v => `%${v}`).join('')) )
</script>