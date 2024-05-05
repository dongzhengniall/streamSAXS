from util.processing_sequence import ProcessingFunction


class LoadH5Data(ProcessingFunction):
    """
    DESCRIPTION:Import DataSource File
    Parameters:
        data_source_file : TYPE str
    Returns:
        data : numpy
    """
    function_text = "Load 2D Data"
    function_tip = "Load data from file"

    def __init__(self):
        super().__init__()
        self._params_dict["file_info"] = {"type": "io", "value":None, "text": "File Info"}

    def run_function(self, **kwargs):

        if self._params_dict["file_info"]:
            if not "file_info" in kwargs:
                raise ValueError("The file path must be input")
            else:
                image = kwargs["file_info"]

        data = {"image": image}

        return {"data": data,
                "plot": {"type": "2DV", "data": data["image"]}}


class Load1DData(ProcessingFunction):
    """
    DESCRIPTION:Import DataSource File
    Parameters:
        data_source_file : TYPE str
    Returns:
        data : numpy
    """
    function_text = "Load 1D Data"
    function_tip = "Load data from file"

    def __init__(self):
        super().__init__()
        self._params_dict["file_location"] = {"type": "io", "value": None, "text": "File Location"}

    def run_function(self, **kwargs):

        if self._params_dict["file_location"]:
            if not "file_location" in kwargs:
                raise ValueError("The file path must be input")
            else:
                curve = kwargs["file_location"]

        data = {"x": curve["x"], "y": curve["y"]}

        return {"data": data,
                "plot": {"data":{'x': curve["x"], 'y': curve["y"]}, 'type': '1DP'}}


class SaveH5Data(ProcessingFunction):
    """
    DESCRIPTION:Save DataSource to File
    """
    function_text = "Save Data"
    function_tip = "Save data to H5 file"

    def __init__(self):
        super().__init__()
        self._params_dict["file_folder"] = {"type": "save", "value": None, "text": "file folder"}
