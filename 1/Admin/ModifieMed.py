from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, QFrame, QComboBox, QDateEdit, QSpacerItem, QSizePolicy,
    QRadioButton,QButtonGroup,QCheckBox
)
from PySide6.QtGui import QPixmap, QFont, QIcon
from PySide6.QtCore import Qt, QDate
from Accueil.CustomPopup import CustomPopup
import requests
import bcrypt 
class ModifieMedecin(QWidget):
    def __init__(self, index, parent=None):
        super().__init__()
        self.parent_window = parent 
        self.index = index
        self.setWindowTitle("Modifier Médecin")
        self.setWindowIcon(QIcon("healthcare.png"))
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: white; border:None;")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_layout.setSpacing(15)

        title = QLabel("Modification du Médecin")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        
        title.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(title)

        name_layout = QHBoxLayout()
        self.nom = QLineEdit()
        self.nom.setPlaceholderText("Nom")
        self.prenom = QLineEdit()
        self.prenom.setPlaceholderText("Prénom")
        for champ in (self.nom, self.prenom):
            champ.setStyleSheet(self._lineedit_style())
        name_layout.addWidget(self.nom)
        name_layout.addWidget(self.prenom)
        form_layout.addLayout(name_layout)

        self.specialite = QLineEdit()
        self.specialite.setPlaceholderText("Spécialité")
        self.specialite.setStyleSheet(self._lineedit_style())
        form_layout.addWidget(self.specialite)

        self.horaires = QLineEdit()
        self.horaires.setPlaceholderText("Horaires")
        self.horaires.setStyleSheet(self._lineedit_style())
        form_layout.addWidget(self.horaires)

        self.email = QLineEdit()
        self.email.setPlaceholderText("Email")
        self.email.setStyleSheet(self._lineedit_style())
        form_layout.addWidget(self.email)

        self.telephone = QLineEdit()
        self.telephone.setPlaceholderText("Téléphone")
        self.telephone.setStyleSheet(self._lineedit_style())
        form_layout.addWidget(self.telephone)

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        form_layout.addItem(spacer)

        submit_btn = QPushButton("Enregistrer")
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #00796b;
                color: white;
                padding: 8px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #004d40;
            }
        """)
        submit_btn.clicked.connect(self.submit)
        form_layout.addWidget(submit_btn)

        main_layout.addWidget(form_frame)
        self.setLayout(main_layout)

        self.charger_donnees()

    def _lineedit_style(self):
        return """
            QLineEdit {
                background-color: #f0f4f8;
                border: 1px solid #b0bec5;
                padding: 12px;
                border-radius: 8px;
            }
            QLineEdit:focus {
                border: 1px solid #00796b;
                background-color: #e0f2f1;
            }
        """

    def charger_donnees(self):
        url = f"http://127.0.0.1:5000/modifieMedecin?index={self.index}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                self.info = response.json()
                self.nom.setText(self.info.get("nom", ""))
                self.prenom.setText(self.info.get("prenom", ""))
                self.specialite.setText(self.info.get("specialite", ""))
                self.horaires.setText(self.info.get("horaires", ""))
                self.email.setText(self.info.get("email", ""))
                self.telephone.setText(self.info.get("telephone", ""))
            else:
                error_data = response.json()
                msg = error_data.get("error", "Erreur inconnue.")
                popup = CustomPopup(popup_type="error", message=msg)
                popup.show_centered(self)
        except requests.exceptions.RequestException as e:
            popup = CustomPopup("error", "Erreur de connexion au serveur.")
            popup.show_centered(self)

    def submit(self):
        url = "http://127.0.0.1:5000/editMedecin"
        data = {
            "id_medecin": self.info.get("id_medecin"),
            "nom": self.nom.text().strip(),
            "prenom": self.prenom.text().strip(),
            "specialite": self.specialite.text().strip(),
            "horaires": self.horaires.text().strip(),
            "email": self.email.text().strip(),
            "telephone": self.telephone.text().strip()
        }

        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(data.get("success"))
                    self.popup = CustomPopup(popup_type="success", message="Modification réussie.")
                    self.popup.show_centered(self.parent_window)
                    self.close()
                else:
                    self.popup = CustomPopup(popup_type="error", message=data.get("error", "Erreur lors de la modification."))
                    self.popup.show_centered(self)
            else:
                popup = CustomPopup(popup_type="error", message="Email déjà utilisé.")
                popup.show_centered(self)
        except requests.exceptions.RequestException:
            popup = CustomPopup("error", "Connexion impossible au serveur.")
            popup.show_centered(self)
