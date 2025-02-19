from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox,
    QComboBox, QLabel, QLineEdit, QAbstractItemView
)
from PyQt6.QtCore import Qt
import sqlite3

class EditPaymentDialog(QDialog):
    def __init__(self, parent, payment_id=None):
        super().__init__(parent)
        self.setWindowTitle("تعديل الدفع")
        self.setGeometry(100, 100, 700, 500)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet("""
            background-color: #f2f2f7;
            color: #000000;
        """)

        self.payment_id = payment_id
        self.layout = QVBoxLayout()

        # Table widget
        self.table = QTableWidget()
        self.table.setStyleSheet("""
            background-color: #ffffff;
            color: #000000;
            gridline-color: #ddd;
            font-size: 14px;
            border: none;
            border-radius: 10px;
            alternate-background-color: #e5e5e5;
        """)
        self.table.horizontalHeader().setStyleSheet("""
            background-color: #4CAF50;
            color: white;
            padding: 0px;  /* Reduced padding */
            border: none;
        """)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.layout.addWidget(self.table)

        # Buttons layout
        buttons_layout = QHBoxLayout()
        self.edit_button = QPushButton("تعديل")
        self.delete_button = QPushButton("حذف")
        self.refresh_button = QPushButton("تحديث")
        # Style the buttons to match the theme
        button_style = """
            QPushButton {
                background-color: #0aad5e;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #007aff;
            }
        """
        self.edit_button.setStyleSheet(button_style)
        self.delete_button.setStyleSheet(button_style)
        self.refresh_button.setStyleSheet(button_style)
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addWidget(self.refresh_button)
        self.layout.addLayout(buttons_layout)

        self.setLayout(self.layout)

        # Populate table
        self.populate_table()

        # Connect buttons
        self.edit_button.clicked.connect(self.edit_payment)
        self.delete_button.clicked.connect(self.delete_payment)
        self.refresh_button.clicked.connect(self.populate_table)

    def populate_table(self):
        conn = sqlite3.connect('business.db')
        cursor = conn.cursor()
        if self.payment_id:
            cursor.execute("""
                SELECT payments.id, clients.name, payments.payment_date, payments.payment_day, payments.amount_paid 
                FROM payments
                JOIN clients ON payments.client_id = clients.id
                WHERE payments.id = ?
            """, (self.payment_id,))
        else:
            cursor.execute("""
                SELECT payments.id, clients.name, payments.payment_date, payments.payment_day, payments.amount_paid
                FROM payments
                JOIN clients ON payments.client_id = clients.id
            """)
        payments = cursor.fetchall()
        conn.close()

        self.table.clear()
        self.table.setRowCount(len(payments))
        self.table.setColumnCount(5)  # Including ID column
        self.table.setHorizontalHeaderLabels(["ID", "العميل", "تاريخ الدفع", "يوم الدفع", "المبلغ المدفوع"])

        for i, payment in enumerate(payments):
            for j in range(5):
                if j == 0:
                    self.table.setItem(i, j, QTableWidgetItem(str(payment[j])))  # ID
                else:
                    self.table.setItem(i, j, QTableWidgetItem(str(payment[j])))
        self.table.resizeColumnsToContents()  # Autofit columns
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    def edit_payment(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "تحذير", "لم يتم تحديد دفعة.")
            return

        payment_id = int(selected_items[0].text())
        # Open a new dialog to edit the payment
        dialog = EditPaymentDialogEdit(self, payment_id)
        dialog.exec()

    def delete_payment(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "تحذير", "لم يتم تحديد دفعة.")
            return

        payment_id = int(selected_items[0].text())
        conn = sqlite3.connect('business.db')
        cursor = conn.cursor()
        cursor.execute("SELECT amount_paid, client_id FROM payments WHERE id = ?", (payment_id,))
        payment = cursor.fetchone()
        if not payment:
            QMessageBox.warning(self, "تحذير", "الدفعة غير موجودة.")
            conn.close()
            return

        amount_paid = payment[0]
        client_id = payment[1]
        confirm = QMessageBox.question(self, "تأكيد الحذف", "هل أنت متأكد من حذف الدفعة؟", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            # Update client's paid_amount and owed_amount
            cursor.execute("SELECT paid_amount, owed_amount FROM clients WHERE id = ?", (client_id,))
            client = cursor.fetchone()
            if client:
                old_paid_amount = client[0]
                old_owed_amount = client[1]
                new_paid_amount = old_paid_amount - amount_paid
                new_owed_amount = old_owed_amount + amount_paid
                cursor.execute("UPDATE clients SET paid_amount = ?, owed_amount = ? WHERE id = ?", (new_paid_amount, new_owed_amount, client_id))
            # Delete the payment
            cursor.execute("DELETE FROM payments WHERE id = ?", (payment_id,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "تم الحذف", "تم حذف الدفعة بنجاح.")
            self.populate_table()

class EditPaymentDialogEdit(QDialog):
    def __init__(self, parent, payment_id):
        super().__init__(parent)
        self.setWindowTitle("تعديل الدفعة")
        self.setGeometry(100, 100, 500, 400)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet("""
            background-color: #f2f2f7;
            color: #000000;
        """)

        self.payment_id = payment_id
        self.layout = QVBoxLayout()

        # Form layout with client selection
        form_layout = QVBoxLayout()

        # Client selection
        self.client_label = QLabel("اختر العميل:")
        self.client_combobox = QComboBox()
        self.client_combobox.setStyleSheet("""
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #ccc;
            border-radius: 5px;
        """)
        form_layout.addWidget(self.client_label)
        form_layout.addWidget(self.client_combobox)

        # Other fields
        self.payment_date_input = QLineEdit()
        self.payment_date_label = QLabel("تاريخ الدفع:")
        form_layout.addWidget(self.payment_date_label)
        form_layout.addWidget(self.payment_date_input)

        self.payment_day_input = QLineEdit()
        self.payment_day_label = QLabel("اليوم:")
        form_layout.addWidget(self.payment_day_label)
        form_layout.addWidget(self.payment_day_input)

        self.amount_paid_input = QLineEdit()
        self.amount_paid_label = QLabel("المبلغ المدفوع:")
        form_layout.addWidget(self.amount_paid_label)
        form_layout.addWidget(self.amount_paid_input)

        self.layout.addLayout(form_layout)

        # Buttons
        buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("حفظ")
        self.cancel_button = QPushButton("إلغاء")
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        self.layout.addLayout(buttons_layout)

        self.setLayout(self.layout)

        # Populate fields and clients
        self.populate_clients()
        self.populate_fields()

        # Connect buttons
        self.save_button.clicked.connect(self.save_payment)
        self.cancel_button.clicked.connect(self.close)

    def populate_clients(self):
        conn = sqlite3.connect('business.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM clients")
        clients = cursor.fetchall()
        conn.close()
        for client in clients:
            self.client_combobox.addItem(client[1], client[0])

    def populate_fields(self):
        conn = sqlite3.connect('business.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM payments WHERE id = ?", (self.payment_id,))
        payment = cursor.fetchone()
        conn.close()

        if payment:
            self.client_combobox.setCurrentIndex(self.client_combobox.findData(payment[1]))  # client_id
            self.payment_date_input.setText(payment[2])       # payment_date
            self.payment_day_input.setText(str(payment[3]))  # payment_day (convert to string)
            self.amount_paid_input.setText(str(payment[4]))   # amount_paid

    def save_payment(self):
        client_id = self.client_combobox.currentData()
        old_payment = self.get_old_payment()
        new_payment_amount = float(self.amount_paid_input.text())

        if old_payment:
            old_payment_amount = old_payment[0]
            delta = new_payment_amount - old_payment_amount
        else:
            delta = new_payment_amount

        # Update client's paid_amount and owed_amount
        conn = sqlite3.connect('business.db')
        cursor = conn.cursor()
        cursor.execute("SELECT paid_amount, owed_amount FROM clients WHERE id = ?", (client_id,))
        client = cursor.fetchone()
        if client:
            old_paid_amount = client[0]
            old_owed_amount = client[1]
            new_paid_amount = old_paid_amount + delta
            new_owed_amount = old_owed_amount - delta
            cursor.execute("UPDATE clients SET paid_amount = ?, owed_amount = ? WHERE id = ?", (new_paid_amount, new_owed_amount, client_id))
        # Update the payment
        cursor.execute("""
            UPDATE payments
            SET client_id = ?, payment_date = ?, payment_day = ?, amount_paid = ?
            WHERE id = ?
        """, (client_id, self.payment_date_input.text(), self.payment_day_input.text(), new_payment_amount, self.payment_id))
        conn.commit()
        conn.close()
        QMessageBox.information(self, "نجاح", "تم تعديل الدفعة بنجاح.")
        self.close()
        self.parent().populate_table()

    def get_old_payment(self):
        conn = sqlite3.connect('business.db')
        cursor = conn.cursor()
        cursor.execute("SELECT amount_paid FROM payments WHERE id = ?", (self.payment_id,))
        payment = cursor.fetchone()
        conn.close()
        return payment

    def delete_payment(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "تحذير", "يرجى تحديد دفعة للحذف.")
            return

        payment_id = int(selected_items[0].text())
        conn = sqlite3.connect('business.db')
        cursor = conn.cursor()
        cursor.execute("SELECT amount_paid, client_id FROM payments WHERE id = ?", (payment_id,))
        payment = cursor.fetchone()
        if not payment:
            QMessageBox.warning(self, "تحذير", "الدفعة المحددة غير موجودة.")
            conn.close()
            return

        amount_paid = payment[0]
        client_id = payment[1]
        confirm = QMessageBox.question(self, "تأكيد الحذف", "هل أنت متأكد من أنك تريد حذف هذه الدفعة؟", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            # Update client's paid_amount and owed_amount
            cursor.execute("SELECT paid_amount, owed_amount FROM clients WHERE id = ?", (client_id,))
            client = cursor.fetchone()
            if client:
                old_paid_amount = client[0]
                old_owed_amount = client[1]
                new_paid_amount = old_paid_amount - amount_paid
                new_owed_amount = old_owed_amount + amount_paid
                cursor.execute("UPDATE clients SET paid_amount = ?, owed_amount = ? WHERE id = ?", (new_paid_amount, new_owed_amount, client_id))
            # Delete the payment
            cursor.execute("DELETE FROM payments WHERE id = ?", (payment_id,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "نجاح", "تم حذف الدفعة بنجاح.")
            self.populate_table()

# Example usage
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    dialog = EditPaymentDialog(None)
    dialog.show()
    sys.exit(app.exec())