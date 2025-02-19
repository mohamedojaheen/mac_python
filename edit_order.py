from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox,
    QLabel, QLineEdit, QAbstractItemView, QComboBox
)
from PyQt6.QtCore import Qt
import sqlite3

class EditOrderDialog(QDialog):
    def __init__(self, parent, order_id=None):
        super().__init__(parent)
        self.setWindowTitle("تعديل الطلب")
        self.setGeometry(100, 100, 900, 600)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet("""
            background-color: #f2f2f7;
            color: #000000;
        """)

        self.order_id = order_id
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
        self.edit_button.clicked.connect(self.edit_order)
        self.delete_button.clicked.connect(self.delete_order)
        self.refresh_button.clicked.connect(self.populate_table)

    def populate_table(self):
        conn = sqlite3.connect('business.db')
        cursor = conn.cursor()
        if self.order_id:
            cursor.execute("""
                SELECT orders.id, orders.order_name, orders.width, orders.length, orders.order_type, clients.name, orders.price_per_cm, orders.total_price, orders.payment_type, orders.order_date, orders.order_day
                FROM orders 
                JOIN clients ON orders.client_id = clients.id 
                WHERE orders.id = ?
            """, (self.order_id,))
        else:
            cursor.execute("""
                SELECT orders.id, orders.order_name, orders.width, orders.length, orders.order_type, clients.name, orders.price_per_cm, orders.total_price, orders.payment_type, orders.order_date, orders.order_day
                FROM orders
                JOIN clients ON orders.client_id = clients.id
            """)
        orders = cursor.fetchall()
        conn.close()

        self.table.clear()
        self.table.setRowCount(len(orders))
        self.table.setColumnCount(11)  # Including ID column
        self.table.setHorizontalHeaderLabels(["ID", "اسم الطلب", "العرض (سم)", "الطول (سم)", " نوع الطلب", "العميل","السعر لكل سم", "السعر الإجمالي", "نوع الدفع", "تاريخ الطلب", "اليوم"])

        for i, order in enumerate(orders):
            for j in range(11):
                if j == 0:
                    self.table.setItem(i, j, QTableWidgetItem(str(order[j])))  # ID
                else:
                    self.table.setItem(i, j, QTableWidgetItem(str(order[j])))
        self.table.resizeColumnsToContents()  # Autofit columns
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    def edit_order(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "تحذير", "لم يتم تحديد طلب.")
            return

        order_id = int(selected_items[0].text())
        # Open a new dialog to edit the order
        dialog = EditOrderDialogEdit(self, order_id)
        dialog.exec()

    def delete_order(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "تحذير", "لم يتم تحديد طلب.")
            return

        order_id = int(selected_items[0].text())
        conn = sqlite3.connect('business.db')
        cursor = conn.cursor()
        cursor.execute("SELECT total_price, client_id FROM orders WHERE id = ?", (order_id,))
        order = cursor.fetchone()
        if not order:
            QMessageBox.warning(self, "تحذير", "الطلب غير موجود.")
            conn.close()
            return

        total_price = order[0]
        client_id = order[1]
        confirm = QMessageBox.question(self, "تأكيد الحذف", "هل أنت متأكد من حذف الطلب؟", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            # Update client's total_bill and owed_amount
            cursor.execute("SELECT total_bill, owed_amount FROM clients WHERE id = ?", (client_id,))
            client = cursor.fetchone()
            if client:
                old_total_bill = client[0]
                old_owed_amount = client[1]
                new_total_bill = old_total_bill - total_price
                new_owed_amount = old_owed_amount - total_price
                cursor.execute("UPDATE clients SET total_bill = ?, owed_amount = ? WHERE id = ?", (new_total_bill, new_owed_amount, client_id))
            # Delete the order
            cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "تم الحذف", "تم حذف الطلب بنجاح.")
            self.populate_table()

