from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, QFrame, QComboBox, QDateEdit, QSpacerItem, QSizePolicy,
    QRadioButton,QButtonGroup,QCheckBox
)
from PySide6.QtGui import QPixmap, QFont, QIcon
from PySide6.QtCore import Qt, QDate
from Accueil.CustomPopup import CustomPopup
import requests
import bcrypt
class Addpat(QWidget):
    def __init__(self):
        super().__init__()
        self.ajout_effectue = False

        #---parametre de fenetre d'inscription---
        self.setWindowTitle("Ajouter Patient")
        self.setWindowIcon(QIcon("healthcare.png"))
        #---layout principale---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: white; border: 1px solid #cfd8dc;")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(50,50, 50, 50)  # ou 30
        form_layout.setSpacing(20)

        title = QLabel("Ajouter Patient")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
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
        self.date_naissance.setFixedHeight(40)

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

        # Mot de passe
        self.password = QLineEdit()
        self.password.setPlaceholderText("Mot de passe")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setStyleSheet(self._lineedit_style())
        form_layout.addWidget(self.password)

        # Confirmation mot de passe
        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("Confirmer le mot de passe")
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setStyleSheet(self._lineedit_style())
        form_layout.addWidget(self.confirm_password)

        # Espacement
        spacer = QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Expanding)

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
        submit_btn.clicked.connect(self.chek_soumettre)
        submit_btn.setCursor(Qt.PointingHandCursor)
        form_layout.addWidget(submit_btn)
        main_layout.addWidget(form_frame)
        self.setLayout(main_layout)
         # Affiche le popup centré dans la fenêtre d'inscription
    def _lineedit_style(self):
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
    def chek_soumettre(self):

        if not self.nom.text().strip() or not self.prenom.text().strip() or  not self.email.text().strip() or not self.password.text().strip() or not self.confirm_password.text().strip() or not self.adresse.text().strip() or not self.telephone.text().strip():
            if not self.nom.text().strip() :
                self.nom.setPlaceholderText("nom requis")
                self.nom.setStyleSheet(""" 
                    QLineEdit {
                        background-color: #f0f4f8;
                        border: 1px solid red;
                        padding: 12px;
                        border-radius: 8px;
                        
                    }
                                         
                """)
            if not self.prenom.text().strip():
                self.prenom.setPlaceholderText("prenom requis")
                self.prenom.setStyleSheet(""" 
                    QLineEdit {
                        background-color: #f0f4f8;
                        border: 1px solid red;
                        padding: 12px;
                        border-radius: 8px;
                        
                    }
                                         
                """)
            if not self.adresse.text().strip() :
                self.adresse.setPlaceholderText("adresse requis")
                self.adresse.setStyleSheet(""" 
                    QLineEdit {
                        background-color: #f0f4f8;
                        border: 1px solid red;
                        padding: 12px;
                        border-radius: 8px;
                        
                    }
                                         
                """)
            if not self.telephone.text().strip() :
                self.telephone.setPlaceholderText("telephone requis")
                self.telephone.setStyleSheet(""" 
                    QLineEdit {
                        background-color: #f0f4f8;
                        border: 1px solid red;
                        padding: 12px;
                        border-radius: 8px;
                        
                    }
                                         
                """)              
            if not self.email.text().strip() :
                self.email.setPlaceholderText("email requis")
                self.email.setStyleSheet(""" 
                    QLineEdit {
                        background-color: #f0f4f8;
                        border: 1px solid red;
                        padding: 12px;
                        border-radius: 8px;
                        
                    }
                                         
                """)
            if not self.password.text().strip() :
                self.password.setPlaceholderText("password requis")
                self.password.setStyleSheet(""" 
                    QLineEdit {
                        background-color: #f0f4f8;
                        border: 1px solid red;
                        padding: 12px;
                        border-radius: 8px;
                        
                    }
                                         
                """)     
            
            if not self.confirm_password.text().strip() :
                self.confirm_password.setPlaceholderText("confrim password requis")
                self.confirm_password.setStyleSheet(""" 
                    QLineEdit {
                        background-color: #f0f4f8;
                        border: 1px solid red;
                        padding: 12px;
                        border-radius: 8px;
                        
                    }
                                         
                """)
        else:
            print("ok")
            self.submit()
    def submit(self):
        url = "http://127.0.0.1:5000/formulaire"
        sexe = "H" if self.homme.isChecked() else "F"
        password_hash = bcrypt.hashpw(self.password.text().strip().encode('utf-8'), bcrypt.gensalt())
        form_data = {
            "nom": self.nom.text().strip(),
            "prenom": self.prenom.text().strip(),
            "email": self.email.text().strip(),
            "password": password_hash.decode('utf-8'),
            "confirm_password": self.confirm_password.text().strip(),
            "adresse": self.adresse.text().strip(),
            "telephone": self.telephone.text().strip(),
            "date_naissance": self.date_naissance.date().toString("dd/MM/yyyy"),
            "sexe": sexe
        }
    
        try:
            response = requests.post(url, json=form_data)
            if response.status_code == 200:
                print("ok")
                data = response.json()
                if data.get("success"):
                    print('good')
                    self.ajout_effectue = True # Affiche le popup centré dans la fenêtre d'inscription
                    self.close()
                else:
                    print("Réponse JSON :", data)
                    popup = CustomPopup(popup_type="error", message="Veuillez remplir tous les champs requis.", parent=None)
                    popup.show_centered(self)
            else:
             print('Erreur serveur')
             self.popup = CustomPopup(popup_type="error", message="l'email est déja utilisé")
             self.popup.show_centered(self)
             self.reset_form()
        except requests.exceptions.RequestException:
            popup = CustomPopup("error", self)
            popup.show_centered(self)
    def reset_form(self):
        self.nom.clear()
        self.prenom.clear()
        self.email.clear()
        self.password.clear()
        self.confirm_password.clear()
        self.adresse.clear()
        self.telephone.clear()
        self.date_naissance.setDate(QDate.currentDate())  # Réinitialise la date

    # Pour décocher les boutons radio (homme/femme)
        self.homme.setAutoExclusive(False)
        self.femme.setAutoExclusive(False)
        self.homme.setChecked(False)
        self.femme.setChecked(False)
        self.homme.setAutoExclusive(True)
        self.femme.setAutoExclusive(True)
