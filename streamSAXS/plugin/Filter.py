
from util.processing_sequence import ProcessingFunction
from enum import unique, Enum
# import numpy as np
import plugin.CT_Process_Function as CTF
from util.io import OutCTData
'''
class NonLocalMeans(ProcessingFunction):
    """
    DESCRIPTION:Non-Local Means Filter
    Parameters:
        data_source_file : array
    Returns:
    """

    function_text = "NonLocalMeans"
    function_tip = "Non-Local Means Filter"

    def __init__(self):
        super().__init__()
        self._params_dict["DataSave"] = {"type": "ct_save",
                                         "value": None,
                                         "text": "Save Path",
                                         "Tip": "The data will be saved in fold as H5 and TIFF"}
        self._params_dict["data_interest"] = {"type": "enum", "value": Interest_Data_Type.unit3,
                                              "text": "Data"}
        self._params_dict["range"] = {"type": "tuple_int", "value": None,
                                              "text": "Range"}
        self._params_dict["h"] = {"type": "float", "value": 3, "text": "h","tip":"	Parameter regulating filter strength. Big h value perfectly removes noise but also removes image details, smaller h value preserves details but also preserves some noise"}
        self._params_dict["search_window"] = {"type": "int", "value": 21, "text": "search_window",'tip':"Size in pixels of the window that is used to compute weighted average for given pixel. Should be odd. Affect performance linearly: greater searchWindowsSize - greater denoising time. Recommended value 21 pixels"}
        self._params_dict["block_size"] = {"type": "int", "value": 7,
                                           "text": "block_size",
                                           "tip": 'Size in pixels of the template patch that is used to compute weights. Should be odd. Recommended value 7 pixels'}

    def run_function(self, data):
        if self.get_param_value("data_interest") == Interest_Data_Type.unit1:
            unit = 'Proj'
        if self.get_param_value("data_interest") == Interest_Data_Type.unit2:
            unit = 'Nordata'
        if self.get_param_value("data_interest") == Interest_Data_Type.unit3:
            unit = 'Recdata'
        if self.get_param_value("range") is None:
            self.set_param("range",(0,data[unit].shape[0]))
        print(self.get_param_value("range"))
        Filter_data={}
        Filter_data["oriData"]=unit
        Filter_data["filterMethod"] = "NonLocalMeans"
        Filter_data["filterRange"] = "NonLocalMeans"
        Filter_data['data']=CTF.NonLocalMeans(data=data[unit][self.get_param_value("range")[0]:self.get_param_value("range")[1]],
                                               h=self.get_param_value("h"),
                                               search_window=self.get_param_value("search_window"),
                                                block_size=self.get_param_value("block_size"))
        data["Filter_data"]=Filter_data

        if self.get_param_value("DataSave") is not None:
            OutCTData.Save_Tiff_data(Path=self.get_param_value("DataSave"),
                                     data=Filter_data['data'],
                                     SlicesStart=0,
                                     ROCRange=None)
            OutCTData.Save_H5_data(Path=self.get_param_value("DataSave"),
                                   data=data["Filter_data"],
                                   RecParas=data["Filter_data"])

        return {'data': data,
                "plot": {"type": "2DV",
                         "data": Filter_data['data'] ,
                         "title": unit + ':' + "NonLocalMeans"}}

'''


class Blur(ProcessingFunction):
    """
    DESCRIPTION:Blur filter
    Parameters:
        data_source_file : array
    Returns:
    """

    function_text = "Blur"
    function_tip = "Blur filter"

    def __init__(self):
        super().__init__()
        self._params_dict["DataSave"] = {"type": "ct_save",
                                         "value": None,
                                         "text": "Save Path",
                                         "Tip": "The data will be saved in fold as H5 and TIFF"}
        self._params_dict["data_interest"] = {"type": "enum", "value": Interest_Data_Type.unit3,
                                              "text": "Data"}
        self._params_dict["range"] = {"type": "tuple_int", "value": None,
                                              "text": "Range"}

        self._params_dict["ksize"] = {"type": "tuple_int", "value": (3,3), "text": "ksize",'tip':"blurring kernel size"}

    def run_function(self, data):
        if self.get_param_value("data_interest") == Interest_Data_Type.unit1:
            unit = 'Proj'
        if self.get_param_value("data_interest") == Interest_Data_Type.unit2:
            unit = 'Nordata'
        if self.get_param_value("data_interest") == Interest_Data_Type.unit3:
            unit = 'Recdata'
        if self.get_param_value("range") is None:
            self.set_param("range",(0,data[unit].shape[0]))
        Filter_data={}
        Filter_data["oriData"]=unit
        Filter_data["filterMethod"] = "Blur"
        Filter_data["ksize"]=self.get_param_value("ksize")
        Filter_data["filterRange"] = self.get_param_value("range")

        Filter_data['data'] = CTF.Blur(
            data=data[unit][self.get_param_value("range")[0]:self.get_param_value("range")[1]],
            ksize=self.get_param_value("ksize"))
        data["Filter_data"] = Filter_data

        if self.get_param_value("DataSave") is not None:
            OutCTData.Save_Tiff_data(Path=self.get_param_value("DataSave"),
                                     data=Filter_data['data'],
                                     SlicesStart=0,
                                     ROCRange=None,
                                     image_name=unit + '_' + "Blur")
            OutCTData.Save_H5_data_Filter(Path=self.get_param_value("DataSave"),
                                   data=data["Filter_data"],File_name=unit + '_' + "Blur")

        return {'data': data,
                "plot": {"type": "2DV",
                         "data": Filter_data['data'],
                         "title": unit + ':' + "Blur"}}





