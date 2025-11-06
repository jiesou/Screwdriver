from .communication import EncoderCommunicator


class EncoderProcessor:
    def __init__(self):
        self.communicator = EncoderCommunicator()

    def parse_data(self):
        for data in self.communicator.read_data():
            if data is None:
                yield None
                continue
            encoder_value = data
            yield {
                "connected_fine": True,
                "encoder_value": encoder_value,
            }


class API:
    def __init__(self):
        self.processor = EncoderProcessor()

    def handle_start(self):
        yield from self.processor.parse_data()
