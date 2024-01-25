import psutil
from .data_amount import DataAmount

class Memory:

    def __init__(self) -> None:
        memory_stats = psutil.virtual_memory()
    
        self.total = DataAmount(memory_stats.total)
        self.used = DataAmount(memory_stats.used)
        self.available = DataAmount(memory_stats.available)
        self.percentage_used = memory_stats.percent

    def update(self):
        memory_stats = psutil.virtual_memory()
        self.used = DataAmount(memory_stats.used)
        self.available = DataAmount(memory_stats.available)
        self.percentage_used = memory_stats.percent

    @property
    def current_percentage_used(self):
        self.update()
        return self.percentage_used
    
    @property
    def current_available(self):
        self.update()
        return self.available
    
    @property
    def current_used(self):
        self.update()
        return self.used
        

    
