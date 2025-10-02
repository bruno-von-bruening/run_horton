from . import *

from qcp_global_utils.parser.parser import controller_model

class output_files(controller_model):
    moments_file: str='moment.mom'
    solution_file: str='solution.json'
    kld_history_file: str='kld_history.json'
    __example_values__={}
    # def check existance

# from pydantic._internal._model_construction import ModelMetaclass
# class controller_meta(ModelMetaclass):
#     def __init__(self, *args,**kwargs):
#         super().__init__(*args,**kwargs)

class horton_wpart_controller(controller_model):
    method: str
    basis: str|None =None
    wfn_file: file
    ang_grid_dens: str='insane'
    rad_grid_dens: int=200
    print_basis: bool=False
    output: output_files = output_files()
    
    # LinearISAWPart in https://github.com/LISA-partitioning-method/horton-part
    solver:str='sc'
    #__example_values__={}
    def __init__(self, *args,**kwargs):
        super().__init__(*args,**kwargs)

        
