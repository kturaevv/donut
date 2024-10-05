import imageio
import numpy as np

from main import settings, write_vertex_to_buffer, Vertex


def get_cube_vertices():
    CUBE_SIZE = 20
    vertices = []
    for z in np.linspace(-1, 1, CUBE_SIZE):
        for y in np.linspace(-1, 1, CUBE_SIZE):
            for x in np.linspace(-1, 1, CUBE_SIZE):
                v = Vertex([x, y, z])
                # empty out cube
                if abs(x) == 1 or abs(y) == 1 or abs(z) == 1:
                    vertices.append(v)
    return vertices


if __name__ == "__main__":
    gif_writer = imageio.get_writer("rotating_cube.gif", mode="I", duration=0.1, loop=0)

    vertices = get_cube_vertices()

    theta = np.pi / 180

    rotate_around_y = np.array(
        [
            [np.cos(theta), 0, np.sin(theta)],
            [0, 1, 0],
            [-np.sin(theta), 0, np.cos(theta)],
        ]
    )

    for i in range(360):
        for vert in vertices:
            vert.xyz = rotate_around_y @ vert.xyz
            vert.update_distance()

        # render far away vertices first to overdraw with closer later
        sorted_cube_vertices = sorted(vertices, key=lambda x: -x.distance)

        buffer = np.zeros((settings.screen_y, settings.screen_x))
        for v in sorted_cube_vertices:
            write_vertex_to_buffer(v, buffer)

        gif_writer.append_data(buffer)
    gif_writer.close()
