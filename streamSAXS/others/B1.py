from enum import unique, Enum
import numpy as np
from PyQt5.QtCore import Qt
from xrd.util.processing_sequence import ProcessingFunction
from pyFAI.ext.reconstruct import reconstruct
from lmfit import Minimizer, Parameters


class LoadH5Data(ProcessingFunction):
    """
    DESCRIPTION:Import DataSource File
    Parameters:
        data_source_file : TYPE str
    Returns:
        data : numpy
    """
    function_text = "Load h5 Data File"
    function_tip = "Load h5 data from file"

    def __init__(self):
        super().__init__()
        self._params_dict["h5_file"] = {"type": "io", "value": "D:/cuticle-waxs.h5 /data hdf5", "text": "H5 File"}

    def run_function(self, **kwargs):
        if not "h5_file" in kwargs:
            raise ValueError("The file path must be input")

        data = {"image": kwargs["h5_file"].astype("float32")}
        return {"data": data,
                "plot": {"type": "2DV", "data": data["image"]}}


class RoiSum(ProcessingFunction):
    """
    DESCRIPTION:
    Parameters:
        data_source_file :
    Returns:
        data :
    """
    function_text = "Roi Sum"
    function_tip = "Roi Sum"

    def __init__(self):
        super().__init__()
        self._params_dict["x_size"] = {"type": "int", "value": 20, "text": "x size"}
        self._params_dict["y_size"] = {"type": "int", "value": 30, "text": "y size"}
        self._params_dict["q_range_start"] = {"type": "int", "value": 10, "text": "range start"}
        self._params_dict["q_range_end"] = {"type": "int", "value": 15, "text": "range end"}
        ####
        #self._params_dict["x_motor"] = {"type": "file", "value": None, "text": "motor x"}
        #self._params_dict["y_motor"] = {"type": "file", "value": None, "text": "motor y"}

    def run_function(self, data):
        self.param_validation()
        q_x = data['x']
        Intensity = data['y']
        q_range_start = self.get_param_value("q_range_start")
        q_range_end = self.get_param_value("q_range_end")
        min_q_pos = np.where(q_x < q_range_start)[0][-1]
        max_q_pos = np.where(q_x > q_range_end)[0][0]

        sum_roi = np.sum(Intensity[min_q_pos:max_q_pos])

        return {"data": sum_roi,
                "plot": {"type": "2DP",
                         "data": sum_roi,
                         "size": {"x": self.get_param_value("x_size"), "y": self.get_param_value("x_size")}}
                }

    def param_validation(self):
        for param in ["x_size", "y_size", "q_range_start", "q_range_end"]:
            if self.get_param_value(param) is None:
                raise ValueError("The " + param + " must be filled out")


class DetectorCalibration(ProcessingFunction):
    """
    DESCRIPTION:Import Calibration File
    Parameters:
        calibrationFile : TYPE str
                DESCRIPTION: PyFAI Calibration File <.poni>
                ATTENTION: Must be input!
    Returns:
        integrator : TYPE obj
                DESCRIPTION: obj of class AzimuthalIntegrator with calibration parameters
    """
    function_text = "Detector Calibration"
    function_tip = "Import detector calibration file"

    def __init__(self):
        super().__init__()
        self._params_dict["calibration_file"] = {"type": "file",
                                                 "value": 'E:/work/lx/mamba/other/precess_data/telson-calib-from-pyFAI.poni',
                                                 "text": "Calibration File",
                                                 "tip": "File extension is '.poni'"}

    def run_function(self, data, **kwargs):
        self.param_validation()
        integrator = kwargs["calibration_file"]
        paraFit2D = integrator.getFit2D()
        detector = (round(paraFit2D['centerX']), round(paraFit2D['centerY']), paraFit2D['pixelX'] / 1000,
                    paraFit2D['pixelY'] / 1000, paraFit2D['directDist'],
                    integrator.wavelength)  # (col-pixel,row-pixel,mm,,mm,mm,m)

        return {"data": data,
                "detector": {'centerX': detector[0], 'centerY': detector[1], 'pixelSizeX': detector[2],
                             'pixelSizeY': detector[3], 'distance': detector[4], 'wavelength': detector[5]},
                "objectset": {"integrator": integrator},
                "plot": {"type": "2DV",
                         "data": data["image"],
                         "message": detector}
                # need to display center point in 2D image and detector information in title
                }

    def param_validation(self):
        if self.get_param_value("calibration_file") is None:
            raise ValueError("The calibration file must be selected")


