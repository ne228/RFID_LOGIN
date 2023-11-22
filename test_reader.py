import random

class TestReader:
    def __init__(self, com_port):
        self.com_port = com_port

    def read(self):
        random_number = random.randint(1, 64000)
        return f"UID: rfid_id_from_test_reader_{random_number}"