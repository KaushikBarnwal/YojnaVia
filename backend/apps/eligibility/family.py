"""
Family-Level Benefits Discovery and Optimization Engine.
Evaluates schemes across all household members (student, farmer parent, mother, elderly grandparent),
combines individual entitlements with family-wide social safety nets (MJPJAY Health, PM Awaas),
and computes the cumulative household economic benefit.
"""

from typing import Dict, Any, List
from decimal import Decimal
from apps.schemes.models import Scheme
from apps.profiles.models import StudentProfile


HOUSEHOLD_PERSONAS = {
    "rohan_obc": {
        "family_name": "Gaikwad Family",
        "district": "Sangli, Maharashtra",
        "category": "OBC (Kunbi)",
        "total_annual_income": 110000,
        "ration_card": "Orange (BPL)",
        "members": [
            {
                "id": "mem_rohan",
                "name": "Rohan Gaikwad",
                "relation": "Self (Applicant)",
                "role": "STUDENT",
                "age": 20,
                "gender": "MALE",
                "details": "B.Tech Mechanical Engineering, Govt. College, Living in private hostel",
                "matched_schemes": [
                    {
                        "code": "MH_OBC_POSTMATRIC_2024",
                        "name": "Post-Matric Scholarship for OBC Students",
                        "department": "Other Backward Class Bahujan Welfare Department",
                        "benefit_text": "50% Tuition Fee Reimbursement + Exam Fees",
                        "annual_value": 55000,
                        "statutory_gr": "GR No. OBC-2024/CR-78/BCW-2",
                        "status": "LIKELY_ELIGIBLE"
                    },
                    {
                        "code": "MH_PANJABRAO_HOSTEL_2024",
                        "name": "Dr. Panjabrao Deshmukh Hostel Maintenance Allowance",
                        "department": "Higher & Technical Education Department",
                        "benefit_text": "₹30,000/yr Hostel Maintenance Cash Allowance",
                        "annual_value": 30000,
                        "statutory_gr": "GR No. TEM-2023/CR-92/TE-4",
                        "status": "LIKELY_ELIGIBLE"
                    }
                ],
                "subtotal_annual_benefit": 85000
            },
            {
                "id": "mem_father",
                "name": "Ramesh Gaikwad",
                "relation": "Father",
                "role": "FARMER",
                "age": 52,
                "gender": "MALE",
                "details": "Small & Marginal Farmer, 2.2 acres dryland holding, Sangli",
                "matched_schemes": [
                    {
                        "code": "SAMPLE-PM-KISAN",
                        "name": "PM Kisan Samman Nidhi Yojana",
                        "department": "Ministry of Agriculture & Farmers Welfare, GoI",
                        "benefit_text": "₹6,000 Direct Cash Transfer (3 installments of ₹2,000)",
                        "annual_value": 6000,
                        "statutory_gr": "Govt of India Operational Guidelines 2019",
                        "status": "LIKELY_ELIGIBLE"
                    },
                    {
                        "code": "MH_NAMO_SHETKARI_2024",
                        "name": "Namo Shetkari Mahasanman Nidhi Yojana",
                        "department": "Agriculture Department, Govt of Maharashtra",
                        "benefit_text": "₹6,000 Top-up Cash Support for Maharashtra PM-Kisan Beneficiaries",
                        "annual_value": 6000,
                        "statutory_gr": "GR No. KISAN-2023/CR-14/Agri-4",
                        "status": "LIKELY_ELIGIBLE"
                    }
                ],
                "subtotal_annual_benefit": 12000
            },
            {
                "id": "mem_mother",
                "name": "Sunita Gaikwad",
                "relation": "Mother",
                "role": "WOMAN_HOMEMAKER",
                "age": 48,
                "gender": "FEMALE",
                "details": "Self-Help Group (Bachat Gat) Member, Small Dairy Activity",
                "matched_schemes": [
                    {
                        "code": "SAMPLE-MH-LADKI-BAHIN",
                        "name": "Mukhyamantri Majhi Ladki Bahin Yojana",
                        "department": "Women & Child Development Department, Govt of Maharashtra",
                        "benefit_text": "₹1,500/month DBT Cash Support (₹18,000 per annum)",
                        "annual_value": 18000,
                        "statutory_gr": "GR No. WCD-2024/CR-189/W-1",
                        "status": "LIKELY_ELIGIBLE"
                    }
                ],
                "subtotal_annual_benefit": 18000
            },
            {
                "id": "mem_sibling",
                "name": "Aniket Gaikwad",
                "relation": "Younger Brother",
                "role": "SCHOOL_STUDENT",
                "age": 16,
                "gender": "MALE",
                "details": "11th Science Junior College, Zilla Parishad School",
                "matched_schemes": [
                    {
                        "code": "MH_OBC_PREMATRIC_2024",
                        "name": "Government of Maharashtra Junior College Book Allowance & Exam Waiver",
                        "department": "School Education & Sports Department",
                        "benefit_text": "Free Textbooks, Uniform Allowance & Exam Fee Waiver",
                        "annual_value": 6000,
                        "statutory_gr": "GR No. PRE-2022/CR-44/SE",
                        "status": "LIKELY_ELIGIBLE"
                    }
                ],
                "subtotal_annual_benefit": 6000
            }
        ],
        "shared_household_schemes": [
            {
                "code": "SAMPLE-MJPJAY-HEALTH",
                "name": "Mahatma Jyotirao Phule Jan Arogya Yojana (MJPJAY 2.0)",
                "department": "Public Health Department, Govt of Maharashtra",
                "coverage_type": "CASHLESS_HEALTH_INSURANCE",
                "benefit_text": "₹5,00,000 Comprehensive Cashless Hospitalization Cover for Entire Household",
                "statutory_gr": "GR No. MJPJAY-2023/CR-112/PHD-3",
                "status": "AUTOMATICALLY_QUALIFIED"
            }
        ]
    },
    "sneha_ebc": {
        "family_name": "Kulkarni Family",
        "district": "Nashik, Maharashtra",
        "category": "Open / EWS (Maratha)",
        "total_annual_income": 320000,
        "ration_card": "White / Tri-color",
        "members": [
            {
                "id": "mem_sneha",
                "name": "Sneha Kulkarni",
                "relation": "Self (Applicant)",
                "role": "STUDENT",
                "age": 19,
                "gender": "FEMALE",
                "details": "Bachelor of Pharmacy (B.Pharm), Admitted via CAP Merit",
                "matched_schemes": [
                    {
                        "code": "MH_DTE_EBC_2024",
                        "name": "Rajarshi Chhatrapati Shahu Maharaj Shikshan Shulkh Shishyavrutti (EBC)",
                        "department": "Directorate of Technical Education (DTE), Maharashtra",
                        "benefit_text": "50% Tuition Fee & Exam Fee Waiver",
                        "annual_value": 45000,
                        "statutory_gr": "GR No. TEM-2018/CR-363/TE-4",
                        "status": "LIKELY_ELIGIBLE"
                    }
                ],
                "subtotal_annual_benefit": 45000
            },
            {
                "id": "mem_mother",
                "name": "Radha Kulkarni",
                "relation": "Mother",
                "role": "WOMAN_HOMEMAKER",
                "age": 46,
                "gender": "FEMALE",
                "details": "Maharashtra Resident Domicile, Family income under ₹8 Lakh cap",
                "matched_schemes": [
                    {
                        "code": "SAMPLE-MH-LADKI-BAHIN",
                        "name": "Mukhyamantri Majhi Ladki Bahin Yojana",
                        "department": "Women & Child Development Department",
                        "benefit_text": "₹1,500/month Direct Cash Transfer (₹18,000/yr)",
                        "annual_value": 18000,
                        "statutory_gr": "GR No. WCD-2024/CR-189/W-1",
                        "status": "LIKELY_ELIGIBLE"
                    }
                ],
                "subtotal_annual_benefit": 18000
            }
        ],
        "shared_household_schemes": [
            {
                "code": "SAMPLE-MJPJAY-HEALTH",
                "name": "Mahatma Jyotirao Phule Jan Arogya Yojana (Universal Cover)",
                "department": "Public Health Department, Govt of Maharashtra",
                "coverage_type": "CASHLESS_HEALTH_INSURANCE",
                "benefit_text": "₹5,00,000 Family Cashless Hospitalization Coverage across 1,356 procedures",
                "statutory_gr": "GR No. MJPJAY-2023/CR-112/PHD-3",
                "status": "AUTOMATICALLY_QUALIFIED"
            }
        ]
    },
    "vikas_sc": {
        "family_name": "Kamble Family",
        "district": "Solapur, Maharashtra",
        "category": "Scheduled Caste (SC - Navboudha)",
        "total_annual_income": 65000,
        "ration_card": "Yellow (Antyodaya Anna Yojana)",
        "members": [
            {
                "id": "mem_vikas",
                "name": "Vikas Kamble",
                "relation": "Self (Applicant)",
                "role": "STUDENT",
                "age": 18,
                "gender": "MALE",
                "details": "Diploma in Civil Engineering, Govt Polytechnic Solapur",
                "matched_schemes": [
                    {
                        "code": "MH_SC_POSTMATRIC_2024",
                        "name": "Government of India Post-Matric Scholarship for SC Students",
                        "department": "Social Justice and Special Assistance Department",
                        "benefit_text": "100% Tuition & Exam Fee Waiver + Monthly Maintenance Allowance",
                        "annual_value": 35000,
                        "statutory_gr": "GR No. BCM-2022/CR-89/BCW-5",
                        "status": "LIKELY_ELIGIBLE"
                    },
                    {
                        "code": "MH_SWADHAR_SC_2024",
                        "name": "Dr. Babasaheb Ambedkar Swadhar Scheme",
                        "department": "Social Justice and Special Assistance Department",
                        "benefit_text": "₹51,000/yr Direct Cash for Food, Lodging & Transport",
                        "annual_value": 51000,
                        "statutory_gr": "GR No. EBC-2016/CR-221/Edu-2",
                        "status": "LIKELY_ELIGIBLE"
                    }
                ],
                "subtotal_annual_benefit": 86000
            },
            {
                "id": "mem_mother",
                "name": "Sharda Kamble",
                "relation": "Mother",
                "role": "WOMAN_HOMEMAKER",
                "age": 44,
                "gender": "FEMALE",
                "details": "BPL Card Holder, Tailoring Worker",
                "matched_schemes": [
                    {
                        "code": "SAMPLE-MH-LADKI-BAHIN",
                        "name": "Mukhyamantri Majhi Ladki Bahin Yojana",
                        "department": "Women & Child Development Department",
                        "benefit_text": "₹1,500/month DBT Cash Support (₹18,000 per annum)",
                        "annual_value": 18000,
                        "statutory_gr": "GR No. WCD-2024/CR-189/W-1",
                        "status": "LIKELY_ELIGIBLE"
                    }
                ],
                "subtotal_annual_benefit": 18000
            },
            {
                "id": "mem_grandmother",
                "name": "Kashibai Kamble",
                "relation": "Grandmother",
                "role": "SENIOR_CITIZEN",
                "age": 68,
                "gender": "FEMALE",
                "details": "Senior Citizen, Destitute, Below Poverty Line",
                "matched_schemes": [
                    {
                        "code": "SAMPLE-MH-SANJAY-GANDHI",
                        "name": "Sanjay Gandhi Niradhar Anudan Yojana",
                        "department": "Social Justice & Special Assistance Department",
                        "benefit_text": "₹1,500 Monthly Destitute Elderly Pension (₹18,000/yr)",
                        "annual_value": 18000,
                        "statutory_gr": "GR No. SGY-2023/CR-15/SJ-3",
                        "status": "LIKELY_ELIGIBLE"
                    }
                ],
                "subtotal_annual_benefit": 18000
            }
        ],
        "shared_household_schemes": [
            {
                "code": "SAMPLE-MJPJAY-HEALTH",
                "name": "Mahatma Jyotirao Phule Jan Arogya Yojana",
                "department": "Public Health Department, Govt of Maharashtra",
                "coverage_type": "CASHLESS_HEALTH_INSURANCE",
                "benefit_text": "₹5,00,000 Cashless Health Coverage for Entire Family",
                "statutory_gr": "GR No. MJPJAY-2023/CR-112/PHD-3",
                "status": "AUTOMATICALLY_QUALIFIED"
            }
        ]
    }
}


