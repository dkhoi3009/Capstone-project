import  traceback
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QDockWidget, QTreeWidget, QTreeWidgetItem,
    QWidget, QGridLayout, QLabel, QLineEdit, QComboBox, QTabWidget,
    QGraphicsScene, QListWidget, QToolBar, QAction, QMessageBox, QDialog, QListWidgetItem,
    QActionGroup
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QColor

from drawing import DrawingApp
from pad_editor import PadEditor
from pad import Pad
from layer_manager import LayerManager
from layer_setting import LayerSetting

# Layer type colors (example colors - adjust as needed)
LAYER_COLORS = {
    "silk": QColor(255, 255, 255, 200),  # White with transparency
    "electric": QColor(0, 100, 255, 180),  # Blue with transparency
    "solder": QColor(0, 180, 0, 180),  # Green with transparency
    "paste": QColor(180, 180, 180, 180),  # Gray with transparency
    "assembly": QColor(255, 200, 0, 180),  # Yellow with transparency
    "board": QColor(30, 30, 30, 255),  # Dark gray
    "plane": QColor(100, 50, 0, 200),  # Brown with transparency
    "drill": QColor(255, 50, 50, 200),  # Red with transparency
    "route": QColor(255, 100, 0, 200),  # Orange with transparency
    "padstack": QColor(0, 200, 200, 200),  # Cyan with transparency
    "viastack": QColor(200, 0, 200, 200),  # Magenta with transparency
    "designRule": QColor(128, 0, 200, 150),  # Purple with transparency
    "dimension": QColor(100, 200, 255, 180),  # Light blue with transparency
    "keepoutRoute": QColor(255, 100, 100, 120),  # Light red with transparency
    "keepoutDrill": QColor(255, 150, 50, 120),  # Light orange with transparency
    "keepoutComponent": QColor(100, 255, 100, 120),  # Light green with transparency
    "heightLimit": QColor(100, 100, 255, 120)  # Light blue with transparency
}

