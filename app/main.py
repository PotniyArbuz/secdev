from datetime import datetime
from pathlib import Path
from typing import List
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base
from app.db import Checkin as CheckinDB
from app.db import Habit as HabitDB
from app.errors import problem
from app.models import Checkin, CheckinCreate, Habit, HabitCreate
from app.upload import secure_save

app = FastAPI(title="Habit Tracker", version="0.1.0")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

UPLOAD_DIR = "uploads"
Path(UPLOAD_DIR).mkdir(exist_ok=True)


engine = create_engine("sqlite:///habits.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_scheme)):
    if token != "fake-token":
        return problem(401, "Unauthorized", "Invalid token", extras={"type": "about:blank"})
    return {"user_id": 1}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    errors_list = []
    for err in exc.errors():
        loc = ".".join(str(loc_part) for loc_part in err.get("loc", []))
        msg = err.get("msg", "")
        errors_list.append({"loc": loc, "msg": msg, "type": err.get("type")})

    return JSONResponse(
        status_code=422,
        content={
            "type": "about:blank",
            "title": "Invalid input",
            "status": 422,
            "detail": errors_list,
            "correlation_id": str(uuid4()),
        },
        headers={"Content-Type": "application/problem+json"},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict) and "type" in exc.detail:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
            headers={"Content-Type": "application/problem+json"},
        )
    if exc.status_code == 401 and exc.detail == "Not authenticated":
        return problem(401, "Unauthorized", "Invalid token")
    return problem(exc.status_code, exc.detail or "Error", str(exc.detail))


@app.post("/upload")
async def upload_avatar(file: UploadFile, current_user=Depends(get_current_user)):
    try:
        data = await file.read()
        path = secure_save(UPLOAD_DIR, data)
        return {"filename": str(path)}
    except ValueError as e:
        return problem(400, "Invalid file", str(e))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/habits", response_model=Habit)
def create_habit(
    habit: HabitCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_habit = HabitDB(
        owner_id=current_user["user_id"],
        created_at=datetime.now(),
        **habit.model_dump(),
    )
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    return db_habit


@app.get("/habits", response_model=List[Habit])
def list_habits(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(HabitDB).filter(HabitDB.owner_id == current_user["user_id"]).all()


@app.get("/habits/{habit_id}", response_model=Habit)
def get_habit(
    habit_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    habit = (
        db.query(HabitDB)
        .filter(
            HabitDB.id == habit_id,
            HabitDB.owner_id == current_user["user_id"],
        )
        .first()
    )
    if not habit:
        return problem(404, "Not found", "Habit not found")
    return habit


@app.post("/habits/{habit_id}/checkins", response_model=Checkin)
def add_checkin(
    habit_id: int,
    checkin: CheckinCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    habit = (
        db.query(HabitDB)
        .filter(
            HabitDB.id == habit_id,
            HabitDB.owner_id == current_user["user_id"],
        )
        .first()
    )
    if not habit:
        return problem(404, "Not found", "Habit not found")
    db_checkin = CheckinDB(habit_id=habit_id, **checkin.model_dump())
    db.add(db_checkin)
    db.commit()
    db.refresh(db_checkin)
    return db_checkin


@app.get("/habits/{habit_id}/checkins", response_model=List[Checkin])
def list_checkins(
    habit_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    habit = (
        db.query(HabitDB)
        .filter(
            HabitDB.id == habit_id,
            HabitDB.owner_id == current_user["user_id"],
        )
        .first()
    )
    if not habit:
        return problem(404, "Not found", "Habit not found")
    return db.query(CheckinDB).filter(CheckinDB.habit_id == habit_id).all()


@app.get("/stats")
def get_stats(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_habits = db.query(HabitDB).filter(HabitDB.owner_id == current_user["user_id"]).all()
    user_checkins = (
        db.query(CheckinDB).filter(CheckinDB.habit_id.in_([h.id for h in user_habits])).all()
    )
    return {
        "total_habits": len(user_habits),
        "total_checkins": len(user_checkins),
        "last_update": datetime.now().isoformat(),
    }
