# -*- coding: utf-8 -*-
"""
@author: WJY
"""
# lib for framework
from xrd.util.processing_sequence import ProcessingFunction
from enum import unique, Enum

# lib for function
import base_function as bf

#%%

class SinglePeakFit(ProcessingFunction):
    function_text = 'Single Peak Fitting'
    function_tip = 'Fit diffraction curve with single peak'

    def __init__(self):
        super().__init__()
        self._params_dict['autoFit'] = {'type': 'bool', 'value': True, 'text': 'Auto Fitting',
                                        'tip':"If selected, initial values of fitting parameters aren't necessarily given. If not selected, values are required."}
        self._params_dict['x_range'] = {'type': 'tuple_int', 'value': None, 'text': 'x range','tip':'(min,max) in pixel'}
        self._params_dict['peak_type'] = {'type': 'enum', 'value': SinglePeakFit_PeakType.type1, 'text': 'Peak Type'}
        self._params_dict['peak_center'] = {'type': 'float', 'value': None, 'text': 'Peak Center'}
        self._params_dict['fixedPeakCenter'] = {'type': 'bool', 'value': False, 'text': 'Peak Center Fixed'}
        self._params_dict['fwhm'] = {'type': 'float', 'value': None, 'text': 'FWHM'}
        self._params_dict['fixedFWHM'] = {'type': 'bool', 'value': False, 'text': 'FWHM Fixed'}
        self._params_dict['area'] = {'type': 'float', 'value': None, 'text': 'Area','tip':'format such as FWHM*H is also supported and H means guess value for peak height'}
        self._params_dict['fixedArea'] = {'type': 'bool', 'value': False, 'text': 'Area Fixed'}
        self._params_dict['k'] = {'type': 'float', 'value': None, 'text': 'Linear Background Slope'}
        self._params_dict['fixedSlope'] = {'type': 'bool', 'value': False, 'text': 'Slope Fixed'}
        self._params_dict['d'] = {'type': 'float', 'value': None, 'text': 'Linear Background Intercept'}
        self._params_dict['fixedIntercept'] = {'type': 'bool', 'value': False, 'text': 'Intercept Fixed'}
        self._params_dict['n'] = {'type': 'float', 'value': None, 'text': 'Lorentz Ratio','tip':'only used for Vogit Fitting'}
        self._params_dict['fixedRatio'] = {'type': 'bool', 'value': False, 'text': 'Ratio Fixed'}
 
    def run_function(self, data,label):
        self.param_validation()
        self.isData1D()
        
        x=data['x'][self.get_param_value('x_range')[0]:self.get_param_value('x_range')[1]+1] #attention the last value shoule +1
        y=data['y'][self.get_param_value('x_range')[0]:self.get_param_value('x_range')[1]+1]
        
        result,yfit=bf.singlePeakFit(x,y,self.get_param_value('autoFit'),self.get_param_value('peak_type'),
                                     self.get_param_value('peak_center'),self.get_param_value('fwhm'),
                                     self.get_param_value('area'),self.get_param_value('k'),
                                     self.get_param_value('d'),self.get_param_value('n'),
                                     self.get_param_value('fixedPeakCenter'),self.get_param_value('fixedFWHM'),
                                     self.get_param_value('fixedArea'),self.get_param_value('fixedSlope'),
                                     self.get_param_value('fixedIntercept'),self.get_param_value('fixedRatio'))
                
        return {'data':data,
                'data_display':{},
                'parameter_display':result,
                'num_value':result}
                       
    
    def param_validation(self):
        if self.get_param_value('autoFit') is False:
            if self.get_param_value('peak_center') is None or self.get_param_value('fwhm') is None \
                or self.get_param_value('area') is None or self.get_param_value('k') is None \
                    or self.get_param_value('d') is None: 
                raise ValueError("The initial value must be input when auto fitting isn't selected")
            
@unique
class SinglePeakFit_PeakType(Enum):
    type1 = "Gaussian+LinearBg"
    type2 = "Lorentz+LinearBg"
    type3 = "Vogit+LinearBg"
