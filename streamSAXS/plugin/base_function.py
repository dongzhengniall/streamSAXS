# -*- coding: utf-8 -*-
# defined functions for data process, independent of frame

#%%
# generic lib
import numpy as np

# lib for calibration
from pyFAI.azimuthalIntegrator import AzimuthalIntegrator

# lib for XRD peak fitting,Porod opration
import lmfit
from lmfit import Minimizer, Parameters

#import traceback

# lib for SAXS
#import bioxtasraw.RAWAPI as raw #lib for GuinierOperation
#import bioxtasraw.SASM as SASM #lib for GuinierOperation
from scipy import integrate #lib for IntegralInvariant


#%%
#---------------------------------Calibration----------------------------------
# detector calibration via PyFAI
def detectorCalibrationPyfai(file):
    '''
    Parameters
    ----------
    calibrationFile : str
        .poni file name.

    Returns
    -------
    integrator: object
        used for integration.           
    '''
    integrator = AzimuthalIntegrator.sload(file)
    return integrator

# detector calibration via fit2d:
def detectorCalibrationFit2d(wavelength,sdd,centerX,centerY,pixelX,pixelY,rotation,tilt):
    '''
    Parameters
    ----------
    wavelength : unit m.
    sdd : unit mm.
    centerX : unit Pixel.
    centerY : unit Pixel.
    pixelX : unit um.
    pixelY : unit um.
    tilt : unit degree.
    rotation : unit degree.

    Returns
    -------
    integrator : object
        used for integration.

    '''
    integrator = AzimuthalIntegrator(wavelength=wavelength)
    integrator.setFit2D(directDist=sdd,centerX=centerX,centerY=centerY,
                        pixelX=pixelX,pixelY=pixelY,
                        tiltPlanRotation=rotation,tilt=tilt)
       
    return integrator

#%%
#------------------------------------Masking-----------------------------------
"""
# user defined 2D mask
def userDefinedMask2D(data,mask):
    '''
    Parameters
    ----------
    data : 2D array.
    file : User-defined mask file, 2D bool array

    Returns
    -------
    data_masked : 2D array.
    '''
    data = reconstruct(data, mask, dummy=-10)
    
    return data
"""
# threshold mask 2D
def thresholdMask2D(data,minValue=None,maxValue=None):
    '''
    Parameters
    ----------
    data : 2D Array
    minValue : float
    maxValue : float

    Returns
    -------
    data : 2D Array
        DESCRIPTION: Masked 2D image.(True：should be masked; False: not masked)

    '''
    
    '''    
    if minValue is None and maxValue is None:
        mask=data<0 
    if minValue is None and maxValue is not None:
        mask= (data<0)|(data>maxValue)
    if minValue is not None and maxValue is None:
        mask= data < minValue 
    if minValue is not None and maxValue is not None:
        mask=(data<minValue)|(data>maxValue)
        
    data = reconstruct(data, mask,dummy=-10)
    '''
    if minValue is None and maxValue is None:
        mask=None
    else:
        if minValue is None and maxValue is not None:
            mask= data>maxValue
        if minValue is not None and maxValue is None:
            mask= data < minValue 
        if minValue is not None and maxValue is not None:
            # print(data)
            # print(minValue)
            # print(maxValue)
            mask=(data<minValue)|(data>maxValue)        
        # data = reconstruct(data, mask,dummy=-10)
    
    return mask    

# user defined 1D mask
def userDefinedMask1D(x0,y0,index=None):
    '''
    Parameters
    ----------
    x0/y0 : 1D array
    index : tuple
        Area will be ignored. Length must be even.

    Returns
    -------
    x/y : 1D array

    '''
    if index is None:
        x,y=x0[x0>0],y0[x0>0]
    else:
        index=np.array(index)
        index=np.insert(index,0,0)
        index=np.append(index,len(x0)-1)
        index.resize((int(len(index)/2),2))
        
        x,y=np.array([]),np.array([])
        for v in iter(index):
            x=np.concatenate((x,x0[v[0]:v[1]]))
            y=np.concatenate((y,y0[v[0]:v[1]]))
        
        '''
        Doesn't work well
        f=interpolate.UnivariateSpline(x,y,k=1,s=0) #k=1:linear,k=3:cubic
        y0_new=f(x0)
        '''

    return x,y    

#%%
#------------------------------------Integration-------------------------------
# integrate 2D
def integrate2D(integrator,data,npt_rad,unit='q_nm^-1',radial_range=None,npt_azim=360,azimuth_range=None,polarization_factor=None,mask=None):
    
    result = integrator.integrate2d(data=data, mask=mask, npt_rad=npt_rad,unit=unit,radial_range=radial_range,
                                    npt_azim=npt_azim,azimuth_range=azimuth_range,
                                    polarization_factor=polarization_factor,method='csr')
    return result

