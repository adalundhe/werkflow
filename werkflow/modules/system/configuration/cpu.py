import psutil


class CPU:

    def __init__(self) -> None:
        self.physical = psutil.cpu_count(logical=False)
        self.total = psutil.cpu_count(logical=True)
        self.percentage_used = psutil.cpu_percent()

    def update(self):
        self.percentage_used = psutil.cpu_percent()
