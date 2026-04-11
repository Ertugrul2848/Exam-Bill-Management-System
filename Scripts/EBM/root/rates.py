"""
Billing rate constants for exam bill calculations.

All amounts are in BDT (Bangladeshi Taka).
"""

# Committee role rates
CHAIRMAN_RATE = 2700
TABULATION_RATE_JUNIOR = 2500   # semId 1-3
TABULATION_RATE_SENIOR = 3125   # semId 4+

# Semester-level role rates
MODERATION_RATE = 2150
TRANSLATION_RATE = 400
STENCIL_CUTTER_RATE = 375

# Theory course rates
QUESTION_PAPER_FORMULATION_RATE = 2150
PAPER_EVALUATION_PER_PAPER = 115

# Lab course rates
LAB_EVALUATION_RATE = 15000
LAB_VIVA_PER_HOUR = 200
LAB_INVIGILATOR_PER_HOUR = 400

# Viva course rates
VIVA_VOCE_PER_HOUR = 200

# Thesis rates
THESIS_PAPER_EVALUATION_PER_PAPER = 1250
THESIS_SUPERVISOR_PER_STUDENT = 3100


def get_tabulation_rate(sem_id):
    """Return tabulation rate based on semester level."""
    if 1 <= sem_id <= 3:
        return TABULATION_RATE_JUNIOR
    return TABULATION_RATE_SENIOR
