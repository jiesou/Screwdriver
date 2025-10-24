from .communication import EncoderCommunicator


class EncoderProcessor:
    def __init__(self):
        self.communicator = EncoderCommunicator()

    def parse_data(self):
        for data in self.communicator.read_data():
            if data is None:
                yield None
                continue
            line_length = data
            yield {
                "connected_fine": True,
                "line_length": line_length,
            }


class API:
    def __init__(self):
        self.processor = EncoderProcessor()

    def handle_start(self):
        yield from self.processor.parse_data()
