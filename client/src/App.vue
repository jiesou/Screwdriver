<template>
  <a-config-provider :locale="locale">
    <div class="app-container">
      <RouterView />
    </div>
  </a-config-provider>
</template>

<script setup>
import { RouterView } from 'vue-router'
import zhCN from 'ant-design-vue/es/locale/zh_CN'
import { ref } from 'vue'

const locale = ref(zhCN)
</script>

<style scoped>
.app-container {
  margin: 20px;
  margin: 0 auto;
  padding: 2rem;
  font-weight: normal;
}
</style>
