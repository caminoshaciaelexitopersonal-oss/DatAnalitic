from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class WidgetConfig(BaseModel):
    id: str = Field(..., description="Widget unique ID")
    type: str = Field(..., description="chart type: bar, line, table, pie, kpi, scatter, area, etc.")
    title: Optional[str] = None

    # Data source handling
    dataset: Optional[str] = Field(None, description="Dataset name/path used by DataService")
    query: Optional[Dict[str, Any]] = Field(None, description="Direct DataService query object")
    filters: Optional[Dict[str, Any]] = None

    # Chart parameters
    xField: Optional[str] = None
    yField: Optional[str] = None
    series: Optional[List[str]] = None
    group_by: Optional[List[str]] = None
    agg: Optional[Dict[str, str]] = None
    agg_func: Optional[str] = "sum"
    max_rows: Optional[int] = 2000

    # Layout
    width: Optional[int] = Field(6, description="Grid width (1-12)")
    height: Optional[int] = Field(3, description="Grid height units")
    row: Optional[int] = Field(None, description="Row position")
    col: Optional[int] = Field(None, description="Column position")

    class Config:
        validate_assignment = True


class DashboardConfig(BaseModel):
    id: str = Field(..., description="Dashboard ID")
    title: str = Field(..., description="Human title")
    description: Optional[str] = None
    category: Optional[str] = "general"

    # Filters
    global_filters: Optional[Dict[str, Any]] = None

    # Layout block system
    layout: Dict[str, Any] = Field(..., description="Layout: {widgets: [...], grid: {...}}")

    @validator("layout")
    def layout_must_contain_widgets(cls, v):
        if "widgets" not in v:
            raise ValueError("layout must contain a widgets array")
        if not isinstance(v["widgets"], list):
            raise ValueError("layout.widgets must be a list")
        return v
