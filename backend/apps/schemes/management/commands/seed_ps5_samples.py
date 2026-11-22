import datetime
import copy
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.schemes.models import Scheme, RequiredDocument, EligibilityRule

SAMPLE_SCHEMES_DATA = [
    {
        "code": "SAMPLE-MH-LADKI-BAHIN",
        "name": "[SAMPLE] Mukhyamantri Majhi Ladki Bahin Yojana",
        "name_marathi": "[नमुना] मुख्यमंत्री माझी लाडकी बहीण योजना",
        "category": "WOMEN_CHILD",
        "jurisdiction": "STATE",
        "state": "Maharashtra",
        "department": "Women and Child Development Department, Maharashtra",
        "statutory_gr": "GR No. WCD-2024/C.R.142/WCD-2",
        "official_portal_url": "https://ladakibahin.maharashtra.gov.in/",
        "official_source_url": "https://ladakibahin.maharashtra.gov.in/",
        "portal_name": "Nari Shakti Doot / Aaple Sarkar",
        "benefit_type": "MAINTENANCE_STIPEND",
        "benefit_amount_text": "₹1,500 per month DBT into Aadhaar-seeded bank account",
        "estimated_annual_value": 18000,
        "brief_description": "Financial assistance of ₹1,500/month for women aged 21-65 from low-income families residing in Maharashtra.",
        "is_sample": True,
        "verification_status": "UNVERIFIED",
        "application_deadline": datetime.date(2027, 3, 31),
        "application_steps": [
            "Download Nari Shakti Doot app or visit Aaple Sarkar portal.",
            "Register using Aadhaar-linked mobile number.",
            "Upload Ration Card, Domicile Certificate, and Bank Passbook copy.",
            "Submit Hamipatra self-declaration form."
        ],
        "eligibility_criteria": {
            "clauses": [
                {
                    "id": "mh_domicile",
                    "description": "Applicant must be a permanent resident / domicile of Maharashtra",
                    "source_ref": "GR No. WCD-2024/C.R.142/WCD-2",
                    "mandatory": True,
                    "field": "is_maharashtra_domicile",
                    "op": "eq",
                    "value": True,
                    "remedy": {
                        "text": "Obtain a Maharashtra State Domicile Certificate or 15-year Ration Card from Tahsildar / Aaple Sarkar.",
                        "source_ref": "GR No. WCD-2024/C.R.142/WCD-2"
                    }
                },
                {
                    "id": "age_min_21",
                    "description": "Minimum age of applicant must be 21 years",
                    "source_ref": "GR No. WCD-2024/C.R.142/WCD-2",
                    "mandatory": True,
                    "field": "age_years",
                    "op": "gte",
                    "value": 21,
                    "remedy": {
                        "text": "Applicant must be at least 21 years of age at the time of application.",
                        "source_ref": "GR No. WCD-2024/C.R.142/WCD-2"
                    }
                },
                {
                    "id": "age_max_65",
                    "description": "Maximum age of applicant must be 65 years",
                    "source_ref": "GR No. WCD-2024/C.R.142/WCD-2",
                    "mandatory": True,
                    "field": "age_years",
                    "op": "lte",
                    "value": 65,
                    "remedy": {
                        "text": "Citizens aged above 65 are eligible for Old Age Pension or Shravanbal Yojana.",
                        "source_ref": "Social Justice Dept Guidelines"
                    }
                },
                {
                    "id": "income_cap_250k",
                    "description": "Annual household income must not exceed ₹2,50,000",
                    "source_ref": "GR No. WCD-2024/C.R.142/WCD-2",
                    "mandatory": True,
                    "field": "annual_household_income_inr",
                    "op": "lte",
                    "value": 250000,
                    "remedy": {
                        "text": "Verify household income proof (Tahsildar Income Certificate or Yellow/Orange Ration Card).",
                        "source_ref": "GR No. WCD-2024/C.R.142/WCD-2"
                    }
                }
            ]
        },
        "documents": [
            {"name": "Aadhaar Card (Aadhaar Seeded)", "description": "Identity and DBT routing proof", "is_mandatory": True, "sort_order": 1},
            {"name": "Maharashtra Domicile Certificate / Ration Card", "description": "Proof of 15 years state residency", "is_mandatory": True, "sort_order": 2},
            {"name": "Annual Family Income Certificate (<= ₹2.5 Lakhs)", "description": "Issued by Tahsildar or Orange/Yellow ration card", "is_mandatory": True, "sort_order": 3},
            {"name": "Hamipatra (Self-Declaration)", "description": "Affidavit that no family member is an income taxpayer", "is_mandatory": True, "sort_order": 4}
        ],
        "rules": [
            {"code": "R1", "field": "is_maharashtra_domicile", "operator": "eq", "value": True, "description": "Must reside in Maharashtra", "is_mandatory": True, "sort_order": 1},
            {"code": "R2", "field": "age_years", "operator": "gte", "value": 21, "description": "Minimum age 21 years", "is_mandatory": True, "sort_order": 2},
            {"code": "R3", "field": "age_years", "operator": "lte", "value": 65, "description": "Maximum age 65 years", "is_mandatory": True, "sort_order": 3},
            {"code": "R4", "field": "annual_household_income_inr", "operator": "lte", "value": 250000, "description": "Annual household income <= ₹2,50,000", "is_mandatory": True, "sort_order": 4}
        ]
    },
    {
        "code": "SAMPLE-PM-KISAN",
        "name": "[SAMPLE] Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
        "name_marathi": "[नमुना] प्रधानमंत्री किसान सन्मान निधी",
        "category": "AGRICULTURE",
        "jurisdiction": "CENTRAL",
        "state": "",
        "department": "Ministry of Agriculture and Farmers Welfare, Govt of India",
        "statutory_gr": "Central Sector Scheme Guidelines PM-KISAN 2019",
        "official_portal_url": "https://pmkisan.gov.in/",
        "official_source_url": "https://pmkisan.gov.in/",
        "portal_name": "PM-KISAN Portal",
        "benefit_type": "MAINTENANCE_STIPEND",
        "benefit_amount_text": "₹6,000 per year in 3 equal installments of ₹2,000 via DBT",
        "estimated_annual_value": 6000,
        "brief_description": "Income support to all landholding farmer families with cultivable land in their names.",
        "is_sample": True,
        "verification_status": "UNVERIFIED",
        "application_deadline": None,
        "application_steps": [
            "Visit pmkisan.gov.in -> Farmer Corner -> New Farmer Registration.",
            "Enter Aadhaar number and select rural/urban region.",
            "Fill land survey details, Gat/Khata number, and upload 7/12 land extract.",
            "Complete mandatory e-KYC via Aadhaar OTP."
        ],
        "eligibility_criteria": {
            "clauses": [
                {
                    "id": "age_adult_18",
                    "description": "Applicant must be an adult aged at least 18 years",
                    "source_ref": "PM-KISAN Operational Guidelines 2019",
                    "mandatory": True,
                    "field": "age_years",
                    "op": "gte",
                    "value": 18,
                    "remedy": {
                        "text": "Applicant must be an adult landholder.",
                        "source_ref": "PM-KISAN Operational Guidelines 2019"
                    }
                },
                {
                    "id": "income_small_farmer",
                    "description": "Annual household income must be within small farmer threshold (<= ₹2,00,000)",
                    "source_ref": "PM-KISAN Guidelines Para 2",
                    "mandatory": True,
                    "field": "annual_household_income_inr",
                    "op": "lte",
                    "value": 200000,
                    "remedy": {
                        "text": "Institutional landholders and income tax-paying farmer families are excluded.",
                        "source_ref": "PM-KISAN Operational Guidelines 2019"
                    }
                }
            ]
        },
        "documents": [
            {"name": "Land Record / 7/12 Land Extract", "description": "Proof of agricultural cultivable land ownership", "is_mandatory": True, "sort_order": 1},
            {"name": "Aadhaar Card with e-KYC", "description": "Mandatory identity authentication", "is_mandatory": True, "sort_order": 2},
            {"name": "NPCI Mapped Bank Account Passbook", "description": "Bank account enabled for direct payment", "is_mandatory": True, "sort_order": 3}
        ],
        "rules": [
            {"code": "R1", "field": "age_years", "operator": "gte", "value": 18, "description": "Minimum age 18 years", "is_mandatory": True, "sort_order": 1},
            {"code": "R2", "field": "annual_household_income_inr", "operator": "lte", "value": 200000, "description": "Annual household income <= ₹2,00,000", "is_mandatory": True, "sort_order": 2}
        ]
    },
    {
        "code": "SAMPLE-MH-EBC-SCHOLARSHIP",
        "name": "[SAMPLE] Rajarshi Chhatrapati Shahu Maharaj Shikshan Shulkh Shishyavrutti (EBC)",
        "name_marathi": "[नमुना] राजर्षी छत्रपती शाहू महाराज शिक्षण शुल्क शिष्यवृत्ती",
        "category": "EDUCATION",
        "jurisdiction": "STATE",
        "state": "Maharashtra",
        "department": "Directorate of Higher & Technical Education, Maharashtra",
        "statutory_gr": "GR No. TEM-2016/C.R.228/TE-4",
        "official_portal_url": "https://mahadbt.maharashtra.gov.in/",
        "official_source_url": "https://mahadbt.maharashtra.gov.in/",
        "portal_name": "MahaDBT",
        "benefit_type": "TUITION_FEE_WAIVER",
        "benefit_amount_text": "50% Tuition Fee & 50% Exam Fee Reimbursement to College",
        "estimated_annual_value": 45000,
        "brief_description": "Fee concession for economically backward class students admitted to professional degree/diploma courses via CAP round.",
        "is_sample": True,
        "verification_status": "UNVERIFIED",
        "application_deadline": datetime.date(2027, 1, 31),
        "application_steps": [
            "Register on MahaDBT portal with Aadhaar authentication.",
            "Complete student profile with Domicile, Tahsildar Income, and CAP allotment details.",
            "Apply under DTE/DHE -> RCSM Shikshan Shulkh Shishyavrutti Yojna.",
            "Submit printed copy with attested proofs to college scholarship clerk."
        ],
        "eligibility_criteria": {
            "clauses": [
                {
                    "id": "mh_domicile",
                    "description": "Student must be a Maharashtra domicile resident",
                    "source_ref": "GR No. TEM-2016/C.R.228/TE-4",
                    "mandatory": True,
                    "field": "is_maharashtra_domicile",
                    "op": "eq",
                    "value": True,
                    "remedy": {
                        "text": "Obtain Maharashtra State Domicile Certificate from Tahsildar / MahaOnline.",
                        "source_ref": "GR No. TEM-2016/C.R.228/TE-4"
                    }
                },
                {
                    "id": "caste_open_general_ews",
                    "description": "Candidate must belong to Open / General or EWS category",
                    "source_ref": "GR No. TEM-2016/C.R.228/TE-4",
                    "mandatory": True,
                    "field": "caste_category",
                    "op": "in",
                    "value": ["GENERAL", "OPEN", "EWS"],
                    "remedy": {
                        "text": "Reserved category students (OBC/SC/ST/VJNT/SBC) should apply under their respective departmental scholarships on MahaDBT.",
                        "source_ref": "MahaDBT Portal Guidelines"
                    }
                },
                {
                    "id": "income_cap_800k",
                    "description": "Annual household income must not exceed ₹8,00,000",
                    "source_ref": "GR No. TEM-2016/C.R.228/TE-4",
                    "mandatory": True,
                    "field": "annual_household_income_inr",
                    "op": "lte",
                    "value": 800000,
                    "remedy": {
                        "text": "Submit authorized Income Certificate from Tahsildar issued for current financial year.",
                        "source_ref": "GR No. TEM-2016/C.R.228/TE-4"
                    }
                },
                {
                    "id": "has_student_enrolled",
                    "description": "Household must have an actively enrolled student member",
                    "source_ref": "GR No. TEM-2016/C.R.228/TE-4",
                    "mandatory": True,
                    "field": "has_student_member",
                    "op": "eq",
                    "value": True,
                    "remedy": {
                        "text": "Ensure candidate is registered as a student with approved CAP admission.",
                        "source_ref": "GR No. TEM-2016/C.R.228/TE-4"
                    }
                }
            ]
        },
        "documents": [
            {"name": "Tahsildar Income Certificate (<= ₹8 Lakhs)", "description": "Issued by Tahsildar for current FY", "is_mandatory": True, "sort_order": 1},
            {"name": "Maharashtra State Domicile Certificate", "description": "Proof of permanent Maharashtra residence", "is_mandatory": True, "sort_order": 2},
            {"name": "CAP Allotment Letter & College Fee Receipt", "description": "Proof of merit seat admission", "is_mandatory": True, "sort_order": 3}
        ],
        "rules": [
            {"code": "R1", "field": "is_maharashtra_domicile", "operator": "eq", "value": True, "description": "Resident of Maharashtra", "is_mandatory": True, "sort_order": 1},
            {"code": "R2", "field": "annual_household_income_inr", "operator": "lte", "value": 800000, "description": "Family income not exceeding ₹8,00,000", "is_mandatory": True, "sort_order": 2},
            {"code": "R3", "field": "caste_category", "operator": "in", "value": ["GENERAL", "OPEN", "EWS"], "description": "Open / General / EWS category", "is_mandatory": True, "sort_order": 3}
        ]
    },
    {
        "code": "SAMPLE-PM-AWAS-GRAMIN",
        "name": "[SAMPLE] Pradhan Mantri Awaas Yojana - Gramin (PMAY-G)",
        "name_marathi": "[नमुना] प्रधानमंत्री आवास योजना - ग्रामीण",
        "category": "HOUSING",
        "jurisdiction": "CENTRAL",
        "state": "",
        "department": "Ministry of Rural Development, Govt of India",
        "statutory_gr": "PMAY-G Operational Guidelines 2016",
        "official_portal_url": "https://pmayg.nic.in/",
        "official_source_url": "https://pmayg.nic.in/",
        "portal_name": "AwaasSoft Portal",
        "benefit_type": "MAINTENANCE_STIPEND",
        "benefit_amount_text": "₹1,20,000 financial grant for pucca house construction in plain areas",
        "estimated_annual_value": 120000,
        "brief_description": "Housing grant provided in 3 installments to rural homeless or families living in kutcha/dilapidated houses.",
        "is_sample": True,
        "verification_status": "UNVERIFIED",
        "application_deadline": None,
        "application_steps": [
            "Inclusion verified via Gram Sabha SECC list or Awaas+ survey.",
            "Geo-tagging of existing kutcha site by Gram Sevak.",
            "Direct installment disbursement tied to construction stages (plinth, lintel, roof)."
        ],
        "eligibility_criteria": {
            "clauses": [
                {
                    "id": "income_cap_180k",
                    "description": "Annual family income must not exceed ₹1,80,000 for rural housing deprivation",
                    "source_ref": "PMAY-G Operational Guidelines 2016",
                    "mandatory": True,
                    "field": "annual_household_income_inr",
                    "op": "lte",
                    "value": 180000,
                    "remedy": {
                        "text": "Applicant family must be listed under SECC 2011 deprivation criteria or Awaas+ list.",
                        "source_ref": "PMAY-G Operational Guidelines 2016"
                    }
                },
                {
                    "id": "household_size_min_1",
                    "description": "Household must have at least one family member",
                    "source_ref": "PMAY-G Operational Guidelines 2016",
                    "mandatory": True,
                    "field": "household_size",
                    "op": "gte",
                    "value": 1
                }
            ]
        },
        "documents": [
            {"name": "Gram Panchayat Residence Proof & Land Title", "description": "Proof of land for house construction", "is_mandatory": True, "sort_order": 1},
            {"name": "Aadhaar Card of Head of Household & Spouse", "description": "Joint ownership identity proof", "is_mandatory": True, "sort_order": 2},
            {"name": "BPL / SECC Deprivation Certificate", "description": "Proof of housing deprivation", "is_mandatory": True, "sort_order": 3}
        ],
        "rules": [
            {"code": "R1", "field": "annual_household_income_inr", "operator": "lte", "value": 180000, "description": "Family income <= ₹1,80,000", "is_mandatory": True, "sort_order": 1},
            {"code": "R2", "field": "household_size", "operator": "gte", "value": 1, "description": "At least one member in household", "is_mandatory": True, "sort_order": 2}
        ]
    },
    {
        "code": "SAMPLE-MH-SANJAY-GANDHI",
        "name": "[SAMPLE] Sanjay Gandhi Niradhar Anudan Yojana",
        "name_marathi": "[नमुना] संजय गांधी निराधार अनुदान योजना",
        "category": "OTHER",
        "jurisdiction": "STATE",
        "state": "Maharashtra",
        "department": "Social Justice and Special Assistance Department, Maharashtra",
        "statutory_gr": "Social Justice Dept Resolution No. SGS-2019/C.R.44/MVK-3",
        "official_portal_url": "https://sjsa.maharashtra.gov.in/",
        "official_source_url": "https://sjsa.maharashtra.gov.in/",
        "portal_name": "Aaple Sarkar / Collector Office",
        "benefit_type": "MAINTENANCE_STIPEND",
        "benefit_amount_text": "₹1,500 per month pension for destitute, disabled or widowed citizens",
        "estimated_annual_value": 18000,
        "brief_description": "Monthly pension support for destitute persons, blind/physically handicapped persons (40%+), widows, or abandoned women.",
        "is_sample": True,
        "verification_status": "UNVERIFIED",
        "application_deadline": None,
        "application_steps": [
            "Collect application form from Tahsildar office / Nayab Tahsildar.",
            "Attach medical disability certificate or death certificate of spouse.",
            "Tahsildar Scrutiny Committee reviews and sanctions monthly pension."
        ],
        "eligibility_criteria": {
            "clauses": [
                {
                    "id": "mh_domicile",
                    "description": "Must have resided in Maharashtra for at least 15 years",
                    "source_ref": "Social Justice Dept Resolution No. SGS-2019/C.R.44/MVK-3",
                    "mandatory": True,
                    "field": "is_maharashtra_domicile",
                    "op": "eq",
                    "value": True,
                    "remedy": {
                        "text": "Submit 15-year Maharashtra residence/domicile proof from Tahsildar.",
                        "source_ref": "Resolution No. SGS-2019/C.R.44/MVK-3"
                    }
                },
                {
                    "id": "destitute_income_cap_21k",
                    "description": "Annual household income must not exceed ₹21,000",
                    "source_ref": "Social Justice Dept Resolution No. SGS-2019/C.R.44/MVK-3",
                    "mandatory": True,
                    "field": "annual_household_income_inr",
                    "op": "lte",
                    "value": 21000,
                    "remedy": {
                        "text": "Income certificate issued by Tahsildar certifying destitute status (annual income <= ₹21,000).",
                        "source_ref": "Resolution No. SGS-2019/C.R.44/MVK-3"
                    }
                }
            ]
        },
        "documents": [
            {"name": "Annual Family Income Certificate (<= ₹21,000)", "description": "Strict income ceiling verified by Tahsildar", "is_mandatory": True, "sort_order": 1},
            {"name": "15 Years Maharashtra Domicile Proof", "description": "Continuous residence certificate", "is_mandatory": True, "sort_order": 2},
            {"name": "Civil Surgeon Disability Certificate (>= 40%) or Death Cert", "description": "Medical disability or widow proof", "is_mandatory": True, "sort_order": 3}
        ],
        "rules": [
            {"code": "R1", "field": "is_maharashtra_domicile", "operator": "eq", "value": True, "description": "Resident of Maharashtra", "is_mandatory": True, "sort_order": 1},
            {"code": "R2", "field": "annual_household_income_inr", "operator": "lte", "value": 21000, "description": "Annual family income not exceeding ₹21,000", "is_mandatory": True, "sort_order": 2}
        ]
    },
    {
        "code": "SAMPLE-MJPJAY-HEALTH",
        "name": "[SAMPLE] Mahatma Jyotirao Phule Jan Arogya Yojana (MJPJAY)",
        "name_marathi": "[नमुना] महात्मा ज्योतिराव फुले जन आरोग्य योजना",
        "category": "HEALTH",
        "jurisdiction": "STATE",
        "state": "Maharashtra",
        "department": "Public Health Department, Maharashtra",
        "statutory_gr": "Public Health Dept GR No. MJPJAY-2023/C.R.108/Health-6",
        "official_portal_url": "https://www.jeevandayee.gov.in/",
        "official_source_url": "https://www.jeevandayee.gov.in/",
        "portal_name": "State Health Assurance Society Portal",
        "benefit_type": "TUITION_FEE_WAIVER",
        "benefit_amount_text": "Cashless health insurance cover up to ₹5,00,000 per family per year",
        "estimated_annual_value": 500000,
        "brief_description": "Cashless hospitalization coverage for 1,356 medical and surgical procedures across empanelled network hospitals in Maharashtra.",
        "is_sample": True,
        "verification_status": "UNVERIFIED",
        "application_deadline": None,
        "application_steps": [
            "Approach Aarogyamitra helpdesk at any network hospital with valid ration card.",
            "Aarogyamitra checks e-card eligibility on portal.",
            "Pre-authorization approved within 12 hours for cashless admission."
        ],
        "eligibility_criteria": {
            "clauses": [
                {
                    "id": "mh_domicile",
                    "description": "Beneficiary family must reside in Maharashtra",
                    "source_ref": "Public Health Dept GR No. MJPJAY-2023/C.R.108/Health-6",
                    "mandatory": True,
                    "field": "is_maharashtra_domicile",
                    "op": "eq",
                    "value": True,
                    "remedy": {
                        "text": "Beneficiary must hold a valid Maharashtra Ration Card (Yellow/Orange) or Domicile.",
                        "source_ref": "GR No. MJPJAY-2023/C.R.108/Health-6"
                    }
                },
                {
                    "id": "income_cap_150k",
                    "description": "Annual family income must not exceed ₹1,50,000",
                    "source_ref": "Public Health Dept GR No. MJPJAY-2023/C.R.108/Health-6",
                    "mandatory": True,
                    "field": "annual_household_income_inr",
                    "op": "lte",
                    "value": 150000,
                    "remedy": {
                        "text": "Yellow (AAY) or Orange (BPL) Ration Card or Tahsildar Income Certificate required.",
                        "source_ref": "GR No. MJPJAY-2023/C.R.108/Health-6"
                    }
                }
            ]
        },
        "documents": [
            {"name": "Yellow (AAY) or Orange (BPL) Ration Card", "description": "Proof of beneficiary household status", "is_mandatory": True, "sort_order": 1},
            {"name": "Aadhaar Card or Photo Voter ID", "description": "Patient identity verification", "is_mandatory": True, "sort_order": 2}
        ],
        "rules": [
            {"code": "R1", "field": "is_maharashtra_domicile", "operator": "eq", "value": True, "description": "Resident of Maharashtra", "is_mandatory": True, "sort_order": 1},
            {"code": "R2", "field": "annual_household_income_inr", "operator": "lte", "value": 150000, "description": "Annual household income <= ₹1,50,000", "is_mandatory": True, "sort_order": 2}
        ]
    },
    {
        "code": "SAMPLE-MH-MAHADBT-OBC",
        "name": "[SAMPLE] Post-Matric Scholarship for OBC Students (MahaDBT)",
        "name_marathi": "[नमुना] इतर मागासवर्गीय मॅट्रिकोत्तर शिष्यवृत्ती",
        "category": "EDUCATION",
        "jurisdiction": "STATE",
        "state": "Maharashtra",
        "department": "VJNT, OBC and SBC Welfare Department, Maharashtra",
        "statutory_gr": "GR No. CBC-2006/C.R.55/MVK-5",
        "official_portal_url": "https://mahadbt.maharashtra.gov.in/",
        "official_source_url": "https://mahadbt.maharashtra.gov.in/",
        "portal_name": "MahaDBT",
        "benefit_type": "TUITION_FEE_WAIVER",
        "benefit_amount_text": "100% Tuition Fee (Income <= ₹1L) or 50% Tuition Waiver (Income ₹1L-₹1.5L)",
        "estimated_annual_value": 40000,
        "brief_description": "Tuition and exam fee reimbursement plus monthly stipend for OBC students in higher and technical courses.",
        "is_sample": True,
        "verification_status": "UNVERIFIED",
        "application_deadline": datetime.date(2027, 2, 28),
        "application_steps": [
            "Register on MahaDBT portal with Aadhaar number.",
            "Fill OBC category profile and upload valid Non-Creamy Layer (NCL) certificate.",
            "Submit online application before college scrutiny cut-off."
        ],
        "eligibility_criteria": {
            "clauses": [
                {
                    "id": "mh_domicile",
                    "description": "Student must be a Maharashtra domicile resident",
                    "source_ref": "GR No. CBC-2006/C.R.55/MVK-5",
                    "mandatory": True,
                    "field": "is_maharashtra_domicile",
                    "op": "eq",
                    "value": True,
                    "remedy": {
                        "text": "Obtain Domicile Certificate from Tahsildar / Aaple Sarkar.",
                        "source_ref": "GR No. CBC-2006/C.R.55/MVK-5"
                    }
                },
                {
                    "id": "caste_obc_sbc",
                    "description": "Applicant must belong to OBC or SBC category",
                    "source_ref": "GR No. CBC-2006/C.R.55/MVK-5",
                    "mandatory": True,
                    "field": "caste_category",
                    "op": "in",
                    "value": ["OBC", "SBC"],
                    "remedy": {
                        "text": "Provide valid Caste Certificate and Non-Creamy Layer (NCL) certificate issued by Competent Authority.",
                        "source_ref": "GR No. CBC-2006/C.R.55/MVK-5"
                    }
                },
                {
                    "id": "income_cap_150k",
                    "description": "Annual household income must not exceed ₹1,50,000 for 100% scholarship",
                    "source_ref": "GR No. CBC-2006/C.R.55/MVK-5",
                    "mandatory": True,
                    "field": "annual_household_income_inr",
                    "op": "lte",
                    "value": 150000,
                    "remedy": {
                        "text": "For income between ₹1,50,000 and ₹8,00,000, check the 50% Tuition Fee Waiver (Freeship) scheme on MahaDBT.",
                        "source_ref": "GR No. CBC-2006/C.R.55/MVK-5"
                    }
                },
                {
                    "id": "has_student_enrolled",
                    "description": "Household must have an enrolled student member",
                    "source_ref": "GR No. CBC-2006/C.R.55/MVK-5",
                    "mandatory": True,
                    "field": "has_student_member",
                    "op": "eq",
                    "value": True,
                    "remedy": {
                        "text": "Applicant must be enrolled in an approved post-matric diploma or degree course.",
                        "source_ref": "GR No. CBC-2006/C.R.55/MVK-5"
                    }
                }
            ]
        },
        "documents": [
            {"name": "Caste Certificate (OBC Category)", "description": "Issued by Competent Authority / SDO", "is_mandatory": True, "sort_order": 1},
            {"name": "Non-Creamy Layer (NCL) Certificate", "description": "Valid for current financial year", "is_mandatory": True, "sort_order": 2},
            {"name": "Tahsildar Income Certificate (<= ₹1.5 Lakhs)", "description": "Family income proof", "is_mandatory": True, "sort_order": 3}
        ],
        "rules": [
            {"code": "R1", "field": "is_maharashtra_domicile", "operator": "eq", "value": True, "description": "Resident of Maharashtra", "is_mandatory": True, "sort_order": 1},
            {"code": "R2", "field": "caste_category", "operator": "in", "value": ["OBC", "SBC"], "description": "Belongs to OBC or SBC", "is_mandatory": True, "sort_order": 2},
            {"code": "R3", "field": "annual_household_income_inr", "operator": "lte", "value": 150000, "description": "Income not exceeding ₹1,50,000", "is_mandatory": True, "sort_order": 3}
        ]
    },
    {
        "code": "SAMPLE-MH-SWADHAR",
        "name": "[SAMPLE] Dr. Babasaheb Ambedkar Swadhar Yojana",
        "name_marathi": "[नमुना] डॉ. बाबासाहेब आंबेडकर स्वाधार योजना",
        "category": "EDUCATION",
        "jurisdiction": "STATE",
        "state": "Maharashtra",
        "department": "Social Justice and Special Assistance Department, Maharashtra",
        "statutory_gr": "GR No. EBC-2016/C.R.221/Edu-1",
        "official_portal_url": "https://sjsa.maharashtra.gov.in/",
        "official_source_url": "https://sjsa.maharashtra.gov.in/",
        "portal_name": "Social Justice Department Portal",
        "benefit_type": "LODGING_BOARDING",
        "benefit_amount_text": "₹51,000 per year directly to Student Bank Account for living & hostel",
        "estimated_annual_value": 51000,
        "brief_description": "Financial assistance for SC students who could not get admission into government hostels and stay in private rental accommodations.",
        "is_sample": True,
        "verification_status": "UNVERIFIED",
        "application_deadline": datetime.date(2027, 2, 15),
        "application_steps": [
            "Apply via Assistant Commissioner, Social Welfare district office.",
            "Attach proof of non-allotment of government hostel and rental agreement.",
            "Direct credit sanctioned directly into student's Aadhaar-linked account."
        ],
        "eligibility_criteria": {
            "clauses": [
                {
                    "id": "mh_domicile",
                    "description": "Student must be a Maharashtra domicile resident",
                    "source_ref": "GR No. EBC-2016/C.R.221/Edu-1",
                    "mandatory": True,
                    "field": "is_maharashtra_domicile",
                    "op": "eq",
                    "value": True,
                    "remedy": {
                        "text": "Obtain Domicile Certificate from Tahsildar / Aaple Sarkar.",
                        "source_ref": "GR No. EBC-2016/C.R.221/Edu-1"
                    }
                },
                {
                    "id": "caste_sc",
                    "description": "Applicant must belong to Scheduled Caste (SC) category",
                    "source_ref": "GR No. EBC-2016/C.R.221/Edu-1",
                    "mandatory": True,
                    "field": "caste_category",
                    "op": "eq",
                    "value": "SC",
                    "remedy": {
                        "text": "Provide SC Caste Certificate and Caste Validity Certificate from District Scrutiny Committee.",
                        "source_ref": "GR No. EBC-2016/C.R.221/Edu-1"
                    }
                },
                {
                    "id": "income_cap_250k",
                    "description": "Annual household income must not exceed ₹2,50,000",
                    "source_ref": "GR No. EBC-2016/C.R.221/Edu-1",
                    "mandatory": True,
                    "field": "annual_household_income_inr",
                    "op": "lte",
                    "value": 250000,
                    "remedy": {
                        "text": "Submit Tahsildar Income Certificate proving annual family income <= ₹2.5 Lakhs.",
                        "source_ref": "GR No. EBC-2016/C.R.221/Edu-1"
                    }
                },
                {
                    "id": "has_student_enrolled",
                    "description": "Household must have an enrolled student member",
                    "source_ref": "GR No. EBC-2016/C.R.221/Edu-1",
                    "mandatory": True,
                    "field": "has_student_member",
                    "op": "eq",
                    "value": True,
                    "remedy": {
                        "text": "Applicant must be a student enrolled in higher professional education and staying in non-hostel rented premises.",
                        "source_ref": "GR No. EBC-2016/C.R.221/Edu-1"
                    }
                }
            ]
        },
        "documents": [
            {"name": "Caste Certificate & Caste Validity", "description": "SC community certificate", "is_mandatory": True, "sort_order": 1},
            {"name": "Registered Rent Agreement / Private Hostel Certificate", "description": "Proof of staying in private accommodation", "is_mandatory": True, "sort_order": 2},
            {"name": "Tahsildar Income Certificate (<= ₹2.5 Lakhs)", "description": "Income proof", "is_mandatory": True, "sort_order": 3}
        ],
        "rules": [
            {"code": "R1", "field": "is_maharashtra_domicile", "operator": "eq", "value": True, "description": "Resident of Maharashtra", "is_mandatory": True, "sort_order": 1},
            {"code": "R2", "field": "caste_category", "operator": "eq", "value": "SC", "description": "Scheduled Caste (SC) category", "is_mandatory": True, "sort_order": 2},
            {"code": "R3", "field": "annual_household_income_inr", "operator": "lte", "value": 250000, "description": "Income ceiling of ₹2.5 Lakhs", "is_mandatory": True, "sort_order": 3}
        ]
    },
    {
        "code": "SAMPLE-ATAL-PENSION",
        "name": "[SAMPLE] Atal Pension Yojana (APY)",
        "name_marathi": "[नमुना] अटल पेन्शन योजना",
        "category": "OTHER",
        "jurisdiction": "CENTRAL",
        "state": "",
        "department": "Pension Fund Regulatory and Development Authority (PFRDA)",
        "statutory_gr": "PFRDA APY Guidelines 2015",
        "official_portal_url": "https://www.npscra.nsdl.co.in/",
        "official_source_url": "https://www.npscra.nsdl.co.in/",
        "portal_name": "Protean / NSDL CRA",
        "benefit_type": "MAINTENANCE_STIPEND",
        "benefit_amount_text": "Guaranteed monthly pension of ₹1,000 to ₹5,000 from age 60",
        "estimated_annual_value": 36000,
        "brief_description": "Government-guaranteed pension scheme primarily focused on unorganized sector workers.",
        "is_sample": True,
        "verification_status": "UNVERIFIED",
        "application_deadline": None,
        "application_steps": [
            "Visit bank branch where savings account is held or use net banking.",
            "Choose monthly pension amount (₹1,000 to ₹5,000).",
            "Auto-debit mandate setup from savings account."
        ],
        "eligibility_criteria": {
            "clauses": [
                {
                    "id": "age_min_18",
                    "description": "Minimum subscriber age is 18 years",
                    "source_ref": "PFRDA APY Guidelines 2015",
                    "mandatory": True,
                    "field": "age_years",
                    "op": "gte",
                    "value": 18,
                    "remedy": {
                        "text": "Subscriber must be at least 18 years old to join APY.",
                        "source_ref": "PFRDA APY Guidelines 2015"
                    }
                },
                {
                    "id": "age_max_40",
                    "description": "Maximum subscriber age is 40 years",
                    "source_ref": "PFRDA APY Guidelines 2015",
                    "mandatory": True,
                    "field": "age_years",
                    "op": "lte",
                    "value": 40,
                    "remedy": {
                        "text": "Citizens above 40 cannot join APY. Check National Pension System (NPS) All Citizen model.",
                        "source_ref": "PFRDA NPS Guidelines"
                    }
                }
            ]
        },
        "documents": [
            {"name": "Bank Savings Account Passbook", "description": "Savings account with auto-debit facility", "is_mandatory": True, "sort_order": 1},
            {"name": "Aadhaar Card", "description": "Identity and subscriber KYC verification", "is_mandatory": True, "sort_order": 2}
        ],
        "rules": [
            {"code": "R1", "field": "age_years", "operator": "gte", "value": 18, "description": "Minimum joining age 18", "is_mandatory": True, "sort_order": 1},
            {"code": "R2", "field": "age_years", "operator": "lte", "value": 40, "description": "Maximum joining age 40", "is_mandatory": True, "sort_order": 2}
        ]
    },
    {
        "code": "SAMPLE-SUKANYA-SAMRIDDHI",
        "name": "[SAMPLE] Sukanya Samriddhi Yojana (Beti Bachao Beti Padhao)",
        "name_marathi": "[नमुना] सुकन्या समृद्धी योजना",
        "category": "WOMEN_CHILD",
        "jurisdiction": "CENTRAL",
        "state": "",
        "department": "Ministry of Finance, Govt of India",
        "statutory_gr": "Sukanya Samriddhi Account Rules 2016 / 2019",
        "official_portal_url": "https://www.indiapost.gov.in/",
        "official_source_url": "https://www.indiapost.gov.in/",
        "portal_name": "India Post / Authorized Commercial Banks",
        "benefit_type": "BOOK_STATIONERY",
        "benefit_amount_text": "High-interest savings account (8.2% p.a.) with full tax exemption under Sec 80C",
        "estimated_annual_value": 25000,
        "brief_description": "Small deposit savings scheme for girl child education and marriage expenses.",
        "is_sample": True,
        "verification_status": "UNVERIFIED",
        "application_deadline": None,
        "application_steps": [
            "Visit nearest Post Office or authorized commercial bank branch.",
            "Submit Account Opening Form (SSA-1) with birth certificate of girl child.",
            "Deposit initial minimum amount of ₹250."
        ],
        "eligibility_criteria": {
            "clauses": [
                {
                    "id": "age_child_max_10",
                    "description": "Girl child age must be 10 years or younger at account opening",
                    "source_ref": "Sukanya Samriddhi Account Rules 2016",
                    "mandatory": True,
                    "field": "age_years",
                    "op": "lte",
                    "value": 10,
                    "remedy": {
                        "text": "Account can only be opened for girl children up to age 10 with authorized birth certificate.",
                        "source_ref": "Sukanya Samriddhi Account Rules 2016"
                    }
                },
                {
                    "id": "household_size_min_1",
                    "description": "Household must have at least one member",
                    "source_ref": "Sukanya Samriddhi Account Rules 2016",
                    "mandatory": True,
                    "field": "household_size",
                    "op": "gte",
                    "value": 1
                }
            ]
        },
        "documents": [
            {"name": "Birth Certificate of Girl Child", "description": "Mandatory age proof", "is_mandatory": True, "sort_order": 1},
            {"name": "Aadhaar / Identity Proof of Parent/Guardian", "description": "KYC proof of legal guardian", "is_mandatory": True, "sort_order": 2}
        ],
        "rules": [
            {"code": "R1", "field": "age_years", "operator": "lte", "value": 10, "description": "Account must be opened before age 10", "is_mandatory": True, "sort_order": 1},
            {"code": "R2", "field": "household_size", "operator": "gte", "value": 1, "description": "Household member count >= 1", "is_mandatory": True, "sort_order": 2}
        ]
    }
]

