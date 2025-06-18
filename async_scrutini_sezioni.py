import asyncio
import os
import json
import requests
from tqdm.asyncio import tqdm_asyncio
from pathlib import Path

# CONFIGURAZIONE
SKIP_EXISTING = True
MAX_CONCURRENT_REQUESTS = 50

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3",
    "Origin": "https://elezioni.interno.gov.it",
    "DNT": "1",
    "Sec-GPC": "1",
    "Referer": "https://elezioni.interno.gov.it/",
}

BASE_URL = "https://eleapi.interno.gov.it"
RESULTS_DIR = Path("results/Scrutini fuorisede")


def safe_filename(nome_comune, numero_sezione):
    return f"scrutini_comune_{''.join(e for e in nome_comune.replace(' ', '_') if e.isalnum())}_sezione_{numero_sezione}.json"


async def fetch_sezioni(numero_regione, numero_provincia, numero_comune):
    url = f"{BASE_URL}/siel/PX/elenchiFIZ/DE/20250608/TE/09/RE/{numero_regione:02d}/PR/{numero_provincia:03d}/CM/{numero_comune:04d}"

    def _get():
        r = requests.get(url, headers=HEADERS)
        r.raise_for_status()
        return [e["cod_ente"] for e in r.json()["scheda"][0]["enti"]]

    return await asyncio.to_thread(_get)


async def fetch_scrutini(nome_comune, numero_provincia, numero_comune, numero_sezione, output_dir, semaphore):
    filename = safe_filename(nome_comune, numero_sezione)
    output_path = output_dir / filename

    if SKIP_EXISTING and output_path.exists():
        return

    url = f"{BASE_URL}/siel/PX/scrutiniFI/DE/20250608/TE/09/PR/{numero_provincia:03d}/CM/{numero_comune:04d}/SZ/{numero_sezione:04d}"

    async with semaphore:
        def _get():
            r = requests.get(url, headers=HEADERS)
            r.raise_for_status()
            return r.json()

        try:
            data = await asyncio.to_thread(_get)
            with open(output_path, "w", encoding="utf8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"[Errore] {url} → {e}")


async def main():
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    with open("codici province.json", "r", encoding="utf8") as f:
        codici_province = json.load(f)
    with open("codici comuni.json", "r", encoding="utf8") as f:
        codici_comuni = json.load(f)

    codici_comuni = {
        k: [i for i in v if i["disponibilità_sezioni"]]
        for k, v in codici_comuni.items()
    }

    tasks = []

    for regione in (pbar:= tqdm_asyncio(codici_province,"Regione")):
        pbar.set_postfix_str(regione)
        for info_provincia in (sbar:=tqdm_asyncio(codici_province[regione], "Provincia", position=1, leave=False)):
            nome_provincia = info_provincia["nome"]
            numero_provincia = info_provincia["codice"]
            numero_regione = info_provincia["codice_regione"]
            sbar.set_postfix_str(nome_provincia)

            provincia_dir = RESULTS_DIR / regione / nome_provincia
            provincia_dir.mkdir(parents=True, exist_ok=True)

            comuni = codici_comuni.get(nome_provincia, [])
            sezioni_tasks = []
            for comune in (cbar:=tqdm_asyncio(comuni, "Comune", position=2, leave=False)):
                nome_comune = comune["nome"]
                numero_comune = comune["codice"]
                cbar.set_postfix_str(nome_comune)
                sezioni_tasks.append(fetch_sezioni(numero_regione, numero_provincia, numero_comune))
            
            sezioni = await tqdm_asyncio.gather(*sezioni_tasks, desc="Sezioni")
            for sezioni, comune in zip(sezioni, comuni):

                #try:
                #    sezioni = await fetch_sezioni(numero_regione, numero_provincia, numero_comune)
                #except Exception as e:
                #    print(f"[Errore sezioni] {nome_comune} ({numero_comune}): {e}")
                #    continue

                for numero_sezione in sezioni:
                    tasks.append(
                        fetch_scrutini(
                            nome_comune,
                            numero_provincia,
                            numero_comune,
                            numero_sezione,
                            provincia_dir,
                            semaphore,
                        )
                    )

    await tqdm_asyncio.gather(*tasks, desc="Scrutini")


if __name__ == "__main__":
    asyncio.run(main())
