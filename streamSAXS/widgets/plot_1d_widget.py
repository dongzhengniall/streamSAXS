import os
import sys
from enum import Enum

import pyqtgraph as pg
import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, Qt, QSize
from PyQt5.QtGui import QColor, QIcon, QFont
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QToolBar, \
    QLabel, QSizePolicy, QGridLayout
from pyqtgraph import mkPen, mkBrush
from pyqtgraph.graphicsItems.ViewBox import ViewBox

ZOOMING = 1
SELECT = 2
SELECT_POLYGON = 3
PANNING = 4

SELECT_SQUARE = 123
SELECT_POLYGON = 124

# view types
INDIVIDUAL = 0
AVERAGE = 1

# selections
SELECTNONE = 0
SELECTONE = 1
SELECTMANY = 2

MAX_INSTANCES_DRAWN = 1000
MAX_THICK_SELECTED = 10
NAN = float("nan")

# distance to the first point in pixels that finishes the polygon
SELECT_POLYGON_TOLERANCE = 10

CURVECOLORBR_SET = [QColor(200, 0, 0), 'b', 'g', 'r', 'y']


class InteractiveViewBox(ViewBox):
    def __init__(self, graph):
        ViewBox.__init__(self, enableMenu=False)
        self.setMenuEnabled(False)
        self.gragh = graph
        self.setMouseMode(self.PanMode)
        self.zoomstartpoint = None
        self.current_selection = None
        self.action = PANNING
        self.y_padding = 0.02
        self.x_padding = 0

        # line for marking selection
        self.selection_line = pg.PlotCurveItem()
        self.selection_line.setPen(pg.mkPen(color=QColor('black'), width=2))
        self.selection_line.setZValue(1e9)
        self.selection_line.hide()
        self.addItem(self.selection_line, ignoreBounds=True)

        # yellow marker for ending the polygon
        self.selection_poly_marker = pg.ScatterPlotItem()
        self.selection_poly_marker.setPen(pg.mkPen(color=QColor('yellow'), width=2))
        self.selection_poly_marker.setSize(SELECT_POLYGON_TOLERANCE * 2)
        self.selection_poly_marker.setBrush(None)
        self.selection_poly_marker.setZValue(1e9 + 1)
        self.selection_poly_marker.hide()
        self.selection_poly_marker.mouseClickEvent = lambda x: x  # ignore mouse clicks
        self.addItem(self.selection_poly_marker, ignoreBounds=True)

        # self.sigRangeChanged.connect(self.resized)
        # self.sigResized.connect(self.resized)
        self.tiptexts = None

    def mouseMovedEvent(self, ev):  # not a Qt event!
        if self.action == ZOOMING and self.zoomstartpoint:
            pos = self.mapFromView(self.mapSceneToView(ev))
            self.updateScaleBox(self.zoomstartpoint, pos)

    def cancel_zoom(self):
        self.setMouseMode(self.PanMode)
        self.rbScaleBox.hide()
        self.zoomstartpoint = None
        self.action = PANNING
        self.unsetCursor()

    def set_mode_panning(self):
        self.cancel_zoom()
        self.enableAutoRange()

    def set_mode_zooming(self):
        self.set_mode_panning()
        self.setMouseMode(self.RectMode)
        self.action = ZOOMING
        self.setCursor(Qt.CrossCursor)

    def enableAutoRange(self, axis=None, enable=True, x=None, y=None):
        super().enableAutoRange(axis=axis, enable=False, x=x, y=y)

    def enableAutoRangeTrue(self, axis=None, enable=True, x=None, y=None):  ##########
        super().enableAutoRange(axis=axis, enable=True, x=x, y=y)


class InteractiveViewBoxC(InteractiveViewBox):

    def wheelEvent(self, ev, axis=None):
        # separate axis handling with modifier keys
        if axis is None:
            axis = 1 if ev.modifiers() & Qt.ControlModifier else 0
        super().wheelEvent(ev, axis=axis)


