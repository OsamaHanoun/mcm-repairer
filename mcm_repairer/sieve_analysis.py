from mcm_repairer.file_io import load_stl

# Define the sieve sizes
# size_list = [0, 0.063, 0.125, 0.25, 0.5, 1, 2, 4, 8, 16, 31.5, 63]
size_list = [2, 4, 8, 16, 31.5]


def calculate_total_volume(mesh_list):
    return sum(mesh.volume for mesh in mesh_list)


def find_second_largest(mesh):
    obb_extents = mesh.bounding_box_oriented.primitive.extents
    obb_dimensions = obb_extents * 2
    return sorted(obb_dimensions)[1]


def calculate_percent_retained(mesh_list):
    retained_array = [0] * len(size_list)

    for mesh in mesh_list:
        aggregate_size = find_second_largest(mesh)
        volume = mesh.volume
        size_index = next(
            (i for i, size in enumerate(size_list) if aggregate_size < size), -1
        )

        if size_index != -1:
            retained_array[size_index - 1] += volume
        else:
            retained_array[size_index] += volume

    return retained_array


def calculate_passing_percentage(retained_array, total_volume):
    percentage = 0
    percent_finer = [0] * len(retained_array)

    for index in range(len(retained_array)):
        percentage += retained_array[index] / total_volume * 100
        percent_finer[index] = percentage

    return percent_finer


def calculate_curve(file_path):
    mesh_list = load_stl(file_path)
    total_volume = calculate_total_volume(mesh_list)
    retained_list = calculate_percent_retained(mesh_list)
    passing_percentage_array = calculate_passing_percentage(retained_list, total_volume)
    data = []

    for index in range(len(size_list)):
        point = {"x": size_list[index], "y": passing_percentage_array[index]}
        data.append(point)

    print(data)
