<template>
  <a-typography-title>
    螺丝管理
  </a-typography-title>
  <a-flex>
    <div style="margin-right: 15px;">
      <a-flex gap="large" wrap="wrap">
        <a-button type="primary" danger @click="handleStopMoving" :loading="movingState.loading"
          v-if="movingState.isDoing">停止</a-button>
        <a-button type="primary" @click="handleMoving" :loading="movingState.loading" v-else>开始</a-button>
        <a-button @click="handleResetZAaxes" :loading="resetZAaxesState.loading" :danger="resetZAaxesState.danger">重置
          Z轴角</a-button>
        <a-button @click="resetDesktopCoordinateSystem" :loading="resetDesktopCoordinateSystemState.loading"
          :danger="resetDesktopCoordinateSystemState.danger">重置桌面坐标系</a-button>
        <a-button @click="simulateScrewTightening" :loading="simulateScrewTighteningState.loading"
          :danger="simulateScrewTighteningState.danger">模拟拧螺丝</a-button>
      </a-flex>
      <div :level="3" style="color: green;">
        <div v-if="state.position" style="color: green;">
          <span>X: {{ (state.position[0] * 100).toFixed(1) }} cm</span>
          <span>Y: {{ (state.position[1] * 100).toFixed(1) }} cm</span>
          <span>{{ state.is_screw_tightening ? '拧螺丝中' : '未拧螺丝' }}</span>
        </div>
        <div v-else style="color: green;">
          等待操作
        </div>
      </div>
      <ScrewTable />
      <ScrewCounter />
    </div>
    <ScrewMap :screws="eventBus.state.screws" :position="eventBus.state.position" />
  </a-flex>
</template>

<script setup>
import { ref, computed, watchEffect, onMounted } from 'vue'
import { message } from 'ant-design-vue'

import { callApi } from '@/units/api'
import eventBus from '@/units/eventBus'

import ScrewTable from '@/components/ScrewTable.vue';
import ScrewMap from '@/components/ScrewMap.vue';
import ScrewCounter from '@/components/ScrewCounter.vue';

const state = ref({})

const resetZAaxesState = ref({
  loading: false,
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

const movingState = ref({
  loading: false,
  isDoing: false,
  reader: null
})

const readWithTimeout = async () => {
  const timeoutPromise = new Promise((_, reject) => {
    setTimeout(() => reject(new Error('延迟超出预期')), 200); // 200毫秒超时
  });
  return Promise.race([
    movingState.value.reader.read(),
    timeoutPromise
  ]);
};
const handleStopMoving = () => {
  movingState.value.isDoing = false;
  if (movingState.value.reader) movingState.value.reader.cancel();
  message.info('已停止');
}
const handleMoving = async () => {
  movingState.value.loading = true;

  const startStream = async () => {
    try {
      let response = await callApi('start_moving', {
          method: 'POST',
          body: eventBus.initScrews
        })
      eventBus.serverConnected = true
      movingState.value.loading = false;
      movingState.value.isDoing = true;

      movingState.value.reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await readWithTimeout();

        if (done) {
          if (movingState.value.isDoing) {
            throw new Error('流异常结束');
          }
          eventBus.serverConnected = false
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split('\n');
        buffer = parts.pop();
        for (const part of parts) {
          if (!part) continue;
          try {
            const newState = JSON.parse(part);
            state.value = { ...state.value, ...newState };
            eventBus.locatedScrew = state.value.located_screw;
            eventBus.counter = state.value.screw_count;
            eventBus.state = state.value;
          } catch (error) {
            console.error('解析数据失败', error);
            throw error;
          }
        }
      }
    } catch (error) {
      console.error('启动流失败', error);
      eventBus.serverConnected = false
      await new Promise(resolve => setTimeout(resolve, 1000));
      await startStream();
    }
  };

  await startStream();
}

const simulateScrewTighteningState = ref({
  loading: false,
})
const simulateScrewTightening = () => {
  simulateScrewTighteningState.value.loading = true
  callApi('screw_tightening').then(() => {
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
    // simulateScrewTightening()
    // resetDesktopCoordinateSystem()
    handleResetZAaxes();
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


onMounted(() => {
  handleMoving()
})
</script>
