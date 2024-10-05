import numpy as np
from dataclasses import dataclass


@dataclass
class settings:
    screen_x = 1920
    screen_y = 1080
    eye_distance = 2
    distance_proj_origin = 2
    size_at_unit_1 = 16


@dataclass
class Vertex:
    xyz: np.ndarray | list[float]
    distance: int = 0

    @property
    def x(self) -> float:
        return self.xyz[0]

    @property
    def y(self) -> float:
        return self.xyz[1]

    @property
    def z(self) -> float:
        return self.xyz[2]

    def update_distance(self) -> None:
        self.distance = np.sqrt(
            self.x * self.x
            + self.y * self.y
            + (settings.eye_distance + settings.distance_proj_origin + self.z)
            * (settings.eye_distance + settings.distance_proj_origin + self.z)
        )


def smooth_step(x: float, edge0: float, edge1: float) -> float:
    """
    Perform smooth interpolation between 0 and 1.
    This function creates a smooth transition using a cubic function.
    """
    x = np.clip((x - edge0) / (edge1 - edge0), 0, 1)
    return x * x * (3 - 2 * x)


def lerp(
    size: float,
    min_val: float = 0,
    max_val: float = 10,
    output_min: float = 255,
    output_max: float = 0,
) -> float:
    """
    Interpolate color based on size, using smooth step function for gradual transition.
    """
    t = smooth_step(size, min_val, max_val)
    return output_min + t * (output_max - output_min)


def rasterize(x: int, y: int, color: float, mut_data: np.ndarray) -> None:
    """Check out of bounds and simply write to buffer"""
    if (x < 0 or x >= settings.screen_x) or (y < 0 or y >= settings.screen_y):
        return
    mut_data[-y, x] = color


def write_to_screen_buffer(x: int, y: int, distance: int, data: np.ndarray) -> None:
    size = int(settings.size_at_unit_1 / max(distance, 1))

    # Adjust color based on distance, assuming distance is non-zero
    color = lerp(distance)

    for dy in range(-size, +size):
        for dx in range(-size, +size):
            r = np.sqrt(dy * dy + dx * dx)
            if r >= size:
                continue

            rasterize(x + dx, y + dy, color * 0.5, mut_data=data)


def write_vertex_to_buffer(vert: Vertex, data: np.ndarray, log: bool = False) -> None:
    #                                           (x/y)-axis
    #                                             ^
    #                    screen projection  ___---|
    #                          |      ___---      |
    #                          |___---            |
    #                    ___---|                  |
    #              ___---      | origin'          |  origin
    #         __---            |/                 | /
    # camera ----------------->|----------------->|-----------> z-axis
    #           eye distance    distance to origin
    #
    # To project from world space to screen space we can scale down
    # the Vertex coordinates, since two triangles formed camera x-axis
    # and camera - screen projection are congruent.

    projection_ratio = settings.eye_distance / (
        settings.eye_distance + settings.distance_proj_origin + vert.z
    )
    proj_y = vert.y * projection_ratio
    proj_x = vert.x * projection_ratio

    # Calculate aspect ratio correction factor
    aspect_ratio = settings.screen_y / settings.screen_x

    # Adjust x projection to account for aspect ratio
    proj_x *= aspect_ratio

    # Map normalized coordinates to screen space
    screen_proj_y = int((proj_y + 1) * settings.screen_y / 2.0)
    screen_proj_x = int((proj_x + 1) * settings.screen_x / 2.0)
    vert.update_distance()

    if log:
        print("Projection ratio: ", projection_ratio)
        print("                    x   y   z")
        print("World position:    ", vert.x, vert.y, vert.z)
        print("Screen projection: ", proj_x, proj_y)
        print("Screen pixels:     ", screen_proj_x, screen_proj_y)
        print("Distance: ", vert.distance)

    write_to_screen_buffer(
        screen_proj_x, screen_proj_y, distance=vert.distance, data=data
    )
