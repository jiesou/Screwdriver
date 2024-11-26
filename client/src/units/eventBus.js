import { reactive } from 'vue';
import { Streamer } from '@/units/stream';

const eventBus = reactive({
    serverConnected: false,
    movingStreamer: new Streamer(),
    initScrews: [
    {"tag": "1", "position": {"x": 0.8, "y": 1.2, "allowOffset": 0.1}},
    {"tag": "2", "position": {"x": 0.8, "y": 1, "allowOffset": 0.1}},
    {"tag": "3", "position": {"x": 0.9, "y": 1.2, "allowOffset": 0.1}},
    {"tag": "4", "position": {"x": 0.9, "y": 1, "allowOffset": 0.1}}
    ],
    counter: -1,
    state: {}
});
export default eventBus;
