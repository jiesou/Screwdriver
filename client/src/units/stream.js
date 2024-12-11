import { reactive } from "vue";

import { callApi } from "./api";
import config from "./config";
import eventBus from "./eventBus";

async function readWithTimeout(reader, timeoutMs) {
    const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('延迟超出预期')), timeoutMs);
    });
    return Promise.race([
        reader.read(),
        timeoutPromise
    ]);
}

export class Streamer {
    timeoutMs = 300;
    reader = null;
    eventState = reactive({
        isDoing: false,
        loading: false
    });
    state = reactive({
        position: null,
        screws: [],
        is_screw_tightening: false
    });

    async startStream() {
    try {
        const response = await callApi('start_moving', {
            method: 'POST',
            body: {
                screws: config.init_screws,
                h: config.imu.vertical_h,
                center_point: config.imu.center_point,
            }
        });
        this.eventState.loading = false;
        this.eventState.isDoing = true;
        eventBus.serverConnected = true;

        this.reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await readWithTimeout(this.reader, this.timeoutMs);

            if (done) {
                if (this.eventState.isDoing) {
                    throw new Error('流异常结束');
                }
                break;
            }

            buffer += decoder.decode(value, { stream: true });
            const parts = buffer.split('\n');
            buffer = parts.pop();

            for (const part of parts) {
                if (!part) continue;
                const data = JSON.parse(part);
                Object.assign(this.state, data);
            }
        }
    } catch(error) {
        console.error('startStream error:', error);
        throw error; // 确保错误继续传播
    }
    }

    start() {
        this.eventState.loading = true;
        this.startStream().catch(error => {
            console.error('连接错误:', error);
            eventBus.serverConnected = false;
            setTimeout(() => this.start(), 300); // 0.1秒后重试
        });
    }

    stop() {
        if (this.reader) this.reader.cancel();
        this.eventState.isDoing = false;
        eventBus.serverConnected = false;
        console.log('手动停止流');
        return '已停止';
    }
}