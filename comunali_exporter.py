import os
import json
import pandas
from tqdm import tqdm


with open("codici province.json","r",encoding="utf8") as f:
    codici_province = json.load(f)
with open("codici comuni.json","r",encoding="utf8") as f:
    codici_comuni = json.load(f)

regioni = codici_province.keys()

info_comuni_path = "results/Info comuni"
base_dir = os.getcwd()


comuni = {}
os.chdir(info_comuni_path)
for r in (rbar:= tqdm(regioni,"Regione")):
    rbar.set_postfix_str(r)
    if not os.path.isdir(r):
        os.mkdir(r)
    os.chdir(r)
    for p in (pbar:= tqdm(codici_province[r],"Provincia", position=1, leave=False)):
        nome_provincia = p["nome"]
        pbar.set_postfix_str(nome_provincia)
        lista_comuni = []
        for c in (cbar:= tqdm(codici_comuni[nome_provincia],"Comune", position=2, leave=False)):
            nome_comune = p["nome"]
            cbar.set_postfix_str(nome_comune)
            nome_comune_mod = ''.join(e for e in nome_comune.replace(" ","_") if e.isalnum())
            try:
                with open("scrutini_comune_{}.json".format(nome_comune_mod),"r",encoding="utf8") as f:
                    data = json.load(f)    
            except FileNotFoundError as e:
                continue

            info_comune = {
                "tipo_territorio": data["int"]["l_terr"],
                "nome_comune": data["int"]["desc_com"],
                "nome_provincia": data["int"]["desc_prov"],
                "nome_regione": data["int"]["desc_reg"],
                "n_elettori": data["int"]["ele_m"], # aventi diritto
                "n_elettrici": data["int"]["ele_f"],
                "n_elettori_totali": data["int"]["ele_t"],
                "disponibilità_dati_sezioni": data["int"]["tipo_tras"]=="SZ"
            }
            for s in data["scheda"]:
                info_scheda = {
                "votanti_maschi_scheda_{}".format(s["cod"]): s["vot_m"],
                "votanti_femmine_scheda_{}".format(s["cod"]): s["vot_f"],
                "votanti_tot_scheda_{}".format(s["cod"]): s["vot_t"],
                "affluenza_totale_scheda_{}".format(s["cod"]): s["perc_vot"],
                "schede_bianche_scheda_{}".format(s["cod"]): s["sk_bianche"],
                "schede_nulle_scheda_{}".format(s["cod"]): s["sk_nulle"],
                "schede_contestate_scheda_{}".format(s["cod"]): s["sk_contestate"],
                "voti_si_scheda_{}".format(s["cod"]): s["voti_si"],
                "voti_no_scheda_{}".format(s["cod"]): s["voti_no"],
                "percentuale_si_scheda_{}".format(s["cod"]): s["perc_si"],
                "percentuale_no_scheda_{}".format(s["cod"]): s["perc_no"],
                }
                info_comune = info_comune | info_scheda
            lista_comuni.append(info_comune)
        df = pandas.DataFrame(lista_comuni)
        df.to_csv("info_comuni_provincia_{}.csv".format(nome_provincia))
    os.chdir(base_dir + "/" + info_comuni_path)
        