# integrate azimuthal I~q
def integrateAzimuthal(integrator,data,npt,unit='q_nm^-1',radial_range=None,azimuth_range=None,polarization_factor=None,mask=None):
    
    result = integrator.integrate1d(data=data, mask=mask, npt=npt,unit=unit,
                                    radial_range=radial_range,azimuth_range=azimuth_range,
                                    polarization_factor=polarization_factor)
        
    return result

# integrate radial I~chi
def integrateRadial(integrator,data,npt,npt_rad,unit='chi_deg',azimuth_range=None,radial_unit='q_nm^-1',radial_range=None,polarization_factor=None,mask=None):
    
    result=integrator.integrate_radial(data=data, mask=mask, npt=npt,npt_rad=npt_rad,
                                       unit=unit,azimuth_range=azimuth_range,
                                       radial_unit=radial_unit,radial_range=radial_range,                                                            
                                       polarization_factor=polarization_factor)
    return result


#%%
#-----------------------------------XRD----------------------------------------
# single peak fitting
def singlePeakFit(x,y,autoFit=True,peak_type="Gaussian+LinearBg",
                  peak_center=None,fwhm=None,area=None,k=0,d=0,n=0.5,
                  #peak_center_range=(None,None),fwhm_range=(None,None),area_range=(None,None),
                  fixedPeakCenter=False,fixedFWHM=False,fixedArea=False,fixedSlope=False,fixedIntercept=False,fixedRatio=False):
    '''
    Parameters
    ----------
    x : TYPE
        DESCRIPTION.
    y : TYPE
        DESCRIPTION.
    autoFit : TYPE
        DESCRIPTION.
    peak_type : TYPE
        DESCRIPTION.
    peak_center : TYPE
        DESCRIPTION.
    fwhm : TYPE
        DESCRIPTION.
    area : TYPE
        DESCRIPTION.
    k : TYPE
        DESCRIPTION.
    d : TYPE
        DESCRIPTION.
    n : TYPE
        DESCRIPTION.
    fixedPeakCenter : bool
        DESCRIPTION.
    fixedFWHM : bool
        DESCRIPTION.
    fixedArea : bool
        DESCRIPTION.
    fixedSlope : bool
        DESCRIPTION.
    fixedIntercept : bool
        DESCRIPTION.
    fixedRatio : bool
        DESCRIPTION.

    Returns
    -------
    result:TYPE
        DESCRIPTION.
    yfit:

    '''
    try:
        #definition for parameters value
        if autoFit is True:
            #initial guess for Peak Center
            ymax = np.max(y)
            value_peakCenter= x[list(y).index(ymax)]
            #initial guess for FWHM
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
            #initial guess for k
            value_k = (y[-1] - y[0]) / (x[-1] - x[0])
            #initial guess for d
            value_d = y[0] - value_k * x[0]
            #initial guess for Area
            value_area=value_fwhm*(ymax-value_k*value_peakCenter-value_d)
            #initial guess for n
            value_n= 0.5
            
            # create a set of Parameters    
            params=Parameters()
            #vary=False will prevent the value from changing in the fit
            params.add('peak_center',value=value_peakCenter)
            params.add('fwhm',value=value_fwhm)
            params.add('area',value=value_area)
            params.add('k',value=value_k)
            params.add('d',value=value_d)
            if peak_type=="Vogit+LinearBg":
                params.add('n',value=value_n)
                
        else:
            value_peakCenter=peak_center
            value_fwhm=fwhm
            value_area=area
            value_k=k
            value_d=d
            value_n=n    
            # create a set of Parameters    
            params=Parameters()
            #vary=False will prevent the value from changing in the fit
            params.add('peak_center',value=value_peakCenter,vary=not fixedPeakCenter) #,min=peak_center_range[0],max=peak_center_range[1]
            params.add('fwhm',value=value_fwhm,vary=not fixedFWHM) #,min=fwhm_range[0],max=fwhm_range[1]
            params.add('area',value=value_area,vary=not fixedArea) #,min=area_range[0],max=area_range[1]
            params.add('k',value=value_k,vary=not fixedSlope)
            params.add('d',value=value_d,vary=not fixedIntercept)
            if peak_type=="Vogit+LinearBg":
                params.add('n',value=value_n,vary=not fixedRatio)
        
        # defined function
        def fun_peak(params,x,y):
            x0=params['peak_center']
            w=params['fwhm']
            A=params['area']
            k=params['k']
            d=params['d']
            if peak_type=="Gaussian+LinearBg":
                model=A *(2 / w * np.sqrt(np.log(2) / np.pi) * np.exp(-4 * np.log(2) * np.power((x - x0) / w, 2))) + k*x+d
            if peak_type=="Lorentz+LinearBg":
                model=A*(2 / (np.pi * w) / (1 + 4 * np.power((x - x0) / w, 2))) + k*x+d
            if peak_type=="Vogit+LinearBg":
                n=params['n']
                model=(1-n)*A *(2 / w * np.sqrt(np.log(2) / np.pi) * np.exp(-4 * np.log(2) * np.power((x - x0) / w, 2)))+\
                    n*A*(2 / (np.pi * w) / (1 + 4 * np.power((x - x0) / w, 2)))+k*x+d
            return model-y
        
        # do fit, here with the default leastsq algorithm
        minner = Minimizer(fun_peak, params, fcn_args=(x, y))
        resultTemp = minner.minimize()
        # calculate final result
        yfit = y + resultTemp.residual
        result={'peak_center':resultTemp.params['peak_center'].value,
                'fwhm':resultTemp.params['fwhm'].value,
                'area':resultTemp.params['area'].value,
                'k':resultTemp.params['k'].value,
                'd':resultTemp.params['d'].value} 
        if peak_type=="Vogit+LinearBg":
            result['n']=resultTemp.params['n'].value
        
        return result,yfit
    
    except Exception: # all exception
        #traceback.print_exc()
        yfit=np.full(x.shape,np.nan)
        result={'peak_center':np.nan,
                'fwhm':np.nan,
                'area':np.nan,
                'k':np.nan,
                'd':np.nan} 
        if peak_type=="Vogit+LinearBg":
            result['n']=np.nan
            
        return result,yfit

