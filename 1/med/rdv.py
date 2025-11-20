from PySide6.QtWidgets import (
    QWidget, QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
    QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLineEdit
)
from PySide6.QtGui import QFont, QBrush, QColor
from PySide6.QtCore import Qt
import requests
from datetime import datetime

class MesRendezVousMedecin(QWidget):
    def __init__(self, id_medecin):
        super().__init__()
        self.id_medecin = id_medecin
        self.setup_ui()
        self.charger_rendez_vous()

    def setup_ui(self):
        self.setStyleSheet("""
            QLabel {
                color: #333;
            }
            QComboBox, QLineEdit {
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit {
                min-width: 200px;
            }
            QPushButton {
                background-color: #00796b;
                color: white;
                padding: 6px 12px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #00695c;
            }
            QTableWidget {
                background-color: white;
                border-radius: 8px;
                gridline-color: #ccc;
            }
            QHeaderView::section {
                background-color: #00796b;
                padding: 6px;
                border: none;
                font-weight: bold;
                color: white;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Mes Rendez-vous")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #00796b;")
        layout.addWidget(title)

        filter_layout = QHBoxLayout()

        self.statut_combo = QComboBox()
        self.statut_combo.addItem("Tous", "all")
        self.statut_combo.addItem("Confirmé", "Confirmé")
        self.statut_combo.addItem("En attente", "En attente")
        self.statut_combo.addItem("Annulé", "Annulé")
        self.statut_combo.currentIndexChanged.connect(self.charger_rendez_vous)

        filter_layout.addWidget(QLabel("Statut:"))
        filter_layout.addWidget(self.statut_combo)

        self.recherche_edit = QLineEdit()
        self.recherche_edit.setPlaceholderText("Rechercher un patient...")
        self.recherche_edit.textChanged.connect(self.charger_rendez_vous)
        filter_layout.addWidget(self.recherche_edit)

        filter_layout.addStretch()

        refresh_btn = QPushButton("Actualiser")
        refresh_btn.clicked.connect(self.charger_rendez_vous)
        filter_layout.addWidget(refresh_btn)

        layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Date", "Heure", "Patient", "Statut"])
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget::item {
                padding: 6px;
            }
            QTableWidget::item:selected {
                background-color: #b2dfdb;
            }
        """)

        # Ajustement des tailles de colonnes
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)  # patient réduit automatiquement
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)

        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.table)

    def charger_rendez_vous(self):
        try:
            statut_selected = self.statut_combo.currentData()
            recherche = self.recherche_edit.text().strip().lower()

            response = requests.get("http://127.0.0.1:5000/charger_mesrdv", params={'id_med': self.id_medecin})
            if response.status_code == 200:
                rendez_vous = response.json()

                if statut_selected != "all":
                    rendez_vous = [rdv for rdv in rendez_vous if rdv['statut'] == statut_selected]

                if recherche:
                    rendez_vous = [rdv for rdv in rendez_vous if recherche in rdv['patient'].lower()]

                self.afficher_rendez_vous(rendez_vous)
            else:
                print(f"Erreur serveur: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Erreur réseau: {e}")

    def afficher_rendez_vous(self, rendez_vous):
        self.table.setRowCount(len(rendez_vous))
        for row, rdv in enumerate(rendez_vous):
            try:
                date_heure = datetime.strptime(rdv['date_heure'], "%a, %d %b %Y %H:%M:%S %Z")
            except:
                date_heure = datetime.fromisoformat(rdv['date_heure'])

            date = date_heure.strftime("%d/%m/%Y")
            heure = date_heure.strftime("%H:%M")

            self.table.setItem(row, 0, QTableWidgetItem(date))
            self.table.setItem(row, 1, QTableWidgetItem(heure))

            patient_item = QTableWidgetItem(rdv['patient'])
            patient_item.setToolTip(rdv['patient'])
            self.table.setItem(row, 2, patient_item)

            statut_item = QTableWidgetItem(rdv['statut'])
            statut_item.setTextAlignment(Qt.AlignCenter)
            if rdv['statut'] == "Confirmé":
                statut_item.setBackground(QBrush(QColor("#c8e6c9")))
            elif rdv['statut'] == "En attente":
                statut_item.setBackground(QBrush(QColor("#fff9c4")))
            elif rdv['statut'] == "Annulé":
                statut_item.setBackground(QBrush(QColor("#ffcdd2")))
            self.table.setItem(row, 3, statut_item)
