from . import *
from .my_basis_set import basis_set, atom_type_basis

#####
# Call the central function load_basis to get a horton basis object for the tag
# Currently, all the functions in this file revovle around this function

@val_cal
def parse_basis(direc:directory) -> basis_set:
    """ For a given directory all files inside this directory are identified as basis files
    Currently only yaml and json dropped dictionaries of the radial_atomic_basis_type are accepted 
    """
    def load_file(file):
        def load_yaml(stream):
            return yaml.safe_load(stream)
        def load_json(stream):
            return json.load(stream)
        extension=file.lower().split('.')[-1]
        if extension in ['yaml']:
            loader=load_yaml
        elif extension in ['json']:
            loader=load_json
        else:
            raise Exception(f"Do not know how to load file of type {extension} (file={file})")
        with open(file, 'r') as rd:
            data=loader(rd)
        return data

    # Get all files in the folder
    files=[ x for x in glob.glob(f"{direc}/*") if os.path.isfile(x) ]

    # Map files to atom type (drop the extension)
    dic={}
    for f in files:
        atom_type=os.path.basename(f).split('.')[0]
        if atom_type in dic.keys():
            raise Exception(f"Atom type doubly defined in directory: {direc}: {[dic[atom_type],f]}")
        else:
            dic.update({atom_type:f})

    # Read the files and intreprete the content as radia basis
    the_basis_set=[]
    for k,v in dic.items():
        content=load_file(v)
        assert isinstance(content, dict), f"The file {v} does not contain a dictionary but {type(content)}"

        the_basis=atom_type_basis(atom_type=k, basis=radial_atomic_basis(content))
        the_basis_set.append(the_basis)
    the_basis_set=basis_set(basis_set=the_basis_set)

    return the_basis_set


@val_cal
def make_horton_basis(the_basis_set: basis_set):
    """ Given """

    # Map the atomtype to its charge (horton does not have atom types) 
    ret_dic={}
    for atom_type_basis in the_basis_set.basis_set:
        atom_type,basis =atom_type_basis.atom_type, atom_type_basis.basis

        # Atom type to Element
        Z=element_symbol_to_nuclear_charge(atom_type)
        if Z in ret_dic.keys():
            message=f"Double definition of atom_type with carge=\'{Z}\': Horton defines basis by charge while CamCASP allows for custom atom types: "
            "Hence, in CamCASP multiple basis sets for a single atom can exists while in horton there can only be one!"
            raise Exception(message)
        ret_dic.update({Z: basis})
    # Map the basis onto the keys required by horton
    for atom_type, crude_basis in ret_dic.items():
        ret_dic[atom_type]=crude_basis.generate_horton_basis() 

    # Reshape the dictionary since horton takes a dictionary of parameters with a dictionary of atomic charges inside
    new_dic={}
    # Iterate over each atom type
    for at_ty, horton_basis in ret_dic.items():
        # For each parameterset in the atom type add them
        for k, basis_item in horton_basis.items():

            # Add to dicitonary in case its not there yet
            if not k in new_dic.keys(): new_dic.update({k:{}})
            
            # Reshape the parmaeter array (I accomodate contracted functions while mbis does not)
            def reshape_item(item):
                if isinstance(item, list):
                    assert len(item)==1, f"Found contracted type which I cannot translate to the primitive types which Horton takes"
                    item=item[0]
                return item
            new_dic[k].update({at_ty: [reshape_item(i) for i in basis_item]})

    # Initialize the Horton basis and return it
    horton_basis = ExpBasisFuncHelper(**new_dic)
    return horton_basis

@val_cal
def get_horton_basis_home() -> directory:
    """ Get Path of Horton Basis """

    # Get horton home directory
    horton_env_name='RUN_HORTON_HOME'
    if not horton_env_name in os.environ.keys():
        raise Exception(f"Could not find environment variable {horton_env_name} in environement")
    horton_home=os.environ[horton_env_name]

    # Check if basis directory is located below home directory
    basis_subdir='basis'
    basis_path=os.path.join(horton_home, basis_subdir)
    if not os.path.isdir(basis_path):
        raise Exception(f"Expected directory to exist (found under environment variable \'${horton_env_name}\')): \'{basis_path}\'")

    return basis_path

@val_cal
def get_basis_directory(basis_home:directory, basis_tag:str) -> directory:
    """ Given the path where directories are found, check if the given tag can be found in this directory"""

    basis_options=[ os.path.basename(x.rstrip('/')) for x in glob.glob(f"{basis_home}/*/")  if os.path.isdir(x) ]
    if not basis_tag in basis_options:
        raise Exception(f"The basis tag \'{basis_tag}\' is not present in {basis_home}, but present are: {basis_options}")
    basis_path=os.path.join(basis_home, basis_tag)
    
    return basis_path

@validate_call
def load_basis(basis_tag:str):
    """ """  
    # Get the directory where basis sets are stored
    basis_home=get_horton_basis_home()
    # Check if the given basis_tag occur in this basis directory and return it
    basis_path=get_basis_directory(basis_home, basis_tag)
    # Parse the basis information found in the given basis directory
    the_basis=parse_basis(basis_path)
    # Transform the found data into a horton basis path object
    horton_basis=make_horton_basis(the_basis)

    return horton_basis
