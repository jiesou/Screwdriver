<template>
    <div ref="plotlyContainer" class="map-container"></div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue';
import Plotly from 'plotly.js-dist';

import config from '@/units/config';

const props = defineProps({
    position: Object,
    screws: Array
});

const plotlyContainer = ref(null);

const getRangeColor = (status) => {
    switch (status) {
        case '已定位':
            return 'rgba(255, 255, 0, 0.2)';
        case '已完成':
            return 'rgba(0, 255, 0, 0.2)';
        default:
            return 'rgba(0, 0, 255, 0.2)';
    }
};

const updateMapRange = () => {
    Plotly.relayout(plotlyContainer.value, {
        xaxis: {
            range: [0, config.map_physics_width],
            scaleratio: 1,
            constrain: 'domain'
        },
        yaxis: {
            range: [0, config.map_physics_height],
            scaleratio: 1,
            scaleanchor: 'x'
        }
    });
};

const initPlot = () => {
    const data = [
        // 螺丝点图层
        {
            mode: 'markers+text',
            type: 'scattergl',
            text: props.screws.map(screw => screw.tag),
            textposition: 'top center',
            marker: { size: 12, color: 'blue' },
            name: 'screws'
        },
        // 位置点图层
        {
            mode: 'markers',
            type: 'scattergl',
            marker: { size: 8, color: 'red' },
            name: 'position'
        }
    ];

    Plotly.newPlot(plotlyContainer.value, data, {
        autosize: true,
        margin: {
            l: 80,
            r: 80,
            t: 80,
            b: 80
        }
    }, { responsive: true });
    
    // 初始化完成后设置范围
    updateMapRange();
};

const updatePosition = (newPosition) => {
    if (!newPosition) return;
    
    Plotly.restyle(plotlyContainer.value, {
        x: [[newPosition[0]]],
        y: [[newPosition[1]]]
    }, [1]);
    // 只更新第1个数据集（位置点）
};

const updateScrews = (newScrews) => {
    const update = {
        x: [newScrews.map(screw => screw.position.x)],
        y: [newScrews.map(screw => screw.position.y)],
        text: [newScrews.map(screw => screw.tag)]
    };

    Plotly.restyle(plotlyContainer.value, update, [0]);
    // 只更新第0个数据集（螺丝点）
    
    // 更新形状
    Plotly.relayout(plotlyContainer.value, {
        shapes: newScrews.map(screw => ({
            type: 'circle',
            x0: (screw.position.x - screw.position.allowOffset),
            y0: (screw.position.y - screw.position.allowOffset),
            x1: (screw.position.x + screw.position.allowOffset),
            y1: (screw.position.y + screw.position.allowOffset),
            fillcolor: getRangeColor(screw.status),
            line: { color: getRangeColor(screw.status) },
            opacity: 0.5
        }))
    });
};

onMounted(() => {
    initPlot();
});

// 分别监听位置和螺丝的更新
watch(() => props.position, (newPosition) => {
    updatePosition(newPosition);
});

watch(() => props.screws, (newScrews) => {
    updateScrews(newScrews);
}, { deep: true });

// 监听地图尺寸配置的变化
watch(() => [config.map_physics_width, config.map_physics_height], () => {
    updateMapRange();
});
</script>

<style scoped>
.map-container {
    height: 800px;
    width: 100%;
}
</style>
