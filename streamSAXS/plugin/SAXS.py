# -*- coding: utf-8 -*-
"""
@author: WJY
"""
# lib for framework
from util.processing_sequence import ProcessingFunction
from enum import unique, Enum

# lib for function
import plugin.base_function as bf

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
        self._params_dict['q_range'] = {'type': 'tuple_float', 'value': None, 'text': 'Guinier region',
                                        'tip': "(qmin ,qmax )"}

        self._params_dict['Rg'] = {'type': 'float', 'value': None, 'text': 'Rg', 'tip': "Rg"}
        self._params_dict['rg_err'] = {'type': 'float', 'value': None, 'text': 'Rg_err', 'tip': "Rg_err"}
        self._params_dict['I0'] = {'type': 'float', 'value': None, 'text': 'I0', 'tip': "I0"}
        self._params_dict['i0_err'] = {'type': 'float', 'value': None, 'text': 'I0_err', 'tip': "I0_err"}

        self._params_dict['q_range_Rg'] = {'type': 'tuple_float', 'value': None, 'text': 'qminRg,qmaxRg',
                                   'tip': "qminRg,qmaxRg"}


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
        
        if self.get_param_value('isGuinierFit') is False:
            data['GuinierX']=data['x']**2
            data['GuinierY'] = np.log(data['y'])
            data['result']=None
            return {'data': data,
                    'plot':{'data': {'x':data['x']**2, 'y': np.log(data['y'])},
                         'type': '1DP',
                         'label': {'xlabel': 'q^2', 'ylabel': 'lnI'},
                        'title': "Guinier plot"}
                    }

        else:
            result,fun_lnI=bf.guinierFit(q=data['x'],intensity=data['y'], autoFit=self.get_param_value('autoFit'), q_range=self.get_param_value('q_range'))
            if result['Rg']>0:
                self.set_param('q_range', (result['qmin'], result['qmax']))
                self.set_param('Rg', result['Rg'])
                self.set_param('rg_err', result['rg_err'])
                self.set_param('I0', result['I0'])
                self.set_param('i0_err', result['i0_err'])
                self.set_param('q_range_Rg', (result['qrg_min'], result['qrg_max']))
                data['GuinierX'] = data['x'][result['qmin_Pixel']:result['qmax_Pixel']+1]**2
                data['GuinierY'] = fun_lnI(result['I0'],result['Rg'],data['x'][result['qmin_Pixel']:result['qmax_Pixel']+1])
                data['result'] = result
                return {'data': data,
                        'plot': {'data': [
                                        {'name': 'guinier', 'style': 'line', 'color': 'b', 'legend': 'Guinier',
                                         'x':data['x'][0:result['qmax_Pixel']+6]**2, 'y': np.log(data['y'][0:result['qmax_Pixel']+6])},
                                        {'name': 'guinierFit', 'style': 'line', 'color': 'r', 'legend': 'GuinierFit',
                                        'x': data['x'][result['qmin_Pixel']:result['qmax_Pixel']+1]**2,
                                        'y': fun_lnI(result['I0'],result['Rg'],data['x'][result['qmin_Pixel']:result['qmax_Pixel']+1])}
                                        ],
                                'type': '1DP',
                                'label': {'xlabel': 'q^2', 'ylabel': 'lnI'},
                                'title': "GuinierFit"},
                        'num_value':result
                        # "DataSave_Update":{
                        #     'GuinierFitParas':[result['Rg'], result['rg_err'] ,result['I0'], result['i0_err'],
                        #                        result['qmin'],result['qmax'],result['qrg_min'],result['qrg_max'],
                        #                        result['qmin_Pixel'], result['qmax_Pixel'], result['r_sq']],
                        #     'GuinierFitX':data['x']**2,
                        #     "GuinierFitY":fun_lnI(result['I0'],result['Rg'],data['x'])
                        #                   },
                        # "DataSave_Static":{
                        #     'GuinierFitParas_Description','Rg,Rg_err,I0,I0_err,qmin,qmax,qrg_min,qrg_max,qmin_Pixel,qmax_Pixel,r_sq'
                        #                    }
                        }

            else:
                ###############失败后怎么办呢######################
                data['GuinierX'] = data['x'] ** 2
                data['GuinierY'] = np.log(data['y'])
                data['result'] = None
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
        self._params_dict['q_range']={'type': 'tuple_int', 'value': (10,1000), 'text': 'high q linear range','tip':'(min,max) in pixel'}

        self._params_dict['PorodSlope'] = {'type': 'float', 'value': None, 'text': 'PorodSlope','tip':'PorodSlope'}
        self._params_dict['PorodLnK'] = {'type': 'float', 'value': None, 'text': 'PorodLnK', 'tip': 'PorodLnK'}
        self._params_dict['PorodConstantK'] = {'type': 'float', 'value': None, 'text': 'PorodConstantK', 'tip': 'PorodConstantK'}

    def run_function(self, data,label):
        self.param_validation()
        # self.isData1D()
        # if label['xlabel']=='q (nm^-1)':
        #     xlabel='q^2 (nm^-2)'
        # elif label['xlabel']=='q (A^-1)':
        #     xlabel='q^2 (A^-2)'
        # else:
        #     raise IOError("X Label Read Error!")
        

        q=data['x']
        intensity=data['y']

        if self.get_param_value('fit')==False:

            return {'data':{'x':q,'y':intensity},
                    'label': {'xlabel':'q^2','ylabel':'I(q)*q^4'},
                    'plot':{'data':{'x':q**2,'y':np.log(intensity*q**4)},
                            'type':'1DP' ,
                            'label':{'xlabel':'q^2','ylabel':'I(q)*q^4'},
                            'title':"Porod plot"}
                    }
        else:
        
            xPorod,yPorod,slopefit,lnKfit=bf.porodFit(q, intensity, self.get_param_value('q_range'))
    
            if slopefit<0:
                result={'PorodSlope':slopefit,'PorodLnK':lnKfit,'PorodConstantK':np.exp(lnKfit),
                        'InterfaceThickPara':np.sqrt(-slopefit),'InterfaceThickness':np.sqrt(-2*np.pi*slopefit)}
            else: #slopefit>=0
                result={'PorodSlope':slopefit,'PorodLnK':lnKfit,'PorodConstantK':np.exp(lnKfit)}


            self.set_param('PorodSlope', result['PorodSlope'])
            self.set_param('PorodLnK', result['PorodLnK'])
            self.set_param('PorodConstantK', result['PorodConstantK'])
    
            if self.get_param_value('correction')==False:

                return {'data':{'x':q,'y':intensity},
                        'label': {'xlabel':'q^2','ylabel':'I(q)*q^4'},
                        'plot':{'data':{'x':xPorod,'y':yPorod},
                                'type':'1DP' ,
                                'label':{'xlabel':'q^2','ylabel':'I(q)*q^4'},
                                'title':"Porod plot"}
                        }

            else:
                intensity_correct,yPorod_correct=bf.porodCorrect(q, intensity, slopefit, lnKfit)
                return {'data': {'x': q, 'y': intensity_correct},
                        'label': {'xlabel': 'q^2', 'ylabel': 'I(q)*q^4'},
                        'plot': {'data': [{'name': 'Porod','style':'line','color':'b','legend':'Porod' ,'x': xPorod, 'y': yPorod},
                                          {'name': 'Porod_correct','style':'line','color':'r','legend':'Porod_correct', 'x':xPorod,'y':yPorod_correct}],
                                 'type': '1DP',
                                 'label': {'xlabel': 'q^2', 'ylabel': 'I(q)*q^4'},
                                 'title':"Porod_correct"
                                 },
                        'num_value': result,
                        }

                self.set_param('PorodSlope', result['PorodSlope'])
                self.set_param('PorodLnK', result['PorodLnK'])
                self.set_param('PorodConstantK', result['PorodConstantK'])

                
    def param_validation(self):
        if self.get_param_value('fit') is True and self.get_param_value('q_range') is None:
            raise ValueError("The high q range for Porod Operation must be input!")
        if self.get_param_value('fit') is False and self.get_param_value('correction') is True:
            raise ValueError("'Porod Fit' should be selected!")


