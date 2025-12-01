from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from backend.core.database import Base

class Dashboard(Base):
    __tablename__ = "powerbi_dashboards"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)

    widgets = relationship("Widget", back_populates="dashboard", cascade="all, delete-orphan")

class Widget(Base):
    __tablename__ = "powerbi_widgets"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    type = Column(String, nullable=False) # e.g., 'bar', 'line', 'table'
    config = Column(JSON, nullable=False) # Stores xField, yField, series, data source info, etc.
    layout = Column(JSON, nullable=False) # Stores x, y, w, h for react-grid-layout

    dashboard_id = Column(Integer, ForeignKey("powerbi_dashboards.id"))
    dashboard = relationship("Dashboard", back_populates="widgets")
