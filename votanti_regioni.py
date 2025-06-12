import requests
import json
import os

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
uri = "/siel/PX/votantiFI/DE/20250608/TE/09/SK/{:02d}"
url = dominio + uri
save = False


base_dir = os.getcwd()
res_dir_name = "results/Votanti regioni"
res_dir = base_dir + "/" + res_dir_name

os.chdir(res_dir)

for numero_quesito in range(1,6):

    response = requests.get(url.format(numero_quesito), headers=headers)
    data = response.json()
    if save:
        json_formatted_str = json.dumps(data, indent=4)

        with open("votanti_regioni_quesito_{:02d}.json".format(numero_quesito), "w", encoding="utf8") as f:
            # json.dump(f, data, indent=4)
            f.write(json_formatted_str)

regioni = data["enti"]["enti_f"]

codici = {r["desc"]: r["cod"] for r in regioni}

for r in regioni:
    print(r["tipo"])
    print(r["desc"])
    print(r["cod"])


print(codici)
dict(sorted(codici.items(), key=lambda item: item[1]))