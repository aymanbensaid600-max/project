from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QWidget, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QMessageBox, QSizePolicy, QGraphicsDropShadowEffect
)
from PySide6.QtGui import QFont, QColor, QBrush
from PySide6.QtCore import Qt
import requests

class AccueilMedecin(QWidget):
    def __init__(self, id_medecin):
        super().__init__()
        self.id_medecin = id_medecin
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
            }
        """)
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Titre
        title = QLabel("Tableau de bord")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        main_layout.addWidget(title)

        # Cartes indicateurs
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)

        self.card_patients, self.label_patients = self.create_card("Patients suivis", "0", "#00796b")
        self.card_rdv_today, self.label_rdv_today = self.create_card("RDV aujourd'hui", "0", "#0288d1")
        self.card_rdv_upcoming, self.label_rdv_upcoming = self.create_card("RDV à venir", "0", "#d32f2f")

        for card in [self.card_patients, self.card_rdv_today, self.card_rdv_upcoming]:
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            cards_layout.addWidget(card)

        main_layout.addLayout(cards_layout)

        # Sous-titre tableau
        rdv_title = QLabel("Prochains rendez-vous")
        rdv_title.setFont(QFont("Arial", 14, QFont.Bold))
        main_layout.addWidget(rdv_title)

        # Tableau des RDV
        self.table_rdv = QTableWidget()
        self.table_rdv.setColumnCount(4)
        self.table_rdv.setHorizontalHeaderLabels(["Patient", "Date", "Heure", "Statut"])
        self.table_rdv.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_rdv.verticalHeader().setVisible(False)
        self.table_rdv.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_rdv.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
                gridline-color: #e0e0e0;
                border: none;
                selection-background-color: #e3f2fd;
                selection-color: #333333;
                font-size: 12px;
            }
            
            QHeaderView::section {
                background-color: #00796b;
                color: white;
                padding: 8px 12px;
                font-weight: bold;
                border: none;
                font-size: 12px;
            }
            
            QTableWidget::item {
                padding: 8px 12px;
                border: none;
            }
        """)
        main_layout.addWidget(self.table_rdv)

    def create_card(self, title, value, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 12px;
                padding: 15px;
            }}
            QLabel {{
                color: white;
            }}
        """)
        card.setMinimumHeight(100)

        # Ajout de l’ombre
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(0, 0, 0, 80))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12))
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 24, QFont.Bold))

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addStretch()

        return card, value_label

    def load_data(self):
        try:
            url = f"http://127.0.0.1:5000/medecin_dashboard?id_medecin={self.id_medecin}"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()

                self.label_patients.setText(str(data['total_patients']))
                self.label_rdv_today.setText(str(data['rdv_today']))
                self.label_rdv_upcoming.setText(str(data['rdv_upcoming']))

                self.table_rdv.setRowCount(len(data['prochains_rdv']))
                for row, rdv in enumerate(data['prochains_rdv']):
                    self.table_rdv.setItem(row, 0, QTableWidgetItem(f"{rdv['patient_nom']} {rdv['patient_prenom']}"))
                    self.table_rdv.setItem(row, 1, QTableWidgetItem(rdv['date']))
                    self.table_rdv.setItem(row, 2, QTableWidgetItem(rdv['heure']))

                    statut_item = QTableWidgetItem(rdv['statut'])
                    if rdv['statut'] == "Confirmé":
                        statut_item.setForeground(QBrush(QColor("#388e3c")))
                    elif rdv['statut'] == "En attente":
                        statut_item.setForeground(QBrush(QColor("#f57c00")))
                    else:
                        statut_item.setForeground(QBrush(QColor("#d32f2f")))

                    self.table_rdv.setItem(row, 3, statut_item)
            else:
                QMessageBox.warning(self, "Erreur", "Erreur lors du chargement des données")

        except Exception as e:
            QMessageBox.critical(self, "Erreur réseau", f"Erreur réseau: {e}")
