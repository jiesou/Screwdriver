import { reactive } from 'vue';
const eventBus = reactive({
    refresh: false,
    initScrews: [
    {"tag": "左上", "position": {"x": 0.75, "y": 1.2, "allowOffset": 0.2}},
    {"tag": "右上", "position": {"x": 1.25, "y": 1.2, "allowOffset": 0.2}},
    {"tag": "左下", "position": {"x": 0.75, "y": 0.5, "allowOffset": 0.1}},
    {"tag": "右下", "position": {"x": 1.25, "y": 0.5, "allowOffset": 0.1}}
    ],
    counter: -1,
    state: {}
});
export default eventBus;