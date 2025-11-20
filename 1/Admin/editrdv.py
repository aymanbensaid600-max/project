from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QComboBox, QDateTimeEdit,
    QVBoxLayout, QFrame, QApplication
)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt, QDateTime
from Accueil.CustomPopup import CustomPopup
import requests
import sys

class ModifierRendezVous(QWidget):
    def __init__(self, id_rdv):
        super().__init__()
        self.setWindowTitle("Modifier le Rendez-vous")
        self.setWindowIcon(QIcon("calendar_icon.png"))
        self.setFixedSize(450, 430)

        self.id_rdv = id_rdv
        self.medecins = []

        main_layout = QVBoxLayout(self)
        frame = QFrame()
        frame.setStyleSheet("background-color: white; border-radius: 10px;")
        layout = QVBoxLayout(frame)
        layout.setSpacing(15)

        title = QLabel("Modifier un rendez-vous")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #00796b; margin-bottom: 20px;")
        layout.addWidget(title)

        layout.addWidget(QLabel("Patient :"))
        self.combo_patient = QComboBox()
        self.combo_patient.setEnabled(False)
        self.combo_patient.setStyleSheet(self._style_combobox())
        layout.addWidget(self.combo_patient)

        layout.addWidget(QLabel("Médecin :"))
        self.combo_medecin = QComboBox()
        self.combo_medecin.setStyleSheet(self._style_combobox())
        layout.addWidget(self.combo_medecin)

        layout.addWidget(QLabel("Date et heure :"))
        self.date_heure = QDateTimeEdit(QDateTime.currentDateTime())
        self.date_heure.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.date_heure.setCalendarPopup(True)
        self.date_heure.setStyleSheet(self._style_datetimeedit())
        layout.addWidget(self.date_heure)

        self.bouton_valider = QPushButton("Enregistrer")
        self.bouton_valider.setStyleSheet("""
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
        self.bouton_valider.clicked.connect(self.modifier_rdv)
        layout.addWidget(self.bouton_valider)

        main_layout.addWidget(frame)

        self.charger_donnees()

    def charger_donnees(self):
        # Charger les médecins
        try:
            r = requests.get("http://127.0.0.1:5000/AfficheMed")
            if r.status_code == 200:
                self.medecins = r.json()
                for m in self.medecins:
                    full_name = f"{m['nom']} {m['prenom']}".strip()
                    self.combo_medecin.addItem(full_name, m["id_medecin"])
        except Exception as e:
            print("Erreur chargement médecins :", e)

        # Charger infos rendez-vous
        try:
            r = requests.post("http://127.0.0.1:5000/get_rdv_by_id", json={"id_rdv": self.id_rdv})
            if r.status_code == 200:
                rdv = r.json()
                patient_nom = f"{rdv['patient_nom']} {rdv['patient_prenom']}"
                self.combo_patient.addItem(patient_nom, rdv["id_patient"])

                index_med = self.combo_medecin.findData(rdv["id_medecin"])
                if index_med != -1:
                    self.combo_medecin.setCurrentIndex(index_med)

                dt = QDateTime.fromString(rdv["date_heure"], "yyyy-MM-dd HH:mm:ss")
                if dt.isValid():
                    self.date_heure.setDateTime(dt)
        except Exception as e:
            print("Erreur chargement rendez-vous :", e)

    def modifier_rdv(self):
        id_medecin = self.combo_medecin.currentData()
        date_heure = self.date_heure.dateTime().toString("yyyy-MM-dd HH:mm:ss")

        data = {
            "id_rdv": self.id_rdv,
            "id_medecin": id_medecin,
            "date_heure": date_heure
        }

        try:
            r = requests.post("http://127.0.0.1:5000/modifier_rendezvous", json=data)
            if r.status_code == 200 and r.json().get("success"):
                self.popup = CustomPopup(popup_type="success", message="Rendez-vous modifié avec succès !")
                self.popup.show_centered(self)
                self.close()
            else:
                print("Erreur lors de la modification du rendez-vous.")
        except Exception as e:
            print("Erreur connexion serveur :", e)

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
            border-left: 1px solid #b0bec5;
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
                border-left: 1px solid #b0bec5;
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModifierRendezVous(id_rdv=1)
    window.show()
    sys.exit(app.exec())
