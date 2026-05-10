from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel # Pydantic - used for verification of input parameters
from database import Base, Base, engine, SessionLocal
from models import DailyInputs, DailyPredictions, EODInputs

app = FastAPI()
Base.metadata.create_all(bind=engine) # Creates the tables in the database based on the models defined in models.py

class DailyInputRequest(BaseModel):  
    date: datetime
    sleep_hours: float
    mood_level: int
    stress_level: int
    todays_contribution_time: float


class EODInputRequest(BaseModel):
    daily_input_id: int  # Reference to the daily_input record
    tasks_completed: int
    

@app.post("/daily-input")
def add_daily_inputs(data: DailyInputRequest):
    db = SessionLocal()
    
    daily_input = DailyInputs(
        date=data.date,
        sleep_hours=data.sleep_hours,
        mood_level=data.mood_level,
        stress_level=data.stress_level,
        todays_contribution_time=data.todays_contribution_time
    )
    
    # Calculate Predicted Score and Tasks Assigned based on the input data     
    score = 50
    
    score += data.sleep_hours * 2
    score += data.mood_level * 5
    score -= data.stress_level * 5
    score += data.todays_contribution_time * 2

    score = max(0, min(100, score))
    
    if score >= 80:
        tasks_assigned = 6
    elif score >= 60:
        tasks_assigned = 4
    else:
        tasks_assigned = 2
    
    db.add(daily_input)
    db.commit()
    db.refresh(daily_input)
    
    predictions = DailyPredictions(
        daily_input_id=daily_input.id,
        predicted_score=score,
        tasks_assigned=tasks_assigned
    )
    
    db.add(predictions)
    db.commit()
    db.refresh(predictions)
    
    return {
        "message": "Daily input added successfully",
        "daily_input_id": daily_input.id,
        "predicted_score": score,
        "tasks_assigned": tasks_assigned
    }
    
    db.close()

@app.post("/eod-input")
def add_eod_input(data: EODInputRequest):
    db = SessionLocal()

    eod_input = EODInputs(
        daily_input_id=data.daily_input_id,
        tasks_completed=data.tasks_completed
    )

    db.add(eod_input)
    db.commit()
    db.refresh(eod_input)
    prediction = db.query(DailyPredictions).filter(
        DailyPredictions.daily_input_id == data.daily_input_id
    ).first()

    if not prediction:
        db.close()
        return {
            "error": "No prediction found for the given daily_input_id"
        }

    prediction.completed_tasks = data.tasks_completed

    prediction.completion_rate = (
        (data.tasks_completed / prediction.tasks_assigned) * 100
        if prediction.tasks_assigned > 0 else 0
    )

    prediction.prediction_error = (
        prediction.completion_rate - prediction.predicted_score
    )

    db.commit()

    eod_input_id = eod_input.id
    completion_rate = prediction.completion_rate
    prediction_error = prediction.prediction_error

    db.close()

    return {
        "message": "EOD input added successfully",
        "eod_input_id": eod_input_id,
        "completion_rate": completion_rate,
        "prediction_error": prediction_error
    }


@app.get("/daily-input/{id}")
def get_daily_input(id: int):
    db = SessionLocal()
    daily_input = db.query(DailyInputs).filter(DailyInputs.id == id).first()
    if not daily_input:
        db.close()
        return {"error": "Daily input not found"}
    
    return {
        "id": daily_input.id,
        "date": daily_input.date,
        "sleep_hours": daily_input.sleep_hours,
        "mood_level": daily_input.mood_level,
        "stress_level": daily_input.stress_level,
        "todays_contribution_time": daily_input.todays_contribution_time    
    }
    
    db.close()


@app.get("/eod-input/{id}")
def get_edo_input(id:int):
    db = SessionLocal()
    
    eod_input = db.query(EODInputs).filter(EODInputs.id == id).first()
    if not eod_input:
        db.close()
        return {"error": "EOD input not found"}
    
    return {
        "id": eod_input.id,
        "daily_input_id": eod_input.daily_input_id,
        "tasks_completed": eod_input.tasks_completed
    }
    
    db.close()
    
@app.get("/prediction/{id}")
def get_daily_prediction(id:int):
    db = SessionLocal()
    
    prediction = db.query(DailyPredictions).filter(DailyPredictions.id == id).first()
    if not prediction:
        db.close()
        return {"error": "Prediction not found"}
    
    return {
        "id": prediction.id,
        "daily_input_id": prediction.daily_input_id,
        "predicted_score": prediction.predicted_score,
        "tasks_assigned": prediction.tasks_assigned,
        "completed_tasks": prediction.completed_tasks,
        "completion_rate": prediction.completion_rate,
        "prediction_error": prediction.prediction_error
    }
    db.close()

@app.post("/")
def root():
    return {"message": "Welcome to the API"}