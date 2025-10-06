from datetime import datetime
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer

from app.exceptions import ApiError
from app.models import Checkin, CheckinCreate, Habit, HabitCreate

app = FastAPI(title="Habit Tracker", version="0.1.0")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str = Depends(oauth2_scheme)):
    if token != "fake-token":
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"user_id": 1}


@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError):
    return JSONResponse(
        status_code=exc.status,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, str) else "http_error"
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": "http_error", "message": detail}},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": {"code": "validation_error", "message": str(exc)}},
    )


_DB = {"habits": [], "checkins": []}
_habit_id_counter = 0
_checkin_id_counter = 0


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/habits", response_model=Habit)
def create_habit(habit: HabitCreate, current_user=Depends(get_current_user)):
    global _habit_id_counter
    _habit_id_counter += 1
    new_habit = Habit(id=_habit_id_counter, owner_id=current_user["user_id"], **habit.model_dump())
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
    raise ApiError(code="not_found", message="habit not found", status=404)


@app.post("/habits/{habit_id}/checkins", response_model=Checkin)
def add_checkin(habit_id: int, checkin: CheckinCreate, current_user=Depends(get_current_user)):
    habit = next(
        (h for h in _DB["habits"] if h.id == habit_id and h.owner_id == current_user["user_id"]),
        None,
    )
    if not habit:
        raise ApiError(code="not_found", message="habit not found", status=404)
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
        raise ApiError(code="not_found", message="habit not found", status=404)
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
