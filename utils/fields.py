"""
The SurveyCTO fields the dashboard uses.

Every name here was checked against the latest coded form
(CLASP PUFF2 Verification Round 1, version 2611110448): all are marked
publishable and none is disabled. Anything else the API returns is dropped
when the data is loaded, so PII and unused fields never reach the app.

If the form changes, re-check this list against the survey sheet
(publishable = yes, disabled empty) before adding a new chart.
"""

FIELDS = {
    "Interview": ["starttime", "endtime", "duration_total", "survey_mode"],
    "Sample (preloaded)": [
        "hh_id", "sample_type", "p_survey_mode", "p_company", "p_county", "p_area_1",
        "p_country_code", "appliance_code", "p_technology", "p_currency", "days_since_purchase",
    ],
    "Contact and status": [
        "response", "consent", "availability", "consent_ok", "interview_ok",
        "appliance_received", "appliance_in_use", "reached_end", "survey_status", "survey_status_lbl",
    ],
    "Appliance confirmation": ["B0", "B0a", "B1", "B1a", "B1b", "B2", "B8"],
    "Household": ["C1", "C2", "C3", "C4_screen", "C4_1", "C4_2", "C4_3", "C4_4", "C4_5", "C4_6", "C5"],
    "Appliance use": ["D1", "D1a", "D1b", "D2", "D3", "D4", "D4a", "D5", "D5b", "D6b", "D7", "D8"],
    "Energy": [
        "E1a", "E1b",
        "E2a_1", "E2a_2", "E2a_3", "E2a_4", "E2a_5", "E2a_6", "E2a_7",
        "E2b_1", "E2b_2", "E2b_3", "E2b_4", "E2b_5", "E2b_6", "E2b_7",
        "F1a", "F1b", "E2", "E3", "E5", "E6",
    ],
    "Income": ["F1", "F2", "F3", "F4", "F4a", "F4b", "F5", "F6"],
    "Business": ["G1_new", "G2", "G4", "G6"],
    "Time use": [
        "G11_shop", "G10_shop", "G13_shop",
        "G11_collect", "G10_collect", "G13_collect",
        "G11_mill", "G10_mill", "G13_mill",
        "G11_irrig", "G10_irrig", "G13_irrig",
        "G11_sell", "G10_sell", "G13_sell",
        "G11_keepshop", "G10_keepshop", "G13_keepshop",
    ],
    "Customers and wellbeing": ["H1", "H2", "I2"],
    "Satisfaction": [
        "J1", "J2", "J6", "J8", "CSAT_1", "CSAT_repair", "CSAT_2", "CSAT_3", "CSAT_4",
        "CSAT_5", "CSAT_global", "NPS", "CES", "K4", "K_warranty", "K6",
    ],
    "Climate resilience": ["PCRS_0", "PCRS_1", "PCRS_1b", "PCRS_2", "PCRS_3"],
    "Future purchases": ["L1", "L2"],
    "In-person check": ["photo_consent", "serial_access", "serial_match", "serial_verified"],
}

# SurveyCTO adds these to every submission
METADATA = ["KEY", "SubmissionDate", "formdef_version"]

# select_multiple questions. The API sends one column per option
# (PCRS_0_1, PCRS_0_2, ..., PCRS_0__96 for -96) holding 1 when the option was
# ticked and nothing otherwise. Those columns are kept as well.
SELECT_MULTIPLE = ["D5b", "E1a", "E1b", "F1a", "F1b", "E3", "E6", "J6", "J8", "PCRS_0", "PCRS_1b", "L2"]

# Text fields (everything else is converted to numbers)
TEXT = ["KEY", "formdef_version", "hh_id", "sample_type", "p_survey_mode", "p_company",
        "p_county", "p_area_1", "p_technology", "p_currency", "survey_status_lbl"]

# Without these the pull is treated as failed and the local file is used
REQUIRED = ["KEY", "starttime", "hh_id", "survey_status", "response", "survey_mode", "p_company"]

ALL_FIELDS = METADATA + [f for group in FIELDS.values() for f in group]
