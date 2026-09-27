from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Person, Participation
from scrapers import scrape_imo, scrape_ioi, scrape_imc, scrape_icpc

DATABASE_URL = "sqlite:///olympiads.db"

def run_import():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    print("Starte Gesamtexport aller Wettbewerbe...")

    all_data = []
    all_data.extend(scrape_imo(1959, 2024))
    all_data.extend(scrape_ioi(1989, 2024))
    all_data.extend(scrape_imc(1994, 2024))
    all_data.extend(scrape_icpc(2000, 2024))

    print(f"\nInsgesamt {len(all_data)} Datensätze heruntergeladen. Speichere in Datenbank...")

    person_cache = {}

    for item in all_data:
        person_key = (item["name"].strip(), (item["country"] or "").strip())

        if person_key not in person_cache:
            person = session.query(Person).filter_by(
                full_name=person_key[0], 
                country=person_key[1]
            ).first()

            if not person:
                person = Person(full_name=person_key[0], country=person_key[1])
                session.add(person)
                session.flush()

            person_cache[person_key] = person.id
        
        person_id = person_cache[person_key]

        participation = Participation(
            person_id=person_id,
            competition=item["competition"],
            year=item["year"],
            score=item["score"],
            award=item["award"]
        )
        session.add(participation)

    session.commit()
    print("Import erfolgreich abgeschlossen!")

if __name__ == "__main__":
    run_import()