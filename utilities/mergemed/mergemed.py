##### 
#####  mergemed utility
#####  
#####  @author : Basile Marchand
#####

import re
import os
import argparse

from pyMEDio import MEDReader, MEDWriter

def open_all(output_name, input_name):
    output = MEDWriter(output_name, input_format="MED")
    data  = []
    for file_name in input_name:
        tmp = MEDReader(file_name)
        data.append(tmp)
    return output, data

def close_all(output, data):
    output.end()
    for med in data:
        med.end()

def copy_mesh(output, data):
    ### Assume that all meshes are the same
    ### copy only from data[0]
    msh = data[0].read_mesh()
    output.write_mesh(msh)

def list_field_names(data):
    fields_names = data[0].get_fields_names()
    for med in data[1:]:
        tmp = med.get_fields_names()
        if tmp != fields_names:
            print("All input med files doesn't contains the same fields \n use the --field option to specify which fields to copy")
            sys.exit(2)
    return fields_names

def merge_field(field_name, output_med, input_med):
    index = 0
    for med in input_med:
        fields = med.read_field(field_name)
        for field in fields: 
            output.write_field_at_time(field, time=index, ite=index)
            index += 1

if __name__ == "__main__":    
    ## input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--field", nargs="+", default="all", help="Name of field to merge in the result med file")
    parser.add_argument("medout",  help="Name of the ouput med file (overwritte file if already exists)")
    parser.add_argument("medinput", nargs='+', help="List of medfiles to merge, can be given as a regular expression")
    args = parser.parse_args()

    ## OPEN ALL MED FILES 
    output, data = open_all(args.medout, args.medinput)
    
    ## COPY MESH
    copy_mesh(output, data)

    ## MERGE FIELD    
    if args.field == "all":
        ## merge all field define in med files
        field_list = list_field_names(data)
    else:
        field_list = args.field

    for field_name in field_list:
            print("field : " + field_name)
            merge_field(field_name, output, data)

    ## CLOSE all
    close_all(output, data)
    
    
            
