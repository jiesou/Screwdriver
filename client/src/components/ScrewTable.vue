<template>
  <div>
    <a-table :columns="columns" :dataSource="props.screws" rowKey="tag" style="min-width: 520px; max-width: 520px" />
  </div>
</template>

<script setup>

const props = defineProps({
    screws: Array
});

const columns = [
  { title: '序号', dataIndex: 'tag', key: 'tag' },
  { title: '动作状态', dataIndex: 'status', key: 'status' },
  { title: 'X位置', dataIndex: ['position', 'x'], key: 'x', customRender: ({ text }) => `${text * 100} cm` },
  { title: 'Y位置', dataIndex: ['position', 'y'], key: 'y', customRender: ({ text }) => `${text * 100} cm` },
  { title: '允许偏差', dataIndex: ['position', 'allowOffset'], key: 'allowOffset', customRender: ({ text }) => `${text * 100} cm` }
]

</script>

<style scoped>
</style>
