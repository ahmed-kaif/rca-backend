import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ALUMNI = "alumni"  # verified alumni
    STUDENT = "student"  # current student
    PENDING = "pending"  # needs admin approval


class BloodGroup(str, enum.Enum):
    A_POS = "A+"
    A_NEG = "A-"
    B_POS = "B+"
    B_NEG = "B-"
    O_POS = "O+"
    O_NEG = "O-"
    AB_POS = "AB+"
    AB_NEG = "AB-"