class ImportMask(ProcessingFunction):
    function_text = "Import Mask File"
    function_tip = "The data will take a non-negative value if no file is imported"

    def __init__(self):
        super().__init__()
        self._params_dict["mask_file"] = {"type": "file", "value": 'E:/work/lx/mamba/proccessing/precess_data/mask.tif',
                                          "text": "Mask File",
                                          "tip": "'.edf','.tif' file extensions are recommended"}

    def run_function(self, data, **kwargs):
        self.param_validation()
        mask = kwargs["mask_file"].astype("bool")
        print(data['image'].shape)
        print(mask.shape)

        data_masked = reconstruct(data['image'], mask, dummy=-10)

        return {'data': {"image": data_masked},
                'plot': {"type": "2DV",
                         "data": data_masked}}

    def param_validation(self):
        pass


# -----------------------------------------------------------------------------
# Attention: azi function is not used as class for framework
def azi(coorX1, coorY1, coorX2, coorY2, centerX, centerY):
    v1 = np.array([1, 0])
    v2 = np.array([coorX1 - centerX, np.abs(coorY1 - centerY)])
    v3 = np.array([coorX2 - centerX, np.abs(coorY2 - centerY)])
    if np.linalg.norm(v2) == 0 or np.linalg.norm(v3) == 0:
        raise ValueError("Azimuth vector is zero magnitude!")
    else:
        deg1 = np.degrees(np.arccos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))))
        deg2 = np.degrees(np.arccos(np.dot(v1, v3) / (np.linalg.norm(v1) * np.linalg.norm(v3))))

    if coorY1 < centerY:
        deg1 = -deg1
    if coorY2 < centerY:
        deg2 = -deg2

    if deg1 == deg2:
        azimuthRange = (-180, 180)
    else:
        azimuthRange = (min(deg1, deg2), max(deg1, deg2))
    '''       
    if deg1==180:
        if deg2==deg1:
            azimuthRange=(-180,180)
        elif deg2<=0:
            azimuthRange=(-180,deg2)
        else:
            raise ValueError("Please turn clockwise. Azimuth1 should smaller than Azimuth2")             
    else:
        if deg1<deg2:
            azimuthRange=(deg1,deg2)    
        else:
            raise ValueError("Please turn clockwise. Azimuth1 should smaller than Azimuth2")             
    '''
    return azimuthRange


