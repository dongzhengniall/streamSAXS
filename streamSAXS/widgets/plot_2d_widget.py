import os
import sys
import numpy as np
import pyqtgraph as pg
from PyQt5 import QtGui
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QApplication, QToolBar, QFileDialog, QComboBox, QDialog, QHBoxLayout,
                             QLabel, QLineEdit, QFormLayout, QPushButton)
from PIL import Image


class MappingSettingDialog(QDialog):
    def __init__(self, mapping_setting, sample_range):
        QDialog.__init__(self)
        self.mapping_setting = mapping_setting
        self.sample_range = sample_range
        self.resize(400, 200)
        self.setWindowTitle("Mapping Setting")
        layout = QVBoxLayout()
        self.error_label = QLabel("Please input the mapping parameters.")
        layout.addWidget(self.error_label)
        main_widget = QWidget()
        main_layout = QFormLayout()
        self.x_size_edit = QLineEdit()
        self.y_size_edit = QLineEdit()
        IntValidator = QtGui.QIntValidator()
        IntValidator.setRange(1, 100000000)
        self.x_size_edit.setValidator(IntValidator)
        self.y_size_edit.setValidator(IntValidator)
        if self.sample_range["x"]:
            self.x_size_edit.setText(str(self.sample_range["x"]))
        if self.sample_range["y"]:
            self.y_size_edit.setText(str(self.sample_range["y"]))

        self.shape_combobox = QComboBox()
        self.shape_combobox.addItems(["Z Shape", "S Shape"])
        self.shape_combobox.setCurrentText(self.mapping_setting["shape"])

        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.submit_close)

        main_layout.addRow("X Mapping Size:", self.x_size_edit)
        main_layout.addRow("Y Mapping Size:", self.y_size_edit)
        main_layout.addRow("Scan Shape:", self.shape_combobox)
        main_layout.addRow("", self.apply_button)
        main_widget.setLayout(main_layout)
        layout.addWidget(main_widget)
        self.setLayout(layout)

    def submit_close(self):
        self.mapping_setting["shape"] = self.shape_combobox.currentText()
        if self.x_size_edit.text() and self.y_size_edit.text():
            if int(self.x_size_edit.text()) > 0 and int(self.y_size_edit.text()) > 0:
                self.sample_range["x"] = int(self.x_size_edit.text())
                self.sample_range["y"] = int(self.y_size_edit.text())
            else:
                self.error_label.setText("Please input the right mapping size.")
                self.error_label.setStyleSheet('color: red')
                return
        else:
            self.error_label.setText("Please input the right mapping size.")
            self.error_label.setStyleSheet('color: red')
            return

        self.accept()


