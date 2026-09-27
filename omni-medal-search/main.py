from fastapi import FastAPI, Depends, Query
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from typing import List, Optional
from models import Person, Participation

DATABASE_URL = "sqlite:///olympiads.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI(title="Olympiad Results Explorer")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"message": "Willkommen bei der Olympiaden-Datenbank API! Gehe zu /docs um die Ergebnisse zu durchsuchen."}

@app.get("/persons")
def search_persons(
    name: Optional[str] = Query(None, description="Name der Person suchen"),
    competition: Optional[str] = Query(None, description="Wettbewerb filtern (IMO, IOI, IMC, ICPC)"),
    db: Session = Depends(get_db)
):
    """Durchsucht Personen und liefert ihre Teilnahmen und Medaillen zurück"""
    query = db.query(Person)

    if name:
        query = query.filter(Person.full_name.ilike(f"%{name}%"))
        
    if competition:
        query = query.join(Person.participations).filter(Participation.competition == competition.upper())

    persons = query.limit(50).all()

    return [
        {
            "id": p.id,
            "name": p.full_name,
            "country_or_uni": p.country,
            "participations": [
                {
                    "competition": part.competition,
                    "year": part.year,
                    "score": part.score,
                    "award": part.award
                }
                for part.participations in [p.participations] for part in part.participations
            ]
        }
        for p in persons
    ]

@app.get("/persons/{person_id}")
def get_person_details(person_id: int, db: Session = Depends(get_db)):
    """Holt die vollständige Historie einer einzelnen Person"""
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        return {"error": "Person nicht gefunden"}
    
    return {
        "id": person.id,
        "name": person.full_name,
        "country": person.country,
        "history": [
            {
                "competition": part.competition,
                "year": part.year,
                "score": part.score,
                "award": part.award
            }
            for part.participations in [person.participations] for part in part.participations
        ]
    }