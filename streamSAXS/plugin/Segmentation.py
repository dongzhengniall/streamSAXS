from util.processing_sequence import ProcessingFunction
from enum import unique, Enum
# import numpy as np
import plugin.CT_Process_Function as CTF
from util.io import OutCTData
import cv2


class InteractiveThreshold(ProcessingFunction):
    """
    DESCRIPTION:InteractiveThreshold
    Parameters:
        data_source_file : array
    Returns:
    """

    function_text = "InteractiveThreshold"
    function_tip = "Interactive Threshold"

    def __init__(self):
        super().__init__()
        self._params_dict["DataSave"] = {"type": "ct_save",
                                         "value": None,
                                         "text": "Save Path",
                                         "Tip": "The data will be saved in fold as H5 and TIFF"}

        self._params_dict["thresh"] = {"type": "float", "value": -0.2,
                                              "text": "thresh","tips":"	threshold value"}

        self._params_dict["maxval"] = {"type": "float", "value": 0, "text": "maxval",'tip':"maximum value to use with the THRESH_BINARY and THRESH_BINARY_INV thresholding types"}

        self._params_dict["thresholdtype"] = {"type": "enum", "value": InteractiveThreshold_Type.unit1,
                                              "text": "thresholding type"}

    def run_function(self, data):
        Threshold_data = {}
        if self.get_param_value("thresholdtype") == InteractiveThreshold_Type.unit1:
            TypeUnit = cv2.THRESH_BINARY
            Threshold_data["type"] = "THRESH_BINARY"
        elif self.get_param_value("thresholdtype") == InteractiveThreshold_Type.unit2:
            TypeUnit = cv2.THRESH_BINARY_INV
            Threshold_data["type"] = "THRESH_BINARY_INV"
        elif self.get_param_value("thresholdtype") == InteractiveThreshold_Type.unit3:
            TypeUnit = cv2.THRESH_TRUNC
            Threshold_data["type"] = "THRESH_TRUNC"
        elif self.get_param_value("thresholdtype") == InteractiveThreshold_Type.unit4:
            TypeUnit = cv2.THRESH_TOZERO
            Threshold_data["type"] = "THRESH_TOZERO"
        elif self.get_param_value("thresholdtype") == InteractiveThreshold_Type.unit5:
            TypeUnit = cv2.THRESH_TOZERO_INV
            Threshold_data["type"] = "THRESH_TOZERO_INV"
        elif self.get_param_value("thresholdtype") == InteractiveThreshold_Type.unit6:
            TypeUnit = cv2.THRESH_BINARY + cv2.THRESH_OTSU
            Threshold_data["type"] = "THRESH_BINARY+THRESH_OTSU"

        Threshold_data["ThresholdMethod"] = "InteractiveThreshold"
        Threshold_data["thresh"] = self.get_param_value("thresh")
        Threshold_data["maxval"] = self.get_param_value("maxval")

        if "Filter_data" in data:
            Thredata=data["Filter_data"]['data']
        else:
            Thredata = data["Recdata"]

        Threshold_data['data'] = CTF.InteractiveThreshold(data=Thredata,Imin=self.get_param_value("thresh"),
                                          Imax=self.get_param_value("maxval"),Ttype=TypeUnit)
        data["Threshold_data"] = Threshold_data

        if self.get_param_value("DataSave") is not None:
            OutCTData.Save_H5_data_Filter(Path=self.get_param_value("DataSave"),
                                          data=data["Threshold_data"], File_name=Threshold_data["ThresholdMethod"])

        return {'data': data,
                "plot": {"type": "2DV",
                         "data": Threshold_data['data'],
                         "title": Threshold_data["ThresholdMethod"]+':'+Threshold_data["type"]}}


@unique
class InteractiveThreshold_Type(Enum):
    unit1 = 'THRESH_BINARY'
    unit2 = 'THRESH_BINARY_INV'
    unit3 = 'THRESH_TRUNC'
    unit4 = 'THRESH_TOZERO'
    unit5 = 'THRESH_TOZERO_INV'
    unit6 = 'THRESH_BINARY+THRESH_OTSU'




