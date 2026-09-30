from datetime import datetime
from reals import call_API

import pygame
pygame.init()

data = None

# ==== CSV FILE ====

# récupérer les données du fichier .csv
def take_csv():
    global data
    call_API()
    with open("flights_sheet.csv",'r',encoding='utf-8') as file:
        data = file.readlines()
        # supprimer les \n à chaque fin de ligne
        data = [line[:-1] for line in data]

        # transformer les lignes en de vrais dictionnaires
        data = [eval(line) for line in data]
    return data
data = take_csv()

# ==== IMAGES ====

lib = {name_cie:pygame.image.load(f"{name_cie}.png") for name_cie in ['United Airlines','TAP Air Portugal','Lufthansa','American Airlines']}
lib = {name_cie:pygame.transform.scale(logo,(200,50)) for name_cie,logo in lib.items()}

# ==== FUNCTIONS ====

def draw_flightbox(i):
    global window
    # effacer l'ancien contenu
    pygame.draw.rect(window,pygame.Color(0,0,0),(0,i*50,1250,50))
    # créer les lignes blanches
    pygame.draw.rect(window,pygame.Color(255,255,255),(0,i*50,1250,50),1)
    # actualiser la fenêtre graphique
    pygame.display.flip()

def show_flight(flight,i):
    global window,lib

    # charger la police d'écriture (en gras) avec la taille
    font = pygame.font.SysFont("Verdana",32,bold=True)

    # afficher le logo de la compagnie
    if flight["company"] in lib:
        window.blit(lib[flight["company"]],(150,i*50))
    else:
        title_render = font.render(flight['company'],False,pygame.Color(230,255,25))
        window.blit(title_render,(100,i*50))  

    # gérer les différents écarts entre les infos
    j=0
    delta = [10,370,700,850]

    # boucle pour afficher chaque info
    for key,elem in flight.items():
        if key!="company" and key!="status":
            # créer le rendu graphique
            rtxt = font.render(elem,False,pygame.Color(230,255,25))

            # l'afficher
            window.blit(rtxt,(delta[j],i*50))

            # à ne pas oublier
            j+=1
            
    # affichage statut
    stat = flight["status"]
    if stat=="BOARDING":
        clr = pygame.Color(0,0,255)
    elif stat=="LEAVING GATE":
        clr = pygame.Color(255,128,0)
    elif stat=="DELAYED":
        clr = pygame.Color(255,0,0)
    else: # SCHEDULED
        clr = pygame.Color(0,255,0)
    font = pygame.font.SysFont("Verdana",32,bold=True)
    rtxt = font.render(stat,False,clr)
    window.blit(rtxt,(975,i*50))


def next_flights(data):

    # récupérer l'heure actuelle et convertir en minutes
    actual_time = datetime.now()
    actual_time_min = actual_time.hour*60+actual_time.minute

    flights_to_display = []
    for flight in data:
        # récupérer l'heure de départ du vol
        departure_time = flight["departure_time"].split(":")
        departure_time_min = int(departure_time[0])*60+int(departure_time[1])

        # prochain départ ?
        if departure_time_min >= actual_time_min:
            flights_to_display.append(flight) # alors on l'ajoute

            # attribuer une porte
            if (departure_time_min-actual_time_min)<=30:
                flights_to_display[-1]["gate"] = choice_gate(flight["num_flight"])

                if flights_to_display[-1]["gate"]!="": # il a une porte
                    flights_to_display[-1]["status"] = "BOARDING" # création du statut
                else: # il doit attendre une porte -> retard
                    flights_to_display[-1]["status"] = "DELAYED" # création du statut

                if departure_time_min==actual_time_min: # heure du départ
                    flights_to_display[-1]["status"] = "LEAVING GATE"

            else: # création du statut
                flights_to_display[-1]["status"] = "SCHEDULED"


        # si on a suffisamment de vols
        if len(flights_to_display)==11:
            break # on arrête la boucle for

    # renvoi des vols
    return flights_to_display

def choice_gate(flight):
    global GATES
    if flight not in GATES.values():
        # recherche de la première porte disponible
        for gate in GATES.keys():
            if GATES[gate] is None:
                GATES[gate] = flight # enregistrement
                return gate
        return "" # pas de portes disponibles
    else:
        return list(GATES.keys())[list(GATES.values()).index(flight)]

def remove_gate(flights):
    global GATES
    for flight in flights:
        departure_time = flight["departure_time"].split(":")
        departure_time_min = int(departure_time[0])*60+int(departure_time[1])
        actual_time = datetime.now()
        actual_time_min = actual_time.hour*60+actual_time.minute
        # le vol a disparu de l'affichage ?
        if departure_time_min<actual_time_min:
            GATES[flight["gate"]] = None
            del flight["gate"]

# ========= MAIN ==========
window = pygame.display.set_mode((1250,550))
pygame.display.set_caption("DEPARTURES")

draw_flightbox(0)
font = pygame.font.SysFont("Verdana",32,bold=True)
j=0
delta = [10,150,370,700,850,975]
for key in ["Dep","Company","To","Num","Gate","Status"]:
    rtxt = font.render(key,False,pygame.Color(230,255,25))
    window.blit(rtxt,(delta[j],0))
    j+=1
pygame.display.flip()

# portes d'embarquement
GATES = {"A1":None,"A2":None,"A3":None,"A4":None,"B1":None,"B2":None,"C":None}

running = True
while running:

    data = take_csv()
    flights_to_display = next_flights(data)
    for i in range(1,len(flights_to_display)+1):
        draw_flightbox(i)
        show_flight(flights_to_display[i-1],i)
    pygame.time.delay(60000)
    remove_gate(flights_to_display)

    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running = False
            pygame.quit()