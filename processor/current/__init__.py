from .communication import CurrentCommunicator


class CurrentProcessor:
    def __init__(self):
        self.is_working = False
        self.threshold = 15.0
        self.appliance_on = False  # 用于跟踪设备状态

        self.communicator = CurrentCommunicator()

    def parse_data(self):
        for data in self.communicator.read_data():
            if data is None:
                yield None
                continue
            frequency = float(data.get('frequency', 0))
            if data['btn_pressed']:
                # 按钮按下时，模拟螺丝刀工作
                yield {
                    "connected_fine": True,
                    "is_working": True
                }
                continue
            if frequency > self.threshold and not self.appliance_on:
                self.is_working = True
                self.appliance_on = True
            elif frequency <= self.threshold and self.appliance_on:
                self.is_working = False
                self.appliance_on = False
            yield {
                "connected_fine": True,
                "is_working": self.is_working is True,
            }


class API:
    def __init__(self):
        self.processor = CurrentProcessor()

    def handle_start(self):
        yield from self.processor.parse_data()
