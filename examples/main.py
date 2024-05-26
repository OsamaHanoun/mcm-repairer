import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mcm_repairer.main import write_failed_meshes
from mcm_repairer.mesh_repairer import repair


def main():
    file_path = os.path.join(os.path.dirname(__file__), "sample_size_50.stl")
    # write_failed_meshes(file_path)
    repair(file_path, 0.4, 0.5, 2)


if __name__ == "__main__":
    main()
