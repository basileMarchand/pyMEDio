from pyMEDio import MEDReader



med = MEDReader("mesh_example.med", output_format="MED")

meshes_id = med.get_meshes_names()
mesh = med.read_mesh(meshes_id[0])











