<template>
  <div style="margin-bottom: 16px">
    <input
      type="file"
      ref="fileInput"
      style="display: none"
      accept=".csv"
      @change="handleFile"
    />
    <a-button @click="triggerFileInput" :loading="loading">
      导入CSV地图
    </a-button>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import config from '@/units/config';
import { message } from 'ant-design-vue';

const fileInput = ref(null);
const loading = ref(false);

const triggerFileInput = () => {
  fileInput.value.click();
};

const parseCsv = (text) => {
  const lines = text.split('\n');
  const headers = lines[0].split(',').map(h => h.trim());
  
  return lines.slice(1)
    .filter(line => line.trim())
    .map((line, index) => {
      const values = line.split(',').map(v => v.trim());
      const row = {};
      headers.forEach((header, i) => {
        row[header] = values[i];
      });
      return {
        tag: (index + 1).toString(),
        status: '未执行',
        position: {
          x: Number(row.X) || 0,
          y: Number(row.Y) || 0,
          allowOffset: Number(row.allowOffset) || 0.1
        }
      };
    });
};

const handleFile = (event) => {
  loading.value = true;
  const file = event.target.files[0];
  const reader = new FileReader();

  reader.onload = (e) => {
    try {
      const text = e.target.result;
      const screws = parseCsv(text);
      config.init_screws = screws;
      message.success('导入成功');
    } catch (error) {
      message.error('导入失败：' + error.message);
    } finally {
      loading.value = false;
      event.target.value = '';
    }
  };

  reader.readAsText(file);
};
</script>