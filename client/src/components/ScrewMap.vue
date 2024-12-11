<template>
    <div>{{ fps_counter }}<div ref="plotlyContainer" class="map-container"></div>
    </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue';
import Plotly from 'plotly.js-dist';
import config from '@/units/config';
import eventBus from '@/units/eventBus';

const props = defineProps({
    position: Object,
    screws: Array
});

const plotlyContainer = ref(null);

const fps_counter = ref(0);

// 计算比例系数：像素/米
const resize2Pixels = (realSize) => {
    const { container_width, container_height } = plotlyContainer.value.getBoundingClientRect()
    const containerSize = 800 * 0.8;
    const physicsSize = config.map_physics_width;
    return (realSize / physicsSize) * containerSize;
};

const updatedData = () => {
    // 生成螺丝位置标记数据
    const screwMarkers = props.screws.map(s => ({
        x: [s.position.x],
        y: [s.position.y],
        mode: 'markers+text',
        textposition: 'top',
        type: 'scatter',
        marker: {
            size: resize2Pixels(s.position.allowOffset * 2), // 直径需要是 allowOffset 的两倍
            color: {
                '已定位': 'rgb(255, 255, 0)',
                '已完成': 'rgb(0, 255, 0)'
            }[s.status] || 'rgb(0, 0, 255)',
            symbol: 'circle',
        },
        text: s.tag,
        textposition: 'top',
        opacity: 0.3,
        showlegend: false,
        name: s.tag
    }));

    // 生成当前位置标记数据
    const positionMarker = {
        x: props.position ? [props.position[0]] : [],
        y: props.position ? [props.position[1]] : [],
        type: 'scatter',
        marker: { size: 8, color: 'red' },
        showlegend: false,
        name: 'position'
    };

    return [...screwMarkers, positionMarker];
};

let updateLock = false;
setInterval(() => {
    if (eventBus.serverConnected === false) return;
    if (updateLock) return;
    const startTime = performance.now();
    updateLock = true;
    Plotly.purge(plotlyContainer.value);

    Plotly.react(plotlyContainer.value, updatedData(), layout, { staticPlot: true, displayModeBar: false });
    updateLock = false;

    fps_counter.value = Math.round(performance.now() - startTime);
}, 1000 / 60);

let layout = {
    autosize: true,
    margin: { l: 80, r: 80, t: 80, b: 80 },
    xaxis: {
        range: [0, config.map_physics_width],
        scaleratio: 1,
        constrain: 'domain'
    },
    yaxis: {
        range: [0, config.map_physics_height],
        scaleratio: 1,
        scaleanchor: 'domain'
    }
};

watch(() => [config.map_physics_width, config.map_physics_height], () => {
    layout.xaxis.range = [0, config.map_physics_width];
    layout.yaxis.range = [0, config.map_physics_height];
    // Plotly.restyle(plotlyContainer.value, [], layout);
});

onMounted(() => {
    Plotly.newPlot(plotlyContainer.value, [], layout, { staticPlot: true, displayModeBar: false });
});
</script>

<style scoped>
.map-container {
    height: 800px;
    width: 800px;
}
</style>