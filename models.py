from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from database import Base
   
class DailyInputs(Base):
    __tablename__ = "daily_inputs"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime)
    sleep_hours = Column(Float)
    mood_level = Column(Integer)
    stress_level = Column(Integer)
    todays_contribution_time = Column(Float)
    
    
class DailyPredictions(Base):
    __tablename__ = "daily_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    daily_input_id = Column(Integer, ForeignKey("daily_inputs.id"))  # Reference to the daily_input record
    predicted_score = Column(Float)  # should come from daily inputs
    tasks_assigned = Column(Integer)  # should come from daily inputs
    completed_tasks = Column(Integer)
    completion_rate = Column(Float)
    prediction_error = Column(Float)
    
class EODInputs(Base):
    __tablename__ = "eod_inputs"
    
    id = Column(Integer, primary_key=True, index=True)
    daily_input_id = Column(Integer, ForeignKey("daily_inputs.id"))  # Reference to the daily_input record
    tasks_completed = Column(Integer)