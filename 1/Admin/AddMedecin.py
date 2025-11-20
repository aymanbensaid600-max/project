from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, QFrame, QComboBox, QSpacerItem, QSizePolicy, QCheckBox
)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt
from Accueil.CustomPopup import CustomPopup

import requests
import bcrypt
class AddMedecin(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ajout Médecin - Cabinet Médical")
        self.setWindowIcon(QIcon("doctor.png"))
        self.setFixedSize(400, 600)  

        self.ajout_effectue = False

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: white;  border-radius: 10px;")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_layout.setSpacing(12)

        title = QLabel("Ajout d'un Médecin")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #00796b")
        form_layout.addWidget(title)

        self.nom = QLineEdit()
        self.prenom = QLineEdit()
        self.specialite = QLineEdit()
        self.email = QLineEdit()
        self.telephone = QLineEdit()
        self.horaires = QLineEdit()
        self.mot_de_passe = QLineEdit()
        self.confirmer_mdp = QLineEdit()

        # Configuration des champs de mot de passe
        self.mot_de_passe.setPlaceholderText("Mot de passe")
        self.mot_de_passe.setEchoMode(QLineEdit.Password)
        self.confirmer_mdp.setPlaceholderText("Confirmer le mot de passe")
        self.confirmer_mdp.setEchoMode(QLineEdit.Password)

        for field, placeholder in [
            (self.nom, "Nom"),
            (self.prenom, "Prénom"),
            (self.specialite, "Spécialité"),
            (self.email, "Email"),
            (self.telephone, "Téléphone"),
            (self.horaires, "Horaires (ex: Lun-Ven 9:00-17:00)"),
            (self.mot_de_passe, "Mot de passe"),
            (self.confirmer_mdp, "Confirmer le mot de passe"),
        ]:
            field.setPlaceholderText(placeholder)
            field.setStyleSheet(self._style_lineedit())
            form_layout.addWidget(field)

        # Ajout d'une case à cocher pour afficher/masquer les mots de passe
        self.show_password = QCheckBox("Afficher les mots de passe")
        self.show_password.setStyleSheet("QCheckBox { color: #555; }")
        self.show_password.stateChanged.connect(self.toggle_password_visibility)
        form_layout.addWidget(self.show_password)

        submit_btn = QPushButton("Ajouter le Médecin")
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #00796b;
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #004d40;
            }
        """)
        submit_btn.clicked.connect(self.valider_formulaire)
        form_layout.addWidget(submit_btn)

        main_layout.addWidget(form_frame)

    def _style_lineedit(self):
        return """
            QLineEdit {
                background-color: #f0f4f8;
                border: 1px solid #b0bec5;
                padding: 8px;
                border-radius: 8px;
            }
            QLineEdit:focus {
                border: 1px solid #00796b;
                background-color: #e0f2f1;
            }
        """

    def toggle_password_visibility(self, state):
        """Affiche ou masque le texte des champs de mot de passe"""
        mode = QLineEdit.Normal if state else QLineEdit.Password
        self.mot_de_passe.setEchoMode(mode)
        self.confirmer_mdp.setEchoMode(mode)

    def valider_formulaire(self):
        # Vérification des champs obligatoires
        if not all([
            self.nom.text().strip(),
            self.prenom.text().strip(),
            self.specialite.text().strip(),
            self.email.text().strip(),
            self.telephone.text().strip(),
            self.horaires.text().strip(),
            self.mot_de_passe.text().strip()
        ]):
            popup = CustomPopup("error", "Veuillez remplir tous les champs obligatoires.")
            popup.show_centered(self)
            return

        
        
        data = {
            "nom": self.nom.text().strip(),
            "prenom": self.prenom.text().strip(),
            "specialite": self.specialite.text().strip(),
            "email": self.email.text().strip(),
            "telephone": self.telephone.text().strip(),
            "horaires": self.horaires.text().strip(),
            "mot_de_passe": self.mot_de_passe.text().strip()
        }

        try:
            response = requests.post("http://127.0.0.1:5000/ajouter_medecin", json=data)
            if response.status_code == 200 and response.json().get("success"):
                popup = CustomPopup("success", "Médecin ajouté avec succès.")
                popup.show_centered(self)
                self.ajout_effectue = True
                self.close()
            else:
                error_msg = response.json().get("error", "Erreur lors de l'ajout du médecin.")
                popup = CustomPopup("error", error_msg)
                popup.show_centered(self)
        except requests.exceptions.RequestException:
            popup = CustomPopup("error", "Impossible de contacter le serveur.")
            popup.show_centered(self)