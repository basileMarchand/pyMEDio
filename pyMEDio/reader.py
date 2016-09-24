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
# file       : reader.py 
# content    : Class definition to read object in a MED file; mesh, groups, fields                                          
# author     : Basile Marchand (basile.marchand@gmail.com)                                                                     
# date       : 17-07-2016                                                     
#----------------------------------      

import sys
from operator import itemgetter
import numpy as np
import h5py
import logging
from .elem_translation import _MED2VTK, _MED2MSH, _MED2MED
from .object_definition import Mesh, Field


_LOGGER = logging.getLogger('pyMEDio.reader')

class MEDReader(object):
    """
    MEDReader class 
    
    Class to open and extract object from a MED file.

    Possibilities are the following
    -> Read meshes in the MED file
    -> Read fields in the MED file : 
        -> Fields defined at the nodes level
        -> Fields defined at the elements level

    """

    def __init__(self, med_file, output_format="MED"):
        """ 
        MEDReader class __init__ function 
        
        Parameters 
        -----------
        med_file : string
            the path of the med_file to read
        output_format : string {"MED", "VTK", "GMSH"}, default MED
            the syntax used for the returned mesh

        """ 
        try:
            self.med_root = h5py.File(med_file,'r')
            _LOGGER.info("MED file {} succesfully opened".format(med_file))
        except IOError:
            _LOGGER.error("MED file {} doesn't exist".format(med_file))
            sys.exit(1)
        
        self.__set_translator(output_format)
        self.__readed_meshes = {} 
    
    def __set_translator(self, output_format):
        """
        set the dictionnary to use for the elements names according to 
        user choice
        """ 
        if output_format=="MED":
            self.__translator = _MED2MED
        elif output_format=="VTK":
            self.__translator = _MED2VTK
        elif output_format=="GMSH":
            self.__translator = _MED2MSH
        else:
            _LOGGER.error("The output_format require %f is not avalaible yet"%(output_format))
            sys.exit(1)

    def read_attrs(self, grp_level):
        return self.med_root[grp_level].attrs
    
    def read_data(self, grp_level):
        return self.med_root[grp_level][:]

    def get_meshes_names(self):
        """
        Method which returns the names of meshes stored in the MED file

        Returns 
        -----------
        output : list of string
            the list of all meshes name stored in the MED file
        """

        return list(self.med_root['/ENS_MAA'])

    def get_mesh_info(self, mesh_name):
        """ 
        Method which returns some information about mesh

        Parameter 
        ----------
        mesh_name : (str)
             the name of the mesh to get information
        
        Return
        ------
        output : dict
             dictionnary which contains some informations about the mesh mesh_name
        """
        iden_list = list(self.med_root['ENS_MAA'][mesh_name].keys())
        iden = iden_list[0]
        info = self.med_root['ENS_MAA'][mesh_name][iden]['NOE']['NUM'].attrs['NBR']
        return info


    
    def read_mesh(self, msh_name=None):
        """
        method which read mesh definitionand return a Mesh object
        
        Parameters
        ------------
        msh_name : string optional,
             the name of the mesh to read, if None it is the first mesh
             defined in the med file which is read

        Returns
        -----------
        output : Mesh
            the corrisponding mesh object
        """

        if msh_name==None:
            mesh_list = list(self.med_root['/ENS_MAA'])
            msh_name = mesh_list[0]
            
        NN, COOR = self._read_nodes_data(msh_name)
        NE, CONNEC, ELEM_BY_TYPES, GROUP_DIC = self._read_elem_data(msh_name)

        mesh = Mesh(msh_name)
        mesh.NN     = NN
        mesh.NE     = NE
        mesh.COOR   = COOR
        mesh.CONNEC = CONNEC
        mesh.ELEMS  = ELEM_BY_TYPES
        mesh.GROUPS = GROUP_DIC

        self.__readed_meshes[mesh.NAME] = mesh
        return mesh

    def _read_nodes_data(self, msh_name):
        """
        Method which reads nodal information about mesh, i.e. nodes coordinates
        """ 
        iden_list = list(self.med_root['ENS_MAA'][msh_name].keys())
        if len(iden_list) > 1:
            _LOGGER.warning("MED file contains multiple mesh iteration (default iteration 0 is read)")
        iden = iden_list[0]
        NUM = np.array(self.med_root['ENS_MAA'][msh_name][iden]['NOE']['NUM'], dtype=np.int32)
        NN = NUM.shape[0]
        COOR = np.array(self.med_root['ENS_MAA'][msh_name][iden]['NOE']['COO']).reshape((-1,NN)).T
        if COOR.shape[1]!=3:
            COOR = np.concatenate((COOR, np.zeros((NN,1))),axis=1)
        _LOGGER.info("nodes have been read")
        _LOGGER.info("nn = {}".format(NN))
        return NN, COOR

    def _read_elem_data(self, msh_name):
        """
        Method which reads elements informations about mesh, i.e. connectivity and elements groups
        """
        NE = 0
        iden = list(self.med_root['ENS_MAA'][msh_name].keys())[0]
        list_elem_types = list(self.med_root['ENS_MAA'][msh_name][iden]['MAI'].keys())
        for key in list_elem_types:
            NE += self.med_root['ENS_MAA'][msh_name][iden]['MAI'][key]['NUM'].attrs['NBR']

        med_grp_name = {}
        grp_salome_list = list(self.med_root['FAS'][msh_name]['ELEME'].keys())
        for grp_key in grp_salome_list:
            name_bytes = self.med_root['FAS'][msh_name]['ELEME'][grp_key]["GRO"]['NOM'][:].tostring()
            name = name_bytes.decode().rstrip("\x00").rstrip()
            med_id = str(self.med_root['FAS'][msh_name]['ELEME'][grp_key].attrs['NUM'])
            med_grp_name[med_id] = name
        
        if "FAMILLE_ZERO" in self.med_root['FAS'][msh_name].keys():
            med_grp_name[str(0)] = "FAMILLE_ZERO"
            
    
        _LOGGER.info("reading elements")
        _LOGGER.info("ne = {}".format(NE))
        CONNEC = np.zeros(NE,dtype=list)
        group_list = np.zeros((NE,2),dtype=int)

        ELEM_BY_TYPES = {}
        for key in self.__translator.keys():
            ELEM_BY_TYPES[self.__translator[key]['id']] = []

        for key_type in list_elem_types:
            n_nodes = self.__translator[key_type]["nn"]
            tmp_connec = np.array(self.med_root['ENS_MAA'][msh_name][iden]['MAI'][key_type]['NOD']).reshape((n_nodes,-1))-1
            tmp_connec = tmp_connec.T
            tmp_num = np.array(self.med_root['ENS_MAA'][msh_name][iden]['MAI'][key_type]['NUM']) - 1
            tmp_grp = np.array(self.med_root['ENS_MAA'][msh_name][iden]['MAI'][key_type]['FAM'])
            e_id = self.__translator[key_type]['id']
            group_list[tmp_num,:] = np.column_stack((tmp_grp, tmp_num))
            for e_num,e_grp,e_connec in zip(tmp_num,tmp_grp,tmp_connec):
                CONNEC[e_num] = [e_num, e_id, med_grp_name[str(e_grp)]]+ e_connec.tolist()
                ELEM_BY_TYPES[e_id].append(e_num)
                
        ### Create the group dictionnary
        list_grp_name = list(set(group_list[:,0].tolist() + [0]))

        group_list.view('i8,i8').sort(order=['f1'], axis=0)
        group_dic = {}
        for key,value in med_grp_name.items():
            group_dic[value]= group_list[group_list[:,0]==int(key),1].astype(int).tolist()
            list_grp_name.remove(int(key))
            
        for grp_id in list_grp_name:
            group_dic[str(grp_id)] = group_list[group_list[:,0]==grp_id,1].astype(int).tolist()
        _LOGGER.info('------------------------------------------')
    
        FINAL_ELEM_BY_TYPES = {}
        for k,v in ELEM_BY_TYPES.items():
            if len(v)!=0:
                FINAL_ELEM_BY_TYPES[k] = v
        return NE, CONNEC, FINAL_ELEM_BY_TYPES, group_dic

    def get_fields_names(self):
        return list(self.med_root['/CHA/'].keys())

    def read_field(self, field_id):
        """ 
        Method which read all iterations, time step, of a given field
        
        Parameter 
        ---------
           field_id : (str)
               name of the fields steps to read
        Output
        -------
           out : (list)
               the list of all time step for the given field name
        """
        list_steps = self._get_field_steps(field_id)
        field_list = []
        for time, ite in list_steps:
            field = self.read_field_at_time(field_id, time, ite)
            field_list.append(field)
        return field_list
        
    def _get_field_steps(self, field_id):
        grp_sol = self.med_root['/CHA/'][field_id]
        list_steps = []
        for index in grp_sol.keys():
            time = grp_sol[index].attrs["NDT"]
            ite  = grp_sol[index].attrs["PDT"]
            list_steps.append( (time, ite) )
        return list_steps

    def read_field_at_time(self, field_id, time, ite):
        field_support, mesh_support  = self._get_field_support(field_id, time, ite)

        if mesh_support in self.__readed_meshes.keys():
            mesh = self.__readed_meshes[mesh_support]
        else:
            mesh = self.read_mesh(mesh_support)

        if field_support == "NODES":
            val, components = self._read_nodal_field(field_id, time, ite)
        elif field_support=="ELEMS":
            val, components = self._read_elem_field(field_id, time, ite)
        elif field_support=="GAUSS":
            val, components = self._read_gauss_field(field_id, time, ite)

        res = Field(field_id, components, field_support, mesh) 
        res[:] = val
        return res

    def _get_field_support(self, field_id, time, ite):
        grp_sol = self.med_root['/CHA/'][field_id]
        mesh_support = grp_sol.attrs['MAI']
        if time is None:
            time = list(grp_sol.keys())[0]
        else:
            time ="%.20d%.20d"%(time, time)
        grp_sol_t = grp_sol[time]
        sub_key = list(grp_sol_t.keys())[0]
        if "NOE" in sub_key:
            return "NODES", mesh_support
        elif "MAI" in sub_key:
            return "ELEMS", mesh_support

    def _read_nodal_field(self, field_id, time, ite):
        """
        Method which read a nodal field in the med file

        Parameters 
        -----------
        field_id : string
              the name of the field to read
        time : int
              the time step to read
        iter : int
              the iteration to read

        Returns 
        -----------
        output : Field object 
              the require field in a Field object
        """ 
        grp_sol = self.med_root['/CHA/'][field_id]
        N_COMPO = grp_sol.attrs["NCO"]
        
        comp_crude = grp_sol.attrs["NOM"]
        components = [ comp_crude[(i*16):(i+1)*16].strip().decode('utf-8') for i in range(N_COMPO)]
        grp_sol_t = grp_sol["%.20d%.20d"%(time, time)]['NOE/MED_NO_PROFILE_INTERNAL']
        NBR = grp_sol_t.attrs['NBR']
        field_crude = grp_sol["%.20d%.20d"%(time, time)]['NOE/MED_NO_PROFILE_INTERNAL/CO'][:]
        field = field_crude.reshape((N_COMPO,NBR)).T
        return field, components

    def _read_elem_field(self, field_id, time, ite):
        """
        Method which read an element level field in the med file

        Parameters 
        -----------
        field_id : string
              the name of the field to read
        time : int
              the time step to read
        iter : int
              the iteration to read

        Returns 
        -----------
        output : ndarray 
              the require field in a numpy ndarray format with the size (Nelements , Ncomponents)
        """ 
        grp_sol = self.med_root['/CHA/'][field_id]
        SUPPORT = grp_sol.attrs["MAI"]
        ### Read mesh information
        _, _, ELEM_BY_TYPES, _ = self._read_elem_data(SUPPORT)
        
        N_COMPO = grp_sol.attrs["NCO"]
        comp_crude = grp_sol.attrs["NOM"]
        components = [ comp_crude[(i*16):(i+1)*16].strip().decode('utf-8') for i in range(N_COMPO)]
        grp_sol_t = grp_sol["%.20d%.20d"%(time, time)]
        types_elem_list = grp_sol_t.keys()
        ### loop one to count total number of elements
        NE = 0
        for e_type in types_elem_list:
            NE += grp_sol_t[e_type+'/MED_NO_PROFILE_INTERNAL'].attrs['NBR']
        field = np.zeros((NE, N_COMPO))
        for e_type in types_elem_list:
            field_on_type = grp_sol_t[e_type+'/MED_NO_PROFILE_INTERNAL/CO'][:].reshape((N_COMPO,-1)).T
            list_elem = ELEM_BY_TYPES[self.__translator[e_type.split('.')[1]]['id']]
            field[list_elem, :] = field_on_type
        return field, components
    
    def _read_gauss_field(self, field_id, time, ite):
        """
        Method which read a Gaussian nodes level field in the med file

        Parameters 
        -----------
        field_id : string
              the name of the field to read
        time : int
              the time step to read
        iter : int
              the iteration to read

        Returns 
        -----------
        output : ndarray 
              the require field in a numpy ndarray format with the size (Nelem, NGaussPoints , Ncomponents)
        """ 
        return NotImplementedError

    def __repr__(self):
        return NotImplementedError
    
    def end(self):
        self.med_root.close()


