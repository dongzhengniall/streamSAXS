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
        self._params_dict["mask_file"] = {"type": "file", "value": "E:/dongzheng/XRD_code/code/testdata/mouse/parameter/mask01.tif", "text": "Mask File",
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


class UserDefinedMask1D(ProcessingFunction):
    function_text = "User-defined Mask 1D"
    function_tip = "User-defined regions in 1D Curve will be ignored."

    def __init__(self):
        super().__init__()
        self._params_dict["index"] = {"type": "tuple_int", "value": (39,50,164,172), "text": "Masked regions (X index)"}

    def run_function(self, data, label):
        self.param_validation()
        # self.isData1D()

        x, y = bf.userDefinedMask1D(data['x'], data['y'], self.get_param_value("index"))

        return {'data': {'x': x, 'y': y},
                'label': label,  # label is unchanged
                'plot': {'data': {'x': x, 'y': y}, 'type': '1DP', 'label': label}
                }

    def param_validation(self):
        if self.get_param_value("index") is not None and len(self.get_param_value("index")) % 2 == 1:
            raise ValueError("The number of input x index must be even")
