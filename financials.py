from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QHBoxLayout, QComboBox, QLabel,
    QAbstractItemView
)
from PyQt6.QtCore import Qt, QSize
import sqlite3
from datetime import datetime


class FinancialsDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("المالية")
        self.setGeometry(100, 100, 900, 600)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet("""
            background-color: #f2f2f7;
            color: #000000;
        """)

        self.layout = QVBoxLayout()

        # Month selection
        self.filter_layout = QHBoxLayout()
        self.month_label = QLabel("اختر الشهر:")
        self.month_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.month_combobox = QComboBox()
        self.month_combobox.setStyleSheet("""
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #ccc;
            border-radius: 5px;
            padding: 5px;
            font-size: 14px;
        """)
        self.filter_layout.addWidget(self.month_label)
        self.filter_layout.addWidget(self.month_combobox)
        self.layout.addLayout(self.filter_layout)

        # Financials table
        self.financials_label = QLabel("المالية الشهرية")
        self.financials_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 20px;")
        self.layout.addWidget(self.financials_label)
        self.financials_table = QTableWidget()
        self.financials_table.setStyleSheet("""
            background-color: #ffffff;
            color: #000000;
            gridline-color: #ccc;
            font-size: 14px;
            border: none;
            border-radius: 10px;
            alternate-background-color: #e5e5e5;
        """)
        self.financials_table.horizontalHeader().setStyleSheet("""
            background-color: #4CAF50;
            color: white;
            padding: 0px;
            border: none;
        """)
        self.financials_table.verticalHeader().setVisible(False)
        self.financials_table.setAlternatingRowColors(True)
        self.financials_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.financials_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.layout.addWidget(self.financials_table)

        # Buttons
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

        # Populate months
        self.populate_months()

        # Update financials when month is changed
        self.month_combobox.currentIndexChanged.connect(self.update_financials)

        # Connect refresh button
        self.refresh_button.clicked.connect(self.populate_months)

    def populate_months(self):
        # Arabic month names mapped to numbers
        arabic_months = {
            "01": "يناير", "02": "فبراير", "03": "مارس", "04": "أبريل", "05": "مايو", "06": "يونيو",
            "07": "يوليو", "08": "أغسطس", "09": "سبتمبر", "10": "أكتوبر", "11": "نوفمبر", "12": "ديسمبر"
        }

        # Clear the combobox
        self.month_combobox.clear()

        # Add all 12 months to the dropdown
        for month_num, month_name in arabic_months.items():
            self.month_combobox.addItem(month_name, month_num)

        # Set default to the current month
        current_month = datetime.now().strftime("%m")
        current_month_index = list(arabic_months.keys()).index(current_month)
        self.month_combobox.setCurrentIndex(current_month_index)

    def update_financials(self):
        try:
            selected_month_num = self.month_combobox.currentData()
            #if selected_month_num == None :
            #    QMessageBox.warning(self, "خطأ في التحديد", "يرجى اختيار شهر صحيح.")
            #    return

            conn = sqlite3.connect('business.db')
            cursor = conn.cursor()
            cursor.execute("SELECT payment_date, payment_day, amount_paid FROM payments WHERE payment_date IS NOT NULL")
            payments = cursor.fetchall()
            conn.close()

            daily_totals = {}
            for payment in payments:
                payment_date, payment_day, amount_paid = payment
                try:
                    date_obj = datetime.strptime(payment_date, "%d/%m/%Y")
                    if date_obj.strftime("%m") == selected_month_num:
                        if payment_date not in daily_totals:
                            daily_totals[payment_date] = {"day": payment_day, "total": 0}
                        daily_totals[payment_date]["total"] += amount_paid
                except ValueError:
                    continue

            daily_totals_list = sorted(daily_totals.items(), key=lambda x: datetime.strptime(x[0], "%d/%m/%Y"))

            self.financials_table.clear()
            self.financials_table.setRowCount(0)  # Start with an empty table
            self.financials_table.setColumnCount(3)
            self.financials_table.setHorizontalHeaderLabels(["التاريخ", "اليوم", "العائد"])

            row_index = 0
            light_green = QColor(144, 238, 144)  # Light green color

            for date, data in daily_totals_list:
                if data["day"] == "السبت":
                    # Insert an empty row before "السبت" and merge all columns
                    self.financials_table.insertRow(row_index)
                    self.financials_table.setSpan(row_index, 0, 1, 3)  # Merge all three columns
                    empty_item = QTableWidgetItem("")
                    empty_item.setBackground(light_green)
                    self.financials_table.setItem(row_index, 0, empty_item)
                    row_index += 1  # Move to the next row

                # Insert the actual data row
                self.financials_table.insertRow(row_index)
                self.financials_table.setItem(row_index, 0, QTableWidgetItem(date))
                self.financials_table.setItem(row_index, 1, QTableWidgetItem(data["day"]))
                self.financials_table.setItem(row_index, 2, QTableWidgetItem(f"{data['total']:.2f}"))
                row_index += 1

            # Add total row
            grand_total = sum(data["total"] for data in daily_totals.values())
            self.financials_table.insertRow(row_index)
            self.financials_table.setSpan(row_index, 0, 1, 2)  # Merge first two columns
            total_label = QTableWidgetItem("الإجمالي")
            total_label.setBackground(light_green)
            self.financials_table.setItem(row_index, 0, total_label)

            total_amount = QTableWidgetItem(f"{grand_total:.2f}")
            total_amount.setBackground(light_green)
            self.financials_table.setItem(row_index, 2, total_amount)

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ: {e}")