# -----------------------------------------------------------------------------
class IntegrateAzimuthal(ProcessingFunction):
    function_text = "1D Azimuthal Integration"
    function_tip = "2D image --> 1D curve I~q/2theta/r"

    def __init__(self):
        super().__init__()
        self._params_dict["npt"] = {"type": "int", "value": 1000, "text": "Number of output points"}
        self._params_dict["radial_range"] = {"type": "tuple", "value": (70, 400), "text": "Radial Range",
                                             "tip": "(Inner Limit,Outer Limit) or (X1,Y1,X2,Y2) in pixel.If not provided, range is simply (min, max)."}
        self._params_dict["azimuth_range"] = {"type": "tuple", "value": (-180, 180), "text": "Azimuth Range",
                                              "tip": "(Lower angle, upper angle) in degree or (X1,Y1,X2,Y2) in pixel.Angle must between -180 and 180 [Clockwise] and can't cross from 180° to -180° .If not provided, range is simply (min, max)."}
        self._params_dict["outUnit"] = {"type": "enum", "value": IntegrateAzimuthal_Unit.unit1, "text": "X Axis Unit"}
        self._params_dict["polarization_factor"] = {"type": "float", "value": None, "text": "Polarization Factor",
                                                    "tip": "-1 (vertical) ~ +1 (horizontal). Default (None) is no correction, 0 for circular polarization or random."}

        self._params_dict["range"] = {"type": "data_button", "value": None, "text": "select range"}

    def run_function(self, data, objectset, detector):
        self.param_validation()
        # self.isData2D()

        if self.get_param_value("outUnit") == IntegrateAzimuthal_Unit.unit4:
            unit = 'r_mm'
        elif self.get_param_value("outUnit") == IntegrateAzimuthal_Unit.unit3:
            unit = '2th_deg'
        else:
            unit = 'q_nm^-1'

        if self.get_param_value("azimuth_range") is not None and len(self.get_param_value("azimuth_range")) == 4:
            azimuthRange = azi(self.get_param_value("radial_range")[0], self.get_param_value("radial_range")[1],
                               self.get_param_value("radial_range")[2], self.get_param_value("radial_range")[3],
                               detector['centerX'], detector['centerY'])
        else:
            azimuthRange = self.get_param_value("azimuth_range")

        if self.get_param_value("radial_range") is None:
            resultTemp = objectset["integrator"].integrate1d(data=data['image'], npt=self.get_param_value("npt"),
                                                             unit=unit,
                                                             radial_range=self.get_param_value("radial_range"),
                                                             azimuth_range=self.get_param_value("azimuth_range"),
                                                             polarization_factor=self.get_param_value(
                                                                 "polarization_factor")
                                                             )
        else:
            if len(self.get_param_value("radial_range")) == 2:
                r = np.array([self.get_param_value("radial_range")[0], self.get_param_value("radial_range")[1]]) * \
                    detector['pixelSizeX']
            elif len(self.get_param_value("radial_range")) == 4:
                coor = [self.get_param_value("radial_range")[0], self.get_param_value("radial_range")[1],
                        self.get_param_value("radial_range")[2], self.get_param_value("radial_range")[3]]
                r1 = np.sqrt(np.abs(coor[0] - detector['centerX']) ** 2 + np.abs(coor[1] - detector['centerY']) ** 2) * \
                     detector['pixelSizeX']
                r2 = np.sqrt(np.abs(coor[2] - detector['centerX']) ** 2 + np.abs(coor[3] - detector['centerY']) ** 2) * \
                     detector['pixelSizeX']
                r = np.array([min(r1, r2), max(r1, r2)])
            else:
                raise ValueError("The Radial Range should contain 2 or 4 element")

            if self.get_param_value("outUnit") == IntegrateAzimuthal_Unit.unit4:
                radialRange = tuple(r)
            elif self.get_param_value("outUnit") == IntegrateAzimuthal_Unit.unit3:
                radialRange = tuple(np.degrees(np.arctan(r / detector['distance'])))
            else:
                radialRange = tuple(4.0e-9 * np.pi * np.sin(np.arctan(r / detector['distance']) / 2.0) / detector[
                    'wavelength'])  # unit:nm-1

            resultTemp = objectset["integrator"].integrate1d(data=data['image'], npt=self.get_param_value("npt"),
                                                             unit=unit,
                                                             radial_range=radialRange,
                                                             azimuth_range=azimuthRange,
                                                             polarization_factor=self.get_param_value(
                                                                 "polarization_factor"),
                                                             )
            if self.get_param_value("outUnit") == IntegrateAzimuthal_Unit.unit2:
                resultTemp.radial /= 10

        return {'data': {'x': resultTemp.radial, 'y': resultTemp.intensity},
                'label': {'xlabel': self.get_param_value("Distance(pixels)"), 'ylabel': 'Intensity(ADUs)'},
                'plot': {'type': '1DP',
                         'data': {'x': resultTemp.radial, 'y': resultTemp.intensity, 'style': 'line', 'legend': 'line1',
                                  'color': 'b', 'width': '3'},
                         # 'data': {'x': resultTemp.radial, 'y': resultTemp.intensity, 'style': 'line', 'legend': 'line1',
                         #          'color': 'b', 'width': '3', 'symbol': "o", "line_style": Qt.DashLine},
                         # 'data':{'style':'Vline', 'x': 1, 'color': 'r', 'width': '2'},
                         # 'data': [{'name': '1', 'x': resultTemp.radial, 'y': resultTemp.intensity, 'style': 'scatter', 'legend': 'line1',
                         #           'color': 'b', 'width': '2', 'symbol': "o"}, {'name': '2', 'style':'Vline', 'x': 1, 'color': 'r', 'width': '2'}],
                         'label': {'xlabel': self.get_param_value("outUnit"), 'ylabel': 'Intensity'}
                         }}

    def param_validation(self):
        if self.get_param_value("npt") is None:
            raise ValueError("The number of output points must be input")


