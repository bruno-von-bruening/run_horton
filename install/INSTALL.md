The simplest way to install is to use the ```qcp_installer``` package
(https://github.com/bruno-von-bruening/qcp_installer)

After installing the corresponding conda environment to ```qcp_installer```.
```
conda activate qcp_installer
# Go to install/ directory in this package
qcp_setup_env.py installer.yaml
```
The ```installer.yaml``` file features some pip packages as dependencies which are declared through the root directory
of the respective pip directory (at the moment this is just the name of the shell environment variable). If something goes wrong during the installation it may be due to a non existent paths
in you environment.

The version requirements file will not be used in the current implementation. (finish the developmental version_checker
routine in the qcp_installer package first)
