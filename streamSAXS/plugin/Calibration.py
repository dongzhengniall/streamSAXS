# -*- coding: utf-8 -*-
# %%
# lib for framework
from util.processing_sequence import ProcessingFunction
# lib for function
import plugin.base_function as bf

# %%
class DetectorCalibrationPyFAI(ProcessingFunction):
    function_text = "Detector Calibration via PyFAI"
    function_tip = "Import detector calibration file."

    def __init__(self):
        super().__init__()
        self._params_dict["calibration_file"] = {"type": "file", "value": "D:/dongzheng/bamboo-saxsCT/cal/waxd.poni", "text": "PyFAI Calibration File",
                                                 "tip": "File extension is '.poni'"}

    def run_function(self, data, **kwargs):
        self.param_validation()
        # self.isData2D()
        integrator = kwargs["calibration_file"]

        return {"data": data,  # data isn't need if no plot
                "plot": {'image': data['image'], 'type': '2DV'},  # need to display center point in 2D image and detector information in title
                "objectset": {"integrator": integrator}
                }

    def param_validation(self):
        if self.get_param_value("calibration_file") is None:
            raise ValueError("'Calibration File' must be input.")


class FlatCorrection(ProcessingFunction):
    function_text = "Flat Field Correction"
    function_tip = "Import flat-field file."

    def __init__(self):
        super().__init__()
        self._params_dict["flat_file"] = {"type": "file", "value": None, "text": "Flat File", "tip": "None"}

    def run_function(self, data, objectset, **kwargs):
        self.param_validation()
        # self.isData2D()

        flat = kwargs["flat_file"]
        data['image'] = bf.flatCorrection(objectset['integrator'], data['image'], flat)

        return {"data": data,
                "plot": {'image': data['image'], 'type': '2DV'}
                }

    def param_validation(self):
        if self.get_param_value("flat_file") is None:
            raise ValueError("'Flat field File' must be input.")


class DarkCorrection(ProcessingFunction):
    function_text = "Dark Current Correction"
    function_tip = "Import dark-current file."

    def __init__(self):
        super().__init__()
        self._params_dict["dark_file"] = {"type": "file", "value": None, "text": "Dark File", "tip": "None"}

    def run_function(self, data, objectset, **kwargs):
        self.param_validation()
        # self.isData2D()

        dark = kwargs["dark_file"]
        data['image'] = bf.darkCorrection(objectset['integrator'], data['image'], dark)

        return {"data": data,
                "plot": {'image': data['image'], 'type': '2DV'}
                }

    def param_validation(self):
        if self.get_param_value("dark_file") is None:
            raise ValueError("'Dark current File' must be input.")