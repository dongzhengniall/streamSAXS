from util.processing_sequence import ProcessingFunction


class LoadH5Data(ProcessingFunction):
    """
    DESCRIPTION:Import DataSource File
    Parameters:
        data_source_file : TYPE str
    Returns:
        data : numpy
    """
    function_text = "Load Data File"
    function_tip = "Load data from file"

    def __init__(self):
        super().__init__()
        self._params_dict["file_info"] = {"type": "io", "value": r'D:/dongzheng/bamboo-saxsCT/S4/S4/WAXD tiff', "text": "File Info"}

    def run_function(self, **kwargs):

        if self._params_dict["file_info"]:
            if not "file_info" in kwargs:
                raise ValueError("The file path must be input")
            else:
                image = kwargs["file_info"]

        data = {"image": image}

        return {"data": data,
                "plot": {"type": "2DV", "data": data["image"]}}


class SaveH5Data(ProcessingFunction):
    """
    DESCRIPTION:Save DataSource to File
    """
    function_text = "Save Data"
    function_tip = "Save data to H5 file"

    def __init__(self):
        super().__init__()
        self._params_dict["file_folder"] = {"type": "save", "value": None, "text": "file folder"}
        self._params_dict["dataset_name"] = {"type": "str", "value": None, "text": "dataset name"}
        self._params_dict["dataset_num"] = {"type": "str", "value": None, "text": "dataset number"}
