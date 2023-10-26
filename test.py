import os
from datetime import datetime

timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

print(timestamp)

class Tool():
    def __init__(self, name:str, func, description:str):
        self.name = name
        self.func = func
        self.description = description


