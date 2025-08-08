import numpy as np
import os, sys , glob, re, json ; sys.path.insert(1, os.environ['SCR'])

#; sys.path.insert(1,'/home/bruno/opt/lisa_cheng_test/docs/notebooks')
#from setup import prepare_argument_dict, prepare_grid_and_dens, print_results
from horton_part import BasisFuncHelper, LinearISAWPart, MBISWPart
import pickle 

import horton_part.core.basis as horton_basis
from gbasis.evals.eval import evaluate_basis
from gbasis.wrappers import from_iodata
from grid import BeckeWeights, ExpRTransform, MolGrid, UniformInteger
from iodata import load_one
from scipy.special import gamma # for some HORTON style equation
import json 

from .util import stamp 

from qcp_run_horton.util.import_helper import * 
from qcp_run_horton.parse.controller import horton_wpart_controller

from qcp_global_utils.encoding_and_conversion.encoding import nuclear_charge_to_element_symbol, element_symbol_to_nuclear_charge, get_nshells_for_nuclear_charge

valid_methods=['mbis','lisa']

# setups
#
def prepare_grid_and_dens(filename, rad_grid_dens=200, ang_grid_dens='insane'):
    """Prepare molecular grid and density."""
    assert os.path.isfile(filename), f"Not a valid file \'{filename}\'"
    mol = load_one(filename)

    # Specify the integration grid
    rgrid_dens=rad_grid_dens
    anggrid_dens=ang_grid_dens
    rtf = ExpRTransform(5e-4, 2e1, rgrid_dens - 1)
    uniform_grid = UniformInteger(rgrid_dens)
    rgrid = rtf.transform_1d_grid(uniform_grid)
    becke = BeckeWeights()
    grid = MolGrid.from_preset(
            mol.atnums, mol.atcoords, rgrid, anggrid_dens, becke, rotate=False, store=True
    )

    # Get the spin-summed density matrix
    one_rdm = mol.one_rdms.get("post_scf", mol.one_rdms.get("scf"))
    basis, coord_types = from_iodata(mol)
    basis_grid = evaluate_basis(basis, grid.points, coord_type=coord_types)
    rho = np.einsum("ab,bp,ap->p", one_rdm, basis_grid, basis_grid, optimize=True)
    nelec = grid.integrate(rho)
    print(f"The number of electrons: {nelec}")
    print(f"Coordinates of the atoms \n {mol.atcoords}")
    print(f"Atomic numbers of the atom \n {mol.atnums}")
    return mol, grid, rho
#
def prepare_argument_dict(mol, grid, rho):
    """Prepare basic input arguments for all AIM methods."""
    kwargs = {
        "coordinates": mol.atcoords,
        "numbers": mol.atnums,
        "pseudo_numbers": mol.atnums,
        "grid": grid,
        "moldens": rho,
        "lmax": 4,
        "maxiter": 1000,
        "threshold": 1e-6,
    }
    return kwargs

# Readers
#
#

### SAVING
def save_histories(partition, output_file=None):
    """ Saves KLD values during iterations into file """
    # Default name of output file
    if type(output_file)==type(None):
        output_file='history_entropies.dat'
    
    # Save history of KLD
    history_entropies=partition.history_entropies
    with open(output_file,'w') as wr:
        wr.write(f"# KLD values | {stamp(__file__)}\n")
        wr.writelines( [ f"{x:.12f}\n" for x in history_entropies] )
    return output_file
