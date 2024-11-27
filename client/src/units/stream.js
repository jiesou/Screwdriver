import { reactive, ref } from "vue";

import { callApi } from "./api";
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
    timeoutMs = 200;
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
                body: eventBus.initScrews
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
                    // 手动停止，正常结束
                    break;
                }

                buffer += decoder.decode(value, { stream: true });
                const parts = buffer.split('\n');
                buffer = parts.pop();

                for (const part of parts) {
                    if (!part) continue;
                    try {
                        const data = JSON.parse(part);
                        Object.assign(this.state, data);
                    } catch (error) {
                        eventBus.serverConnected = false;
                        throw error;
                    }
                }
            }
        } catch (error) {
            eventBus.serverConnected = false;
            await new Promise(resolve => setTimeout(resolve, 100));
            await this.startStream();
        }
    };

    start() {
        this.eventState.loading = true;
        this.startStream();
    }

    stop() {
        if (this.reader) this.reader.cancel();
        this.eventState.isDoing = false;
        eventBus.serverConnected = false;
        return '已停止';
    }
}