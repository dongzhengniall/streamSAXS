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
        self._params_dict["file_info"] = {"type": "io", "value": "E:/dongzheng/XRD_code/data/SSRF-10U-202107/SSRF-10U-202107/SSRF_202107 tiff", "text": "File Info"}

    def run_function(self, **kwargs):
        i=0
        if self._params_dict["file_info"]:
            if not "file_info" in kwargs:
                raise ValueError("The file path must be input")
            else:
                image = kwargs["file_info"]
                i = i+1

        data = {"image": image,"Image_num":i}
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
