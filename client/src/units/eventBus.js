import { reactive } from 'vue';
import { Streamer } from '@/units/stream';

const eventBus = reactive({
    serverConnected: false,
    movingStreamer: new Streamer(),
    counter: -1,
    state: {}
});
export default eventBus;