class Plot2DWidget(QWidget):
    def __init__(self, parent=None):
        super(Plot2DWidget, self).__init__(parent)
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        pg.setConfigOptions(imageAxisOrder='col-major')
        self.win = pg.GraphicsLayoutWidget()
        self.p1 = self.win.addPlot()
        # Item for displaying image data
        self.img = pg.ImageItem()
        self.p1.addItem(self.img)
        # Contrast/color control
        self.hist = pg.HistogramLUTItem()
        self.hist.fillHistogram(color=(255, 0, 0))
        self.hist.setImageItem(self.img)
        self.win.addItem(self.hist)
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.navbar = QToolBar()
        self.navbar.setIconSize(QSize(30, 30))
        self.navbar.addAction(QIcon(os.getcwd()+'/ui/icons/settings'), "Mapping Setting", self.set_mapping_setting)
        self.navbar.addAction(QIcon(os.getcwd()+'/ui/icons/save.png'), "Save Image in File", self.save_image_to_file)
        self.navbar.addAction(QIcon(os.getcwd()+'/ui/icons/load.png'), "Load Image in File", self.load_image_in_file)
        self.layout.addWidget(self.navbar)
        self.layout.addWidget(self.win)

        self.sample_range = {"x": 0, "y": 0}
        self.current_axis = {"x": None, "y": None}
        self.data = None
        self.init = 1
        self.mapping_setting = {"shape": "Z Shape", "direction": "left_right"}

    def set_mapping_setting(self):
        dialog = MappingSettingDialog(self.mapping_setting, self.sample_range)
        if dialog.exec_():
            self.mapping_setting = dialog.mapping_setting
            self.sample_range = dialog.sample_range
            self.set_show_range(self.sample_range)

    def set_show_range(self, size):
        self.sample_range = size
        self.axis_info = {"x": 0, "y": 0}
        # Set the scan area numpy
        self.data = np.full((self.sample_range["x"], self.sample_range["y"]), float('nan'))
        self.img.setImage(self.data)
        # Set x and y range
        self.p1.setXRange(0, self.sample_range["x"] - 1)
        self.p1.setYRange(0, self.sample_range["y"] - 1)

        for axis in ["x", "y"]:
            # Set display scale
            x = np.linspace(0, self.sample_range[axis] - 1, self.sample_range[axis])
            strx = np.linspace(0, self.sample_range[axis] - 1, self.sample_range[axis])
            strx = strx.astype(str)
            x_show = []
            strx_show = []
            if len(x) > 10:
                a = len(x) // 10
                i = 0
                while i < len(x):
                    x_show.append(x[i])
                    strx_show.append(strx[i])
                    i = i + a
            else:
                x_show = x
                strx_show = strx

            ticksx = [[i, j] for i, j in zip(x_show, strx_show)]
            if axis == "x":
                self.p1.getAxis("bottom").setTicks([ticksx])
            if axis == "y":
                self.p1.getAxis("left").setTicks([ticksx])

    def clear(self):
        if self.sample_range["x"] > 0 and self.sample_range["y"] > 0:
            self.set_show_range(self.sample_range)
        self.current_axis = {"x": None, "y": None}
        #self.data = None

    def update_data_all(self, plot):
        if plot["type"] == "2DP":
            value = plot["data"]
            self.position_without_coordinate()
            if self.current_axis:
                self.update_data(self.current_axis, value)
        elif plot["type"] == "2DPL":
            value = plot["data"]
            self.update_data_list(value)

    def position_without_coordinate(self):
        if self.mapping_setting['shape'] == "Z Shape":
            if self.current_axis["x"] is None:
                self.current_axis["y"] = self.sample_range["y"] - 1
                self.current_axis["x"] = 0
            else:
                if 0 <= self.current_axis["x"] <= self.sample_range["x"] - 1 and 0 <= self.current_axis["y"] <= \
                        self.sample_range["y"] - 1:
                    if self.current_axis["x"] == self.sample_range["x"] - 1:
                        self.current_axis["x"] = 0
                        self.current_axis["y"] -= 1
                    else:
                        self.current_axis["x"] += 1
                else:
                    self.current_axis["x"] = None
        elif self.mapping_setting['shape'] == "S Shape":
            if self.current_axis["x"] is None:
                self.current_axis["y"] = self.sample_range["y"] - 1
                self.current_axis["x"] = 0
            else:
                if 0 <= self.current_axis["x"] <= self.sample_range["x"] - 1 and 0 <= self.current_axis["y"] <= \
                        self.sample_range["y"] - 1:
                    if self.mapping_setting["direction"] == "left_right" and self.current_axis["x"] == \
                            self.sample_range["x"] - 1:
                        self.mapping_setting["direction"] = "right_left"
                        self.current_axis["y"] -= 1
                    elif self.mapping_setting["direction"] == "right_left" and self.current_axis["x"] == 0:
                        self.current_axis["y"] -= 1
                        self.mapping_setting["direction"] = "left_right"
                    elif self.mapping_setting["direction"] == "right_left":
                        self.current_axis["x"] -= 1
                    elif self.mapping_setting["direction"] == "left_right":
                        self.current_axis["x"] += 1
                else:
                    self.current_axis["x"] = None

    def update_data(self, axis, value):
        if not np.isnan(value["value"]) and axis["x"] is not None:
            #print(value["value"])
            self.data[axis["x"]][axis["y"]] = value["value"]
            self.img.setImage(self.data)

    def update_data_list(self, value):
        #print(value["x"])
        #print(value["y"])
        #self.p1.setXRange(0, 1000 - 1)
        if self.data is None:
            self.p1.setXRange(0, np.shape(value["y"])[0] - 1)
            self.data = np.expand_dims(value["y"], axis=0)
            self.p1.setYRange(0, np.shape(self.data)[0] - 1)
            x = np.linspace(0, np.shape(value["x"])[0] - 1, np.shape(value["x"])[0])
            strx = value["x"]
            strx = np.around(strx, 3)
            strx = strx.astype(str)
            x_show = []
            strx_show = []
            if len(x) > 10:
                a = len(x) // 10
                i = 0
                while i < len(x):
                    x_show.append(x[i])
                    strx_show.append(strx[i])
                    i = i + a
            else:
                x_show = x
                strx_show = strx

            ticksx = [[i, j] for i, j in zip(x_show, strx_show)]
            self.p1.getAxis("bottom").setTicks([ticksx])

        else:
            c = np.expand_dims(value["y"], axis=0)
            self.data = np.concatenate((self.data, c))
            self.p1.setYRange(0, np.shape(self.data)[0] - 1)
            y = np.linspace(0, np.shape(self.data)[0] - 1, np.shape(self.data)[0])
            if len(y) > 10:
                y = np.linspace(0, np.shape(self.data)[0] - 1, 10)
                y = y.astype(int)
            stry = y.astype(str)
            ticksy = [[i, j] for i, j in zip(y, stry)]
            self.p1.getAxis("left").setTicks([ticksy])

        self.img.setImage(self.data.T)

    def set_title(self, title):
        self.setWindowTitle(title)

    def load_image_in_file(self):
        file_path = QFileDialog.getOpenFileName(self, "open file dialog", "./",
                                                "Tif files(*.tif; *.tiff);;All files(*.*)")
        try:
            image = Image.open(file_path[0])
        except:
            print("Can not open the image")
        else:
            image = np.array(image).T
            self.img.setImage(image)

    def save_image_to_file(self):
        file_path = QFileDialog.getSaveFileName(self, "save file dialog", "./",
                                                "Tif files(*.tif; *.tiff);;All files(*.*)")
        try:
            data = Image.fromarray(self.img.image).save(file_path[0]+".tif")
        except:
            print("Can not save the image")
            return



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Plot2DWidget()
    ex.resize(500, 300)
    ex.show()
    sys.exit(app.exec_())
