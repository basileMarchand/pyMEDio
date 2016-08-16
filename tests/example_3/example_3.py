#### 
## Example 3 : load mesh define from med file
##             create analytic elem field
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

U = Field("fake", ["X1", "X2", "X3"], "ELEMS", mesh)

def barycenter(coor):
    return np.mean(coor, axis=0)/coor.shape[0]

## On Group VolExt

f = lambda X: X

for elem in mesh.GROUPS["VolExt"]:
    nodes = mesh.CONNEC[elem][3:]
    coors = mesh.COOR[nodes,:]
    X = barycenter(coors)    
    U[elem,:] = f(X)
    #U[elem,1] = 1./f(X)

## On Group VolInt

f = lambda X: X**2

for elem in mesh.GROUPS["VolInt"]:
    nodes = mesh.CONNEC[elem][3:]
    coors = mesh.COOR[nodes,:]
    X = barycenter(coors)    
    U[elem,:] = f(X)
    #U[elem,1] = -f(X)



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





































