import os
import json

company_ids_jsons = {}
company_ids_errors = {}
path_to_json = r'C:\Users\mmandziej001\Desktop\Projects\FAIT\Prediction Module\EMIS\FULL'
json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
for i in json_files:
    with open(os.path.join(path_to_json, i), encoding="utf8") as json_file:
        nip = i[0:10] 
        try:
            json_text = json.load(json_file)     
            if len(json_text) == 1:
                company_ids_jsons[nip] = json_text['result']
            else:
                company_ids_jsons[nip] = json_text
        except Exception as e:
            error = 'Code: {c}, Message: {m}'.format(c=type(e).__name__, m=str(e))
            company_ids_errors[nip] = error



"""
asd = {"InformacjaOZakazie": [{"Typ": "Zakaz wykonywania zawodu",
				"Opis": "zakaz wykonywania funkcji biegłego --",
				"OkresNaJakiZostalOrzeczonyZakaz": "4 lata",
				"ZakazWydal": "sąd",
				"Nazwa": "Sąd Rejonowy --",
				"SygnaturaAktSprawy": "--",
				"DataWydaniaOrzeczenia": "2014-02-18",
				"DataUprawomocnieniaOrzeczenia": "2014-06-17"},
			{"Typ": "Zakaz wykonywania zawodu",
				"Opis": "zakaz wykonywania funkcji biegłego --",
				"OkresNaJakiZostalOrzeczonyZakaz": "4 lata",
				"ZakazWydal": "sąd",
				"Nazwa": "Sąd Rejonowy --",
				"SygnaturaAktSprawy": "--",
				"DataWydaniaOrzeczenia": "2014-02-18",
				"DataUprawomocnieniaOrzeczenia": "2014-06-17"}]}
company_ids_jsons['8390007622']['data']['zakazy'] = asd
"""