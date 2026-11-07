# Value labels for the coded variables used in the dashboard.
# Taken from the choices sheet of the latest coded form
# (CLASP PUFF2 Verification Round 1, version 2611070342), shortened for charts.
# If the form's choices change, update the codes here.

COUNTRY = {1: "Ethiopia", 2: "Kenya", 3: "Nigeria"}
# codes 4 and 5 come from the sales report (appliance portfolio), not the form list
APPLIANCE = {1: "Solar water pump", 2: "Grain mill", 3: "Refrigerator/freezer",
             4: "Walk-in cold room", 5: "Egg incubator/brooder"}
MODE = {1: "In-person", 2: "Phone"}
GENDER = {1: "Female", 0: "Male"}
YESNO = {1: "Yes", 0: "No"}
YESNO_PARTIAL = {1: "Yes", 2: "Partially", 0: "No", -99: "Don't know"}

# B0a - who contacted the respondent before the survey
CONTACTED_BY = {1: "The company", 2: "Company sales agent", 3: "Laterite", -96: "Other",
                -99: "Don't know"}
DESC_MATCH = {1: "Matches", 2: "Partly matches", 0: "Does not match", -99: "Could not describe"}

EDUCATION = {0: "Never attended", 1: "Early childhood", 2: "Primary", 3: "Secondary", 4: "Tertiary"}

# D1a - what happened to the appliance (asked when D1 = No)
APPLIANCE_FATE = {1: "Sold it", 2: "Gave it away", 3: "Stolen", 4: "Broke down, discarded",
                  5: "Returned to company", 6: "Repossessed", 7: "Never received/installed",
                  -96: "Other"}
# D1b - why it was not received or installed
NOT_RECEIVED = {1: "Waiting for delivery", 2: "Delivered, not installed",
                3: "Installation not finished", 4: "Order cancelled", 5: "Could not pay",
                6: "Site not suitable", -96: "Other", -99: "Don't know"}
NOT_USING = {1: "Stopped working", 2: "In repair", 3: "Returned", 4: "Could not afford",
             5: "Got sick", 6: "Don't know how to use", 7: "Not useful", -96: "Other"}
USE_PURPOSE = {1: "Non-income", 2: "Income-generating", 3: "Both"}
PUMP_USE = {1: "Irrigating crops", 2: "Household water", 3: "Watering livestock",
            4: "Selling water", -96: "Other"}
DECISION = {0: "Respondent", 1: "Spouse", 2: "Parent", 3: "Son/daughter", 11: "Jointly with partner",
            -96: "Other"}

ENERGY_SOURCE = {1: "Grid", 2: "Mini grid", 3: "Biomass", 4: "Solar home system",
                 5: "Diesel/generator", 6: "Kerosene", 7: "None", -96: "Other"}
REPLACE = {1: "Completely replace", 2: "Complement"}
PREVIOUS_FATE = {1: "Still used alongside", 2: "Kept as backup", 3: "Sold", 4: "Given away",
                 5: "Broke down/discarded", 6: "Traded in", -96: "Other"}

YIELD_CHANGE = {1: "Decreased", 2: "Unchanged", 3: "Increased"}
WELLBEING = {1: "Much worse", 2: "Slightly worse", 3: "No change", 4: "Slightly improved",
             5: "Much improved"}

SATISFACTION_4 = {1: "Very dissatisfied", 2: "Dissatisfied", 3: "Satisfied", 4: "Very satisfied"}
PAYMENT = {1: "Own income/savings", 2: "Friends/family", 3: "Formal loan", 4: "Informal lender",
           5: "PAYGo/installments", -96: "Other"}
WARRANTY_KNOW = {1: "Yes, knows length", 2: "Yes, length unknown", 0: "No warranty",
                 -99: "Don't know"}

SHOCKS = {1: "Drought", 2: "Flood", 3: "Storm/cyclone", 4: "Heat wave", 5: "Erratic rainfall",
          6: "Pests/crop disease", 0: "None", -96: "Other"}
SERIAL_ACCESS = {1: "Readable", 2: "Visible, not readable", 3: "Cannot access",
                 4: "No label found", -96: "Other"}

CSAT_ITEMS = {
    "CSAT_1": "Product quality",
    "CSAT_repair": "Repairability",
    "CSAT_2": "Reliability",
    "CSAT_3": "Value for money",
    "CSAT_4": "Ease of operation",
    "CSAT_5": "Customer service",
    "CSAT_global": "Overall",
}
# PCRS_global is disabled in the form, so only the three pillars are shown
PCRS_ITEMS = {
    "PCRS_1": "Absorptive (recovery)",
    "PCRS_2": "Anticipatory (preparedness)",
    "PCRS_3": "Adaptive (incremental shift)",
}
TIME_ACTIVITIES = {"shop": "Shopping for food", "collect": "Collecting water", "mill": "Milling",
                   "irrig": "Irrigating", "sell": "Selling produce",
                   "keepshop": "Keeping shop open"}
