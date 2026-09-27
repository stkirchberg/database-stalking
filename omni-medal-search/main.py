from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session, sessionmaker, aliased
from thefuzz import fuzz
from typing import Optional
import os
from models import Person, Participation

DATABASE_URL = "sqlite:///olympiads.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI(title="Olympiad Results Explorer & Analysis")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def serve_ui():
    """Lädt das HTML-Frontend direkt beim Aufruf der Hauptadresse."""
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Fehler: index.html nicht gefunden.</h1><p>Bitte lege die Datei im selben Verzeichnis wie main.py ab.</p>"

@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Zeigt eine Übersicht aller Datensätze in der Datenbank"""
    total_persons = db.query(Person).count()
    total_participations = db.query(Participation).count()
    comp_counts = db.query(Participation.competition, func.count(Participation.id)).group_by(Participation.competition).all()
    return {
        "total_persons": total_persons,
        "total_participations": total_participations,
        "by_competition": dict(comp_counts)
    }

@app.get("/api/persons")
def search_persons(
    name: Optional[str] = Query(None, description="Name der Person suchen"),
    competition: Optional[str] = Query(None, description="Wettbewerb filtern"),
    award: Optional[str] = Query(None, description="Medaillen-Filter"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    query = db.query(Person).join(Person.participations)

    if competition:
        query = query.filter(Participation.competition == competition.upper())
    if award:
        query = query.filter(Participation.award.ilike(f"%{award}%"))

    persons = query.distinct().all()

    if name:
        search_name = name.lower()
        filtered_persons = []
        for p in persons:
            if fuzz.partial_ratio(search_name, p.full_name.lower()) >= 75:
                filtered_persons.append(p)
        persons = filtered_persons

    persons = persons[:limit]

    return [
        {
            "id": p.id,
            "name": p.full_name,
            "country": p.country,
            "participations": [
                {"competition": part.competition, "year": part.year, "score": part.score, "award": part.award} 
                for part in p.participations
            ]
        }
        for p in persons
    ]

@app.get("/api/crossover")
def get_crossover_winners(
    comp1: str = Query(..., description="Erster Wettbewerb"),
    award1: str = Query(..., description="Medaillentyp Wettbewerb 1"),
    comp2: str = Query(..., description="Zweiter Wettbewerb"),
    award2: str = Query(..., description="Medaillentyp Wettbewerb 2"),
    db: Session = Depends(get_db)
):
    """Komplexe Kombinationssuche: Findet Personen, die in zwei verschiedenen Wettbewerben spezifische Auszeichnungen gewonnen haben."""
    p1 = aliased(Participation)
    p2 = aliased(Participation)

    results = (
        db.query(Person)
        .join(p1, Person.id == p1.person_id)
        .join(p2, Person.id == p2.person_id)
        .filter(
            p1.competition == comp1.upper(),
            p1.award.ilike(f"%{award1}%"),
            p2.competition == comp2.upper(),
            p2.award.ilike(f"%{award2}%")
        )
        .distinct()
        .all()
    )

    return [
        {
            "id": p.id,
            "name": p.full_name,
            "country": p.country,
            "participations": [{"competition": part.competition, "year": part.year, "score": part.score, "award": part.award} for part in p.participations]
        }
        for p in results
    ]