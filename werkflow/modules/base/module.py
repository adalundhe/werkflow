class Module:
    module_enabled=True
    dependencies=[]
    
    def __init__(self) -> None:
        pass

    async def close(self):
        pass

    def abort(self):
        pass