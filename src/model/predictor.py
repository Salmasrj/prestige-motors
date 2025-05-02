import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import json

class CarPricePredictor:
    def __init__(self):
        self.model = None
        self.feature_names = ['Année', 'ValeurEntrée', 'Kilométrage', 'ImportancePieces']

    def process_pieces(self, pieces_str):
        pieces = json.loads(pieces_str) if isinstance(pieces_str, str) else pieces_str
        importance_totale = sum(piece['importance_pièce'] for piece in pieces)
        return importance_totale

    def train(self, data_path):
        # Charger les données
        df = pd.read_csv(data_path)

        # Préparation des features
        X = pd.DataFrame()
        X['Année'] = df['Année']
        X['ValeurEntrée'] = df['ValeurEntrée']
        X['Kilométrage'] = df['Kilométrage']
        X['ImportancePieces'] = df['Pièces'].apply(self.process_pieces)

        y = df['ValeurSortie']

        # Split et entrainement
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model = LinearRegression()
        self.model.fit(X_train, y_train)

        # Scores
        return {
            'train_score': self.model.score(X_train, y_train),
            'test_score': self.model.score(X_test, y_test),
            'coefficients': dict(zip(self.feature_names, self.model.coef_))
        }

    def predict(self, annee, valeur_entree, kilometrage, pieces):
        if self.model is None:
            raise ValueError("Le modèle doit d'abord être entraîné")
        
        importance_pieces = self.process_pieces(pieces)
        X_pred = pd.DataFrame([[annee, valeur_entree, kilometrage, importance_pieces]], 
                            columns=self.feature_names)
        prediction = self.model.predict(X_pred)[0]
        return round(prediction, 2)