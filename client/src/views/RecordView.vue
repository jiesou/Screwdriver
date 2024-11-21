<template>
  <a-typography-title>产品管理</a-typography-title>
  
  <a-flex>
    <div style="margin-right: 15px;">
      <a-flex gap="middle" style="margin-bottom: 20px">
        <a-button type="primary" @click="showAddModal" :disabled="isRecording">添加产品</a-button>
        <a-button type="primary" danger @click="stopRecording" v-if="isRecording">停止记录</a-button>
      </a-flex>

      <a-table :columns="columns" :dataSource="products" rowKey="id" style="width: 600px">
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'action'">
            <a-space>
              <a @click="viewProduct(record)">查看</a>
              <a @click="deleteProduct(record)">删除</a>
            </a-space>
          </template>
        </template>
      </a-table>

      <a-form-item label="螺丝数据" style="margin-top: 20px">
        <a-textarea
          v-model:value="screwsJson"
          :rows="10"
          @change="handleJsonChange"
          placeholder="螺丝位置数据 JSON"
        />
      </a-form-item>
    </div>

    <div>
      <ScrewMap :screws="displayScrews" :position="currentPosition" />
    </div>
  </a-flex>

  <a-modal v-model:open="addModalVisible" title="添加产品" @ok="startRecord" :confirmLoading="recordingState.loading">
    <a-form :model="newProduct">
      <a-form-item label="产品名称">
        <a-input v-model:value="newProduct.name" />
      </a-form-item>
    </a-form>
  </a-modal>

  <a-modal v-model:open="viewModalVisible" title="查看产品" width="800px">
    <ScrewMap :screws="currentProduct.screws" :position="currentPosition" />
  </a-modal>
</template>

<script setup>
import { ref } from 'vue';
import { message } from 'ant-design-vue';
import { callApi } from '@/units/api';
import ScrewMap from '@/components/ScrewMap.vue';

const columns = [
  { title: '产品名称', dataIndex: 'name', key: 'name' },
  { title: '螺丝数量', dataIndex: 'screwCount', key: 'screwCount' },
  { title: '操作', key: 'action' }
];

const products = ref([]);
const addModalVisible = ref(false);
const viewModalVisible = ref(false);
const currentProduct = ref({});
const isRecording = ref(false);

const newProduct = ref({
  name: '',
  screws: []
});

const recordingState = ref({
  loading: false,
  reader: null,
  screwPositions: []
});

const screwsJson = ref('[]');
const currentPosition = ref(null);
const displayScrews = ref([]);

const showAddModal = () => {
  newProduct.value = {
    name: '',
    screws: []
  };
  addModalVisible.value = true;
};

const startRecord = async () => {
  if (!newProduct.value.name) {
    message.error('请输入产品名称');
    return;
  }

  recordingState.value.loading = true;
  isRecording.value = true;
  recordingState.value.screwPositions = [];
  addModalVisible.value = false;

  try {
    const response = await callApi('start_record', {
      method: 'POST'
    });

    recordingState.value.reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await recordingState.value.reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const parts = buffer.split('\n');
      buffer = parts.pop();

      for (const part of parts) {
        if (!part) continue;
        try {
          const data = JSON.parse(part);
          currentPosition.value = data.position;
          
          if (data.is_working) {
            const newScrew = {
              tag: recordingState.value.screwPositions.length + 1,
              position: {
                x: data.position[0],
                y: data.position[1],
                allowOffset: 0.1
              }
            };
            recordingState.value.screwPositions.push(newScrew);
            displayScrews.value = recordingState.value.screwPositions;
            screwsJson.value = JSON.stringify(displayScrews.value, null, 2);
          }
        } catch (e) {
          console.error('解析数据失败:', e);
        }
      }
    }
  } catch (error) {
    message.error('记录失败：' + error);
  }
};

const stopRecording = async () => {
  if (recordingState.value.reader) {
    recordingState.value.reader.cancel();
  }
  
  const product = {
    id: Date.now(),
    name: newProduct.value.name,
    screws: recordingState.value.screwPositions,
    screwCount: recordingState.value.screwPositions.length
  };
  
  products.value.push(product);
  isRecording.value = false;
  recordingState.value.loading = false;
  cleanup();
  message.success('记录完成');
};

const viewProduct = (product) => {
  currentProduct.value = product;
  displayScrews.value = product.screws;
  screwsJson.value = JSON.stringify(product.screws, null, 2);
  viewModalVisible.value = true;
};

const deleteProduct = (product) => {
  products.value = products.value.filter(p => p.id !== product.id);
  message.success('删除成功');
};

const handleJsonChange = (e) => {
  try {
    const parsed = JSON.parse(e.target.value);
    displayScrews.value = parsed;
  } catch (error) {
    message.error('JSON格式错误');
  }
};

const cleanup = () => {
  currentPosition.value = null;
  displayScrews.value = [];
  screwsJson.value = '[]';
};
</script>

<style scoped>
.ant-table {
  margin-top: 20px;
}
</style>