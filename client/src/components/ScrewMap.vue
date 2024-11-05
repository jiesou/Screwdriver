<template>
    <div class="map-container">
        <!-- 坐标点 -->
        <div v-if="position"
            class="position-dot"
            :style="{
                left: `${position[0] * 100}cm`,
                bottom: `${position[1] * 100}cm`
            }"
        >{{
            `X: ${(position[0] * 100).toFixed(1)}cm, Y: ${(position[1] * 100).toFixed(1)}cm`
        }}</div>
    </div>
</template>

<script setup>
import { computed, watchEffect } from 'vue';
import eventBus from '@/units/eventBus';

const position = computed(() => eventBus.state.position);

</script>

<style scoped>
.map-container {
    position: relative;
    width: 400px;
    height: 200px;
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
</style>
