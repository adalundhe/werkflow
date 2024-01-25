class DataAmount:

    def __init__(self, value: int) -> None:
        self.value: int = value

    @property
    def kb(self) -> float:
        return round(self.value/10**3, 2)

    @property
    def mb(self) -> float:
        return round(self.value/10**6, 2)
    
    @property
    def gb(self) -> float:
        return round(self.value/10**9, 2)
    
    @property
    def tb(self) -> float:
        return round(self.value/10**12, 2)