from . import *


from .my_basis_set import basis_set

@val_cal
def get_camcasp_basis_directory(camcasp_path: directory, basis_type:str ) -> directory:
    """ Find the basis relative to $CAMCASP environment variabale """ 

        
    
    def get_basis_home(camcasp_path):
        # Check if the camcasp basis directory exists
        aux_basis_path=os.path.join( camcasp_path, 'basis/auxiliary/')
        if not os.path.isdir(aux_basis_path):
            raise Exception(f"Cannot find directory with CamCASP basis: {aux_basis_path}")
        return aux_basis_path
    
    # Get the directory that contain the auxilary basis sets
    basis_home=get_basis_home(camcasp_path)
    return basis_home


def read_camcasp_basis_file(basis_file:file) -> radial_atomic_basis:
    basis=radial_atomic_basis(basis_file, inp_type='CamCASP')
    basis.initial_coefficients=np.array( [ 1./len(basis.exponent_scales) for x in basis.exponent_scales ] ).tolist()
    return basis

def get_subdir(basis_home,basis_type):
    folder_map={
        'set2': 'ISA/set2',
        'avqz': 'aug-cc-pVQZ',
    }
    basis_type=basis_type.lower()
    if basis_type.lower() in folder_map.keys():
        basis_subdir=folder_map[basis_type.lower()]
        # raise Exception(f"The requested basis {basis_type.lower()} cannot be found in available directory mapping"
        #         +f"{list(folder_map.keys())}")
    else:
        basis_subdir=basis_type
    
    basis_dir=os.path.join(basis_home, basis_subdir)
    if not os.path.isdir(basis_dir): raise Exception(f"Not a valid path for final basis directory: {basis_dir}")
    return basis_dir
@val_cal 
def read_camcasp_basis(basis_home:directory, basis_type:str):
    """ """
    basis_location=get_subdir(basis_home, basis_type)
    
    # Get all the files as directory
    basis_files=glob.glob( os.path.join( basis_location, '*' ) )
    basis_dic=dict( [ (os.path.basename(x), os.path.realpath(x)) for x in basis_files ] )

    # Replace the file_paths by their content
    basis_dic=dict([ (k,read_camcasp_basis_file(v)) for k,v in basis_dic.items()])

    return basis_dic

@val_cal
def load_camcasp_basis( basis_type, camcasp_path:directory|None=None):
    """ Loads basis from camcasp file structure into dumped radial_atomic_basis objects"""

    # If camcasp path is None, then load the default
    @val_cal
    def default_camcasp_path(camcasp_var_name:str='CAMCASP') -> directory:
        """ Find CamCASP path by variable """
        if not camcasp_var_name in os.environ.keys():
            raise Exception(f"Could not find default Camcasp since environment varilabel \'{camcasp_var_name}\' cannot be found in current environemtn")
        else:
            return os.environ[camcasp_var_name]
    if camcasp_path is None:
        camcasp_path=default_camcasp_path()

    # Get the directory where the specific camcasp basis set should be found
    basis_home=get_camcasp_basis_directory(camcasp_path, basis_type)


    def get_mixed_basis(basis_home,basis_type):

        my_get_basis=partial(read_camcasp_basis, basis_home)

        def mix_basis(basis_types_for_mixing:List[str]):
            basis_mixer=dict([ (k,my_get_basis(k)) for k in basis_types_for_mixing])
            
            basis_mix={}
            for basis_type, basis_dic in basis_mixer.items():
                for at_ty, basis in basis_dic.items():
                    if not at_ty in basis_mix.keys(): basis_mix.update({at_ty:{}})
                    basis_mix[at_ty].update({basis_type:basis})
            return basis_mix


        sep='_'
        if re.match(r'set2'+sep,basis_type):
            # Get the basis sets that will contribute
            ar=basis_type.split(sep)
            assert len(ar)==3, f"Excpected three segmenets separated by \'{sep}\', got: {basis_type}"

            first='set2'
            try:
                limit=int(ar[1])
            except Exception as ex: raise Exception(f"Cannot interprete as integer (in key \'{basis_type}\'): {ar[1]}")
            second=ar[2]

            mixed_basis=mix_basis([first, second])
            united_basis={}
            for atom_type, basis_options in mixed_basis.items():
                try:
                    Z=element_symbol_to_nuclear_charge(atom_type)
                except Exception as ex:
                    continue
                if Z>=limit:
                    key='avqz'
                else:
                    key='set2'
                
                if key in basis_options.keys():
                    united_basis.update({atom_type: basis_options[key]})
            the_basis=united_basis
        else:
            # Load the elements found in this directory
            the_basis=my_get_basis(basis_type)
        return the_basis

    the_basis=get_mixed_basis(basis_home,basis_type)


    the_basis_cl=basis_set(basis_set=[ {'atom_type':k,'basis':b.model_dump()} for k,b in the_basis.items() ])
    the_basis_cl.drop_to_file_structure(basis_set_name=basis_type)
    

    return the_basis

    
