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

        x,y=bf.curveCrop(x,y,self.get_param_value("start"),self.get_param_value("end"))

        '''
        if self.get_param_value["start"]!=None and self.get_params_value["end"]!=None:
            x = x[self.get_params_value["start"]:self.get_params_value["end"]]
            y = y[self.get_params_value["start"]:self.get_params_value["end"]]
        if self.get_params_dict["start"]!=None and self.get_params_value["end"]==None:
            x = x[self.get_params_value["start"]:]
            y = y[self.get_params_value["start"]:]
        if self.get_params_value["start"]==None and self.get_params_value["end"]!=None:
            x = x[0:self.get_params_value["end"]]
            y = y[0:self.get_params_value["end"]]
        '''
        
        return {"data":{'x':x,'y':y},
                "plot":{'data':{'x':x,'y':y},
                        'type':'1DP'
                        }
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