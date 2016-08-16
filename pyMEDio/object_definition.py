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
# file       : mesh_object.py 
# content    : Definition of the Mesh object                                          
# author     : Basile Marchand (basile.marchand@gmail.com)                                                                     
# date       : 17-07-2016                                                     
#----------------------------------      


import numpy as np

class Mesh(object):
    
    def __init__(self, name):
        self.NAME = name
        self.NN   = None
        self.NE   = None
        self.COOR = None
        self.CONNEC = None
        self.ELEMS  = None
        self.GROUPS = None

    def __repr__(self):
        text = "pyMEDio.Mesh object \n"
        text += "   NN : %i \n"%(self.NN)
        text += "   NE : %i \n"%(self.NE)
        text += "   GROUPS : " + " ; ".join(list(self.GROUPS.keys())) + "\n"
        return text
        

class Field(object):
    def __init__(self, name, components, support, mesh):
        self.NAME = name
        self.MESH = mesh
        self.COMPONENTS = components
        self.NCOMPO = len(components)
        self.SUPPORT = support
        if support=="NODES":
            self.SIZE = (self.MESH.NN, self.NCOMPO)
        elif support=="ELEMS":
            self.SIZE = (self.MESH.NE, self.NCOMPO)
        else:
            print("Error : support %s not supported yet"%(support))

        self._init_values()

    def _init_values(self):
        self.__values = np.zeros(self.SIZE)

    def __getitem__(self, item):
        return self.__values[item]

    def __setitem__(self, item, value):
        self.__values[item] = value
    
    def __repr__(self):
        text = "pyMEDio.Field object defined at %s level\n"%(self.SUPPORT)
        text += "   Field Name : %s \n"%(self.NAME)
        text += "   Components : " + " ; ".join(self.COMPONENTS) + "\n"
        text += "   Size       : " + " ; ".join([str(x) for x in self.SIZE]) + "\n"
        return text
