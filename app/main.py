from datetime import datetime
from pathlib import Path
from typing import List
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer

from app.errors import problem
from app.models import Checkin, CheckinCreate, Habit, HabitCreate
from app.upload import secure_save

app = FastAPI(title="Habit Tracker", version="0.1.0")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

UPLOAD_DIR = "uploads"
Path(UPLOAD_DIR).mkdir(exist_ok=True)


def get_current_user(token: str = Depends(oauth2_scheme)):
    if token != "fake-token":
        raise HTTPException(
            status_code=401,
            detail={
                "type": "about:blank",
                "title": "Unauthorized",
                "status": 401,
                "detail": "Invalid token",
                "correlation_id": str(uuid4()),
            },
            headers={"Content-Type": "application/problem+json"},
        )
    return {"user_id": 1}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    message = "Periodicity must be 'daily' or 'weekly'" if "periodicity" in str(exc) else str(exc)
    return problem(422, "Invalid input", message)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict) and "type" in exc.detail:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
            headers={"Content-Type": "application/problem+json"},
        )
    if exc.status_code == 401 and exc.detail == "Not authenticated":
        return JSONResponse(
            status_code=401,
            content={
                "type": "about:blank",
                "title": "Unauthorized",
                "status": 401,
                "detail": "Invalid token",
                "correlation_id": str(uuid4()),
            },
            headers={"Content-Type": "application/problem+json"},
        )
    return problem(exc.status_code, exc.detail or "Error", str(exc.detail))


_DB = {"habits": [], "checkins": []}
_habit_id_counter = 0
_checkin_id_counter = 0


@app.post("/upload")
async def upload_avatar(file: UploadFile, current_user=Depends(get_current_user)):
    try:
        data = await file.read()
        path = secure_save(UPLOAD_DIR, data)
        return {"filename": path}
    except ValueError as e:
        return problem(400, "Invalid file", str(e))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/habits", response_model=Habit)
def create_habit(habit: HabitCreate, current_user=Depends(get_current_user)):
    global _habit_id_counter
    _habit_id_counter += 1
    new_habit = Habit(
        id=_habit_id_counter,
        owner_id=current_user["user_id"],
        created_at=datetime.now(),
        **habit.model_dump(),
    )
    _DB["habits"].append(new_habit)
    return new_habit


@app.get("/habits", response_model=List[Habit])
def list_habits(current_user=Depends(get_current_user)):
    return [h for h in _DB["habits"] if h.owner_id == current_user["user_id"]]


@app.get("/habits/{habit_id}", response_model=Habit)
def get_habit(habit_id: int, current_user=Depends(get_current_user)):
    for h in _DB["habits"]:
        if h.id == habit_id and h.owner_id == current_user["user_id"]:
            return h
    return problem(404, "Not found", "Habit not found")


@app.post("/habits/{habit_id}/checkins", response_model=Checkin)
def add_checkin(habit_id: int, checkin: CheckinCreate, current_user=Depends(get_current_user)):
    habit = next(
        (h for h in _DB["habits"] if h.id == habit_id and h.owner_id == current_user["user_id"]),
        None,
    )
    if not habit:
        return problem(404, "Not found", "Habit not found")
    global _checkin_id_counter
    _checkin_id_counter += 1
    new_checkin = Checkin(id=_checkin_id_counter, habit_id=habit_id, **checkin.model_dump())
    _DB["checkins"].append(new_checkin)
    return new_checkin


@app.get("/habits/{habit_id}/checkins", response_model=List[Checkin])
def list_checkins(habit_id: int, current_user=Depends(get_current_user)):
    habit = next(
        (h for h in _DB["habits"] if h.id == habit_id and h.owner_id == current_user["user_id"]),
        None,
    )
    if not habit:
        return problem(404, "Not found", "Habit not found")
    return [c for c in _DB["checkins"] if c.habit_id == habit_id]


@app.get("/stats")
def get_stats(current_user=Depends(get_current_user)):
    user_habits = [h for h in _DB["habits"] if h.owner_id == current_user["user_id"]]
    user_checkins = [c for c in _DB["checkins"] if any(h.id == c.habit_id for h in user_habits)]
    return {
        "total_habits": len(user_habits),
        "total_checkins": len(user_checkins),
        "last_update": datetime.now().isoformat(),
    }
