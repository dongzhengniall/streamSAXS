# -*- coding: utf-8 -*-
"""
@author: WJY
"""
#%%
# lib for framework
from xrd.util.processing_sequence import ProcessingFunction
from enum import unique, Enum

# generic lib
# import numpy as np

# lib for function
import base_function as bf

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