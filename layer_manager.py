from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsItem, QListWidget, QListWidgetItem

class LayerManager:
    def __init__(self, scene: QGraphicsScene, layers_widget: QListWidget):
        """
        Quản lý các layer trong cảnh vẽ.
        :param scene: QGraphicsScene nơi các layer sẽ được quản lý.
        """
        self.scene = scene
        self.layers_widget = layers_widget
        self.layers = {} # Dictionary để lưu các layer theo tên

    def add_layer(self, layer_name: str, color: QColor = QColor(0, 0, 0), z_index: int = 0):
        """
        Thêm một layer mới vào cảnh.
        :param layer_name: Tên của layer.
        :param color: Màu mặc định của layer.
        :param z_index: Thứ tự hiển thị của layer (z-index).
        """
        if layer_name in self.layers:
            raise ValueError(f"Layer '{layer_name}' đã tồn tại.")

        # Tạo một layer mới
        layer = {
            "items": [],  # Danh sách các đối tượng trong layer
            "color": color,
            "z_index": z_index
        }
        self.layers[layer_name] = layer
        self.add_layer_to_list(layer_name, color)

    def add_layer_to_list(self, layer_name: str, color: QColor):
        item = QListWidgetItem(layer_name)
        icon = QIcon(QPixmap(16, 16))
        icon.pixmap(16, 16).fill(color)
        item.setIcon(icon)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(Qt.CheckState.Checked)
        self.layers_widget.addItem(item)
        self.layers_widget.setCurrentItem(item)

    def remove_layer(self, layer_name: str):
        """
        Xóa một layer khỏi cảnh.
        :param layer_name: Tên của layer cần xóa.
        """
        if layer_name not in self.layers:
            raise ValueError(f"Layer '{layer_name}' không tồn tại.")

        # Xóa tất cả các đối tượng trong layer khỏi scene
        for item in self.layers[layer_name]["items"]:
            self.scene.removeItem(item)
        del self.layers[layer_name]

    def hide_layer(self, layer_name: str):
        """
        Xóa một layer khỏi cảnh.
        :param layer_name: Tên của layer cần xóa.
        """
        if layer_name not in self.layers:
            raise ValueError(f"Layer '{layer_name}' không tồn tại.")

        # Xóa tất cả các đối tượng trong layer khỏi scene
        for item in self.layers[layer_name]["items"]:
            item.setVisible(False)

    def show_layer(self, layer_name: str):
        """
        Xóa một layer khỏi cảnh.
        :param layer_name: Tên của layer cần xóa.
        """
        if layer_name not in self.layers:
            raise ValueError(f"Layer '{layer_name}' không tồn tại.")

        # Xóa tất cả các đối tượng trong layer khỏi scene
        for item in self.layers[layer_name]["items"]:
            item.setVisible(True)

    def add_item_to_layer(self, layer_name: str, item: QGraphicsItem):
        """
        Thêm một đối tượng vào layer.
        :param layer_name: Tên của layer.
        :param item: Đối tượng QGraphicsItem cần thêm.
        """
        if layer_name not in self.layers:
            raise ValueError(f"Layer '{layer_name}' không tồn tại.")

        # Thêm đối tượng vào layer và scene
        self.layers[layer_name]["items"].append(item)
        item.setZValue(self.layers[layer_name]["z_index"])  # Đặt z-index cho đối tượng
        self.scene.addItem(item)

    def clear_layer(self, layer_name: str):
        """
        Xóa tất cả các đối tượng trong một layer.
        :param layer_name: Tên của layer cần xóa.
        """
        if layer_name not in self.layers:
            raise ValueError(f"Layer '{layer_name}' không tồn tại.")

        for item in self.layers[layer_name]["items"]:
            self.scene.removeItem(item)
        self.layers[layer_name]["items"].clear()

    def set_layer_color(self, layer_name: str, color: QColor):
        """
        Đặt màu cho tất cả các đối tượng trong layer.
        :param layer_name: Tên của layer.
        :param color: Màu mới.
        """
        if layer_name not in self.layers:
            raise ValueError(f"Layer '{layer_name}' không tồn tại.")

        for item in self.layers[layer_name]["items"]:
            if isinstance(item, QGraphicsItem):
                pen = QPen(color)
                item.setPen(pen)
        self.layers[layer_name]["color"] = color