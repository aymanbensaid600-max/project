# serveur_flask.py
from flask import Flask
import os
from conficonn import routes
from flaks import routes1
from patient import routes2
from medecin import routes3
from paiement import routes4
from patientdat import routes5
from medi import routes7
app = Flask(__name__)
app.register_blueprint(routes)
app.register_blueprint(routes1)
app.register_blueprint(routes2)
app.register_blueprint(routes3)
app.register_blueprint(routes4)
app.register_blueprint(routes5)

app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), "ordonnances")
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
app.register_blueprint(routes7)
if __name__ == '__main__':
    app.run(debug=False)
