from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QComboBox,
    QPushButton, QTextEdit, QFileDialog, QFrame, QApplication, QCompleter, QDialog, QMessageBox
)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt
import requests
import sys
import os

class FichePatient(QDialog):
    def __init__(self, id_patient):
        super().__init__()
        self.setWindowTitle("Fiche Patient")
        self.setWindowIcon(QIcon("patient_icon.png"))
        self.setFixedSize(500, 600)
        self.id_patient = id_patient.get("id_patient")
        self.id_medecin = id_patient.get("id_medecin")
        self.id_dossier = id_patient.get("id_dossier")
        self.rendezvous = []
        self.chemin_fichier = None  # Ordonnance à envoyer

        main_layout = QVBoxLayout(self)
        frame = QFrame()
        frame.setStyleSheet("background-color: white; border-radius: 10px;")
        layout = QVBoxLayout(frame)
        layout.setSpacing(15)

        # Titre
        title = QLabel("Fiche Patient")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #00796b; margin-bottom: 20px;")
        layout.addWidget(title)

        # Nom + prénom
        self.label_nom = QLabel("Nom: ")
        self.label_nom.setFont(QFont("Segoe UI", 14))
        layout.addWidget(self.label_nom)

        self.label_prenom = QLabel("Prénom: ")
        self.label_prenom.setFont(QFont("Segoe UI", 14))
        layout.addWidget(self.label_prenom)

        # ComboBox rendez-vous
        layout.addWidget(QLabel("Rendez-vous :"))
        self.combo_rdv = QComboBox()
        self.combo_rdv.setEditable(True)
        self.combo_rdv.setInsertPolicy(QComboBox.NoInsert)
        self.combo_rdv.completer().setFilterMode(Qt.MatchContains)
        self.combo_rdv.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.combo_rdv.lineEdit().textEdited.connect(self.filtrer_rdv)
        self.combo_rdv.setStyleSheet("""
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
        """)
        layout.addWidget(self.combo_rdv)

        # Observation
        layout.addWidget(QLabel("Observations :"))
        self.text_observation = QTextEdit()
        self.text_observation.setPlaceholderText("Saisir les observations...")
        self.text_observation.setStyleSheet("""
            QTextEdit {
                background-color: #f0f4f8;
                border: 1px solid #b0bec5;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }
            QTextEdit:focus {
                border: 2px solid #00796b;
                background-color: #e0f2f1;
            }
        """)
        layout.addWidget(self.text_observation)

        # Import ordonnance
        h_layout = QHBoxLayout()
        self.btn_importer = QPushButton("Importer ordonnance")
        self.btn_importer.setStyleSheet("""
            QPushButton {
                background-color: #00796b;
                color: white;
                padding: 10px 20px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #004d40;
            }
        """)
        self.btn_importer.clicked.connect(self.importer_ordonnance)
        h_layout.addWidget(self.btn_importer)

        self.label_fichier = QLabel("Aucun fichier sélectionné")
        self.label_fichier.setStyleSheet("font-style: italic; color: #666666;")
        h_layout.addWidget(self.label_fichier)
        layout.addLayout(h_layout)

        # Bouton Valider
        self.btn_valider = QPushButton("Valider")
        self.btn_valider.setStyleSheet("""
            QPushButton {
                background-color: #388e3c;
                color: white;
                padding: 10px 25px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2e7d32;
            }
        """)
        self.btn_valider.clicked.connect(self.enregistrer_observation)
        layout.addWidget(self.btn_valider, alignment=Qt.AlignCenter)

        main_layout.addWidget(frame)

        self.charger_donnees()

    def charger_donnees(self):
        try:
            r = requests.get(f"http://127.0.0.1:5000/get_patient?id_patient={self.id_patient}")
            if r.status_code == 200:
                patient = r.json()
                self.label_nom.setText(f"Nom: {patient.get('nom', '')}")
                self.label_prenom.setText(f"Prénom: {patient.get('prenom', '')}")
                self.text_observation.setPlainText(patient.get("observation", ""))
            else:
                print("Erreur chargement patient:", r.status_code)
        except Exception as e:
            print("Erreur réseau patient:", e)

        try:
            r = requests.get(f"http://127.0.0.1:5000/get_rendezvous_patient?id_patient={self.id_patient}&id_medecin={self.id_medecin}")
            if r.status_code == 200:
                self.rendezvous = r.json()
                self.afficher_rendezvous()
            else:
                print("Erreur chargement rdv:", r.status_code)
        except Exception as e:
            print("Erreur réseau rdv:", e)

    def afficher_rendezvous(self):
        self.combo_rdv.clear()
        for rdv in self.rendezvous:
            dt = rdv.get("date_heure", "N/A")
            medecin = rdv.get("medecin_nom", "N/A")
            statut = rdv.get("statut", "N/A")
            texte = f"{dt} - {medecin} ({statut})"
            self.combo_rdv.addItem(texte, rdv.get("id_rdv"))

    def importer_ordonnance(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Choisir un fichier ordonnance", "", "PDF Files (*.pdf);;All Files (*)")
        if file_path:
            self.chemin_fichier = file_path
            self.label_fichier.setText(os.path.basename(file_path))

    def enregistrer_observation(self):
        observation = self.text_observation.toPlainText().strip()
        if not observation and not self.chemin_fichier:
            QMessageBox.warning(self, "Erreur", "Aucune observation ni fichier à envoyer.")
            return
        id_rdv = self.combo_rdv.currentData()
        try:
            data = {
                "id_dossier":str(self.id_dossier),
                "id_patient": str(self.id_patient),
                "id_rdv": str(id_rdv) if id_rdv else "",
                "observation": observation
            }

            files = {}
            if self.chemin_fichier:
                files["ordonnance"] = open(self.chemin_fichier, "rb")

            r = requests.post("http://127.0.0.1:5000/update_observation", data=data, files=files)

            if r.status_code == 200:
                QMessageBox.information(self, "Succès", "Observation et fichier envoyés avec succès.")
                # Optionnel : Réinitialiser l'interface
                self.chemin_fichier = None
                self.label_fichier.setText("Aucun fichier sélectionné")
                self.accept()

            else:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de l'envoi: {r.status_code}")

        except Exception as e:
            QMessageBox.critical(self, "Erreur réseau", str(e))
        finally:
            if self.chemin_fichier:
                files["ordonnance"].close()

    def filtrer_rdv(self, text):
        if text.strip():
            self.combo_rdv.showPopup()
        else:
            self.combo_rdv.hidePopup()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Exemple de test
    window = FichePatient(id_patient={"id_patient": 1, "id_medecin": 2})
    window.show()
    sys.exit(app.exec())
