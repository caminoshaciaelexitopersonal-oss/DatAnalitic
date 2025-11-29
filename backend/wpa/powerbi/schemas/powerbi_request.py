from pydantic import BaseModel

class DataQueryRequest(BaseModel):
    query: str
    source: str = "local"
