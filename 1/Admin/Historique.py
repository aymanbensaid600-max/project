from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QScrollArea, QFrame, QApplication, QMessageBox
)
from PySide6.QtGui import QFont, QCursor, QDesktopServices
from PySide6.QtCore import Qt, Signal, QUrl
from functools import partial
import sys
import requests


class SuiviWidget(QWidget):
    ordonnanceClicked = Signal(int)  # on émet l'id_suivi (int)

    def __init__(self, suivi):
        super().__init__()
        self.suivi = suivi
        self.setMinimumHeight(100)

        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                padding: 10px;
                margin-bottom: 10px;
            }
            QWidget:hover {
                background-color: #e8f5e9;
            }
            QLabel {
                border: none;
                background: transparent;
            }
            QLabel.date_label {
                color: #80cbc4;
                font-weight: 700;
                font-size: 14px;
                margin-bottom: 4px;
            }
            QLabel.observation_label {
                color: #555555;
                font-size: 12px;
                margin-bottom: 8px;
                font-style: italic;
            }
            QLabel.link_label {
                color: #2e7d32;
                font-weight: 600;
                font-size: 13px;
                text-decoration: underline;
            }
            QLabel.no_ord_label {
                color: #999999;
                font-style: italic;
                font-size: 12px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        date_label = QLabel(f"Date : {suivi['date_suivi']}")
        date_label.setObjectName("date_label")
        date_label.setProperty("class", "date_label")
        date_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(date_label)

        obs_text = suivi.get('observations') or "Aucune observation"
        obs_label = QLabel(f"Observation : {obs_text}")
        obs_label.setWordWrap(True)
        obs_label.setObjectName("observation_label")
        obs_label.setProperty("class", "observation_label")
        obs_label.setFont(QFont("Segoe UI", 11))
        layout.addWidget(obs_label)

        ordonnance = suivi.get('fichier_ordonnance')
        if ordonnance and ordonnance.lower().endswith('.pdf'):
            ord_label = QLabel("📎 Voir l'ordonnance")
            ord_label.setObjectName("link_label")
            ord_label.setProperty("class", "link_label")
            ord_label.setFont(QFont("Segoe UI", 11, italic=True))
            ord_label.setCursor(QCursor(Qt.PointingHandCursor))
            ord_label.mousePressEvent = self._on_ordonnance_clicked
            layout.addWidget(ord_label)
        else:
            no_ord = QLabel("📎 Pas d'ordonnance")
            no_ord.setObjectName("no_ord_label")
            no_ord.setProperty("class", "no_ord_label")
            no_ord.setFont(QFont("Segoe UI", 11, italic=True))
            layout.addWidget(no_ord)

    def _on_ordonnance_clicked(self, event):
        id_suivi = self.suivi.get('id_suivi')
        if id_suivi is not None:
            self.ordonnanceClicked.emit(id_suivi)


class HistoriquePatient(QWidget):
    def __init__(self, id_patient):
        super().__init__()
        self.id_patient = id_patient
        self.setWindowTitle("Historique Médical")
        self.resize(500, 450)
        self.setMinimumSize(400, 400)

        self.setStyleSheet("""
            QWidget#main_widget {
                background-color: #f9f9f9;
            }
            QLabel#title_label {
                font-size: 20px;
                font-weight: 700;
                color: #80cbc4;
                padding-bottom: 8px;
                border-bottom: 2px solid #4caf50;
            }
            QLabel#info_patient {
                background-color: #80cbc4;
                border-radius: 12px;
                padding: 10px;
                font-size: 12px;
                color: Black;
                margin-bottom: 15px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(5)

        title_label = QLabel("Historique Médical du Patient")
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        main_layout.addWidget(title_label)

        self.info_patient = QLabel("Chargement des informations...")
        self.info_patient.setObjectName("info_patient")
        self.info_patient.setWordWrap(True)
        self.info_patient.setFont(QFont("Segoe UI", 11))
        main_layout.addWidget(self.info_patient)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet(""" QScrollArea {
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
 
        main_layout.addWidget(scroll_area)

        self.container = QWidget()
        self.container.setObjectName("main_widget")
        scroll_area.setWidget(self.container)

        self.suivi_layout = QVBoxLayout(self.container)
        self.suivi_layout.setContentsMargins(0, 0, 0, 0)
        self.suivi_layout.setSpacing(10)

        self.charger_historique()

    def charger_historique(self):
        try:
            url = f"http://127.0.0.1:5000/historique/{self.id_patient}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    patient = data.get("patient", {})
                    dossier = data.get("dossier", {})

                    self.info_patient.setText(
                        f"<b>Nom :</b> {patient.get('nom', '')} {patient.get('prenom', '')}<br>"
                        f"<b>Date de création du dossier :</b> {dossier.get('date_creation', 'N/A')}"
                    )

                    for i in reversed(range(self.suivi_layout.count())):
                        widget = self.suivi_layout.itemAt(i).widget()
                        if widget:
                            widget.setParent(None)

                    suivis = dossier.get("suivis", [])

                    if not suivis:
                        vide_label = QLabel("Aucun suivi médical pour ce patient.")
                        vide_label.setAlignment(Qt.AlignCenter)
                        vide_label.setFont(QFont("Segoe UI", 12, italic=True))
                        vide_label.setStyleSheet("color: #666666; margin-top: 30px;")
                        self.suivi_layout.addWidget(vide_label)
                    else:
                        for suivi in suivis:
                            suivi_widget = SuiviWidget(suivi)
                            id_suivi = suivi.get('id_suivi', '')
                            # Connexion correcte avec capture de id_suivi
                            suivi_widget.ordonnanceClicked.connect(lambda _: self.telecharger_pdf(id_suivi))

                            cadre = QFrame()
                            cadre.setFrameShape(QFrame.StyledPanel)
                            cadre.setFrameShadow(QFrame.Raised)
                            cadre.setStyleSheet("""
                                QFrame {
                                    border-radius: 10px;
                                    background-color: #ffffff;
                                }
                            """)

                            cadre_layout = QVBoxLayout(cadre)
                            cadre_layout.setContentsMargins(5, 5, 5, 5)
                            cadre_layout.addWidget(suivi_widget)

                            self.suivi_layout.addWidget(cadre)

                    self.suivi_layout.addStretch()
                else:
                    QMessageBox.warning(self, "Erreur", data.get("message", "Erreur inconnue"))
            else:
                QMessageBox.critical(self, "Erreur Serveur", "Impossible de récupérer les données.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur Réseau", f"Impossible de contacter le serveur:\n{e}")

    def telecharger_pdf(self, id_suivi):
        url_pdf = f"http://127.0.0.1:5000/telecharger_ordonnance/{id_suivi}"
        qurl = QUrl(url_pdf)
        if not QDesktopServices.openUrl(qurl):
            QMessageBox.warning(self, "Erreur", "Impossible d'ouvrir le fichier PDF.")
