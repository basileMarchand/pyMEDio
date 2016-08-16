#### 
## Example 2 : load mesh define from med file
##             create analytic scalar nodal field
##             and write all in a new MED file 
##
## @author : Basile Marchand
##
###

from pyMEDio import MEDReader, MEDWriter, Field
import numpy as np

### -> 1 : Load mesh
med = MEDReader("mesh_example.med", output_format="MED")


meshes_id = med.get_meshes_names()
mesh = med.read_mesh(meshes_id[0])

med.end()

print(mesh)

### -> 2 :  Define analytic field

U = Field("fake", ["U1", "U2"], "NODES", mesh)

for i,(x,y,z) in enumerate(mesh.COOR):
    U[i,0] = np.sqrt(x**2+y**2+z**2)
    U[i,1] = - np.sqrt(x**2+y**2+z**2)

### -> 3 : Write mesh and field in a new MED file
writer = MEDWriter("output.med", input_format="MED")
writer.write_mesh(mesh)
writer.write_field_at_time(U, time=1.6 , ite=1)
writer.end()


####-> 4 : Read the previous created MED file and extract field

reader = MEDReader("output.med", output_format="MED")

mesh_2 = reader.read_mesh()

V = reader.read_field_at_time("fake", time=1, ite=1)


reader.end()





































