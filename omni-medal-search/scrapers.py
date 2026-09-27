import time
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scrape_imo(start_year: int = 1959, end_year: int = 2024) -> List[Dict[str, Any]]:
    """Scrapt die IMO-Ergebnisse von imo-official.org"""
    results = []
    print("--- Starte IMO Scraper ---")
    
    with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=15.0) as client:
        for year in range(start_year, end_year + 1):
            if year == 1980: 
                continue
            
            url = f"https://www.imo-official.org/year_individual_r.aspx?year={year}"
            print(f"Lade IMO {year}...")
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
                time.sleep(0.5)
            except Exception as e:
                print(f"Fehler bei IMO {year}: {e}")
                
    return results

def scrape_ioi(start_year: int = 1989, end_year: int = 2024) -> List[Dict[str, Any]]:
    """Scrapt die IOI-Ergebnisse von stats.ioinformatics.org"""
    results = []
    print("--- Starte IOI Scraper ---")
    
    with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=15.0) as client:
        for year in range(start_year, end_year + 1):
            url = f"https://stats.ioinformatics.org/results/{year}"
            print(f"Lade IOI {year}...")
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
                time.sleep(0.5)
            except Exception as e:
                print(f"Fehler bei IOI {year}: {e}")

    return results