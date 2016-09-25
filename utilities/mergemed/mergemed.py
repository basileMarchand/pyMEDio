##### 
#####  mergemed utility
#####  
#####  @author : Basile Marchand
#####

import re
import os
import argparse

from pyMEDio import MEDReader, MEDWriter, verbose, quiet

def open_all(output_name, input_name):
    medoutput = MEDWriter(output_name)
    medinput  = [MEDReader(f) for f in input_name] 
    return medoutput, medinput

def close_all(medoutput, medinput):
    medoutput.end()
    for med in medinput:
        med.end()


def copy_mesh(medoutput, medinput):
    """ 
    Assume than all med input files 
    contains the same mesh 
    """
    msh = medinput[0].read_mesh()
    medoutput.write_mesh(msh)
    
def list_fields_input(medinput):
    fields_names = medinput[0].get_fields_names()
    for med in medinput[1:]:
        tmp = med.get_fields_names()
        if tmp != fields_names:
            print(" All input med files doesn't contains the same fields,\n use the -f option to specify which fields to merge")
            sys.exit(2)
    return fields_names

def merge_field(field_name, output_med, input_med):
    step = 0
    for med in input_med:
        fields = med.read_field(field_name)
        for field in fields:
            output_med.write_field_at_time(field, step, step)
            step += 1
    

if __name__ == "__main__":
    quiet()
    ## input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--field", nargs="+", default="all", help="Name of field to merge in the result med file")
    parser.add_argument("medoutput",  help="Name of the ouput med file (overwritte file if already exists)")
    parser.add_argument("medinput", nargs='+', help="List of medfiles to merge, can be given as a regular expression")
    args = parser.parse_args()

    ## OPEN ALL MED FILES
    medoutput, medinput = open_all(args.medoutput, args.medinput)

    ## Copy mesh
    copy_mesh(medoutput, medinput)

    ## MERGE FIELD    
    if args.field == "all":
        ## merge all field define in med files
        field_list = list_fields_input(medinput)
    else:
        field_list = args.field_name

    for field_name in field_list:
        print("** Merge field : " + field_name)
        merge_field(field_name, medoutput, medinput)
     

    close_all(medoutput, medinput)

            
