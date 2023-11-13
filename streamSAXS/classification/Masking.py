# -*- coding: utf-8 -*-
"""
@author: WJY
"""
#%%
# lib for framework
from xrd.util.processing_sequence import ProcessingFunction

# lib for function
import base_function as bf

#%%
class UserDefinedMask2D(ProcessingFunction):
    function_text = "User-defined Mask 2D"
    function_tip = "Import user-defined mask file." 
    
    def __init__(self):
        super().__init__()
        self._params_dict["mask_file"] = {"type": "file", "value": None, "text": "Mask File",
                                          "tip":"File extensions such as '.tif', '.edf' are recommended."}

        
    def run_function(self,data,**kwargs):
        self.param_validation()
        #self.isData2D()
                      
        mask=kwargs["mask_file"]
        data['mask']=mask
        
        return {'data': data
                }
    
    def param_validation(self):
        if self.get_param_value("mask_file") is None:
            raise ValueError("'Mask File' must be input.")


class ThresholdMask2D(ProcessingFunction):
    
    function_text = "Threshold Mask 2D"
    function_tip = "(MinValue,MaxValue)"
    
    def __init__(self):
        super().__init__()
        self._params_dict["minimum"] = {"type": "int", "value": None, "text": "Min Value"}
        self._params_dict["maximum"] = {"type": "int", "value": None, "text": "Max Value"}
        
    def run_function(self,data):
        self.param_validation()
        #self.isData2D()
                      
        mask = bf.thresholdMask2D(data['image'],self._params_dict["minimum"],self._params_dict["maximum"])
        data['mask']=mask
        
        return {'data': data
                }

    def param_validation(self):
        pass


    
class UserDefinedMask1D(ProcessingFunction):

    function_text = "User-defined Mask 1D"
    function_tip = "User-defined regions in 1D Curve will be ignored."

    def __init__(self):
        super().__init__()
        self._params_dict["index"] = {"type": "tuple_int", "value": None, "text": "Masked regions (X index)",
                                      "tip":"Monotonically increasing (start1, End1, Start2, End2, ...). If None, default mask is YAxis<=0"}
    def run_function(self,data,label):
        self.param_validation()
        #self.isData1D()
        
        x,y=bf.userDefinedMask1D(data['x'],data['y'],self.get_param_value("index"))
                    
        return {'data': {'x':x,'y':y},
                'label':label, # label is unchanged
                'data_display':{'data': {'x':x,'y':y},'type':'1DP','label':label}
                }

    def param_validation(self):
        if self.get_param_value("index") is not None and len(self.get_param_value("index"))%2==1:
            raise ValueError("The number of input x index must be even")