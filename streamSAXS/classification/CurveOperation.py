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
class CurveCrop(ProcessingFunction):
    function_text = "Curve Crop"
    function_tip = "Valid data selection"
    
    def __init__(self):
        super().__init__()
        self._params_dict["start"] = {"type": "int", "value":None, "text": "Start Index"}
        self._params_dict["end"] = {"type": "int", "value":None, "text": "End Index"}
    
    def run_function(self,data):
        self.param_validation()
        #self.isData1D()
        x=data['x']
        y=data['y']
        
        if self.get_params_dict["start"]!=None and self.get_params_dict["end"]!=None:
            x=x[self.get_params_dict["start"]:self.get_params_dict["end"]]
        if self.get_params_dict["start"]!=None and self.get_params_dict["end"]==None:
            x=x[self.get_params_dict["start"]:]
        if self.get_params_dict["start"]==None and self.get_params_dict["end"]!=None:
            x=x[0:self.get_params_dict["end"]]            
        
        return {"data":{'x':x,'y':y},
                "plot":{'x':x,'y':y,'type':'1DV'}
                }
        
    def param_validation(self):
        pass

#------------------------------------------------------------------------------    
class CurvePositive(ProcessingFunction):
    function_text = "Take Positive Curve"
    function_tip = "Ignore data<=0"
    
    def __init__(self):
        super().__init__()
    
    def run_function(self,data):
        self.param_validation()
        #self.isData1D()
        
        x,y=bf.curvePositive(data['x'], data['y'])           
        
        return {"data":{'x':x,'y':y},
                "plot":{'x':x,'y':y,'type':'1DV'}
                }
        
    def param_validation(self):
        pass