class EditOrderDialogEdit(QDialog):
    def __init__(self, parent, order_id):
        super().__init__(parent)
        self.setWindowTitle("تعديل الطلب")
        self.setGeometry(100, 100, 600, 500)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet("""
            background-color: #f2f2f7;
            color: #000000;
        """)

        self.order_id = order_id
        self.layout = QVBoxLayout()

        # Form layout without client selection
        form_layout = QVBoxLayout()

        # Other fields
        self.order_name_input = QLineEdit()
        self.order_name_label = QLabel("اسم الطلب:")
        form_layout.addWidget(self.order_name_label)
        form_layout.addWidget(self.order_name_input)

        self.order_type_input = QLineEdit()
        self.order_type_label = QLabel("نوع الطلب:")
        form_layout.addWidget(self.order_type_label)
        form_layout.addWidget(self.order_type_input)

        self.width_input = QLineEdit()
        self.width_label = QLabel("العرض:")
        form_layout.addWidget(self.width_label)
        form_layout.addWidget(self.width_input)

        self.length_input = QLineEdit()
        self.length_label = QLabel("الطول:")
        form_layout.addWidget(self.length_label)
        form_layout.addWidget(self.length_input)

        self.price_per_cm_input = QLineEdit()
        self.price_per_cm_label = QLabel("السعر لكل سم:")
        form_layout.addWidget(self.price_per_cm_label)
        form_layout.addWidget(self.price_per_cm_input)

        self.total_price_input = QLineEdit()
        self.total_price_label = QLabel("السعر الإجمالي:")
        form_layout.addWidget(self.total_price_label)
        form_layout.addWidget(self.total_price_input)

        self.payment_type_input = QComboBox()
        self.payment_type_label = QLabel("نوع الدفع:")
        self.payment_type_input.addItems(["نقدًا", "تقسيطًا"])
        form_layout.addWidget(self.payment_type_label)
        form_layout.addWidget(self.payment_type_input)

        #self.order_date_input = QLineEdit()
        #self.order_date_label = QLabel("تاريخ الطلب:")
        #form_layout.addWidget(self.order_date_label)
        #form_layout.addWidget(self.order_date_input)

        #self.order_day_input = QLineEdit()
        #self.order_day_label = QLabel("اليوم:")
        #form_layout.addWidget(self.order_day_label)
        #form_layout.addWidget(self.order_day_input)

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
        self.save_button.clicked.connect(self.save_order)
        self.cancel_button.clicked.connect(self.close)

    def populate_fields(self):
        conn = sqlite3.connect('business.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE id = ?", (self.order_id,))
        order = cursor.fetchone()
        conn.close()

        if order:
            self.order_name_input.setText(order[1])  # order_name
            self.order_type_input.setText(order[8])  # order_type
            self.width_input.setText(str(order[3]))       # width
            self.length_input.setText(str(order[4]))      # length
            self.price_per_cm_input.setText(str(order[5]))# price_per_cm
            self.total_price_input.setText(str(order[6])) # total_price
            self.payment_type_input.setCurrentText(order[7])# payment_type
            ##self.order_date_input.setText(order[8])       # order_date
            ##self.order_day_input.setText(str(order[9]))   # order_day

    def save_order(self):
        old_order = self.get_old_order()
        new_total_price = float(self.total_price_input.text())

        if old_order:
            old_total_price = old_order[0]
            delta = new_total_price - old_total_price
        else:
            delta = new_total_price

        # Update client's total_bill and owed_amount
        client_id = self.get_client_id()
        conn = sqlite3.connect('business.db')
        cursor = conn.cursor()
        cursor.execute("SELECT total_bill, owed_amount FROM clients WHERE id = ?", (client_id,))
        client = cursor.fetchone()
        if client:
            old_total_bill = client[0]
            old_owed_amount = client[1]
            new_total_bill = old_total_bill + delta
            new_owed_amount = old_owed_amount + delta
            cursor.execute("UPDATE clients SET total_bill = ?, owed_amount = ? WHERE id = ?", (new_total_bill, new_owed_amount, client_id))
        # Update the order
        cursor.execute("""
            UPDATE orders
            SET order_name = ?, order_type = ?, width = ?, length = ?, price_per_cm = ?, total_price = ?, payment_type = ?
            WHERE id = ?
        """, (self.order_name_input.text(), self.order_type_input.text(),self.width_input.text(), self.length_input.text(), self.price_per_cm_input.text(), new_total_price, self.payment_type_input.currentText(), self.order_id))
        conn.commit()
        conn.close()
        QMessageBox.information(self, "نجاح", "تم تعديل الطلب بنجاح.")
        self.close()
        self.parent().populate_table()

    def get_old_order(self):
        conn = sqlite3.connect('business.db')
        cursor = conn.cursor()
        cursor.execute("SELECT total_price FROM orders WHERE id = ?", (self.order_id,))
        order = cursor.fetchone()
        conn.close()
        return order

    def get_client_id(self):
        conn = sqlite3.connect('business.db')
        cursor = conn.cursor()
        cursor.execute("SELECT client_id FROM orders WHERE id = ?", (self.order_id,))
        client_id = cursor.fetchone()[0]
        conn.close()
        return client_id

    def delete_order(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "تحذير", "يرجى تحديد طلب للحذف.")
            return

        order_id = int(selected_items[0].text())
        conn = sqlite3.connect('business.db')
        cursor = conn.cursor()
        cursor.execute("SELECT total_price, client_id FROM orders WHERE id = ?", (order_id,))
        order = cursor.fetchone()
        if not order:
            QMessageBox.warning(self, "تحذير", "الطلب المحدد غير موجود.")
            conn.close()
            return

        total_price = order[0]
        client_id = order[1]
        confirm = QMessageBox.question(self, "تأكيد الحذف", "هل أنت متأكد من أنك تريد حذف هذا الطلب؟", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            # Update client's total_bill and owed_amount
            cursor.execute("SELECT total_bill, owed_amount FROM clients WHERE id = ?", (client_id,))
            client = cursor.fetchone()
            if client:
                old_total_bill = client[0]
                old_owed_amount = client[1]
                new_total_bill = old_total_bill - total_price
                new_owed_amount = old_owed_amount - total_price
                cursor.execute("UPDATE clients SET total_bill = ?, owed_amount = ? WHERE id = ?", (new_total_bill, new_owed_amount, client_id))
            # Delete the order
            cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "نجاح", "تم حذف الطلب بنجاح.")
            self.populate_table()

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    dialog = EditOrderDialog(None)
    dialog.show()
    sys.exit(app.exec())