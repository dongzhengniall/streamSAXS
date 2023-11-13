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
class DetectorCalibrationPyFAI(ProcessingFunction):
    function_text = "Detector Calibration via PyFAI"
    function_tip = "Import detector calibration file."

    def __init__(self):
        super().__init__()
        self._params_dict["calibration_file"] = {"type": "file", "value": None, "text": "PyFAI Calibration File","tip":"File extension is '.poni'"}
        
    def run_function(self,**kwargs):
        self.param_validation()
        #self.isData2D()
        
        integrator=kwargs["calibration_file"]
        
        return {# "data":data, # data isn't need if no plot 
                # "plot":{'image':data['image'],'type':'2DV'}, #need to display center point in 2D image and detector information in title
                "objectset": {"integrator":integrator}
                }
        
    def param_validation(self):
        if self.get_param_value("calibration_file") is None:
            raise ValueError("'Calibration File' must be input.")
            
class DetectorCalibrationFit2d(ProcessingFunction):
    function_text = "Detector Calibration via fit2d"
    function_tip = "Image must be flipped along Y axis when this operation is selected."
    
    def __init__(self):
        super().__init__()
        self._params_dict["wavelength"] = {"type": "float", "value": None, "text": "Wavelength(Angstrom)"}
        self._params_dict["sdd"] = {"type": "float", "value": None, "text": "Distance(mm)"}
        self._params_dict["centerX"] = {"type": "float", "value": None, "text": "Beam Center X (Pixel)"}
        self._params_dict["centerY"] = {"type": "float", "value": None, "text": "Beam Center Y (Pixel)"}
        self._params_dict["pixelX"] = {"type": "float", "value": None, "text": "X Pixel Size (Microns)"}
        self._params_dict["pixelY"] = {"type": "float", "value": None, "text": "Y Pixel Size (Microns)"}
        self._params_dict["rotation"] = {"type": "float", "value": 0.0, "text": "Rotation Angle (Degree)"}
        self._params_dict["tilt"] = {"type": "float", "value": 0.0, "text": "Tilt in Plane (Degree)"}
    
    def run_function(self):
        self.param_validation()
        #self.isData2D()
        
        integrator=bf.detectorCalibrationFit2d(self._params_dict["wavelength"]*1e-10,
                                               self._params_dict["sdd"],
                                               self._params_dict["centerX"],
                                               self._params_dict["centerY"],
                                               self._params_dict["pixelX"],
                                               self._params_dict["pixelY"],
                                               self._params_dict["rotation"],
                                               self._params_dict["tilt"])
        
        return {#"data":data,
                #"plot":{'image':data['image'],'type':'2DV'}, #need to display center point in 2D image and detector information in title
                "objectset": {"integrator":integrator}
                }
    
    def param_validation(self):
        if self.get_param_value("wavelength") or self.get_param_value("sdd") \
            or self.get_param_value("centerX") or self.get_param_value("centerY") \
                or self.get_param_value("pixelX") or self.get_param_value("pixelX") is None:
                    raise ValueError("Fit2d parameters must be input.")

    

    

