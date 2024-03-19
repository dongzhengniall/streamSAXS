import inspect
import os

import filetype
import h5py
import sys
import numpy as np
from collections import OrderedDict
import time

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore

from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QInputDialog, QVBoxLayout, QFileDialog, QApplication
from PyQt5.QtGui import QIcon, QColor, QBrush
from PyQt5.QtCore import Qt, QSize, pyqtSignal

from dialogs.select_file_dialog import Select_file_dialog
from dialogs.select_1d_file_dialog import Select_1D_file_dialog
from plugin.Calibration import DetectorCalibrationPyFAI
from plugin.IO import LoadH5Data
from util.io import IoHdf5, IoFile
from util.plan_manager import PlanManager
from util.processing_sequence import ProcessingSequence
from ui.ui_processing_widget import Ui_processing_widget


class Runthread(QtCore.QThread):
    signal_1DP = pyqtSignal(str, dict)
    signal_2DV = pyqtSignal(str, dict)
    signal_2DP = pyqtSignal(str, dict)
    signal_thread_end = pyqtSignal()
    signal_thread_error = pyqtSignal()
    excepted = pyqtSignal(str)
    update_attribute_signal = pyqtSignal()

    def __init__(self, processing_list):
        super(Runthread, self).__init__()
        self.processing_list = processing_list
        self.init_flag = 1
        self.skip_step = []
        self.data_in_memory = [None] * len(self.processing_list)
        self.tiff_step = []
        self.stop_status = False
        self.save_data = None
        self.dataset_num = None

    def stop_work(self):
        self.stop_status = True

    def __del__(self):
        self.wait()

    def run(self):
        # load data in memory
        try:
            if self.init_flag:
                data_length = None
                self.save_path = []
                self.tiff_image_path = []
                for i, process in enumerate(self.processing_list):
                    if self.data_in_memory[i] is None:
                        self.data_in_memory[i] = {}

                    param_dict = process.attribute.get_params()
                    for key in param_dict:
                        if param_dict[key]["type"] in ["io"]:
                            if key == "file_info":
                                file_info = param_dict[key]["value"].split()
                                if "tiff" == file_info[1]:  # TIFF File
                                    self.tiff_image_path = []
                                    tiff_path = []
                                    if os.path.isdir(file_info[0]):
                                        for root, dirs, files in os.walk(file_info[0]):
                                            tiff_path = files
                                        for file in tiff_path:
                                            kind = filetype.guess(root + '/' + file)
                                            if kind and kind.extension:
                                                self.tiff_image_path.append(root + '/' + file)
                                            data_length = len(self.tiff_image_path)
                                        self.tiff_step.append(i)
                                    else:
                                        QMessageBox.about(self, "wrong", "Please input a tiff folder!")

                                elif "hdf5" == file_info[2]:  # HDF5 File
                                    self.data_in_memory[i][key] = IoHdf5.Load_H5_Data(file_info[0], file_info[1])
                                    length = self.data_in_memory[i][key].shape
                                    if len(length) > 1:
                                        if data_length is None:
                                            data_length = length[0]
                                        else:
                                            if not data_length == length[0]:
                                                QMessageBox.about(self, "wrong", "the data is not right")
                                                return
                                    self.skip_step.append(i)
                            else:#######################################################################
                                file_info = param_dict[key]["value"].split()
                                data_1d = {"x":IoHdf5.Load_H5_Data(file_info[0], file_info[1]),
                                           "y":IoHdf5.Load_H5_Data(file_info[0], file_info[2])}
                                self.data_in_memory[i][key] = data_1d
                                length = self.data_in_memory[i][key]["x"].shape
                                if len(length) > 1:
                                    if data_length is None:
                                        data_length = length[0]
                                    else:
                                        if not data_length == length[0]:
                                            QMessageBox.about(self, "wrong", "the data is not right")
                                            return
                                self.skip_step.append(i)

                        elif param_dict[key]["type"] in ["file"]:
                            file_info = param_dict[key]["value"]
                            if file_info:
                                image = IoFile.Load_File_Data(file_info)
                                if image is not None:
                                    self.data_in_memory[i][key] = image
                                    self.skip_step.append(i)
                                else:
                                    QMessageBox.about(self, "wrong", "load tiff file false!")
                                    return
                            else:
                                QMessageBox.about(self, "wrong", "load tiff file false!")
                        elif process.attribute.function_text == "Save Data":
                            self.save_path = param_dict["file_folder"]["value"]
                            self.dataset_num = process.step_input_number
                            self.save_data = {}
                            for m in range(len(self.dataset_num)):
                               self.save_data[self.dataset_num[m]] = None
                            self.skip_step.append(i)
                self.init_flag = 0
            # process data
            if data_length:  # data in memory
                for gen in range(data_length):
                    if self.stop_status:
                        break
                    steps_output_result = []
                    for i, process in enumerate(self.processing_list):
                        input_value = {}
                        if i in self.skip_step:
                            for key in self.data_in_memory[i]:
                                if process.attribute.get_params()[key]["type"] in ["io"]:
                                    if isinstance(self.data_in_memory[i][key], dict):
                                        input_value[key] = {}
                                        if self.data_in_memory[i][key]["x"].ndim == 1:
                                            input_value[key]["x"] = self.data_in_memory[i][key]["x"][gen]
                                            input_value[key]["y"] = self.data_in_memory[i][key]["y"][gen]
                                        if self.data_in_memory[i][key]["x"].ndim == 2:
                                            input_value[key]["x"] = self.data_in_memory[i][key]["x"][gen, :]
                                            input_value[key]["y"] = self.data_in_memory[i][key]["y"][gen, :]
                                        if self.data_in_memory[i][key]["x"].ndim == 3:
                                            input_value[key]["x"] = self.data_in_memory[i][key]["x"][gen, :, :]
                                            input_value[key]["y"] = self.data_in_memory[i][key]["y"][gen, :, :]
                                    else:
                                        if self.data_in_memory[i][key].ndim == 1:
                                            input_value[key] = self.data_in_memory[i][key][gen]
                                        if self.data_in_memory[i][key].ndim == 2:
                                            input_value[key] = self.data_in_memory[i][key][gen, :]
                                        if self.data_in_memory[i][key].ndim == 3:
                                            input_value[key] = self.data_in_memory[i][key][gen, :, :]

                                if process.attribute.get_params()[key]["type"] in ["file"]:
                                    input_value[key] = self.data_in_memory[i][key]

                        elif i in self.tiff_step:
                            input_value["file_info"] = IoFile.Load_File_Data(self.tiff_image_path[gen])

                        if hasattr(process.attribute, "run_function"):
                            step_output_result = {}
                            if i == 0:
                                process.step_output_params = process.attribute.run_function(**input_value)
                            else:
                                for step_num in process.step_input_number:
                                    step_output_result.update(steps_output_result[step_num - 1])
                                keys = inspect.getargspec(process.attribute.run_function).args
                                keys.remove('self')
                                next_input_params = dict.fromkeys(keys)
                                input_keys_list = step_output_result.keys() & keys
                                for key in input_keys_list:
                                    next_input_params[key] = step_output_result[key]
                                next_input_params.update(input_value)
                                process.step_output_params = process.attribute.run_function(**next_input_params)

                        if process.step_connect_widget:
                            if "plot" in list(process.step_output_params.keys()):
                                if process.step_output_params["plot"]:
                                    plot = process.step_output_params["plot"]
                                    if plot["type"] == "2DV" or plot["type"] == "2DXY":
                                        self.signal_2DV.emit(process.step_connect_widget, plot)
                                    elif plot["type"] == "1DP":
                                        self.signal_1DP.emit(process.step_connect_widget, plot)
                                    elif plot["type"] == "2DP" or plot["type"] == "2DPL":
                                        self.signal_2DP.emit(process.step_connect_widget, plot)

                        steps_output_result.append({})
                        steps_output_result[i].update(step_output_result)
                        if process.step_output_params:
                            steps_output_result[i].update(process.step_output_params)

                    # for key, params_info in self.processing_list[i].attribute.get_params().items():######xiugai
                    #     print(params_info["type"], params_info["value"])########xiugai

                    self.update_attribute_signal.emit()

                    # save data
                    self.save_length = 2
                    if self.save_path and self.dataset_num:
                        if gen == 0:
                            for num in self.dataset_num:
                                self.save_data[num] = {}
                                self.save_data[num]["result"] = {}
                                for key, value in self.processing_list[num - 1].attribute.get_params().items():
                                    self.save_data[num][value["text"]] = []
                                    for length_attri in range(self.save_length):
                                        self.save_data[num][value["text"]].append("")

                                if "plot" in self.processing_list[num - 1].step_output_params:
                                    if self.processing_list[num - 1].step_output_params["plot"]["type"] == "1DP":
                                        if isinstance(self.processing_list[num - 1].step_output_params["plot"]["data"],
                                                      list):
                                            for data_xy in self.processing_list[num - 1].step_output_params["plot"]["data"]:
                                                length1 = data_xy["x"].shape[0]
                                                self.save_data[num]["result"][data_xy["legend"] + "_x"] = np.ones((self.save_length, length1))
                                                self.save_data[num]["result"][data_xy["legend"] + "_y"] = np.ones((self.save_length, length1))
                                        else:
                                            length1 = \
                                                self.processing_list[num - 1].step_output_params["plot"]["data"]["x"].shape[0]
                                            self.save_data[num]["result"]["x"] = np.ones((self.save_length, length1))
                                            self.save_data[num]["result"]["y"] = np.ones((self.save_length, length1))

                                    elif self.processing_list[num - 1].step_output_params["plot"]["type"] == "2DXY":
                                        lengthx = self.processing_list[num - 1].step_output_params["plot"]["data"]["x"].shape[0]
                                        lengthy = self.processing_list[num - 1].step_output_params["plot"]["data"]["y"].shape[0]
                                        self.save_data[num]["result"]["x"] = np.ones((self.save_length, lengthx))
                                        self.save_data[num]["result"]["y"] = np.ones((self.save_length, lengthy))
                                        self.save_data[num]["result"]["z"] = np.ones((self.save_length, lengthy, lengthx))

                                    elif self.processing_list[num - 1].step_output_params["plot"]["type"] == "2DV":
                                        length1 = self.processing_list[num - 1].step_output_params["plot"]["image"].shape[0]
                                        length2 = self.processing_list[num - 1].step_output_params["plot"]["image"].shape[1]
                                        self.save_data[num]["result"]["image"] = np.ones((self.save_length, length2, length1))

                                    elif self.processing_list[num - 1].step_output_params["plot"]["type"] == "2DP":
                                        self.save_data[num]["result"]["x"] = np.ones(self.save_length)

                        for num in self.dataset_num:
                            for key, value in self.processing_list[num - 1].attribute.get_params().items():
                                if value["type"] == "enum":
                                    result = value["value"].value
                                else:
                                    result = value["value"]
                                self.save_data[num][value["text"]][gen % self.save_length] = str(result)

                            if "plot" in self.processing_list[num - 1].step_output_params:
                                if self.processing_list[num - 1].step_output_params["plot"]["type"] == "1DP":
                                    if isinstance(self.processing_list[num - 1].step_output_params["plot"]["data"], list):
                                        for data_xy in self.processing_list[num - 1].step_output_params["plot"]["data"]:
                                            print(data_xy["x"].shape)
                                            self.save_data[num]["result"][data_xy["legend"]+"_x"][gen % self.save_length, :] = data_xy["x"]
                                            self.save_data[num]["result"][data_xy["legend"]+"_y"][gen % self.save_length, :] = data_xy["y"]
                                    else:
                                        self.save_data[num]["result"]["x"][gen % self.save_length, :] = \
                                            self.processing_list[num - 1].step_output_params["plot"]["data"]["x"]
                                        self.save_data[num]["result"]["y"][gen % self.save_length, :] = \
                                            self.processing_list[num - 1].step_output_params["plot"]["data"]["y"]

                                elif self.processing_list[num - 1].step_output_params["plot"]["type"] == "2DXY":
                                    self.save_data[num]["result"]["x"][gen % self.save_length][:] = \
                                        self.processing_list[num - 1].step_output_params["plot"]["data"]["x"]
                                    self.save_data[num]["result"]["y"][gen % self.save_length][:] = \
                                        self.processing_list[num - 1].step_output_params["plot"]["data"]["y"]
                                    self.save_data[num]["result"]["z"][gen % self.save_length][:] = \
                                        self.processing_list[num - 1].step_output_params["plot"]["data"]["z"]

                                elif self.processing_list[num - 1].step_output_params["plot"]["type"] == "2DV":
                                    self.save_data[num]["result"]["image"][gen % self.save_length][:] = \
                                        self.processing_list[num - 1].step_output_params["plot"]["image"]

                                elif self.processing_list[num - 1].step_output_params["plot"]["type"] == "2DP":
                                    self.save_data[num]["result"]["value"][gen % self.save_length][:] = \
                                        self.processing_list[num - 1].step_output_params["plot"]["data"]["value"]

                        if gen and gen % self.save_length == 1:
                            for key, value in self.save_data.items():
                                step_text = self.processing_list[key - 1].step_text
                                for attri_text, atrri_value in self.save_data[key].items():
                                    if attri_text == "result":
                                        for tt in self.save_data[key][attri_text]:
                                            IoHdf5.Save_H5_data(self.save_path, step_text+"/result/" + tt, atrri_value[tt], data_length=data_length, end=gen, save_length=self.save_length)
                                    else:
                                        IoHdf5.Save_H5_data(self.save_path, step_text+"/"+attri_text, atrri_value, data_set_type="attri", data_length = data_length,end=gen,save_length=self.save_length)

                        elif gen == data_length - 1 and gen % self.save_length > 0:
                            for key, value in self.save_data.items():
                                step_text = self.processing_list[key - 1].step_text
                                for attri_text, atrri_value in self.save_data[key].items():
                                    if attri_text == "result":
                                        for tt in self.save_data[key][attri_text]:
                                            IoHdf5.Save_H5_data(self.save_path, step_text+"/result/" + tt,
                                                                atrri_value, data_length = data_length, end=gen, save_length=self.save_length)
                                    else:
                                        IoHdf5.Save_H5_data(self.save_path, step_text+"/"+ attri_text,
                                                            atrri_value, data_set_type="attri", data_length = data_length,end=gen, save_length=self.save_length)

                self.signal_thread_end.emit()
            else:
                self.signal_thread_error.emit()
                return
        except Exception as e:
           self.excepted.emit(str(e))


