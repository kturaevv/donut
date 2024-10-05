import imageio
import numpy as np

from main import settings, write_vertex_to_buffer, Vertex


def get_donut_vertices():
    vertices = []
    R = 1.0
    r = 0.4
    steps = 32

    for theta in np.linspace(0, 2 * np.pi, steps * 2):
        for phi in np.linspace(0, 2 * np.pi, steps):
            x = (R + r * np.cos(phi)) * np.cos(theta)
            y = (R + r * np.cos(phi)) * np.sin(theta)
            z = r * np.sin(phi)
            vertices.append(Vertex([x, y, z]))

    return vertices


if __name__ == "__main__":
    gif_writer = imageio.get_writer(
        "rotating_donut.gif", mode="I", duration=0.1, loop=0
    )

    vertices = get_donut_vertices()

    theta = np.pi / 180

    rotate_around_x = np.array(
        [
            [1, 0, 0],
            [0, np.cos(theta), -np.sin(theta)],
            [0, np.sin(theta), np.cos(theta)],
        ]
    )

    rotate_around_y = np.array(
        [
            [np.cos(theta), 0, np.sin(theta)],
            [0, 1, 0],
            [-np.sin(theta), 0, np.cos(theta)],
        ]
    )

    rotate_around_z = np.array(
        [
            [np.cos(theta), -np.sin(theta), 0],
            [np.sin(theta), np.cos(theta), 0],
            [0, 0, 1],
        ]
    )

    rotate_around_xyz = rotate_around_x @ rotate_around_y @ rotate_around_z
    for i in range(207):
        for vert in vertices:
            vert.xyz = rotate_around_xyz @ vert.xyz
            vert.update_distance()

        # render far away vertices first to overdraw with closer later
        sorted_cube_vertices = sorted(vertices, key=lambda x: -x.distance)

        buffer = np.zeros((settings.screen_y, settings.screen_x))
        for v in sorted_cube_vertices:
            write_vertex_to_buffer(v, buffer)

        gif_writer.append_data(buffer)
    gif_writer.close()
