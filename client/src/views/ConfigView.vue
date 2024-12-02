<template>
  <a-typography-title>
    配置
  </a-typography-title>
  <a-flex gap="middle">
    <div style="flex: 1;">
      <a-form :model="config" layout="vertical">
        <a-form-item label="物理地图宽度(米)">
          <a-row>
            <a-col :span="16">
              <a-slider v-model:value="config.map_physics_width" :min="0.1" :max="10" :step="0.1"/>
            </a-col>
            <a-col :span="4">
              <a-input-number v-model:value="config.map_physics_width" :min="0.1" :max="10" :step="0.1" style="margin-left: 16px"/>
            </a-col>
          </a-row>
        </a-form-item>

        <a-form-item label="物理地图高度(米)">
          <a-row>
            <a-col :span="16">
              <a-slider v-model:value="config.map_physics_height" :min="0.1" :max="10" :step="0.1"/>
            </a-col>
            <a-col :span="4">
              <a-input-number v-model:value="config.map_physics_height" :min="0.1" :max="10" :step="0.1" style="margin-left: 16px"/>
            </a-col>
          </a-row>
        </a-form-item>

        <a-form-item label="垂直参考中心X坐标(米)">
          <a-row>
            <a-col :span="16">
              <a-slider v-model:value="config.imu.center_point[0]" :step="0.1" :min="0" :max="4" style="width: 200px" @afterChange="reconnect" />
            </a-col>
            <a-col :span="4">
              <a-input-number v-model:value="config.imu.center_point[0]" :step="0.1" :min="0" :max="4" style="margin-left: 16px" @pressEnter="reconnect" />
            </a-col>
          </a-row>
        </a-form-item>

        <a-form-item label="垂直参考中心Y坐标(米)">
          <a-row>
            <a-col :span="16">
              <a-slider v-model:value="config.imu.center_point[1]" :step="0.1" :min="0" :max="4" style="width: 200px" @afterChange="reconnect" />
            </a-col>
            <a-col :span="4">
              <a-input-number v-model:value="config.imu.center_point[1]" :step="0.1" :min="0" :max="4" style="margin-left: 16px" @pressEnter="reconnect" />
            </a-col>
          </a-row>
        </a-form-item>

        <a-form-item label="位置单元垂直距离(米)">
          <a-row>
            <a-col :span="16">
              <a-slider v-model:value="config.imu.vertical_h" :step="0.1" :min="0" :max="1.5" style="width: 200px" @afterChange="reconnect" />
            </a-col>
            <a-col :span="4">
              <a-input-number v-model:value="config.imu.vertical_h" :step="0.1" :min="0" :max="1.5" style="margin-left: 16px" @pressEnter="reconnect" />
            </a-col>
          </a-row>
        </a-form-item>
      </a-form>
    </div>
    <div style="flex: 2;">
      <ScrewMap :screws="[]" :position="eventBus.movingStreamer.state.position" />  
    </div>
  </a-flex>
</template>

<script setup>
import { ref, watch } from 'vue';
import { message } from 'ant-design-vue';
import config from '@/units/config';
import ScrewMap from '@/components/ScrewMap.vue';
import eventBus from '@/units/eventBus';

const reconnect = () => {
  // 需要重连服务端才能更新的配置
  message.info('配置已更新');
  if (eventBus.movingStreamer.reader) eventBus.movingStreamer.reader.cancel();
};


</script>

<style scoped>
.ant-form {
  max-width: 500px;
  padding: 20px;
}
</style>