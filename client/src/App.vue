<template>
  <a-config-provider :locale="zhCN">
    <a-layout class="layout">
      <a-affix :offset-top=1>
        <div style="background-color: aliceblue;">
          <a-alert :message="'服务连接状态: ' + (eventBus.serverConnected ? '已连接' : '正在连接……')"
            :type="eventBus.serverConnected ? 'success' : 'error'" banner />

          <a-space>
            <!-- 服务连接启停 -->
            <a-button type="primary" :danger="eventBus.movingStreamer.eventState.isDoing"
              @click="eventBus.movingStreamer.eventState.isDoing ? handleStopMoving() : handleMoving()"
              :loading="eventBus.movingStreamer.eventState.loading">
              {{ eventBus.movingStreamer.eventState.isDoing ? '中断连接' : '连接' }}
            </a-button>

            <!-- 操作菜单 -->
            <a-dropdown>
              <template #overlay>
                <a-menu :items="operations" @click="operate" />
              </template>
              <a-button>
                操作
              </a-button>
            </a-dropdown>

            <!--路由按钮-->
            <RouterLink to="/config">
              <a-button>
                系统配置
              </a-button>
            </RouterLink>

            <!-- 信息显示 -->
            <span style="color: green;">
              <div v-if="eventBus.movingStreamer.state.position" style="color: green;">
                <span>X: {{ (eventBus.movingStreamer.state.position[0] * 100).toFixed(1) }} cm</span>
                <span>Y: {{ (eventBus.movingStreamer.state.position[1] * 100).toFixed(1) }} cm</span>
                <span>{{ eventBus.movingStreamer.state.is_screw_tightening ? '拧螺丝中' : '未拧螺丝' }}</span>
              </div>
              <div v-else style="color: green;">
                等待操作
              </div>
            </span>
          </a-space>

        </div>
      </a-affix>
    </a-layout>
    <RouterView />
  </a-config-provider>
</template>

<script setup>
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { message } from 'ant-design-vue'
import zhCN from 'ant-design-vue/es/locale/zh_CN'
import eventBus from '@/units/eventBus'
import { callApi } from '@/units/api'
import config from './units/config'

// 定义操作配置
const operations = [
  {
    key: 'resetZAxes',
    label: '重置Z轴角',
    title: '重置Z轴角',
    api: 'reset_z_axes'
  },
  {
    key: 'resetDesktop',
    label: '重置桌面坐标系',
    title: '重置桌面坐标系'
  },
  {
    key: 'simulateScrew',
    label: '模拟拧螺丝',
    title: '模拟拧螺丝',
    api: 'screw_tightening'
  }
]

const operate = ({ key }) => {
  const operation = operations.find(op => op.key === key)
  if (!operation) return

  if (key === 'resetDesktop') {
    message.info('重置桌面坐标系')
    const [x, y] = eventBus.movingStreamer.state.position
    const [cx, cy] = config.imu.center_point
    config.imu.center_point = [cx - x, cy - y]
    eventBus.movingStreamer.reader?.cancel()
    return
  }

  message.loading({ content: '操作中……', key: operation.key, duration: 0 })
  callApi(operation.api)
    .then(() => message.success({ content: '操作成功', key: operation.key }))
    .catch(() => message.error({ content: '操作失败', key: operation.key }))
}


// 运动控制函数
const handleMoving = () => eventBus.movingStreamer.start()
const handleStopMoving = () => message.info(eventBus.movingStreamer.stop())

// 快捷键处理
window.addEventListener('keydown', (event) => {
  if (event.code === 'Space') {
    message.info('重置Z轴角')
    operate({ key: 'resetZAxes' })
  }
})

onMounted(() => {
  // handleMoving()
})
</script>

<style>
#app {
  padding: 2.5%;
}
</style>