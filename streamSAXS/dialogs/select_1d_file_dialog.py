import h5py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QToolBox, QPushButton, QWidget, QLineEdit, QHBoxLayout, QLabel, \
    QFileDialog, QInputDialog


class Select_1D_file_dialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.file_info = {"type": None}
        self.resize(800, 600)
        self.setWindowTitle("Select 1D Data")
        self.names = ["hdf5"]

        vLayout = QVBoxLayout(self)
        self.toolBox = QToolBox(self)
        self.toolBox.currentChanged.connect(self.onToolBoxCurrentChanged)
        hdf5 = self.hdf5_box()
        self.toolBox.addItem(hdf5, "hdf5")

        #self.toolBox.addItem(tiff, "tiff")

        vLayout.addWidget(self.toolBox)

        self.submit = QPushButton('ok', self)
        self.submit.clicked.connect(self.submitclose)
        vLayout.addWidget(self.submit)

        self.setLayout(vLayout)

        self.toolBox.setCurrentIndex(1)

    def hdf5_box(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.h5_file_select = QLineEdit()
        widget1 = self._set_widget_layout("file name", self.h5_file_select, self.h5_file_select_button_clicked)
        layout.addWidget(widget1)

        self.x_dataset_select = QLineEdit()
        widget2 = self._set_widget_layout("X dataset", self.x_dataset_select, self.select_xdataset)
        layout.addWidget(widget2)

        self.y_dataset_select = QLineEdit()
        widget3 = self._set_widget_layout("Y dataset", self.y_dataset_select, self.select_ydataset)
        layout.addWidget(widget3)
        layout.addStretch(1)
        widget.setLayout(layout)

        return widget

    def tiff_box(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.tiff_file_select = QLineEdit()
        widget1 = self._set_widget_layout("file folder", self.tiff_file_select, self.tiff_file_select_button_clicked)
        layout.addWidget(widget1)

        layout.addStretch(1)
        widget.setLayout(layout)

        return widget

    def _set_widget_layout(self, name, edit, clicked_function):
        widget = QWidget()
        layout = QHBoxLayout()
        label = QLabel(name)
        button = QPushButton("…")
        button.clicked.connect(clicked_function)
        layout.addWidget(label)
        layout.addWidget(edit)
        layout.addWidget(button)
        widget.setLayout(layout)
        return widget

    def onToolBoxCurrentChanged(self):
        self.file_info["type"] = self.names[self.toolBox.currentIndex()]

    def h5_file_select_button_clicked(self):
        file_name, file_type = QFileDialog.getOpenFileName(self, "getOpenFileName", "./",
                                                           "All Files (*);;Text Files (*.txt)")
        if file_name:
            self.h5_file_select.setText(file_name)
            self.file_info["file"] = file_name

    def tiff_file_select_button_clicked(self):
        folder_name = QFileDialog.getExistingDirectory(self, "Select folder", "./")
        if folder_name:
            self.tiff_file_select.setText(folder_name)
            self.file_info["file"] = folder_name

    def get_data_in_h5_file(self, f, h5_dataset_dict):
        for k in f.keys():
            d = f[k]
            if isinstance(d, h5py.Group):
                self.get_data_in_h5_file(d, h5_dataset_dict)
            elif isinstance(d, h5py.Dataset):
                h5_dataset_dict[d.name] = {}
                h5_dataset_dict[d.name]["dataset"] = d
                h5_dataset_dict[d.name]["size"] = d.size
            else:
                print('??->', d, 'Unkown Object!')
        return h5_dataset_dict

    def select_xdataset(self):
        file = self.h5_file_select.text()
        if file:
            try:
                f = h5py.File(file, 'r')
                data = self.get_data_in_h5_file(f, {})
                items = []
                for dataset in data:
                    items.append(dataset)

                item, ok = QInputDialog.getItem(self, "select dataset dialog", "dataset", items, 0, False)
                if ok and item:
                    self.file_info["x_dataset"] = str(item)
                    self.x_dataset_select.setText(str(item))
                f.close()
            except:
               print("No dataset")

    def select_ydataset(self):
        file = self.h5_file_select.text()
        if file:
            try:
                f = h5py.File(file, 'r')
                data = self.get_data_in_h5_file(f, {})
                items = []
                for dataset in data:
                    items.append(dataset)

                item, ok = QInputDialog.getItem(self, "select dataset dialog", "dataset", items, 0, False)
                if ok and item:
                    self.file_info["y_dataset"] = str(item)
                    self.y_dataset_select.setText(str(item))
                f.close()
            except:
               print("No dataset")

    def submitclose(self):
        self.accept()
