import imageio
import numpy as np

from main import get_cube_vertices, settings, write_vertex_to_buffer

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
