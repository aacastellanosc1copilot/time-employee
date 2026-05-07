from datetime import datetime
from typing import Generator, List, Optional

from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import Column, Integer, DateTime, create_engine, desc, null
from sqlalchemy.orm import declarative_base, sessionmaker, Session

DATABASE_URL = "sqlite:///./app.db"
connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()
templates = Jinja2Templates(directory="templates")


class TimeEntry(Base):
    __tablename__ = "time_entries"
    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)


Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_open_entry(db: Session) -> Optional[TimeEntry]:
    return db.query(TimeEntry).filter(TimeEntry.end_time.is_(None)).order_by(desc(TimeEntry.start_time)).first()


@app.get("/")
def index(request: Request, db: Session = Depends(get_db)):
    entries = db.query(TimeEntry).order_by(desc(TimeEntry.start_time)).all()
    formatted = []
    for e in entries:
        formatted.append({
            "id": e.id,
            "start": e.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end": e.end_time.strftime("%Y-%m-%d %H:%M:%S") if e.end_time else None,
        })
    open_entry = get_open_entry(db)
    status = {
        "is_open": bool(open_entry),
        "open_since": open_entry.start_time.strftime("%Y-%m-%d %H:%M:%S") if open_entry else None,
    }
    return templates.TemplateResponse("index.html", {"request": request, "entries": formatted, "status": status})


@app.post("/entrada")
def entrada(db: Session = Depends(get_db)):
    # If there is an open entry, do not create another; redirect back
    if get_open_entry(db):
        return RedirectResponse("/", status_code=303)
    now = datetime.now()
    entry = TimeEntry(start_time=now)
    db.add(entry)
    db.commit()
    return RedirectResponse("/", status_code=303)


@app.post("/salida")
def salida(db: Session = Depends(get_db)):
    open_entry = get_open_entry(db)
    if not open_entry:
        return RedirectResponse("/", status_code=303)
    open_entry.end_time = datetime.now()
    db.add(open_entry)
    db.commit()
    return RedirectResponse("/", status_code=303)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)