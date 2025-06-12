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
uri = "/siel/PX/votantiFI/DE/20250608/TE/09/SK/{:02d}/PR/{:03d}"
url = dominio + uri

save = False
codici_province = {
    "AGRIGENTO": 1,
    "ALESSANDRIA": 2,
    "ANCONA": 3,
    "AOSTA": 4,
    "AREZZO": 5,
    "ASCOLI PICENO": 6,
    "ASTI": 7,
    "AVELLINO": 8,
    "BARI": 9,
    "BELLUNO": 10,
    "BENEVENTO": 11,
    "BERGAMO": 12,
    "BOLOGNA": 13,
    "BOLZANO": 14,
    "BRESCIA": 15,
    "BRINDISI": 16,
    "CAGLIARI": 17,
    "CALTANISSETTA": 18,
    "CAMPOBASSO": 19,
    "CASERTA": 20,
    "CATANIA": 21,
    "CATANZARO": 22,
    "CHIETI": 23,
    "COMO": 24,
    "COSENZA": 25,
    "CREMONA": 26,
    "CUNEO": 27,
    "ENNA": 28,
    "FERRARA": 29,
    "FIRENZE": 30,
    "FOGGIA": 31,
    "FORLI'-CESENA": 32,
    "FROSINONE": 33,
    "GENOVA": 34,
    "GORIZIA": 35,
    "GROSSETO": 36,
    "IMPERIA": 37,
    "L'AQUILA": 38,
    "LA SPEZIA": 39,
    "LATINA": 40,
    "LECCE": 41,
    "LIVORNO": 42,
    "LUCCA": 43,
    "MACERATA": 44,
    "MANTOVA": 45,
    "MASSA-CARRARA": 46,
    "MATERA": 47,
    "MESSINA": 48,
    "MILANO": 49,
    "MODENA": 50,
    "NAPOLI": 51,
    "NOVARA": 52,
    "NUORO": 53,
    "PADOVA": 54,
    "PALERMO": 55,
    "PARMA": 56,
    "PAVIA": 57,
    "PERUGIA": 58,
    "PESARO E URBINO": 59,
    "PESCARA": 60,
    "PIACENZA": 61,
    "PISA": 62,
    "PISTOIA": 63,
    "POTENZA": 64,
    "RAGUSA": 65,
    "RAVENNA": 66,
    "REGGIO CALABRIA": 67,
    "REGGIO NELL'EMILIA": 68,
    "RIETI": 69,
    "ROMA": 70,
    "ROVIGO": 71,
    "SALERNO": 72,
    "SASSARI": 73,
    "SAVONA": 74,
    "SIENA": 75,
    "SIRACUSA": 76,
    "SONDRIO": 77,
    "TARANTO": 78,
    "TERAMO": 79,
    "TERNI": 80,
    "TORINO": 81,
    "TRAPANI": 82,
    "TRENTO": 83,
    "TREVISO": 84,
    "UDINE": 85,
    "VARESE": 86,
    "VENEZIA": 87,
    "VERCELLI": 88,
    "VERONA": 89,
    "VICENZA": 90,
    "VITERBO": 91,
    "TRIESTE": 92,
    "PORDENONE": 93,
    "ISERNIA": 94,
    "ORISTANO": 95,
    "BIELLA": 96,
    "CROTONE": 97,
    "LECCO": 98,
    "LODI": 99,
    "PRATO": 100,
    "RIMINI": 101,
    "VERBANO-CUSIO-OSSOLA": 102,
    "VIBO VALENTIA": 103,
    "MONZA E DELLA BRIANZA": 104,
    "FERMO": 105,
    "BARLETTA-ANDRIA-TRANI": 106,
}

base_dir = os.getcwd()
res_dir_name = "results/Votanti comuni"
res_dir = base_dir + "/" + res_dir_name

comuni = {}

os.chdir(res_dir)
for nome_provincia, numero_provincia in tqdm(codici_province.items()):
    comuni[nome_provincia] = []
    if not os.path.isdir(nome_provincia):
        os.mkdir(nome_provincia)
    os.chdir(nome_provincia)
    for numero_quesito in range(1, 6):

        response = requests.get(
            url.format(numero_quesito, numero_provincia), headers=headers
        )
        data = response.json()
        comuni[nome_provincia] = data
        if save:
            json_formatted_str = json.dumps(data, indent=4)

            with open(
                "votanti_comuni_provincia_{}_quesito_{:02d}.json".format(
                    nome_provincia, numero_quesito
                ),
                "w",
                encoding="utf8",
            ) as f:
                # json.dump(f, data, indent=4)
                f.write(json_formatted_str)
    os.chdir(res_dir)

os.chdir(base_dir)


# for k,v in comuni.items():
#    print(k)
#    print()
#    for c in v["enti"]["enti_f"]:
#        print(c["desc"])
#        print(c["cod"])
#        print({k:{"nome":v["enti"]["enti_f"]["desc"],"codice":v["enti"]["enti_f"]["cod"]}})
#

codici = {
    k: [
        {
            "nome": c["desc"],
            "codice": c["cod"],
            "codice_provincia": v["enti"]["ente_p"]["cod"],
            "disponibilità_sezioni": c["tipo_tras"] == "SZ",
        }
        for c in v["enti"]["enti_f"]
    ]
    for k, v in comuni.items()
}


print(codici)

with open("codici comuni.json", "w", encoding="utf8") as f:
    json_formatted_str = json.dumps(codici, indent=4)
    f.write(json_formatted_str)
