import math
import os
import sys
import copy
import numpy as np
import pyqtgraph as pg
from PIL import Image
from PyQt5.QtWidgets import (QToolBar, QAction, QPushButton)
from PyQt5.QtCore import QSize, QRectF, Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QIntValidator
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QLabel, QSizePolicy, QLineEdit, QApplication,
                             QFileDialog, QMenu)


class Visualizer2DWidget(QWidget):
    roi_line_change_signal = pyqtSignal(list, list)

    def __init__(self):
        super().__init__()
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        pg.setConfigOptions(imageAxisOrder='row-major')

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.navbar = QToolBar()
        self.navbar.setIconSize(QSize(30, 30))
        self.navbar.setStyleSheet("font-size:25px;")
        self.navbar.addAction(QIcon(os.getcwd()+'/xrd/ui/icons/load.png'), "Load Image in File", self.load_image_in_file)
        # self.navbar.addAction(QIcon('widgets/ui/icons/save.png'), "Save Image To File")
        self.navbar.addSeparator()

        # ROI Action---------------------------------------
        self.roi_action = QAction(QIcon(os.getcwd()+'/xrd/ui/icons/button_line.png'), "ROI Line")
        self.roi_action.setCheckable(True)
        self.navbar.addAction(self.roi_action)
        self.roi = False
        self.start = None
        self.line_roi_item = None
        self.pixel_list = None
        self.roi_x = []

        # Crop Action----------------------------------------
        crop_menu = QMenu(self)
        crop_action = crop_menu.addAction(QIcon('ui/icons/crop.png'), "crop image", self.add_crop_roi)
        crop_panel = QMenu(self)
        crop_action.setMenu(crop_panel)
        self.crop_range_edit = {}
        layout = QGridLayout()
        for i, range_name in enumerate(["minx", "maxx", "miny", "maxy"]):
            self.crop_range_edit[range_name] = QLineEdit()
            self.crop_range_edit[range_name].setValidator(QIntValidator())
            self.crop_range_edit[range_name].setEnabled(False)
            self.crop_range_edit[range_name].textChanged.connect(self.crop_edit_change)
            layout.addWidget(self.crop_range_edit[range_name], i // 2, 2 * (i % 2) + 1)
        layout.addWidget(QLabel("X range:"), 0, 0)
        layout.addWidget(QLabel("Y range:"), 1, 0)
        layout.addWidget(QLabel("-"), 0, 2)
        layout.addWidget(QLabel("-"), 1, 2)
        crop_panel.setLayout(layout)
        self.navbar.addAction(crop_action)
        self.crop_roi = None  # crop roi widget
        self.crop_range = [0, 10, 0, 10]  # crop range [xmin, xmax, ymin, ymax]
        self.crop_zero = [0, 0]
        self.show_range = None

        # Auto levels Action----------------------------------------
        level_menu = QMenu(self)
        self.level_action = level_menu.addAction(QIcon(os.getcwd()+'/xrd/ui/icons/button_range.png'), "Level")
        self.level_action.setCheckable(True)
        level_panel = QMenu(self)
        self.level_action.setMenu(level_panel)
        layout = QGridLayout()
        layout.addWidget(QLabel("level(min):"), 0, 0)
        self.level_min_edit = QLineEdit()
        self.level_min_edit.setValidator(QIntValidator(0, 100000))
        layout.addWidget(self.level_min_edit, 0, 1)
        layout.addWidget(QLabel("level(max):"), 1, 0)
        self.level_max_edit = QLineEdit()
        self.level_max_edit.setValidator(QIntValidator(0, 100000))
        layout.addWidget(self.level_max_edit, 1, 1)
        self.level_button = QPushButton("Apply")
        layout.addWidget(self.level_button, 2, 1)
        level_panel.setLayout(layout)
        self.navbar.addAction(self.level_action)
        self.level_button.clicked.connect(self.set_level)
        self.layout.addWidget(self.navbar)
        self.auto_level = True

        # axis label--------------------------------------------------
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.navbar.addWidget(spacer)
        self.axis_label = QLabel("")
        self.navbar.addWidget(self.axis_label)

        self.navbar.actionTriggered[QAction].connect(self.navbar_triggered)
        self.layout.addWidget(self.navbar)

        self.ticksx = None
        self.ticksy = None

        # imageview---------------------------------------------------
        self.plot_item = pg.PlotItem()
        self.image_view = pg.ImageView(view=self.plot_item)
        self.layout.addWidget(self.image_view)
        self.image_view.setPredefinedGradient('thermal')
        self.plot_item.scene().sigMouseMoved.connect(self.mouse_moved_axies)
        self.plot_item.scene().sigMouseClicked.connect(self.set_roi_line)
        self.image = None

        self.init = True

    def navbar_triggered(self, name):
        if name.text() == "ROI Line":
            self.roi = not self.roi
            self.roi_action.setChecked(self.roi)
            if not self.roi and self.line_roi_item:
                self.plot_item.removeItem(self.line_roi_item)
                self.line_roi_item = None
        if name.text() == "Level":
            self.auto_level = not self.auto_level
            self.level_action.setChecked(not self.auto_level)
            if not self.auto_level:
                self.set_level()

    def set_level(self):
        if self.level_max_edit.text().isdecimal() and self.level_min_edit.text().isdecimal():
            max_value = int(self.level_max_edit.text())
            min_value = int(self.level_min_edit.text())
            if min_value > max_value:
                self.level_max_edit.setText(str(min_value))
                self.level_min_edit.setText(str(max_value))
                self.image_view.setLevels(max_value, min_value)
            else:
                self.image_view.setLevels(min_value, max_value)

    # set the roi line on imageview
    # signal:position list of the roi handles
    def set_roi_line(self, event):
        def euclideanDistance(p1, p2):
            return math.sqrt(((p1[0] - p2[0]) ** 2) + ((p1[1] - p2[1]) ** 2))

        def get_pixel(x1, y1, x2, y2):
            self.pixel_list = []
            self.value_list = []
            self.roi_x = []
            xDis = x2 - x1
            yDis = y2 - y1
            maxstep = int(abs(xDis)) if abs(xDis) > abs(yDis) else int(abs(yDis))
            xUnitstep = xDis / maxstep
            yUnitstep = yDis / maxstep
            x = x1
            y = y1
            for k in range(maxstep):
                x = x + xUnitstep
                y = y + yUnitstep
                if 0 < int(x) < self.image.shape[0] and 0 < int(y) < self.image.shape[1]:
                    self.pixel_list.append([int(x), int(y)])
                    self.roi_x.append(euclideanDistance([x1, y1], [x, y]))

        def roi_line_changed():
            handle1, handle2 = self.line_roi_item.getLocalHandlePositions()
            handle_list = ([(handle1[1].x(), handle1[1].y()), (handle2[1].x(), handle2[1].y())])
            if abs(handle_list[0][0] - handle_list[1][0]) + abs(handle_list[0][1] - handle_list[1][1]):
                get_pixel(handle_list[0][0], handle_list[0][1], handle_list[1][0], handle_list[1][1])
                self.get_roi_value()

        if self.roi and event.buttons() == Qt.LeftButton and self.image is not None \
                and self.plot_item.vb.sceneBoundingRect().contains(event.scenePos()):
            if self.line_roi_item:
                self.plot_item.removeItem(self.line_roi_item)
                self.line_roi_item = None

            mousePoint = self.plot_item.vb.mapSceneToView(event.scenePos())
            self.start = [mousePoint.x(), mousePoint.y()]
            self.line_roi_item = pg.LineSegmentROI([self.start, self.start], pen=pg.mkPen('g', width=2), movable=False)
            self.line_roi_item.sigRegionChanged.connect(roi_line_changed)
            self.plot_item.addItem(self.line_roi_item)

    def get_roi_value(self):
        if self.pixel_list and self.roi:
            value_list = []
            for p in self.pixel_list:
                value_list.append(self.image[p[0]][p[1]])
            self.roi_line_change_signal.emit(self.roi_x, value_list)

    def mouse_moved_axies(self, pos):
        if self.plot_item.vb.sceneBoundingRect().contains(pos):
            mousePoint = self.plot_item.vb.mapSceneToView(pos)
            posx, posy = mousePoint.x(), mousePoint.y()
            axisx = " "
            if self.ticksx and posx >= 0:
                for i in range(len(self.ticksx)):
                    if int(self.ticksx[i][0]) == int(posx):
                        axisx = round(self.ticksx[i][1], 3)
                        break
            axisy = " "
            if self.ticksy and posy >= 0:
                for i in range(len(self.ticksy)):
                    if int(self.ticksy[i][0]) == int(posy):
                        axisy = round(self.ticksy[i][1], 3)
                        break
            labels = "pixel:x=" + str(round(posx)) + " y=" + str(round(posy)) + \
                     "  axies:x=" + str(axisx) + " y=" + str(axisy)
            self.axis_label.setText(labels)

    def add_crop_roi(self):
        def new_region(roi):
            roi.addScaleHandle([1, 0.5], [0, 0.5])
            roi.addScaleHandle([0, 0.5], [1, 0.5])
            roi.addScaleHandle([0.5, 0], [0.5, 1])
            roi.addScaleHandle([0.5, 1], [0.5, 0])
            roi.addScaleHandle([1, 1], [0, 0])
            roi.addScaleHandle([0, 0], [1, 1])
            roi.setZValue(10)
            self.image_view.addItem(roi)

        if self.image is not None:
            if self.crop_roi is None:
                roi_range = [0, self.image.shape[0], 0, self.image.shape[1]]
                for i, range_name in enumerate(["minx", "maxx", "miny", "maxy"]):
                    self.crop_range_edit[range_name].setEnabled(True)
                    if self.crop_range_edit[range_name].text() != '':
                        roi_range[i] = int(self.crop_range_edit[range_name].text())

                bound = QRectF(0, 0, self.image.shape[0], self.image.shape[1])
                self.crop_roi = pg.ROI([0, 0], [max(0, roi_range[1] - roi_range[0]),
                                                max(0, roi_range[3] - roi_range[2])],
                                       maxBounds=bound, handlePen=pg.mkPen('r', width=2), pen=pg.mkPen('r', width=2),
                                       hoverPen=pg.mkPen('r', width=2), handleHoverPen=pg.mkPen('r', width=2))
                self.crop_roi.sigRegionChangeFinished.connect(self.crop_roi_change)
                new_region(self.crop_roi)
            else:
                for range_name in ["minx", "maxx", "miny", "maxy"]:
                    self.crop_range_edit[range_name].setEnabled(False)
                self.image_view.removeItem(self.crop_roi)
                self.show_range = copy.deepcopy(self.crop_range)
                self.crop_roi = None
                self.crop_zero = [self.show_range[0], self.show_range[2]]

    def crop_roi_change(self):
        self.crop_range_edit["minx"].setText(str(int(self.crop_roi.state["pos"][0]) + self.crop_zero[0]))
        self.crop_range_edit["miny"].setText(str(int(self.crop_roi.state["pos"][1]) + self.crop_zero[1]))
        self.crop_range_edit["maxx"].setText(
            str(int(self.crop_roi.state["pos"][0] + self.crop_roi.state["size"][0]) + self.crop_zero[0]))
        self.crop_range_edit["maxy"].setText(
            str(int(self.crop_roi.state["pos"][1] + self.crop_roi.state["size"][1]) + self.crop_zero[1]))

    def crop_edit_change(self, key):
        crop_limit = [[0, self.image.shape[0]], [0, self.image.shape[0]], [0, self.image.shape[1]],
                      [0, self.image.shape[1]]]
        for i, range_name in enumerate(["minx", "maxx", "miny", "maxy"]):
            if self.sender() == self.crop_range_edit[range_name]:
                if int(self.crop_range_edit[range_name].text()) < crop_limit[i][0]:
                    self.crop_range_edit[range_name].setText(str(crop_limit[i][0]))
                if int(self.crop_range_edit[range_name].text()) > crop_limit[i][1]:
                    self.crop_range_edit[range_name].setText(str(crop_limit[i][1]))
                self.crop_range[i] = int(self.crop_range_edit[range_name].text())
                break

    def load_image_in_file(self):
        file_path = QFileDialog.getOpenFileName(self, "open file dialog", "./",
                                                "Tif files(*.tif; *.tiff);;All files(*.*)")
        if file_path[0]:
            try:
                image = Image.open(file_path[0])
            except:
                print("Can not open the image")
            else:
                self.image = np.array(image)
                self.image_view.setImage(self.image, autoLevels=self.auto_level, autoRange=False)
                self.get_roi_value()
        else:
            print("Can not open the image")

    def clear(self):
        pass

    def init_plot_item(self, plot):
        if "label" in plot:
            if plot["label"]["ylabel"]:
                self.plot_item.setLabel("left", plot["label"]["ylabel"])
            else:
                self.plot_item.setLabel("left", "")
            if plot["label"]["xlabel"]:
                self.plot_item.setLabel("bottom", plot["label"]["xlabel"])
            else:
                self.plot_item.setLabel("bottom", "")
        else:
            location = ["left", "right", "top", "bottom"]
            for l in location:
                self.plot_item.setLabel(l, "")
        if "title" in plot:
            self.plot_item.setTitle(str(plot["message"]))
        else:
            self.plot_item.setTitle("")

        if plot["type"] == "2DXY":
            x = plot["data"]["x"]
            y = plot["data"]["y"]
            self.plot_item.setXRange(0, len(x) - 1)
            self.plot_item.setYRange(0, len(y) - 1)
            ox = np.linspace(0, len(x) - 1, len(x))
            oy = np.linspace(0, len(y) - 1, len(y))
            self.ticksx = [[i, round(j, 3)] for i, j in zip(ox, x)]
            ticksx_show = []
            if len(x) > 10:
                a = len(x) // 10
                i = 0
                while i < len(x):
                    ticksx_show.append(self.ticksx[i])
                    i = i + a
            else:
                ticksx_show = self.ticksx
            self.plot_item.getAxis("bottom").setTicks([ticksx_show])

            self.ticksy = [[i, round(j, 3)] for i, j in zip(oy, y)]
            ticksy_show = []
            if len(y) > 10:
                a = len(y) // 10
                i = 0
                while i < len(y):
                    ticksy_show.append(self.ticksy[i])
                    i = i + a
            else:
                ticksy_show = self.ticksy
            self.plot_item.getAxis("left").setTicks([ticksy_show])

    def update_image_data(self, image):
        self.image = image
        if self.show_range:
            self.image_view.setImage(self.image[self.show_range[0]:self.show_range[1],
                                           self.show_range[2]:self.show_range[3]], autoLevels=self.auto_level)
        else:
            self.image_view.setImage(self.image, autoLevels=self.auto_level)
        self.get_roi_value()

    def update_data(self, plot):
        if self.init:
            self.init = False
            self.init_plot_item(plot)
        if "title" in plot:
            self.plot_item.setTitle(str(plot["message"]))
        else:
            self.plot_item.setTitle("")
        if plot["type"] == "2DXY":
            image = plot["data"]["z"]
            self.update_image_data(image)
        else:
            image = plot["data"]
            self.update_image_data(image)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Visualizer2DWidget()
    ex.resize(600, 500)
    ex.show()
    sys.exit(app.exec_())
