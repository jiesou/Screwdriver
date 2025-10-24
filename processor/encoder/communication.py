import asyncio


class EncoderCommunicator:
    def __init__(self):
        pass

    async def read_data(self):
        """异步生成器：模拟异步 IO，周期性产出数据"""
        while True:
            # 模拟异步等待
            await asyncio.sleep(0.1)
            yield 1  # 占位符，后续实现具体逻辑
