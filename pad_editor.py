# modules/pad_editor.py

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox,
    QGroupBox, QGraphicsScene, QGraphicsView,
    QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsPathItem
)
from PyQt5.QtGui import QPen, QBrush, QColor, QPainterPath
from PyQt5.QtCore import Qt

# Giả sử Pad là một class bạn định nghĩa ở nơi khác
try:
    from pad import Pad  # nếu bạn có một module riêng cho Pad
except ImportError:
    class Pad: pass  # placeholder nếu không có class Pad

class PadEditor(QDialog): 
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pad Editor")
        self.current_pad = None
        self.init_ui()
    def init_ui(self):
        layout = QVBoxLayout()

        # Pad type selection
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Pad Type:"))
        self.pad_type_combo = QComboBox()
        self.pad_type_combo.addItems(["THT (Through Hole)", "SMD (Surface Mount)", "NPTH (Non-Plated)"])
        self.pad_type_combo.currentIndexChanged.connect(self.update_pad_preview)
        type_layout.addWidget(self.pad_type_combo)
        layout.addLayout(type_layout)

        # Pad shape selection
        shape_layout = QHBoxLayout()
        shape_layout.addWidget(QLabel("Shape:"))
        self.pad_shape_combo = QComboBox()
        self.pad_shape_combo.addItems(["Circle", "Rectangle", "Oval", "Custom"])
        self.pad_shape_combo.currentIndexChanged.connect(self.update_pad_preview)
        shape_layout.addWidget(self.pad_shape_combo)
        layout.addLayout(shape_layout)

        # Dimensions
        dims_group = QGroupBox("Dimensions")
        dims_layout = QGridLayout()

        # Width
        dims_layout.addWidget(QLabel("Width:"), 0, 0)
        self.width_edit = QLineEdit("1.5")
        dims_layout.addWidget(self.width_edit, 0, 1)
        dims_layout.addWidget(QLabel("mm"), 0, 2)

        # Height
        dims_layout.addWidget(QLabel("Height:"), 1, 0)
        self.height_edit = QLineEdit("1.5")
        dims_layout.addWidget(self.height_edit, 1, 1)
        dims_layout.addWidget(QLabel("mm"), 1, 2)

        # Hole diameter (for THT)
        dims_layout.addWidget(QLabel("Hole Diameter:"), 2, 0)
        self.hole_diameter_edit = QLineEdit("0.8")
        dims_layout.addWidget(self.hole_diameter_edit, 2, 1)
        dims_layout.addWidget(QLabel("mm"), 2, 2)

        # Corner radius (for rectangle)
        dims_layout.addWidget(QLabel("Corner Radius:"), 3, 0)
        self.corner_radius_edit = QLineEdit("0")
        dims_layout.addWidget(self.corner_radius_edit, 3, 1)
        dims_layout.addWidget(QLabel("mm"), 3, 2)

        dims_group.setLayout(dims_layout)
        layout.addWidget(dims_group)

        # Layer configuration
        layer_group = QGroupBox("Layers")
        layer_layout = QVBoxLayout()

        # Copper layers
        self.top_copper_check = QCheckBox("Top Copper")
        self.top_copper_check.setChecked(True)
        layer_layout.addWidget(self.top_copper_check)

        self.bottom_copper_check = QCheckBox("Bottom Copper")
        layer_layout.addWidget(self.bottom_copper_check)

        # Mask layers
        self.top_mask_check = QCheckBox("Top Solder Mask")
        self.top_mask_check.setChecked(True)
        layer_layout.addWidget(self.top_mask_check)

        self.bottom_mask_check = QCheckBox("Bottom Solder Mask")
        layer_layout.addWidget(self.bottom_mask_check)

        # Paste layers
        self.top_paste_check = QCheckBox("Top Paste")
        self.top_paste_check.setChecked(True)
        layer_layout.addWidget(self.top_paste_check)

        self.bottom_paste_check = QCheckBox("Bottom Paste")
        layer_layout.addWidget(self.bottom_paste_check)

        layer_group.setLayout(layer_layout)
        layout.addWidget(layer_group)

        # Thermal settings for THT pads
        thermal_group = QGroupBox("Thermal Relief")
        thermal_layout = QGridLayout()

        self.thermal_enabled = QCheckBox("Enable Thermal Relief")
        self.thermal_enabled.setChecked(True)
        thermal_layout.addWidget(self.thermal_enabled, 0, 0, 1, 2)

        thermal_layout.addWidget(QLabel("Spoke Width:"), 1, 0)
        self.thermal_spoke_width = QLineEdit("0.3")
        thermal_layout.addWidget(self.thermal_spoke_width, 1, 1)

        thermal_layout.addWidget(QLabel("Gap Width:"), 2, 0)
        self.thermal_gap_width = QLineEdit("0.2")
        thermal_layout.addWidget(self.thermal_gap_width, 2, 1)

        thermal_group.setLayout(thermal_layout)
        layout.addWidget(thermal_group)

        # Preview area
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()
        self.pad_preview_scene = QGraphicsScene()
        self.pad_preview_view = QGraphicsView(self.pad_preview_scene)
        self.pad_preview_view.setMinimumSize(200, 200)
        preview_layout.addWidget(self.pad_preview_view)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        # Buttons
        button_layout = QHBoxLayout()

        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_pad)
        button_layout.addWidget(self.apply_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Connect signals for updating preview
        self.width_edit.textChanged.connect(self.update_pad_preview)
        self.height_edit.textChanged.connect(self.update_pad_preview)
        self.hole_diameter_edit.textChanged.connect(self.update_pad_preview)
        self.corner_radius_edit.textChanged.connect(self.update_pad_preview)

        # Initial preview
        self.update_pad_preview()

    def update_pad_preview(self):
        # Update the pad preview based on current settings
        self.pad_preview_scene.clear()

        try:
            width = float(self.width_edit.text()) * 20  # Scale for better visibility
            height = float(self.height_edit.text()) * 20
            hole_diameter = float(self.hole_diameter_edit.text()) * 20
            corner_radius = float(self.corner_radius_edit.text()) * 20
        except ValueError:
            # If any conversion fails, use default values
            width = 30
            height = 30
            hole_diameter = 16
            corner_radius = 0

        pad_type = self.pad_type_combo.currentText()
        pad_shape = self.pad_shape_combo.currentText()

        # Draw pad outline
        if pad_shape == "Circle":
            diameter = max(width, height)
            pad_item = QGraphicsEllipseItem(-diameter / 2, -diameter / 2, diameter, diameter)
        elif pad_shape == "Rectangle":
            if corner_radius > 0:
                # Create rounded rectangle path
                path = QPainterPath()
                path.addRoundedRect(-width / 2, -height / 2, width, height, corner_radius, corner_radius)
                pad_item = QGraphicsPathItem(path)
            else:
                pad_item = QGraphicsRectItem(-width / 2, -height / 2, width, height)
        elif pad_shape == "Oval":
            path = QPainterPath()
            path.addEllipse(-width / 2, -height / 2, width, height)
            pad_item = QGraphicsPathItem(path)
        else:  # Custom - just use rectangle for now
            pad_item = QGraphicsRectItem(-width / 2, -height / 2, width, height)

        # Set pad appearance
        pad_item.setPen(QPen(QColor(0, 128, 0), 1))
        pad_item.setBrush(QBrush(QColor(0, 200, 0, 128)))
        self.pad_preview_scene.addItem(pad_item)

        # Draw hole for THT pads
        if "THT" in pad_type and hole_diameter > 0:
            hole_item = QGraphicsEllipseItem(-hole_diameter / 2, -hole_diameter / 2,
                                             hole_diameter, hole_diameter)
            hole_item.setPen(QPen(QColor(0, 0, 0), 1))
            hole_item.setBrush(QBrush(QColor(255, 255, 255)))
            self.pad_preview_scene.addItem(hole_item)

            # Draw thermal relief if enabled
            if self.thermal_enabled.isChecked():
                try:
                    spoke_width = float(self.thermal_spoke_width.text()) * 20
                    gap_width = float(self.thermal_gap_width.text()) * 20
                except ValueError:
                    spoke_width = 6
                    gap_width = 4

                # Draw thermal relief spokes
                for angle in [0, 90, 180, 270]:
                    # Create a rectangle rotated at the specified angle
                    spoke = QGraphicsRectItem(-width / 2, -spoke_width / 2, width, spoke_width)
                    spoke.setRotation(angle)
                    spoke.setPen(QPen(QColor(0, 128, 0), 1))
                    spoke.setBrush(QBrush(QColor(0, 200, 0, 128)))
                    self.pad_preview_scene.addItem(spoke)

                    # Create cutouts on each side of the spoke
                    gap = QGraphicsRectItem(-hole_diameter / 2 - gap_width, -spoke_width / 2 - gap_width / 2,
                                            gap_width, spoke_width + gap_width)
                    gap.setRotation(angle)
                    gap.setPen(QPen(QColor(0, 0, 0), 1))
                    gap.setBrush(QBrush(QColor(255, 255, 255)))
                    self.pad_preview_scene.addItem(gap)

        # Reset view
        self.pad_preview_view.setScene(self.pad_preview_scene)
        self.pad_preview_view.fitInView(self.pad_preview_scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        self.pad_preview_view.centerOn(0, 0)

    def apply_pad(self):
        # Create a pad with the current settings and return it
        pad_data = {
            'type': self.pad_type_combo.currentText(),
            'shape': self.pad_shape_combo.currentText(),
            'width': float(self.width_edit.text()),
            'height': float(self.height_edit.text()),
            'hole_diameter': float(self.hole_diameter_edit.text()),
            'corner_radius': float(self.corner_radius_edit.text()),
            'layers': {
                'top_copper': self.top_copper_check.isChecked(),
                'bottom_copper': self.bottom_copper_check.isChecked(),
                'top_mask': self.top_mask_check.isChecked(),
                'bottom_mask': self.bottom_mask_check.isChecked(),
                'top_paste': self.top_paste_check.isChecked(),
                'bottom_paste': self.bottom_paste_check.isChecked()
            },
            'thermal': {
                'enabled': self.thermal_enabled.isChecked(),
                'spoke_width': float(self.thermal_spoke_width.text()),
                'gap_width': float(self.thermal_gap_width.text())
            }
        }

        # Here you would normally create the pad and add it to your PCB
        # This is a signal that the pad was created successfully
        self.current_pad = pad_data
        self.close()
        return pad_data

    def edit_selected_pad(self):
        # Edit the currently selected pad
        selected_items = self.drawing_app.scene.selectedItems()
        for item in selected_items:
            if isinstance(item, Pad):
                # Mở Pad Editor với dữ liệu từ pad đã chọn
                pad_editor = PadEditor(self)

                # Thiết lập dữ liệu hiện tại
                pad_editor.pad_type_combo.setCurrentText(item.pad_data['type'])
                pad_editor.pad_shape_combo.setCurrentText(item.pad_data['shape'])
                pad_editor.width_edit.setText(str(item.pad_data['width']))
                pad_editor.height_edit.setText(str(item.pad_data['height']))
                pad_editor.hole_diameter_edit.setText(str(item.pad_data['hole_diameter']))
                pad_editor.corner_radius_edit.setText(str(item.pad_data['corner_radius']))

                # Thiết lập các checkboxes cho layers
                if 'layers' in item.pad_data:
                    layers = item.pad_data['layers']
                    pad_editor.top_copper_check.setChecked(layers.get('top_copper', True))
                    pad_editor.bottom_copper_check.setChecked(layers.get('bottom_copper', False))
                    pad_editor.top_mask_check.setChecked(layers.get('top_mask', True))
                    pad_editor.bottom_mask_check.setChecked(layers.get('bottom_mask', False))
                    pad_editor.top_paste_check.setChecked(layers.get('top_paste', True))
                    pad_editor.bottom_paste_check.setChecked(layers.get('bottom_paste', False))

                # Thiết lập thermal relief settings
                if 'thermal' in item.pad_data:
                    thermal = item.pad_data['thermal']
                    pad_editor.thermal_enabled.setChecked(thermal.get('enabled', True))
                    pad_editor.thermal_spoke_width.setText(str(thermal.get('spoke_width', 0.3)))
                    pad_editor.thermal_gap_width.setText(str(thermal.get('gap_width', 0.2)))

                # Show dialog
                if pad_editor.exec_() == QDialog.Accepted and pad_editor.current_pad:
                    # Cập nhật pad với dữ liệu mới
                    item.pad_data = pad_editor.current_pad
                    item.update()  # Cập nhật hiển thị
                    self.display_message("Updated pad properties")

                break 