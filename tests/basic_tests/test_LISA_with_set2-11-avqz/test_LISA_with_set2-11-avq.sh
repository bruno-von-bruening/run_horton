#!/bin/bash

activate_conda_env() {
	conda_env=${1}
	if [ -z ${conda_env} ]; then
		echo called activate_conda_env without providing environment name
	fi
	base=${CONDA_EXE%/bin/conda}
	source ${base}/etc/profile.d/conda.sh
	conda activate ${conda_env}
}

conda_env=run_horton
activate_conda_env ${conda_env}
run_horton_wpart.py --method LISA --basis set2-11-avqz --wfn ../../example_files/pbe0_aug-cc-pVDZ_h2.fchk --exc
