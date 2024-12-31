from .communication import read_data


class CurrentProcessor:
    def __init__(self):
        self.is_working = False
        self.threshold = 15.0
        self.appliance_on = False  # 用于跟踪设备状态

    def parse_data(self):
        for data in read_data():
            if data is None:
                yield {
                    "connected_fine": False,
                    "is_working": False
                }
                continue
            frequency = data['frequency']
            # if data['btn_pressed']:
            #     # 按钮按下时，模拟螺丝刀工作
            #     yield {
            #         "connected_fine": True,
            #         "is_working": True
            #     }
            #     continue
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


class CurrentAPI:
    def __init__(self):
        self.processor = CurrentProcessor()

    def handle_start(self):
        yield from self.processor.parse_data()

