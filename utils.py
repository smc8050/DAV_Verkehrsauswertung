import numpy as numpy
from datetime import datetime

class Timestamp:
    def _convert(self, input_str):
        return datetime.strptime(input_str, '%Y-%m-%dT%H:%M:%S')

    def __init__(self, messungDatZeit):
        self.timestamp = self._convert(messungDatZeit)

    def isSmaller(self, input_str):
        return self.timestamp <= self._convert(input_str)

    def isBigger(self, input_str):
        return self.timestamp >= self._convert(input_str)

    def date(self):
        return self.timestamp
