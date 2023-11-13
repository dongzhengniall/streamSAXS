# -*- coding: utf-8 -*-
"""
@author: WJY
"""
# lib for framework
from xrd.util.processing_sequence import ProcessingFunction
from enum import unique, Enum

# lib for function
import base_function as bf

# lib for general
import numpy as np


#%%
#------------------------------------------------------------------------------
class GuinierOperation(ProcessingFunction):
    function_text = 'Guinier Operation'
    function_tip = 'Guinier calculation(I~q-->lnI~q^2) and Guinier fitting'

    def __init__(self):
        super().__init__()
        self._params_dict['isGuinierFit'] = {'type': 'bool', 'value': False, 'text': 'Guinier Fit',
                                             'tip':"If not selected, Guinier plot will be displayed but Guinier Fit won't be done."}
        self._params_dict['autoFit'] = {'type': 'bool', 'value': False, 'text': 'Auto Calculation for Guinier region',
                                        'tip':"If selected, q range for Guinier fit is calculated automatically. If not, Guinier fit is applied to the filled q range."}
        self._params_dict['q_range'] = {'type': 'tuple_int', 'value': None, 'text': 'Guinier region',
                                        'tip': "(qmin index,qmax index)"}

    def run_function(self, data,label):
        self.param_validation()
        #self.isData1D()
        '''
        if label['xlabel']=='q (nm^-1)':
            xlabel='q^2 (nm^-2)'
        elif label['xlabel']=='q (A^-1)':
            xlabel='q^2 (A^-2)'
        else:
            raise IOError("X Label Read Error!")
        '''
        
        if self.get_params_dict('isGuinierFit') is False:
            return {'data': data,
                    'label':label,
                    'data_display':{'x0': data['x']**2, 'y0': np.log(data['y']),
                                    'xlabel':'q^2','ylabel':'lnI'}
                    }
        else:            
            result,fun_lnI=bf.guinierFit(q=data['x'],intensity=data['y'], autoFit=self.get_params_dict('autoFit'), q_range=self.get_params_dict('q_range'))
            
            if result['Rg']>0:
                return {'data': data,
                        'data_display':{'x0': data['x'][0:result['qmax_Pixel']+6]**2, 'y0': np.log(data['y'][0:result['qmax_Pixel']+6]),
                                        'xfit': data['x'][result['qmin_Pixel']:result['qmax_Pixel']+1]**2,
                                        'yfit':fun_lnI(result['I0'],result['Rg'],data['x'][result['qmin_Pixel']:result['qmax_Pixel']+1]),
                                        'xlabel':'q^2','ylabel':'lnI'},
                        'parameter_display':{'q_range':(result['qmin_Pixel'],result['qmax_Pixel'])}, # need be showed in the initial parameter position
                        'num_value':result}
            else:
                return {'data': data,
                        'data_display':{},#待补充
                        'parameter_display':{'q_range':(result['qmin_Pixel'],result['qmax_Pixel'])}, # need be showed in the initial parameter position
                        'num_value':result}
        
    def param_validation(self):
        if self.get_param_value('isGuinierFit') is True and \
            self.get_param_value('autoFit') is False and \
                self.get_param_value('q_range') is None:
            raise ValueError("The q range must be input when auto fitting isn't selected!")


#------------------------------------------------------------------------------
class PorodOperation(ProcessingFunction):
    function_text = 'Porod Operation'
    function_tip = "Porod calculation(I~q-->I*q^4~q^2) and Porod correction"
    
    def __init__(self):
        super().__init__()
        self._params_dict['fit'] = {'type': 'bool', 'value': False, 'text': 'Porod Fit',
                                    'tip':"If selected, porod fit is done."}
        self._params_dict['correction'] = {'type': 'bool', 'value': False, 'text': 'Porod Correction',
                                           'tip':"If selected, porod correction is done and high q linear range will be needed."}
        self._params_dict['q_range']={'type': 'tuple_int', 'value': None, 'text': 'high q linear range','tip':'(min,max) in pixel'}
        
    def run_function(self, data,label):
        self.param_validation()
        # self.isData1D()
        
       
        '''
        if label['xlabel']=='q (nm^-1)':
            xlabel='q^2 (nm^-2)'
        elif label['xlabel']=='q (A^-1)':
            xlabel='q^2 (A^-2)'
        else:
            raise IOError("X Label Read Error!")
        '''
        q=data['x']
        intensity=data['y']
        
        if self.get_param_value('fit')==False:
            return {'data':{'x':q,'y':intensity},
                    'label':label,
                    'data_display':{'x':q**2,'y':np.log(intensity*q**4),'xlabel':'q^2','ylabel':'I(q)*q^4'}
                    }
        else:
        
            xPorod,yPorod,slopefit,lnKfit=bf.porodFit(q, intensity, self.get_param_value('q_range'))
    
            if slopefit<0:
                result={'PorodSlope':slopefit,'PorodLnK':lnKfit,'PorodConstantK':np.exp(lnKfit),
                        'InterfaceThickPara':np.sqrt(-slopefit),'InterfaceThickness':np.sqrt(-2*np.pi*slopefit)}
            else: #slopefit>=0
                result={'PorodSlope':slopefit,'PorodLnK':lnKfit,'PorodConstantK':np.exp(lnKfit)}
    
    
            if self.get_param_value('correction')==False:
                            
                return {'data':{'x':q,'y':intensity},
                        'label':label,
                        'data_display':{'x':xPorod,'y':yPorod,'xlabel':'q^2','ylabel':'I(q)*q^4'} #辅助线待补充
                        }    
            else:
                intensity_correct,yPorod_correct=bf.porodCorrect(q, intensity, slopefit, lnKfit)
                return {'data':{'x':q,'y':intensity_correct},
                        'label':label,
                        'data_display':{'x0':xPorod,'y0':yPorod,'x1':xPorod,'y1':yPorod_correct},#辅助线待补充
                        'num_value':result                     
                        }

                
    def param_validation(self):
        if self.get_param_value('fit') is True and self.get_param_value('q_range') is None:
            raise ValueError("The high q range for Porod Operation must be input!")
        if self.get_param_value('fit') is False and self.get_param_value('correction') is True:
            raise ValueError("'Porod Fit' should be selected!")
            
            
