from os.path import split, splitext, join, exists


def safe_access(matrix, i, j, default=False):
    try:
        return matrix[i][j]
    except Exception:
        return default


def safe_dict_setter(matrix, i, j, value):
    if i in matrix and len(matrix[i].keys()):
        matrix[i][j] = value
    elif i in matrix:
        matrix[i][j] = value
    else:
        matrix[i] = {j: value}


def add_prefix_if_exists(file_path, prefix="mcm_result_"):
    # Split the directory, base name, and extension
    dir_name, base_name = split(file_path)
    file_name, ext = splitext(base_name)

    # Initialize a counter for the prefix number
    counter = 1
    new_file_path = join(dir_name, prefix + file_name + ext)

    # Loop until a unique file name is found
    while exists(new_file_path):
        # Create a new file name with the prefix and counter
        new_file_name = f"{prefix}{file_name}_{counter}{ext}"
        new_file_path = join(dir_name, new_file_name)
        counter += 1

    return new_file_path
