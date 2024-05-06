# Boîte à Outils Réseau

Ce dépôt contient une collection de scripts Python conçus pour aider les administrateurs réseau à gérer et surveiller leur infrastructure réseau. Les scripts utilisent des techniques d'asynchronisme pour exécuter des opérations réseau de manière efficace.

## Contenu

- **script_ssh_status_connection.py**: Ce script effectue des connexions SSH à une liste d'adresses IP pour vérifier leur accessibilité et exécute une commande spécifique. Les résultats sont enregistrés dans un fichier CSV pour un examen ultérieur.
- **ping_test.py**: Ce script réalise des tests de ping sur une liste d'adresses IP à partir d'un fichier CSV et enregistre le statut de chaque IP dans un nouveau fichier CSV.

## Dépendances

Les scripts nécessitent les modules Python suivants :
- `netmiko` pour **script_ssh_status_connection.py**
- `asyncio` et `pandas` pour **ping_test.py**

Installez les dépendances nécessaires via pip:
```
pip install netmiko pandas
```

## Utilisation

### Script SSH Status Connection

Exécutez le script comme suit pour vérifier l'état de la connexion SSH:

```
python script_ssh_status_connection.py
```

Assurez-vous que le fichier CSV contenant les adresses IP (switch_list.csv) est présent dans le même répertoire que le script.
### Ping Test

Pour effectuer un test de ping, exécutez le script:

```
python ping_test.py
```

Ce script nécessite un fichier CSV output_for_ping.csv avec une colonne IP pour les adresses IP.
## Contribution

Les contributions à ce projet sont les bienvenues. Vous pouvez contribuer en:

- Proposant des améliorations via des issues.
- Soumettant des pull requests avec des améliorations ou corrections.

## Licence

Ce projet est distribué sous licence MIT. Veuillez voir le fichier LICENSE pour plus de détails.
