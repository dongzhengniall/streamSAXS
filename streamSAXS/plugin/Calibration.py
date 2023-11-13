# -*- coding: utf-8 -*-
# %%
# lib for framework
from util.processing_sequence import ProcessingFunction
# lib for function


# %%
class DetectorCalibrationPyFAI(ProcessingFunction):
    function_text = "Detector Calibration via PyFAI"
    function_tip = "Import detector calibration file."

    def __init__(self):
        super().__init__()
        self._params_dict["calibration_file"] = {"type": "file", "value": "E:/dongzheng/XRD_code/data/SSRF-10U-202107/SSRF-10U-202107/SSRF_10U/202107SSRF/cailb/2023-05-03_zzz_AgBH_sample-pyfai.poni", "text": "PyFAI Calibration File",
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