class ProcessingOperateWidget(QWidget):
    signal_stop_work = pyqtSignal()

    def __init__(self, parent=None):
        super(ProcessingOperateWidget, self).__init__(parent)
        # ToolBar-------------------------------------------------------------------------------------
        self.navbar = QToolBar()
        self.navbar.setIconSize(QSize(30, 30))
        self.action_play = QAction("RUN", self)
        self.action_play.setIcon(QIcon(os.getcwd()+'/ui/icons/playback-play.png'))
        self.action_play.triggered.connect(self.start_work)
        self.navbar.addAction(self.action_play)

        self.action_stop = QAction("STOP", self)
        self.action_stop.setIcon(QIcon(os.getcwd()+'/ui/icons/playback-stop.png'))
        self.action_stop.triggered.connect(self.stop_work)
        self.navbar.addAction(self.action_stop)
        self.action_stop.setEnabled(False)

        self.action_save = QAction("SAVE PLAN", self)
        self.action_save.setIcon(QIcon(os.getcwd() + '/ui/icons/save.png'))
        self.action_save.triggered.connect(self.save_button_clicked)
        self.navbar.addAction(self.action_save)

        self.action_load = QAction("LOAD PLAN", self)
        self.action_load.setIcon(QIcon(os.getcwd() + '/ui/icons/load.png'))
        self.action_load.triggered.connect(self.load_button_clicked)
        self.navbar.addAction(self.action_load)

        # self.navbar.addAction(QIcon('ui/icons/save.png'), "Save Processing")
        # self.navbar.addAction(QIcon('ui/icons/load.png'), "load Processing")
        # processing Widget layout-------------------------------------------------------------------
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.navbar)
        self.processing_widget = ProcessingWidget()
        self.layout.addWidget(self.processing_widget)
        self.thread = None


    def save_button_clicked(self):
        file_path = QFileDialog.getSaveFileName(self, "save plan dialog", "D:/", "Txt files(*.yaml)")
        plan_dir = file_path[0][0: file_path[0].rfind('/')]
        file_name = file_path[0][file_path[0].rfind('/') + 1:]
        if file_name:
            if self.processing_widget.processing_list:
                PlanManager.save_processing_plan(plan_dir, file_name, self.processing_widget.processing_list)
            else:
                QMessageBox.about(self, "Error Message", "Do not save the empty plan")
        else:
            QMessageBox.about(self, "Error Message", "please input file name")

    def load_button_clicked(self):
        file_path = QFileDialog.getOpenFileName(self, "open plan dialog", "D:/", "Txt files(*.yaml)")
        plan_dir = file_path[0][0: file_path[0].rfind('/')]
        file_name = file_path[0][file_path[0].rfind('/') + 1:]
        plan_text = PlanManager.load_processing_plan(plan_dir, file_name)
        if plan_text is not None:
            self.processing_widget.processing_list = plan_text
            self.processing_widget.update_steps_tableWidget()
            # self.processing_widget.steps_tablewidget.insertRow(len(self.processing_list))
            # self.processing_widget.steps_tablewidget.setCellWidget(len(self.processing_list), 0,
            #                                              Button("add", self.processing_widget.add_step_button_clicked))
            # self.processing_widget.update_attribute(0)
        else:
            QMessageBox.about(self, "Error Message", "please load the correct plan")


    def start_work(self):
        for widget_dict in [self.processing_widget.plot1d_widget_dict, self.processing_widget.plot2d_widget_dict,
                            self.processing_widget.visualizer2d_widget_dict]:
            for widget in widget_dict.values():
                widget["widget"].clear()
        self.thread = Runthread(self.processing_widget.processing_list)
        self.thread.signal_1DP.connect(self.plot1d_show)
        self.thread.signal_2DV.connect(self.visualizer2d_show)
        self.thread.signal_2DP.connect(self.plot2d_show)
        self.thread.signal_thread_end.connect(self.thread_end)
        self.thread.signal_thread_error.connect(self.thread_error)
        self.thread.excepted.connect(self.error_info)
        self.thread.update_attribute_signal.connect(self.processing_widget.update_attribute_thread)
        self.action_stop.setEnabled(True)
        self.action_play.setEnabled(False)
        self.signal_stop_work.connect(self.thread.stop_work)
        self.thread.start()

    def error_info(self, info):
        QMessageBox.information(self, "Error", "please check the parameters and pipeline sequence!\n"+info)
        self.thread_end()


    def thread_end(self):
        self.action_play.setEnabled(True)
        self.action_stop.setEnabled(False)

    def thread_error(self):
        self.action_play.setEnabled(True)
        self.action_stop.setEnabled(False)
        QMessageBox.critical(self, 'Error', "please input the data source", QMessageBox.Close)

    def stop_work(self):
        self.signal_stop_work.emit()

    def plot1d_show(self, widget_name, plot):
        self.processing_widget.signal_1DP.emit(widget_name, plot)

    def plot2d_show(self, widget_name, plot):
        self.processing_widget.signal_2DP.emit(widget_name, plot)

    def visualizer2d_show(self, widget_name, plot):
        self.processing_widget.signal_2DV.emit(widget_name, plot)


