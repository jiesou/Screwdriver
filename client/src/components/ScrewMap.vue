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


const updatedData = () => {
    
    return props.screws.map(screw => ({
        x: Array.from({length: 51}, (_, i) => 
            screw.position.x + Math.cos(2 * Math.PI * i / 50) * screw.position.allowOffset),
        y: Array.from({length: 51}, (_, i) => 
            screw.position.y + Math.sin(2 * Math.PI * i / 50) * screw.position.allowOffset),
        mode: 'lines',
        type: 'scattergl',
        fill: 'toself',
        fillcolor: {
            '已定位': 'rgba(255, 255, 0, 1)',
            '已完成': 'rgba(0, 255, 0, 1)'
        }[screw.status] || 'rgba(0, 0, 255, 1)',
        line: { width: 0 },
        opacity: 0.3,
        showlegend: false, // 不显示图注
    })).concat([
        {
            x: props.screws.map(s => s.position.x),
            y: props.screws.map(s => s.position.y),
            text: props.screws.map(s => s.tag),
            mode: 'markers+text',
            type: 'scattergl',
            textposition: 'top',
            marker: { size: 12, color: 'blue' },
            name: 'screws'
        },
        {
            x: props.position ? [props.position[0]] : [],
            y: props.position ? [props.position[1]] : [],
            type: 'scattergl',
            marker: { size: 8, color: 'red' },
            name: 'position'
        }
    ]);
};

watch(() => props.position, () => {
    console.log(updatedData())
    Plotly.purge(plotlyContainer.value);
    Plotly.react(plotlyContainer.value, updatedData(), layout);
});

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
    Plotly.react(plotlyContainer.value, [], layout);
});

onMounted(() => {
    Plotly.newPlot(plotlyContainer.value, [], layout, { responsive: true });
});
</script>

<style scoped>
.map-container {
    height: 800px;
}
</style>
