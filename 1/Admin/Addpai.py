from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QComboBox, QDateEdit,
    QVBoxLayout, QHBoxLayout, QFrame, QApplication, QDoubleSpinBox, QCompleter
)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt, QDate
import requests
import sys
from datetime import datetime
from Accueil.CustomPopup import CustomPopup  # Assure-toi que ce fichier est bien présent


class ComboBoxReload(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.patient = []
        self.setEditable(True)

        # Crée le completer AVANT
        self.completer = QCompleter([], self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.setCompleter(self.completer)

        # Puis charge les patients (met à jour aussi le completer)
        self.chargerPatient()



    def chargerPatient(self):
        try:
            response = requests.get("http://127.0.0.1:5000/Affiche")
            if response.status_code == 200:
                self.patient = response.json()
            else:
                self.patient = []
        except:
            self.patient = []

        self.clear()
        noms_complets = []
        for p in self.patient:
            full_name = f"{p.get('nom', 'Inconnu')} {p.get('prenom', '')}".strip()
            self.addItem(full_name, p.get("id_patient"))
            noms_complets.append(full_name)

        model = self.completer.model()
        model.setStringList(noms_complets)



class AddPaiement(QWidget):
    def __init__(self):
        super().__init__()
        self.ajout_effect = False
        self.setWindowTitle("Ajouter un Paiement")
        self.setWindowIcon(QIcon("payment_icon.png"))
        self.setFixedSize(510, 500)

        main_layout = QVBoxLayout(self)

        frame = QFrame()
        frame.setStyleSheet("background-color: white; border-radius: 10px;")
        layout = QVBoxLayout(frame)
        layout.setSpacing(20)

        title = QLabel("Ajouter un Paiement")
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
        self.rdv = []
        self.chargerRdv()

        self.combo_patient = ComboBoxReload()
        self.combo_patient.setEditable(True)
        self.combo_patient.setCurrentIndex(-1)
        self.combo_patient.setEditText("")
        self.combo_patient.setStyleSheet(champs_style)
        self.combo_patient.currentIndexChanged.connect(self.mettre_a_jour_rdv_pour_patient)
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

        btn_submit = QPushButton("Valider le paiement")
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

    def mettre_a_jour_rdv_pour_patient(self):
        id_patient_selectionne = self.combo_patient.currentData()
        self.combo_rdv.clear()

        if id_patient_selectionne is None:
            self.combo_rdv.addItem("Aucun patient sélectionné", None)
            return

        rdv_filtres = [r for r in self.rdv if r.get("id_patient") == id_patient_selectionne]
        if not rdv_filtres:
            self.combo_rdv.addItem("Aucun rendez-vous trouvé", None)
        else:
            for r in rdv_filtres:
                dt = r.get("date_heure")
                if isinstance(dt, datetime):
                    date_str = dt.strftime("%d/%m/%Y %H:%M")
                else:
                    date_str = str(dt)
                label = f"{date_str} - ID {r.get('id_rdv')}"
                self.combo_rdv.addItem(label, r.get("id_rdv"))

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
        QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
            border: none;
            background: none;
            width: 0px;
            height: 0px;
        }
        """

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
            response = requests.post("http://127.0.0.1:5000/ajouter_paiement", json=data)
            if response.status_code == 200 and response.json().get("success"):
                self.ajout_effect = True
                self.close()
            else:
                CustomPopup("error", "Erreur lors de l'enregistrement.").show_centered(self)
        except requests.exceptions.RequestException:
            CustomPopup("error", "Erreur réseau : serveur injoignable.").show_centered(self)

    def chargerRdv(self):
        try:
            response = requests.get("http://127.0.0.1:5000/rendezvous")
            if response.status_code == 200:
                self.rdv = response.json()
                for r in self.rdv:
                    try:
                        r["date_heure"] = datetime.fromisoformat(r["date_heure"])
                    except Exception:
                        pass
            else:
                self.rdv = []
        except:
            self.rdv = []


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AddPaiement()
    window.show()
    sys.exit(app.exec())
