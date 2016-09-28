#==============================================================================
# Copyright (C) 2016 Marchand Basile                                  
#                                                                     
# This file is part of pyMEDio  
#                                                                     
# pyMEDio is free software: you can redistribute it and/or modify   
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or   
# any later version.                           
#                                                               
# pyMEDio is distributed in the hope that it will be useful,   
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the  
# GNU General Public License for more details.
#                                
# You should have received a copy of the GNU General Public License 
# along with pyPointer.  If not, see <http://www.gnu.org/licenses/>   
#==============================================================================          
#----------------------------------      
# package    : pyMEDio     
# file       : elem_translation.py 
# content    : Contain connectivity tables between MED/VTK/GMSH elements definitions                                          
# author     : Basile Marchand (basile.marchand@gmail.com)                                                                     
# date       : 17-07-2016                                                     
#----------------------------------      

_MED2MED = {"PO1":{"nn":1,"id":"PO1","ngauss":0,"geo":'001'},
            "SE2":{"nn":2,'id':"SE2","ngauss":1,"geo":'102'},
            "TR3":{"nn":3,'id':"TR3","ngauss":3,"geo":'203'},
            "QU4":{"nn":4,'id':"QU4","ngauss":3,"geo":'204'},
            "TE4":{"nn":4,'id':"TE4","ngauss":4,"geo":'304'},
            "PY5":{"nn":5,'id':"PY5","ngauss":4,"geo":'305'}}


### Table for Reader class

_MED2VTK = {"PO1":{"nn":1,"id":1},
            "SE2":{"nn":2,'id':3},
            "TR3":{"nn":3,'id':5},
            "QU4":{"nn":4,'id':9},
            "TE4":{"nn":4,'id':10}}

_MED2MSH = {"PO1":{"nn":1,"id":15},
             "SE2":{"nn":2,'id':1},
             "TR3":{"nn":3,'id':2},
             "QU4":{"nn":4,'id':3},
             "TE4":{"nn":4,'id':4}}

### Table for Writer class

_GMSH2MED = None



_VTK2MED = {1:{'id':"PO1", 'nn':1, 'ngauss':0, 'geo':'001'},
            3:{'id':"SE2", 'nn':2},
            5:{'id':"TR3", 'nn':3},
            9:{'id':"QU4", 'nn':4},
            10:{'id':"TE4",'nn':4}}



### To delete


_GMSH2VTK = {1 : 3,    # SEG2
             2 : 5,    # TRI3
             3 : 9,    # QUA4
             4 : 10,   # TET4
             5 : 12,   # HEX8
             6 : 13,   # PRI6
             7 : 14,   # PYR5
             8 : 21,   # SEG3
             9 : 22,   # TRI6
             11 : 24,  # TET10
             15 : 1,    # VERTEX
             16 : 23}  # QUA8 