class KratkyAnalysis(ProcessingFunction):
    function_text = 'Kratky Analysis'
    function_tip = "Kratky plot (I~q-->q~I*(q**2)) and Normalized Kratky plot (qRg)**2I(q)/I(0)  vs. qRg"

    def __init__(self):
        super().__init__()
        self._params_dict['Normalized_profiles'] = {'type': 'bool', 'value': False, 'text': 'Normalized Kratky plot',
                                    'tip': "If selected, Guinier fit is done."}

    def run_function(self,data,label):
        self.param_validation()
        q = data['x']
        intensity = data['y']
        GuinierFit=data['result']
        if self.get_param_value('Normalized_profiles') is False or GuinierFit is None:
            print('wwwwww',GuinierFit)
            return {'data':{'x':q,'y':intensity},
                    'plot':{'data':{'x':q,'y':intensity*(q**2)},
                            'type':'1DP' ,
                            'label':{'xlabel':'q^2','ylabel':'I*(q**2)'},
                            "title":"Kratky plot",}
                    }
        else:
            Rg=GuinierFit['Rg']
            I0=GuinierFit['I0']
            # (qRg)**2I(q)/I(0) vs. qRg
            return {'data': {'x': q, 'y': intensity},
                    'plot': {'data': {'x': q*Rg, 'y': ((q*Rg)**2)*intensity /I0},
                             'type': '1DP',
                             'label': {'xlabel': 'q*Rg', 'ylabel': '(qRg)**2I(q)/I(0)'},
                             "title":"Normalized Kratky plot",
                             }
                    }


    # def param_validation(self):
    #     if self.get_param_value('Normalized_profiles') is True and num_value is None:
    #         raise ValueError("The Guinier fit must be done!")

            
