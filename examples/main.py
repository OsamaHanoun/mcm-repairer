import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mcm_repairer.main import write_failed_meshes
from mcm_repairer.mesh_repairer import repair
from mcm_repairer.mesh_trimmer import trim
from mcm_repairer.sieve_analysis import calculate_curve
from mcm_repairer.reduce_volume_fraction import reduce, reduce_iteratively
from mcm_repairer.cut_csg import trim_csg
from mcm_repairer.convert_stl_to_ascii import convert


def main():
    # repair
    # file_path = os.path.join(os.path.dirname(__file__), "cube70_3.stl")
    # repair(file_path, 0.5, 0.5, 4)

    # cutting CSG
    # file_path = os.path.join(os.path.dirname(__file__), "repair_result_cube30_1.stl")
    # trim_csg(file_path, 30, 2, 4, 0.5)

    ## cutting B-rep
    """
    sample_file_path = os.path.join(
        os.path.dirname(__file__), "repair_result_sample_size_100.stl"
    )
    container_file_path = os.path.join(os.path.dirname(__file__), "cylinder.stl")
    trim(sample_file_path, container_file_path, 0.5)
    """

    ## sieve analysis
    # file_path = os.path.join(os.path.dirname(__file__), "sample_BA16.stl")
    # calculate_curve(file_path)

    ## reduce volume fraction
    # file_path = os.path.join(os.path.dirname(__file__), "sample_size_50.stl")
    # reduce(file_path, 0.2)

    # reduce volume fraction iteratively
    # file_path = os.path.join(os.path.dirname(__file__), "cuboid_50_1_vf_49.stl")
    # reduce_iteratively(file_path, 0.15, 0.001, 100)

    # convert to ascii
    file_path = os.path.join(os.path.dirname(__file__), "repair_result_cube30_1.stl")
    convert(file_path)


if __name__ == "__main__":
    main()
