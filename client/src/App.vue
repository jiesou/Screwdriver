<template>
  <a-config-provider :locale="locale">
    <a-affix :offset-top=1>
      <a-alert 
        :message="'服务连接状态: ' + (eventBus.serverConnected ? '已连接' : '未连接')" 
        :type="eventBus.serverConnected ? 'success' : 'error'"
        banner
      />
    </a-affix>
    <div class="app-container">
      <RouterView />
    </div>
  </a-config-provider>
</template>

<script setup>
import { RouterView } from 'vue-router'
import zhCN from 'ant-design-vue/es/locale/zh_CN'
import { ref } from 'vue'

import eventBus from './units/eventBus';

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