class KmeansSegmentation(ProcessingFunction):
    """
    DESCRIPTION:adaptiveInteractiveThreshold
    Parameters:
        data_source_file : array
    Returns:
    """

    function_text = "K-means Segmentation"
    function_tip = "K-means Segmentation"

    def __init__(self):
        super().__init__()
        self._params_dict["DataSave"] = {"type": "ct_save",
                                         "value": None,
                                         "text": "Save Path",
                                         "Tip": "The data will be saved in fold as H5 and TIFF"}

        self._params_dict["nclusters"] = {"type": "int", "value": 3, "text": "nclusters"}
        self._params_dict["CriteriaType"] = {"type": "enum", "value": KmeansCriteriaType.unit1,
                                              "text": "thresholding type","Tip":"cv.TERM_CRITERIA_EPS - stop the algorithm iteration if specified accuracy, epsilon, is reached.;  cv.TERM_CRITERIA_MAX_ITER - stop the algorithm after the specified number of iterations, max_iter. ;cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER - stop the iteration when any of the above condition is met."}

        self._params_dict["max_iter"] = {"type": "int", "value": 50, "text": "max_iter",'tip':"An integer specifying maximum number of iterations."}

        self._params_dict["epsilon"] = {"type": "float", "value": 0.2, "text": "epsilon",'tip':"Required accuracy"}

        self._params_dict["attempts"] = {"type": "int", "value": 5, "text": "max_iter", 'tip': "Flag to specify the number of times the algorithm is executed using different initial labellings. The algorithm returns the labels that yield the best compactness. This compactness is returned as output."}

        self._params_dict["FlagsType"] = {"type": "enum", "value": KmeansflagsType.unit1,
                                              "text":"flags type",'tip':'This flag is used to specify how initial centers are taken.'}

    def run_function(self, data):
        Threshold_data = {}
        if self.get_param_value("CriteriaType") == KmeansCriteriaType.unit1:
            CriteriaType = cv2.TERM_CRITERIA_EPS
            Threshold_data['CriteriaType']="TERM_CRITERIA_EPS"
        elif self.get_param_value("CriteriaType") == KmeansCriteriaType.unit2:
            CriteriaType = cv2.TERM_CRITERIA_MAX_ITER
            Threshold_data['CriteriaType'] = "TERM_CRITERIA_MAX_ITER"
        elif self.get_param_value("CriteriaType") == KmeansCriteriaType.unit3:
            CriteriaType = cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER
            Threshold_data['CriteriaType'] = "TERM_CRITERIA_EPS + TERM_CRITERIA_MAX_ITER"

        if self.get_param_value("FlagsType") == KmeansflagsType.unit1:
            FlagsType = cv2.KMEANS_PP_CENTERS
            Threshold_data['FlagsType']="KMEANS_PP_CENTERS"
        elif self.get_param_value("FlagsType") == KmeansflagsType.unit2:
            FlagsType = cv2.KMEANS_RANDOM_CENTERS
            Threshold_data['FlagsType'] = "KMEANS_RANDOM_CENTERS"


        Threshold_data = {}
        Threshold_data["ThresholdMethod"] = "KmeansSegmentation"
        Threshold_data["nclusters"] = self.get_param_value("nclusters")
        Threshold_data["max_iter"] = self.get_param_value("max_iter")
        Threshold_data["epsilon"] = self.get_param_value("epsilon")
        Threshold_data["attempts"] = self.get_param_value("attempts")

        if "Filter_data" in data:
            Thredata=data["Filter_data"]['data']
        else:
            Thredata = data["Recdata"]

        Threshold_data['data'] = CTF.KmeansSegmentation(data=Thredata,
                                                        nclusters=self.get_param_value("nclusters"),
                                                        CriteriaType=CriteriaType,
                                                        max_iter=self.get_param_value("max_iter"),
                                                        epsilon=self.get_param_value("epsilon"),
                                                        attempts=self.get_param_value("attempts"),
                                                        FlagsType=FlagsType)

        data["Threshold_data"] = Threshold_data

        if self.get_param_value("DataSave") is not None:
            OutCTData.Save_H5_data_Filter(Path=self.get_param_value("DataSave"),
                                          data=data["Threshold_data"], File_name=Threshold_data["ThresholdMethod"])

        return {'data': data,
                "plot": {"type": "2DV",
                         "data": Threshold_data['data'],
                         "title": Threshold_data["ThresholdMethod"]}}


@unique
class KmeansCriteriaType(Enum):
    unit1 = 'TERM_CRITERIA_EPS'
    unit2 = 'TERM_CRITERIA_MAX_ITER'
    unit3 = 'TERM_CRITERIA_EPS + TERM_CRITERIA_MAX_ITER'

@unique
class KmeansflagsType(Enum):
    unit1 = 'KMEANS_PP_CENTERS'
    unit2 = 'KMEANS_RANDOM_CENTERS'

