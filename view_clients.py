from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QHBoxLayout, QComboBox, QLabel, QLineEdit
)
from PyQt6.QtCore import Qt
import sqlite3

class ViewClientsDialog(QDialog):
    def __init__(self, parent, client_id=None):
        super().__init__(parent)
        self.setWindowTitle("العملاء")
        self.setGeometry(100, 100, 700, 600)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet("""
            background-color: #f2f2f7;
            color: #000000;
        """)

        self.client_id = client_id
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
        # Style the buttons to match main.py
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
        self.edit_button.clicked.connect(self.edit_client)
        self.delete_button.clicked.connect(self.delete_client)
        self.refresh_button.clicked.connect(self.populate_table)

    def populate_table(self):
        conn = sqlite3.connect('business.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, paid_amount, owed_amount, total_bill FROM clients")
        clients = cursor.fetchall()
        conn.close()

        self.table.clear()
        self.table.setRowCount(len(clients))
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "الاسم", "المدفوع", "المستحق", "إجمالي الفاتورة"])

        for i, client in enumerate(clients):
            for j in range(5):
                if j == 0:
                    self.table.setItem(i, j, QTableWidgetItem(str(client[j])))  # ID
                else:
                    self.table.setItem(i, j, QTableWidgetItem(str(client[j])))
        self.table.resizeColumnsToContents()  # Autofit columns
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def edit_client(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "تحذير", "لم يتم تحديد عميل.")
            return

        client_id = int(selected_items[0].text())
        # Open a new dialog to edit the client
        dialog = EditClientDialog(self, client_id)
        dialog.exec()

    def delete_client(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "تحذير", "لم يتم تحديد عميل.")
            return

        client_id = int(selected_items[0].text())
        confirm = QMessageBox.question(self, "تأكيد الحذف", "هل أنت متأكد من حذف العميل؟", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            conn = sqlite3.connect('business.db')
            cursor = conn.cursor()
            # Check if the client has related orders or payments
            cursor.execute("SELECT COUNT(*) FROM orders WHERE client_id = ?", (client_id,))
            order_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM payments WHERE client_id = ?", (client_id,))
            payment_count = cursor.fetchone()[0]
            if order_count > 0 or payment_count > 0:
                QMessageBox.warning(self, "تحذير", "لا يمكن حذف العميل بسبب وجود طلبات أو مدفوعات مرتبطة به.")
                conn.close()
                return
            # Delete the client
            cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "تم الحذف", "تم حذف العميل بنجاح.")
            self.populate_table()



class EditClientDialog(QDialog):
    def __init__(self, parent, client_id):
        super().__init__(parent)
        self.setWindowTitle("تعديل العميل")
        self.setGeometry(100, 100, 400, 300)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet("""
            background-color: #f2f2f7;
            color: #000000;
        """)

        self.client_id = client_id
        self.layout = QVBoxLayout()

        # Form layout
        form_layout = QVBoxLayout()

        # Example fields
        self.name_input = QLineEdit()
        self.name_label = QLabel("اسم العميل:")
        form_layout.addWidget(self.name_label)
        form_layout.addWidget(self.name_input)

        self.paid_amount_input = QLineEdit()
        self.paid_amount_label = QLabel("المدفوع:")
        form_layout.addWidget(self.paid_amount_label)
        form_layout.addWidget(self.paid_amount_input)

        self.owed_amount_input = QLineEdit()
        self.owed_amount_label = QLabel("المستحق:")
        form_layout.addWidget(self.owed_amount_label)
        form_layout.addWidget(self.owed_amount_input)

        self.total_bill_input = QLineEdit()
        self.total_bill_label = QLabel("إجمالي الفاتورة:")
        form_layout.addWidget(self.total_bill_label)
        form_layout.addWidget(self.total_bill_input)

        self.layout.addLayout(form_layout)

        # Buttons
        buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("حفظ")
        self.cancel_button = QPushButton("إلغاء")
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        self.layout.addLayout(buttons_layout)

        self.setLayout(self.layout)

        # Populate fields
        self.populate_fields()

        # Connect buttons
        self.save_button.clicked.connect(self.save_client)
        self.cancel_button.clicked.connect(self.close)

    def populate_fields(self):
        conn = sqlite3.connect('business.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients WHERE id = ?", (self.client_id,))
        client = cursor.fetchone()
        conn.close()

        if client:
            self.name_input.setText(client[1])
            self.paid_amount_input.setText(str(client[2]))
            self.owed_amount_input.setText(str(client[3]))
            self.total_bill_input.setText(str(client[4]))

    def save_client(self):
        name = self.name_input.text()
        paid_amount = self.paid_amount_input.text()
        owed_amount = self.owed_amount_input.text()
        total_bill = self.total_bill_input.text()

        # Validation
        if not name or not paid_amount or not owed_amount or not total_bill:
            QMessageBox.warning(self, "تحذير", "يرجى ملء جميع الحقول.")
            return

        try:
            paid_amount = float(paid_amount)
            owed_amount = float(owed_amount)
            total_bill = float(total_bill)
        except ValueError:
            QMessageBox.warning(self, "تحذير", "البيانات المدخلة غير صحيحة.")
            return

        conn = sqlite3.connect('business.db')
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE clients
            SET name = ?, paid_amount = ?, owed_amount = ?, total_bill = ?
            WHERE id = ?
        """, (name, paid_amount, owed_amount, total_bill, self.client_id))
        conn.commit()
        conn.close()
        QMessageBox.information(self, "نجاح", "تم تعديل العميل بنجاح.")
        self.close()
        self.parent().populate_table()

# Example usage
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    dialog = ViewClientsDialog(None)
    dialog.show()
    sys.exit(app.exec())