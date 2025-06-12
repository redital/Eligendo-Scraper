import requests
import json
import os
from tqdm import tqdm

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3",
    # 'Accept-Encoding': 'gzip, deflate, br, zstd',
    "Origin": "https://elezioni.interno.gov.it",
    "DNT": "1",
    "Sec-GPC": "1",
    "Connection": "keep-alive",
    "Referer": "https://elezioni.interno.gov.it/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "Priority": "u=0",
    # Requests doesn't support trailers
    # 'TE': 'trailers',
}

dominio = "https://eleapi.interno.gov.it"
uri = "/siel/PX/votantiFI/DE/20250608/TE/09/SK/{:02d}/RE/{:02d}"
url = dominio + uri

save = False
codici_regioni = {
    "PIEMONTE": 1,
    "VALLE D'AOSTA": 2,
    "LOMBARDIA": 3,
    "TRENTINO-ALTO ADIGE": 4,
    "VENETO": 5,
    "FRIULI-VENEZIA GIULIA": 6,
    "LIGURIA": 7,
    "EMILIA-ROMAGNA": 8,
    "TOSCANA": 9,
    "UMBRIA": 10,
    "MARCHE": 11,
    "LAZIO": 12,
    "ABRUZZO": 13,
    "MOLISE": 14,
    "CAMPANIA": 15,
    "PUGLIA": 16,
    "BASILICATA": 17,
    "CALABRIA": 18,
    "SICILIA": 19,
    "SARDEGNA": 20,
}

base_dir = os.getcwd()
res_dir_name = "results/Votanti province"
res_dir = base_dir + "/" + res_dir_name

province = {}

os.chdir(res_dir)
for nome_regione, numero_regione in tqdm(codici_regioni.items()):
    province[nome_regione] = []

    if not os.path.isdir(nome_regione):
        os.mkdir(nome_regione)
    os.chdir(nome_regione)

    for numero_quesito in range(1, 6):

        response = requests.get(
            url.format(numero_quesito, numero_regione), headers=headers
        )
        data = response.json()
        province[nome_regione] = data
        if save:
            json_formatted_str = json.dumps(data, indent=4)

            with open(
                "votanti_province_regione_{}_quesito_{:02d}.json".format(
                    nome_regione, numero_quesito
                ),
                "w",
                encoding="utf8",
            ) as f:
                # json.dump(f, data, indent=4)
                f.write(json_formatted_str)
    os.chdir(res_dir)
os.chdir(base_dir)

province_unico = []
for p in province.values():
    province_unico.extend(p["enti"]["enti_f"] ) 

codici = {p["desc"]: p["cod"] for p in province_unico}


print(codici)
print(dict(sorted(codici.items(), key=lambda item: item[1])))


codici = {
    k: [
        {
            "nome": c["desc"],
            "codice": c["cod"],
            "codice_regione": v["enti"]["ente_p"]["cod"],
        }
        for c in v["enti"]["enti_f"]
    ]
    for k, v in province.items()
}


print(codici)

with open("codici province.json", "w", encoding="utf8") as f:
    json_formatted_str = json.dumps(codici, indent=4)
    f.write(json_formatted_str)

print("ok")