#%%
#-----------------------------------XRD----------------------------------------
# 2D Gaussion fitting
def singlePeakFit_2D(data,miny, maxy, minx, maxx):

    intensity = data[miny:maxy, minx:maxx]

    x, y = np.meshgrid(np.arange(minx, maxx), np.arange(miny, maxy))

    model = lmfit.models.Gaussian2dModel()
    params = model.guess(intensity.ravel(), x=x.ravel(), y=y.ravel())

    try:
        result = model.fit(intensity.ravel(),
                           params,
                           x=x.ravel(),
                           y=y.ravel())

        lmfit.report_fit(result)

        cen_x = result.params['centerx'].value
        cen_y = result.params['centery'].value
        fwhmx = result.params['fwhmx'].value
        fwhmy = result.params['fwhmy'].value
        height = result.params['height'].value
        chisqr = result.chisqr
        cen_x_stderr = result.params['centerx'].stderr
        cen_y_stderr = result.params['centery'].stderr

        fwhm_x = fwhmx * 0.089981
        fwhm_y = fwhmy * 0.089981
        tth = cen_x * 0.089981  # + 10
        chi = cen_y * 0.089981  # + 40

        print('\n',
              'tth:', tth, '\n',
              'chi:', chi, '\n',
              'fwhm_x', fwhm_x, '\n',
              'fwhm_y', fwhm_y,
              '\n')

    except Exception:

        print('exception')



#%%
#-----------------------------------SAXS----------------------------------------
def guinierFit(q,intensity,autoFit=True,q_range=None):
    '''
    Parameters
    ----------
    q: 1D array 
    intensity : 1D array
    autoFit : bool
        True-q_range for guinier is auto fited. False- user defined q_range is used when fitting.
    q_range : tuple (idx_min,idx_max)
        Only used when autoFit is False.

    Returns
    -------
    result : dict including fitting parameters.
    fun_lnI : function used for calculating yfit.

    '''

    profile=SASM.SASM(i=intensity,q=q , err=np.zeros_like(q), parameters={'filename':None}) #generate an object of SASM for input of function auto_guinier

    try:
        if autoFit is True:
            resultTemp=raw.auto_guinier(profile,error_weight=False)
            ###返回值resultTemp=(rg, i0, rg_err, i0_err, qmin, qmax, qrg_min, qrg_max, idx_min, idx_max,r_sq)####
            result={'Rg':resultTemp[0],'I0':resultTemp[1],'rg_err':resultTemp[2],'i0_err':resultTemp[3],
                    'qmin': resultTemp[4],'qmax': resultTemp[5],'qrg_min': resultTemp[6],'qrg_max': resultTemp[7],
                    'qmin_Pixel':resultTemp[8],'qmax_Pixel':resultTemp[9],'r_sq':resultTemp[10]}
        else:
            resultTemp=raw.guinier_fit(profile, qmin=q_range[0], qmax=q_range[1], error_weight=False)
            result = {'Rg': resultTemp[0], 'I0': resultTemp[1], 'rg_err': resultTemp[2], 'i0_err': resultTemp[3],
                      'qmin': resultTemp[4], 'qmax': resultTemp[5], 'qrg_min': resultTemp[6], 'qrg_max': resultTemp[7],
                       'qmin_Pixel':resultTemp[8], 'qmax_Pixel': resultTemp[9],'r_sq':resultTemp[10]}
        

        fun_lnI=lambda I0,Rg,q:np.log(I0)-Rg**2*q**2/3      
        
        return result,fun_lnI

    except Exception: # all exception
        #traceback.print_exc()
        result = {'Rg': np.nan, 'I0': np.nan, 'rg_err': np.nan, 'i0_err': np.nan,
                  'qmin': np.nan, 'qmax':np.nan, 'qrg_min':np.nan, 'qrg_max': np.nan,
                  'qmin_Pixel':np.nan, 'qmax_Pixel': np.nan,'r_sq':np.nan}
        fun_lnI=np.nan
        return result,fun_lnI
        

