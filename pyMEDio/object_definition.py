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
        
    def merge_without_remove(self, other):
        ### Used to merge two meshes, don't remove double nodes !!
        res = Mesh("merged")
        res.NN = self.NN + other.NN
        res.NE = self.NE + other.NE
        #offset_coor = other.COOR + self.NE
        res.COOR = np.concatenate((self.COOR, other.COOR),axis=0)
        offset_connec = other.CONNEC
        ## Merge connectivity table
        for i,elem in enumerate(offset_connec):
            tmp = np.array(elem[3:])
            elem[0] += self.NE   ## offset elem numbering
            tmp += self.NN  ## offset nodes numbering
            offset_connec[i] = elem[:3] + tmp.tolist()

        res.CONNEC = np.concatenate((self.CONNEC, offset_connec), axis=0)
        ## Merge ELEMS dictionnary 
        res.ELEMS = self.ELEMS
        for key,value in other.ELEMS.items():
            tmp = (np.array(value)+self.NE).tolist()
            if key in res.ELEMS.keys():
                res.ELEMS[key] += tmp
            else:
                res.ELEMS[key] = tmp

        ## Merge groups dictionnary
        res.GROUPS = self.GROUPS
        for key,value in other.GROUPS.items():
            tmp = (np.array(value)+self.NE).tolist()
            if key in res.GROUPS.keys():
                res.GROUPS[key] += tmp
            else:
                res.GROUPS[key] = tmp
        return res


    def __add__(self, other):
        res = self.merge_without_remove(other)
        return res
        


class Field(object):
    def __init__(self, name, components, support, mesh):
        self.NAME = name
        self.MESH = mesh
        self.COMPONENTS = components
        self.NCOMPO = len(components)
        self.SUPPORT = support
        self.PROFILS = None
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

    def __merge_components(self, other):
        if self.COMPONENTS == other.COMPONENTS:
            merged_components = self.COMPONENTS
        elif self.NCOMPO == other.NCOMPO:
            _LOGGER.warning("The two fields  doesn't have the same components name, it is used : {}".format(";".join(self.COMPONENTS)))
            merged_components = self.COMPONENTS
        else:
            _LOGGER.error("The two fields to merged doesn't have the same number of components")
            sys.exit(3)
        return self.NCOMPO, merged_components

    def __add__(self, other):
        merged_name = self.NAME
        nbr_comp, comp = self.__merge_components(other)
        if self.SUPPORT != other.SUPPORT:
            _LOGGER.error("The two fields to merge are defined to different level")
            sys.exit(4)
        supp = self.SUPPORT        
        mesh = self.MESH + other.MESH
        res = Field(merged_name, comp, supp, mesh)
        
        res[:] = np.concatenate((self.__values, other[:]), axis=0)

        if self.PROFILS is not None:
            prof_name1 = list(self.PROFILS.keys())[0]
            prof_name2 = list(other.PROFILS.keys())[0]
            if res.SUPPORT == "NODES":
                prof_index = np.concatenate((self.PROFILS[prof_name1],(other.PROFILS[prof_name2]+self.MESH.NN)), axis=0) 
            elif res.SUPPORT == "ELEMS":
                prof_index = np.concatenate((self.PROFILS[prof_name1],(other.PROFILS[prof_name2]+self.MESH.NE)), axis=0)
            res.PROFILS = {prof_name1 : prof_index}
        return res
        

    def __repr__(self): 
        text = "pyMEDio.Field object defined at %s level\n"%(self.SUPPORT)
        text += "   Field Name : %s \n"%(self.NAME)
        text += "   Components : " + " ; ".join(self.COMPONENTS) + "\n"
        text += "   Size       : " + " ; ".join([str(x) for x in self.SIZE]) + "\n"
        return text
