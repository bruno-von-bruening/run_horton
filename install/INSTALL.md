For install just run 
```
conda env create -f run_horton_env.yaml
```
You may also run (in case the environment already exists):
```
conda env update -f run_horton_env.yaml
```

Finally go to the top-level of this project and install  the content itself.
```
cd <top-level>
conda activate run_horton
pip install .
```
