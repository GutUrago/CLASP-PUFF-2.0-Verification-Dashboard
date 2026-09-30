# Value labels for the coded variables used in the dashboard.
# Copied from the choices sheet of the PUFF 2.0 verification form (R1).
# If the form changes, update the codes here.

COUNTRY = {1: "Ethiopia", 2: "Kenya", 3: "Nigeria"}
APPLIANCE = {1: "Solar water pump", 2: "Grain mill", 3: "Refrigerator/freezer"}
MODE = {1: "In-person", 2: "Phone"}
GENDER = {1: "Female", 0: "Male"}
YESNO = {1: "Yes", 0: "No"}
YESNO_PARTIAL = {1: "Yes", 2: "Partially", 0: "No", -99: "Don't know"}

CALL_STATUS = {
    1: "Completed",
    2: "Answered, not completed",
    3: "Answered, not by respondent",
    4: "No answer",
    5: "Refusal",
    6: "Purchase not confirmed (respondent)",
    7: "Purchase not confirmed (someone else)",
    8: "Not enough knowledge",
    9: "Rescheduled",
    10: "Wrong number",
    11: "Did not receive appliance",
    12: "Did not use appliance",
    13: "Dropped midway",
}

EDUCATION = {0: "Never attended", 1: "Early childhood", 2: "Primary", 3: "Secondary", 4: "Tertiary"}
USE_PURPOSE = {1: "Non-income", 2: "Income-generating", 3: "Both"}
NOT_USING = {1: "Stopped working", 2: "In repair", 3: "Returned", 4: "Could not afford",
             5: "Got sick", 6: "Don't know how to use", 7: "Not useful", -96: "Other"}
DECISION = {0: "Respondent", 1: "Spouse", 2: "Parent", 3: "Son/daughter", 11: "Jointly with partner",
            -96: "Other"}
YIELD_CHANGE = {1: "Decreased", 2: "Unchanged", 3: "Increased"}
REPLACE = {1: "Completely replace", 2: "Complement"}

ENERGY_SOURCE = {1: "Grid", 2: "Mini grid", 3: "Biomass", 4: "Solar home system",
                 5: "Diesel/generator", 6: "Kerosene", 7: "None", -96: "Other"}
PAYMENT = {1: "Own income/savings", 2: "Friends/family", 3: "Formal loan", 4: "Informal lender",
           5: "PAYGo/installments", -96: "Other"}
SHOCKS = {1: "Drought", 2: "Flood", 3: "Storm/cyclone", 4: "Heat wave", 5: "Erratic rainfall",
          6: "Pests/crop disease", 0: "None", -96: "Other"}

SCALE_5 = {1: "1", 2: "2", 3: "3", 4: "4", 5: "5"}
WELLBEING = {1: "Much worse", 2: "Slightly worse", 3: "No change", 4: "Slightly improved",
             5: "Much improved"}
SATISFACTION_4 = {1: "Very dissatisfied", 2: "Dissatisfied", 3: "Satisfied", 4: "Very satisfied"}

CSAT_ITEMS = {
    "CSAT_1": "Product quality",
    "CSAT_repair": "Repairability",
    "CSAT_2": "Reliability",
    "CSAT_3": "Value for money",
    "CSAT_4": "Ease of operation",
    "CSAT_5": "Customer service",
    "CSAT_global": "Overall",
}
PCRS_ITEMS = {
    "PCRS_1": "Absorptive (recovery)",
    "PCRS_2": "Anticipatory (preparedness)",
    "PCRS_3": "Adaptive (incremental shift)",
    "PCRS_global": "Overall resilience",
}
TIME_ACTIVITIES = {"shop": "Shopping for food", "collect": "Collecting water", "mill": "Milling",
                   "irrig": "Irrigating", "farm": "Farming", "sell": "Selling produce",
                   "keepshop": "Keeping shop open"}
