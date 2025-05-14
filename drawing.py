import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QColorDialog
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtWidgets import QGraphicsLineItem, QGraphicsRectItem, QGraphicsEllipseItem

class DrawingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 Multi-Layer Drawing")
        self.setGeometry(100, 100, 800, 600)

        self.scene = QGraphicsScene()
        self.drawing_window = QGraphicsView(self.scene)
        self.setCentralWidget(self.drawing_window)

        self.drawing_mode = None
        self.selected_color = QColor(Qt.black)
        self.layer = None

        self.current_item = None
        self.start_point = None

        # Assign event handlers correctly
        self.drawing_window.setMouseTracking(True)  # Enable mouse tracking
        self.drawing_window.viewport().installEventFilter(self)

    def eventFilter(self, source, event):
        if source is self.drawing_window.viewport():
            if event.type() == event.MouseButtonPress:
                self.mouse_press(event)
                return True  # Trả về True để báo hiệu đã xử lý xong sự kiện
            elif event.type() == event.MouseButtonRelease:
                self.mouse_release(event)
                return True
            elif event.type() == event.MouseMove:
                self.mouse_move(event)
                return True
        return super().eventFilter(source, event)  # Không chặn các sự kiện khác

    # Fix the mouse_press method in DrawingApp class
    def mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self.start_point = self.drawing_window.mapToScene(event.pos())
            if self.drawing_mode == "line":
                # Create a line with proper initialization (from start point to itself initially)
                self.current_item = QGraphicsLineItem(
                    self.start_point.x(), self.start_point.y(),
                    self.start_point.x(), self.start_point.y()
                )
                self.current_item.setPen(QPen(self.selected_color, 2))
                self.scene.addItem(self.current_item)
            elif self.drawing_mode == "rect":
                # Create an empty rectangle at the start point
                self.current_item = QGraphicsRectItem(
                    QRectF(self.start_point.x(), self.start_point.y(), 0, 0)
                )
                self.current_item.setPen(QPen(self.selected_color, 2))
                self.scene.addItem(self.current_item)
            elif self.drawing_mode == "circle":
                # Create an empty ellipse at the start point
                self.current_item = QGraphicsEllipseItem(
                    QRectF(self.start_point.x(), self.start_point.y(), 0, 0)
                )
                self.current_item.setPen(QPen(self.selected_color, 2))
                self.scene.addItem(self.current_item)

    def mouse_release(self, event):
        if self.current_item:
            self.layer["items"].append(self.current_item)  # Lưu lại vào danh sách
        self.current_item = None

    def mouse_move(self, event):
        if self.current_item and self.start_point:
            self.end_point = self.drawing_window.mapToScene(event.pos())
            if isinstance(self.current_item, QGraphicsLineItem):
                self.current_item.setLine(self.start_point.x(), self.start_point.y(),
                                          self.end_point.x(), self.end_point.y())
            elif isinstance(self.current_item, QGraphicsRectItem) or isinstance(self.current_item,
                                                                                QGraphicsEllipseItem):
                rect = QRectF(self.start_point, self.end_point).normalized()
                self.current_item.setRect(rect)
        return True

    def choose_color(self):
        color = QColorDialog.getColor(self.selected_color, self, "Choose Color")
        if color.isValid():
            self.selected_color = color