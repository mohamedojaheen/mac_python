from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
import sqlite3
from datetime import datetime

class AddPaymentDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("إضافة دفعة جديدة")
        self.setGeometry(100, 100, 600, 500)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet("""
            background-color: #f2f2f7;
            color: #000000;
        """)

        self.layout = QVBoxLayout()

        # Client selection
        self.client_label = QLabel("اختر العميل:")
        self.client_combobox = QComboBox()
        self.client_combobox.setStyleSheet("""
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #ccc;
            border-radius: 5px;
        """)
        self.layout.addWidget(self.client_label)
        self.layout.addWidget(self.client_combobox)

        # Client info
        self.client_info = QLabel("")
        self.layout.addWidget(self.client_info)

        # Amount paid
        self.amount_label = QLabel("المبلغ المدفوع:")
        self.amount_input = QLineEdit()
        self.amount_input.setStyleSheet("""
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #ccc;
            border-radius: 5px;
        """)
        self.layout.addWidget(self.amount_label)
        self.layout.addWidget(self.amount_input)

        # Save button
        self.save_button = QPushButton("حفظ الدفعة")
        self.save_button.setStyleSheet("""
            background-color: #0aad5e;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
        """)
        self.save_button.clicked.connect(self.handle_save_payment)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

        # Populate clients
        self.populate_clients()

        # Update client info
        self.client_combobox.currentIndexChanged.connect(self.update_client_info)

    def populate_clients(self):
        conn = sqlite3.connect('business.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM clients")
        clients = cursor.fetchall()
        conn.close()
        for client in clients:
            self.client_combobox.addItem(client[1], client[0])

    def update_client_info(self):
        client_id = self.client_combobox.currentData()
        try:
            conn = sqlite3.connect('business.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name, owed_amount FROM clients WHERE id = ?", (client_id,))
            client = cursor.fetchone()
            conn.close()
            if client:
                self.client_info.setText(f"المبلغ المستحق: {client[1]:.2f}")
            else:
                self.client_info.setText("")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "خطأ في قاعدة البيانات", f"فشل جلب معلومات العميل: {e}")
            self.client_info.setText("")

    def handle_save_payment(self):
        client_id = self.client_combobox.currentData()
        amount_paid = self.amount_input.text()

        arabic_days = {
            "Sunday": "الأحد",
            "Monday": "الاثنين",
            "Tuesday": "الثلاثاء",
            "Wednesday": "الأربعاء",
            "Thursday": "الخميس",
            "Friday": "الجمعة",
            "Saturday": "السبت"
        }

        if not client_id or not amount_paid:
            QMessageBox.warning(self, "خطأ في الإدخال", "يرجى اختيار العميل وإدخال المبلغ المدفوع.")
            return

        try:
            amount_paid = float(amount_paid)
        except ValueError:
            QMessageBox.warning(self, "خطأ في الإدخال", "يرجى إدخال رقم صحيح للمبلغ المدفوع.")
            return

        try:
            conn = sqlite3.connect('business.db')
            cursor = conn.cursor()
            cursor.execute("SELECT owed_amount FROM clients WHERE id = ?", (client_id,))
            owed = cursor.fetchone()[0]
            if amount_paid > owed:
                QMessageBox.warning(self, "خطأ في الإدخال", "لا يمكن أن يتجاوز المبلغ المدفوع المبلغ المستحق.")
                conn.close()
                return

            payment_date_str = datetime.now().strftime("%d/%m/%Y")
            payment_day_str = datetime.now().strftime("%A")
            arabic_day = arabic_days.get(payment_day_str, "")
            cursor.execute("""
                INSERT INTO payments (client_id, payment_date, payment_day, amount_paid) 
                VALUES (?, ?, ?, ?)
            """, (client_id, payment_date_str, arabic_day, amount_paid))
            cursor.execute("UPDATE clients SET paid_amount = paid_amount + ? WHERE id = ?", (amount_paid, client_id))
            cursor.execute("UPDATE clients SET owed_amount = owed_amount - ? WHERE id = ?", (amount_paid, client_id))
            # Ensure owed_amount is not negative
            cursor.execute("""
                UPDATE clients 
                SET owed_amount = CASE 
                                    WHEN owed_amount < 0 THEN 0
                                    ELSE owed_amount
                                  END
                WHERE id = ?
            """, (client_id,))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "نجاح", "الدفعة أضيفت بنجاح.")
            self.close()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "خطأ في قاعدة البيانات", f"فشل إضافة الدفعة: {e}")