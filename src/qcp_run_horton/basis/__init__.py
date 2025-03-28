import os, re, glob, numpy as np, shutil, json, yaml
from pydantic import BaseModel, validate_call; val_cal=validate_call(config=dict(arbitrary_types_allowed=True))
from typing import Tuple, List, Union, Literal
from qc_global_utilities.environment import directory, file

from qc_objects.objects.basis import radial_atomic_basis

from horton_part.core.basis import AnalyticBasisFuncHelper, BasisFuncHelper, ExpBasisFuncHelper
from qc_global_utilities.encoding_and_conversion.encoding import element_symbol_to_nuclear_charge
from functools import partial