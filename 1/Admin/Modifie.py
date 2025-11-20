from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, QFrame, QComboBox, QDateEdit, QSpacerItem, QSizePolicy,
    QRadioButton,QButtonGroup,QCheckBox
)
from PySide6.QtGui import QPixmap, QFont, QIcon
from PySide6.QtCore import Qt, QDate
from Accueil.CustomPopup import CustomPopup
import requests
import bcrypt
class Modifie(QWidget):
    def __init__(self,index):
        super().__init__()
        self.index=index
        self.ajout_effectu = False
        #---parametre de fenetre d'inscription---
        self.setWindowTitle("Modifier Patient")
        self.setWindowIcon(QIcon("healthcare.png"))
                                                    
        #---layout principale---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: white; border: 1px solid #cfd8dc;")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_layout.setSpacing(25)

        title = QLabel("Modifier Patient")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet("color: #00796b;")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
        QLabel {
        color: #00796b;
        border: none;
        }
        """)
        form_layout.addWidget(title)

        # Nom + Prénom sur une ligne
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

        # Date de naissance + Sexe (radio buttons) sur une ligne
        birth_gender_layout = QHBoxLayout()

        # Date de naissance
        self.date_naissance = QDateEdit()
        self.date_naissance.setDate(QDate.currentDate())
        self.date_naissance.setDisplayFormat("dd/MM/yyyy")
        self.date_naissance.setCalendarPopup(True)
        self.date_naissance.setStyleSheet("""
            QDateEdit {
                background-color: #f0f4f8;
                border: 1px solid #b0bec5;
                padding: 10px;
                border-radius: 8px;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left: 1px solid #b0bec5;
            }
            QDateEdit::down-arrow {
                image: url(calendar_icon.png); /* Mets ici ton icône */
                width: 16px;
                height: 16px;
            }
        """)
        birth_gender_layout.addWidget(self.date_naissance)

        # Groupe radio sexe
        sexe_layout = QHBoxLayout()
        sexe_label = QLabel("Sexe : ")
        self.homme = QRadioButton("Homme")
        self.femme = QRadioButton("Femme")
        self.homme.setChecked(True)
        group = QButtonGroup(self)
        for i, btn in enumerate([self.homme, self.femme]):
            group.addButton(btn, i)
        sexe_layout.addWidget(sexe_label)
        sexe_layout.addWidget(self.homme)
        sexe_layout.addWidget(self.femme)
        sexe_frame = QFrame()
        sexe_frame.setLayout(sexe_layout)
        sexe_frame.setStyleSheet("border: none; background: transparent;")
        birth_gender_layout.addWidget(sexe_frame)
        form_layout.addLayout(birth_gender_layout)
      
        # Adresse
        self.adresse = QLineEdit()
        self.adresse.setPlaceholderText("Adresse")
        self.adresse.setStyleSheet(self._lineedit_style())
        form_layout.addWidget(self.adresse)

        # Email
        self.email = QLineEdit()
        self.email.setPlaceholderText("Email")
        self.email.setStyleSheet(self._lineedit_style())
        form_layout.addWidget(self.email)

        # Téléphone
        self.telephone = QLineEdit()
        self.telephone.setPlaceholderText("Téléphone")
        self.telephone.setStyleSheet(self._lineedit_style())
        form_layout.addWidget(self.telephone)

      
        # Espacement
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        form_layout.addItem(spacer)

        # Bouton Soumettre
        submit_btn = QPushButton("Submit")
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
        submit_btn.clicked.connect(self.Submit)
        submit_btn.setCursor(Qt.PointingHandCursor)
        form_layout.addWidget(submit_btn)
        main_layout.addWidget(form_frame)
        self.setLayout(main_layout)
       
        self.charge()
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
    


    def charge(self):
        url = f"http://127.0.0.1:5000/modifie?index={self.index}"  # f-string corrigé

        try:
            response = requests.get(url) 
            if response.status_code == 200:
                self.info = response.json()
                self.nom.setText(self.info.get("nom", ""))
                self.prenom.setText(self.info.get("prenom", ""))
                self.adresse.setText(self.info.get("adresse", ""))
                self.email.setText(self.info.get("email", ""))
                self.telephone.setText(self.info.get("telephone", ""))

          
                date_naissance_str = self.info.get("date_naissance", "")
                if date_naissance_str:
                    date_obj = QDate.fromString(date_naissance_str, "yyyy-MM-dd")
                if date_obj.isValid():
                    self.date_naissance.setDate(date_obj)
                sexe = self.info.get("sexe", "").lower()
                if sexe == "homme":
                    self.homme.setChecked(True)
                elif sexe == "femme":
                    self.femme.setChecked(True)
            else:
                error_data = response.json()
                msg= error_data.get("error")
                self.popup = CustomPopup(popup_type="error", message=msg)
                self.popup.show_centered(self)
                self.reset_form()
        except requests.exceptions.RequestException as e:
            print("Erreur de connexion:", str(e))
            popup = CustomPopup("error", "Impossible de contacter le serveur.")
            popup.show_centered(self)

    def Submit(self):
        url = "http://127.0.0.1:5000/Edit"
        sexe = "H" if self.homme.isChecked() else "F"
        form_data = {
            "id_patient":self.info['id_patient'],
            "nom": self.nom.text().strip(),
            "prenom": self.prenom.text().strip(),
            "email": self.email.text().strip(),
            "adresse": self.adresse.text().strip(),
            "telephone": self.telephone.text().strip(),
            "date_naissance": self.date_naissance.date().toString("dd/MM/yyyy"),
            "sexe": sexe
        }
    
        try:
            response = requests.post(url, json=form_data)
            if response.status_code == 200:
                
                data = response.json()
                if data.get("success"):
                    print("ok")
                    self.ajout_effectu=True
                    self.close()
                else:
                    print("Réponse JSON :", data)
                    popup = CustomPopup(popup_type="error", message="Veuillez remplir tous les champs requis.")
                    popup.show_centered(self)
            else:
             print('Erreur serveur')
             self.popup = CustomPopup(popup_type="error", message="l'email est déja utilisé")
             self.popup.show_centered(self)
             self.reset_form()
        except requests.exceptions.RequestException:
            popup = CustomPopup("error", self)
            popup.show_centered(self)