class GuassianBlur(ProcessingFunction):
    """
    DESCRIPTION:GuassianBlur filter
    Parameters:
        data_source_file : array
    Returns:
    """

    function_text = "GuassianBlur"
    function_tip = "GuassianBlur filter"

    def __init__(self):
        super().__init__()
        self._params_dict["DataSave"] = {"type": "ct_save",
                                         "value": None,
                                         "text": "Save Path",
                                         "Tip": "The data will be saved in fold as H5 and TIFF"}
        self._params_dict["data_interest"] = {"type": "enum", "value": Interest_Data_Type.unit3,
                                              "text": "Data"}
        self._params_dict["range"] = {"type": "tuple_int", "value": None,
                                              "text": "Range"}

        self._params_dict["ksize"] = {"type": "tuple_int", "value": (5,5), "text": "ksize",'tip':"Gaussian Kernel Size. [height width]. height and width should be odd and can have different values. If ksize is set to [0 0], then ksize is computed from sigma values"}

        self._params_dict["sigmaX"] = {"type": "float", "value": 0, "text": "sigmaX", 'tip':"Kernel standard deviation along X-axis (horizontal direction)."}
        self._params_dict["sigmaY"] = {"type": "float", "value": 0, "text": "sigmaY", 'tip':'Kernel standard deviation along Y-axis (vertical direction). If sigmaY=0, then sigmaX value is taken for sigmaY'}

    def run_function(self, data):
        if self.get_param_value("data_interest") == Interest_Data_Type.unit1:
            unit = 'Proj'
        if self.get_param_value("data_interest") == Interest_Data_Type.unit2:
            unit = 'Nordata'
        if self.get_param_value("data_interest") == Interest_Data_Type.unit3:
            unit = 'Recdata'
        if self.get_param_value("range") is None:
            self.set_param("range",(0,data[unit].shape[0]))
        Filter_data={}
        Filter_data["oriData"]=unit
        Filter_data["filterMethod"] = "GuassianBlur"
        Filter_data["ksize"]=self.get_param_value("ksize")
        Filter_data["sigmaX"] = self.get_param_value("sigmaX")
        Filter_data["sigmaY"] = self.get_param_value("sigmaY")
        Filter_data["filterRange"] = self.get_param_value("range")

        Filter_data['data'] = CTF.GaussianBlur(
            data=data[unit][self.get_param_value("range")[0]:self.get_param_value("range")[1]],
            ksize=self.get_param_value("ksize"),sigmaX=self.get_param_value("sigmaX"),sigmaY=self.get_param_value("sigmaY"))
        data["Filter_data"] = Filter_data

        if self.get_param_value("DataSave") is not None:
            OutCTData.Save_Tiff_data(Path=self.get_param_value("DataSave"),
                                     data=Filter_data['data'],
                                     SlicesStart=0,
                                     ROCRange=None,
                                     image_name=unit + '_' + "GuassianBlur")
            OutCTData.Save_H5_data_Filter(Path=self.get_param_value("DataSave"),
                                   data=data["Filter_data"],File_name=unit + '_' + "GuassianBlur")

        return {'data': data,
                "plot": {"type": "2DV",
                         "data": Filter_data['data'],
                         "title": unit + ':' + "GuassianBlur"}}