class CurvePlot(QWidget):
    limits_changed = pyqtSignal()

    def __init__(self, parent=None):
        super(CurvePlot, self).__init__(parent)
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        self.setContentsMargins(0, 0, 0, 0)
        # self.plotview = pg.PlotWidget(background="w", viewBox=InteractiveViewBoxC(self))
        self.plotview = pg.PlotWidget(viewBox=InteractiveViewBoxC(self))
        self.plotview.getPlotItem().addLegend()
        self.plot = self.plotview.getPlotItem()
        self.plot.hideButtons()  # hide the autorange button
        self.plot.setDownsampling(auto=True, mode="peak")
        self._curves = {}
        self._current_vline = None

        self.markings = []
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.plot.scene().sigMouseMoved.connect(self.mouse_moved_viewhelpers)
        self.plot.scene().sigMouseMoved.connect(self.plot.vb.mouseMovedEvent)

        # interface settings
        self.markclosest = True  # mark
        self.crosshair = True
        self.log = True
        self.init = True

        # ----------------QToolBar---------------------------------------
        self.navbar = QToolBar()
        self.navbar.setIconSize(QSize(30, 30))
        self.navbar.setStyleSheet("font-size:25px;")
        self.navbar.addAction(QIcon(os.getcwd()+'/xrd/ui/icons/button_grid.png'),
                              "Show grid", self.grid_changed)
        self.navbar.addAction(QIcon(os.getcwd()+'/xrd/ui/icons/button_big.png'),
                              "Zoom in", self.plot.vb.set_mode_zooming)
        self.navbar.addAction(QIcon(os.getcwd()+'/xrd/ui/icons/button_hand.png'),
                              "move", self.plot.vb.set_mode_panning)
        self.navbar.addAction(QIcon(os.getcwd()+'/xrd/ui/icons/button_fount.png'),
                              "auto", self.plot.vb.enableAutoRangeTrue)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.navbar.addWidget(spacer)
        self.axis_label = QLabel("")
        self.navbar.addWidget(self.axis_label)
        vbox = QVBoxLayout()
        vbox.setSpacing(0)
        vbox.setContentsMargins(10, 10, 10, 10)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.navbar)
        vbox.addWidget(self.plotview)
        self.setLayout(vbox)
        # -------------------------------------------------------------------

        self.show_grid = False
        self.grid_changed()
        self.class_name_old = None

    def set_log(self):
        self.log = not self.log

    def clear(self):
        self.init = True

    def init_plot_item(self, plot):
        # curve style
        if not self._curves == {}:
            for curves_id in list(self._curves.keys()):
                self.remove_curve(curve_id=curves_id)
            self._curves = {}

        if isinstance(plot["data"], dict):
            curve_plot = {"style": "line", "line_style": Qt.SolidLine, "symbol": None, "color": "b",
                          "legend": None, "width": 2}
            curve_plot.update(plot["data"])
            self.add_curve(curve_id="default", curve_name=curve_plot["legend"], curve_color=curve_plot["color"],
                           curve_style=curve_plot["style"], curve_symbol=curve_plot["symbol"],
                           curve_width=curve_plot["width"], line_style=curve_plot["line_style"])
        else:
            for index, line in enumerate(plot["data"]):
                curve_plot = {"style": "line", "line_style": Qt.SolidLine, "symbol": None,
                              "color": CURVECOLORBR_SET[index], "legend": None, "width": 1}
                curve_plot.update(line)
                self.add_curve(curve_id=line["name"], curve_name=curve_plot["legend"],
                               curve_color=curve_plot["color"],
                               curve_style=curve_plot["style"], curve_symbol=curve_plot["symbol"],
                               curve_width=curve_plot["width"], line_style=curve_plot["line_style"])

        # label
        if "label" in plot:
            if isinstance(plot["label"]["xlabel"], Enum):
                self.set_label("bottom", plot["label"]["xlabel"].value)
            else:
                self.set_label("bottom", plot["label"]["xlabel"])
            if isinstance(plot["label"]["ylabel"], Enum):
                self.set_label("left", plot["label"]["ylabel"].value)
            else:
                self.set_label("left", plot["label"]["ylabel"])
        else:
            location = ["left", "right", "top", "bottom"]
            for l in location:
                self.set_label(l, None)

    def update_data_all(self, plot):
        if self.init:
            self.init = False
            self.init_plot_item(plot)
        self.update_data(plot)
        # update title
        if "title" in plot:
            self.plot.setTitle(str(plot["title"]))
        else:
            self.plot.setTitle("")

    def update_data(self, plot):
        # update curve
        if isinstance(plot["data"], dict):
            if "style" in plot["data"] and plot["data"]["style"] == "Vline":
                self.set_line_values(curve_id="default", data=plot["data"]["x"])
            elif "style" in plot["data"] and plot["data"]["style"] == "Hline":
                self.set_line_values(curve_id="default", data=plot["data"]["y"])
            else:
                self.set_values(curve_id="default", data_x=plot["data"]["x"], data_y=plot["data"]["y"])
        else:
            for line in plot["data"]:
                if line["style"] == "Vline":
                    self.set_line_values(curve_id=line["name"], data=line["x"])
                elif line["style"] == "Hline":
                    self.set_line_values(curve_id=line["name"], data=line["y"])
                else:
                    self.set_values(curve_id=line["name"], data_x=line["x"], data_y=line["y"])

    def set_label(self, location, label, units=None):
        self.plot.setLabel(location, label, units=units)

    def grid_changed(self):
        self.show_grid = not self.show_grid
        self.grid_apply()

    def grid_apply(self):
        self.plot.showGrid(self.show_grid, self.show_grid)

    def mouse_moved_viewhelpers(self, pos):
        if self.plot.vb.sceneBoundingRect().contains(pos):
            mousePoint = self.plot.vb.mapSceneToView(pos)
            posx, posy = mousePoint.x(), mousePoint.y()
            labels = str(round(posx, 4)) + "   " + str(round(posy, 4))
            self.axis_label.setText(labels)

    def add_curve(self, curve_id, curve_name=None, curve_color=QColor('blue'), curve_style="line", curve_symbol=None,
                  curve_width=1, line_style=Qt.SolidLine):
        # this adds the item to the plot and legend
        if curve_style == "scatter":
            plot = self.plot.plot(name=curve_name, pen=None, symbol=curve_symbol, symbolPen=mkPen(curve_color),
                                  symbolBrush=mkBrush(curve_color), symbolSize=int(curve_width))
        elif curve_style in ["line", "Vline", "Hline"]:
            pen = mkPen(curve_color, width=int(curve_width), style=line_style)
            if curve_style == "line":
                plot = self.plot.plot(name=curve_name, pen=pen)
            elif curve_style == "Vline":
                plot = self.plot.addLine(x=None, y=None, z=None, angle=90, pen=pen)
            else:
                plot = self.plot.addLine(x=None, y=None, z=None, pen=pen)

        self._curves[curve_id] = plot

    def remove_curve(self, curve_id):
        if curve_id in self._curves:
            self.plot.removeItem(self._curves[curve_id])
            del self._curves[curve_id]
            self._update_legend()

    def _update_legend(self):
        # clear and rebuild legend (there is no remove item method for the legend...)
        self.plot.clear()
        # self.plot.getPlotItem().legend.items = []
        for curve in self._curves.values():
            self.plot.addItem(curve)
        if self._current_vline:
            self.plot.addItem(self._current_vline)

    def set_values(self, curve_id, data_x, data_y):
        curve = self._curves[curve_id]
        curve.setData(data_x, data_y)

    def set_line_values(self, curve_id, data):
        curve = self._curves[curve_id]
        curve.setValue(data)

    def vline(self, x, color):
        if self._current_vline:
            self.plot.removeItem(self._current_vline)
        self._current_vline = self.plot.addLine(x=x, pen=color)


