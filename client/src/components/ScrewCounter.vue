<template>
    <a-typography-title>
      剩余 {{ eventBus.counter }}
    </a-typography-title>
</template>

<script setup>
import eventBus from '@/units/eventBus';
import { watchEffect } from 'vue';

watchEffect(() => {
  if (eventBus.counter <= 0) {
    eventBus.restart = !eventBus.restart
  }
});
</script>

<style scoped>
</style>
