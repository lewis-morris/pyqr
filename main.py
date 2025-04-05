import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet

from qr.functions import resource_path
from qr.gui import QRCodeGeneratorApp

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set app icon
    icon_path = resource_path("assets/appico.png")
    app.setWindowIcon(QIcon(icon_path))

    window = QRCodeGeneratorApp()

    extra = {
        # Density Scale
        'density_scale': '-2',
    }

    apply_stylesheet(app, theme='dark_teal.xml', extra=extra)

    placeholder_color_css = """
        QLineEdit, QTextEdit, QPlainTextEdit, QComboBox {
            color: white;
        }
        QLineEdit::placeholder,
        QTextEdit::placeholder,
        QPlainTextEdit::placeholder,
        QComboBox QAbstractItemView {
            color: white;
            background-color: #2e2e2e;
            selection-background-color: #00796b;
            selection-color: white;
        }
        QComboBox QAbstractItemView::item {
            padding: 5px;
        }
        QComboBox:editable {
            color: white;
        }
        QComboBox QLineEdit:placeholder {
            color: #AAAAAA;
        }
    """



    app.setStyleSheet(app.styleSheet() + placeholder_color_css)


    window.show()
    sys.exit(app.exec())