<template>
  <div>
    <a-table :columns="columns" :dataSource="props.screws" rowKey="tag" :rowClassName="highlightRow" style="max-width: 720px" />
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

// watch(() => eventBus.locatedScrew, (newScrew) => {
//   if (!newScrew) return
//   eventBus.initScrews.forEach(screw => {
//     if (screw.tag === newScrew.tag) {
//       screw.status = 'highlight'
//     } else {
//       screw.status = ''
//     }
//   })
// })


// 定义一个方法来动态应用高亮类
const highlightRow = (record) => {
  return record.status === 'highlight' ? 'highlight' : ''
}
</script>

<style scoped>
.highlight {
  background-color: yellow;
  /* 你可以根据需要调整样式 */
}
</style>
