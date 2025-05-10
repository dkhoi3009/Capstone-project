from PyQt5.QtGui import QPen, QColor
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsItem

class LayerManager:
    def __init__(self, scene: QGraphicsScene):
        """
        Quản lý các layer trong cảnh vẽ.
        :param scene: QGraphicsScene nơi các layer sẽ được quản lý.
        """
        self.scene = scene
        self.layers = {}  # Dictionary để lưu các layer theo tên
        # Thêm các layer mặc định
        self.add_layer("top_copper", QColor(240, 240, 240), z_index=-3)
        self.add_layer("bottom_copper", QColor(0, 0, 255), z_index=-2)
        self.add_layer("top_mark", QColor(255, 0, 0), z_index=-1)
        self.add_layer("bottom_mark", QColor(0, 255, 0), z_index=0)
        self.add_layer("top_paste", QColor(255, 255, 0), z_index=1)
        self.add_layer("bottom_paste", QColor(255, 165, 0), z_index=2)

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