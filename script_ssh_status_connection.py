#!/usr/bin/python3
# Yann Kerdoncuff 
# version d'apdatée de Jimmy Taylor
# https://www.consentfactory.com/python-threading-queuing-netmiko/

# Ce script utilise des threads pour traiter les adresses IP dans une file d'attente

# Import des modules Netmiko
import time
from unittest import result
from netmiko import ConnectHandler

# Importation supplémentaire pour obtenir le mot de passe et l'impression formatée
from getpass import getpass
from pprint import pprint
import signal, os

# Import des bibliothèques de file d'attente et de threading
from queue import Queue
import threading

import pandas as pd

# Ces captures gèrent les erreurs liées à la frappe de Ctrl+C 
# signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # IOError : canal brisé
# signal.signal(signal.SIGINT, signal.SIG_DFL)  # KeyboardInterrupt : Ctrl-C

# Chargement des adresses IP à partir d'un fichier texte contenant une IP par ligne
ip_adrrs_file = pd.read_csv('switch_list.csv')
ip_addrs = ip_adrrs_file['IP'].to_list()

# Configuration de la file d'attente
enclosure_queue = Queue()
# Configuration du verrou de thread pour que seul un thread imprime à la fois
print_lock = threading.Lock()

# !! Commande CLI à envoyer !!
command = "show time"

# Fonction utilisée dans les threads pour se connecter aux appareils, en passant le numéro de thread et la file
def deviceconnector(i, q):

    # Cette boucle while s'exécute indéfiniment, récupère les adresses IP de la file et les traite
    # La boucle s'arrête et redémarre si "ip = q.get()" est vide
    while True:
        output = ""
        # Ces instructions print sont principalement pour l'utilisateur, indiquant où en est le processus
        # et ne sont pas nécessaires
        print(f"{i}: En attente d'adresse IP...")
        grab = q.get()
        ip = ip_adrrs_file['IP'][i]
        print(f"{i}: IP acquise : {ip}")
        
        device_dict = {
            'host': str(ip),
            'username': 'USER',
            'password': 'PASSWORD',
            'device_type': 'cisco_ios'
        }
        try:
            net_connect = ConnectHandler(**device_dict)
            output = net_connect.send_command(command, use_textfsm=True)
            with print_lock:
                print(f"{i}: Impression des résultats pour {ip}")
                pprint(output)
            net_connect.disconnect()
            ip_adrrs_file.loc[i, 'SSH Status'] = "OK"
        except Exception as e:
            print(f"Erreur d'authentification pour {ip}.")
            output = "ERREUR : Échec de l'authentification"
            ip_adrrs_file.loc[i, 'SSH Status'] = output
        q.task_done()

# Fonction principale qui compile le lanceur de threads et gère la file
def main():

    start = time.perf_counter()
    # Configuration des threads en fonction du nombre défini ci-dessus
    for i in range(len(ip_adrrs_file)):
        # Création du thread en utilisant 'deviceconnector' comme fonction, en passant le numéro de thread et l'objet file comme paramètres
        thread = threading.Thread(target=deviceconnector, args=(i, enclosure_queue,))
        # Définition du thread comme un daemon/de fond
        thread.setDaemon(True)
        # Démarrage du thread
        thread.start()

    # Pour chaque adresse IP dans "ip_addrs", ajout de cette adresse IP dans la file
    for ip_addr in ip_addrs:
        enclosure_queue.put(ip_addr)

    # Attente que toutes les tâches dans la file soient marquées comme complétées (task_done)
    enclosure_queue.join()
    while not enclosure_queue.empty():
        result = enclosure_queue.get()
        print(result)
    finish = time.perf_counter()
    
    print("*** Script complet")
    #Sortie
    print(ip_adrrs_file)
    print("*** Export CSV ***")
    ip_adrrs_file.to_csv("export_ssh_status.csv")
    print("*** Export Done ***")
    print(f'Runtime: {round(finish-start,4)} seconds')

if __name__ == '__main__':
    
    # Calling the main function
    main()