class MedianBlur(ProcessingFunction):
    """
    DESCRIPTION:MedianBlur filter
    Parameters:
        data_source_file : array
    Returns:
    """

    function_text = "MedianBlur"
    function_tip = "MedianBlur filter"

    def __init__(self):
        super().__init__()
        self._params_dict["DataSave"] = {"type": "ct_save",
                                         "value": None,
                                         "text": "Save Path",
                                         "Tip": "The data will be saved in fold as H5 and TIFF"}
        self._params_dict["data_interest"] = {"type": "enum", "value": Interest_Data_Type.unit3,
                                              "text": "Data"}
        self._params_dict["range"] = {"type": "tuple_int", "value": None,
                                              "text": "Range"}

        self._params_dict["ksize"] = {"type": "int", "value": 3, "text": "ksize",'tip':"aperture linear size; it must be odd and greater than 1, for example: 3, 5, 7 ..."}

    def run_function(self, data):
        if self.get_param_value("data_interest") == Interest_Data_Type.unit1:
            unit = 'Proj'
        if self.get_param_value("data_interest") == Interest_Data_Type.unit2:
            unit = 'Nordata'
        if self.get_param_value("data_interest") == Interest_Data_Type.unit3:
            unit = 'Recdata'
        if self.get_param_value("range") is None:
            self.set_param("range",(0,data[unit].shape[0]))
        Filter_data={}
        Filter_data["oriData"]=unit
        Filter_data["filterMethod"] = "MedianBlur"
        Filter_data["ksize"]=self.get_param_value("ksize")
        Filter_data["filterRange"] = self.get_param_value("range")

        Filter_data['data'] = CTF.MedianBlur(
            data=data[unit][self.get_param_value("range")[0]:self.get_param_value("range")[1]],
            ksize=self.get_param_value("ksize"))
        data["Filter_data"] = Filter_data

        if self.get_param_value("DataSave") is not None:
            OutCTData.Save_Tiff_data(Path=self.get_param_value("DataSave"),
                                     data=Filter_data['data'],
                                     SlicesStart=0,
                                     ROCRange=None,
                                     image_name=unit + '_' + "MedianBlur")
            OutCTData.Save_H5_data_Filter(Path=self.get_param_value("DataSave"),
                                   data=data["Filter_data"],File_name=unit + '_' + "MedianBlur")

        return {'data': data,
                "plot": {"type": "2DV",
                         "data": Filter_data['data'],
                         "title": unit + ':' + "MedianBlur"}}




class BilateralFilter(ProcessingFunction):
    """
    DESCRIPTION:Bilateral filter
    Parameters:
        data_source_file : array
    Returns:
    """

    function_text = "BilateralFilter"
    function_tip = "BilateralFilter filter"

    def __init__(self):
        super().__init__()
        self._params_dict["DataSave"] = {"type": "ct_save",
                                         "value": None,
                                         "text": "Save Path",
                                         "Tip": "The data will be saved in fold as H5 and TIFF"}
        self._params_dict["data_interest"] = {"type": "enum", "value": Interest_Data_Type.unit3,
                                              "text": "Data"}
        self._params_dict["range"] = {"type": "tuple_int", "value": None,
                                              "text": "Range"}

        self._params_dict["d"] = {"type": "int", "value": 5, "text": "d",'tip':"Diameter of each pixel neighborhood that is used during filtering. If it is non-positive, it is computed from sigmaSpace."}
        self._params_dict["sigmaColor"] = {"type": "float", "value": 30, "text": "sigmaColor", 'tip':'	Filter sigma in the color space. A larger value of the parameter means that farther colors within the pixel neighborhood (see sigmaSpace) will be mixed together, resulting in larger areas of semi-equal color.'}
        self._params_dict["sigmaSpace"] = {"type": "float", "value": 30, "text": "sigmaSpace", 'tip':'Filter sigma in the coordinate space. A larger value of the parameter means that farther pixels will influence each other as long as their colors are close enough (see sigmaColor ). When d>0, it specifies the neighborhood size regardless of sigmaSpace. Otherwise, d is proportional to sigmaSpace.'}

    def run_function(self, data):
        if self.get_param_value("data_interest") == Interest_Data_Type.unit1:
            unit = 'Proj'
        if self.get_param_value("data_interest") == Interest_Data_Type.unit2:
            unit = 'Nordata'
        if self.get_param_value("data_interest") == Interest_Data_Type.unit3:
            unit = 'Recdata'
        if self.get_param_value("range") is None:
            self.set_param("range",(0,data[unit].shape[0]))
        Filter_data={}
        Filter_data["oriData"]=unit
        Filter_data["filterMethod"] = "BilateralFilter"
        Filter_data["ksize"]=self.get_param_value("ksize")
        Filter_data["filterRange"] = self.get_param_value("range")

        Filter_data['data'] = CTF.BilateralFilter(
            data=data[unit][self.get_param_value("range")[0]:self.get_param_value("range")[1]],
            d=self.get_param_value("d"),sigmaColor=self.get_param_value("sigmaColor"),
            sigmaSpace=self.get_param_value("sigmaSpace"))
        data["Filter_data"] = Filter_data

        if self.get_param_value("DataSave") is not None:
            OutCTData.Save_Tiff_data(Path=self.get_param_value("DataSave"),
                                     data=Filter_data['data'],
                                     SlicesStart=0,
                                     ROCRange=None,
                                     image_name=unit + '_' + "BilateralFilter")
            OutCTData.Save_H5_data_Filter(Path=self.get_param_value("DataSave"),
                                   data=data["Filter_data"],File_name=unit + '_' + "BilateralFilter")

        return {'data': data,
                "plot": {"type": "2DV",
                         "data": Filter_data['data'],
                         "title": unit + ':' + "BilateralFilter"}}






@unique
class Interest_Data_Type(Enum):
    unit1 = 'Projection'
    unit2 = 'Normalized Filter'
    unit3 = 'Reconstruction'
