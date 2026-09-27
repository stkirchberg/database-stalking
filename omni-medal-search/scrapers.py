import time
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scrape_imo(start_year: int = 1959, end_year: int = 2024) -> List[Dict[str, Any]]:
    results = []
    print("--- Lade IMO Daten ---")
    
    with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=10.0) as client:
        for year in range(start_year, end_year + 1):
            if year == 1980:
                continue
            
            print(f"IMO {year}...", end="\r", flush=True)
            url = f"https://www.imo-official.org/year_individual_r.aspx?year={year}"
            try:
                response = client.get(url)
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.text, "html.parser")
                table = soup.find("table", {"class": "grid"})
                if not table:
                    continue

                for row in table.find_all("tr")[1:]:
                    cols = [td.get_text(strip=True) for td in row.find_all("td")]
                    if len(cols) < 5:
                        continue
                    
                    name = cols[0]
                    country = cols[1]
                    total_score = float(cols[-3]) if cols[-3].replace('.', '', 1).isdigit() else None
                    award = cols[-1] if cols[-1] else "Participant"

                    results.append({
                        "name": name,
                        "country": country,
                        "competition": "IMO",
                        "year": year,
                        "score": total_score,
                        "award": award
                    })
                time.sleep(0.3)
            except Exception as e:
                print(f"Fehler bei {year}: {e}")
                
    print("\nIMO abgeschlossen.")
    return results

def scrape_ioi(start_year: int = 1989, end_year: int = 2024) -> List[Dict[str, Any]]:
    results = []
    print("--- Lade IOI Daten ---")
    
    with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=10.0) as client:
        for year in range(start_year, end_year + 1):
            print(f"IOI {year}...", end="\r", flush=True)
            url = f"https://stats.ioinformatics.org/results/{year}"
            try:
                response = client.get(url)
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.text, "html.parser")
                table = soup.find("table")
                if not table:
                    continue

                for row in table.find_all("tr")[1:]:
                    cols = [td.get_text(strip=True) for td in row.find_all("td")]
                    if len(cols) < 4:
                        continue

                    name = cols[0]
                    country = cols[1]
                    score = float(cols[2]) if cols[2].replace('.', '', 1).isdigit() else None
                    award = cols[-1] if cols[-1] else "Participant"

                    results.append({
                        "name": name,
                        "country": country,
                        "competition": "IOI",
                        "year": year,
                        "score": score,
                        "award": award
                    })
                time.sleep(0.3)
            except Exception as e:
                print(f"Fehler bei {year}: {e}")

    print("\nIOI abgeschlossen.")
    return results

def scrape_imc(start_year: int = 1994, end_year: int = 2024) -> List[Dict[str, Any]]:
    results = []
    print("--- Lade IMC Daten ---")
    
    with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=10.0) as client:
        for year in range(start_year, end_year + 1):
            print(f"IMC {year}...", end="\r", flush=True)
            url = f"https://www.imc-math.org.uk/imc{year}/results.html"
            try:
                response = client.get(url)
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.text, "html.parser")
                table = soup.find("table")
                if not table:
                    continue

                for row in table.find_all("tr")[1:]:
                    cols = [td.get_text(strip=True) for td in row.find_all("td")]
                    if len(cols) < 3:
                        continue

                    name = cols[0]
                    university = cols[1] if len(cols) > 1 else ""
                    award = cols[-1] if cols[-1] else "Participant"

                    results.append({
                        "name": name,
                        "country": university,
                        "competition": "IMC",
                        "year": year,
                        "score": None,
                        "award": award
                    })
                time.sleep(0.3)
            except Exception as e:
                print(f"Fehler bei {year}: {e}")

    print("\nIMC abgeschlossen.")
    return results

def scrape_icpc(start_year: int = 2000, end_year: int = 2024) -> List[Dict[str, Any]]:
    results = []
    print("--- Lade ICPC Daten ---")
    
    with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=10.0) as client:
        for year in range(start_year, end_year + 1):
            print(f"ICPC {year}...", end="\r", flush=True)
            url = f"https://icpc.global/api/worldfinals/results/{year}"
            try:
                response = client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    for team in data.get("teams", []):
                        award = team.get("rank", "Participant")
                        university = team.get("university", "")
                        
                        for member in team.get("contestants", []):
                            results.append({
                                "name": f"{member.get('firstName', '')} {member.get('lastName', '')}".strip(),
                                "country": university,
                                "competition": "ICPC",
                                "year": year,
                                "score": float(team.get("solved", 0)),
                                "award": f"Rank {award}" if isinstance(award, int) else str(award)
                            })
                time.sleep(0.3)
            except Exception as e:
                print(f"Fehler bei {year}: {e}")

    print("\nICPC abgeschlossen.")
    return results