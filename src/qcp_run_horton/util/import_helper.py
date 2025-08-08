from qcp_objects.objects.basis import molecular_radial_basis, radial_atomic_basis
import os

from pydantic import BaseModel, validate_call; val_call=validate_call(config=dict(arbitrary_types_allowed=True))
from typing import List, Union, Tuple
import yaml, json, glob

file=str