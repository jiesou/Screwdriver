import { reactive } from 'vue';
const eventBus = reactive({
    refresh: false,
    restart: false,
    initScrews: [
    {"tag": "左上", "position": {"x": 0.1, "y": 0.2, "allowOffset": 0.1},
        "quaternion": {"x": 0, "y": 0}},
    {"tag": "右上", "position": {"x": 0.3, "y": 0.2, "allowOffset": 0.1},
        "quaternion": {"x": 0, "y": 0}},
    {"tag": "左下", "position": {"x": 0.1, "y": 0.1, "allowOffset": 0.1},
        "quaternion": {"x": 0, "y": 0}},
    {"tag": "右下", "position": {"x": 0.3, "y": 0.1, "allowOffset": 0.1},
        "quaternion": {"x": 0, "y": 0}}
    ],
    locatedScrew: {},
    counter: -1,
    state: {}
});
export default eventBus;