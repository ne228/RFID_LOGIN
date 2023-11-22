import serial
from threading import Lock

class ReaderCom:
    _instance = None
    _lock = Lock()

    def __new__(cls, com_port):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(ReaderCom, cls).__new__(cls)
                cls._instance.com_port = com_port
                cls._instance.ser = serial.Serial(cls._instance.com_port, 9600, timeout=1)
        return cls._instance

    def read(self):
        try:
            data = self.ser.readline().decode('utf-8').strip()
            print(f"Serial data: {data}")

            if data:
                print(f"Serial data: {data}")
                return data
        except Exception as e:
            print(f"Error reading data from {self.com_port}: {e}")

    def close(self):
        if self.ser.is_open:
            self.ser.close()