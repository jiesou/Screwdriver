<template>
  <a-typography-title>
    螺丝管理
  </a-typography-title>
  <a-flex gap="large" wrap="wrap">
    <a-button type="primary" @click="handleStartMoving" :loading="startMovingState.loading"
      :danger="startMovingState.danger">开始移动</a-button>
    <a-button @click="handleResetZAaxes" :loading="resetZAaxesState.loading" :danger="resetZAaxesState.danger">重置
      Z轴角</a-button>
    <a-button @click="resetDesktopCoordinateSystem" :loading="resetDesktopCoordinateSystemState.loading"
      :danger="resetDesktopCoordinateSystemState.danger">重置桌面坐标系</a-button>
    <a-button @click="simulateScrewTightening" :loading="simulateScrewTighteningState.loading"
      :danger="simulateScrewTighteningState.danger">模拟拧螺丝</a-button>
  </a-flex>
  <div :style="{ marginTop: '20px' }">
    <a-typography-title :level="3" style="color: green;">
      {{ stateText }}
    </a-typography-title>
    <ScrewMap :state="state" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { message } from 'ant-design-vue'
import { callApi } from '@/units/api'

import ScrewMap from '@/components/ScrewMap.vue';

const stateText = ref('等待操作')
const state = ref({})

const resetZAaxesState = ref({
  loading: false,
  danger: null,
})
const handleResetZAaxes = () => {
  resetZAaxesState.value.loading = true
  callApi('reset_z_axes').then(() => {
    resetZAaxesState.value.loading = false
    message.success('重置 Z 轴角成功')
  }).catch(err => {
    resetZAaxesState.value.loading = false
    message.error(`重置 Z 轴角失败${err}`)
  })
}

const startMovingState = ref({
  loading: false,
  danger: null,
})
const handleStartMoving = () => {
  startMovingState.value.loading = true
  callApi('start_moving')
    .then(response => {
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      
      const read = () => {
        reader.read().then(({ done, value }) => {
          if (done) {
            // 流读取完毕
            startMovingState.value.loading = false
            message.success('完成')
            return
          }
          // 处理流数据
          buffer += decoder.decode(value, { stream: true })
          const parts = buffer.split('\n')
          buffer = parts.pop() // 保留最后一个未完成的部分
          parts.forEach(part => {
            if (part) {
                try {
                state.value = JSON.parse(part)
                stateText.value = `
                  X: ${state.value.position[0].toFixed(3)}
                  Y: ${state.value.position[1].toFixed(3)}
                  Z: ${state.value.position[2].toFixed(3)}
                `
              } catch (err) {
                console.error('JSON 解析错误:', err)
              }
            }
          })
          read()
        }).catch(err => {
          // 处理读取错误
          startMovingState.value.loading = false
          message.error(`读取流数据失败: ${err}`)
        })
      }

      read()
    })
    .catch(err => {
      startMovingState.value.loading = false
      message.error(`后端连接失败: ${err}`)
    })
}
const simulateScrewTighteningState = ref({
  loading: false,
  danger: null,
})
const simulateScrewTightening = () => {
  simulateScrewTighteningState.value.loading = true
  callApi('simulate_screw_tightening').then(() => {
    simulateScrewTighteningState.value.loading = false
    message.success('模拟拧螺丝成功')
  }).catch(err => {
    simulateScrewTighteningState.value.loading = false
    message.error(`模拟拧螺丝失败${err}`)
  })
}

// 空格键
window.addEventListener('keydown', (event) => {
  if (event.code === 'Space') {
    simulateScrewTightening()
  }
})

const resetDesktopCoordinateSystemState = ref({
  loading: false,
  danger: null,
})
const resetDesktopCoordinateSystem = () => {
  resetDesktopCoordinateSystemState.value.loading = true
  callApi('reset_desktop_coordinate_system').then(() => {
    resetDesktopCoordinateSystemState.value.loading = false
    message.success('重置桌面坐标系成功')
  }).catch(err => {
    resetDesktopCoordinateSystemState.value.loading = false
    message.error(`重置桌面坐标系失败${err}`)
  })
}

</script>
