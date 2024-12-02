import { reactive, watch } from 'vue';

const STORAGE_KEY = 'screwdriver_config';

const savedConfig = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');

const defaultConfig = {
    init_screws: [
        { "tag": "1", "position": { "x": 1.05, "y": 1.2, "allowOffset": 0.08 } },
        { "tag": "2", "position": { "x": 1.05, "y": 0.8, "allowOffset": 0.08 } },
        { "tag": "3", "position": { "x": 1.5, "y": 1.2, "allowOffset": 0.1 } },
        { "tag": "4", "position": { "x": 1.5, "y": 0.8, "allowOffset": 0.1 } }
    ],
    map_physics_width: 2,
    map_physics_height: 2,
    imu: {
        vertical_h: 1,
        center_point: [1, 1]
    }
};

const config = reactive({
    ...defaultConfig,
    ...savedConfig
});

watch(config, (newValue) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newValue));
}, { deep: true });

export default config;