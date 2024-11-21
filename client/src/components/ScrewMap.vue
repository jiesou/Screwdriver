<template>
    <div class="map-container" :style="{
        width: container_width + 'px',
        height: container_height + 'px'
    }">
        <div v-if="position" class="position-dot" :style="{
            left: `${boundedPixel(position[0], 'width')}px`,
            bottom: `${boundedPixel(position[1], 'height')}px`
        }">{{
            `${(position[0] * 100).toFixed(1)}cm\n${(position[1] * 100).toFixed(1)}cm`
            }}</div>

        <div v-for="screw in screws" :key="screw.tag" class="screw-wrapper" :style="{
            left: `${boundedPixel(screw.position.x, 'width')}px`,
            bottom: `${boundedPixel(screw.position.y, 'height')}px`
        }">
            <div class="screw-dot">
                {{ screw.tag }}
            </div>
            <div class="screw-allowed-range" :style="{
                width: `${resize2Pixels(screw.position.allowOffset * 2, 'width')}px`,
                height: `${resize2Pixels(screw.position.allowOffset * 2, 'height')}px`,
                borderColor: getRangeColor(screw.status).border,
                background: getRangeColor(screw.status).background
            }">
            </div>
        </div>
    </div>
</template>

<script setup>
import { computed, ref } from 'vue';

const props = defineProps({
    position: Object,
    screws: Array
});

const position = computed(() => props.position);
const screws = computed(() => props.screws);

// 物理和显示尺寸常量
const physics_width = 2;
const physics_height = 2;
const container_width = ref(800);
const container_height = ref(800);
const dot_size = 10;

const resize2Pixels = (realSize, dimension) => {
    const containerSize = dimension === 'width' ? container_width.value : container_height.value;
    const physicsSize = dimension === 'width' ? physics_width : physics_height;
    return (realSize / physicsSize) * containerSize;
};


// 计算边界内的位置
const boundedPixel = (realValue, dimension) => {
    const containerSize = dimension === 'width' ? container_width.value : container_height.value;
    const pixelValue = resize2Pixels(realValue, dimension);
    return Math.min(Math.max(pixelValue, dot_size / 2), containerSize - dot_size / 2);
};

// 根据状态获取颜色
const getRangeColor = (status) => {
    switch (status) {
        case '已定位':
            return {
                border: 'rgba(255, 255, 0, 0.5)',
                background: 'rgba(255, 255, 0, 0.2)'
            };
        case '已完成':
            return {
                border: 'rgba(0, 255, 0, 0.5)',
                background: 'rgba(0, 255, 0, 0.2)'
            };
        default:
            return {
                border: 'rgba(0, 0, 255, 0.5)',
                background: 'rgba(0, 0, 255, 0.2)'
            };
    }
};
</script>

<style scoped>
.map-container {
    position: relative;
    border: 1px solid #ccc;
    background: #f0f0f0;
}

.position-dot {
    position: absolute;
    width: 10px;
    height: 10px;
    background: red;
    border-radius: 50%;
    transform: translate(-50%, 50%);
}

.screw-wrapper {
    position: absolute;
    transform: translate(-50%, 50%);
}

.screw-allowed-range {
    position: absolute;
    border-radius: 50%;
    left: 0;
    bottom: 0;
    transform: translate(-50%, 50%);
}

.screw-dot {
    position: absolute;
    width: 8px;
    height: 8px;
    background: blue;
    border-radius: 50%;
    left: 0;
    bottom: 0;
    transform: translate(-50%, 50%);
    text-align: center;
    white-space: nowrap;
    font-size: large;
    color: #333;
    display: flex;
    align-items: center;
    justify-content: center;
}
</style>
