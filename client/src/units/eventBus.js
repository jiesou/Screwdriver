import { reactive } from 'vue';
const eventBus = reactive({
    refresh: false,
    initScrews: [
    {"tag": "左上", "position": {"x": 0.5, "y": 1.5, "allowOffset": 0.2},
        "quaternion": {"x": 0, "y": 0}},
    {"tag": "右上", "position": {"x": 1.5, "y": 1.5, "allowOffset": 0.2},
        "quaternion": {"x": 0, "y": 0}},
    {"tag": "左下", "position": {"x": 0.5, "y": 0.5, "allowOffset": 0.1},
        "quaternion": {"x": 0, "y": 0}},
    {"tag": "右下", "position": {"x": 1.5, "y": 0.5, "allowOffset": 0.1},
        "quaternion": {"x": 0, "y": 0}}
    ],
    counter: -1,
    state: {}
});
export default eventBus;