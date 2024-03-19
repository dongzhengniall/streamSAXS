# -*- coding: utf-8 -*-
# lib for framework
from util.processing_sequence import ProcessingFunction
from enum import unique, Enum
import numpy as np

# lib for function
import plugin.base_function as bf


# %%

class IntegrationPlot(ProcessingFunction):
    function_text = 'Integration Plot'
    function_tip = 'Integration Plot'

    def __init__(self):
        super().__init__()

    def run_function(self, data, label):

        return {'data': data,
                "plot": {"type": "2DPL",
                         "data": data}}
                # "size": {"x": self.get_param_value("x_size"), "y": self.get_param_value("y_size")}},}


class SinglePeakFit(ProcessingFunction):
    function_text = 'Single Peak Fitting'
    function_tip = 'Fit diffraction curve with single peak'

    def __init__(self):
        super().__init__()

        self._params_dict['autoFit'] = {'type': 'bool', 'value': True, 'text': 'Auto Fitting',
                                        'tip': "If selected, initial values of fitting parameters aren't necessarily given. If not selected, values are required."}
        self._params_dict['x_range'] = {'type': 'tuple_float', 'value': None, 'text': 'x range',
                                        'tip': '(min,max)'}
        self._params_dict['peak_type'] = {'type': 'enum', 'value': SinglePeakFit_PeakType.type1, 'text': 'Peak Type'}
        self._params_dict['peak_center'] = {'type': 'float', 'value': None, 'text': 'Peak Center'}
        self._params_dict['fixedPeakCenter'] = {'type': 'bool', 'value': False, 'text': 'Peak Center Fixed'}
        self._params_dict['fwhm'] = {'type': 'float', 'value': None, 'text': 'FWHM'}
        self._params_dict['fixedFWHM'] = {'type': 'bool', 'value': False, 'text': 'FWHM Fixed'}
        self._params_dict['area'] = {'type': 'float', 'value': None, 'text': 'Area',
                                     'tip': 'format such as FWHM*H is also supported and H means guess value for peak height'}
        self._params_dict['fixedArea'] = {'type': 'bool', 'value': False, 'text': 'Area Fixed'}
        self._params_dict['k'] = {'type': 'float', 'value': None, 'text': 'Linear Background Slope'}
        self._params_dict['fixedSlope'] = {'type': 'bool', 'value': False, 'text': 'Slope Fixed'}
        self._params_dict['d'] = {'type': 'float', 'value': None, 'text': 'Linear Background Intercept'}
        self._params_dict['fixedIntercept'] = {'type': 'bool', 'value': False, 'text': 'Intercept Fixed'}
        self._params_dict['n'] = {'type': 'float', 'value': None, 'text': 'Lorentz Ratio',
                                  'tip': 'only used for Vogit Fitting'}
        self._params_dict['fixedRatio'] = {'type': 'bool', 'value': False, 'text': 'Ratio Fixed'}

    def run_function(self, data, label):
        self.param_validation()
        #self.isData1D()
        x_min=self.get_param_value('x_range')[0]
        x_max=self.get_param_value('x_range')[1]
        x_min_pixel=np.where(data['x'] < x_min)[0][-1]
        x_max_pixel = np.where(data['x'] > x_max)[0][0]
        x = data['x'][x_min_pixel:x_max_pixel]  # attention the last value shoule +1
        y = data['y'][x_min_pixel:x_max_pixel]

        result, yfit = bf.singlePeakFit(x, y, self.get_param_value('autoFit'), self.get_param_value('peak_type').value,
                                        self.get_param_value('peak_center'), self.get_param_value('fwhm'),
                                        self.get_param_value('area'), self.get_param_value('k'),
                                        self.get_param_value('d'), self.get_param_value('n'),
                                        self.get_param_value('fixedPeakCenter'), self.get_param_value('fixedFWHM'),
                                        self.get_param_value('fixedArea'), self.get_param_value('fixedSlope'),
                                        self.get_param_value('fixedIntercept'), self.get_param_value('fixedRatio'))
        # print(result['peak_center'])
        self.set_param('peak_center',result['peak_center'])
        self.set_param('fwhm', result['fwhm'])
        self.set_param('area', result['area'])
        self.set_param('k', result['k'])
        self.set_param('d', result['d'])
        # self.set_param('n', result['n'])
        # print(yfit)
        data['peakfit'] = result
        # data['peakfit']={'PeakPos':result['peak_center'] , 'PeakArea' : result['area'],
        #                  'PeakFWHM':result['fwhm']}

        return {'data': data,
                "plot": {"type": "1DP",
                         "data": [{"name":"I(q)","style":"line","color":"b","legend":"I(q)",
                                   "x":x,"y":y},
                                  {"name":"IFit","style":"line" ,"color":"r","legend":"Fitting",
                                   "x":x,"y":yfit}],
                         'label': {'xlabel': 'q', 'ylabel': 'Intensity'}},
                'num_value': result}





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


