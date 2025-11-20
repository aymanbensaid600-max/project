from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, QFrame, QCheckBox,QGraphicsOpacityEffect
)
from Admin.DashboardPage import DashboardPage
from Patient.Patientdash import PatientDash  # Import du DashboardPage
from PySide6.QtGui import QFont, QPixmap, QIcon
from PySide6.QtCore import Qt
from Accueil.RegistrationPage import RegistrationPage
from med.meddash import MedecinDash
import requests


class MedicalLoginPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Connexion - Cabinet Médical")
        self.setMinimumSize(1000, 600)
        self.setWindowIcon(QIcon("healthcare.png"))  

       
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        
        self.image_frame = QFrame()
        self.image_frame.setStyleSheet("background-color: #e0f7fa;")
        image_layout = QVBoxLayout(self.image_frame)
        image_layout.setContentsMargins(0, 0, 0, 0)

        self.image_label = QLabel()
        self.pixmap = QPixmap("pola.png")  
        if self.pixmap.isNull():
            print("Erreur: L'image n'a pas pu être chargée.")
        else:
            self.image_label.setPixmap(self.pixmap)
            self.image_label.setScaledContents(True)
            self.image_label.setAlignment(Qt.AlignCenter)
            opacity_effect = QGraphicsOpacityEffect()
            opacity_effect.setOpacity(1)  
            self.image_label.setGraphicsEffect(opacity_effect)
            image_layout.addWidget(self.image_label)

      
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: white; border;none;")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(80, 80, 80, 80)
        form_layout.setSpacing(25)

      
        title = QLabel("Bienvenue au Cabinet Médical")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet("color: #00796b;")
        title.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(title)

        self.email = QLineEdit()
        self.email.setPlaceholderText("Adresse Email")
        self.email.setStyleSheet(""" 
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
        """)
        form_layout.addWidget(self.email)

       
        self.password = QLineEdit()
        self.password.setPlaceholderText("Mot de passe")
        self.password.setEchoMode(QLineEdit.Password) 
        self.password.setStyleSheet(""" 
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
        """)
        form_layout.addWidget(self.password)

       
        self.show_password_checkbox = QCheckBox("Afficher le mot de passe")
        self.show_password_checkbox.stateChanged.connect(self.toggle_password_visibility)
        form_layout.addWidget(self.show_password_checkbox)

       
        login_btn = QPushButton("Se connecter")
        login_btn.setStyleSheet("""
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
        form_layout.addWidget(login_btn)

       
        link_layout = QHBoxLayout()
        forgot = QPushButton("Mot de passe oublié ?")
        forgot.setFlat(True)
        forgot.setStyleSheet("color: #00796b; border: none; font-size: 12px;")
        forgot.setStyleSheet("""QPushButton {
                color: #00796b;
                border: none;
                font-size: 12px;
            }
            QPushButton:hover {
                color: #b0bec5;
            }
        """)
        register = QPushButton("S’inscrire")
        register.setFlat(True)
        register.setStyleSheet("""
            color: #00796b; 
            border: none; 
            font-size: 12px;
        """)
        
        register.setStyleSheet("""
            QPushButton {
                color: #00796b;
                border: none;
                font-size: 12px;
            }
            QPushButton:hover {
                color: #b0bec5;
            }
        """)
        
       
        register.setCursor(Qt.PointingHandCursor)  
        forgot.setCursor(Qt.PointingHandCursor) 
        login_btn.setCursor(Qt.PointingHandCursor) 
        register.clicked.connect(self.show_registration_form)

        link_layout.addWidget(forgot)
        link_layout.addStretch()
        link_layout.addWidget(register)
        form_layout.addLayout(link_layout)

     
        main_layout.addWidget(self.image_frame, 1)
        main_layout.addWidget(form_frame, 1)

       
        login_btn.clicked.connect(self.check_and_login)

    def toggle_password_visibility(self, state):
        """Change l'affichage du mot de passe en fonction de la case à cocher"""
        if self.show_password_checkbox.isChecked():
            self.password.setEchoMode(QLineEdit.Normal)  
        else:
            self.password.setEchoMode(QLineEdit.Password)  

    def show_registration_form(self, event=None):
        self.registration_window = RegistrationPage()  # 
        self.registration_window.show()

    def closeEvent(self, event):
        if hasattr(self, "registration_window"):
            try:
                self.registration_window.close()
            except Exception as e:
                print("Erreur fermeture registration_window:", e)
        super().closeEvent(event)



    def check_and_login(self):
        """Vérifie si les champs sont remplis avant de permettre la connexion"""
        email = self.email.text().strip()
        password = self.password.text().strip()

        
        self.reset_field_placeholders()
        if not email or not password:
       
            if not email:
                self.email.setPlaceholderText("Adresse Email - Ce champ est requis")
                self.email.setStyleSheet(""" 
                    QLineEdit {
                        background-color: #f0f4f8;
                        border: 1px solid red;
                        padding: 12px;
                        border-radius: 8px;
                        
                    }
                                         
                """)
            if not password:
                self.password.setPlaceholderText("Mot de passe - Ce champ est requis")
                self.password.setStyleSheet(""" 
                    QLineEdit {
                        background-color: #f0f4f8;
                        border: 1px solid red;
                        padding: 12px;
                        border-radius: 8px;
                       
                    }
                    QLineEdit::placeholder{
                        color:red;                    
                                }
                """)
        else:
            
            self.login(email, password)

    def reset_field_placeholders(self):
        """Réinitialise les placeholders des champs de texte"""
        self.email.setPlaceholderText("Adresse Email")
        self.password.setPlaceholderText("Mot de passe")
        self.email.setStyleSheet(""" 
            QLineEdit {
                background-color: #f0f4f8;
                border: 1px solid #b0bec5;
                padding: 12px;
                border-radius: 8px;
            }
        """)
        self.password.setStyleSheet(""" 
            QLineEdit {
                background-color: #f0f4f8;
                border: 1px solid #b0bec5;
                padding: 12px;
                border-radius: 8px;
            }
            QLineEdit::placeholder{
                color:red;                    
             }
        """)
    def login(self, email, password):
        """Vérifie les identifiants auprès du backend Flask via une requête HTTP"""
        url = "http://127.0.0.1:5000/connexion"  # L'URL de votre API Flask
        data = {"email": email, "mot_de_passe": password}

        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get("success"):
                    type_util=response_data.get("type_utilisateur")
                    print(type_util)
                    if type_util == "admin":
                        print('dmin')
                        self.dashboard = DashboardPage()   # Crée l'instance du Dashboard
                        self.dashboard.show()   
                        self.close()
                        
                    elif type_util=="patient":
                        id=response_data.get("id_pat")
                        print(id)
                        self.patient=PatientDash(id)
                        self.patient.show()  
                        self.close()
                    elif type_util=="medecin":
                        id=response_data.get("id_med")
                        print(id)
                        self.med=MedecinDash(id)
                        self.med.show()  
                        self.close()

                    
                else:
                    self.show_error_message(response_data.get("message"))
            else:
                self.show_error_message("Erreur de connexion au serveur.")
        except requests.exceptions.RequestException as e:
            self.show_error_message("Une erreur est survenue lors de la connexion au serveur.")
    def show_error_message(self, message):
        """Affiche un message d'erreur"""
        print(f"Erreur: {message}")  # Pour le debug
        self.password.setPlaceholderText(message)
        self.password.setStyleSheet("""
            QLineEdit {
                background-color: #f0f4f8;
                border: 1px solid red;
                padding: 12px;
                border-radius: 8px;
            }
            QLineEdit::placeholder {
                color: red;
            }
        """)