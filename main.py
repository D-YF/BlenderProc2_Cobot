import blenderproc as bproc
import argparse
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('bin_object', default="BlenderProc/examples/advanced/physics_convex_decomposition/bin.obj",help="Path to the object file containing the bin, should be examples/advanced/physics_convex_decomposition/bin.obj.")
parser.add_argument('cobotCAD_path', default="./CAD_model/models/insert_mold.obj", help="Path to the downloaded shape net core v2 dataset, get it [here](http://www.shapenet.org/)")
parser.add_argument('output_dir', nargs='?', default="./output", help="Path to where the final files will be saved ")
parser.add_argument('vhacd_path', nargs='?', default="blenderproc_resources/vhacd", help="The directory in which vhacd should be installed or is already installed.")
args = parser.parse_args()

bproc.init()

# Load a bin object that gonna catch the usb objects
bin_obj = bproc.loader.load_obj(args.bin_object)[0]

insert_mold = bproc.loader.load_obj(args.cobotCAD_path)
insert_mold[0].set_scale([10, 10, 10])
# Define a function that samples the pose of a given usb object
def sample_pose(obj: bproc.types.MeshObject):
    # Sample the location above the bin
    # obj.set_location(np.random.uniform([-0.5, -0.5, 1], [0.5, 0.5, 2.5]))
    obj.set_location(np.array([0, 0, 1]))
    obj.set_rotation_euler(bproc.sampler.uniformSO3())

# Sample the poses of all usb objects, while making sure that no objects collide with each other.
bproc.object.sample_poses(
    insert_mold,
    sample_pose_func=sample_pose
)

# Define a sun light
light = bproc.types.Light()
light.set_type("SUN")
light.set_location([0, 0, 0])
light.set_rotation_euler([-0.063, 0.6177, -0.1985])
light.set_color([1, 1, 1])
light.set_energy(1)

# Set the camera pose to be in front of the bin
bproc.camera.add_camera_pose(bproc.math.build_transformation_mat([0, -2.13, 3.22], [0.64, 0, 0]))

# # Make the bin object passively participate in the physics simulation
# bin_obj.enable_rigidbody(active=False, collision_shape="COMPOUND")
# # Let its collision shape be a convex decomposition of its original mesh
# # This will make the simulation more stable, while still having accurate collision detection
# bin_obj.build_convex_decomposition_collision_shape(args.vhacd_path)

# # Make the bin object actively participate in the physics simulation (they should fall into the bin)
# insert_mold.enable_rigidbody(active=True, collision_shape="COMPOUND")
# # Also use convex decomposition as collision shapes
# insert_mold.build_convex_decomposition_collision_shape(args.vhacd_path)

# # Run the physics simulation for at most 20 seconds
# bproc.object.simulate_physics_and_fix_final_poses(
#     min_simulation_time=4,
#     max_simulation_time=20,
#     check_object_interval=1
# )

# render the whole pipeline
data = bproc.renderer.render()

# write the data to a .hdf5 container
bproc.writer.write_hdf5(args.output_dir, data)
