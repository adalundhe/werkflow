from pydantic import BaseModel
from typing import (
    Dict,
    Any
)


class Env(BaseModel):
    pass

    @classmethod
    def get_parse_map(self) -> Dict[str, Any]:
        return {}