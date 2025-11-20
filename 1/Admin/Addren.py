from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QComboBox, QDateTimeEdit,
    QVBoxLayout, QFrame, QApplication, QCompleter
)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt, QDateTime
from Accueil.CustomPopup import CustomPopup
import requests
import sys

class AddRendezVous(QWidget):
    def __init__(self):
        super().__init__()
        self.effect=False
        self.setWindowTitle("Ajouter un Rendez-vous")
        self.setWindowIcon(QIcon("calendar_icon.png"))
        self.setFixedSize(450, 430)  # Hauteur augmentée

        self.chargerPatient()
        self.chargerMed()

        main_layout = QVBoxLayout(self)
        

        frame = QFrame()
        frame.setStyleSheet("background-color: white; border-radius: 10px;")
        layout = QVBoxLayout(frame)
        layout.setSpacing(15)

        title = QLabel("Programmer un rendez-vous")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #00796b; margin-bottom: 20px;")
        layout.addWidget(title)

        # Choix patient
        layout.addWidget(QLabel("Patient :"))
        self.combo_patient = QComboBox()
        for p in self.patient:
            nom = p.get("nom", "Inconnu")
            prenom = p.get("prenom", "")
            full_name = f"{nom} {prenom}".strip()
            self.combo_patient.addItem(full_name, p.get("id_patient"))
        self.combo_patient.setStyleSheet(self._style_combobox())
        layout.addWidget(self.combo_patient)
        self.combo_patient.setEditable(True)
        self.combo_patient.setCurrentIndex(-1)
        self.combo_patient.setEditText("")
        liste_patients = [self.combo_patient.itemText(i) for i in range(self.combo_patient.count())]
        completer_patient = QCompleter(liste_patients, self.combo_patient)
        completer_patient.setCaseSensitivity(Qt.CaseInsensitive)
        self.combo_patient.setCompleter(completer_patient)
        # Choix médecin
        layout.addWidget(QLabel("Médecin :"))
        self.combo_medecin = QComboBox()
        for m in self.med:
            nom = m.get("nom", "Inconnu")
            prenom = m.get("prenom", "")
            full_name = f"{nom} {prenom}".strip()
            self.combo_medecin.addItem(full_name, m.get("id_medecin"))
        self.combo_medecin.setStyleSheet(self._style_combobox())
        layout.addWidget(self.combo_medecin)

        # Date & heure
        layout.addWidget(QLabel("Date et heure :"))
        self.date_heure = QDateTimeEdit(QDateTime.currentDateTime())
        self.date_heure.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.date_heure.setCalendarPopup(True)
        self.date_heure.setStyleSheet(self._style_datetimeedit())
        layout.addWidget(self.date_heure)
        self.combo_medecin.setEditable(True)
        self.combo_medecin.setCurrentIndex(-1)
        self.combo_medecin.setEditText("")

        liste_medecins = [self.combo_medecin.itemText(i) for i in range(self.combo_medecin.count())]
        completer_med =  QCompleter(liste_medecins, self.combo_medecin)
        completer_med.setCaseSensitivity(Qt.CaseInsensitive)
        self.combo_medecin.setCompleter(completer_med)

        # Bouton soumettre
        btn_submit = QPushButton("Programmer")
        btn_submit.setStyleSheet("""
    QPushButton {
        background-color: #00796b;
        color: white;
        padding: 14px 0;
        border-radius: 10px;
        font-weight: bold;
        font-size: 16px;
        min-width: 100%;
       
    }
    QPushButton:hover {
        background-color: #004d40;
    }
    QPushButton:pressed {
        background-color: #00332e;
    }
""")
        btn_submit.clicked.connect(self.valider_formulaire)
        layout.addWidget(btn_submit)

        main_layout.addWidget(frame)

    def _style_combobox(self):
        return """
        QComboBox {
            background-color: #ffffff;
            border: 2px solid #b0bec5;
            padding:4px 9px;
            border-radius: 10px;
            min-height: 30px;
            font-size: 14px;
            color: #37474f;
            selection-background-color: #00796b;
            selection-color: white;
        }
        QComboBox:hover {
            border: 2px solid #4db6ac;
            background-color: #f0f9f8;
        }
        QComboBox:focus {
            border: 2px solid #00796b;
            background-color: #e0f2f1;
            color: #004d40;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 25px;
            border-left-width: 1px;
            border-left-color: #b0bec5;
            border-left-style: solid;
            border-top-right-radius: 10px;
            border-bottom-right-radius: 10px;
            background-color: #e0f2f1;
        }
        QComboBox::down-arrow {
            image: url(down_arrow_icon.png);
            width: 14px;
            height: 14px;
        }
    """
    def _style_datetimeedit(self):
        return """
            QDateTimeEdit {
                background-color: #f0f4f8;
                border: 1px solid #b0bec5;
                padding: 8px;
                border-radius: 8px;
            }
            QDateTimeEdit:focus {
                 border: 2px solid #00796b;
            background-color: #e0f2f1;
            color: #004d40;

            }
        QDateTimeEdit::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 25px;
            border-left-width: 1px;
            border-left-color: #b0bec5;
            border-left-style: solid;
            border-top-right-radius: 10px;
            border-bottom-right-radius: 10px;
            background-color: #e0f2f1;
            }
        QDateTimeEdit::down-arrow {
            image: url(down_arrow_icon.png);
            width: 14px;
            height: 14px;
        }
        """

    def valider_formulaire(self):
        patient_index = self.combo_patient.currentIndex()
        medecin_index = self.combo_medecin.currentIndex()

        if patient_index == -1 or medecin_index == -1:
            popup = CustomPopup("error", "Veuillez sélectionner un patient et un médecin.")
            popup.show_centered(self)
            return

        patient_id = self.combo_patient.currentData()
        medecin_id = self.combo_medecin.currentData()
        date_heure = self.date_heure.dateTime().toString("yyyy-MM-dd HH:mm:ss")

        data = {
            "patient_id": patient_id,
            "medecin_id": medecin_id,
            "date_heure": date_heure,
            
        }

        try:
            response = requests.post("http://127.0.0.1:5000/ajouter_rendezvous", json=data)
            if response.status_code == 200 and response.json().get("success"):
                self.effect=True
                self.close()
            else:
                popup = CustomPopup("error", "Erreur lors de l'ajout du rendez-vous.")
                popup.show_centered(self)
        except requests.exceptions.RequestException:
            popup = CustomPopup("error", "Impossible de contacter le serveur.")
            popup.show_centered(self)

    def chargerPatient(self):
        try:
            url = "http://127.0.0.1:5000/Affiche"
            resultas = requests.get(url)
            if resultas.status_code == 200:
                self.patient = resultas.json()
            else:
                self.popup = CustomPopup(popup_type="error", message="Impossible de récupérer les patients !")
                self.popup.show_centered(self)
                self.patient = []
        except Exception as e:
            self.popup = CustomPopup(popup_type="error", message=f"Erreur réseau : {e}")
            self.popup.show_centered(self)
            self.patient = []

    def chargerMed(self):
        try:
            url = "http://127.0.0.1:5000/AfficheMed"
            resultas = requests.get(url)
            if resultas.status_code == 200:
                self.med = resultas.json()
            else:
                self.popup = CustomPopup(popup_type="error", message="Impossible de récupérer les médecins !")
                self.popup.show_centered(self)
                self.med = []
        except Exception as e:
            self.popup = CustomPopup(popup_type="error", message=f"Erreur réseau : {e}")
            self.popup.show_centered(self)
            self.med = []
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window =AddRendezVous()
    window.show()
    sys.exit(app.exec())
