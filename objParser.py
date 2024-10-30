import os


class Vertex:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return 'Vertex({:.6f}, {:.6f}, {:.6f})'.format(self.x, self.y, self.z)

    def __str__(self):
        return self.__repr__()

    def get_distance(self, other):
        diff = self - other
        return (diff.x ** 2 + diff.y ** 2 + diff.z ** 2) ** 0.5

    def __add__(self, other):
        return Vertex(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vertex(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other):
        return Vertex(self.x * other, self.y * other, self.z * other)

    def __truediv__(self, other):
        return Vertex(self.x / other, self.y / other, self.z / other)

    def __rtruediv__(self, other):
        return Vertex(other / self.x, other / self.y, other / self.z)

    def __hash__(self):
        return hash((self.x, self.y, self.z))


class VertexNormal(Vertex):
    def __repr__(self):
        return f'VertexNormal({self.x}, {self.y}, {self.z})'

    def __str__(self):
        return self.__repr__()


class VertexTextureCoordinate:
    def __init__(self, u, v):
        self.u = u
        self.v = v

    def __repr__(self):
        return f'TextureCoordinate({self.u}, {self.v})'

    def __str__(self):
        return self.__repr__()

    def __hash__(self):
        return hash((self.u, self.v))


class Face:
    def __init__(self, vertices, texture_coords, vertex_normals):
        self.vertices = vertices
        self.texture_coords = texture_coords
        self.vertex_normals = vertex_normals

    def __str__(self):
        return self.__repr__()

    def __hash__(self):
        return hash((self.vertices, self.texture_coords, self.vertex_normals))


class Object:
    def __init__(self, name, file_name, vertices, texture_coordinates, vertex_normals, faces, smooth_shading=False):
        self.name = name
        self.file_name = file_name
        self.vertices = vertices
        self.texture_coordinates = texture_coordinates
        self.vertex_normals = vertex_normals
        self.faces = faces
        self.smooth_shading = smooth_shading

    @staticmethod
    def from_obj_str(obj_str, file_name):
        lines = obj_str.split('\n')
        name = ''
        vertices = []
        texture_coordinates = []
        vertex_normals = []
        faces = []
        smooth_shading = False
        for line in lines:
            if line.startswith('#'):
                continue
            if line.startswith('o '):
                name = line.split()[1]
                vertices = []
                texture_coordinates = []
                vertex_normals = []
                faces = []
                continue
            if line.startswith('v '):
                vertices.append(Vertex(*map(float, line.split()[1:])))
                continue
            if line.startswith('vt '):
                texture_coordinates.append(VertexTextureCoordinate(*map(float, line.split()[1:])))
                continue
            if line.startswith('vn '):
                vertex_normals.append(VertexNormal(*map(float, line.split()[1:])))
                continue
            if line.startswith('s '):
                smooth_shading = True if line.split()[1] == '1' else False
                continue
            if line.startswith('f '):
                face_vertices = []
                face_texture_coords = []
                face_vertex_normals = []
                for vertex_str in line.split()[1:]:
                    vertex_str = vertex_str.split('/')
                    face_vertices.append(vertices[int(vertex_str[0]) - 1])
                    face_texture_coords.append(texture_coordinates[int(vertex_str[1]) - 1])
                    face_vertex_normals.append(vertex_normals[int(vertex_str[2]) - 1])
                faces.append(Face(face_vertices, face_texture_coords, face_vertex_normals))
        return Object(name, file_name, vertices, texture_coordinates, vertex_normals, faces, smooth_shading)

    def _faces_to_str(self):
        obj_str = ''
        for face in self.faces:
            obj_str += f'f'
            for v, vtc, vn in zip(face.vertices, face.texture_coords, face.vertex_normals):
                v_index = self.vertices.index(v) + 1
                vt_index = self.texture_coordinates.index(vtc) + 1
                vn_index = self.vertex_normals.index(vn) + 1
                obj_str += f' {v_index}/{vt_index}/{vn_index}'
            obj_str += '\n'
        return obj_str

    def to_obj_str(self):
        obj_str = ''
        obj_str += f'o {self.name}\n'
        for vertex in self.vertices:
            # write only 6 decimal places
            v_x_y_z_6digit = map(lambda x: "{:.6f}".format(x), [vertex.x, vertex.y, vertex.z])
            obj_str += f'v {" ".join(v_x_y_z_6digit)}\n'
        for texture_coordinate in self.texture_coordinates:
            # write only 6 decimal places
            vt_u_v_6digit = map(lambda x: "{:.6f}".format(x), [texture_coordinate.u, texture_coordinate.v])
            obj_str += f'vt {" ".join(vt_u_v_6digit)}\n'
        for vertex_normal in self.vertex_normals:
            # write only 6 decimal places
            vn_x_y_z_6digit = map(lambda x: "{:.6f}".format(x), [vertex_normal.x, vertex_normal.y, vertex_normal.z])
            obj_str += f'vn {" ".join(vn_x_y_z_6digit)}\n'
        if self.smooth_shading:
            obj_str += 's 1\n'
        obj_str += self._faces_to_str()
        return obj_str

    def __copy__(self):
        return Object(self.name, self.file_name, self.vertices, self.texture_coordinates, self.vertex_normals,
                      self.faces, self.smooth_shading)

    def __repr__(self):
        return f'{self.file_name}: Object({self.name})'

    def __str__(self):
        return self.__repr__()


def import_obj(filepath) -> Object:
    with open(filepath, 'r') as f:
        lines = f.readlines()
    return Object.from_obj_str(''.join(lines), os.path.basename(filepath))


def export_obj(filepath, obj_object: Object):
    with open(filepath, 'w') as f:
        f.write(obj_object.to_obj_str())


if __name__ == '__main__':
    obj_object = import_obj('117832.obj')
    obj_object.texture_coordinates = sorted(obj_object.texture_coordinates, key=lambda x: [x.u, x.v])
    export_obj('117832_out.obj', obj_object)