#
def save_solution(partition, output_file=None):
    """ Saves shape functions """
    # Default name of output file
    if type(output_file)==type(None):
        output_file='solution.json'

    # Get the required objects
    coefficient_raw= partition.history_propars[-1]
    coordinates=partition.coordinates
    atomic_numbers=partition.numbers

    if isinstance(partition, MBISWPart): pass
    elif isinstance(partition, LinearISAWPart):
        basis=print_basis(partition.bs_helper, format='json')
    else: raise Exception()

    def get_lisa_func_info( basis, atomic_numbers, coefficient_list ):
        cur_index=0
        exponent_list, coefficients_list, normalization_list, orders_list = [ [] for i in range(4) ]
        for i,z in enumerate(atomic_numbers):
            local_exponents=basis.exponents[z]
            local_orders=basis.orders[z]
            
            new_index=cur_index+len(local_exponents)
            local_coeff=coefficient_list[cur_index:new_index]
            cur_index=new_index

            local_normalization=[]
            for i,alpha in enumerate(local_exponents):
                order=local_orders[i]
                # see /opt/miniconda3/envs/LISA_wpart/lib/python3.10/site-packages/horton_part/core/basis.py:l.137
                normalization=order*alpha**(3/order) / ( 4*np.pi* gamma(3 / order) )
                local_normalization.append(normalization)
            orders_list.append(local_orders)
            exponent_list.append(local_exponents)
            coefficients_list.append(local_coeff)
            normalization_list.append(local_normalization)
        # Sanity check
        assert len(coefficient_list)==cur_index, \
                f"Length of coefficients and basis does not work out: \'{len(coefficient_list)}\' \'{cur_index}\'"
        return exponent_list, orders_list, coefficients_list, normalization_list 
    def get_mbis_func_info(atomic_numbers, coefficient_list ):
        cur_index=0
        exponent_list, orders_list, coefficients_list, normalization_list = [ [] for i in range(4) ]
        coefficients, exponents = [ coefficient_list[i::2] for i in [0,1] ]

        for Z in atomic_numbers:
            nshell=get_nshells_for_nuclear_charge(Z)
            new_index=cur_index+nshell

            exponent_list+=[ exponents[cur_index:new_index].tolist() ]
            coefficients_list+=[ coefficients[cur_index:new_index].tolist() ]
            orders_list+=[ [1 for x in range(new_index-cur_index) ] ]
            local_normalization=[]
            for i,alpha in enumerate(exponent_list[-1]):
                order=1
                # see /opt/miniconda3/envs/LISA_wpart/lib/python3.10/site-packages/horton_part/core/basis.py:l.137
                normalization=order*alpha**(3/order) / ( 4*np.pi* gamma(3 / order) )
                local_normalization.append(normalization)
            normalization_list+=[ local_normalization ]

            cur_index=new_index

        return exponent_list, orders_list, coefficients_list, normalization_list 

        # Create atom
    if isinstance(partition, MBISWPart):
        exponent_list, orders_list, coefficient_list, normalization_list = get_mbis_func_info( atomic_numbers, coefficient_raw)
    elif isinstance(partition, LinearISAWPart):
        exponent_list, orders_list, coefficient_list, normalization_list = get_lisa_func_info( basis, atomic_numbers, coefficient_raw)
    else:
        raise Exception()

    ### Save the solution
    #-- Get in the object style
    #   First get dict and lists
    coordinates=coordinates
    shape_functions, atom_types=[ [] for i in range(2) ]
    for i,z in enumerate(atomic_numbers):
        atom_type=nuclear_charge_to_element_symbol(z)
        at={
            'exponent_scales': [ [x] for x in exponent_list[i] ],
            'exponent_orders': [ [x] for x in orders_list[i] ],
            'normalizations':  [ [x] for x in normalization_list[i]],
            'coefficients':    coefficient_list[i],
        }

        rad_bas=radial_atomic_basis(**at)
        shape_functions.append(rad_bas)
        atom_types.append(atom_type)
    dic={
        'basis_expansions':shape_functions,
        'centers':coordinates,
        'atom_types':atom_types,
    }
    sol=molecular_radial_basis(**dic)
    with open(output_file, 'w') as wr:
        json.dump(sol.model_dump(), wr)
    #output_file=sol.to_json(output_file=output_file)
    return output_file
