import argparse
from pyMEDio import MEDReader



parser = argparse.ArgumentParser(description='medinfo \n Utility to simply visualize objects defined in a given MED file')

parser.add_argument('medfile', type=str, help="the med file to investigate")
parser.add_argument('-m', '--mesh', action="store_true")
parser.add_argument('-f', '--field', action="store_true")
args = parser.parse_args()

med = MEDReader(args.medfile)

if args.mesh:
    ## Display informations about meshes
    meshes = med.get_meshes_names()    
    print("Mesh stored in {}".format(args.medfile))
    for mesh in meshes:
        print(" -> {}".format(mesh))
        msh_info = med.get_mesh_info(mesh)
        print("         Number of nodes    : {}".format(msh_info['NN']))
        print("         Number of elements : {}".format(msh_info['NE']))
        for tup in msh_info['ELEMS']:
            print("            * {}    :   {}".format(*tup))
        print("         List of groups     : {}".format(", ".join(msh_info['GROUPS'])))

if args.field:
    #display informations about fields
    fields = med.get_fields_names()
    print("Fields stored in {}".format(args.medfile))
    for field in fields:
        print("  -> Field   : {}".format(field))
        field_info = med.get_field_info(field)
        print("         support       : {} on mesh {}".format(*field_info["support"]))
        print("         components    : {}".format(", ".join(field_info["components"])))
        print("         steps         : {}".format("; ".join([str(x) for x in field_info["steps"]])))
        
med.end()
