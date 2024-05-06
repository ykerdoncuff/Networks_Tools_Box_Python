import asyncio
import time
from collections import deque

import pandas as pd

# Fonction asynchrone pour pinger une adresse IP
async def async_ping(host, semaphore):
    async with semaphore:  # Utilisation d'un sémaphore pour limiter le nombre de pings simultanés
        for _ in range(5):  # Répète le ping 5 fois
            proc = await asyncio.create_subprocess_shell(
                f'C:\\Windows\\System32\\ping {host} -n 1 -w 1 -l 1',  # Commande de ping
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            status = await proc.wait()  # Attente de la fin du processus
            if status == 0:
                return 'Alive'  # Retourne 'Alive' si le ping réussit
        return 'Timeout'  # Retourne 'Timeout' après 5 tentatives infructueuses

# Fonction principale asynchrone pour gérer les pings
async def async_main(hosts, limit):
    semaphore = asyncio.Semaphore(limit)  # Crée un sémaphore pour limiter le nombre de tâches simultanées
    tasks1 = deque()  # Utilise une deque pour gérer les tâches
    for host in hosts:
        tasks1.append(asyncio.create_task(
            async_ping(host, semaphore)  # Crée une tâche asynchrone pour chaque host
        ))
    return (t1 for t1 in await asyncio.gather(*tasks1))  # Attend la fin de toutes les tâches et les retourne

# Chargement des adresses IP à partir d'un fichier CSV
host_df = pd.read_csv('output_for_ping.csv')

# Limite des tâches concurrentes
limit = 256

start = time.perf_counter()  # Début du chronomètre

loop = asyncio.get_event_loop()  # Obtention de la boucle d'événements
asyncio.set_event_loop(loop)
resp = loop.run_until_complete(async_main(host_df['IP'].to_list(), limit))  # Exécution de la fonction principale
loop.close()  # Fermeture de la boucle d'événements

finish = time.perf_counter()  # Fin du chronomètre

# Enregistrement du statut de chaque IP dans le DataFrame
host_df['Status'] = list(resp)
print(host_df)
host_df.to_csv('output_test_ping.csv')  # Sauvegarde des résultats dans un fichier CSV
print(f'Temps d\'exécution: {round(finish-start,4)} secondes')
