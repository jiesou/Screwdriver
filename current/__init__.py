from .communication import read_data


class CurrentProcessor:
    def __init__(self):
        self.is_working = False
        self.threshold = 15.0

    def parse_data(self):
        for data in read_data():
            if data is None:
                yield {
                    'is_working': self.is_working is True,
                }
                continue
            frequency = data['frequency']
            if frequency > self.threshold and not self.is_working:
                self.is_working = True
            elif frequency <= self.threshold and self.is_working:
                self.is_working = False
            yield {
                "is_working": self.is_working is True,
            }


class CurrentAPI:
    def __init__(self):
        self.current_processor = CurrentProcessor()

    def handle_start(self):
        yield from self.current_processor.parse_data()

