# General description
This repository is just a collection of useful Python code for SNOM data processing. Not all the implemented procedures are finished and tested.

# NeaSpectrum class
The NeaSpectra.py implements a base class for nano-FTIR, TERS, PTE, and PsHetPoint Spectroscopy data collected by NeaSNOM/NeaSCOPE instruments. `readNeaSpectrum` method of the NeaSpectrum class read the measurement parameter and the measurement data channels for the measurement `.txt` file.

## Usage
`test_neaspectrummodule.py` provides an example of creating a NeaSpectrum object and the measurement load data:
```python
import NeaSpectra as neas
s = neas.NeaSpectrum()
s.readNeaSpectrum(file_name)
```
The `parameters` attribute of the NeaSpectrum object is a dictionary containing the measurement parameters. For example:
```python
print(s.parameters["Project"])
print(s.parameters["Description"])
```
The `data` attribute is also a dictionary containing the measurement channels as key-value pairs. For example:
```python
s.data["Wavenumber"][0,0,:]
s.data["PTE"][0,0,:]
s.data["O3P"][0,0,:]
```
In case of hyperspectral measurement (linescan or areascan) the data channels are 3D numpy arrays, while in case of single spectra it is a simple numpy array with only one index.

# NeaImage class

The NeaImager.py file implements the base class for imaging measurements (PsHet, PTE, AFM) collected with NeaSCOPE instruments. The attributes of the class contain the basic parameters from the `.gwy` file. As an extra, you can load the additional measurement parameters from the info text file generated when you save the measurements.

## Usage
`test_neaimagemodule.py` provides an example how the create a NeaImage object and load the measurement. You have to create the object and call `read_from_gwyfile()` and define with measurement channel you want to load from the `.gwy` file:
```python
import NeaImager as neaim
channelname = 'O3P raw'
m = neaim.NeaImage()
m.read_from_gwyfile(meas_path,channelname)
m.parameters = m.read_info_file(info_path)
```
The `data` attribute contains the measured image as a 2d numpy array. The most basic measurement parameters related to the image are also read from the `.gwy` file. They are `xreal`,`yreal` - real, physical lengths of the corresponding axes, `xoff`,`yoff` - x and y offset of the middlepoint of teh corresponding axes (this is the scanner centor position basically), `xres`,`yres` - number of pixels along each axes. You can use these to plot the data with the physically correct axes. Example:
```python
import matplotlib.pyplot as plt
# Calculate min and max of the axis (*1e6 converts to microns from meters)
xmin = (-m.xreal/2+m.xoff)*1e6
xmax = (m.xreal/2+m.xoff)*1e6
ymin = (-m.yreal/2+m.yoff)*1e6
ymax = (m.yreal/2+m.yoff)*1e6
# Plot data with the correct axis extent
plt.imshow(m.data, extent=[xmin, xmax, ymin, ymax])
plt.xlabel('Scanner Position - X / micron')
plt.ylabel('Scanner Position - Y / micron')
plt.title('Original image')
plt.show()
```
The `parameters` attribute contains all the other measurement parameters that are not necessary but can be useful in some cases. For example:
```python
print(s.parameters["Scan"])
print(s.parameters["TargetWavelength"])
print(s.parameters["LaserSource"])
```

# Image correction methods
The NeaImager module not only defines the NeaImage class but also provides methods to correct image artifact and normalize the pixel values. These method are `BackgroundPolyFit`, `LineLevel`, `NeaImage`, `RotatePhase`, `SelfReferencing`, `SimpleNormalize`. The inputobject is a NeaImage object for all methods and their return value is a new NeaImage objact with the corresponding correction method applied.

`test_imageprocess.ipynb` notebook demonstrates the usage of all the available methods.