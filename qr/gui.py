import urllib.parse
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QMainWindow

from qr.functions import resource_path
# Import your QR code generation functions from make_qr.py
from qr.qr_functions import generate_qr, add_logo_to_qr, add_whitespace_with_text


class QRCodeGeneratorApp(QMainWindow):
    """
    QRCodeGeneratorApp is a QMainWindow-based application for generating QR codes with various customization options.

    Attributes:
        current_qr_image (PIL.Image.Image): The current QR code image.
        custom_footer_font (str): Path to the custom font for the footer text.
        footer_font_color (str): Color of the footer font.
        selected_color (str): Color of the QR code.
        type_group (QButtonGroup): Group of radio buttons for selecting QR code type.
        data_input (QLineEdit): Input field for the main data.
        extra_fields_container (QVBoxLayout): Layout for additional input fields based on QR type.
        email_subject_input (QLineEdit): Input field for email subject.
        email_body_input (QLineEdit): Input field for email body.
        sms_message_input (QLineEdit): Input field for SMS message.
        whatsapp_message_input (QLineEdit): Input field for WhatsApp message.
        error_combo (QComboBox): Combo box for selecting error correction level.
        border_slider (QSlider): Slider for adjusting border width.
        color_button (QPushButton): Button for picking QR code color.
        logo_checkbox (QCheckBox): Checkbox for adding a logo to the QR code.
        logo_path_input (QLineEdit): Input field for logo file path.
        logo_browse_button (QPushButton): Button for browsing logo file.
        footer_checkbox (QCheckBox): Checkbox for adding a footer to the QR code.
        footer_text_input (QLineEdit): Input field for footer text.
        whitespace_slider (QSlider): Slider for adjusting whitespace percentage.
        font_button (QPushButton): Button for choosing footer font.
        font_color_button (QPushButton): Button for picking footer font color.
        preview_label (QLabel): Label for displaying QR code preview.
        export_png_btn (QPushButton): Button for exporting QR code as PNG.
        export_jpg_btn (QPushButton): Button for exporting QR code as JPG.
        export_webp_btn (QPushButton): Button for exporting QR code as WEBP.
        export_pdf_btn (QPushButton): Button for exporting QR code as PDF.
    """

    def __init__(self):
        """
        Initializes the QRCodeGeneratorApp, setting up the UI components and connecting signals.
        """
        super().__init__()
        self.setWindowTitle("QR Code Generator")
        icon_path = resource_path("assets/appico.png")
        self.setWindowIcon(QtGui.QIcon(icon_path))
        self.resize(800, 600)
        self.current_qr_image = None
        self.custom_footer_font = None
        self.footer_font_color = None

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QtWidgets.QVBoxLayout(central_widget)

        # SECTION: QR Type
        self.add_section_title("QR Type")
        self.type_group = QtWidgets.QButtonGroup(self)
        type_layout = QtWidgets.QHBoxLayout()
        self.radio_url = QtWidgets.QRadioButton("URL")
        self.radio_email = QtWidgets.QRadioButton("Email")
        self.radio_sms = QtWidgets.QRadioButton("SMS")
        self.radio_whatsapp = QtWidgets.QRadioButton("WhatsApp")
        self.radio_url.setChecked(True)
        for btn in [self.radio_url, self.radio_email, self.radio_sms, self.radio_whatsapp]:
            self.type_group.addButton(btn)
            type_layout.addWidget(btn)
            btn.toggled.connect(self.update_placeholder)
            btn.toggled.connect(self.update_qr)
        self.main_layout.addLayout(type_layout)

        self.data_input = QtWidgets.QLineEdit()
        self.data_input.setPlaceholderText("Enter URL")
        self.data_input.textChanged.connect(self.update_qr)
        self.main_layout.addWidget(self.data_input)

        self.extra_fields_container = QtWidgets.QVBoxLayout()
        self.extra_fields_container.setSpacing(4)
        self.extra_fields_container.setContentsMargins(0, 0, 0, 0)
        self.extra_fields_widget = QtWidgets.QWidget()
        self.extra_fields_widget.setLayout(self.extra_fields_container)
        self.extra_fields_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.main_layout.addWidget(self.extra_fields_widget)

        # Email extras
        self.email_subject_input = QtWidgets.QLineEdit()
        self.email_subject_input.setPlaceholderText("Subject")
        self.email_subject_input.textChanged.connect(self.update_qr)

        self.email_body_input = QtWidgets.QLineEdit()
        self.email_body_input.setPlaceholderText("Body")
        self.email_body_input.textChanged.connect(self.update_qr)

        # SMS extras
        self.sms_message_input = QtWidgets.QLineEdit()
        self.sms_message_input.setPlaceholderText("Message")
        self.sms_message_input.textChanged.connect(self.update_qr)

        # WhatsApp extras
        self.whatsapp_message_input = QtWidgets.QLineEdit()
        self.whatsapp_message_input.setPlaceholderText("Message")
        self.whatsapp_message_input.textChanged.connect(self.update_qr)

        # SECTION: QR Settings
        self.add_section_title("QR Settings")
        error_layout = QtWidgets.QHBoxLayout()
        self.error_combo = QtWidgets.QComboBox()
        self.error_combo.addItems([
            "Low (L) - 7%",
            "Medium (M) - 15%",
            "Quartile (Q) - 25%",
            "High (H) - 30%"
        ])
        self.error_combo.setCurrentIndex(0)
        self.error_combo.currentIndexChanged.connect(self.update_qr)
        error_layout.addWidget(QtWidgets.QLabel("Error Correction Level:"))
        error_layout.addWidget(self.error_combo)
        self.main_layout.addLayout(error_layout)

        border_layout = QtWidgets.QHBoxLayout()
        self.border_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.border_slider.setRange(0, 100)
        self.border_slider.setValue(25)
        self.border_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.border_slider.setTickInterval(5)
        self.border_slider.valueChanged.connect(self.update_qr)
        border_layout.addWidget(QtWidgets.QLabel("Border Width:"))
        border_layout.addWidget(self.border_slider)
        self.main_layout.addLayout(border_layout)

        color_layout = QtWidgets.QHBoxLayout()
        self.color_button = QtWidgets.QPushButton("Pick Color")
        self.color_button.clicked.connect(self.pick_color)
        self.selected_color = "#000000"
        color_layout.addWidget(QtWidgets.QLabel("QR Code Color:"))
        color_layout.addWidget(self.color_button)
        self.main_layout.addLayout(color_layout)

        # SECTION: QR Extras
        self.add_section_title("QR Extras")

        self.logo_checkbox = QtWidgets.QCheckBox("Add Logo")
        self.logo_checkbox.toggled.connect(self.toggle_logo)
        self.logo_checkbox.toggled.connect(self.update_qr)

        self.logo_widget = QtWidgets.QWidget()
        logo_layout = QtWidgets.QHBoxLayout(self.logo_widget)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(6)
        self.logo_path_input = QtWidgets.QLineEdit()
        self.logo_path_input.setPlaceholderText("Select logo file")
        self.logo_path_input.textChanged.connect(self.update_qr)
        self.logo_browse_button = QtWidgets.QPushButton("Browse")
        self.logo_browse_button.clicked.connect(self.browse_logo)
        logo_layout.addWidget(self.logo_path_input)
        logo_layout.addWidget(self.logo_browse_button)
        self.logo_widget.setVisible(False)

        # Wrap logo checkbox and widget in a single group
        logo_section = QtWidgets.QWidget()
        logo_section_layout = QtWidgets.QVBoxLayout(logo_section)
        logo_section_layout.setContentsMargins(0, 0, 0, 0)
        logo_section_layout.setSpacing(2)
        logo_section_layout.addWidget(self.logo_checkbox)
        logo_section_layout.addWidget(self.logo_widget)
        self.main_layout.addWidget(logo_section)


        # --- Footer Section ---
        self.footer_checkbox = QtWidgets.QCheckBox("Add Footer")
        self.footer_checkbox.toggled.connect(self.toggle_footer)
        self.footer_checkbox.toggled.connect(self.update_qr)

        self.footer_widget = QtWidgets.QWidget()
        footer_layout = QtWidgets.QVBoxLayout(self.footer_widget)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setSpacing(6)
        self.footer_text_input = QtWidgets.QLineEdit()
        self.footer_text_input.setPlaceholderText("Footer text")
        self.footer_text_input.textChanged.connect(self.update_qr)

        self.whitespace_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.whitespace_slider.setRange(0, 100)
        self.whitespace_slider.setValue(20)
        self.whitespace_slider.valueChanged.connect(self.update_qr)

        font_layout = QtWidgets.QHBoxLayout()
        self.font_button = QtWidgets.QPushButton("Choose Font")
        self.font_button.clicked.connect(self.choose_footer_font)
        font_layout.addWidget(QtWidgets.QLabel("Footer Font:"))
        font_layout.addWidget(self.font_button)

        font_color_layout = QtWidgets.QHBoxLayout()
        self.font_color_button = QtWidgets.QPushButton("Pick Font Color")
        self.font_color_button.clicked.connect(self.pick_footer_font_color)
        font_color_layout.addWidget(QtWidgets.QLabel("Footer Font Color:"))
        font_color_layout.addWidget(self.font_color_button)

        footer_layout.addWidget(self.footer_text_input)
        footer_layout.addWidget(QtWidgets.QLabel("Whitespace (%)"))
        footer_layout.addWidget(self.whitespace_slider)
        footer_layout.addLayout(font_layout)
        footer_layout.addLayout(font_color_layout)
        self.footer_widget.setVisible(False)

        # Wrap footer checkbox and widget in a single group
        footer_section = QtWidgets.QWidget()
        footer_section_layout = QtWidgets.QVBoxLayout(footer_section)
        footer_section_layout.setContentsMargins(0, 0, 0, 0)
        footer_section_layout.setSpacing(2)
        footer_section_layout.addWidget(self.footer_checkbox)
        footer_section_layout.addWidget(self.footer_widget)
        self.main_layout.addWidget(footer_section)
        # SECTION: QR Preview
        self.add_section_title("QR Preview")
        self.preview_label = QtWidgets.QLabel()
        self.preview_label.setAlignment(QtCore.Qt.AlignCenter)
        self.preview_label.setMinimumSize(250, 250)
        self.preview_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        self.main_layout.addWidget(self.preview_label, alignment=QtCore.Qt.AlignCenter)


        # SECTION: QR Export
        self.add_section_title("QR Export")
        export_layout = QtWidgets.QHBoxLayout()
        self.export_png_btn = QtWidgets.QPushButton("Export as PNG")
        self.export_jpg_btn = QtWidgets.QPushButton("Export as JPG")
        self.export_webp_btn = QtWidgets.QPushButton("Export as WEBP")
        self.export_pdf_btn = QtWidgets.QPushButton("Export as PDF")
        self.export_png_btn.clicked.connect(lambda: self.export_qr("PNG"))
        self.export_jpg_btn.clicked.connect(lambda: self.export_qr("JPG"))
        self.export_webp_btn.clicked.connect(lambda: self.export_qr("WEBP"))
        self.export_pdf_btn.clicked.connect(lambda: self.export_qr("PDF"))
        export_layout.addWidget(self.export_png_btn)
        export_layout.addWidget(self.export_jpg_btn)
        export_layout.addWidget(self.export_webp_btn)
        export_layout.addWidget(self.export_pdf_btn)
        self.main_layout.addLayout(export_layout)

        # Final update
        self.update_qr()

    def update_placeholder(self):
        """Updates the placeholder text and extra fields based on the selected QR code type.

        This method clears the current extra fields and sets the placeholder text for the main
        data input field according to the selected QR code type (URL, Email, SMS, or WhatsApp).
        It also adds the appropriate extra input fields for Email, SMS, and WhatsApp types.

        Raises:
            None
        """
        # Clear current extra fields
        while self.extra_fields_container.count():
            child = self.extra_fields_container.takeAt(0)
            if child.widget():
                child.widget().setParent(None)

        if self.radio_url.isChecked():
            self.data_input.setPlaceholderText("Enter URL")
        elif self.radio_email.isChecked():
            self.data_input.setPlaceholderText("Enter Email Address")
            self.extra_fields_container.addWidget(QtWidgets.QLabel("Subject:"))
            self.extra_fields_container.addWidget(self.email_subject_input)
            self.extra_fields_container.addWidget(QtWidgets.QLabel("Body:"))
            self.extra_fields_container.addWidget(self.email_body_input)
        elif self.radio_sms.isChecked():
            self.data_input.setPlaceholderText("Enter Phone Number")
            self.extra_fields_container.addWidget(QtWidgets.QLabel("Message:"))
            self.extra_fields_container.addWidget(self.sms_message_input)
        elif self.radio_whatsapp.isChecked():
            self.data_input.setPlaceholderText("Enter WhatsApp Number")
            self.extra_fields_container.addWidget(QtWidgets.QLabel("Message:"))
            self.extra_fields_container.addWidget(self.whatsapp_message_input)

        # Resize to fit new content
        self.extra_fields_widget.adjustSize()
        self.repack_layout()

    def add_section_title(self, title):
        """
        Adds a section title to the main layout with a bold label and a horizontal line.

        Args:
            title (str): The title text to be displayed.

        Returns:
            None
        """
        label = QtWidgets.QLabel(title)
        label.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 12px;")
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.main_layout.addWidget(label)
        self.main_layout.addWidget(line)

    def pick_color(self):
        """
        Opens a color dialog to select a color for the QR code.
        The selected color is stored in the `selected_color` attribute and the QR code is updated.
        Returns:
            None

        """
        color = QtWidgets.QColorDialog.getColor(QtGui.QColor(self.selected_color), self, "Select QR Code Color")
        if color.isValid():
            self.selected_color = color.name()
            self.update_qr()

    def choose_footer_font(self):
        """
        Opens a file dialog to select a custom font for the footer text.
        Returns:
            None
        """
        from pathlib import Path
        from qr.qr_functions import find_font_path  # Import it from your own file

        # Get font folder from the first valid font path
        default_font_path = find_font_path()
        if default_font_path:
            default_font_dir = str(Path(default_font_path).parent)
        else:
            default_font_dir = "."

        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select Font File",
            default_font_dir,  # ← open in font folder
            "Font Files (*.ttf *.otf)"
        )

        if file_path:
            self.custom_footer_font = file_path
            self.update_qr()

    def pick_footer_font_color(self):
        """
        Opens a color dialog to select a color for the footer font.

        Returns:
            None
        """
        # Default to QR color if not set
        initial = QtGui.QColor(self.selected_color) if not self.footer_font_color else QtGui.QColor(self.footer_font_color)
        color = QtWidgets.QColorDialog.getColor(initial, self, "Select Footer Font Color")
        if color.isValid():
            self.footer_font_color = color.name()
            self.update_qr()

    def toggle_logo(self, checked):
        self.logo_widget.setVisible(checked)
        self.repack_layout()

    def toggle_footer(self, checked):
        self.footer_widget.setVisible(checked)
        self.repack_layout()

    def repack_layout(self):
        # Update size hints and geometry for all major widgets.
        QtCore.QTimer.singleShot(10, self._repack)

    def _repack(self):
        """Repack the layout by adjusting the size and geometry of key widgets.

        This method iterates over the main widgets in the layout, adjusts their sizes,
        updates their geometries, and triggers a full layout recalculation to ensure
        that the UI is properly updated.

        Widgets:
            - self.logo_widget: The widget containing the logo.
            - self.footer_widget: The widget containing the footer.
            - self.extra_fields_widget: The widget containing extra fields.
            - self.centralWidget(): The central widget of the main window.

        Actions:
            - Adjusts the size of each widget.
            - Updates the geometry of each widget.
            - Invalidates and activates the main layout.
            - Adjusts the size of the main window.
        """
        for widget in [
            self.logo_widget,
            self.footer_widget,
            self.extra_fields_widget,
            self.centralWidget()
        ]:
            widget.adjustSize()
            widget.updateGeometry()

        # Trigger full layout recalculation
        self.main_layout.invalidate()
        self.main_layout.activate()
        self.adjustSize()

    def browse_logo(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Logo", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_path:
            self.logo_path_input.setText(file_path)

    def export_qr(self, fmt):
        """
        Exports the current QR code image to a file in the specified format.
        Args:
            fmt (str): The format to export the QR code image (e.g., "PNG", "JPG", "WEBP", "PDF").

        Returns:
            None

        """
        if self.current_qr_image is None:
            return
        options = QtWidgets.QFileDialog.Options()
        file_filter = ""
        ext = ""
        if fmt.upper() == "PNG":
            file_filter = "PNG Files (*.png)"
            ext = ".png"
        elif fmt.upper() == "JPG":
            file_filter = "JPG Files (*.jpg *.jpeg)"
            ext = ".jpg"
        elif fmt.upper() == "WEBP":
            file_filter = "WEBP Files (*.webp)"
            ext = ".webp"
        elif fmt.upper() == "PDF":
            file_filter = "PDF Files (*.pdf)"
            ext = ".pdf"
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, f"Export QR Code as {fmt}", "", file_filter, options=options)
        if file_path:
            if not file_path.lower().endswith(ext):
                file_path += ext
            if fmt.upper() == "PDF":
                self.current_qr_image.convert("RGB").save(file_path, "PDF")
            else:
                self.current_qr_image.save(file_path, fmt.upper())

    def update_qr(self):
        """
        Generates the QR code based on the current input data and settings.
        Returns:
            None
        """
        data_base = self.data_input.text().strip()
        if self.radio_email.isChecked():
            email_address = data_base
            subject = self.email_subject_input.text().strip()
            body = self.email_body_input.text().strip()
            data = "mailto:" + email_address
            params = []
            if subject:
                params.append("subject=" + urllib.parse.quote(subject))
            if body:
                params.append("body=" + urllib.parse.quote(body))
            if params:
                data += "?" + "&".join(params)
        elif self.radio_sms.isChecked():
            phone = data_base
            message = self.sms_message_input.text().strip()
            data = "sms:" + phone
            if message:
                data += "?body=" + urllib.parse.quote(message)
        elif self.radio_whatsapp.isChecked():
            number = data_base
            message = self.whatsapp_message_input.text().strip()
            data = "https://wa.me/" + number
            if message:
                data += "?text=" + urllib.parse.quote(message)
        else:
            data = data_base

        index = self.error_combo.currentIndex()
        error_ratio = ["L", "M", "Q", "H"][index]
        border_width = int(self.border_slider.value() / 10)
        size = 300  # base size for QR generation

        # Generate base QR image
        qr_img, box_size = generate_qr(size=size, error_ratio=error_ratio, color=self.selected_color, data=data, border=border_width)

        # If adding a logo
        if self.logo_checkbox.isChecked() and self.logo_path_input.text().strip():
            try:
                qr_img = add_logo_to_qr(qr_img, self.logo_path_input.text().strip(),
                                        correction=error_ratio, border_size=border_width)
            except Exception as e:
                print("Error adding logo:", e)

        # If adding a footer
        if self.footer_checkbox.isChecked():
            footer_text = self.footer_text_input.text().strip()
            whitespace_percent = self.whitespace_slider.value()
            if footer_text:
                try:
                    font_color = self.footer_font_color if self.footer_font_color else self.selected_color
                    qr_img = add_whitespace_with_text(
                        qr_img,
                        footer_text,
                        whitespace_percent,
                        custom_font_path=self.custom_footer_font,
                        font_color=font_color,
                        border=border_width,   # pass border in modules
                        box_size=box_size      # pass box_size in pixels
                    )
                except Exception as e:
                    print("Error adding footer:", e)

        # Now `qr_img` is final
        self.current_qr_image = qr_img

        # Convert the PIL image to QPixmap
        original_pixmap = self.pil2pixmap(qr_img)
        self.current_qr_pixmap = original_pixmap

        # Scale pixmap to always be 400px wide
        scaled_pixmap = original_pixmap.scaledToWidth(150, QtCore.Qt.SmoothTransformation)

        self.preview_label.setFixedWidth(150)
        self.preview_label.setFixedHeight(scaled_pixmap.height())
        self.preview_label.setPixmap(scaled_pixmap)

        self.adjustSize()

    def pil2pixmap(self, im):
        """
        Convert a PIL image to QPixmap.
        Args:
            im (PIL.Image.Image): The PIL image to convert.

        Returns:
            QPixmap: The converted QPixmap.

        """
        if im.mode != "RGB":
            im = im.convert("RGB")
        data = im.tobytes("raw", "RGB")
        qimage = QImage(data, im.size[0], im.size[1], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        return pixmap

