<template>
  <a-typography-title>
    配置
  </a-typography-title>
  <a-flex gap="middle">
    <div style="flex: 1;">
      <a-form :model="mapConfig" layout="vertical">
        <a-form-item label="地图宽度(像素)">
          <a-input-number 
            v-model:value="mapConfig.width" 
            :min="500" 
            :max="2000"
            style="width: 200px"
          />
        </a-form-item>
        
        <a-form-item label="地图高度(像素)">
          <a-input-number 
            v-model:value="mapConfig.height" 
            :min="500" 
            :max="2000"
            style="width: 200px"
          />
        </a-form-item>

        <a-form-item label="地图中心X坐标(米)">
          <a-input-number 
            v-model:value="mapConfig.centerX" 
            :step="0.1"
            :precision="2"
            style="width: 200px"
          />
        </a-form-item>

        <a-form-item label="地图中心Y坐标(米)">
          <a-input-number 
            v-model:value="mapConfig.centerY" 
            :step="0.1"
            :precision="2"
            style="width: 200px"
          />
        </a-form-item>

        <a-form-item label="位置单元垂直距离(米)">
          <a-input-number 
            v-model:value="mapConfig.unitDistance" 
            :step="0.1"
            :precision="2"
            style="width: 200px"
          />
        </a-form-item>
      </a-form>
    </div>
    <div style="flex: 2;">
      <ScrewMap 
        :screws="mockScrews" 
        :position="mockPosition"
        :container_width="mapConfig.width"
        :container_height="mapConfig.height"
      />
    </div>
  </a-flex>
</template>

<script setup>
import { ref } from 'vue';
import ScrewMap from '@/components/ScrewMap.vue';

const mapConfig = ref({
  width: 800,
  height: 600,
  centerX: 0,
  centerY: 0,
  unitDistance: 1.0
});

// 用于测试显示的模拟数据
const mockScrews = ref([
  {
    tag: "1",
    position: {
      x: 0.5,
      y: 0.5,
      allowOffset: 0.1
    }
  }
]);

const mockPosition = ref([0, 0]);
</script>

<style scoped>
.ant-form {
  max-width: 500px;
  padding: 20px;
}
</style>