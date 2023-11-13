# -*- coding: utf-8 -*-
# %%
# lib for framework
from util.processing_sequence import ProcessingFunction
import plugin.base_function as bf

# lib for function


# %%
class UserDefinedMask2D(ProcessingFunction):
    function_text = "User-defined Mask 2D"
    function_tip = "Import user-defined mask file."

    def __init__(self):
        super().__init__()
        self._params_dict["mask_file"] = {"type": "file", "value": None, "text": "Mask File",
                                          "tip": "File extensions such as '.tif', '.edf' are recommended."}

    def run_function(self, data, **kwargs):
        self.param_validation()
        # self.isData2D()

        mask = kwargs["mask_file"]
        data['mask'] = mask

        return {'data': data}

    def param_validation(self):
        if self.get_param_value("mask_file") is None:
            raise ValueError("'Mask File' must be input.")


class ThresholdMask2D(ProcessingFunction):
    function_text = "Threshold Mask 2D"
    function_tip = "(MinValue,MaxValue)"

    def __init__(self):
        super().__init__()
        self._params_dict["minimum"] = {"type": "int", "value": 0, "text": "Min Value"}
        self._params_dict["maximum"] = {"type": "int", "value": 100000, "text": "Max Value"}

    def run_function(self, data):
        self.param_validation()
        # self.isData2D()

        mask = bf.thresholdMask2D(data['image'], self.get_param_value('minimum'), self.get_param_value('maximum'))
        data['mask'] = mask

        return {'data': data
                }

    def param_validation(self):
        pass
