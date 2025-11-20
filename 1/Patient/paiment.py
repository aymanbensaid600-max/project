from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QSizePolicy, QLineEdit,
    QAbstractItemView, QGraphicsDropShadowEffect, QSpacerItem, QFileDialog,
    QMessageBox, QApplication, QMenu, QDateEdit, QDialogButtonBox, QDialog
)
from PySide6.QtGui import QFont, QIcon, QColor, QBrush, QLinearGradient, QPainter, QPalette
from PySide6.QtCore import Qt, QDate, QSize, QPoint
import sys
import requests
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import datetime as py_datetime
from Accueil.CustomPopup import CustomPopup
class PatientPaymentPage(QWidget):
    def __init__(self, patient_id="id"):
        super().__init__()
        self.patient_id = patient_id
        self.original_paiements = []  # Stockage des données originales
        self.current_status_filter = "Tous"
        self.current_date_filter = "Toutes"
        self.custom_date_range = (None, None)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Titre de la page
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 10)
        
        title_label = QLabel("Paiements")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setStyleSheet("color: #00796b;")
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        # Ajout du bouton de statut ici
        self.statut_btn = QPushButton("Statut")
        self.statut_btn.setFixedSize(100, 40)
        self.statut_btn.setStyleSheet("""
            QPushButton {
                background-color: #00796b;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a4e;
            }
        """)
        title_layout.addWidget(self.statut_btn)
        
        main_layout.addLayout(title_layout)
        
        # Carte de résumé financier
        summary_frame = QFrame()
        summary_frame.setStyleSheet("""
            background-color: white;
            border-radius: 10px;
            padding: 15px;
        """)
        
        # Ajouter une ombre
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 3)
        summary_frame.setGraphicsEffect(shadow)
        
        summary_layout = QHBoxLayout(summary_frame)
        summary_layout.setContentsMargins(15, 15, 15, 15)
        summary_layout.setSpacing(20)
        self.load_payment_statuses()
        
        # Cartes de statut financier
        status_cards = [
            {"title": "Montant payé", "value": f"{self.statuts['total_paye']} €", "color": "#00796b"},
            {"title": "En Attente", "value": f"{self.statuts['total_non_paye']} €", "color": "#f39c12"},
        ]
        
        for card in status_cards:
            card_frame = QFrame()
            card_frame.setFixedHeight(120)
            card_frame.setStyleSheet(f"""
                background-color: ;
                border-radius: 8px;
                padding: 12px;
            """)
            card_layout = QVBoxLayout(card_frame)
            card_layout.setContentsMargins(0,0, 0, 0)
            
            title = QLabel(card["title"])
            title.setFont(QFont("Segoe UI", 10))
            title.setStyleSheet(f"color: {card['color']};")
            card_layout.addWidget(title)
            
            value = QLabel(card["value"])
            value.setFont(QFont("Segoe UI", 12, QFont.Bold))
            value.setStyleSheet(f"color: {card['color']};")
            card_layout.addWidget(value)
            
            summary_layout.addWidget(card_frame)
        
        main_layout.addWidget(summary_frame)
        
        # Barre de recherche et filtres
        filter_layout = QHBoxLayout()
        filter_layout.setContentsMargins(0, 0, 0, 10)
        
        # Barre de recherche
        search_container = QWidget()
        search_container.setStyleSheet("background-color: white; border-radius: 6px;")
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(10, 5, 10, 5)
        
        search_icon = QLabel()
        search_icon.setPixmap(QIcon("search.png").pixmap(20, 20))
        search_layout.addWidget(search_icon)
        
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Rechercher un paiement...")
        self.search_field.setStyleSheet("""
            QLineEdit {
                background-color: transparent;
                border: none;
                padding: 5px;
                font-size: 14px;
            }
        """)
        self.search_field.textChanged.connect(self.search_payments)
        search_layout.addWidget(self.search_field)
        
        filter_layout.addWidget(search_container)
        
        # Filtres
        filter_layout.addStretch()
        
        # Filtre par statut avec menu déroulant
        self.status_filter_btn = QPushButton("Statut ▼")
        self.status_filter_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #00796b;
                padding: 8px 15px;
                border-radius: 6px;
                border: 1px solid #b0bec5;
            }
            QPushButton:hover {
                background-color: #f0f4f8;
            }
        """)
        # Création du menu déroulant pour les statuts
        self.status_menu = QMenu()
        self.status_menu.addAction("Tous").triggered.connect(lambda: self.apply_status_filter("Tous"))
        self.status_menu.addAction("Payé").triggered.connect(lambda: self.apply_status_filter("Payé"))
        self.status_menu.addAction("En attente").triggered.connect(lambda: self.apply_status_filter("En attente"))
        self.status_filter_btn.clicked.connect(self.show_status_menu)
        filter_layout.addWidget(self.status_filter_btn)
        
        # Filtre par date avec menu déroulant
        self.date_filter_btn = QPushButton("Date ▼")
        self.date_filter_btn.setStyleSheet(self.status_filter_btn.styleSheet())
        # Création du menu déroulant pour les dates
        self.date_menu = QMenu()
        self.date_menu.addAction("Toutes").triggered.connect(lambda: self.apply_date_filter("Toutes"))
        self.date_menu.addAction("Aujourd'hui").triggered.connect(lambda: self.apply_date_filter("Aujourd'hui"))
        self.date_menu.addAction("Cette semaine").triggered.connect(lambda: self.apply_date_filter("Cette semaine"))
        self.date_menu.addAction("Ce mois").triggered.connect(lambda: self.apply_date_filter("Ce mois"))
        self.date_menu.addAction("Personnalisée...").triggered.connect(self.open_custom_date_dialog)
        self.date_filter_btn.clicked.connect(self.show_date_menu)
        filter_layout.addWidget(self.date_filter_btn)
        
        main_layout.addLayout(filter_layout)
        
        # Tableau des paiements avec colonne pour télécharger les factures
        self.payments_table = QTableWidget()
        self.payments_table.setColumnCount(6)
        self.payments_table.setHorizontalHeaderLabels([
            "Date", "Référence", "Service", "Montant", "Statut", "Facture"
        ])
        
        # Configuration du tableau
        self.payments_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.payments_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.payments_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.payments_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.payments_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.payments_table.horizontalHeader().setSectionResizeMode(5,  QHeaderView.Stretch)
        
        self.payments_table.horizontalHeader().setStyleSheet(
            "QHeaderView::section {"
            "   background-color: #00796b;"
            "   color: white;"
            "   padding: 12px;"
            "   font-weight: bold;"
            "   border: none;"
            "}"
        )
        
        self.payments_table.verticalHeader().setVisible(False)
        self.payments_table.setStyleSheet(
            "QTableWidget {"
            "   background-color: white;"
            "   border: 1px solid #e0e0e0;"
            "   border-radius: 8px;"
            "   gridline-color: #e0e0e0;"
            "}"
            "QTableWidget::item {"
            "   padding: 12px;"
            "}"
        )
        self.payments_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.payments_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.payments_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.payments_table.setAlternatingRowColors(True)
        
        main_layout.addWidget(self.payments_table, 1)
        
        # Charger les données
        self.load_demo_data()
    
    def show_status_menu(self):
        """Affiche le menu déroulant pour les statuts"""
        self.status_menu.exec_(self.status_filter_btn.mapToGlobal(
            QPoint(0, self.status_filter_btn.height())
        ))
    
    def show_date_menu(self):
        """Affiche le menu déroulant pour les dates"""
        self.date_menu.exec_(self.date_filter_btn.mapToGlobal(
            QPoint(0, self.date_filter_btn.height())
        ))
    
    def load_demo_data(self):
        try:
            url = "http://127.0.0.1:5000/get_paiements_patient"
            payload = {"id_patient": self.patient_id}
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                self.original_paiements = response.json()
                # Convertir les dates en objets datetime pour le filtrage
                for payment in self.original_paiements:
                    try:
                        payment['date_obj'] = datetime.datetime.strptime(payment['date_paiement'], '%Y-%m-%d').date()
                    except:
                        payment['date_obj'] = datetime.date.today()
                self.update_table_with_filters()
            else:
                QMessageBox.warning(self, "Erreur", "Impossible de récupérer les paiements.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue : {e}")
    
    def update_table(self, payments_list):
        """Met à jour le tableau avec la liste des paiements fournie"""
        self.payments_table.setRowCount(len(payments_list))
        
        for row, payment in enumerate(payments_list):
            # Date
            date_item = QTableWidgetItem(payment["date_paiement"])
            date_item.setTextAlignment(Qt.AlignCenter)
            self.payments_table.setItem(row, 0, date_item)
            
            # Référence
            ref_item = QTableWidgetItem(payment["id_paiement"])
            self.payments_table.setItem(row, 1, ref_item)
            
            # Service
            service_item = QTableWidgetItem(payment["observation"])
            self.payments_table.setItem(row, 2, service_item)
            
            # Montant
            amount_item = QTableWidgetItem(f"{payment['montant']} €")
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.payments_table.setItem(row, 3, amount_item)
            
            # Statut
            status_item = QTableWidgetItem(payment["statut"])
            status_item.setTextAlignment(Qt.AlignCenter)
            
            # Colorisation selon le statut
            if payment["statut"].lower() == "payé":  # Insensible à la casse
                status_item.setForeground(QBrush(QColor("#27ae60")))
            elif payment["statut"].lower() == "en attente":  # Insensible à la casse
                status_item.setForeground(QBrush(QColor("#f39c12")))
            else:
                status_item.setForeground(QBrush(QColor("#e74c3c")))
                
            self.payments_table.setItem(row, 4, status_item)
            
            # Bouton de téléchargement de la facture
            download_btn = QPushButton("Télécharger")
            download_btn.setIcon(QIcon("download.png"))
            download_btn.setIconSize(QSize(16, 16))
            download_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    padding: 6px 10px;
                    border-radius: 4px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:disabled {
                    background-color: #95a5a6;
                }
            """)
            
            # Désactiver le bouton pour les paiements en attente
            if payment["statut"].lower() == "en attente":  # Insensible à la casse
                download_btn.setEnabled(False)
                download_btn.setText("Indisponible")
            else:
                download_btn.setEnabled(True)
                download_btn.setText("Télécharger")
            
            # Stocker les données de paiement dans le bouton
            download_btn.setProperty("payment_data", payment)
            download_btn.clicked.connect(self.download_invoice)
            
            # Créer un widget pour contenir le bouton
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.addWidget(download_btn)
            btn_layout.setAlignment(Qt.AlignCenter)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            
            self.payments_table.setCellWidget(row, 5, btn_widget)
        
        # Ajuster la hauteur des lignes
        for row in range(self.payments_table.rowCount()):
            self.payments_table.setRowHeight(row, 45)
    
    def load_payment_statuses(self):
        try:
            url = "http://127.0.0.1:5000/get_statuts_paiement"
            payload = {"id_patient": self.patient_id}
            response = requests.get(url, json=payload)
            if response.status_code == 200:
                self.statuts = response.json()
            else:
                QMessageBox.warning(self, "Erreur", "Impossible de récupérer les statuts.")
                self.statuts = {"total_paye": 0, "total_non_paye": 0}
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue : {e}")
            self.statuts = {"total_paye": 0, "total_non_paye": 0}
    
    def download_invoice(self):
        button = self.sender()
        payment = button.property("payment_data")
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Enregistrer la facture",
            f"Facture_{payment['id_paiement']}.pdf",
            "Fichiers PDF (*.pdf)"
        )
        
        if file_path:
            try:
                # Création du PDF avec ReportLab
                c = canvas.Canvas(file_path, pagesize=A4)
                width, height = A4
                x_margin = 2 * cm
                y = height - 3 * cm

                # Logo (optionnel - vous pouvez ajouter votre propre logo)
                # logo_path = "logo.png"
                # if os.path.exists(logo_path):
                #     c.drawImage(logo_path, x_margin, y - 2*cm, width=4*cm, preserveAspectRatio=True)

                # En-tête
                c.setFont("Helvetica-Bold", 16)
                c.drawString(x_margin, y, "FACTURE MÉDICALE")
                y -= 1 * cm

                # Ligne de séparation
                c.setLineWidth(1)
                c.line(x_margin, y, width - x_margin, y)
                y -= 1 * cm

                # Infos du patient
                c.setFont("Helvetica", 12)
                c.drawString(x_margin, y, f"Date : {payment['date_paiement']}")
                y -= 0.7 * cm
                c.drawString(x_margin, y, f"Référence : {payment['id_paiement']}")
                y -= 0.7 * cm
                c.drawString(x_margin, y, f"Patient ID : {self.patient_id}")
                y -= 0.7 * cm
                c.drawString(x_margin, y, f"Service : {payment['observation']}")
                y -= 0.7 * cm
                c.drawString(x_margin, y, f"Montant : {payment['montant']} €")
                y -= 0.7 * cm
                c.drawString(x_margin, y, f"Statut : {payment['statut']}")
                y -= 1.5 * cm

                # Détails supplémentaires
                c.setFont("Helvetica-Bold", 12)
                c.drawString(x_margin, y, "Détails :")
                y -= 0.7 * cm
                c.setFont("Helvetica", 12)
                details = [
                    "- Consultation médicale",
                    "- Services associés",
                    "- Frais administratifs"
                ]
                for detail in details:
                    c.drawString(x_margin + 1 * cm, y, detail)
                    y -= 0.6 * cm
                
                y -= 1 * cm

                # Tableau des montants
                c.setFont("Helvetica-Bold", 12)
                c.drawString(x_margin, y, "Récapitulatif :")
                y -= 0.7 * cm
                
                # Ligne de séparation
                c.line(x_margin, y, width - x_margin, y)
                y -= 0.5 * cm
                
                # En-tête du tableau
                c.setFont("Helvetica-Bold", 12)
                c.drawString(x_margin, y, "Description")
                c.drawRightString(width - x_margin, y, "Montant")
                y -= 0.7 * cm
                
                # Ligne de séparation
                c.line(x_margin, y, width - x_margin, y)
                y -= 0.5 * cm
                
                # Contenu du tableau
                c.setFont("Helvetica", 12)
                items = [
                    (payment['observation'], f"{payment['montant']} €"),
                    ("Frais administratifs", "0.00 €")
                ]
                
                for item in items:
                    c.drawString(x_margin, y, item[0])
                    c.drawRightString(width - x_margin, y, item[1])
                    y -= 0.7 * cm
                
                # Ligne de séparation
                c.line(x_margin, y, width - x_margin, y)
                y -= 0.5 * cm
                
                # Total
                c.setFont("Helvetica-Bold", 12)
                c.drawString(x_margin, y, "TOTAL")
                c.drawRightString(width - x_margin, y, f"{payment['montant']} €")
                y -= 1 * cm

                # Coordonnées cabinet
                c.setFont("Helvetica", 10)
                c.drawString(x_margin, y, "Cabinet Médical")
                y -= 0.5 * cm
                c.drawString(x_margin, y, "123 Rue de la Santé, Ville")
                y -= 0.5 * cm
                c.drawString(x_margin, y, "Tél : 01 23 45 67 89")
                y -= 0.5 * cm
                c.drawString(x_margin, y, "contact@cabinetmedical.com")
                y -= 1 * cm
                c.drawString(x_margin, y, "Merci pour votre confiance!")

                # Pied de page
                c.setFont("Helvetica-Oblique", 8)
                c.drawRightString(
                    width - x_margin, 1.5 * cm,
                    f"Généré le {py_datetime.now().strftime('%d/%m/%Y %H:%M')}"
                )

                # Sauvegarde
                c.save()

                self.popup=CustomPopup(popup_type="success",message=f"Téléchargement réussi,Facture {payment['id_paiement']} enregistrée avec succès !")
                self.popup.show_centered(self)
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Erreur",
                    f"Une erreur est survenue : {str(e)}"
                )
    
    def apply_status_filter(self, status):
        """Applique le filtre par statut et met à jour le tableau"""
        self.current_status_filter = status
        self.status_filter_btn.setText(f"Statut: {status} ▼")
        self.update_table_with_filters()
    
    def apply_date_filter(self, date_range):
        """Applique le filtre par date et met à jour le tableau"""
        self.current_date_filter = date_range
        self.custom_date_range = (None, None)  # Réinitialise la plage personnalisée
        self.date_filter_btn.setText(f"Date: {date_range} ▼")
        self.update_table_with_filters()
    
    def open_custom_date_dialog(self):
        """Ouvre une boîte de dialogue pour sélectionner une plage de dates personnalisée"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Sélection de plage de dates")
        layout = QVBoxLayout(dialog)
        
        # Sélecteur de date de début
        start_layout = QHBoxLayout()
        start_layout.addWidget(QLabel("De:"))
        start_date_edit = QDateEdit()
        start_date_edit.setDate(QDate.currentDate().addMonths(-1))
        start_date_edit.setCalendarPopup(True)
        start_layout.addWidget(start_date_edit)
        
        # Sélecteur de date de fin
        end_layout = QHBoxLayout()
        end_layout.addWidget(QLabel("À:"))
        end_date_edit = QDateEdit()
        end_date_edit.setDate(QDate.currentDate())
        end_date_edit.setCalendarPopup(True)
        end_layout.addWidget(end_date_edit)
        
        layout.addLayout(start_layout)
        layout.addLayout(end_layout)
        
        # Boutons OK/Annuler
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.Accepted:
            start_date = start_date_edit.date().toString("yyyy-MM-dd")
            end_date = end_date_edit.date().toString("yyyy-MM-dd")
            self.custom_date_range = (start_date, end_date)
            self.current_date_filter = "Personnalisée"
            self.date_filter_btn.setText(f"Date: Personnalisée ▼")
            self.update_table_with_filters()
    
    def update_table_with_filters(self):
        """Met à jour le tableau avec les filtres appliqués"""
        filtered_data = self.original_paiements.copy()
        
        # Appliquer le filtre par statut (insensible à la casse)
        if self.current_status_filter != "Tous":
            status_filter = self.current_status_filter.lower()
            filtered_data = [p for p in filtered_data 
                            if p["statut"].lower() == status_filter]
        
        # Appliquer le filtre par date
        if self.current_date_filter != "Toutes":
            today = datetime.date.today()
            
            if self.current_date_filter == "Aujourd'hui":
                today_str = today.strftime("%Y-%m-%d")
                filtered_data = [p for p in filtered_data 
                                if p["date_paiement"] == today_str]
            
            elif self.current_date_filter == "Cette semaine":
                start_of_week = today - datetime.timedelta(days=today.weekday())
                end_of_week = start_of_week + datetime.timedelta(days=6)
                
                filtered_data = [p for p in filtered_data 
                                if start_of_week <= p['date_obj'] <= end_of_week]
            
            elif self.current_date_filter == "Ce mois":
                start_of_month = today.replace(day=1)
                end_of_month = start_of_month + datetime.timedelta(days=32)
                end_of_month = end_of_month.replace(day=1) - datetime.timedelta(days=1)
                
                filtered_data = [p for p in filtered_data 
                                if start_of_month <= p['date_obj'] <= end_of_month]
            
            elif self.current_date_filter == "Personnalisée" and self.custom_date_range[0]:
                start_date = datetime.datetime.strptime(self.custom_date_range[0], "%Y-%m-%d").date()
                end_date = datetime.datetime.strptime(self.custom_date_range[1], "%Y-%m-%d").date()
                
                filtered_data = [p for p in filtered_data 
                                if start_date <= p['date_obj'] <= end_date]
        
        # Appliquer la recherche
        search_text = self.search_field.text().lower()
        if search_text:
            filtered_data = [p for p in filtered_data 
                           if (search_text in p["id_paiement"].lower() or 
                               search_text in p["observation"].lower() or
                               search_text in p["date_paiement"].lower() or
                               search_text in p["statut"].lower())]
        
        # Mettre à jour le tableau avec les données filtrées
        self.update_table(filtered_data)
    
    def search_payments(self):
        """Mise à jour du tableau lors de la recherche"""
        self.update_table_with_filters()
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PatientPaymentPage(1)
    window.show()
    sys.exit(app.exec())