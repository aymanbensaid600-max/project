from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QComboBox, QDateEdit,
    QVBoxLayout, QHBoxLayout, QFrame, QApplication, QDoubleSpinBox
)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt, QDate
import requests
import sys
from Accueil.CustomPopup import CustomPopup


class EDIT_Paiement(QWidget):
    def __init__(self, id_paiement=None):
        super().__init__()
        self.id_paiement = id_paiement
        self.ajout_effect = False
        self.setWindowTitle("Modifier un Paiement" if self.id_paiement else "Ajouter un Paiement")
        self.setWindowIcon(QIcon("payment_icon.png"))
        self.setFixedSize(510, 500)

        self.donnees = {}
        self.rdv = []

        main_layout = QVBoxLayout(self)
        frame = QFrame()
        frame.setStyleSheet("background-color: white; border-radius: 10px;")
        layout = QVBoxLayout(frame)
        layout.setSpacing(20)

        title = QLabel("Modifier un Paiement" if self.id_paiement else "Ajouter un Paiement")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #00796b; margin-bottom: 20px;")
        layout.addWidget(title)

        label_style = "font-weight: bold; font-size: 14px; color: #37474f;"
        champs_style = self._style_champs()

        hbox_patient_rdv = QHBoxLayout()
        hbox_patient_rdv.setSpacing(8)

        v_patient = QVBoxLayout()
        v_patient.addWidget(QLabel("Patient :", styleSheet=label_style))
        self.combo_patient = QComboBox()
        self.combo_patient.setStyleSheet(champs_style)
        v_patient.addWidget(self.combo_patient)

        v_rdv = QVBoxLayout()
        v_rdv.addWidget(QLabel("Rendez-vous :", styleSheet=label_style))
        self.combo_rdv = QComboBox()
        self.combo_rdv.setStyleSheet(champs_style)
        v_rdv.addWidget(self.combo_rdv)

        hbox_patient_rdv.addLayout(v_patient)
        hbox_patient_rdv.addLayout(v_rdv)
        layout.addLayout(hbox_patient_rdv)

        layout.addWidget(QLabel("Date de paiement :", styleSheet=label_style))
        self.date_paiement = QDateEdit(QDate.currentDate())
        self.date_paiement.setCalendarPopup(True)
        self.date_paiement.setStyleSheet(champs_style)
        layout.addWidget(self.date_paiement)

        hbox_montant_mode = QHBoxLayout()
        hbox_montant_mode.setSpacing(10)

        v_montant = QVBoxLayout()
        v_montant.addWidget(QLabel("Montant :", styleSheet=label_style))
        self.montant_input = QDoubleSpinBox()
        self.montant_input.setPrefix("€ ")
        self.montant_input.setRange(0, 100000)
        self.montant_input.setDecimals(2)
        self.montant_input.setStyleSheet(champs_style)
        v_montant.addWidget(self.montant_input)

        v_mode = QVBoxLayout()
        v_mode.addWidget(QLabel("Mode de paiement :", styleSheet=label_style))
        self.combo_mode = QComboBox()
        self.combo_mode.addItems(["Espèce", "Carte Bancaire", "Chèque", "Virement"])
        self.combo_mode.setStyleSheet(champs_style)
        v_mode.addWidget(self.combo_mode)

        hbox_montant_mode.addLayout(v_montant)
        hbox_montant_mode.addLayout(v_mode)
        layout.addLayout(hbox_montant_mode)

        layout.addWidget(QLabel("Paiement effectué :", styleSheet=label_style))
        self.combo_effectue = QComboBox()
        self.combo_effectue.addItems(["Non", "Oui"])
        self.combo_effectue.setStyleSheet(champs_style)
        layout.addWidget(self.combo_effectue)

        btn_submit = QPushButton("Modifier le paiement" if self.id_paiement else "Valider le paiement")
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
        layout.addStretch()
        layout.addWidget(btn_submit)

        main_layout.addWidget(frame)

        # Chargement des données selon ajout ou modification
        if self.id_paiement:
            self.charger_donnees_edition()
        else:
            self.charger_donnees_paiement()

    def _style_champs(self):
        return """
             QComboBox, QDateEdit, QDoubleSpinBox {
            background-color: #ffffff;
            border: 1px solid #b0bec5;
            padding: 6px 8px;
            border-radius: 8px;
            font-size: 14px;
            min-height: 20px;
            color: #37474f;
        }
        QComboBox:hover, QDateEdit:hover, QDoubleSpinBox:hover {
            border: 2px solid #4db6ac;
            background-color: #f0f9f8;
        }
        QComboBox:focus, QDateEdit:focus, QDoubleSpinBox:focus {
            border: 2px solid #00796b;
            background-color: #e0f2f1;
            color: #004d40;
        }
        QComboBox::drop-down, QDateEdit::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 25px;
            border-left: 1px solid #b0bec5;
            background-color: #e0f2f1;
        }
        QComboBox::down-arrow, QDateEdit::down-arrow {
            image: url(down_arrow_icon.png);
            width: 14px;
            height: 14px;
        }
        /* Cacher les flèches du QDoubleSpinBox */
        QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
            border: none;
            background: none;
            width: 0px;
            height: 0px;
        }
        """

    def charger_donnees_edition(self,):
        # Méthode pour la modification : charge uniquement le paiement et ses données liées
        try:
            response = requests.post(f"http://127.0.0.1:5000/charge_edi?index={self.id_paiement}")
            if response.status_code == 200:
                data = response.json()
                if not data:
                    CustomPopup("error", "Aucune donnée trouvée pour ce paiement.").show_centered(self)
                    return

                full_name = f"{data['nom_patient']} {data['prenom_patient']}".strip()
                self.combo_patient.clear()
                self.combo_patient.addItem(full_name, data["id_patient"])

                self.combo_rdv.clear()
                date_str = data.get("date_heure")
                self.combo_rdv.addItem(f"{date_str} - ID {data.get('id_rdv')}", data.get("id_rdv"))

                self.date_paiement.setDate(QDate.fromString(data["date_paiement"], "yyyy-MM-dd"))
                self.montant_input.setValue(float(data.get("montant", 0)))
                self.combo_mode.setCurrentText(data.get("mode_paiement", ""))
                self.combo_effectue.setCurrentIndex(1 if data.get("paiement_effectue") else 0)
            else:
                CustomPopup("error", "Erreur lors du chargement des données.").show_centered(self)
        except Exception as e:
            print("Erreur lors du chargement des données:", e)
            CustomPopup("error", "Erreur réseau : impossible de contacter le serveur.").show_centered(self)

    def remplir_formulaire(self, paiement):
        self.combo_patient.setCurrentIndex(self.combo_patient.findData(paiement.get("id_patient")))
        self.combo_rdv.setCurrentIndex(self.combo_rdv.findData(paiement.get("id_rdv")))
        self.date_paiement.setDate(QDate.fromString(paiement.get("date_paiement"), "yyyy-MM-dd"))
        self.montant_input.setValue(float(paiement.get("montant", 0)))
        self.combo_mode.setCurrentText(paiement.get("mode_paiement", ""))
        self.combo_effectue.setCurrentIndex(1 if paiement.get("paiement_effectue") else 0)

    def valider_formulaire(self):
        id_patient = self.combo_patient.currentData()
        id_rdv = self.combo_rdv.currentData()
        date_paiement = self.date_paiement.date().toString("yyyy-MM-dd")
        montant = self.montant_input.value()
        mode = self.combo_mode.currentText()
        effectue = 1 if self.combo_effectue.currentText() == "Oui" else 0

        data = {
            "id_patient": id_patient,
            "id_rdv": id_rdv,
            "date_paiement": date_paiement,
            "montant": montant,
            "mode_paiement": mode,
            "paiement_effectue": effectue
        }

        try:
            if self.id_paiement:
                url = f"http://127.0.0.1:5000/edit_pai/{self.id_paiement}"
                response = requests.put(url, json=data)
           
            if response.status_code == 200 and response.json().get("success"):
                self.popup = CustomPopup(popup_type="success", message="Paiement modifié avec succès !")
                self.popup.show_centered(self)
                self.close()
            else:
                CustomPopup("error", "Erreur lors de l'enregistrement.").show_centered(self)
        except Exception as e:
            print("Erreur lors de l'enregistrement:", e)
            CustomPopup("error", "Erreur réseau : serveur injoignable.").show_centered(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Exemple avec id_paiement pour modifier
    window = EDIT_Paiement(id_paiement=3)
    window.show()
    sys.exit(app.exec())
