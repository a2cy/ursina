def normalize_v3(arr):
    ''' Normalize a numpy array of 3 component vectors shape=(n,3) '''
    import numpy

    lens = numpy.sqrt( arr[:,0]**2 + arr[:,1]**2 + arr[:,2]**2 )
    arr[:,0] /= lens
    arr[:,1] /= lens
    arr[:,2] /= lens
    return arr


def generate_normals(vertices, triangles=None, smooth=True):
    import numpy

    if not vertices:
        raise ValueError("can't generate normals for a mesh with 0 vertices")

    if not triangles:
        new_tris = [(i, i+1, i+2) for i in range(0, len(vertices), 3)]

    elif not isinstance(triangles[0], int):
        raise TypeError(f'triangles must be ints, not {type(triangles[0])} ({triangles[0]})')

    else:
        new_tris = [(triangles[i], triangles[i+1], triangles[i+2]) for i in range(0, len(triangles), 3)]


    vertices = numpy.array(vertices)
    triangles = numpy.array(new_tris)

    normals = numpy.zeros(vertices.shape, dtype=vertices.dtype)
    #Create an indexed view into the vertex array using the array of three indices for triangles
    tris = vertices[triangles]
    #Calculate the normal for all the triangles, by taking the cross product of the vectors v1-v0, and v2-v0 in each triangle
    n = numpy.cross(tris[::,1] - tris[::,0] ,tris[::,2] - tris[::,0])
    # n is now an array of normals per triangle. The length of each normal is dependent the vertices,
    # we need to normalize these, so that our next step weights each normal equally.
    normalize_v3(n)

    # inverse it, dunno why
    n = [-e for e in n]

    # now we have a normalized array of normals, one per triangle, i.e., per triangle normals.
    # But instead of one per triangle (i.e., flat shading), we add to each vertex in that triangle,
    # the triangles' normal. Multiple triangles would then contribute to every vertex, so we need to normalize again afterwards.
    # The cool part, we can actually add the normals through an indexed view of our (zeroed) per vertex normal array
    normals[triangles[:,0]] += n
    normals[triangles[:,1]] += n
    normals[triangles[:,2]] += n
    normalize_v3(normals)

    # smooth
    if smooth:
        vertices = vertices.tolist()
        visited = set()

        for i, v in enumerate(vertices):
            if i in visited:
                continue

            overlapping_verts_indices = [j for j, w in enumerate(vertices) if w == v and j not in visited]
            visited.update(overlapping_verts_indices)

            if overlapping_verts_indices:
                average_normal = sum(normals[e] for e in overlapping_verts_indices) / 3
                for index in overlapping_verts_indices:
                    normals[index] = average_normal


    return normals

if __name__ == '__main__':
    vertices = (
        (-0.0, -0.5, 0.0), (0.1, -0.48, -0.073), (-0.038, -0.48, -0.11),
        (0.361804, -0.22, -0.26), (0.3, -0.32, -0.22), (0.40, -0.25, -0.14),
        (-0.0, -0.5, 0.0), (-0.038, -0.48, -0.11), (-0.03, -0.48, -0.11)
    )
    from time import perf_counter
    t = perf_counter()
    norms = generate_normals(vertices, smooth=True)
    print('------', perf_counter() - t)
    # print(norms)
    # from ursina import *
    # app = Ursina()
    # m = Mesh(vertices=vertices)
    # m.generate_normals()
    # e = Entity(model=m)
    # # print(e.normals)
    # if e.normals:
    #     verts = list()
    #     for i in range(len(e.vertices)):
    #         verts.append(e.vertices[i])
    #         verts.append(Vec3(e.vertices[i][0], e.vertices[i][1], e.vertices[i][2])
    #             + Vec3(e.normals[i][0], e.normals[i][1], e.normals[i][2])*2)
    #
    #     lines=Entity(model=Mesh(verts, mode='line'))
    # # e.shader = 'shader_normals'
    # EditorCamera()
    # app.run()