class TParameters(ProcessingFunction):
    function_text = 'T-Parameter'
    function_tip = 'T-Parameter of 002 peak'

    def __init__(self):
        super().__init__()

        self._params_dict['k'] = {'type': 'float', 'value': 1, 'text': 'k',
                                        'tip': "k is a constant related to the crystalline shape in the range of 0.87–1.0"}

        self._params_dict['wavelength'] = {'type': 'float', 'value': 12.461, 'text': 'wavelength',
                                  'tip': "wavelength@10U1"}

        self._params_dict['T_parameter'] = {'type': 'float', 'value': None, 'text': 'T parameter',
                                           'tip': "wavelength@10U1"}
    def run_function(self, data, label):
        self.param_validation()
        # self.isData1D()
        k = self.get_param_value('k')
        wavelength = self.get_param_value('wavelength')

        fwhm = data['peakfit']['fwhm']
        peaks = data['peakfit']['peak_center']
        peaks_rad = np.deg2rad(peaks)
        T = (k * wavelength) / (fwhm * np.cos(peaks_rad))
        self.set_param('T_parameter', T)

        return {'data': data,
                "plot": {"type": "2DP",
                         "data": {'value':T},
                         'title': 'T parameter'}
                }



class SinglePeakFitPlot(ProcessingFunction):
    function_text = 'Single Peak Fitting Plot'
    function_tip = '2D plot'

    def __init__(self):
        super().__init__()
        self._params_dict["plotLable"] = {"type": "enum", "value": SinglePeakFitPlot_Type.unit1,
                                          "text": "Interest data"}

    def run_function(self, data, label):

        unit = 'peak_center'
        if self.get_param_value("sinoLable") == SinglePeakFitPlot_Type.unit1:
            unit = 'peak_center'
        if self.get_param_value("sinoLable") == SinglePeakFitPlot_Type.unit2:
            unit = 'area'
        if self.get_param_value("sinoLable") == SinglePeakFitPlot_Type.unit3:
            unit = 'fwhm'
        if self.get_param_value("sinoLable") == SinglePeakFitPlot_Type.unit4:
            unit = 'peak_intensity_max'
        if self.get_param_value("sinoLable") == SinglePeakFitPlot_Type.unit5:
            unit = 'PeakInt'
        if unit ==  'PeakInt':
            plotdata = data['PeakInt']
        else:

            plotdata = data['peakfit'][unit]


        return {'data': data,
                "plot": {"type": "2DP",
                         "data": {'value': plotdata},
                         'title': unit}
                }


@unique
class SinglePeakFitPlot_Type(Enum):
    unit1 = 'PeakPos'
    unit2 = 'PeakArea'
    unit3 = 'PeakFWHM'
    unit4 = 'PeakIntensity'
    unit5 = 'ROIPeakIntensity'

class SinglePeakFit2D(ProcessingFunction):
    function_text = 'Single Peak Fitting 2D'
    function_tip = '2D Gaussion fitting of single peak'

    def __init__(self):
        super().__init__()

        # self._params_dict['autoFit'] = {'type': 'bool', 'value': True, 'text': 'Auto Fitting',
        #                                 'tip': "If selected, initial values of fitting parameters aren't necessarily given. If not selected, values are required."}
        self._params_dict['x_range'] = {'type': 'tuple_float', 'value': (20,22), 'text': 'q range',
                                        'tip': '(min,max)'}
        self._params_dict['y_range'] = {'type': 'tuple_float', 'value': (20, 22), 'text': 'chi range',
                                        'tip': '(min,max)'}
        self._params_dict['peak_type'] = {'type': 'enum', 'value': SinglePeakFit2D_PeakType.type1, 'text': 'Peak Type'}
        self._params_dict['peak_center'] = {'type': 'float', 'value': None, 'text': 'Peak Center'}
        self._params_dict['fixedPeakCenter'] = {'type': 'bool', 'value': False, 'text': 'Peak Center Fixed'}

    def run_function(self, data):
        self.param_validation()
        # self.isData1D()
        k = self.get_param_value('k')



@unique
class SinglePeakFit2D_PeakType(Enum):
    type1 = "Gaussian"


class ROIPeak(ProcessingFunction):
    function_text = 'ROI Peak Intensity'
    function_tip = 'ROI Peak Intensity'

    def __init__(self):
        super().__init__()
        self._params_dict['ROI_range'] = {'type': 'tuple_float', 'value': (14, 16), 'text': 'ROI range',
                                        'tip': '(min,max) '}

    def run_function(self,  data, label):

        PeakInt = bf.ROIPeak ( data['x'],data['y'], self.get_param_value('ROI_range'))

        data['PeakInt'] = PeakInt
        #
        return {'data': data,
                "plot": {"type": "2DP",
                         "data": {'value':PeakInt},
                         'title': 'ROI Peak intensity'}
                }