class FamilyBenefitsService:
    @classmethod
    def get_family_assessment(cls, persona_key: str = "rohan_obc", custom_family_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Returns full family-level benefits breakdown including:
        - Total household financial value unlocked per year
        - Per-member breakdown of entitlement packages
        - Universal / shared household social security benefits (health cover, housing)
        """
        if custom_family_data:
            family_info = custom_family_data
        else:
            family_info = HOUSEHOLD_PERSONAS.get(persona_key, HOUSEHOLD_PERSONAS["rohan_obc"])

        members = family_info.get("members", [])
        shared_schemes = family_info.get("shared_household_schemes", [])

        # Calculate totals
        total_cash_and_fee_benefit = sum(
            sum(s["annual_value"] for s in m.get("matched_schemes", []))
            for m in members
        )

        total_schemes_count = sum(len(m.get("matched_schemes", [])) for m in members) + len(shared_schemes)

        return {
            "family_name": family_info.get("family_name", "Citizen Family"),
            "district": family_info.get("district", "Maharashtra"),
            "category": family_info.get("category", "General"),
            "total_annual_income": family_info.get("total_annual_income", 0),
            "ration_card": family_info.get("ration_card", "Orange BPL"),
            "total_annual_household_benefit_inr": total_cash_and_fee_benefit,
            "total_schemes_unlocked": total_schemes_count,
            "health_insurance_coverage_inr": 500000,
            "members": members,
            "shared_household_schemes": shared_schemes,
            "counsellor_action_notes": [
                "Schedule one single visit to Aaple Sarkar Seva Kendra (CSC) for all family certificates.",
                "Procure the Tahsildar Income Certificate once; it satisfies both Rohan's scholarship and Ramesh's PM-Kisan verification.",
                "Ensure Aadhaar DBT seeding is active on Ramesh's and Sunita's primary bank accounts for instant monthly transfers."
            ]
        }
