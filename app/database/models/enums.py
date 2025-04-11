from enum import Enum


class RoleType(Enum):
    STUDENT = "student"
    PROFESSOR = "professor"
    SUPPORT = "support"


class ProfessorPosType(Enum):
    ASSISTANT_PROFESSOR = "assistant_professor"
    ASSOCIATE_PROFESSOR = "associate_professor"
    FULL_PROFESSOR = "full_professor"
    LECTURER = "lecturer"
    ADJUNCT_PROFESSOR = "adjunct_professor"
    VISITING_PROFESSOR = "visiting_professor"
