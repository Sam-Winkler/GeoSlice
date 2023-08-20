import sys, os.path, time

# update this path with wherever trimesh is
sys.path.append("C:/Users/Sam/.nuke/ToolSets")
import trimesh

startTime = time.time()
# user_path = os.environ.get("USERPROFILE")
geo_file = nuke.thisNode().knob("geo_file").value()
mesh = trimesh.load_mesh(geo_file)
slice_name = nuke.thisNode().knob("slice_name").value()


right = (
    nuke.thisNode().knob("origin").value(0)
    + (
        nuke.thisNode().knob("scale_x").value()
        * nuke.thisNode().knob("scale_u").value()
    )
    / 2
)
left = (
    nuke.thisNode().knob("origin").value(0)
    - (
        nuke.thisNode().knob("scale_x").value()
        * nuke.thisNode().knob("scale_u").value()
    )
    / 2
)

top = (
    nuke.thisNode().knob("origin").value(0)
    + (
        nuke.thisNode().knob("scale_y").value()
        * nuke.thisNode().knob("scale_u").value()
    )
    / 2
)
bottom = (
    nuke.thisNode().knob("origin").value(0)
    - (
        nuke.thisNode().knob("scale_y").value()
        * nuke.thisNode().knob("scale_u").value()
    )
    / 2
)

front = (
    nuke.thisNode().knob("origin").value(0)
    + (
        nuke.thisNode().knob("scale_z").value()
        * nuke.thisNode().knob("scale_u").value()
    )
    / 2
)
back = (
    nuke.thisNode().knob("origin").value(0)
    - (
        nuke.thisNode().knob("scale_z").value()
        * nuke.thisNode().knob("scale_u").value()
    )
    / 2
)


if os.path.exists(geo_file) == True:
    # create slice file name and path based on incoming geo file
    directory = os.path.dirname(geo_file)
    path_name, extension = os.path.splitext(geo_file)
    geo_file_name = path_name.split("\\")
    geo_file_name = geo_file_name[-1]
    slice_file = os.path.join(
        directory, geo_file_name + "_" + slice_name + "_v01" + extension
    )

    # version up if slice file already exists
    while os.path.exists(slice_file) == True:
        slice_file = str(slice_file)
        version = slice_file[-5:-3]
        new_version = int(float(version)) + 1
        new_version = str(new_version).zfill(2)
        slice_file = os.path.join(
            directory,
            geo_file_name + "_" + slice_name + "_v" + new_version + extension,
        )

    # process geo via trimesh
    # mesh slicing operations:
    mesh = trimesh.intersections.slice_mesh_plane(
        mesh, [-1, 0, 0], [right, 0, 0], face_index=None, cap=False, cached_dots=None
    )
    mesh = trimesh.intersections.slice_mesh_plane(
        mesh, [1, 0, 0], [left, 0, 0], face_index=None, cap=False, cached_dots=None
    )
    mesh = trimesh.intersections.slice_mesh_plane(
        mesh, [0, -1, 0], [0, top, 0], face_index=None, cap=False, cached_dots=None
    )
    mesh = trimesh.intersections.slice_mesh_plane(
        mesh, [0, 1, 0], [0, bottom, 0], face_index=None, cap=False, cached_dots=None
    )
    mesh = trimesh.intersections.slice_mesh_plane(
        mesh, [0, 0, -1], [0, 0, front], face_index=None, cap=False, cached_dots=None
    )
    mesh = trimesh.intersections.slice_mesh_plane(
        mesh, [0, 0, 1], [0, 0, back], face_index=None, cap=False, cached_dots=None
    )

    slice_obj = trimesh.exchange.obj.export_obj(
        mesh,
        include_normals=True,
        include_color=False,
        include_texture=False,
        return_texture=False,
        write_texture=False,
        resolver=None,
        digits=7,
    )

    with open(slice_file, "w") as f:
        f.write(slice_obj)
        nuke.nodes.ReadGeo(file=slice_file)

    executionTime = time.time() - startTime
    print("Slice Complete! \n Execution time: " + str(executionTime) + " seconds.")
