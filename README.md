
### pyMEDio
@author : Basile Marchand  
@mail   : basile.marchand@gmail.com

pyMEDio, for python MED file input/output, is a pure python implementation of the MED file format developped
by EDF Research and Development and the CEA (Commissariat à l'Energié Atomique). The original implementation
of the MED file library is done in C++ with a python wrapper, only working for python2.7. 
That's why I have made this python packages to simply enable the use of the MED file format
in python code.   

The MED file format is mainly used in the SALOME platform and Code_Aster. In the first one it is used to write mesh file
and in the second one it is added results fields for post-processing. Hidden behind the MED file format there is the 
HDF5 one. That is why to work pyMEDio require h5py packages and also the numpy package.   

pyMEDio work with python3.X and perhaps with python2.7+, I have never done test ....  


All ideas for new functionalities or comments are welcome and can be send to basile.marchand@gmail.com


### Installation : really simple

- Download the packages or clone git repository

- extend your PYTHONPATH variable : 
  -  in your .bashrc file as follow   
         export PYTHONPATH="/path/to/pyPointer/package:$PYTHONPATH"
  -  or dynamicaly in your python script as follow   
         import sys  
         sys.path.insert(0, "path/to/pyPointer/package")  



 