@unique
class IntegrateAzimuthal_Unit(Enum):
    unit1 = 'q (nm^-1)'
    unit2 = 'q (A^-1)'
    unit3 = '2' + chr(952) + ' (degree)'
    unit4 = 'r (mm)'


class SinglePeakFit(ProcessingFunction):
    function_text = 'Single Peak Fitting'
    function_tip = 'Fit diffraction curve with single peak'
    '''
    data:XY->XY
    result:{Peak Center,FWHM,Area,BgSlope,BgIntercept,LorentzRatio}
    '''

    def __init__(self):
        super().__init__()

        self._params_dict['autoFit'] = {'type': 'bool', 'value': True, 'text': 'Auto Fitting',
                                        'tip': "If selected, initial values of fitting parameters aren't necessarily given. If not selected, values are required."}
        self._params_dict['x_range'] = {'type': 'tuple', 'value': (632, 675), 'text': 'x range',
                                        'tip': '(min,max) in pixel'}
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
        # self.isData1D()

        x = data['x'][self.get_param_value('x_range')[0]:self.get_param_value('x_range')[
                                                             1] + 1]  # attention the last value shoule +1
        y = data['y'][self.get_param_value('x_range')[0]:self.get_param_value('x_range')[1] + 1]

        # definition for parameters value
        if self.get_param_value('autoFit') is True:
            # initial guess for Peak Center
            ymax = np.max(y)
            value_peakCenter = x[list(y).index(ymax)]
            # initial guess for FWHM
            half_left = 0
            ymin_left = y[0:list(y).index(ymax)].min()
            for i in range(0, list(y).index(ymax)):
                if y[i] > ymin_left + (ymax - ymin_left) / 2:
                    half_left = i
                    break
            half_right = 0
            ymin_right = y[list(y).index(ymax):len(y)].min()
            for i in range(list(y).index(ymax), len(y)):
                if y[i] < ymin_right + (ymax - ymin_right) / 2:
                    half_right = i
                    break
            value_fwhm = x[half_right] - x[half_left]
            # initial guess for k
            value_k = (y[-1] - y[0]) / (x[-1] - x[0])
            # initial guess for d
            value_d = y[0] - value_k * x[0]
            # initial guess for Area
            value_area = value_fwhm * (ymax - value_k * value_peakCenter - value_d)
            # initial guess for n
            value_n = 0.5

            # create a set of Parameters
            params = Parameters()
            # vary=False will prevent the value from changing in the fit
            params.add('peak_center', value=value_peakCenter)
            params.add('fwhm', value=value_fwhm)
            params.add('area', value=value_area)
            params.add('k', value=value_k)
            params.add('d', value=value_d)
            if self.get_param_value('peak_type') == SinglePeakFit_PeakType.type3:
                params.add('n', value=value_n)

        else:
            value_peakCenter = self.get_param_value('peak_center')
            value_fwhm = self.get_param_value('fwhm')
            value_area = self.get_param_value('area')
            value_k = self.get_param_value('k')
            value_d = self.get_param_value('d')
            value_n = self.get_param_value('n')
            # create a set of Parameters
            params = Parameters()
            # vary=False will prevent the value from changing in the fit
            params.add('peak_center', value=value_peakCenter, vary=not self.get_param_value('fixedPeakCenter'))
            params.add('fwhm', value=value_fwhm, vary=not self.get_param_value('fixedFWHM'))
            params.add('area', value=value_area, vary=not self.get_param_value('fixedArea'))
            params.add('k', value=value_k, vary=not self.get_param_value('fixedSlope'))
            params.add('d', value=value_d, vary=not self.get_param_value('fixedIntercept'))
            if self.get_param_value('peak_type') == SinglePeakFit_PeakType.type3:
                params.add('n', value=value_n, vary=not self.get_param_value('fixedRatio'))

        # defined function
        def fun_peak(params, x, y):
            x0 = params['peak_center']
            w = params['fwhm']
            A = params['area']
            k = params['k']
            d = params['d']
            if self.get_param_value('peak_type') == SinglePeakFit_PeakType.type1:
                model = A * (2 / w * np.sqrt(np.log(2) / np.pi) * np.exp(
                    -4 * np.log(2) * np.power((x - x0) / w, 2))) + k * x + d
            if self.get_param_value('peak_type') == SinglePeakFit_PeakType.type2:
                model = A * (2 / (np.pi * w) / (1 + 4 * np.power((x - x0) / w, 2))) + k * x + d
            if self.get_param_value('peak_type') == SinglePeakFit_PeakType.type3:
                n = params['n']
                model = (1 - n) * A * (
                        2 / w * np.sqrt(np.log(2) / np.pi) * np.exp(-4 * np.log(2) * np.power((x - x0) / w, 2))) + \
                        n * A * (2 / (np.pi * w) / (1 + 4 * np.power((x - x0) / w, 2))) + k * x + d
            return model - y

        # do fit, here with the default leastsq algorithm
        minner = Minimizer(fun_peak, params, fcn_args=(x, y))
        resultTemp = minner.minimize()
        # calculate final result
        yfit = y + resultTemp.residual
        result = {'peak_center': resultTemp.params['peak_center'].value,
                  'fwhm': resultTemp.params['fwhm'].value,
                  'area': resultTemp.params['area'].value,
                  'k': resultTemp.params['k'].value,
                  'd': resultTemp.params['d'].value}
        if self.get_param_value('peak_type') == SinglePeakFit_PeakType.type3:
            result['n'] = resultTemp.params['n'].value

        # self.p1.plot([motor_x], [motor_y], pen=None, symbol='o')
        # name_list = ['o', 's', 't', 't1', 't2', 't3', 'd', '+', 'x', 'p', 'h', 'star',
        #             'arrow_up', 'arrow_right', 'arrow_down', 'arrow_left', 'crosshair']
        #
        return {'data': data,
                'parameter_display': result,
                'numerical_result': result,
                'plot': {'type': '1DP',
                         'data': [{'name': '1', 'x': x, 'y': y, 'style': 'scatter', 'symbol': 'o', 'color': 'b',
                                   'legend': 'data'},
                                  {'name': '2', 'x': x, 'y': yfit, 'style': 'line', 'symbol': Qt.SolidLine,
                                   'color': 'r',
                                   'width': 2.5, 'legend': 'Peak Fitting'},
                                  {'name': '3', 'x': 1, 'style': 'vline', 'symbol': Qt.SolidLine, 'color': 'g'}],
                         'label': {'xlabel': label['xlabel'], 'ylabel': label['ylabel']}
                         }
                }

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


