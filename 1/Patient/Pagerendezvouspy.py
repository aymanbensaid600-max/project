from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton,
    QFrame, QApplication, QMessageBox, QDateEdit,
    QSizePolicy, QScrollArea
)
from PySide6.QtCore import Qt, QDate, QUrl
from PySide6.QtGui import QFont, QDesktopServices
import sys
import requests
from Accueil.CustomPopup import CustomPopup


class PageRendezVousPatient(QWidget):
    def __init__(self, patient_id):
        super().__init__()
        self.patient_id = patient_id
        self.setStyleSheet("background-color: #f0f4f8;")

        # Charger la liste des médecins et les données du patient
        self.charger_med()
        self.load_patient_data()
        self.historique = None

        # Widget principal qui contiendra tout (pour le scroll principal)
        self.widget_central = QWidget()
        main_layout = QVBoxLayout(self.widget_central)
        main_layout.setSpacing(10)

        # Titre
        titre = QLabel(f"Prise de rendez-vous - Patient #{patient_id}")
        titre.setFont(QFont("Segoe UI", 20, QFont.Bold))
        titre.setStyleSheet("color: #004d40; margin-bottom: 10px;")
        titre.setMaximumHeight(40)
        main_layout.addWidget(titre)

        # Layout vertical pour la section principale
        section_layout = QVBoxLayout()
        section_layout.setSpacing(15)

        # --- Partie Prise de RDV ---
        rdv_frame = QFrame()
        rdv_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 16px;
            }
        """)
        rdv_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        rdv_layout = QVBoxLayout(rdv_frame)
        rdv_layout.setContentsMargins(15, 15, 15, 15)
        rdv_layout.setSpacing(12)

        # Label et Combo Médecin
        label1 = QLabel("Sélection du médecin")
        label1.setStyleSheet("font-size: 14px; color: #37474f; font-weight: bold;")
        rdv_layout.addWidget(label1)

        self.combo_medecin = QComboBox()
        for info in self.medecin:
            self.combo_medecin.addItem(info["nom"], info["id_medecin"])
        self.combo_medecin.currentIndexChanged.connect(self.update_creneaux)
        self.combo_medecin.setStyleSheet(self._style_combobox())
        rdv_layout.addWidget(self.combo_medecin)

        # Label et DateEdit
        label2 = QLabel("Date du rendez-vous")
        label2.setStyleSheet("font-size: 14px; color: #37474f; font-weight: bold;")
        rdv_layout.addWidget(label2)

        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.dateChanged.connect(self.update_creneaux)
        self.date_edit.setStyleSheet(self._style_dateedit())
        rdv_layout.addWidget(self.date_edit)

        # Label et Combo Créneau
        label3 = QLabel("Créneau horaire disponible")
        label3.setStyleSheet("font-size: 14px; color: #37474f; font-weight: bold;")
        rdv_layout.addWidget(label3)

        self.combo_creneau = QComboBox()
        self.combo_creneau.setStyleSheet(self._style_combobox())
        rdv_layout.addWidget(self.combo_creneau)

        # Bouton prendre RDV
        self.btn_prendre = QPushButton("Prendre rendez-vous")
        self.btn_prendre.setStyleSheet("""
            QPushButton {
                background-color: #009688;
                color: white;
                font-size: 15px;
                padding: 12px;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00796b;
            }
            QPushButton:pressed {
                background-color: #004d40;
            }
        """)
        self.btn_prendre.clicked.connect(self.prendre_rdv)
        rdv_layout.addWidget(self.btn_prendre)
        rdv_layout.addStretch()

        # --- Partie Historique ---
        historique_frame = QFrame()
        historique_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 16px;
            }
        """)
        historique_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        hist_layout = QVBoxLayout(historique_frame)
        hist_layout.setContentsMargins(15, 15, 15, 15)
        hist_layout.setSpacing(10)

        hist_label = QLabel("Historique de vos rendez-vous :")
        hist_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        hist_label.setStyleSheet("color: #004d40;")
        hist_layout.addWidget(hist_label)

        # Ici on retire le QScrollArea pour historique, juste un widget normal
        self.hist_widget = QWidget()
        self.hist_layout = QVBoxLayout(self.hist_widget)
        self.hist_layout.setAlignment(Qt.AlignTop)
        self.hist_widget.setStyleSheet("background-color:White;")

        hist_layout.addWidget(self.hist_widget)

        # Ajout au layout principal
        section_layout.addWidget(rdv_frame, 1)
        section_layout.addWidget(historique_frame, 1)

        main_layout.addLayout(section_layout)

        # Scroll principal qui englobe tout le contenu
        scroll_principal = QScrollArea()
        scroll_principal.setWidgetResizable(True)
        scroll_principal.setWidget(self.widget_central)
        scroll_principal.setStyleSheet(""" QScrollArea {
                border: none;
                background-color: #f5f5f5;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 12px;
                margin: 2px 0 2px 0;
            }
            QScrollBar::handle:vertical {
                background: #80cbc4;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #4db6ac;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)

        # Layout principal de la fenêtre
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.addWidget(scroll_principal)

        # Initialisation
        self.update_creneaux()
        self.charger_historique()
        self.afficher_historique()

    # Le reste de ton code (styles, fonctions, etc) reste inchangé
    # ... (idem code que tu as fourni)

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

    def _style_dateedit(self):
        return """
        QDateEdit {
            background-color: #f0f4f8;
            border: 1px solid #b0bec5;
            padding: 8px;
            border-radius: 8px;
            font-size: 14px;
            color: #37474f;
        }
        QDateEdit:focus {
            border: 2px solid #00796b;
            background-color: #e0f2f1;
        }
        QDateEdit::drop-down {
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
        QDateEdit::down-arrow {
            image: url(down_arrow_icon.png);
            width: 14px;
            height: 14px;
        }
        """


    def load_patient_data(self):
        try:
            url = f"http://127.0.0.1:5000/charger?id_patient={self.patient_id}"
            response = requests.get(url)
            if response.status_code == 200:
                self.patient = response.json()
            else:
                self.patient = {"nom": "Inconnu", "prenom": ""}
                self.popup = CustomPopup(popup_type="error", message="Impossible de récupérer les données du patient !")
                self.popup.show_centered(self)
        except Exception as e:
            self.patient = {"nom": "Erreur", "prenom": ""}
            self.popup = CustomPopup(popup_type="error", message=f"Erreur réseau : {e}")
            self.popup.show_centered(self)

    def update_creneaux(self):
        self.combo_creneau.clear()
        med_id = self.combo_medecin.currentData()
        if med_id is None:
            return
        date = self.date_edit.date().toString("yyyy-MM-dd")

        url = f"http://127.0.0.1:5000/creneaux_disponibles?medecin_id={med_id}&date={date}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                creneaux = data.get("creneaux", [])
                if creneaux:
                    self.combo_creneau.addItems(creneaux)
                    self.combo_creneau.setEnabled(True)
                else:
                    self.combo_creneau.addItem("Aucun créneau disponible")
                    self.combo_creneau.setEnabled(False)
            else:
                self.combo_creneau.addItem("Erreur de serveur")
                self.combo_creneau.setEnabled(False)
        except Exception as e:
            self.combo_creneau.addItem("Erreur de connexion")
            self.combo_creneau.setEnabled(False)
            print(f"Erreur lors de la requête Flask : {e}")

    def charger_med(self):
        url = "http://127.0.0.1:5000/getMede"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                self.medecin = response.json()
            else:
                self.medecin = []
        except Exception as e:
            self.medecin = []
            print(f"Erreur lors de la requête Flask : {e}")

    def charger_historique(self):
        try:
            url = f"http://127.0.0.1:5000/historique_rdv/{self.patient_id}"
            response = requests.get(url)
            if response.status_code == 200:
                self.historique = response.json().get("dossier", {}).get("suivis", [])

                print("Réponse brute :", response.text)
                print("Historique chargé :", self.historique)
            else:
                self.historique = []
        except Exception as e:
            self.historique = []
            print(f"Erreur lors de la requête Flask : {e}")

    def afficher_historique(self):
        # Vider le layout avant ajout
        while self.hist_layout.count():
            child = self.hist_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not self.historique:
            label = QLabel("Aucun rendez-vous précédent.")
            label.setStyleSheet("font-style: italic; color: gray; font-size: 13px;")
            self.hist_layout.addWidget(label)
            return

        for item in self.historique:
            frame = QFrame()
            frame.setStyleSheet("""
                QFrame {
                    background-color: #e0f2f1;
                    border-radius: 10px;
                    padding: 10px;
                }
            """)
            layout = QVBoxLayout(frame)

            date = item.get("date_suivi", "")
            observations = item.get("observations", "Aucune")
            fichier = item.get("fichier_ordonnance", None)

# Création d'une frame pour ce suivi
            suivi_frame = QFrame()      
            suivi_frame.setFrameShape(QFrame.StyledPanel)
            suivi_layout = QVBoxLayout(suivi_frame)

            suivi_layout.addWidget(QLabel(f"<b>Date :</b> {date}"))
            suivi_layout.addWidget(QLabel(f"<b>Observations :</b> {observations}"))

            if fichier:
                btn_download = QPushButton("Télécharger ordonnance")
                btn_download.setFlat(True)
                btn_download.clicked.connect(lambda _, f=fichier: self.telecharger_pdf(f))
                btn_download.setStyleSheet( """
            QPushButton:hover {
                background-color: #00796b;
            }
            QPushButton:pressed {
                background-color: #004d40;
            }
        """)
                suivi_layout.addWidget(btn_download)

            self.hist_layout.addWidget(suivi_frame)


    def prendre_rdv(self):
        med_id = self.combo_medecin.currentData()
        date = self.date_edit.date().toString("yyyy-MM-dd")
        creneau = self.combo_creneau.currentText()

        if med_id is None or not date or not creneau or self.combo_creneau.count() == 0 or not self.combo_creneau.isEnabled():
            self.popup = CustomPopup(popup_type="error", message="Veuillez remplir tous les champs correctement.")
            self.popup.show_centered(self)
            return

        payload = {
            "patient_id": self.patient_id,
            "medecin_id": med_id,
            "date": date,
            "heure": creneau
        }
        try:
            url = "http://127.0.0.1:5000/prendre_rdv"
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                self.popup = CustomPopup(popup_type="success", message="Rendez-vous enregistré avec succès.")
                self.popup.show_centered(self)
                self.update_creneaux()
                self.charger_historique()
                self.afficher_historique()
            else:
                self.popup = CustomPopup(popup_type="error", message="Erreur lors de la prise de rendez-vous.")
                self.popup.show_centered(self)
        except Exception as e:
            self.popup = CustomPopup(popup_type="error", message=f"Erreur réseau : {e}")
            self.popup.show_centered(self)

    def telecharger_pdf(self, fichier):
        url_pdf = f"http://127.0.0.1:5000/uploads/ordonnances/{fichier}"
        qurl = QUrl(url_pdf)
        if not QDesktopServices.openUrl(qurl):
            QMessageBox.warning(self, "Erreur", "Impossible d'ouvrir le fichier PDF.")