class Command(BaseCommand):
    help = "Seed 10 clearly labelled sample schemes with structured criteria and documents. Idempotent; never overwrites verified records."

    def handle(self, *args, **options):
        self.stdout.write("Seeding Phase 1 & 2 sample schemes with eligibility criteria...")
        created_count = 0
        updated_count = 0
        skipped_count = 0

        for raw_item in SAMPLE_SCHEMES_DATA:
            item = copy.deepcopy(raw_item)
            code = item["code"]
            existing = Scheme.objects.filter(code=code).first()

            if existing and existing.verification_status == "VERIFIED":
                self.stdout.write(self.style.WARNING(f"Skipping {code}: Already marked VERIFIED. Verified records are never overwritten."))
                skipped_count += 1
                continue

            documents = item.pop("documents", [])
            flat_rules = item.pop("rules", [])
            if "rules" not in item:
                item["rules"] = {"operator": "ALL", "conditions": []}

            with transaction.atomic():
                scheme, created = Scheme.objects.update_or_create(
                    code=code,
                    defaults=item
                )
                scheme.clean()
                scheme.save()

                # Sync RequiredDocuments
                scheme.required_documents.all().delete()
                for doc_data in documents:
                    doc = RequiredDocument(scheme=scheme, **doc_data)
                    doc.full_clean()
                    doc.save()

                # Sync EligibilityRules
                scheme.eligibility_rules.all().delete()
                for rule_data in flat_rules:
                    rule = EligibilityRule(scheme=scheme, **rule_data)
                    rule.full_clean()
                    rule.save()

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Successfully finished seeding: {created_count} created, {updated_count} updated, {skipped_count} skipped."
        ))
