import requests
from datetime import datetime

apikey = "MA_CLE_API" # remplacez ici par votre vrai clé UNIQUEMENT SI VOUS NE VOULEZ PAS MODIFIER

actual_date = datetime.now()
extrainfos = {
    "iata":"EWR",
    "day":actual_date.day,
    "month":actual_date.month,
    "year":actual_date.year,
    "mode":"dep",
    "page":"1"
}

def call_API():
    resp = requests.get(f"https://api.flightapi.io/schedule/v2/{apikey}",params=extrainfos)
    if resp.status_code!=200:
        return
    resp = resp.json()
    resp = resp['data']["flights"]
    
    # traitement des vols
    flights = []
    for flight in resp:
        dico = {}
        dico["departure_time"] = flight["departureTime"]["time24"]
        dico["company"] = flight["carrier"]["name"]
        dico["destination"] = flight["airport"]["city"]
        dico["num_flight"] = flight["carrier"]["fs"]+' '+flight["carrier"]["flightNumber"]
        flights.append(dico)
    flights.append('')
        
    # enregistrement
    with open("flights_sheet.csv","w",encoding="utf-8") as file:
        file.write('\n'.join([str(elem) for elem in flights]))