from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QCalendarWidget,
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import QDate
import sys
import requests

# Créneaux de 08h00 à 18h30 par 30 minutes
HEURES_TRAVAIL = [f"{h:02d}:{m:02d}" for h in range(8, 19) for m in (0, 30)]

class CalendrierRendezVous(QWidget):
    def __init__(self, id_medecin):
        super().__init__()
        self.id_medecin = id_medecin

        self.setWindowTitle("Agenda Médical")
        self.setMinimumSize(750, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f4f8;
                font-family: 'Segoe UI';
            }
            QLabel {
                color: #37474f;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        self.label = QLabel("Calendrie des rendez-vous")
        self.label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        layout.addWidget(self.label)

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendar.clicked.connect(self.afficher_rdv_du_jour)
        self.styliser_calendrier()
        layout.addWidget(self.calendar)

        self.table_rdv = QTableWidget()
        self.table_rdv.setColumnCount(2)
        self.table_rdv.setHorizontalHeaderLabels(["Heure", "Rendez-vous"])
        self.table_rdv.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_rdv.verticalHeader().setVisible(False)
        self.table_rdv.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #e0f2f1;
                border-radius: 12px;
                font-size: 12pt;
            }
            QTableWidget::item {
                padding: 10px;
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
        layout.addWidget(self.table_rdv)

        self.rendezvous = {}
        self.afficher_rdv_du_jour(self.calendar.selectedDate())

    def styliser_calendrier(self):
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: white;
                border: 2px solid #80deea;
                border-radius: 15px;
                font-size: 12pt;
            }
            QCalendarWidget QToolButton {
                color: #00695c;
                font-weight: bold;
                font-size: 16px;
                background-color: transparent;
            }
            QCalendarWidget QAbstractItemView:enabled {
                font-size: 12px;
                background-color: white;
                color: #37474f;
                selection-background-color: #b2dfdb;
                selection-color: black;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #e0f2f1;
                border: none;
                border-radius: 12px;
            }
        """)

    def afficher_rdv_du_jour(self, date: QDate):
        date_str = date.toString("yyyy-MM-dd")

        try:
            response = requests.post(
                'http://127.0.0.1:5000/pla',
                json={"id_medecin": self.id_medecin}
            )
            response.raise_for_status()
            self.rendezvous = response.json()
        except Exception as e:
            QMessageBox.critical(self, "Erreur réseau", f"Impossible de récupérer les rendez-vous:\n{e}")
            self.rendezvous = {}

        rdvs_du_jour = self.rendezvous.get(date_str, {})

        self.table_rdv.setRowCount(len(HEURES_TRAVAIL))

        for row, heure in enumerate(HEURES_TRAVAIL):
            self.table_rdv.setItem(row, 0, QTableWidgetItem(heure))
            texte = rdvs_du_jour.get(heure, "Libre")
            item = QTableWidgetItem(texte)
            if texte != "Libre":
                item.setForeground(QColor("#004d40"))
                item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            else:
                item.setForeground(QColor("#90a4ae"))
            self.table_rdv.setItem(row, 1, item)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CalendrierRendezVous(id_medecin=2)  # change id_medecin si besoin
    window.show()
    sys.exit(app.exec())
