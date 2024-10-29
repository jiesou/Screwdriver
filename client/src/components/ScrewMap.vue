<template>
    <div>
        <a-table :columns="columns" :dataSource="data" rowKey="tag" />
    </div>
</template>

<script setup>
import { ref, watchEffect } from 'vue'
import { message } from 'ant-design-vue'
import { callApi } from '@/units/api'

const props = defineProps({
    state: Object
})
const data = ref([])

const columns = [
    { title: '序号', dataIndex: 'tag', key: 'tag' },
    { title: '动作状态', dataIndex: 'status', key: 'status' },
    { title: 'X位置', dataIndex: ['position', 'x'], key: 'x', customRender: ({ text }) => `${text * 100} cm`},
    { title: 'Y位置', dataIndex: ['position', 'y'], key: 'y', customRender: ({ text }) => `${text * 100} cm`},
    { title: '允许偏差', dataIndex: ['position', 'allow_offset'], key: 'allow_offset', customRender: ({ text }) => `${text * 100} cm`}
]

const fetchData = async () => {
    callApi('screw_data').then(res => {
        const reader = res.body.getReader()
        const decoder = new TextDecoder()

        const read = () => {
            reader.read().then(({ done, value }) => {
                if (done) {
                    // 流读取完毕
                    return
                }
                // 处理流数据
                const res = decoder.decode(value, { stream: true })

                data.value = JSON.parse(res)
                read()
            }).catch(err => {
                // 处理读取错误
                message.error(`读取流数据失败: ${err}`)
            })
        }

        read()
    })
}

watchEffect(() => {
    if (props.state.located_screw) {
        console.log(props.state.located_screw)
    }
})

defineExpose({
    fetchData
})
</script>

<style scoped>
</style>
