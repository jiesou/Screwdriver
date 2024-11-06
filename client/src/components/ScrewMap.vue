<template>
    <div class="map-container">
        <!-- 坐标点 -->
        <div v-if="position" class="position-dot" :style="{
            left: `${boundedPosition[0]}px`,
            bottom: `${boundedPosition[1]}px`
        }">{{
            `${(position[0] * 100).toFixed(1)}\n${(position[1] * 100).toFixed(1)}`
        }}</div>
        
        <!-- 螺丝点 -->
        <div v-for="screw in screws" :key="screw.id" 
             class="screw-dot" 
             :style="{
                left: `${mapToPixels(screw.position.x, screw.position.y)[0]}px`,
                bottom: `${mapToPixels(screw.position.x, screw.position.y)[1]}px`
             }">
             {{
                screw.tag
             }}
        </div>
    </div>
</template>

<script setup>
import { computed } from 'vue';
import eventBus from '@/units/eventBus';

const position = computed(() => eventBus.state.position);

const physics_width = 2;
const physics_height = 1;

const container_width = 1600;
const container_height = 800;
const dot_size = 10;

const mapToPixels = (realX, realY) => {
    const pixelX = (realX / physics_width) * container_width;
    const pixelY = (realY / physics_height) * container_height;
    return [pixelX, pixelY];
};

const boundedPosition = computed(() => {
    if (!position.value) return [0, 0];

    const [pixelX, pixelY] = mapToPixels(position.value[0], position.value[1]);

    const x = Math.min(Math.max(pixelX, dot_size / 2), container_width - dot_size / 2);
    const y = Math.min(Math.max(pixelY, dot_size / 2), container_height - dot_size / 2);

    return [x, y];
});

const screws = computed(() => eventBus.state.screws);
</script>

<style scoped>
.map-container {
    position: relative;
    width: 1600px;
    height: 800px;
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
    /* 使点的中心对准坐标 */
}

.screw-dot {
    position: absolute;
    width: 8px;  /* 增加宽度 */
    height: 8px;
    background: blue;
    border-radius: 50%;
    transform: translate(-50%, 50%);
    text-align: center;  /* 文字居中 */
    white-space: nowrap;  /* 防止文��换行 */
    font-size: 12px;  /* 设置字体大小 */
    color: #333;  /* 文字颜色 */
    display: flex;
    align-items: center;
    justify-content: center;
}
</style>