def porodFit(q,intensity,q_range):
    '''
    Parameters
    ----------
    q : 1D array
    intensity : 1D array
    q_range : tuple
        High q range for Porod Operation.


    Returns
    -------
    xPorod:   Porod plot x
    yPorod:   Porod plot y
    slopefit: Porod linear range-slope
    lnKfit:   Porod linear range-lnK (intercept)

    '''
    #x,y are for Porod Operation and Plot
    xPorod=q**2
    yPorod=np.log(intensity*q**4)
    
    xcal=xPorod[q_range[0]:q_range[1]+1]
    ycal=yPorod[q_range[0]:q_range[1]+1]

       
    #ln[q^4I(q)]=lnK+slope*q^2
    #initial guess for sigma^2
    value_slope=(ycal[-1] - ycal[0]) / (xcal[-1] - xcal[0])
    #initial guess for lnK
    value_lnK=ycal[0] - value_slope* xcal[0]
    

    # create a set of Parameters    
    params=Parameters()
    params.add('slope',value=value_slope)
    params.add('lnK',value=value_lnK)
    # defined function

    def fun_porod(params,x,y):

        slope=params['slope']
        lnK=params['lnK']
        model=lnK+slope*x
        return model-y
    
    # do fit, here with the default leastsq algorithm
    minner = Minimizer(fun_porod, params, fcn_args=(xcal, ycal))
    resultTemp = minner.minimize()
    # calculate final result para
    slopefit=resultTemp.params['slope'].value
    lnKfit=resultTemp.params['lnK'].value
    
    return xPorod,yPorod,slopefit,lnKfit

def porodCorrect(q,intensity,slopefit,lnKfit):   
    
    #I'(q)=exp(sigma^2*q^2)I(q)
    #only correct for high q---wrong
    # correct_I=y0[self.get_param_value('q_range')[0]:]*np.exp(slopefit*x[self.get_param_value('q_range')[0]:])
    # correct_I_allRange=np.append(y0[0:self.get_param_value('q_range')[0]],correct_I)
    # y_correct_allRange=np.log(correct_I_allRange*x0**4)
    #correct for all q range-right 
    
    intensity_correct=intensity*np.exp(-slopefit*q**2)
    yPorod_correct=np.log(intensity_correct*q**4)
    
    return intensity_correct,yPorod_correct


def KratkyFit(q,intensity,autoFit=True,q_range=None):
    if autoFit is False:
        return q,I*(q**2)


    

#------------------------------------------------------------------------------
def integralInvariant(x,y,rg,i0,porodK):
    
    #integrate fun=I(q)*q^2
    igq2 = lambda q: (i0*np.exp(-rg**2*q**2/3))*q**2
    ipq2 = lambda q: porodK/q**2
    
    inv1,error=integrate.quad(igq2,0,x[0])
    inv2=np.trapz(y,x)
    inv3,error=integrate.quad(ipq2,x[-1],np.inf)
    invQ=inv1+inv2+inv3
    
    return invQ

#%%
#---------------------------------ImageOperation-------------------------------
# image flip

def imageFlip(data,axis='Along Y Axis'):    
    '''
    Parameters
    ----------
    data : 2D array
    axis : direction

    Returns
    -------
    data : 2D array

    '''
    if axis=='Along Y Axis':
        data=np.flipud(data) #top and down
        
    if axis=='Along X Axis':
        data=np.fliplr(data)#left and right
    
    return data

#%%
#---------------------------------Normalization--------------------------------
# normalization for SAXS
def normalizeSAXS(data,ic_sample,coeff_sample,bg,ic_bg,coeff_bg,noise):
    
    return (data-noise)/ic_sample*coeff_sample-(bg-noise)/ic_bg*coeff_bg
    
    
#%%
# generate fit2d parameters based on .poni file


#%%
#----------------------------------Curve Operation-----------------------------
'''
# 1D mask include
# curve take positive value
def curvePositive(x,y):
    x=x[y>0]
    y=y[y>0]
    
    return x,y
'''

#%%
#----------------------------------------------------------------------------        
if __name__ == '__main__':
    pass