class ProcessingWidget(QWidget, Ui_processing_widget):
    signal_1DP = pyqtSignal(str, dict)
    signal_2DP = pyqtSignal(str, dict)
    signal_2DV = pyqtSignal(str, dict)

    signal_add_plot1d = pyqtSignal(str)
    signal_add_plot2d = pyqtSignal(str)
    signal_add_visualizer2d = pyqtSignal(str)

    def __init__(self, parent=None):
        super(ProcessingWidget, self).__init__(parent)
        # Initialize local parameters----------------------------------------------------------------
        self.processing_list = ProcessingSequence()
        self.step_object_dict = self.processing_list.step_object_dict
        self.step_item_tip_list = [tip for _, tip in list(self.step_object_dict.values())]
        self.step_item_list = list(self.step_object_dict.keys())
        self.step_remove = None
        self.attribute_widget_dict = OrderedDict()
        self.plot1d_widget_dict = None
        self.plot2d_widget_dict = None
        self.visualizer2d_widget_dict = None
        self.file_select_save = None
        self.file_select_dataset = None
        self.file_select_read = None

        # Initialize view-----------------------------------------------------------------------------
        self.setupUi(self)
        self.steps_tablewidget.setCellWidget(0, 0, Button("add", self.add_step_button_clicked))
        self.steps_tablewidget.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.steps_tablewidget.setStyleSheet("QTableWidget::item:selected { selection-color: rgb(255, 0, 0) }")

        # QT Signal connect-----------------------------------------------------------------------------
        # self.steps_tablewidget.clicked.connect(self.steps_tablewidget_clicked)
        self.steps_tablewidget.itemClicked.connect(self.show_clicked_step_attribute)
        self.steps_tablewidget.customContextMenuRequested.connect(self.generateMenu)

    def generateMenu(self, pos):
        for i in self.steps_tablewidget.selectionModel().selection().indexes():
            row_num = i.row()
        main_menu = QMenu()
        main_menu.setMinimumWidth(150)
        add_1d_menu = main_menu.addAction(u"add plot 1d")
        add_2d_menu = main_menu.addAction(u"add image visualizer")
        if "row_num" in dir() and row_num < self.steps_tablewidget.rowCount() - 1:
            # select input number
            if row_num > 0:
                select_input_menu = main_menu.addAction(u"select input step number")
                self.select_input_combobox = QComboBox()
                self.select_input_combobox.addItems(str(x) for x in list(range(1, row_num + 1)))
                add_input_button = QPushButton("add")
                add_input_button.clicked.connect(lambda: self.add_input_button_clicked(row_num))
                self.selected_input_label = QLabel(str(self.processing_list[row_num].step_input_number))
                clear_input_button = QPushButton("clear")
                clear_input_button.clicked.connect(lambda: self.clear_input_button_clicked(row_num))
                select_input_submenu = QMenu()
                layout = QGridLayout()
                layout.addWidget(self.select_input_combobox, 0, 0)
                layout.addWidget(add_input_button, 0, 1)
                layout.addWidget(self.selected_input_label, 1, 0)
                layout.addWidget(clear_input_button, 1, 1)
                select_input_submenu.setLayout(layout)
                select_input_menu.setMenu(select_input_submenu)
            # select output widget
            if self.plot1d_widget_dict:
                select_output_menu = main_menu.addAction(u"select connect widget")
                self.connect_widget_combobox = QComboBox()
                self.ids = []
                for id in self.plot1d_widget_dict.keys():
                    self.connect_widget_combobox.addItem(self.plot1d_widget_dict[id]["name"])
                    self.ids.append(id)
                for id in self.plot2d_widget_dict.keys():
                    self.connect_widget_combobox.addItem(self.plot2d_widget_dict[id]["name"])
                    self.ids.append(id)
                for id in self.visualizer2d_widget_dict.keys():
                    self.connect_widget_combobox.addItem(self.visualizer2d_widget_dict[id]["name"])
                    self.ids.append(id)
                self.connect_widget_combobox.addItem("clear")#####
                self.ids.append("")
                connect_widget_button = QPushButton("connect")
                connect_widget_button.clicked.connect(lambda: self.select_show_widget(row_num))
                select_widget_menu = QMenu()
                layout = QGridLayout()
                layout.addWidget(self.connect_widget_combobox, 0, 0)
                layout.addWidget(connect_widget_button, 0, 1)
                select_widget_menu.setLayout(layout)
                select_output_menu.setMenu(select_widget_menu)
        action = main_menu.exec_(self.steps_tablewidget.mapToGlobal(pos))
        if action == add_1d_menu:
            text, ok = QInputDialog.getText(self, '设置窗口', '请输入一维图名：')
            if ok:
                self.signal_add_plot1d.emit(text)
        elif action == add_2d_menu:
            text, ok = QInputDialog.getText(self, '设置窗口', '请输入二维图名：')
            if ok:
                self.signal_add_visualizer2d.emit(text)
        else:
            return

    def add_input_button_clicked(self, row_num):
        if int(self.select_input_combobox.currentText()) not in self.processing_list[row_num].step_input_number:
            self.processing_list[row_num].step_input_number.append(int(self.select_input_combobox.currentText()))
            self.processing_list[row_num].step_input_number.sort()
            self.selected_input_label.setText(str(self.processing_list[row_num].step_input_number))
            self.update_steps_tableWidget()

    def clear_input_button_clicked(self, row_num):
        self.processing_list[row_num].step_input_number = []
        self.selected_input_label.setText(str(self.processing_list[row_num].step_input_number))
        self.update_steps_tableWidget()

    def select_show_widget(self, row_num):
        self.processing_list[row_num].step_connect_widget = self.ids[self.connect_widget_combobox.currentIndex()]
        self.update_steps_tableWidget()

    # def steps_tablewidget_clicked(self, index):
    #     step_index = index.row()
    #     if len(self.processing_list) > step_index and self.processing_list[step_index].step_connect_widget:
    #         if "plot" in list(self.processing_list[step_index].step_output_params.keys()):
    #             plot = self.processing_list[step_index].step_output_params["plot"]
    #             class_name = type(self.processing_list[step_index].attribute).__name__
    #             step_connect_widget = self.processing_list[step_index].step_connect_widget
    #             if plot["type"] == "2DV":
    #                 print(step_connect_widget)
    #                 self.signal_2DV.emit(class_name, step_connect_widget, plot)
    #             if plot["type"] == "1DP":
    #                 self.signal_1DP.emit(class_name, step_connect_widget, plot)
    #             if plot["type"] == "2DP":
    #                 self.signal_2DP.emit(class_name, step_connect_widget, plot)

    def clear_steps_tableWidget(self):
        self.steps_tablewidget.clearContents()
        self.steps_tablewidget.setRowCount(0)

    def clear_attributes_tableWidget(self):
        self.attributes_tablewidget.clearContents()
        self.attributes_tablewidget.setRowCount(0)

    def show_clicked_step_attribute(self, index):
        if self.processing_list[index.row()].attribute:
            self.update_attribute(index.row())

    def update_steps_tableWidget_without_add_button(self):
        row = len(self.processing_list)
        self.steps_tablewidget.setRowCount(row)
        self.step_remove = [None] * row
        if row:
            for i in range(row):
                self.step_remove[i] = Button("remove", self.remove_step_button_clicked, i)
                self.steps_tablewidget.setCellWidget(i, 0, self.step_remove[i])
                item_text = self.processing_list[i].attribute.function_text + "   " + str(self.processing_list[i].step_input_number)
                uid = self.processing_list[i].step_connect_widget
                if uid in self.plot1d_widget_dict:
                    item_text = item_text + "   " + str(self.plot1d_widget_dict[uid]["name"])
                elif uid in self.visualizer2d_widget_dict:
                    item_text = item_text + "   " + str(self.visualizer2d_widget_dict[uid]["name"])
                elif uid in self.plot2d_widget_dict:
                    item_text = item_text + "   " + str(self.plot2d_widget_dict[uid]["name"])
                item = QTableWidgetItem(item_text)
                self.steps_tablewidget.setItem(i, 1, item)

    def update_steps_tableWidget(self):
        self.update_steps_tableWidget_without_add_button()
        self.steps_tablewidget.insertRow(len(self.processing_list))
        self.steps_tablewidget.setCellWidget(len(self.processing_list), 0, Button("add", self.add_step_button_clicked))

    def add_step_button_clicked(self):
        self.attributes_tablewidget.setRowCount(0)
        self.update_steps_tableWidget_without_add_button()
        row = len(self.processing_list)
        self.steps_tablewidget.insertRow(row)
        self.step_remove.append(Button("remove", self.remove_step_button_clicked, row))
        self.steps_tablewidget.setCellWidget(row, 0, self.step_remove[row])
        self.step_select_combobox = QComboBox()
        model = QStandardItemModel()
        for i, item in enumerate(self.step_item_list):
            self.step_select_combobox.addItem(item)
            item = QStandardItem(item)
            item.setToolTip(self.step_item_tip_list[i])
            model.appendRow(item)
        self.step_select_combobox.setModel(model)
        self.step_select_combobox.activated.connect(self.step_select_combobox_clicked)
        self.steps_tablewidget.setCellWidget(row, 1, self.step_select_combobox)

    def remove_step_button_clicked(self, index):
        self.clear_steps_tableWidget()
        self.clear_attributes_tableWidget()
        if len(self.processing_list) > index:
            self.processing_list.pop(index)
            for i in range(index, len(self.processing_list)):
                self.processing_list[i].step_input_number = (np.array(self.processing_list[i].step_input_number) - 1)
                self.processing_list[i].step_input_number = self.processing_list[i].step_input_number[
                    self.processing_list[i].step_input_number != 0].tolist()
        self.update_steps_tableWidget()

    def step_select_combobox_clicked(self):
        # add new step in processing sequence and show attribute empty property
        current_line = len(self.processing_list)
        step_type = self.step_item_list[self.step_select_combobox.currentIndex()]
        self.steps_tablewidget.removeCellWidget(current_line, 1)
        # update the variable
        input_step_number = [current_line] if current_line else []
        self.processing_list.add_step_in_data(step_type, self.step_object_dict[step_type][0](), input_step_number)
        self.update_attribute(current_line)
        self.update_steps_tableWidget()

    def attribute_edit_changed(self, step_index, attribute_key):
        self.processing_list[step_index].attribute.set_param(attribute_key,
                                                             self.attribute_widget_dict[attribute_key].text())

    def attribute_combobox_changed(self, step_index, attribute_key, enum_type):
        value = self.attribute_widget_dict[attribute_key].currentText()
        self.processing_list[step_index].attribute.set_param(attribute_key, enum_type(value))

    def attribute_checkbox_changed(self, step_index, attribute_key):
        self.processing_list[step_index].attribute.set_param(attribute_key,
                                                             self.attribute_widget_dict[attribute_key].isChecked())

    def update_attribute(self, step_index):
        self.clear_attributes_tableWidget()
        current_line = 0
        for key, params_info in self.processing_list[step_index].attribute.get_params().items():
            self._set_attribute_name_item(current_line, params_info["text"])
            self.attribute_widget_dict[key] = self._set_attribute_value_item(current_line, step_index, key,
                                                                             params_info["type"], params_info["value"])
            current_line = current_line + 1

    def update_attribute_thread(self):
        if self.steps_tablewidget.selectedItems():
            step_index = self.steps_tablewidget.selectedItems()[0].row()
            self.update_attribute(step_index)

    def _set_attribute_name_item(self, current_row, attribute_name):
        self.attributes_tablewidget.insertRow(current_row)
        Item = QTableWidgetItem(attribute_name)
        Item.setFont(QFont('Times New Roman', 10))
        Item.setForeground(QBrush(QColor(0, 0, 0)))
        self.attributes_tablewidget.setItem(current_row, 0, Item)
        self.attributes_tablewidget.item(current_row, 0).setFlags(Qt.ItemIsEditable)

    def _set_attribute_value_item(self, current_row, step_index, attribute_key, attribute_type, attribute_text):
        if attribute_type in ["str", "int", "float", "tuple", "tuple_float", "tuple_int"]:
            attribute_widget = QLineEdit()
            attribute_widget.setAlignment(Qt.AlignCenter)
            attribute_widget.setStyleSheet("QLineEdit{border-width:0;border-style:outset}")
            attribute_widget.setFont(QFont("Times New Roman", 10))
            if attribute_text is not None:
                attribute_widget.setText(str(attribute_text))
            attribute_widget.textChanged.connect(lambda: self.attribute_edit_changed(step_index, attribute_key))
            self.attributes_tablewidget.setCellWidget(current_row, 1, attribute_widget)
            return attribute_widget

        elif attribute_type in ["file", "save"]:
            attribute_widget = QWidget()
            layout = QHBoxLayout()
            file_select = QLineEdit()
            file_select.setStyleSheet("QLineEdit{border-width:0;border-style:outset}")
            if attribute_text is not None:
                file_select.setText(str(attribute_text))
            file_select.textChanged.connect(lambda: self.attribute_edit_changed(step_index, attribute_key))
            file_select_button = QPushButton("…")
            file_select_button.setMaximumWidth(40)
            if attribute_type in ["file"]:
                file_select_button.clicked.connect(lambda: self.file_select_button_clicked(file_select))
            elif attribute_type in ["save"]:
                file_select_button.clicked.connect(lambda: self.file_save_button_clicked(file_select))
            layout.addWidget(file_select)
            layout.addWidget(file_select_button)
            layout.setContentsMargins(0, 0, 0, 0)
            attribute_widget.setLayout(layout)
            self.attributes_tablewidget.setCellWidget(current_row, 1, attribute_widget)
            return file_select

        elif attribute_type in ["io"]:
            attribute_widget = QWidget()
            layout = QHBoxLayout()
            file_select = QLineEdit()
            file_select.setStyleSheet("QLineEdit{border-width:0;border-style:outset}")
            if attribute_text is not None:
                file_select.setText(str(attribute_text))
            file_select.textChanged.connect(lambda: self.attribute_edit_changed(step_index, attribute_key))
            file_select_button = QPushButton("…")
            file_select_button.setMaximumWidth(40)
            if attribute_type in ["io"]:
                if attribute_key == "file_location":
                    file_select_button.clicked.connect(lambda: self.file1d_select_button_clicked_dialog(file_select))
                else:
                    file_select_button.clicked.connect(lambda: self.file_select_button_clicked_dialog(file_select))
            layout.addWidget(file_select)
            layout.addWidget(file_select_button)
            layout.setContentsMargins(0, 0, 0, 0)
            attribute_widget.setLayout(layout)
            self.attributes_tablewidget.setCellWidget(current_row, 1, attribute_widget)
            return file_select

        elif attribute_type in ["bool"]:
            attribute_widget = QCheckBox()
            attribute_widget.setChecked(attribute_text)
            attribute_widget.stateChanged.connect(lambda: self.attribute_checkbox_changed(step_index, attribute_key))
            self.attributes_tablewidget.setCellWidget(current_row, 1, attribute_widget)
            return attribute_widget
        elif attribute_type in ["enum"]:
            attribute_widget = QComboBox()
            enum_type = type(self.processing_list[step_index].attribute.get_param(attribute_key))
            for attr in enum_type:
                attribute_widget.addItem(attr.value)
            attribute_widget.setCurrentText(self.processing_list[step_index].attribute.get_param(attribute_key).value)
            attribute_widget.currentIndexChanged.connect(
                lambda: self.attribute_combobox_changed(step_index, attribute_key, enum_type))
            self.attributes_tablewidget.setCellWidget(current_row, 1, attribute_widget)
            return attribute_widget

    def file_select_button_clicked_dialog(self, select):
        dialog = Select_file_dialog()
        if dialog.exec_():
            file_info = dialog.file_info
            if "file" in file_info and "h5_dataset" in file_info and "type" in file_info:
                if file_info["file"] and file_info["h5_dataset"] and file_info["type"]:
                    select.setText('{} {} {}'.format(file_info["file"], file_info["h5_dataset"], file_info["type"]))
            elif "file" in file_info and file_info["file"] and "type" in file_info and file_info["type"]:
                select.setText('{} {}'.format(file_info["file"], file_info["type"]))

    def file1d_select_button_clicked_dialog(self, select):
        dialog = Select_1D_file_dialog()
        if dialog.exec_():
            file_info = dialog.file_info
            if "file" in file_info and "x_dataset" in file_info and "y_dataset" in file_info:
                select.setText('{} {} {}'.format(file_info["file"], file_info["x_dataset"], file_info["y_dataset"]))

    def file_select_button_clicked(self, file_select):
        file_name, file_type = QFileDialog.getOpenFileName(self, "getOpenFileName", "./",
                                                           "All Files (*);;Text Files (*.txt)")
        if file_name:
            file_select.setText(file_name)

    def file_save_button_clicked(self, file_select):
        file_name, file_type = QFileDialog.getSaveFileName(self, 'save file', './', "edf files(*.h5)")
        if file_name:
            file_select.setText(file_name)


class Button(QPushButton):
    def __init__(self, type, clicked_function=None, index=None, color=None):
        super(Button, self).__init__()
        if color:
            self.setStyleSheet("background-color:" + color + ";" "border:none")
        else:
            self.setStyleSheet("background-color:rgb(255, 255, 255);" "border:none")
        if type == "add":
            self.setIcon(QIcon(os.getcwd()+"/ui/icons/list-add.png"))
        if type == "remove":
            self.setIcon(QIcon(os.getcwd()+"/ui/icons/list-remove.png"))
        if type == "setting":
            self.setIcon(QIcon(os.getcwd()+"/ui/icons/settings.png"))
        if clicked_function is not None and index is None:
            self.clicked.connect(clicked_function)
        if clicked_function is not None and index is not None:
            self.clicked.connect(lambda: clicked_function(index))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ProcessingOperateWidget()
    ex.resize(1200, 800)
    ex.show()
    sys.exit(app.exec_())
