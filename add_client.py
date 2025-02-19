from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
import sqlite3

class AddClientDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("إضافة عميل جديد")
        self.setGeometry(100, 100, 500, 400)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet("""
            background-color: #f2f2f7;
            color: #000000;
        """)

        self.layout = QVBoxLayout()

        # Client name
        self.name_label = QLabel("اسم العميل:")
        self.name_input = QLineEdit()
        self.name_input.setStyleSheet("""
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #ccc;
            border-radius: 5px;
        """)
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_input)

        # Paid amount
        self.paid_label = QLabel("المبلغ المدفوع:")
        self.paid_input = QLineEdit()
        self.paid_input.setText("0")
        self.paid_input.setStyleSheet("""
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #ccc;
            border-radius: 5px;
        """)
        self.paid_input.textChanged.connect(self.update_total_bill)  # Update total when changed
        self.layout.addWidget(self.paid_label)
        self.layout.addWidget(self.paid_input)

        # Owed amount
        self.owed_label = QLabel("المبلغ المستحق:")
        self.owed_input = QLineEdit()
        self.owed_input.setText("0")
        self.owed_input.setStyleSheet("""
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #ccc;
            border-radius: 5px;
        """)
        self.owed_input.textChanged.connect(self.update_total_bill)  # Update total when changed
        self.layout.addWidget(self.owed_label)
        self.layout.addWidget(self.owed_input)

        # Total bill (Read-only)
        self.total_bill_label = QLabel("إجمالي الفاتورة:")
        self.total_bill_input = QLineEdit()
        self.total_bill_input.setText("0")
        self.total_bill_input.setReadOnly(True)  # Make it read-only since it's auto-calculated
        self.total_bill_input.setStyleSheet("""
            background-color: #e0e0e0;
            color: #000000;
            border: 1px solid #ccc;
            border-radius: 5px;
        """)
        self.layout.addWidget(self.total_bill_label)
        self.layout.addWidget(self.total_bill_input)

        # Save button
        self.save_button = QPushButton("حفظ العميل")
        self.save_button.clicked.connect(self.save_client)
        self.save_button.setStyleSheet("""
            background-color: #0aad5e;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
        """)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

    def update_total_bill(self):
        """Automatically update total bill as sum of Paid Amount and Owed Amount."""
        try:
            paid = float(self.paid_input.text()) if self.paid_input.text() else 0
            owed = float(self.owed_input.text()) if self.owed_input.text() else 0
            self.total_bill_input.setText(f"{paid + owed:.2f}")
        except ValueError:
            self.total_bill_input.setText("0.00")  # Reset if invalid input

    def save_client(self):
        name = self.name_input.text()
        paid = self.paid_input.text()
        owed = self.owed_input.text()
        total_bill = self.total_bill_input.text()

        if not name:
            QMessageBox.warning(self, "خطأ في الإدخال", "يرجى إدخال اسم العميل.")
            return

        try:
            paid = float(paid)
            owed = float(owed)
            total_bill = float(total_bill)
        except ValueError:
            QMessageBox.warning(self, "خطأ في الإدخال", "يرجى إدخال أرقام صحيحة للمبالغ.")
            return

        conn = sqlite3.connect('business.db')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO clients (name, paid_amount, owed_amount, total_bill) 
            VALUES (?, ?, ?, ?)
        """, (name, paid, owed, total_bill))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "نجاح", "تم إضافة العميل بنجاح.")
        self.close()