# #------------------------------------------------------------------------------
# class IntegralInvariant(ProcessingFunction):
#     function_text = 'Integral Invariant'
#     function_tip = 'Calculate the integral invariant (Q) from SAXS curve I~q. Porod operation and Guinier operation are required in advance.'
#
#     def __init__(self):
#         super().__init__()
#
#     def run_function(self, data,num_value,label):
#         self.param_validation()
#         # self.isData1D()
#
#         if not 'Rg' in num_value:
#             raise RuntimeWarning("Guinier operation haven't been done.")
#         if not 'PorodConstantK' in num_value:
#             raise RuntimeWarning("Porod operation haven't been done.")
#
#         invQ=bf.integralInvariant(data['x'], data['y'], num_value['Rg'], num_value['I0'], num_value['PorodConstantK'])
#
#         return {'data': data,
#                 'num_value':{'InvariantQ':invQ}}
#
# #------------------------------------------------------------------------------
# class TParameter(ProcessingFunction):
#     function_text = 'T Parameter'
#     function_tip = 'Calculate T-parameter from SAXS curve I~q. Integral invariant are required in advance.'
#
#     def __init__(self):
#         super().__init__()
#
#     def run_function(self, num_value):
#         self.param_validation()
#         # self.isData1D()
#
#         if not 'InvariantQ' in num_value:
#             raise RuntimeWarning("Integral invariant haven't been calculated.")
#
#         t_parameter=4*num_value['invQ']/np.pi/num_value['PorodConstantK']
#
#         return {'num_value':{'T_Parameter':t_parameter}}
#

#------------------------------------------------------------------------------
class NormalizationSAXS(ProcessingFunction):
    function_text = 'SAXS Normalization'
    function_tip = '(I_sample-noise)/Ic_sample*coeff_sample*-(I_bg-noise)/Ic_bg*coeff_bg.'
    
    # Any:Any 注意一维二维均适用情况，显示的差别-需要判断，后续加入
    def __init__(self):
        super().__init__()
        self._params_dict['ic_sample'] = {'type': 'file', 'value': None, 'text': 'Ic Monitor'}##后面更改为file
        self._params_dict['coeff_sample'] = {'type': 'float', 'value': 1.0, 'text': 'Normalization Coefficient'}                                            
        self._params_dict['noise'] = {'type': 'float', 'value': 0.0, 'text': 'Detector Noise'}
        self._params_dict['bg'] = {'type': 'file', 'value': None, 'text': 'Background'}##后面更改为file
        self._params_dict['ic_bg'] = {'type': 'file', 'value': None, 'text': 'Background Ic Monitor'}##后面更改为file
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
        # ---------------------------------Normalization--------------------------------
        # normalization for SAXS
        # def normalizeSAXS(data, ic_sample, coeff_sample, bg, ic_bg, coeff_bg, noise):

        # return (data - noise) / ic_sample * coeff_sample - (bg - noise) / ic_bg * coeff_bg
        #if self.isData2D():
        data['image']=bf.normalizeSAXS(data['image'], ic_sample, self.get_param_value('coeff_sample'),
                                       bg, ic_bg, self.get_param_value('coeff_bg'), self.get_param_value('noise'))
        
        return {'data':data,
                'data_display':{'image':data['image'],'type':'2DV'}
                }

        
    def param_validation(self):
        if self.get_param_value('ic_sample') is None:
            raise ValueError("'Ic Monitor' must be selected!")