#------------------------------------------------------------------------------
class IntegralInvariant(ProcessingFunction):
    function_text = 'Integral Invariant'
    function_tip = 'Calculate the integral invariant (Q) from SAXS curve I~q. Porod operation and Guinier operation are required in advance.'
    
    def __init__(self):
        super().__init__()
        
    def run_function(self, data,num_value,label):
        self.param_validation()
        # self.isData1D()
        
        if not 'Rg' in num_value:
            raise RuntimeWarning("Guinier operation haven't been done.")
        if not 'PorodConstantK' in num_value:
            raise RuntimeWarning("Porod operation haven't been done.")
        
        invQ=bf.integralInvariant(data['x'], data['y'], num_value['Rg'], num_value['I0'], num_value['PorodConstantK'])    
        
        return {'data': data,
                'num_value':{'InvariantQ':invQ}}
    
#------------------------------------------------------------------------------
class TParameter(ProcessingFunction):
    function_text = 'T Parameter'
    function_tip = 'Calculate T-parameter from SAXS curve I~q. Integral invariant are required in advance.'
    
    def __init__(self):
        super().__init__()
        
    def run_function(self, num_value):
        self.param_validation()
        # self.isData1D()
        
        if not 'InvariantQ' in num_value:
            raise RuntimeWarning("Integral invariant haven't been calculated.")
        
        t_parameter=4*num_value['invQ']/np.pi/num_value['PorodConstantK']   
        
        return {'num_value':{'T_Parameter':t_parameter}}

    
#------------------------------------------------------------------------------
class NormalizationSAXS(ProcessingFunction):
    function_text = 'SAXS Normalization'
    function_tip = '(I_sample-noise)/Ic_sample*coeff_sample*-(I_bg-noise)/Ic_bg*coeff_bg.'
    
    # Any:Any 注意一维二维均适用情况，显示的差别-需要判断，后续加入
    
    def __init__(self):
        super().__init__()
        self._params_dict['ic_sample'] = {'type': 'io', 'value': None, 'text': 'Ic Monitor'} 
        self._params_dict['coeff_sample'] = {'type': 'float', 'value': 1.0, 'text': 'Normalization Coefficient'}                                            
        self._params_dict['noise'] = {'type': 'float', 'value': 0.0, 'text': 'Detector Noise'}
        self._params_dict['bg'] = {'type': 'file', 'value': None, 'text': 'Background'}
        self._params_dict['ic_bg'] = {'type': 'file', 'value': None, 'text': 'Background Ic Monitor'}
        self._params_dict['coeff_bg'] = {'type': 'float', 'value': 1.0, 'text': 'Background Normalization Coefficient'}
        
    def run_function(self, data):
        self.param_validation()
        
        if self.get_param_value('ic_sample') is None:
            ic_sample=1
        else:
            ic_sample=self.get_param_value('ic_sample')
        if self.get_param_value('bg') is None:
            bg=0
        else:
            bg=self.get_param_value('bg')
        if self.get_param_value('ic_bg') is None:
            ic_bg=1
        else:
            ic_bg=self.get_param_value('ic_bg')
        
        '''
        #if self.isData1D():
        data['y']=bf.normalizeSAXS(data['y'], ic_sample, self.get_param_value('coeff_sample'),
                                   bg, ic_bg, self.get_param_value('coeff_bg'), self.get_param_value('noise'))
        
        return{'data':data,
               'data_display':{}
              }
        '''
        #if self.isData2D():
        data['image']=bf.normalizeSAXS(data['image'], ic_sample, self.get_param_value('coeff_sample'),
                                       bg, ic_bg, self.get_param_value('coeff_bg'), self.get_param_value('noise'))
        
        return {'data':data,
                'data_display':{'image':data['image'],'type':'2DV'}
                }

        
    def param_validation(self):
        if self.get_param_value('ic_sample') is None:
            raise ValueError("'Ic Monitor' must be selected!")


