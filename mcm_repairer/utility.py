from os.path import basename


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


def get_file_name(file_path):
    return basename(file_path)
