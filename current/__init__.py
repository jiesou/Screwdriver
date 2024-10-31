from .communication import read_data


class CurrentProcessor:
    def __init__(self):
        self.is_working = False
        self.threshold = 16.0
        self.appliance_on = False  # 用于跟踪设备状态

    def parse_data(self):
        for data in read_data():
            frequency = data['frequency']
            if frequency > self.threshold and not self.appliance_on:
                self.is_working = True
                self.appliance_on = True
            elif frequency <= self.threshold and self.appliance_on:
                self.is_working = False
                self.appliance_on = False
            yield data


class CurrentAPI:
    def __init__(self):
        self.current_processor = CurrentProcessor()

    def handle_start(self):
        yield from self.current_processor.parse_data()

    def is_working(self):
        return self.current_processor.is_working
