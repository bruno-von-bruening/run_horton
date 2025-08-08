from . import *
from qcp_run_horton.parse.controller import horton_wpart_controller

from qcp_run_horton.parse.parser import read_horton_wpart_file

from qcp_run_horton.execution.util  import process_mp2_and_cc_file



from qcp_run_horton.execution.run_horton import run_horton
@val_call
def input_file_parser(inp_fi:file, printout=False):
    if inp_fi.lower().endswith('.yaml'):
        with open(inp_fi, 'r') as rd:
            content=yaml.safe_load(rd)
            dic=horton_wpart_controller(content).model_dump()
    else:
        reader=read_horton_wpart_file(inp_fi, printout=printout)
        dic=reader.value_dict
        dic.update({'out_name':reader.out_name})
        dic_keys=list(dic.keys())
        keys=[]
        for key in keys:
            key=key.upper()
            if not key in dic_keys:
                raise Exception(f"Could not find entry for {key}, available keys are {dic_keys}")
    return dic
def setup_partitioning(inp_dic):
    """ Setup calculation, generate supplementary tags and objects """
    method=inp_dic['METHOD']
    basis_type=inp_dic['BASIS']
    if method in ['LISA']:
        ### Setup
        if type(basis_type)==type(None):
            basis=None
        elif isinstance(basis_type, str):
            camcasp_options=['set2','avqz','set2-11-avqz']
            from qcp_run_horton.basis.load_basis import load_basis
            basis=load_basis(basis_tag=basis_type)
        else:
            raise Exception(f"Invalid type for basis: {type(basis_type)}\n{basis_type}")
        solver='sc'
    elif method in ['MBIS']:
        solver='MBIS'
        basis=None
    else:
        raise Exception(f"Provided method \'{method}\', but is not implemented yet")
    if type(basis)==type(None):
        basis_key='GISA'
    else:
        basis_key=basis
    print(f"Using basis of type: {basis_key}")
    return {'solver':solver, 'basis':basis, 'method':method}

from qcp_run_horton.parse.controller import horton_wpart_controller
from qcp_global_utils.environment.file_handling import temporary_file
from qcp_run_horton.execution.util import process_mp2_and_cc_file


def main(inp_fi:file|None=None, method:str|None=None, basis:str|None=None, wfn_file:file|None=None, execute=True):
    """ Takes dictionary with all information about the run 
    1. Process and check the information
    2. Run horton
    If input is empty then print an example file
    """
    # In case no input has been provided, print a dummy input file, otherwise read it

    if inp_fi is None:
        print( f"No input file, will work with dummy file options")
        kwargs={}
        if not method is None: kwargs.update(dict(method=method))
        if not basis is None: kwargs.update(dict(basis=basis))
        if not wfn_file is None: kwargs.update(dict(wfn_file=wfn_file))
        dummy_controller=horton_wpart_controller(**horton_wpart_controller.example(**kwargs))
        inp_fi=dummy_controller.write()
        print(f"Wrote input file to {inp_fi}")

    if not execute:
        return None
    controller=horton_wpart_controller(inp_fi)
    print(controller)




    def process_information(cntrl: horton_wpart_controller) -> Tuple[list,dict]:
        """ """

        @val_call
        def transfrom_fchk_file(wfn_fi:file) -> temporary_file:
            # Copy file
            try:
                process_mp2_and_cc_file(wfn_fi, test=True)
            except Exception as ex:
                raise Exception(f"Test failed for {process_mp2_and_cc_file}: {ex}")
            wfn_fi=process_mp2_and_cc_file(wfn_fi)
            return wfn_fi

        wfn_fi_tmp=temporary_file(controller.wfn_file)
        # if mp2 or cc I need to change
        controller.wfn_file=transfrom_fchk_file(wfn_fi_tmp.file)

        # setup arguments
        args=[ controller.wfn_file, cntrl.method, cntrl.basis ]
        kwargs=dict(
            solver=controller.solver,
            ang_grid_dens=cntrl.ang_grid_dens,
        )
        return args, kwargs
    def delete_tmp_files():
        for the_file in glob.glob('*'):
            if the_file.startswith('tmp.'):
                os.popen(f"rm {the_file}")
                print(f"Deleted temportary file \'{the_file}\'")
    
    controller=horton_wpart_controller(inp_fi)
    args,kwargs=process_information(controller)
    try:
        run_horton(controller,*args, **kwargs)
        delete_tmp_files()
    except Exception as ex:
        delete_tmp_files()
        raise Exception(ex)
    # Remove temporary file