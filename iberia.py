#Creating/Opening a netCDF file
'''
There are many options for working with NetCDF files
in Python. In this example we have chosen to highlight
the use of the netCDF4-python module.

The netCDF4-python module is useful because:
    • It implements the basic “classic” model as well as
    more advanced features.
    • It provides a simple interface to the NetCDF
    structure.
    • It has been used as the underlying NetCDF I/O layer
    for many more advanced packages.
'''
'''
To create a netCDF file from python, you simply call the
Dataset() constructor. This is also the method used
to open an existing netCDF file.

If the file is open for write access (w, r+ or a), you
may write any type of data including new dimensions,
groups, variables and attributes.

The netCDF4 module can read and write files in any
netCDF format. When creating a new file, the format
may be specified using the format keyword in the
Dataset constructor. The default format is
NETCDF4.

This tutorial will focus exclusively on the NetCDF-
”classic” data model using: NETCDF4_CLASSIC
'''
from netCDF4 import Dataset

#Open a netCDF file in write "w" mode
dataset = Dataset('data/iberia.nc' , 'w' , format='NETCDF4_CLASSIC')

#Create dimensions
print(dataset.file_format)
#-- level = dataset.createDimension('level', 1)
#-- lat = dataset.createDimension('lat', 320)
#-- lon = dataset.createDimension('lon', 400)
south_north = dataset.createDimension('south_north', 320)
west_east = dataset.createDimension('west_east', 400)
time = dataset.createDimension('time', None)
#-- print(len(south_north))
#-- print(len(west_east))
#-- print(time.isunlimited())

#Query dimensions. All Dimension instances are stored in a python dictionary
#-- print('west_east dimension:' , dataset.dimensions['west_east'])

for dimname in dataset.dimensions.keys():
    dim = dataset.dimensions[dimname]
    print(dimname, len(dim), dim.isunlimited())

#Variables
'''
NetCDF variables behave much like python multi-dimensional arrays in numpy. However, unlike numpy
arrays, netCDF4 variables can be appended to along the 'unlimited' dimension (a.k.a. the "record dimension").
'''
import numpy as np
# Create coordinate variables for 4-dimensions
times = dataset.createVariable('time', np.float64, ('time',))
#-- levels = dataset.createVariable('level', np.int32, ('level',))
#-- latitudes = dataset.createVariable('latitude', np.float32, ('lat',))
#-- longitudes = dataset.createVariable('longitude', np.float32, ('lon',))
latitudes = dataset.createVariable('lat', np.float32, ('south_north', 'west_east',))
longitudes = dataset.createVariable('lon', np.float32, ('south_north', 'west_east',))
# Create the actual 4-d variable
#-- temp = dataset.createVariable('temp', np.float32, ('time','level','south_north', 'west_east'))
temp = dataset.createVariable('temp', np.float32, ('time','south_north', 'west_east'))

#Accessing variables
'''
All of the variables in the Dataset are stored in a
Python dictionary, in the same way as the dimensions:
'''
print ('temp variable:', dataset.variables['temp'])
for varname in dataset.variables.keys():
    var = dataset.variables[varname]
    print (varname, var.dtype, var.dimensions, var.shape)

# Global Attributes
'''
Global attributes are set by assigning values to
Dataset instance variables. Attributes can be strings,
numbers or sequences.
'''
import time
dataset.description = 'Iberia en 400x320 celdas (3kmx3km por celda)'
dataset.history = 'Created ' + time.ctime(time.time())
dataset.source = ''

# Variable Attributes
'''
Variable attributes are set by assigning values to
Variable instance variables:
'''
latitudes.units = 'degrees_north'
latitudes.long_name = 'Latitude'
latitudes.standard_name = 'latitude'
longitudes.units = 'degrees_east'
longitudes.long_name = 'Longitude'
longitudes.standard_name = 'longitude'
#-- levels.units = 'hPa'
temp.long_name = "Temperature at 2 m" ;
temp.standard_name = "air_temperature" ;
temp.units = 'degC'
temp.coordinates = 'lon lat'
times.units = 'hours since 2001-01-01 00:00:00'
times.calendar = 'standard'
times.long_name = 'Time'
times.standard_name = 'time'

#Accessing attributes
'''
Attributes are accessed as attributes of their
relevant instances:
'''
print(dataset.description)
print(dataset.history)

#Writing data
'''
Now that you have a netCDF Variable instance, how
do you put data into it? You can just treat it like an array
and assign data to a slice.
'''
#-- lats = np.arange(35.5,44,0.0265625)
#-- lons = np.arange(-9.5,4.5,0.035)
#-- latitudes[:] = lats
#-- longitudes[:] = lons
#-- latitudes[:], longitudes[:] = np.mgrid[0:320,0:400]
latitudes[:], longitudes[:] = np.mgrid[35.5:44:0.0265625,-9.5:4.5:0.035]

print('latitudes =\n', latitudes[:])
print('longitudes =\n', longitudes[:])

#Growing data along unlimited dimension
'''
Unlike NumPy's array objects, netCDF Variable
objects that have an unlimited dimension will grow
along that dimension if you assign data outside the
currently defined range of indices.
'''
'''
NOTE: numpy.random.uniform(size = X) returns values
from a uniform distribution in a numpy array with
dimensions expressed in a tuple X.
'''
print('temp shape before adding data = ', temp.shape)
nlats = len(dataset.dimensions['south_north'])
nlons = len(dataset.dimensions['west_east'])
from numpy.random import uniform
temp[0:24,:,:] = 10*uniform(size=(24,nlats,nlons))

#-- temp[0:24,:,:,:] = np.ones(shape=(24,1,nlats,nlons))
#-- temp[0:24,:,:] = np.ones(shape=(24,nlats,nlons))

'''
for ii in range(24):
    for jj in range(nlats):
        for kk in range(nlons):
            temp[ii,jj,kk]=(1000*ii)+jj+kk
'''  
temp[0:24,:,:] = np.array([[[(10.0*ii)+jj+kk for kk in range(nlons)] for jj in range(nlats)] for ii in range(24)])

print('temp shape after adding data = ', temp.shape)

#Defining date/times correctly
'''
Time coordinate values pose a special challenge to
netCDF users. Most metadata standards (such as CF and
COARDS) specify that time should be measure relative
to a fixed date using a certain calendar, with units
specified like "hours since YY:MM:DD hh-mm-ss".

These units can be awkward to deal with, without a
utility to convert the values to and from calendar dates.
The functions num2date() and date2num() are
provided with this package to do just that.

num2date() converts numeric values of time in the specified
units and calendar to datetime objects, and
date2num() does the reverse.
'''
from datetime import datetime, timedelta
from netCDF4 import num2date, date2num
dates = []
for n in range(temp.shape[0]):
    dates.append(datetime(2020, 2, 1) + n * timedelta(hours=1))

times[:] = date2num(dates, units = times.units, calendar = times.calendar)
print('time values (in units %s): ' % times.units + '\n', times[:])
dates = num2date(times[:], units=times.units, calendar=times.calendar)
print('dates corresponding to time values:\n ', dates)

#Write the file
dataset.close()

