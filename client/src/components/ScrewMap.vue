<template>
    <div>
        <a-table :columns="columns" :dataSource="data" rowKey="tag" />
    </div>
</template>

<script setup>
import { ref, onMounted, watchEffect } from 'vue'
import { message } from 'ant-design-vue'
import { callApi } from '@/units/api'

const props = defineProps({
    state: Object
})
const data = ref([])

const columns = [
    { title: '螺丝（范围）序号', dataIndex: 'tag', key: 'tag' },
    { title: '动作状态', dataIndex: 'status', key: 'status' },
    { title: 'X位置', dataIndex: ['position', 'x'], key: 'x', customRender: ({ text }) => `${text * 100} cm`},
    { title: 'Y位置', dataIndex: ['position', 'y'], key: 'y', customRender: ({ text }) => `${text * 100} cm`},
    { title: '允许误差', dataIndex: ['position', 'offset'], key: 'offset', customRender: ({ text }) => `${text * 100} cm`}
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

onMounted(() => {
    fetchData()
})

watchEffect(() => {
    if (props.state) {
        console.log(props.state)
    }
})
</script>

<style scoped>
</style>
