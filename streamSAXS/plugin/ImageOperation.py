# -*- coding: utf-8 -*-
"""
@author: WJY
"""
#%%
# lib for framework
from util.processing_sequence import ProcessingFunction
from enum import unique, Enum

# generic lib
# import numpy as np

# lib for function
import plugin.base_function as bf
import plugin.base_function_laue as bfl

#%%
#------------------------------------------------------------------------------
class ImageFlip(ProcessingFunction):
    function_text = "Image Flip"
    function_tip = "Along X Axis or Y Axis"
    
    def __init__(self):
        super().__init__()
        self._params_dict["along_axis"] = {"type": "enum", "value":ImageFlip_Unit.unit1, "text": "Direction"}
    
    def run_function(self,data):
        self.param_validation()
        #self.isData2D()
        
        data['image']=bf.imageFlip(data['image'],self._params_dict["along_axis"])
        
        return {"data":data,
                "plot":{'image':data['image'],'type':'2DV'}
                }

    def param_validation(self):
        pass

@unique
class ImageFlip_Unit(Enum):
    unit1 = "Along Y Axis"
    unit2 = "Along X Axis"


class PeakNumbers(ProcessingFunction):
    function_text = "Peak Numbers"
    function_tip = "Peak numbers of diffraction pattern"

    def __init__(self):
        super().__init__()
        self._params_dict["areaLimit"] = {"type": "float", "value": 4, "text": "Minimum area of single peaks"}
        self._params_dict['threshold'] = {'type': 'float', 'value': 10000, 'text': 'Maximum intensity', 'tip': "Maximum intensity of diffraction pattern"}

    def run_function(self, data):
        self.param_validation()
        # self.isData2D()

        peak_nums = bfl.Find_peaks(data=data['image'], picture_number=1, areaLimit=self.get_param_value("areaLimit"), threshold=self.get_param_value("threshold"))
        print(peak_nums)
        return {"data": data
                }

    # def param_validation(self):
    #     pass
