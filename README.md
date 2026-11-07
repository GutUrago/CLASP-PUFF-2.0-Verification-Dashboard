# CLASP PUFF 2.0 – Verification dashboard

This Streamlit dashboard follows the CLASP PUFF 2.0 verification survey, run
by Laterite to check that subsidised productive-use appliances reached the
customers on the distributors' sales records, and how those customers use and
judge them. It gives the field and MEL teams one place to see how fieldwork is
going and what the interviews are finding, without handling raw survey data.

The dashboard pulls submissions from SurveyCTO through its API, on a fixed
schedule and whenever someone clicks Refresh. Only fields marked publishable
in the form are returned, and the app keeps just the anonymised fields it
needs, so names, phone numbers, locations and other personal details never
reach it. The sample roster is read the same way, from a SurveyCTO server
dataset. If SurveyCTO can't be reached, the app shows the last data it
downloaded.

The Overview page tracks progress against the main households on the roster:
how many have been attempted and completed, where each household stands, how
companies and counties compare, and which households need a callback or were
interviewed in a different mode from the one assigned. The Indicator analysis
page reports the survey's indicators for completed interviews (verification,
use of the appliance, energy, livelihoods, customer satisfaction and climate
resilience), and every chart can be split by company, county, sample, survey
mode, appliance, gender or age group.
