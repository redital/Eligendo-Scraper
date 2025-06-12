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

uri = "/siel/PX/votantiFIZ/DE/20250608/TE/09/SK/{:02d}/PR/{:03d}/CM/{:04d}"
url = dominio + uri

save = True

with open("codici comuni.json","r",encoding="utf8") as f:
    codici_comuni = json.load(f)

codici_comuni = {k:[i for i in v if i["disponibilità_sezioni"]] for k,v in codici_comuni.items()}


base_dir = os.getcwd()
res_dir_name = "results/Votanti sezioni"
res_dir = base_dir + "/" + res_dir_name

sezioni = {}

os.chdir(res_dir)
for provincia in (pbar:= tqdm(codici_comuni,"Provincia")):
    pbar.set_postfix_str(provincia)
    if not os.path.isdir(provincia):
        os.mkdir(provincia)
    os.chdir(provincia)

    for info_comune in (sbar:=tqdm(codici_comuni[provincia], "Comune", position=1, leave=False)):
        nome_comune, numero_comune = info_comune["nome"],info_comune["codice"]
        numero_provincia = info_comune["codice_provincia"]
        sbar.set_postfix_str(nome_comune)
        
        sezioni[nome_comune] = []
        if not os.path.isdir(nome_comune):
            os.mkdir(nome_comune)
        os.chdir(nome_comune)
        
        for numero_quesito in range(1, 6):

            response = requests.get(
                url.format(numero_quesito, numero_provincia,numero_comune), headers=headers
            )
            data = response.json()
            sezioni[nome_comune] = data
            if save:
                json_formatted_str = json.dumps(data, indent=4)

                with open(
                    "votanti_sezioni_comune_{}_quesito_{:02d}.json".format(
                        nome_comune, numero_quesito
                    ),
                    "w",
                    encoding="utf8",
                ) as f:
                    # json.dump(f, data, indent=4)
                    f.write(json_formatted_str)
        os.chdir(res_dir+"\\"+provincia)
    os.chdir(res_dir)

os.chdir(base_dir)
exit()



