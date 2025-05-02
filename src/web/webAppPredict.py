from flask import Flask, render_template, request
import os
import sys

# Ajouter le répertoire racine au path Python
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(root_dir)

from src.model.predictor import CarPricePredictor

app = Flask(__name__)
predictor = CarPricePredictor()

# Initialiser et entraîner le modèle au démarrage
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'inventory.csv')
model_metrics = predictor.train(DATA_PATH)

@app.route('/', methods=['GET', 'POST'])
def home():
    prediction = None
    if request.method == 'POST':
        # Récupérer les données du formulaire
        pieces = [
            {
                "nom_pièce": "Moteur",
                "importance_pièce": int(request.form['importance_moteur'])
            },
            {
                "nom_pièce": "Freins",
                "importance_pièce": int(request.form['importance_freins'])
            }
        ]
        
        # Faire la prédiction
        prediction = predictor.predict(
            annee=int(request.form['annee']),
            valeur_entree=float(request.form['valeur_entree']),
            kilometrage=float(request.form['kilometrage']),
            pieces=pieces
        )
    
    return render_template('index.html', prediction=prediction)

if __name__ == '__main__':
    app.run(debug=True)