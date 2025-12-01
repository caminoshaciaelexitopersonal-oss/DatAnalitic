from pydantic import BaseModel

class WidgetConfig(BaseModel):
    id: str
    type: str

class DashboardConfig(BaseModel):
    id: str
    title: str