#
def print_basis(basis, format='CamCASP'):
    """ Print the basis to an output file (in CamCASP format) """
    # Get the important data
    #if type(basis) in [ horton_basis.BasisFuncHelper , horton_basis.ExpBasisFuncHelper ]:
    try:
        exponents=basis.exponents
    except Exception as ex:
        raise Exception(f"Unkown type: {type(basis)}")
    # Define atom names and check if mapping works
    for key in exponents.keys():
        try:
            nuclear_charge_to_element_symbol(key)
        except:
            raise Exception(f"What to do with Z=\'{key}\'")\


    # Output the exponents
    if format=='CamCASP':
        # Generate a file dir_name/at_ty for all atom types in the dictionary
        dir_name='Cheng_LISA'
        if os.path.isdir(dir_name):
            print(f"Path {os.path.realpath(dir_name)} already existed")
        else:
            os.mkdir(dir_name)
        from datetime import datetime
        for key in exponents.keys():
            at_ty=nuclear_charge_to_element_symbol(key)
            file_name=os.path.join(dir_name, at_ty)


            # Get the header
            lines=[f"! CamCASP : ISA/{file_name} : {at_ty}" ]
            date=datetime.today().strftime('%Y-%m-%d')
            lines.append(f"! B.V. von Bruening extracted from the L-ISA implementation, {date}")
            lines.append('!')

            # Print the s-type functions
            lead_line=4*' '+f"1 s"
            for exp in exponents[key]:
                line=' '*4+f"{exp:.1f}       1.0"
                lines+=[lead_line, line ]

            # Print
            with open(file_name, 'w') as wr:
                wr.writelines([ l+"\n" for l in lines])
            print(f"File written to {os.path.realpath(file_name)}")
    elif format=='json':
        return basis
#
def save_moments(wpart, output_nam=None, method=None):
    sys.path.insert(1,os.environ['PY_MODULES'])
    #print(mol.atcharges, mol.atcoords)
    nuclear_charges=wpart.numbers
    coordinates=wpart.coordinates

    thres=1.e-16
    if any([np.abs(i%1)>1.e-16 for i in nuclear_charges]):
        raise Exception(f"Core charges not integers (thres: {thres}): {mol.atcorenums}")
    else:
        nuclear_charges=[ int(i) for i in nuclear_charges ]

    if type(method)==type(None):
        raise Exception(f"Provide method for naming!")
    if output_nam==None:
        output_nam=f"{method}_moments.mom"
    np.savetxt(f"{method}_charges.txt", wpart['charges'])
    np.savetxt(f"{method}_moments.txt", wpart['cartesian_multipoles'])

    from qcp_objects.objects.properties import custom_mtp_mom_file

    custom_mtp_mom_file(output_nam,nuclear_charges,wpart['pure_multipoles'],coords=coordinates, type=method)
    return output_nam
#
def save_part(wpart, cntrl:horton_wpart_controller, save_objs='all'):
    # Write the result to a file
    method=cntrl.method
    mom_nam=cntrl.output.moments_file
    his_nam=cntrl.output.kld_history_file
    sol_nam=cntrl.output.solution_file
    #pickle.dump(wpart, open('partition_dump.pkl','wb'))


    # Save information
    result_di={'files':{}}
    if isinstance(save_objs, list):
        raise Exception()
    elif isinstance(save_objs, str):
        if save_objs=='all':
            mom_file=save_moments(wpart, output_nam=mom_nam, method=method)
            his_file=save_histories(wpart, output_file=his_nam)
            sol_file=save_solution(wpart, output_file=sol_nam)
            result_di['files'].update({
                'moments':mom_file,
                'kld_history':his_file,
                'solution': sol_file,
            })
        else:
            raise Exception()
    else:
        raise Exception()
    with open('results.json', 'w') as wr:
        json.dump(result_di, wr)

### EXECUTION
@val_call
def exc_partition(mol, grid, rho, method:str, basis=None, solver=None):
    """Local LISA by solving convex optimization problem."""

    kwargs=prepare_argument_dict(mol, grid, rho)
    if method.lower() in ['mbis']:
        part = MBISWPart(**kwargs)
    elif method.lower() in ['lisa']:
        if type(solver)==type(None):
            raise Exception(f"Provide solver as option")
        
        from qcp_run_horton.basis.load_basis import load_basis
        if not basis is None:
            basis_func=load_basis(basis)
            kwargs['basis_func']=basis_func
        kwargs['solver']=solver
        part = LinearISAWPart(**kwargs)
    else:
        raise Exception(f"Unown method: {method}")

    part._lmax=4
    part.do_charges()
    part.do_moments()
    return part

def run_horton(controller, wfn_fi, method, basis, solver=None, ang_grid_dens=None):
    """ Run horton for the provided input """
    # Setup the calculation
    mol, grid, rho = prepare_grid_and_dens(wfn_fi, ang_grid_dens=ang_grid_dens)

    # Execute Partitioning and save results
    partition=exc_partition(mol, grid, rho, method=method, basis=basis, solver=solver)
    # Save multipoles, soltion and KLD
    save_part(partition, controller , save_objs='all')

    

