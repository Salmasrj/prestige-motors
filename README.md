# Prestige Motors - Prédiction de Prix

Application web permettant de prédire le prix de revente d'une voiture en fonction de ses caractéristiques et des réparations à effectuer.

## Fonctionnalités

- Prédiction du prix de revente basée sur :
  - L'année du véhicule
  - La valeur d'entrée
  - Le kilométrage
  - Les pièces à réparer et leur importance
- Interface web intuitive
- Sélection dynamique des pièces à réparer
- Affichage des métriques du modèle (scores R²)

## Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

## Installation

1. Clonez le repository :
```bash
git clone https://github.com/votre-username/prestige-motors.git
cd prestige-motors
```

2. Créez un environnement virtuel (recommandé) :
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## Structure du Projet

```
prestige-motors/
├── data/
│   └── inventory.csv        # Données d'entraînement
├── src/
│   ├── model/
│   │   └── predictor.py    # Logique de prédiction
│   └── web/
│       ├── static/
│       │   └── css/
│       │       └── styles.css
│       ├── templates/
│       │   └── index.html
│       └── webAppPredict.py # Application Flask
├── README.md
└── requirements.txt
```

## Utilisation

1. Activez l'environnement virtuel si ce n'est pas déjà fait :
```bash
.\venv\Scripts\activate
```

2. Lancez l'application :
```bash
python -m src.web.webAppPredict
```

3. Ouvrez votre navigateur et accédez à :
```
http://localhost:5000
```

## Utilisation de l'Interface

1. Remplissez les informations de base du véhicule :
   - Année
   - Valeur d'entrée
   - Kilométrage

2. Ajoutez les pièces à réparer :
   - Sélectionnez une pièce dans la liste déroulante
   - Indiquez l'importance de la réparation (0-5)
   - Ajoutez autant de pièces que nécessaire

3. Cliquez sur "Calculer la prédiction"

## Modèle de Prédiction

- Utilise une régression linéaire (scikit-learn)
- Entraîné sur les données historiques de l'inventaire
- Métriques de performance affichées avec chaque prédiction

## Technologies Utilisées

- Python 3.x
- Flask (framework web)
- scikit-learn (machine learning)
- pandas (manipulation de données)
- HTML/CSS (interface utilisateur)

## Auteurs

- [Votre Nom]
- [Autres Contributeurs]

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.