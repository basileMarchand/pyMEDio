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
# file       : writer.py
# content    : Class definition to write data in a MED file                                          
# author     : Basile Marchand (basile.marchand@gmail.com)                                                                     
# date       : 17-07-2016                                                     
#---------------------------------- 

import os
import logging
import numpy as np
import h5py

from .elem_translation import _VTK2MED, _MED2MED, _GMSH2MED

_LOGGER = logging.getLogger('pyMEDio.reader')

class MEDWriter(object):
    def __init__(self, med_file, input_format="MED"):
        """
        MEDWriter __init__ method which create a new MED file or open an existing 

        Parameters
        -----------
        med_file : string 
             the path to the med_file you want create or used

        input_format : string {"MED", "VTK", "GMSH"} default "MED"
             the syntax used in the Mesh object we will write in the MED file

        """
        self.__med_root = h5py.File(med_file, "w")
        self.__create_structure()
        
        self.__set_mesh_syntax(input_format)


    def __set_mesh_syntax(self, input_format):
        if input_format=="MED":
            self.__translator = _MED2MED
        elif input_format=="VTK":
            self.__translator = _VTK2MED
        elif input_format=="GMSH":
            self.__translator = _GMSH2MED
        else:
            _LOGGER.error('The input Mesh syntax %f is not avalaible'%(input_format))
            sys.exit(1)

    def __create_structure(self):
        """ 
        Method wich create the MED file structure backgrounds in the hdf5 file
        """
        grp = self.__med_root.create_group("INFOS_GENERALES")
        grp.attrs.create('MAJ',data=3,dtype=np.int32)
        grp.attrs.create('MIN',data=0,dtype=np.int32)
        grp.attrs.create('REL',data=8,dtype=np.int32)
        self.__med_root.create_group('ENS_MAA')
        self.__med_root.create_group('FAS')
        self.__med_root.create_group('CHA')
        self.__med_root.create_group('GAUSS')
        
    def add_group(self, grp_name, attrs):
        grp = self.__med_root.create_group(grp_name)
        for key, value in attrs.items():
            grp.attrs.create(key, data=value)
        
    def add_dataset(self, set_name, value):
        self.__med_root.create_dataset(set_name, data=value)
        
    def end(self):
        self.__med_root.close()
        
    def write_mesh(self, mesh_obj, iteration=1):
        """
        Method which write mesh informations; coordinates, connectivity, groups
        in the MED file

        Parameters 
        ------------
        mesh_obj : Mesh
              the Mesh object to write in the MED file
        iteration : int (optional)
              the iteration number associated to this mesh
        """
        grp_0_0 = self.__med_root['/ENS_MAA'].create_group(mesh_obj.NAME)
        grp_0_0.attrs.create('DES', data=b'')
        grp_0_0.attrs.create('DIM', data=3, dtype=np.int32)
        grp_0_0.attrs.create('ESP', data=3, dtype=np.int32)
        grp_0_0.attrs.create('NOM', data=b'')
        grp_0_0.attrs.create('NXI', data=-1, dtype=np.int32)
        grp_0_0.attrs.create('NXT', data=-1, dtype=np.int32)
        grp_0_0.attrs.create('REP', data=0, dtype=np.int32)
        grp_0_0.attrs.create('SRT', data=0, dtype=np.int32)
        grp_0_0.attrs.create('TYP', data=0, dtype=np.int32)
        grp_0_0.attrs.create('UNI', data=b'')
        grp_0_0.attrs.create('UNT', data=b'')
        
        grp_0_0_0 = grp_0_0.create_group('-0000000000000000001-0000000000000000001')
        grp_0_0_0.attrs.create('CGT',data=1, dtype=np.int32)
        grp_0_0_0.attrs.create('NDT',data=-1, dtype=np.int32)
        grp_0_0_0.attrs.create('NOR',data=-1, dtype=np.int32)
        grp_0_0_0.attrs.create('NXI',data=-1, dtype=np.int32)
        grp_0_0_0.attrs.create('NXT',data=-1, dtype=np.int32)
        grp_0_0_0.attrs.create('PDT',data=-1.0, dtype=np.float64)
        grp_0_0_0.attrs.create('PVI',data=-1, dtype=np.int32)
        grp_0_0_0.attrs.create('PVT',data=-1, dtype=np.int32)

        grp_0_0_0_NOE = grp_0_0_0.create_group('NOE')
        grp_0_0_0_NOE.attrs.create('CGS', data=1, dtype=np.int32)
        grp_0_0_0_NOE.attrs.create('CGT', data=1, dtype=np.int32)
        grp_0_0_0_NOE.attrs.create('PFL', data=b'MED_NO_PROFILE_INTERNAL', dtype=np.dtype('a24'))
        
        d1 = grp_0_0_0_NOE.create_dataset("NUM", data=(np.arange(mesh_obj.COOR.shape[0])+1) )
        d1.attrs.create('CGT', data=1, dtype=np.int32)
        d1.attrs.create('NBR', data=mesh_obj.COOR.shape[0], dtype=np.int32)
        d2 = grp_0_0_0_NOE.create_dataset("COO", data=mesh_obj.COOR.T.ravel())
        d2.attrs.create('CGT', data= 1, dtype=np.int32)
        d2.attrs.create('NBR', data= mesh_obj.COOR.shape[0], dtype=np.int32)
        d3 = grp_0_0_0_NOE.create_dataset("FAM", data=np.zeros(mesh_obj.COOR.shape[0],dtype=np.int32)) 
        d3.attrs.create('CGT', data= 1, dtype=np.int32)
        d3.attrs.create('NBR', data= mesh_obj.COOR.shape[0], dtype=np.int32)
        grp_0_0_0_MAI = grp_0_0_0.create_group('MAI')
        grp_0_0_0_MAI.attrs.create('CGT', data=1, dtype=np.int32)

        group_dict = self.__group_rename(mesh_obj)

        for e_type in mesh_obj.ELEMS.keys():
            grp_0_0_0_MAI_E = grp_0_0_0_MAI.create_group(self.__translator[e_type]['id'])
            grp_0_0_0_MAI_E.attrs.create('CGS',data=1, dtype=np.int32)
            grp_0_0_0_MAI_E.attrs.create('CGT',data=1, dtype=np.int32)
            grp_0_0_0_MAI_E.attrs.create('GEO',data=self.__translator[e_type]['geo'], dtype=np.int32)
            grp_0_0_0_MAI_E.attrs.create('PFL', data=b'MED_NO_PROFILE_INTERNAL', dtype=np.dtype('a24'))
            elem_lst = mesh_obj.ELEMS[e_type]
            nod_array = np.zeros((len(elem_lst),self.__translator[e_type]['nn']),dtype=np.int32)
            num_array  = np.zeros(len(elem_lst),dtype=np.int32)
            fam_array  = np.zeros(len(elem_lst),dtype=np.int32)
            for i,e in enumerate(elem_lst):
                elem = mesh_obj.CONNEC[e]
                nod_array[i,:] = np.array(elem[3:]) + 1
                num_array[i] = elem[0]+1
                fam_array[i] = group_dict[elem[2]]
                

            d1 = grp_0_0_0_MAI_E.create_dataset("NOD",data=nod_array.T.ravel())
            d1.attrs.create('CGT', data=1, dtype=np.int32)
            d1.attrs.create('NBR', num_array.shape[0], dtype=np.int32)
            d2 = grp_0_0_0_MAI_E.create_dataset("NUM",data=num_array)
            d2.attrs.create('CGT', data=1, dtype=np.int32)
            d2.attrs.create('NBR', num_array.shape[0], dtype=np.int32)
            d3 = grp_0_0_0_MAI_E.create_dataset("FAM",data=fam_array)
            d3.attrs.create('CGT', data=1, dtype=np.int32)
            d3.attrs.create('NBR', num_array.shape[0], dtype=np.int32)

        grp_1_0 = self.__med_root['/FAS'].create_group(mesh_obj.NAME)
        grp_1_0_ELEME = grp_1_0.create_group('ELEME')
        for key,value in group_dict.items():
            grp_1_0_ELEME_KEY = grp_1_0_ELEME.create_group("FAM_{}_{}".format(value,key))
            grp_1_0_ELEME_KEY.attrs.create('NUM', data=value, dtype=np.int32)
            grp_1_0_ELEME_KEY_GRO = grp_1_0_ELEME_KEY.create_group("GRO")
            grp_1_0_ELEME_KEY_GRO.attrs.create('NBR', data=1, dtype=np.int32)
            dset = grp_1_0_ELEME_KEY_GRO.create_dataset("NOM", (1,), dtype=('i1',(80,)))
            dset[0] = bytearray(key.ljust(80), 'utf-8')
        grp_1_0_KEY = grp_1_0.create_group("FAMILLE_ZERO")
        grp_1_0_KEY.attrs.create('NUM', data=0)

    def __group_rename(self, mesh_obj):
        grp_list = mesh_obj.GROUPS
        grp_dict = {}
        for i, grp in enumerate(grp_list):
            grp_dict[grp] = -(i+1)
        return grp_dict

    def __group_adapt(self, group):
        for i in range(80-len(group)):
            group += ' '
        return bytearray(group, 'utf-8')

    def write_field_at_time(self, field, time=0., ite=0):
        if field.SUPPORT == "NODES":
            self._write_field_on_nodes_at_time(field.MESH, field.NAME, field[:], field.COMPONENTS, (time, ite))
        elif field.SUPPORT == "ELEMS":
            self._write_field_on_elems_at_time(field.MESH, field.NAME, field[:], field.COMPONENTS, field.MESH.ELEMS , (time, ite))
        elif field.SUPPORT == "GAUSS":
            self._write_field_on_gauss_at_time(field.MESH, field.NAME, field[:], field.COMPONENTS, (time, ite))

    def _write_field_on_nodes_at_time(self, mesh, field_id, field, COMPO, time): 
        grp = self.__field_structure(mesh, field_id, COMPO, time)
        grp_noe = grp.create_group("NOE")
        grp_noe.attrs.create('GAU', data=b'')
        grp_noe.attrs.create('PFL', data=b'MED_NO_PROFILE_INTERNAL', dtype=np.dtype('a24'))
        ## level 4
        grp_4 = grp_noe.create_group('MED_NO_PROFILE_INTERNAL')
        grp_4.attrs.create('GAU', data=b'')
        grp_4.attrs.create('NBR', data=field.shape[0], dtype=np.int32)
        grp_4.attrs.create('NGA', data=1, dtype=np.int32)
        data2store = field.T.ravel()
        data_value = grp_4.create_dataset("CO", data=data2store)
        
    def _write_field_on_elems_at_time(self, mesh, field_id, field, COMPO, types_dict, time):
        grp = self.__field_structure(mesh, field_id, COMPO, time)
        for e_type, e_list in types_dict.items():
            grp_mai = grp.create_group("MAI."+self.__translator[e_type]['id'])
            grp_mai.attrs.create('GAU', data=b'')
            grp_mai.attrs.create('PFL', data=b'MED_NO_PROFILE_INTERNAL', dtype=np.dtype('a24'))
            ## level 4
            grp_4 = grp_mai.create_group('MED_NO_PROFILE_INTERNAL')
            grp_4.attrs.create('GAU', data=b'')
            grp_4.attrs.create('NBR', data=len(e_list), dtype=np.int32)
            grp_4.attrs.create('NGA', data=1, dtype=np.int32)
            data2store = field[e_list,:].T.ravel()
            data_value = grp_4.create_dataset("CO", data=data2store)
        
    def _write_field_on_gauss_at_time(self, mesh, field_id, field, COMPO, types_dict, time):
        grp = self.__field_structure(mesh, field_id, COMPO, time)
        for e_type, e_list in types_dict.items():
            gauss_e = self.med_root['/GAUSS'].create_group(VTK2MED[e_type]['id']+'__PG')
            gauss_e.attrs.create('DIM', data=3, dtype=np.int32)
            gauss_e.attrs.create('GEO', data=VTK2MED[e_type]['id'], dtype=np.int32)
            gauss_e.attrs.create('INM', data=b'')
            #gauss_e.attrs.create('NBR', data=ELEM_DB[type]['N_PG'])
            
            grp_mai = grp.create_group("MAI."+VTK2MED[e_type]['id'])
            grp_mai.attrs.create('GAU', data=b'')
            grp_mai.attrs.create('PFL', data=b'MED_NO_PROFILE_INTERNAL', dtype=np.dtype('a24'))
            ## level 4
            grp_4 = grp_mai.create_group('MED_NO_PROFILE_INTERNAL')
            grp_4.attrs.create('GAU', data=b'')
            grp_4.attrs.create('NBR', data=len(e_list), dtype=np.int32)
            grp_4.attrs.create('NGA', data=1, dtype=np.int32)
            data2store = field[e_list,:].T.ravel()
            data_value = grp_4.create_dataset("CO", data=data2store)
    
    def __field_structure(self, mesh, field_id, COMPO, time):
        """
        Method which create MED file format background for fields writing
        """
        if field_id not in self.__med_root['/CHA'].keys():
            f_group = self.__med_root['/CHA/'].create_group(field_id) 
            f_group.attrs.create('MAI', data=mesh.NAME,dtype=np.dtype('a15'))
            f_group.attrs.create('NCO', data=len(COMPO), dtype=np.int32)
            components = ''.join([comp.ljust(16) for comp in COMPO])

            f_group.attrs.create('NOM', data=components,dtype=np.dtype('a%i'%(17*len(components))))
            f_group.attrs.create('TYP', data=6, dtype=np.int32)
            f_group.attrs.create('UNI', data='', dtype=np.dtype('a17'))
            f_group.attrs.create('UNT', data='', dtype=np.dtype('a1'))
        else:
            f_group = self.__med_root['/CHA/'+field_id]
        grp_debile = f_group.create_group("%.20d%.20d"%(time[0], time[0]))
        grp_debile.attrs.create('NDT', data=time[0], dtype=np.int32)
        grp_debile.attrs.create('NOR', data=time[0], dtype=np.int32)
        grp_debile.attrs.create('PDT', data=time[1], dtype=np.float64)
        grp_debile.attrs.create('RDT', data=-1, dtype=np.int32)
        grp_debile.attrs.create('ROR', data=-1, dtype=np.int32)
        return grp_debile








