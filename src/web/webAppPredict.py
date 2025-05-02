from flask import Flask, render_template, request
import os
import sys

# Ajouter le répertoire racine au path Python
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(root_dir)

from src.model.predictor import CarPricePredictor
import pandas as pd
import json

app = Flask(__name__)
predictor = CarPricePredictor()

# Chemin vers le fichier de données
DATA_PATH = os.path.join(root_dir, 'data', 'inventory.csv')

# Initialiser et entraîner le modèle
model_metrics = predictor.train(DATA_PATH)

@app.route('/', methods=['GET', 'POST'])
def home():
    prediction = None
    pieces_disponibles = predictor.get_unique_pieces(DATA_PATH)
    
    if request.method == 'POST':
        pieces = []
        for piece_name in request.form.getlist('pieces[]'):
            importance = request.form.get(f'importance_{piece_name}')
            if importance:
                pieces.append({
                    "nom_pièce": piece_name,
                    "importance_pièce": int(importance)
                })
        
        try:
            prediction = predictor.predict(
                annee=int(request.form['annee']),
                valeur_entree=float(request.form['valeur_entree']),
                kilometrage=float(request.form['kilometrage']),
                pieces=pieces
            )
        except ValueError as e:
            return str(e), 400
    
    return render_template('index.html', 
                         prediction=prediction, 
                         pieces_disponibles=pieces_disponibles)

if __name__ == '__main__':
    app.run(debug=True)