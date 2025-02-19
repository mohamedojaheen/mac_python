import sqlite3
import sys

import pandas as pd
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont, QPalette, QColor, QAction
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QMessageBox, QToolBar, QGridLayout
)
from PyQt6.QtWidgets import QFileDialog

import constants, add_order, add_payment, add_client, edit_payment, edit_order,\
    view_clients, financials, client_records


# Function to get resource path (for cross-platform compatibility)
#def resource_path(relative_path):
#    """ Get absolute path to resource, works for dev and for PyInstaller """
#    try:
#        # PyInstaller creates a temp folder and stores path in _MEIPASS
#        base_path = Path(sys._MEIPASS)
#    except AttributeError:
#        base_path = Path(__file__).parent
#    return base_path / relative_path

# Function to apply Excel-like green theme
def apply_excel_theme(app_instance):
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(0, 176, 80))  # Green for top bar
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))    # White
    palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))          # Black
    palette.setColor(QPalette.ColorRole.Button, QColor(0, 176, 80))     # Green
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255)) # White
    palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 176, 80))  # Green
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255)) # White
    app_instance.setPalette(palette)

    app_instance.setStyleSheet("""
        QMainWindow {
            background-color: #f2f2f7;
        }
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
        QLabel {
            font-size: 16px;
            color: #000000;
        }
        QLineEdit {
            font-size: 14px;
            padding: 5px;
            border: 1px solid #ccc;
            border-radius: 5px;
            background-color: #ffffff;
        }
        QComboBox {
            font-size: 14px;
            padding: 5px;
            border: 1px solid #ccc;
            border-radius: 5px;
            background-color: #ffffff;
        }
        QComboBox QAbstractItemView {
            border: 1px solid #ccc;
            background-color: #ffffff;
            selection-background-color: #0aad5e;
            selection-color: #000000;
        }
        QComboBox::drop-down {
            width: 20px;
            border-left-width: 1px;
            border-left-color: #ccc;
            border-left-style: solid;
            border-top-right-radius: 3px;
            border-bottom-right-radius: 3px;
        }
        QComboBox::down-arrow {
            image: url(:/icons/green_arrow.png);
        }
        QTableWidget {
            font-size: 14px;
            border: 1px solid #ccc;
            background-color: #ffffff;
            gridline-color: #ccc;
            selection-background-color: #e0ffe0;
            selection-color: #000000;
        }
        QTableWidget::item:selected {
            background-color: #e0ffe0;
            color: #000000;
        }
        QMessageBox {
            font-size: 14px;
            background-color: #ffffff;
            color: #000000;
        }
    """)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نظام إدارة الأعمال")
        self.setGeometry(100, 100, 1200, 800)
        #self.setWindowIcon(QIcon(str(resource_path('icon.png')))) # Use .png for Windows
        #self.setWindowIcon(QIcon(str(resource_path('icon.icns')))) # Use .icns for macOS
        self.setStyleSheet("background-color: #f2f2f7;")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowMaximizeButtonHint | Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.WindowMinimizeButtonHint)

        # Apply Excel-like theme
        apply_excel_theme(QApplication.instance())

        # Create main layout
        main_layout = QVBoxLayout()

        # Create toolbar
        toolbar = QToolBar("شريط الأدوات الرئيسي")
        toolbar.setMovable(False)
        toolbar.setStyleSheet("background-color: #0aad5e;")
        self.addToolBar(toolbar)

        # Add actions to toolbar
        add_order_action = QAction("إضافة طلب جديد", self)
        add_order_action.triggered.connect(self.add_new_order)
        toolbar.addAction(add_order_action)

        edit_order_action = QAction("تحرير و حذف الطلب", self)
        edit_order_action.triggered.connect(self.edit_delete_order)
        toolbar.addAction(edit_order_action)

        add_client_action = QAction("إضافة عميل جديد", self)
        add_client_action.triggered.connect(self.add_new_client)
        toolbar.addAction(add_client_action)

        edit_view_client_action = QAction("عرض و تحرير العملاء", self)
        edit_view_client_action.triggered.connect(self.edit_view_clients)
        toolbar.addAction(edit_view_client_action)

        add_payment_action = QAction("إضافة دفعة جديدة", self)
        add_payment_action.triggered.connect(self.add_new_payment)
        toolbar.addAction(add_payment_action)

        edit_delete_payment_action = QAction("تحرير و حذف الدفعات", self)
        edit_delete_payment_action.triggered.connect(self.edit_delete_payments)
        toolbar.addAction(edit_delete_payment_action)

        client_records_action = QAction("سجلات العملاء", self)
        client_records_action.triggered.connect(self.client_records)
        toolbar.addAction(client_records_action)

        financials_action = QAction("المالية", self)
        financials_action.triggered.connect(self.financials)
        toolbar.addAction(financials_action)

        export_action = QAction("تصدير إلى إكسل", self)
        export_action.triggered.connect(self.export_to_excel)
        toolbar.addAction(export_action)

        # Create container widget and set layout
        container = QWidget()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        main_layout.addLayout(self.create_button_layout())
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Status bar
        self.statusBar().showMessage("جاهز")

    def export_to_excel(self):
        """Exports the database to an Excel file where each client has their own sheet."""
        file_path, _ = QFileDialog.getSaveFileName(self, "حفظ ملف Excel", "", "Excel Files (*.xlsx);;All Files (*)")

        if not file_path:
            return  # User canceled

        try:
            conn = sqlite3.connect('business.db')
            cursor = conn.cursor()

            # Fetch all clients
            cursor.execute("SELECT * FROM clients")
            clients = cursor.fetchall()

            with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
                if not clients:
                    # ✅ Ensure at least one sheet exists if no clients found
                    df_empty = pd.DataFrame({"ملاحظة": ["لا توجد بيانات متاحة"]})
                    df_empty.to_excel(writer, sheet_name="لا يوجد عملاء", index=False)
                else:
                    for client in clients:
                        client_id, name, paid, owed, total_bill = client

                        # Fetch client's orders
                        cursor.execute("SELECT * FROM orders WHERE client_id = ?", (client_id,))
                        orders = cursor.fetchall()
                        orders_df = pd.DataFrame(orders, columns=[desc[0] for desc in
                                                                  cursor.description]) if orders else pd.DataFrame()

                        # Fetch client's payments
                        cursor.execute("SELECT * FROM payments WHERE client_id = ?", (client_id,))
                        payments = cursor.fetchall()
                        payments_df = pd.DataFrame(payments, columns=[desc[0] for desc in
                                                                      cursor.description]) if payments else pd.DataFrame()

                        # Create a sheet for each client
                        client_sheet_name = f"{name[:25]}"  # Excel sheet names can't exceed 31 characters
                        client_info_df = pd.DataFrame({
                            "اسم العميل": [name],
                            "المبلغ المدفوع": [paid],
                            "المبلغ المستحق": [owed],
                            "إجمالي الفاتورة": [total_bill]
                        })
                        client_info_df.to_excel(writer, sheet_name=client_sheet_name, index=False, startrow=0)

                        # Write Orders
                        if not orders_df.empty:
                            orders_df.to_excel(writer, sheet_name=client_sheet_name, index=False, startrow=3)

                        # Write Payments
                        if not payments_df.empty:
                            payments_df.to_excel(writer, sheet_name=client_sheet_name, index=False,
                                                 startrow=orders_df.shape[0] + 6)

            conn.close()
            QMessageBox.information(self, "نجاح", f"تم تصدير البيانات إلى {file_path} بنجاح.")

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء التصدير: {e}")

    def create_button_layout(self):
        layout = QGridLayout()
        buttons = [
            ("إضافة طلب جديد", self.add_new_order),
            ("تحرير و حذف الطلبات", self.edit_delete_order),
            ("إضافة عميل جديد", self.add_new_client),
            ("عرض و تحرير العملاء", self.edit_view_clients),
            ("إضافة دفعة جديدة", self.add_new_payment),
            ("تحرير و حذف الدفعات", self.edit_delete_payments),
            ("سجلات العملاء", self.client_records),
            ("المالية", self.financials)
        ]

        for i, (text, func) in enumerate(buttons):
            button = QPushButton(text)
            button.clicked.connect(func)
            button.setFont(QFont("Arial", 14))
            button.setFixedSize(200, 50)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #0aad5e;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                }
                QPushButton:hover {
                    background-color: #007aff;
                }
            """)
            layout.addWidget(button, i//4, i%4)
        return layout

    # Button functions
    def add_new_order(self):
        from add_order import AddOrderDialog
        dialog = AddOrderDialog(self)
        dialog.exec()

    def edit_delete_order(self):
        from edit_order import EditOrderDialog
        dialog = EditOrderDialog(self)
        dialog.exec()

    def add_new_client(self):
        from add_client import AddClientDialog
        dialog = AddClientDialog(self)
        dialog.exec()

    def edit_view_clients(self):
        from view_clients import ViewClientsDialog
        dialog = ViewClientsDialog(self)
        dialog.exec()

    def add_new_payment(self):
        from add_payment import AddPaymentDialog
        dialog = AddPaymentDialog(self)
        dialog.exec()

    def edit_delete_payments(self):
        from edit_payment import EditPaymentDialog
        dialog = EditPaymentDialog(self)
        dialog.exec()

    def client_records(self):
        from client_records import ClientRecordsDialog
        dialog = ClientRecordsDialog(self)
        dialog.exec()

    def financials(self):
        from financials import FinancialsDialog
        dialog = FinancialsDialog(self)
        dialog.exec()

def main():
    app = QApplication(sys.argv)
    #icon_path = str(resource_path('icon.png'))  # Use .png for Windows
    #icon_icns_path = str(resource_path('icon.icns'))  # Use .icns for macOS
    #app.setWindowIcon(QIcon(icon_path))
    apply_excel_theme(app)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()