# modules/pad_item.py

import json
import traceback
from PyQt5.QtWidgets import QGraphicsItem, QMessageBox
from PyQt5.QtGui import QPen, QBrush, QColor
from PyQt5.QtCore import QRectF, Qt


class Pad(QGraphicsItem):
    def __init__(self, pad_data, parent=None):
        super().__init__(parent)
        self.pad_data = json.loads(json.dumps(pad_data))  # deep copy tránh lỗi

        # Gán giá trị mặc định
        if 'width' not in self.pad_data or not isinstance(self.pad_data['width'], (int, float)):
            self.pad_data['width'] = 1.5
        if 'height' not in self.pad_data or not isinstance(self.pad_data['height'], (int, float)):
            self.pad_data['height'] = 1.5
        if 'hole_diameter' not in self.pad_data or not isinstance(self.pad_data['hole_diameter'], (int, float)):
            self.pad_data['hole_diameter'] = 0.8
        if 'corner_radius' not in self.pad_data or not isinstance(self.pad_data['corner_radius'], (int, float)):
            self.pad_data['corner_radius'] = 0

        if 'layers' not in self.pad_data:
            self.pad_data['layers'] = {
                'top_copper': True, 'bottom_copper': False,
                'top_mask': True, 'bottom_mask': False,
                'top_paste': True, 'bottom_paste': False
            }

        if 'thermal' not in self.pad_data:
            self.pad_data['thermal'] = {'enabled': True, 'spoke_width': 0.3, 'gap_width': 0.2}

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)

    def show_error_message(self, title, message):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setWindowTitle(title)
        error_dialog.setText(message)
        tb_str = traceback.format_exc()
        if tb_str != "NoneType: None\n":
            error_dialog.setDetailedText(tb_str)
        print(f"{title}: {message}\n{tb_str}")
        error_dialog.exec_()

    def boundingRect(self):
        width = self.pad_data['width'] * 10
        height = self.pad_data['height'] * 10
        return QRectF(-width / 2, -height / 2, width, height)

    def paint(self, painter, option, widget):
        width = self.pad_data['width'] * 10
        height = self.pad_data['height'] * 10
        hole_diameter = self.pad_data['hole_diameter'] * 10
        corner_radius = self.pad_data['corner_radius'] * 10

        painter.setPen(QPen(QColor(0, 128, 0), 1))
        painter.setBrush(QBrush(QColor(0, 200, 0, 128) if self.pad_data['layers']['top_copper']
                                else QColor(0, 100, 0, 64)))

        shape = self.pad_data.get('shape', 'Rectangle')

        if shape == "Circle":
            diameter = max(width, height)
            painter.drawEllipse(-diameter / 2, -diameter / 2, diameter, diameter)
        elif shape == "Rectangle":
            if corner_radius > 0:
                painter.drawRoundedRect(-width / 2, -height / 2, width, height, corner_radius, corner_radius)
            else:
                painter.drawRect(-width / 2, -height / 2, width, height)
        elif shape == "Oval":
            painter.drawEllipse(-width / 2, -height / 2, width, height)

        if "THT" in self.pad_data.get('type', '') and hole_diameter > 0:
            painter.setPen(QPen(QColor(0, 0, 0), 1))
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(-hole_diameter / 2, -hole_diameter / 2, hole_diameter, hole_diameter)

            if self.pad_data['thermal']['enabled']:
                spoke_width = self.pad_data['thermal']['spoke_width'] * 10
                gap_width = self.pad_data['thermal']['gap_width'] * 10
                painter.save()
                for angle in [0, 90, 180, 270]:
                    painter.rotate(angle)
                    painter.setPen(QPen(QColor(0, 128, 0), 1))
                    painter.setBrush(QBrush(QColor(0, 200, 0, 128)))
                    painter.drawRect(-width / 2, -spoke_width / 2,
                                     width / 2 - hole_diameter / 2, spoke_width)
                    painter.restore()
                    painter.save()
                painter.restore()

        if self.isSelected():
            painter.setPen(QPen(QColor(255, 0, 0), 2, Qt.DashLine))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(self.boundingRect())
