import math

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QCheckBox
)
from PyQt6.QtCore import Qt
import sqlite3
from datetime import datetime

class AddOrderDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("إضافة طلب جديد")
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

        # Order name
        self.order_name_label = QLabel("اسم الطلب:")
        self.order_name_input = QLineEdit()
        self.order_name_input.setStyleSheet("""
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #ccc;
            border-radius: 5px;
        """)
        self.layout.addWidget(self.order_name_label)
        self.layout.addWidget(self.order_name_input)

        self.order_type_label = QLabel("نوع الطلب:")
        self.order_type_input = QLineEdit()
        self.order_type_input.setStyleSheet("""
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                """)

        self.layout.addWidget(self.order_type_label)
        self.layout.addWidget(self.order_type_input)

        # Dimensions
        self.dimensions_layout = QHBoxLayout()
        self.width_label = QLabel("العرض (سم):")
        self.width_input = QLineEdit()
        self.width_input.setStyleSheet("""
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #ccc;
            border-radius: 5px;
        """)
        self.length_label = QLabel("الطول (سم):")
        self.length_input = QLineEdit()
        self.length_input.setStyleSheet("""
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #ccc;
            border-radius: 5px;
        """)
        self.dimensions_layout.addWidget(self.width_label)
        self.dimensions_layout.addWidget(self.width_input)
        self.dimensions_layout.addWidget(self.length_label)
        self.dimensions_layout.addWidget(self.length_input)
        self.layout.addLayout(self.dimensions_layout)

        # Price per cm
        self.price_per_cm_label = QLabel("السعر لكل سم:")
        self.price_per_cm_input = QLineEdit()
        self.price_per_cm_input.setStyleSheet("""
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #ccc;
            border-radius: 5px;
        """)
        self.layout.addWidget(self.price_per_cm_label)
        self.layout.addWidget(self.price_per_cm_input)

        # Total price
        self.total_price_label = QLabel("إجمالي السعر:")
        self.total_price_input = QLineEdit()
        self.total_price_input.setReadOnly(True)
        self.total_price_input.setStyleSheet("""
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #ccc;
            border-radius: 5px;
        """)
        self.layout.addWidget(self.total_price_label)
        self.layout.addWidget(self.total_price_input)

        # Payment type
        self.payment_type_label = QLabel("نوع الدفع:")
        self.payment_type_combobox = QComboBox()
        self.payment_type_combobox.addItems(["نقدًا", "تقسيطًا"])
        self.payment_type_combobox.setStyleSheet("""
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #ccc;
            border-radius: 5px;
        """)
        self.layout.addWidget(self.payment_type_label)
        self.layout.addWidget(self.payment_type_combobox)

        # Save button
        self.save_button = QPushButton("حفظ الطلب")
        self.save_button.clicked.connect(self.save_order)
        self.save_button.setStyleSheet("""
            background-color: #0aad5e;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
        """)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

        # Connect inputs to update total price
        self.width_input.textChanged.connect(self.calculate_total_price)
        self.length_input.textChanged.connect(self.calculate_total_price)
        self.price_per_cm_input.textChanged.connect(self.calculate_total_price)

        # Populate clients
        self.populate_clients()

    def populate_clients(self):
        conn = sqlite3.connect('business.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM clients")
        clients = cursor.fetchall()
        conn.close()
        for client in clients:
            self.client_combobox.addItem(client[1], client[0])

    def calculate_total_price(self):
        try:
            width = float(self.width_input.text())
            length = float(self.length_input.text())
            price_per_cm = float(self.price_per_cm_input.text())
            total = math.ceil(width * length * price_per_cm)
            self.total_price_input.setText(f"{total:.2f}")
        except ValueError:
            self.total_price_input.setText("")

    def save_order(self):
        client_id = self.client_combobox.currentData()
        order_name = self.order_name_input.text()
        order_type = self.order_type_input.text()
        width = self.width_input.text()
        length = self.length_input.text()
        price_per_cm = self.price_per_cm_input.text()
        total_price = self.total_price_input.text()
        payment_type = self.payment_type_combobox.currentText()

        arabic_days = {
            "Sunday": "الأحد",
            "Monday": "الاثنين",
            "Tuesday": "الثلاثاء",
            "Wednesday": "الأربعاء",
            "Thursday": "الخميس",
            "Friday": "الجمعة",
            "Saturday": "السبت"
        }

        if not client_id or not order_name or not order_type or not width or not length or not price_per_cm or not total_price:
            QMessageBox.warning(self, "خطأ في الإدخال", "يرجى ملء جميع الحقول.")
            return

        try:
            width = float(width)
            length = float(length)
            price_per_cm = float(price_per_cm)
            total_price = float(total_price)
        except ValueError:
            QMessageBox.warning(self, "خطأ في الإدخال", "يرجى إدخال أرقام صحيحة.")
            return

        conn = sqlite3.connect('business.db')
        cursor = conn.cursor()
        order_date_str = datetime.now().strftime("%d/%m/%Y")
        order_day_str = datetime.now().strftime("%A")
        arabic_day = arabic_days.get(order_day_str, "")
        cursor.execute("""
            INSERT INTO orders (order_name, client_id, width, length, price_per_cm, total_price, payment_type, order_type, order_date, order_day)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (order_name, client_id, width, length, price_per_cm, total_price, payment_type, order_type, order_date_str, arabic_day))
        # Update total bill
        cursor.execute("UPDATE clients SET total_bill = total_bill + ? WHERE id = ?", (total_price, client_id))
        # For cash orders, insert a payment record
        if payment_type == "نقدًا":
            cursor.execute("""
                INSERT INTO payments (client_id, payment_date, payment_day, amount_paid) 
                VALUES (?, ?, ?, ?)
            """, (client_id, order_date_str, arabic_day, total_price))
            # Update paid_amount without changing owed_amount
            cursor.execute("""
                UPDATE clients 
                SET paid_amount = paid_amount + ?
                WHERE id = ?
            """, (total_price, client_id))
        else:
            # For installment, update owed_amount
            cursor.execute("""
                UPDATE clients 
                SET owed_amount = owed_amount + ?
                WHERE id = ?
            """, (total_price, client_id))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "نجاح", "تم إضافة الطلب بنجاح.")
        self.close()