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
uri = "/siel/PX/scrutiniFI/DE/20250608/TE/09/RE/{:02d}/PR/{:03d}/CM/{:04d}/SZ/{:04d}"
url = dominio + uri

save = True

with open("codici province.json","r",encoding="utf8") as f:
    codici_province = json.load(f)
with open("codici comuni.json","r",encoding="utf8") as f:
    codici_comuni = json.load(f)

codici_comuni = {k:[i for i in v if i["disponibilità_sezioni"]] for k,v in codici_comuni.items()}

base_dir = os.getcwd()
res_dir_name = "results/Scrutini sezioni"
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
        
        if not os.path.isdir(nome_provincia):
            os.mkdir(nome_provincia)
        os.chdir(nome_provincia)
        for info_comune in (cbar:=tqdm(codici_comuni[nome_provincia], "Comune", position=2, leave=False)): 
            nome_comune, numero_comune = info_comune["nome"],info_comune["codice"]
            numero_provincia = info_comune["codice_provincia"]

            # Rispetto che leggere un file per sapere la lunghezza per ciclare conviene a sto punto meglio mettere un numero enorme e smettere quando non ritorna nulla
            #nome_file_scrutini_comune = "scrutini_comune_{}.json".format(''.join(e for e in nome_comune.replace(" ","_") if e.isalnum()))
            #path_scrutini_comune = base_dir + "/Scrutini comuni/" + regione + "/" + nome_provincia + "/" + nome_file_scrutini_comune

            url_elenco_sezioni = dominio + "/siel/PX/elenchiFIZ/DE/20250608/TE/09/RE/{:02d}/PR/{:03d}/CM/{:04d}"
            response = requests.get(
                url_elenco_sezioni.format(numero_regione, numero_provincia, numero_comune), headers=headers
            )
            data_elenco = response.json()["scheda"][0]["enti"]
            elenco = [i["cod_ente"] for i in data_elenco]

            for numero_sezione in elenco:

                response = requests.get(
                    url.format(numero_regione, numero_provincia, numero_comune, numero_sezione), headers=headers
                )

                
                try:
                    data = response.json()
                except:
                    print(url.format(numero_regione, numero_provincia, numero_provincia))
                    print(response)
                    print(response.text)
                    exit()
                if save:
                    json_formatted_str = json.dumps(data, indent=4)

                    with open(
                        "scrutini_comune_{}.json".format(
                            ''.join(e for e in nome_comune.replace(" ","_") if e.isalnum())
                        ),
                        "w",
                        encoding="utf8",
                    ) as f:
                        # json.dump(f, data, indent=4)
                        f.write(json_formatted_str)
        os.chdir(res_dir+"\\"+regione)
    os.chdir(res_dir)

os.chdir(base_dir)

