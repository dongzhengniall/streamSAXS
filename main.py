# -*- coding: utf-8 -*-
import os
from collections import OrderedDict

from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys

from PyQt5.QtWidgets import QMainWindow, QDockWidget, QApplication, QAction, QInputDialog, QMessageBox, qApp

import uuid

from plugin.XRD import IntegrationPlot, SinglePeakFit, TParameters, SinglePeakFitPlot
from widgets.plot_2d_widget import Plot2DWidget
from processing_widget import ProcessingOperateWidget
from widgets.visualizer_2d_widget import Visualizer2DWidget

###############
import pyFAI
from pyFAI.gui.CalibrationWindow import CalibrationWindow
from pyFAI.gui.CalibrationContext import CalibrationContext
from silx.gui import qt
from widgets.plot_1d_widget import CurvePlot

from plugin.Calibration import DetectorCalibrationPyFAI
from plugin.IO import LoadH5Data
from plugin.Integration import IntegrateAzimuthal, IntegrateRadial
from plugin.Masking import UserDefinedMask2D, ThresholdMask2D


class MainWidget(QMainWindow):
    switch_signal = pyqtSignal(int, int, int, int)

    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)
        self.setWindowTitle("高能同步辐射光源")
        self.setWindowIcon(QIcon(os.getcwd()+"/ui/icons/icon.png"))

        # self.statusBar()
        # menubar = self.menuBar()
        # menubar.setNativeMenuBar(False)
        # file_menu = menubar.addMenu('File')
        # view_menu = menubar.addMenu('View')
        # help_menu = menubar.addMenu('Help')
        #
        # # 给menu创建一个Action
        # exit_action = QAction(QIcon('exit.png'), 'Exit', self)
        # exit_action.setStatusTip('Exit Application')
        # exit_action.triggered.connect(qApp.quit)
        # # 将这个Action添加到fileMenu�?
        # file_menu.addAction(exit_action)
        #
        # # 给menu创建一个Action
        # help_action = QAction(QIcon('exit.png'), 'Help', self)
        # help_action.setStatusTip('Help')
        # help_action.triggered.connect(self.load_html)
        # # 将这个Action添加到fileMenu�?
        # help_menu.addAction(help_action)
        #
        # # 给menu创建一个Action
        # view_action = QAction('View', self)
        # view_action.triggered.connect(self.show_view)
        # # 将这个Action添加到fileMenu�?
        # view_menu.addAction(view_action)
        # edit = view_menu.addMenu('1d plot')
        # edit.addAction(view_action)
        # edit.addAction(view_action)

        self.processing_operate_widget = ProcessingOperateWidget()
        self.setDockNestingEnabled(True)

        self.plot1d_widget_dict = OrderedDict()
        self.plot1d_dock_dict = OrderedDict()
        self.visualizer2d_widget_dict = OrderedDict()
        self.visualizer2d_dock_dict = OrderedDict()
        self.plot2d_widget_dict = OrderedDict()
        self.plot2d_dock_dict = OrderedDict()

        self.dock_name = []
        self.add_plot1d_widget("I(q)")
        self.add_plot1d_widget("I(chi)")
        #self.add_visualizer2d_widget("2D integration")
        self.add_plot2d_widget("2D plot")
        self.add_plot2d_widget("2D")

        # put the widget text name to processing widget to select
        self.processing_operate_widget.processing_widget.plot1d_widget_dict = self.plot1d_widget_dict
        self.processing_operate_widget.processing_widget.plot2d_widget_dict = self.plot2d_widget_dict
        self.processing_operate_widget.processing_widget.visualizer2d_widget_dict = self.visualizer2d_widget_dict
        # pyqt signal---------------------------------------------
        self.processing_operate_widget.processing_widget.signal_add_plot1d.connect(self.add_plot1d_widget)
        self.processing_operate_widget.processing_widget.signal_add_plot2d.connect(self.add_plot2d_widget)
        self.processing_operate_widget.processing_widget.signal_add_visualizer2d.connect(self.add_visualizer2d_widget)

        self.processing_operate_widget.processing_widget.signal_2DV.connect(self.visualizer2d_connect_widget)
        self.processing_operate_widget.processing_widget.signal_1DP.connect(self.plot1d_connect_widget)
        self.processing_operate_widget.processing_widget.signal_2DP.connect(self.plot2d_connect_widget)

        # processing widget
        processing_dock = QDockWidget(self.tr("Processing"), self)
        processing_dock.setFeatures(QDockWidget.DockWidgetMovable)
        processing_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        processing_dock.setWidget(self.processing_operate_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, processing_dock)

        # PyFAI Calibration Parameter configuration
        pyFAI.resources.silx_integration()
        settings = qt.QSettings(qt.QSettings.IniFormat, qt.QSettings.UserScope, "pyfai", "pyfai-calib2", None)
        context = CalibrationContext(settings)
        context.restoreSettings()
        self.calibration_window = CalibrationWindow(context)
        self.calibration_window.setMinimumHeight(350)

        calibration_dock = QDockWidget(self.tr("Calibration"), self)
        calibration_dock.setFeatures(QDockWidget.DockWidgetMovable)
        calibration_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        calibration_dock.setWidget(self.calibration_window)
        self.addDockWidget(Qt.LeftDockWidgetArea, calibration_dock)

        self.typesetting_plot1d()
        self.typesetting_visualizer2d()
        self.typesetting_plot2d()
        
        self.processing_operate_widget.processing_widget.processing_list.add_step_in_data("Load Data File",
                                                                                          LoadH5Data(), [])
        self.processing_operate_widget.processing_widget.processing_list.add_step_in_data(
            "Detector Calibration via PyFAI", DetectorCalibrationPyFAI(), [1])
        self.processing_operate_widget.processing_widget.processing_list.add_step_in_data(
            "Threshold Mask 2D", ThresholdMask2D(), [2])
        self.processing_operate_widget.processing_widget.processing_list.add_step_in_data(
            "Azimuthal Integration", IntegrateAzimuthal(), [3])
        # self.processing_operate_widget.processing_widget.processing_list.add_step_in_data(
        #     "Radial Integration", IntegrateRadial(), [3])
        # self.processing_operate_widget.processing_widget.processing_list.add_step_in_data(
        #     "Integration Plot", IntegrationPlot(), [4])

        self.processing_operate_widget.processing_widget.processing_list.add_step_in_data(
            "SinglePeakFit", SinglePeakFit(), [4])
        self.processing_operate_widget.processing_widget.processing_list.add_step_in_data(
            "T-Parameters", TParameters(), [5])
        self.processing_operate_widget.processing_widget.processing_list.add_step_in_data(
            "SinglePeakFitPlot", SinglePeakFitPlot(), [5])

        self.processing_operate_widget.processing_widget.processing_list[3].step_connect_widget = list(self.plot1d_widget_dict.keys())[0]
        self.processing_operate_widget.processing_widget.processing_list[4].step_connect_widget = \
        list(self.plot1d_widget_dict.keys())[1]
        self.processing_operate_widget.processing_widget.processing_list[5].step_connect_widget = \
            list(self.plot2d_widget_dict.keys())[0]
        self.processing_operate_widget.processing_widget.processing_list[6].step_connect_widget = \
            list(self.plot2d_widget_dict.keys())[1]
        self.processing_operate_widget.processing_widget.update_steps_tableWidget()

    def load_html(self):
        print(QFileInfo(".help.html").absoluteFilePath())
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(QFileInfo("doc_help/help.html").absoluteFilePath()))

    def show_view(self):
        print(self.plot1d_widget_dict)

    def change_window_name(self, type, id):
        text, ok = QInputDialog.getText(self, '窗口改名', '请输入修改后的名字：')
        if ok and text != "":
            if text not in self.dock_name:
                if type == "plot1d":
                    old_name = self.plot1d_dock_dict[id]["name"]
                    self.plot1d_dock_dict[id]["dock"].setWindowTitle(self.tr(text))
                    self.plot1d_dock_dict[id]["name"] = text
                    self.plot1d_widget_dict[id]["name"] = text
                    self.processing_operate_widget.processing_widget.plot1d_widget_dict = self.plot1d_widget_dict
                elif type == "visualizer2d":
                    old_name = self.visualizer2d_dock_dict[id]["name"]
                    self.visualizer2d_dock_dict[id]["dock"].setWindowTitle(self.tr(text))
                    self.visualizer2d_dock_dict[id]["name"] = text
                    self.visualizer2d_widget_dict[id]["name"] = text
                    self.processing_operate_widget.processing_widget.visualizer2d_widget_dict = self.visualizer2d_widget_dict
                self.dock_name.remove(old_name)
                self.dock_name.append(text)
            else:
                msg_box = QMessageBox(QMessageBox.Warning, '警告', 'the name is exist, please change the name.')
                msg_box.exec_()

    def window_show(self, x, y, width, height):
        if x == 0 and y == 0 and width == 0 and height == 0:
            self.showMaximized()
        else:
            self.showNormal()
            self.move(x, y)
            self.resize(width, height)
        self.show()

    def window_change_triggered(self, window_name):
        if window_name.text() == "window2":
            if self.isMaximized():
                self.switch_signal.emit(0, 0, 0, 0)
            else:
                self.switch_signal.emit(self.x(), self.y(), self.width(), self.height())
            self.hide()

    def plot1d_connect_widget(self, widget_id, plot):
        if widget_id:
            self.plot1d_widget_dict[widget_id]["widget"].update_data_all(plot)

    def plot2d_connect_widget(self, widget_id, plot):
        if widget_id:
            self.plot2d_widget_dict[widget_id]["widget"].update_data_all(plot)

    def visualizer2d_connect_widget(self, widget_id, plot):
        if widget_id:
            self.visualizer2d_widget_dict[widget_id]["widget"].update_data(plot)

    def add_plot2d_widget(self, image_name):
        if image_name not in self.dock_name:
            uid = str(uuid.uuid1())
            widget = {"name": image_name, "widget": Plot2DWidget()}
            self.plot2d_widget_dict[uid] = widget
            self.plot2d_widget_dict[uid]["widget"].navbar.setContextMenuPolicy(Qt.CustomContextMenu)
            self.plot2d_widget_dict[uid]["widget"].navbar.customContextMenuRequested.connect(
                lambda: self.change_window_name("plot2d", uid))
            dock = {"name": image_name, "dock": QDockWidget(self.tr(image_name), self)}
            self.plot2d_dock_dict[uid] = dock
            self.plot2d_dock_dict[uid]["dock"].setWidget(self.plot2d_widget_dict[uid]["widget"])
            self.plot2d_dock_dict[uid]["dock"].setMinimumSize(200, 200)
            self.processing_operate_widget.processing_widget.plot2d_widget_dict = self.plot2d_widget_dict
            self.typesetting_plot1d()
            self.typesetting_visualizer2d()
            self.dock_name.append(image_name)
        else:
            msg_box = QMessageBox(QMessageBox.Warning, '警告', 'The name is exist, please change the name.')
            msg_box.exec_()

    def add_plot1d_widget(self, image_name):
        if image_name not in self.dock_name:
            uid = str(uuid.uuid1())
            widget = {"name": image_name, "widget": CurvePlot()}
            self.plot1d_widget_dict[uid] = widget
            self.plot1d_widget_dict[uid]["widget"].navbar.setContextMenuPolicy(Qt.CustomContextMenu)
            self.plot1d_widget_dict[uid]["widget"].navbar.customContextMenuRequested.connect(
                lambda: self.change_window_name("plot1d", uid))
            dock = {"name": image_name, "dock": QDockWidget(self.tr(image_name), self)}
            self.plot1d_dock_dict[uid] = dock
            self.plot1d_dock_dict[uid]["dock"].setWidget(self.plot1d_widget_dict[uid]["widget"])
            self.plot1d_dock_dict[uid]["dock"].setMinimumSize(200, 200)
            self.processing_operate_widget.processing_widget.plot1d_widget_dict = self.plot1d_widget_dict
            self.typesetting_plot1d()
            self.typesetting_visualizer2d()
            self.dock_name.append(image_name)
        else:
            msg_box = QMessageBox(QMessageBox.Warning, '警告', '111the name is exist, please change the name.')
            msg_box.exec_()

    def typesetting_plot1d(self):
        column = 3
        i = 0
        widget_list = [None] * column
        for id in self.plot1d_dock_dict.keys():
            self.addDockWidget(Qt.RightDockWidgetArea, self.plot1d_dock_dict[id]["dock"])
            if i < column:
                if i > 0:
                    self.splitDockWidget(widget_list[i - 1], self.plot1d_dock_dict[id]["dock"], Qt.Horizontal)
                widget_list[i] = self.plot1d_dock_dict[id]["dock"]
            else:
                self.splitDockWidget(widget_list[i % column], self.plot1d_dock_dict[id]["dock"], Qt.Vertical)
                widget_list[i % column] = self.plot1d_dock_dict[id]["dock"]
            i = i + 1

    def add_visualizer2d_widget(self, image_name):
        if image_name not in self.dock_name:
            uid = str(uuid.uuid1())
            widget = {"name": image_name, "widget": Visualizer2DWidget()}
            self.visualizer2d_widget_dict[uid] = widget
            self.visualizer2d_widget_dict[uid]["widget"].navbar.setContextMenuPolicy(Qt.CustomContextMenu)
            self.visualizer2d_widget_dict[uid]["widget"].navbar.customContextMenuRequested.connect(
                lambda: self.change_window_name("visualizer2d", uid))
            dock = {"name": image_name, "dock": QDockWidget(self.tr(image_name), self)}
            self.visualizer2d_dock_dict[uid] = dock
            self.visualizer2d_dock_dict[uid]["dock"].setWidget(self.visualizer2d_widget_dict[uid]["widget"])
            self.processing_operate_widget.processing_widget.visualizer2d_widget_dict = self.visualizer2d_widget_dict
            self.typesetting_visualizer2d()
            self.dock_name.append(image_name)
        else:
            msg_box = QMessageBox(QMessageBox.Warning, '警告', '222the name is exist, please change the name.')
            msg_box.exec_()

    def typesetting_visualizer2d(self):
        column = 2
        i = 0
        first_dock = None
        last_dock = None
        for id in self.visualizer2d_dock_dict.keys():
            self.addDockWidget(Qt.LeftDockWidgetArea, self.visualizer2d_dock_dict[id]["dock"])
            if first_dock is None:
                first_dock = self.visualizer2d_dock_dict[id]["dock"]
                last_dock = self.visualizer2d_dock_dict[id]["dock"]
            if i > 0:
                if column > i:
                    self.splitDockWidget(last_dock, self.visualizer2d_dock_dict[id]["dock"], Qt.Horizontal)
                    last_dock = self.visualizer2d_dock_dict[id]["dock"]
                else:
                    self.tabifyDockWidget(first_dock, self.visualizer2d_dock_dict[id]["dock"])
            i = i + 1

    def typesetting_plot2d(self):
        column = 2
        i = 0
        first_dock = None
        last_dock = None
        for id in self.plot2d_dock_dict.keys():
            self.addDockWidget(Qt.RightDockWidgetArea, self.plot2d_dock_dict[id]["dock"])
            if first_dock is None:
                first_dock = self.plot2d_dock_dict[id]["dock"]
                last_dock = self.plot2d_dock_dict[id]["dock"]
            if i > 0:
                if column > i:
                    self.splitDockWidget(last_dock, self.plot2d_dock_dict[id]["dock"], Qt.Horizontal)
                    last_dock = self.plot2d_dock_dict[id]["dock"]
                else:
                    self.tabifyDockWidget(first_dock, self.plot2d_dock_dict[id]["dock"])
            i = i + 1


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWidget()
    main.showMaximized()
    main.show()
    app.exec_()
