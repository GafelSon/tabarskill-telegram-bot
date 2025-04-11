from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import Models

from .enums import *

from .profile import ProfileModel
from .students import StudentModel
from .professors import ProfessorModel
from .faculty import FacultyModel
from .major import MajorModel
from .university import UniversityModel
from .wallet import WalletBase
