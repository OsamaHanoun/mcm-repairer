# mcm-repairer

## run:

conda env create -f environment.yml
conda activate mcm_repairer

## if prefix already exists, run this first:

conda env remove -n mcm_repairer


tetgen -d filename.stl > tetgen_output.log 2>&1