# ------------------------------------------------------------------------------
class DoublePeakFit(ProcessingFunction):
    function_text = 'Double Peak Fitting'
    function_tip = 'Fit diffraction curve with double peak'
    '''
    data:XY->XY
    result:{PeakCenter1,FWHM1,Area1,PeakCenter2,FWHM2,Area2,BgSlope,BgIntercept}
    '''

    def __init__(self):
        super().__init__()
        self._params_dict['x_range'] = {'type': 'tuple_int', 'value': None, 'text': 'x range (MinPixel,MaxPixel)'}
        self._params_dict['peak_type'] = {'type': 'enum', 'value': DoublePeakFit_PeakType.type1, 'text': 'Peak Type'}
        self._params_dict['peak_center1'] = {'type': 'float', 'value': None, 'text': 'Peak Center1'}
        self._params_dict['fixedPeakCenter1'] = {'type': 'bool', 'value': False, 'text': 'Peak Center1 Fixed'}
        self._params_dict['fwhm1'] = {'type': 'float', 'value': None, 'text': 'FWHM1'}
        self._params_dict['fixedFWHM1'] = {'type': 'bool', 'value': False, 'text': 'FWHM1 Fixed'}
        self._params_dict['area1'] = {'type': 'float', 'value': None, 'text': 'Area1(FWHM*H is supported)'}
        self._params_dict['fixedArea1'] = {'type': 'bool', 'value': False, 'text': 'Area1 Fixed'}
        self._params_dict['peak_center2'] = {'type': 'float', 'value': None, 'text': 'Peak Center2'}
        self._params_dict['fixedPeakCenter2'] = {'type': 'bool', 'value': False, 'text': 'Peak Center2 Fixed'}
        self._params_dict['fwhm2'] = {'type': 'float', 'value': None, 'text': 'FWHM2'}
        self._params_dict['fixedFWHM2'] = {'type': 'bool', 'value': False, 'text': 'FWHM2 Fixed'}
        self._params_dict['area2'] = {'type': 'float', 'value': None, 'text': 'Area2(FWHM*H is supported)'}
        self._params_dict['fixedArea2'] = {'type': 'bool', 'value': False, 'text': 'Area2 Fixed'}
        self._params_dict['autoBg'] = {'type': 'bool', 'value': True, 'text': 'Auto Background'}
        self._params_dict['k'] = {'type': 'float', 'value': None, 'text': 'Linear Background Slope'}
        self._params_dict['fixedSlope'] = {'type': 'bool', 'value': False, 'text': 'Slope Fixed'}
        self._params_dict['d'] = {'type': 'float', 'value': None, 'text': 'Linear Background Intercept'}
        self._params_dict['fixedIntercept'] = {'type': 'bool', 'value': False, 'text': 'Intercept Fixed'}
        self._input_param_dict = {'data': None}

    def run_function(self, data):
        self.param_validation()
        self.isData1D()

        x = data['x'][self.get_param_value('x_range')[0]:self.get_param_value('x_range')[
                                                             1] + 1]  # attention the last value shoule +1
        y = data['y'][self.get_param_value('x_range')[0]:self.get_param_value('x_range')[1] + 1]

        # definition for parameters value
        value_peakCenter1 = self.get_param_value('peak_center1')
        value_fwhm1 = self.get_param_value('fwhm1')
        value_area1 = self.get_param_value('area1')
        value_peakCenter2 = self.get_param_value('peak_cente21')
        value_fwhm2 = self.get_param_value('fwhm2')
        value_area2 = self.get_param_value('area2')

        # create a set of Parameters
        params = Parameters()
        # vary=False will prevent the value from changing in the fit
        params.add('peak_center1', value=value_peakCenter1, vary=not self.get_params_dict['fixedPeakCenter1'])
        params.add('fwhm1', value=value_fwhm1, vary=not self.get_params_dict['fixedFWHM1'])
        params.add('area1', value=value_area1, vary=not self.get_params_dict['fixedArea1'])
        params.add('peak_center2', value=value_peakCenter2, vary=not self.get_params_dict['fixedPeakCenter2'])
        params.add('fwhm2', value=value_fwhm2, vary=not self.get_params_dict['fixedFWHM2'])
        params.add('area2', value=value_area2, vary=not self.get_params_dict['fixedArea2'])

        if self.get_params_dict('autoBg') is True:
            # initial guess for k
            value_k = (y[-1] - y[0]) / (x[-1] - x[0])
            # initial guess for d
            value_d = y[0] - value_k * x[0]

            params.add('k', value=value_k)
            params.add('d', value=value_d)
        else:
            value_k = self.get_param_value('k')
            value_d = self.get_param_value('d')
            params.add('k', value=value_k, vary=not self.get_params_dict['fixedSlope'])
            params.add('d', value=value_d, vary=not self.get_params_dict['fixedIntercept'])

        # defined function
        def fun_peak(params, x, y):
            x01 = params['peak_center1']
            w1 = params['fwhm1']
            A1 = params['area1']
            x02 = params['peak_center2']
            w2 = params['fwhm2']
            A2 = params['area2']
            k = params['k']
            d = params['d']
            if self.get_params_dict['peak_type'] == DoublePeakFit_PeakType.type1:
                model = A1 * (2 / w1 * np.sqrt(np.log(2) / np.pi) * np.exp(
                    -4 * np.log(2) * np.power((x - x01) / w1, 2))) + \
                        A2 * (2 / w2 * np.sqrt(np.log(2) / np.pi) * np.exp(
                    -4 * np.log(2) * np.power((x - x02) / w2, 2))) + \
                        k * x + d
            if self.get_params_dict['peak_type'] == DoublePeakFit_PeakType.type2:
                model = A1 * (2 / (np.pi * w1) / (1 + 4 * np.power((x - x01) / w1, 2))) + \
                        A2 * (2 / (np.pi * w2) / (1 + 4 * np.power((x - x02) / w2, 2))) + \
                        k * x + d
            if self.get_params_dict['peak_type'] == DoublePeakFit_PeakType.type3:
                model = A1 * (2 / w1 * np.sqrt(np.log(2) / np.pi) * np.exp(
                    -4 * np.log(2) * np.power((x - x01) / w1, 2))) + \
                        A2 * (2 / (np.pi * w2) / (1 + 4 * np.power((x - x02) / w2, 2))) + k * x + d
            if self.get_params_dict['peak_type'] == DoublePeakFit_PeakType.type4:
                model = A1 * (2 / (np.pi * w1) / (1 + 4 * np.power((x - x01) / w1, 2))) + \
                        A2 * (2 / w2 * np.sqrt(np.log(2) / np.pi) * np.exp(
                    -4 * np.log(2) * np.power((x - x02) / w2, 2))) + \
                        k * x + d

            return model - y

        # do fit, here with the default leastsq algorithm
        minner = Minimizer(fun_peak, params, fcn_args=(x, y))
        resultTemp = minner.minimize()
        # calculate final result
        yfit = y + resultTemp.residual
        result = {'peak_center1': resultTemp.params['peak_center1'].value,
                  'fwhm1': resultTemp.params['fwhm1'].value,
                  'area1': resultTemp.params['area1'].value,
                  'peak_center2': resultTemp.params['peak_center2'].value,
                  'fwhm2': resultTemp.params['fwhm2'].value,
                  'area2': resultTemp.params['area2'].value,
                  'k': resultTemp.params['k'].value,
                  'd': resultTemp.params['d'].value}

        ig = lambda A, w, x0, k, d, x: A * (
                2 / w * np.sqrt(np.log(2) / np.pi) * np.exp(-4 * np.log(2) * np.power((x - x0) / w, 2))) + k * x + d
        il = lambda A, w, x0, k, d, x: A * (2 / (np.pi * w) / (1 + 4 * np.power((x - x0) / w, 2))) + k * x + d
        if self.get_params_dict['peak_type'] == DoublePeakFit_PeakType.type1:
            peak1 = ig(result['area1'], result['fwhm1'], result['peak_center1'], result['k'], result['d'], x)
            peak2 = ig(result['area2'], result['fwhm2'], result['peak_center2'], result['k'], result['d'], x)
        if self.get_params_dict['peak_type'] == DoublePeakFit_PeakType.type2:
            peak1 = il(result['area1'], result['fwhm1'], result['peak_center1'], result['k'], result['d'], x)
            peak2 = il(result['area2'], result['fwhm2'], result['peak_center2'], result['k'], result['d'], x)
        if self.get_params_dict['peak_type'] == DoublePeakFit_PeakType.type3:
            peak1 = ig(result['area1'], result['fwhm1'], result['peak_center1'], result['k'], result['d'], x)
            peak2 = il(result['area2'], result['fwhm2'], result['peak_center2'], result['k'], result['d'], x)
        if self.get_params_dict['peak_type'] == DoublePeakFit_PeakType.type4:
            peak1 = il(result['area1'], result['fwhm1'], result['peak_center1'], result['k'], result['d'], x)
            peak2 = ig(result['area2'], result['fwhm2'], result['peak_center2'], result['k'], result['d'], x)

        return {'data': data,
                'data_display': {'x0': x, 'y0': y, 'xfit': x, 'yfit': yfit,
                                 'xfit1': x, 'yfit1': peak1, 'xfit2': x, 'yfit2': peak2,
                                 'xlabel': data['xlabel'], 'ylabel': data['ylabel']},
                'parameter_display': result,
                'numerical_result': result}

    def param_validation(self):
        if self.get_params_dict('autoBg') is True:
            if self.get_param_value('peak_center1') is None or self.get_param_value('fwhm1') is None \
                    or self.get_param_value('area1') is None or self.get_param_value('peak_center2') is None \
                    or self.get_param_value('fwhm2') is None or self.get_param_value('area2') is None:
                raise ValueError(
                    "The initial value except slope and intercept must be input when auto background is selected")
        else:
            if self.get_param_value('peak_center1') is None or self.get_param_value('fwhm1') is None \
                    or self.get_param_value('area1') is None or self.get_param_value('peak_center2') is None \
                    or self.get_param_value('fwhm2') is None or self.get_param_value('area2') is None \
                    or self.get_param_value('k') is None or self.get_param_value('d') is None:
                raise ValueError("The initial value must be input")


@unique
class DoublePeakFit_PeakType(Enum):
    type1 = "Gaussian+Gaussian+LinearBg"
    type2 = "Lorentz+Lorentz+LinearBg"
    type3 = "Gaussian+Lorentz+LinearBg"
    type4 = "Lorentz+Gaussian+LinearBg"
