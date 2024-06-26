# StreamSAXS <br>
StreamSAXS is a Python-based SAXS/WAXS data analysis workflow platform with GUI. <br>
## Installation <br>
{StreamSAXS runs on Windows currently.} <br>
<br>
1.Environment Setup <br>
`pip install -r requirements.txt` <br>
<br>
2.Third-party packages <br>
ASTRA <br>
(@ https://github.com/astra-toolbox/astra-toolbox) <br>
-->`pip install astra-toolbox` <br>
-->`conda install astra-toolbox -c astra-toolbox -c nvidia` <br>
<br>
BioXTAS RAW <br>
(@ https://sourceforge.net/projects/bioxtasraw/) <br> 
-->Directly copy the bioxtasraw source folder <br>
-->https://bioxtas-raw.readthedocs.io/en/latest/install.html <br>
<br>
3. Download the StreamSAXS project, run main.py <br>
(\examples\ contains data files that may slow down the download speed. <br>
&emsp;These folder is provided for familiarizing users with the operating procedures and is unnecessary for running the project.) <br>
<br>
## Running Example <br>
1. Import workflow file --> \examples\PeakFit.yaml <br>
2. Select input <br>
   Load 2D Data -->  \examples\data\  <br>
   Detector Calibration via PyFAI --> \examples\calibration.poni <br>
   User-defined Mask 2D --> \examples\mask01.tif <br>
3. Set plot widget <br>
   3.1 Creation <br>
     Default: Plot1d for I(q), Plot1d for I(chi), Plot2d for mapping <br>
     Right Click - add image visualizer - "RawData" <br>
     Right Click - add plot 1d - "PeakFit" <br>
   3.2 Layout <br>
     Close "I(q)" widget <br>
     Drag "RawData" widget to merge with Plot2d <br>
3. Associate plot widget <br>
   Right Click - select connect widget
   Load 2D Data -->  "RawData" widget <br>
   Radial Integration & Background Subtraction --> "I(chi)" widget <br>
   Single Peak Fitting --> "PeakFit" widget <br>
   Single Peak Fitting Plot --> plot2d widget, set X=101/Y=10 within plot2d widget <br>
4. Run the workflow <br>
   
## Documentation <br>
The default components provided by StreamSAXS are listed in file Default Components.txt.<br>
<br>
## Getting help
A mailing-list, wangjy@ihep.ac.cn, is available to get help on the program and how to use it. 
