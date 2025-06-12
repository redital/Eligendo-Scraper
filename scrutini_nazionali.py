import requests
import json

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
uri = "/siel/PX/scrutiniFI/DE/20250608/TE/09"
url = dominio + uri
save = True


response = requests.get(url, headers=headers)
data = response.json()
if save:
    json_formatted_str = json.dumps(data, indent=4)

    with open("results/scrutini nazionali.json", "w", encoding="utf8") as f:
        # json.dump(f, data, indent=4)
        f.write(json_formatted_str)
