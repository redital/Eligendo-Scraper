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
uri = "/siel/PX/scrutiniFI/DE/20250608/TE/09/RE/{:02d}/PR/{:03d}"
url = dominio + uri

save = True

with open("codici province.json","r",encoding="utf8") as f:
    codici_province = json.load(f)

base_dir = os.getcwd()
res_dir_name = "results/Scrutini province"
res_dir = base_dir + "/" + res_dir_name


os.chdir(res_dir)
for regione in (pbar:= tqdm(codici_province,"Regione")):
    pbar.set_postfix_str(regione)
    if not os.path.isdir(regione):
        os.mkdir(regione)
    os.chdir(regione)

    for info_provincia in (sbar:=tqdm(codici_province[regione], "Provincia", position=1, leave=False)):
        nome_provincia, numero_provincia = info_provincia["nome"],info_provincia["codice"]
        numero_regione = info_provincia["codice_regione"]
        sbar.set_postfix_str(nome_provincia)
        
        response = requests.get(
            url.format(numero_regione, numero_provincia), headers=headers
        )
        data = response.json()
        if save:
            json_formatted_str = json.dumps(data, indent=4)

            with open(
                "scrutini_provincia_{}.json".format(
                    nome_provincia
                ),
                "w",
                encoding="utf8",
            ) as f:
                # json.dump(f, data, indent=4)
                f.write(json_formatted_str)
        os.chdir(res_dir+"\\"+regione)
    os.chdir(res_dir)

os.chdir(base_dir)

