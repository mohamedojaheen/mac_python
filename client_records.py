import logging
import sqlite3
import traceback
from datetime import datetime

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QHBoxLayout, QComboBox, QLabel,
    QAbstractItemView
)

from constants import arabic_days

#from main import resource_path


class ClientRecordsDialog(QDialog):
    def __init__(self, parent):
        try:
            super().__init__(parent)
            self.setWindowTitle("سجلات العملاء")
            self.setGeometry(100, 100, 900, 600)  # Increased size for two tables
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            self.setStyleSheet("""
                background-color: #f2f2f7;
                color: #000000;
            """)

            self.layout = QVBoxLayout()

            # Client selection
            self.client_selection_layout = QHBoxLayout()
            self.client_label = QLabel("اختر العميل:")
            self.client_label.setStyleSheet("font-size: 16px; font-weight: bold;")
            self.client_combobox = QComboBox()
            self.client_combobox.setStyleSheet("""
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            """)
            self.client_selection_layout.addWidget(self.client_label)
            self.client_selection_layout.addWidget(self.client_combobox)
            self.layout.addLayout(self.client_selection_layout)

            # Client info
            self.client_info = QLabel("")
            self.client_info.setStyleSheet("font-size: 14px;")
            self.layout.addWidget(self.client_info)

            # Orders table widget
            self.orders_label = QLabel("الطلبات:")
            self.orders_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 20px;")
            self.layout.addWidget(self.orders_label)
            self.orders_table = QTableWidget()
            self.orders_table.setStyleSheet("""
                background-color: #ffffff;
                color: #000000;
                gridline-color: #ddd;
                font-size: 14px;
                border: none;
                border-radius: 10px;
                alternate-background-color: #e5e5e5;
            """)
            self.orders_table.horizontalHeader().setStyleSheet("""
                background-color: #4CAF50;
                color: white;
                padding: 0px;
                border: none;
            """)
            self.orders_table.verticalHeader().setVisible(False)
            self.orders_table.setAlternatingRowColors(True)
            self.orders_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            self.orders_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            self.layout.addWidget(self.orders_table)

            # Payments table widget
            self.payments_label = QLabel("المدفوعات:")
            self.payments_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 20px;")
            self.layout.addWidget(self.payments_label)
            self.payments_table = QTableWidget()
            self.payments_table.setStyleSheet("""
                background-color: #ffffff;
                color: #000000;
                gridline-color: #ddd;
                font-size: 14px;
                border: none;
                border-radius: 10px;
                alternate-background-color: #e5e5e5;
            """)
            self.payments_table.horizontalHeader().setStyleSheet("""
                background-color: #4CAF50;
                color: white;
                padding: 0px;
                border: none;
            """)
            self.payments_table.verticalHeader().setVisible(False)
            self.payments_table.setAlternatingRowColors(True)
            self.payments_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            self.payments_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            self.layout.addWidget(self.payments_table)

            # Buttons layout
            buttons_layout = QHBoxLayout()
            self.refresh_button = QPushButton("تحديث")
            self.refresh_button.setStyleSheet("""
                background-color: #0aad5e;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
            """)
            #self.refresh_button.setIcon(QIcon(str(resource_path('refresh_icon.png'))))
            #self.refresh_button.setIconSize(QSize(16, 16))
            buttons_layout.addWidget(self.refresh_button)
            self.layout.addLayout(buttons_layout)

            self.setLayout(self.layout)

            # Populate clients
            self.populate_clients()

            # Update client info and tables
            self.client_combobox.currentIndexChanged.connect(self.update_client_info_and_tables)

            # Connect refresh button
            self.refresh_button.clicked.connect(self.populate_records)
        except Exception as e:
            logging.error(f"Error initializing ClientRecordsDialog: {e}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ: {e}")
            self.close()

    def populate_clients(self):
        try:
            conn = sqlite3.connect('business.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM clients")
            clients = cursor.fetchall()
            conn.close()
            for client in clients:
                self.client_combobox.addItem(client[1], client[0])
        except sqlite3.Error as e:
            logging.error(f"Database connection error: {e}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "خطأ", f"خطأ في الاتصال بقاعدة البيانات: {e}")
            self.close()

    def update_client_info_and_tables(self):
        client_id = self.client_combobox.currentData()
        if client_id is None:
            QMessageBox.warning(self, "تحذير", "لم يتم تحديد عميل.")
            return
        try:
            conn = sqlite3.connect('business.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name, paid_amount, owed_amount, total_bill FROM clients WHERE id = ?", (client_id,))
            client = cursor.fetchone()
            conn.close()
            if client:
                self.client_info.setText(f"الاسم: {client[0]}, المدفوع: {client[1]}, المستحق: {client[2]}, إجمالي الفاتورة: {client[3]}")
            else:
                self.client_info.setText("")
        except sqlite3.Error as e:
            logging.error(f"Error fetching client info: {e}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "خطأ", f"خطأ في جلب معلومات العميل: {e}")
            self.client_info.setText("")

        self.populate_orders(client_id)
        self.populate_payments(client_id)

    def populate_orders(self, client_id):
        try:
            conn = sqlite3.connect('business.db')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT orders.id, orders.order_name, orders.order_type, orders.width, orders.length, orders.price_per_cm, orders.total_price, orders.payment_type, orders.order_date, orders.order_day
                FROM orders
                WHERE client_id = ?
            """, (client_id,))
            orders = cursor.fetchall()
            conn.close()

            self.orders_table.clear()
            self.orders_table.setRowCount(len(orders))
            self.orders_table.setColumnCount(9)  # orders.id removed, order_day added
            self.orders_table.setHorizontalHeaderLabels(["اسم الطلب", "نوع الطلب", "العرض (سم)", "الطول (سم)", "السعر لكل سم", "إجمالي السعر", "نوع الدفع", "تاريخ الطلب", "اليوم"])

            for i, order in enumerate(orders):
                for j in range(9):
                    if j == 8:
                        # Format the date and include the Arabic day
                        date_str = order[j+1]
                        try:
                            date_obj = datetime.strptime(date_str, "%d/%m/%Y")
                            arabic_day = arabic_days.get(date_obj.strftime("%A"), "")
                            self.orders_table.setItem(i, j, QTableWidgetItem(f"{date_str} ({arabic_day})"))
                        except ValueError as e:
                            logging.debug(f"Error parsing date {date_str}: {e}")
                            self.orders_table.setItem(i, j, QTableWidgetItem(date_str))
                    else:
                        self.orders_table.setItem(i, j, QTableWidgetItem(str(order[j+1])))
            self.orders_table.resizeColumnsToContents()  # Autofit columns
            self.orders_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        except sqlite3.Error as e:
            logging.error(f"Error populating orders: {e}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "خطأ", f"خطأ في جلب الطلبات: {e}")
            self.orders_table.clear()

    def populate_payments(self, client_id):
        try:
            conn = sqlite3.connect('business.db')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT payments.payment_date, payments.payment_day, payments.amount_paid
                FROM payments
                WHERE client_id = ?
            """, (client_id,))
            payments = cursor.fetchall()
            conn.close()

            self.payments_table.clear()
            self.payments_table.setRowCount(len(payments))
            self.payments_table.setColumnCount(3)  # payment_date, payment_day, amount_paid
            self.payments_table.setHorizontalHeaderLabels(["تاريخ الدفع", "يوم الدفع", "المبلغ المدفوع"])

            for i, payment in enumerate(payments):
                for j in range(3):
                    if j == 0:
                        # Payment date
                        self.payments_table.setItem(i, j, QTableWidgetItem(payment[0]))
                    elif j == 1:
                        # Payment day in Arabic
                        self.payments_table.setItem(i, j, QTableWidgetItem(payment[1]))
                    elif j == 2:
                        # Amount paid
                        self.payments_table.setItem(i, 2, QTableWidgetItem(f"{payment[2]:.2f}"))
            self.payments_table.resizeColumnsToContents()  # Autofit columns
            self.payments_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        except sqlite3.Error as e:
            logging.error(f"Error populating payments: {e}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "خطأ", f"خطأ في جلب المدفوعات: {e}")
            self.payments_table.clear()

    def populate_records(self):
        client_id = self.client_combobox.currentData()
        if client_id is None:
            QMessageBox.warning(self, "تحذير", "لم يتم تحديد عميل.")
            return
        self.update_client_info_and_tables()