class Plot1dParameter(QWidget):
    def __init__(self, parent=None):
        super(Plot1dParameter, self).__init__(parent)
        main_layout = QVBoxLayout()
        self.parameter = QWidget()
        parameter_layout = QGridLayout()
        max_value_label = QLabel('max value:')
        max_value_label.setFont(QFont("Roman times", 15))
        self.max_value_edit = QLabel()
        self.max_value_edit.setFont(QFont("Roman times", 15))
        parameter_layout.addWidget(max_value_label, 0, 0, 1, 1)
        parameter_layout.addWidget(self.max_value_edit, 0, 1, 1, 1)
        self.parameter.setLayout(parameter_layout)
        self.plot1d = CurvePlot()
        main_layout.addWidget(self.parameter)
        main_layout.addWidget(self.plot1d)
        self.setLayout(main_layout)
        self.add_curve(curve_id=0)

    def add_curve(self, curve_id):
        plot = {'data': [{'name': curve_id, 'style': 'line', 'color': 'b', 'width': '2'}],
                'label': {'xlabel': "Distance(pixels)", 'ylabel': 'Intensity(ADUs)'}}
        self.plot1d.init_plot_item(plot)

    def set_values(self, curve_id, data_x, data_y):
        self.plot1d.set_values(curve_id, data_x, data_y)
        self.max_value_edit.setText(str(max(data_y)))

    def update_roi_plot(self, data_x, data_y):
        self.set_values(0, data_x, data_y)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    plot_channel_1 = CurvePlot()
    plot_widgets = QWidget()
    layout = QVBoxLayout()
    layout.addWidget(plot_channel_1)
    plot_widgets.setLayout(layout)

    plot_channel_1.add_curve(curve_id=0, curve_name="111")

    x = np.arange(1000)
    y = np.random.normal(size=(1000))
    y1 = np.random.normal(size=(1000))

    ptr = 1


    def update():
        global ptr
        if ptr <= 1000:
            plot_channel_1.set_values(0, x[:ptr], y[:ptr])
            ptr += 1


    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(100)

    # # ex.vline(1, QColor('black'))
    plot_widgets.resize(600, 500)
    plot_widgets.show()
    sys.exit(app.exec_())