class main_app(QMainWindow):
    def __init__(self):
        try:
            super().__init__()
            self.setWindowTitle('PCB Design Studio')
            self.setGeometry(100, 100, 1200, 800)
            self.drawing_app = DrawingApp()  # Create an instance of DrawingApp
            self.init_ui()  # Call init_ui method
            self.layer_manager = LayerManager(scene=self.drawing_app.scene, layers_widget=self.layers_widget)
            self.add_default_layers()
        except Exception as e:
            # Fallback error handling
            print(f"Initialization Error: {e}")
            print(traceback.format_exc())
            QMessageBox.critical(None, "Initialization Error", str(e))

    def init_ui(self):
        try:
            # Create main layout components
            self.create_menu_bar()
            self.create_toolbar()
            self.create_left_sidebar()
            self.create_right_sidebar()
            self.create_central_canvas()
            self.create_bottom_panel()
        except Exception as e:
            # Fallback error handling
            print(f"UI Creation Error: {e}")
            print(traceback.format_exc())
            QMessageBox.critical(None, "UI Creation Error", str(e))

    def create_menu_bar(self):
        # Create menubar if it doesn't exist
        if not hasattr(self, 'menubar'):
            self.menubar = self.menuBar()

        # File Menu
        file_menu = self.menubar.addMenu('File')
        new_project_action = QAction('New Project', self)
        open_project_action = QAction('Open Project', self)
        save_action = QAction('Save', self)
        file_menu.addAction(new_project_action)
        file_menu.addAction(open_project_action)
        file_menu.addAction(save_action)

        # Edit Menu
        edit_menu = self.menubar.addMenu('Edit')
        undo_action = QAction('Undo', self)
        redo_action = QAction('Redo', self)
        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)

        # Design Menu
        design_menu = self.menubar.addMenu('Design')
        create_footprint_action = QAction('Create Footprint', self)
        layer_manager_menu = design_menu.addMenu('Layer Manager')
        add_layer_action = QAction('Add Layer', self)
        layer_setting_action = QAction('Layer Setting', self)
        add_layer_action.triggered.connect(lambda: self.add_custom_layer())
        layer_setting_action.triggered.connect(lambda: self.open_layer_setting_dialog())
        layer_manager_menu.addAction(add_layer_action)
        layer_manager_menu.addAction(layer_setting_action)
        design_menu.addAction(create_footprint_action)

    # Add layer
    def add_custom_layer(self):
        layer_name = f'Custom {len(self.layer_manager.layers) - 6}'
        self.layer_manager.add_layer(layer_name)

    def add_default_layers(self):
        # Thêm các layer mặc định
        index = 0
        for layer, color in LAYER_COLORS.items():
            self.layer_manager.add_layer(layer, color, z_index=index-len(LAYER_COLORS))
        # self.layer_manager.add_layer("bottom_copper", QColor(0, 0, 255), z_index=-2)
        # self.layer_manager.add_layer("top_mark", QColor(255, 0, 0), z_index=-1)
        # self.layer_manager.add_layer("bottom_mark", QColor(0, 255, 0), z_index=0)
        # self.layer_manager.add_layer("top_paste", QColor(255, 255, 0), z_index=1)
        # self.layer_manager.add_layer("bottom_paste", QColor(255, 165, 0), z_index=2)

    # Design toolbar
    def create_toolbar(self):
        toolbar = QToolBar('Design Tools')
        self.addToolBar(toolbar)

        # Drawing tools
        draw_line_action = QAction('Draw Line', self)
        draw_line_action.triggered.connect(lambda: self.set_drawing_mode("line"))
        toolbar.addAction(draw_line_action)

        draw_rect_action = QAction('Draw Rectangle', self)
        draw_rect_action.triggered.connect(lambda: self.set_drawing_mode("rect"))
        toolbar.addAction(draw_rect_action)

        draw_circle_action = QAction('Draw Circle', self)
        draw_circle_action.triggered.connect(lambda: self.set_drawing_mode("circle"))
        toolbar.addAction(draw_circle_action)

        color_action = QAction('Choose Color', self)
        color_action.triggered.connect(self.choose_drawing_color)
        toolbar.addAction(color_action)

        toolbar.addSeparator()
        pad_editor_action = QAction('Pad Editor', self)
        pad_editor_action.triggered.connect(self.show_pad_editor)
        toolbar.addAction(pad_editor_action)

    def set_drawing_mode(self, mode):
        print(f"Setting drawing mode to: {mode}")  # Debug print
        if hasattr(self, 'drawing_app'):
            self.drawing_app.drawing_mode = mode
            print(f"Drawing mode set to: {self.drawing_app.drawing_mode}")

    def choose_drawing_color(self):
        if hasattr(self, 'drawing_app'):
            self.drawing_app.choose_color()

    def create_central_canvas(self):
        self.canvas_widget = QTabWidget()

        # Set up the scene for DrawingApp
        scene = QGraphicsScene(self)
        scene.setSceneRect(0, 0, 2000, 2000)
        self.drawing_app.scene = scene
        self.drawing_app.drawing_window.setScene(scene)

        self.add_grid(scene)
        self.canvas_widget.addTab(self.drawing_app.drawing_window, 'PCB Design')
        self.setCentralWidget(self.canvas_widget)

    def add_grid(self, scene):
        grid_color = QColor(240, 240, 240)
        grid_spacing = 10
        for x in range(0, 2000, grid_spacing):
            scene.addLine(x, 0, x, 2000, QPen(grid_color))
        for y in range(0, 2000, grid_spacing):
            scene.addLine(0, y, 2000, y, QPen(grid_color))

    def create_left_sidebar(self):
        dock = QDockWidget('Component Library', self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        tree = QTreeWidget()
        tree.setHeaderLabel('Components')
        categories = [
            ('Passive', ['Resistor', 'Capacitor', 'Inductor']),
            ('Active', ['Transistor', 'IC', 'Diode']),
            ('Connectors', ['USB', 'HDMI', 'Pin Header'])
        ]
        for category, components in categories:
            cat_item = QTreeWidgetItem(tree, [category])
            for component in components:
                QTreeWidgetItem(cat_item, [component])
        dock.setWidget(tree)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

    def create_right_sidebar(self):
        layer_dock = QDockWidget('Layers', self)
        layer_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.layers_widget = QListWidget()
        self.layers_widget.itemChanged.connect(self.on_layer_checked)
        self.layers_widget.itemSelectionChanged.connect(self.on_layer_selected)
        layer_dock.setWidget(self.layers_widget)

        prop_dock = QDockWidget('Properties', self)
        prop_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        properties_widget = QWidget()
        layout = QGridLayout()
        properties = [
            ('Component Type:', QComboBox()),
            ('Footprint:', QLineEdit()),
            ('Value:', QLineEdit()),
            ('Tolerance:', QComboBox())
        ]
        for i, (label, widget) in enumerate(properties):
            layout.addWidget(QLabel(label), i, 0)
            layout.addWidget(widget, i, 1)
        properties_widget.setLayout(layout)
        prop_dock.setWidget(properties_widget)

        self.addDockWidget(Qt.RightDockWidgetArea, layer_dock)
        self.addDockWidget(Qt.RightDockWidgetArea, prop_dock)

    def create_bottom_panel(self):
        dock = QDockWidget('Messages', self)
        dock.setAllowedAreas(Qt.BottomDockWidgetArea)
        message_list = QListWidget()
        message_list.addItems([
            'Welcome to PCB Design Studio',
            'Ready to start designing'
        ])
        dock.setWidget(message_list)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock)

    def show_error_message(self, title, message):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setWindowTitle(title)
        error_dialog.setText(message)
        error_dialog.setDetailedText(traceback.format_exc())
        error_dialog.exec_()

    def show_pad_editor(self):
        # Open the pad editor dialog
        try:
            pad_editor = PadEditor(self)
            pad_editor.setWindowModality(Qt.ApplicationModal)

            # Use a safe approach to show the dialog
            if pad_editor.exec_() == QDialog.Accepted and pad_editor.current_pad:
                self.add_pad_to_design(pad_editor.current_pad)
        except Exception as e:
            traceback_str = traceback.format_exc()
            print(f"Error in pad editor: {str(e)}\n{traceback_str}")
            self.show_error_message("Pad Editor Error", f"Error in pad editor: {str(e)}")

    def add_pad_to_design(self, pad_data):
        # Add a pad to the PCB design
        try:
            pad = Pad(pad_data)
            # Position the pad at the center of the view
            view_center = self.drawing_app.drawing_window.mapToScene(
                self.drawing_app.drawing_window.viewport().rect().center())
            pad.setPos(view_center)

            # Add to scene
            self.drawing_app.scene.addItem(pad)

            # Store in appropriate layer
            if not hasattr(self.drawing_app, 'pads'):
                self.drawing_app.pads = []
            self.drawing_app.pads.append(pad)

            # Select the pad so the user can move it
            pad.setSelected(True)
        except Exception as e:
            self.show_error_message("Pad Creation Error", f"Error creating pad: {str(e)}")

    # Function to handle item check state change
    def on_layer_checked(self, item):
        if item.checkState() == Qt.CheckState.Checked:
            self.layer_manager.show_layer(item.text())
        else:
            self.layer_manager.hide_layer(item.text())

    # Function to handle item selection state change
    def on_layer_selected(self):
        selected_layer_name = self.layers_widget.selectedItems()[0].text()
        self.drawing_app.layer = self.layer_manager.layers[selected_layer_name]

    # Open layer dialog
    def open_layer_setting_dialog(self):
        try:
            layer_setting = LayerSetting(self)
            layer_setting.setWindowModality(Qt.ApplicationModal)

            # Use a safe approach to show the dialog
            if layer_setting.exec_() == QDialog.Accepted and layer_setting.current_pad:
                self.add_pad_to_design(layer_setting.current_pad)
        except Exception as e:
            traceback_str = traceback.format_exc()
            print(f"Error in pad editor: {str(e)}\n{traceback_str}")
            self.show_error_message("Pad Editor Error", f"Error in pad editor: {str(e)}")