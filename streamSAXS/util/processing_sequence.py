from enum import Enum
import os
from abc import abstractmethod
from collections import OrderedDict

from util.data_verification import DataVerification
from util.processing_plugin import get_classes_from_path, filter_classes_by_function


class ProcessingFunction(object):
    function_text = ""
    function_tip = ""

    """
    DESCRIPTION: Encapsulate the parameters and implementation methods of each function as a class
    Attributes for input:
        _text_names: list
             The name displayed to the user
        _keys: list
             Parameter name, consistent with the parameter name of the calling function
        _vars: dict
             A dictionary that stores parameter type and value, the key is the parameter name, and the value is the user input
        __last_step_input_vars:dict
             The value passed down from the previous step
             key:
                 integrator: obj of class AzimuthalIntegrator with calibration parameters
                 data: 1D/2D data
                 res1D: Integrate1dResult namedtuple with (q,I,sigma) +extra informations in it.
                 res2D :azimuthaly regrouped intensity, q/2theta/r pos. and chi pos.

    """

    def __init__(self):
        self._params_dict = OrderedDict()

    @abstractmethod
    def run_function(self):
        pass

    def param_validation(self):
        return None

    def get_param_text(self, key):
        return self._params_dict[key]["text"]

    def get_param_value(self, key):
        if key in self._params_dict:
            # if self._params_dict[key]["type"] == "enum":
            #     return self._params_dict[key]["value"].value
            return self._params_dict[key]["value"]

    def get_plan_param_value(self, key):
        if key in self._params_dict:
            if self._params_dict[key]["type"] == "enum":
                return self._params_dict[key]["value"].value
            return self._params_dict[key]["value"]

    def get_param(self, key):
        return self._params_dict[key]["value"]

    def get_params(self):
        return self._params_dict

    def get_params_key(self):
        return list(self._params_dict.keys())

    def set_param(self, key, value):
        if self._params_dict[key]["type"] == "str":
            self._params_dict[key]["value"] = DataVerification.str(value)
            return
        if self._params_dict[key]["type"] == "h5dataset":
            self._params_dict[key]["value"] = DataVerification.str(value)
            return
        if self._params_dict[key]["type"] == "data_button":
            self._params_dict[key]["value"] = DataVerification.str(value)
            return
        if self._params_dict[key]["type"] == "int":
            self._params_dict[key]["value"] = DataVerification.int(value)
            return
        if self._params_dict[key]["type"] == "float":
            self._params_dict[key]["value"] = DataVerification.float(value)
            return
        if self._params_dict[key]["type"] == "tuple":
            self._params_dict[key]["value"] = DataVerification.tuple(value)
            return
        if self._params_dict[key]["type"] == "tuple_float":
            self._params_dict[key]["value"] = DataVerification.tuple_float(value)
            return
        if self._params_dict[key]["type"] == "tuple_int":
            self._params_dict[key]["value"] = DataVerification.tuple_int(value)
            return
        if self._params_dict[key]["type"] in ["file", "save"]:
            self._params_dict[key]["value"] = DataVerification.str(value)
            return
        if self._params_dict[key]["type"] == "enum":
            self._params_dict[key]["value"] = DataVerification.enum(value)
            return
        if self._params_dict[key]["type"] == "bool":
            self._params_dict[key]["value"] = DataVerification.bool(value)
            return
        if self._params_dict[key]["type"] == "io":
            self._params_dict[key]["value"] = DataVerification.io(value)
            return


class StepAttribute(object):
    def __init__(self, step_text, attribute=None, input_step_number=[]):
        self.step_text = step_text
        self.attribute = attribute
        self.step_input_number = input_step_number
        self.step_connect_widget = ""
        self.step_output_params = None


class ProcessingSequence(list):
    def __init__(self):
        list.__init__([])
        self._data_in_memory = {}
        self.step_object_dict = OrderedDict()
        module_file_path = os.path.join(os.path.dirname(__file__) + '\\..\\plugin')
        classes = get_classes_from_path(file_path=module_file_path, file_type=".py")
        classes_list = filter_classes_by_function(classes, "function_text")

        for classes in classes_list:
            self.step_object_dict[classes.__module__ + "." + classes.function_text] = [classes, classes.function_tip]

    def add_step_in_data(self, step_text, attribute, input_step_number):
        self.append(StepAttribute(step_text, attribute, input_step_number))

    def del_step_in_data(self, index):
        self.RemoveAt(index)


if __name__ == '__main__':
    a = ProcessingSequence()
