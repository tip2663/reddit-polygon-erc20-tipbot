<template>
  <span class="amount">
    <span class="integer">{{ integerPart }}</span>
    <template v-if="decimalsPreCollapse || collapseAmount">.</template>
    <span class="decimals_pre_collapse">{{ decimalsPreCollapse }}</span>
    <span v-if="collapseAmount" class="decimals_collapse">0<sub class="collapse_amount">{{ collapseAmount }}</sub></span>
    <span class="decimals_post_collapse" v-if="collapseAmount">{{ decimalsPostCollapse }}</span>
  </span>
</template>

<script setup>
import { computed } from 'vue';

// Define the props for amount and decimals
const props = defineProps({
  amount: Number,
  decimals: Number
});

// Function to extract and format the decimal part of the amount
function getDecimalPart(amount, decimals) {
  const amountStr = `${amount}`;
  const amountRev = amountStr.split('').reverse();
  let decimalStr = amountRev.splice(0, decimals).reverse().join('').padStart(decimals, '0');

  // Remove trailing zeros
  decimalStr = decimalStr.replace(/0+$/, '');

  return decimalStr;
}

// Compute the integer part separately
const integerPart = computed(() => {
  const amountStr = `${props.amount}`;
  const amountRev = amountStr.split('').reverse();
  // Reverse back after removing decimal part
  const integerPartStr = amountRev.splice(props.decimals).join('') || '0';
  console.log(integerPartStr)
  const integerPartWithTicksStr = integerPartStr.match(/\d\d?\d?/g).join(' ').split('').reverse().join('')
  return integerPartWithTicksStr;
});

// Compute the separate parts of the decimal section
const decimalsPreCollapse = computed(() => {
  const decimalStr = getDecimalPart(props.amount, props.decimals);
  const leadingZeroMatch = decimalStr.match(/^0+/);

  // If leading zeros are found, return the part before leading zeros
  return leadingZeroMatch && leadingZeroMatch[0].length > 3 ? '' : decimalStr; // Always show first decimal digit if available
});

const collapseAmount = computed(() => {
  const decimalStr = getDecimalPart(props.amount, props.decimals);
  const leadingZeroMatch = decimalStr.match(/^0+/);

  // Check if there are leading zeros and if their count is greater than 3
  if (leadingZeroMatch) {
    const leadingZeroCount = leadingZeroMatch[0].length;
    return leadingZeroCount > 3 ? leadingZeroCount : null; // Collapse only if more than 3 leading zeros
  }

  // No leading zeros to collapse
  return null;
});

const decimalsPostCollapse = computed(() => {
  const decimalStr = getDecimalPart(props.amount, props.decimals);
  const leadingZeroMatch = decimalStr.match(/^0+/);

  // Return the decimal part after the collapsed zeros
  if (leadingZeroMatch) {
    const remainingDecimal = decimalStr.slice(leadingZeroMatch[0].length);
    return remainingDecimal; // Just return the remaining decimal part
  }

  // If no leading zeros, return the full decimal part
  return decimalStr;
});
</script>

<style scoped>
.collapse_amount {
  font-size: 0.7em;
  vertical-align: sub;
}
</style>

