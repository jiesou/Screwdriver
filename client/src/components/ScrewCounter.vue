<template>
    <a-typography-title>
      剩余 {{ props.num }}
    </a-typography-title>
</template>

<script setup>
const props = defineProps({
   num: Number
});

</script>

<style scoped>
</style>
