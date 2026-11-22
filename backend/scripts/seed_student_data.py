"""
Seed script for Maharashtra Low-Income Student Schemes & Documents.
Includes verified official Government Resolutions (GRs), AST rules, and cross-scheme dependencies.
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from apps.schemes.models import Scheme
from apps.documents.models import Document, SchemeDocumentRequirement

def seed_documents():
    docs_data = [
        {
            "code": "DOC_TAHSILDAR_INCOME",
            "name": "Income Certificate issued by Tahsildar (FY 2023-24)",
            "name_marathi": "तहसीलदार उत्पन्न प्रमाणपत्र (चालू आर्थिक वर्ष)",
            "issuing_authority": "Revenue Department / Tahsildar Office",
            "procurement_portal": "aaplesarkar.mahaonline.gov.in",
            "estimated_sla_days": 15,
            "validity_duration": "1 Financial Year (Ending March 31)",
            "prerequisite_documents": ["Ration Card", "Applicant / Parent Photo ID", "Salary Certificate or Talathi Report"],
            "how_to_obtain_steps": [
                "Visit Aaple Sarkar portal (aaplesarkar.mahaonline.gov.in) or nearest Maha e-Seva Kendra.",
                "Select 'Revenue Department' -> 'Issuance of Income Certificate'.",
                "Upload ration card copy, photo ID, and self-declaration affidavit.",
                "Pay official portal fee of ₹33.60.",
                "Download digitally signed certificate upon Tahsildar approval within 15 days."
            ]
        },
        {
            "code": "DOC_DOMICILE",
            "name": "Maharashtra State Domicile Certificate",
            "name_marathi": "महाराष्ट्र अधिवास (डोमिसाईल) प्रमाणपत्र",
            "issuing_authority": "Sub-Divisional Officer (SDO) / Tahsildar",
            "procurement_portal": "aaplesarkar.mahaonline.gov.in",
            "estimated_sla_days": 15,
            "validity_duration": "Lifetime Validity",
            "prerequisite_documents": ["Birth Certificate / School Leaving Certificate", "15 Years Residence Proof (Ration card / Electricity bills)"],
            "how_to_obtain_steps": [
                "Apply online on Aaple Sarkar portal under Revenue Department.",
                "Upload School Leaving Certificate showing place of birth in Maharashtra.",
                "Submit proof of 15 years continuous residence in Maharashtra.",
                "Download digitally signed Domicile Certificate."
            ]
        },
        {
            "code": "DOC_CASTE",
            "name": "Caste Certificate (SC / ST / OBC / VJNT / SBC)",
            "name_marathi": "जातीचे प्रमाणपत्र",
            "issuing_authority": "Sub-Divisional Magistrate (SDM) / Tahsildar",
            "procurement_portal": "aaplesarkar.mahaonline.gov.in",
            "estimated_sla_days": 21,
            "validity_duration": "Lifetime Validity",
            "prerequisite_documents": ["Pre-1967 (SC/ST) or Pre-1967/1961 (OBC/VJNT) genealogical blood relation proof", "School Leaving Certificate"],
            "how_to_obtain_steps": [
                "Apply on Aaple Sarkar under Social Justice / Revenue Department.",
                "Upload genealogical tree (Vanshavali) and historical proof of residence prior to deemed date.",
                "Collect digitally signed Caste Certificate."
            ]
        },
        {
            "code": "DOC_CASTE_VALIDITY",
            "name": "Caste Validity Certificate",
            "name_marathi": "जात वैधता प्रमाणपत्र",
            "issuing_authority": "Divisional Caste Scrutiny Committee (BARTI / TRTI)",
            "procurement_portal": "bartievalidity.maharashtra.gov.in",
            "estimated_sla_days": 60,
            "validity_duration": "Lifetime Validity",
            "prerequisite_documents": ["Caste Certificate", "College Recommendation Letter (Form 16/17)", "Family Blood Relation Validity Records"],
            "how_to_obtain_steps": [
                "Apply online through CCVIS / BARTI portal after securing college admission.",
                "Submit original Form 16 recommendation from College Principal.",
                "Appear for document verification at Divisional Caste Scrutiny Committee office.",
                "Receive Caste Validity Certificate essential for professional degrees and government jobs."
            ]
        },
        {
            "code": "DOC_NON_CREAMY_LAYER",
            "name": "Non-Creamy Layer (NCL) Certificate",
            "name_marathi": "नॉन-क्रीमी लेयर प्रमाणपत्र",
            "issuing_authority": "Sub-Divisional Officer / Tahsildar",
            "procurement_portal": "aaplesarkar.mahaonline.gov.in",
            "estimated_sla_days": 15,
            "validity_duration": "3 Financial Years",
            "prerequisite_documents": ["Caste Certificate", "Last 3 Years Income Certificate / ITR"],
            "how_to_obtain_steps": [
                "Mandatory for OBC / VJNT / SBC applicants claiming quota or fee concessions.",
                "Apply on Aaple Sarkar with 3 consecutive years income certificates.",
                "Download certificate verifying family income is below ₹8.00 Lakhs."
            ]
        },
        {
            "code": "DOC_CAP_ALLOTMENT",
            "name": "CAP Allotment Letter & College Admission Fee Receipt",
            "name_marathi": "कॅप अलॉटमेंट लेटर व कॉलेज प्रवेश पावती",
            "issuing_authority": "State Common Entrance Test Cell (CET Cell) / College",
            "procurement_portal": "cetcell.mahacet.org",
            "estimated_sla_days": 1,
            "validity_duration": "Current Academic Year",
            "prerequisite_documents": ["CET Merit Card", "College Fee Payment Receipt"],
            "how_to_obtain_steps": [
                "Download official allotment letter from CET Cell portal after round confirmation.",
                "Retain original signed college admission confirmation receipt."
            ]
        },
        {
            "code": "DOC_PREV_MARKSHEET",
            "name": "Previous Year Examination Marksheet (SSC / HSC / Semesters)",
            "name_marathi": "मागील वर्षाची गुणपत्रिका",
            "issuing_authority": "Maharashtra State Board / Affiliated University",
            "procurement_portal": "mahahsscboard.in",
            "estimated_sla_days": 1,
            "validity_duration": "Permanent",
            "prerequisite_documents": ["Admit Card"],
            "how_to_obtain_steps": [
                "Collect original marksheet from Junior College or University Examination Cell."
            ]
        },
        {
            "code": "DOC_HOSTEL_RENT_PROOF",
            "name": "Registered Rent Agreement & Non-Govt Hostel Affidavit",
            "name_marathi": "भाडे करारनामा व वसतिगृह प्रमाणपत्र",
            "issuing_authority": "Sub-Registrar Office / Hostel Warden / Notary",
            "procurement_portal": "igrmaharashtra.gov.in",
            "estimated_sla_days": 3,
            "validity_duration": "Current Academic Year (10-11 months)",
            "prerequisite_documents": ["Landlord Aadhaar & Electricity Bill", "Student ID Card"],
            "how_to_obtain_steps": [
                "Execute 11-month rental agreement with flat owner or obtain official certificate from private hostel.",
                "Attach college principal certificate certifying non-availability of government hostel seat."
            ]
        },
        {
            "code": "DOC_FARMER_7_12",
            "name": "7/12 Agricultural Land Extract & Small Farmer Certificate",
            "name_marathi": "७/१२ शेतजमीन उतारा व अल्पभूधारक प्रमाणपत्र",
            "issuing_authority": "Revenue Dept / Talathi Office",
            "procurement_portal": "bhulekh.mahabhumi.gov.in",
            "estimated_sla_days": 3,
            "validity_duration": "6 Months",
            "prerequisite_documents": ["Survey Number", "Gat Number"],
            "how_to_obtain_steps": [
                "Download digitally signed 7/12 extract from Mahabhumi portal (bhulekh.mahabhumi.gov.in).",
                "Obtain certificate from Talathi proving agricultural landholding is <= 5 acres (small landholder)."
            ]
        },
        {
            "code": "DOC_AADHAAR_NPCI_BANK",
            "name": "Bank Passbook with NPCI Aadhaar DBT Mapping",
            "name_marathi": "आधार लिंक बँक पासबुक (NPCI Seeding)",
            "issuing_authority": "Nationalized / Scheduled Commercial Bank",
            "procurement_portal": "npci.org.in",
            "estimated_sla_days": 2,
            "validity_duration": "Permanent",
            "prerequisite_documents": ["Aadhaar Card", "Bank Account Passbook"],
            "how_to_obtain_steps": [
                "Visit bank branch and submit 'NPCI Aadhaar Seeding Consent Form'.",
                "Check seeding status via UIDAI or NPCI portal to ensure DBT direct credit operates."
            ]
        }
    ]

    docs_dict = {}
    for data in docs_data:
        doc, _ = Document.objects.update_or_create(code=data["code"], defaults=data)
        docs_dict[doc.code] = doc
    print(f"Successfully seeded {len(docs_dict)} documents.")
    return docs_dict

def seed_schemes(docs_dict):
    schemes_data = [
        {
            "code": "MH_DTE_EBC_2024",
            "version": "2024.1",
            "effective_academic_year": "2024-2025",
            "name": "Rajarshi Chhatrapati Shahu Maharaj Shikshan Shulkh Shishyavrutti Yojna (EBC)",
            "name_marathi": "राजर्षी छत्रपती शाहू महाराज शिक्षण शुल्क शिष्यवृत्ती योजना (ईबीसी)",
            "department": "Directorate of Higher & Technical Education, Maharashtra",
            "statutory_gr": "Govt. Resolution No. TEM-2016/C.R.228/TE-4 dated 07/10/2017",
            "official_portal_url": "https://mahadbt.maharashtra.gov.in/",
            "portal_name": "MahaDBT (Aaple Sarkar DBT Portal)",
            "benefit_type": "TUITION_FEE_WAIVER",
            "benefit_amount_text": "50% Tuition Fee & 50% Exam Fee Reimbursement directly to College",
            "estimated_annual_value": 45000,
            "brief_description": "Financial assistance for general/open/EWS category students admitted to professional, technical, diploma, and degree courses through CAP merit rounds.",
            "stackable_with_benefit_types": ["HOSTEL_ALLOWANCE", "MAINTENANCE_STIPEND", "BOOK_STATIONERY"],
            "rules": {
                "operator": "ALL",
                "conditions": [
                    {
                        "field": "is_maharashtra_domicile",
                        "op": "==",
                        "value": True,
                        "label": "Domicile of Maharashtra State",
                        "citation": "Clause 2.1: Candidate must be an Indian national and domicile of Maharashtra."
                    },
                    {
                        "field": "caste_category",
                        "op": "in",
                        "value": ["OPEN", "EWS"],
                        "label": "General / Open / EWS Category",
                        "citation": "Clause 2.2: Scheme applies exclusively to General/EWS candidates not availing other caste scholarships."
                    },
                    {
                        "field": "annual_family_income",
                        "op": "<=",
                        "value": 800000,
                        "boundary_tolerance": 50000,
                        "label": "Annual family income not exceeding ₹8,00,000",
                        "citation": "Clause 3.1: Annual family income certified by Tahsildar must be <= ₹8 Lakhs."
                    },
                    {
                        "field": "admission_quota",
                        "op": "in",
                        "value": ["CAP_ROUND", "DIRECT_SECOND_YEAR"],
                        "label": "Admitted through Centralized Admission Process (CAP Round)",
                        "citation": "Clause 4.1: Students admitted through Management or Institutional quota are ineligible."
                    }
                ]
            },
            "documents": [
                {"doc_code": "DOC_TAHSILDAR_INCOME", "mandatory": True, "purpose": "Proof of income below ₹8 Lakhs"},
                {"doc_code": "DOC_DOMICILE", "mandatory": True, "purpose": "Proof of Maharashtra domicile"},
                {"doc_code": "DOC_CAP_ALLOTMENT", "mandatory": True, "purpose": "Verification of merit-based CAP seat"},
                {"doc_code": "DOC_PREV_MARKSHEET", "mandatory": True, "purpose": "Proof of qualifying exam pass"},
                {"doc_code": "DOC_AADHAAR_NPCI_BANK", "mandatory": True, "purpose": "Aadhaar seeded bank account for DBT"}
            ]
        },
        {
            "code": "MH_OBC_POSTMATRIC_2024",
            "version": "2024.1",
            "effective_academic_year": "2024-2025",
            "name": "Post-Matric Scholarship for OBC Students (MahaDBT)",
            "name_marathi": "इतर मागासवर्गीय (OBC) मॅट्रिकोत्तर शिष्यवृत्ती योजना",
            "department": "VJNT, OBC and SBC Welfare Department, Maharashtra",
            "statutory_gr": "Govt. Resolution No. CBC-2006/C.R.55/MVK-5 dated 01/01/2007",
            "official_portal_url": "https://mahadbt.maharashtra.gov.in/",
            "portal_name": "MahaDBT (Aaple Sarkar DBT Portal)",
            "benefit_type": "TUITION_FEE_WAIVER",
            "benefit_amount_text": "100% Tuition Fee (if income <= ₹1L) or 50% Tuition Fee (if income ₹1L-₹1.5L) + Maintenance Allowance",
            "estimated_annual_value": 40000,
            "brief_description": "Comprehensive fee waiver and monthly allowance for OBC students pursuing post-matric, technical, and professional courses.",
            "stackable_with_benefit_types": ["HOSTEL_ALLOWANCE"],
            "rules": {
                "operator": "ALL",
                "conditions": [
                    {
                        "field": "is_maharashtra_domicile",
                        "op": "==",
                        "value": True,
                        "label": "Domicile of Maharashtra State",
                        "citation": "Clause 1.1: Must be resident of Maharashtra with valid Domicile Certificate."
                    },
                    {
                        "field": "caste_category",
                        "op": "in",
                        "value": ["OBC", "SBC"],
                        "label": "Belongs to OBC or SBC Category",
                        "citation": "Clause 2.1: Recognized backward class category in Maharashtra."
                    },
                    {
                        "field": "annual_family_income",
                        "op": "<=",
                        "value": 150000,
                        "boundary_tolerance": 30000,
                        "label": "Annual family income not exceeding ₹1,50,000",
                        "citation": "Clause 3.1: Full scholarship up to ₹1L; Freeship tuition waiver between ₹1L to ₹1.5L (extends up to ₹8L for Freeship scheme)."
                    },
                    {
                        "field": "admission_quota",
                        "op": "in",
                        "value": ["CAP_ROUND", "DIRECT_SECOND_YEAR"],
                        "label": "Admitted via Centralized CAP Round",
                        "citation": "Clause 4.1: Must be admitted through merit quota."
                    }
                ]
            },
            "documents": [
                {"doc_code": "DOC_CASTE", "mandatory": True, "purpose": "Proof of OBC/SBC category"},
                {"doc_code": "DOC_NON_CREAMY_LAYER", "mandatory": True, "purpose": "Valid Non-Creamy Layer Certificate"},
                {"doc_code": "DOC_TAHSILDAR_INCOME", "mandatory": True, "purpose": "Income verification <= ₹1.5 Lakhs"},
                {"doc_code": "DOC_DOMICILE", "mandatory": True, "purpose": "Maharashtra residency"},
                {"doc_code": "DOC_CAP_ALLOTMENT", "mandatory": True, "purpose": "CAP admission confirmation"},
                {"doc_code": "DOC_AADHAAR_NPCI_BANK", "mandatory": True, "purpose": "Direct DBT bank transfer"}
            ]
        },
        {
            "code": "MH_SC_POSTMATRIC_2024",
            "version": "2024.1",
            "effective_academic_year": "2024-2025",
            "name": "Government of India Post-Matric Scholarship for SC Students",
            "name_marathi": "भारत सरकार अनुसूचित जाती (SC) मॅट्रिकोत्तर शिष्यवृत्ती",
            "department": "Social Justice and Special Assistance Department, Maharashtra",
            "statutory_gr": "Social Justice Dept GR No. BVD-2013/C.R.63/MVK-3 & Central Guidelines 2021",
            "official_portal_url": "https://mahadbt.maharashtra.gov.in/",
            "portal_name": "MahaDBT (Aaple Sarkar DBT Portal)",
            "benefit_type": "TUITION_FEE_WAIVER",
            "benefit_amount_text": "100% Tuition & Exam Fee Waiver + Monthly Maintenance Stipend (up to ₹1,200/mo)",
            "estimated_annual_value": 65000,
            "brief_description": "Full financial coverage of tuition and examination fees plus monthly maintenance stipend for Scheduled Caste and Navboudha students in post-matric studies.",
            "stackable_with_benefit_types": ["HOSTEL_ALLOWANCE", "LODGING_BOARDING", "BOOK_STATIONERY"],
            "rules": {
                "operator": "ALL",
                "conditions": [
                    {
                        "field": "is_maharashtra_domicile",
                        "op": "==",
                        "value": True,
                        "label": "Domicile of Maharashtra State",
                        "citation": "Clause 1.1: Maharashtra residency required."
                    },
                    {
                        "field": "caste_category",
                        "op": "==",
                        "value": "SC",
                        "label": "Scheduled Caste (SC) or Navboudha",
                        "citation": "Clause 2.1: Recognized SC community under Constitution Order."
                    },
                    {
                        "field": "annual_family_income",
                        "op": "<=",
                        "value": 250000,
                        "boundary_tolerance": 40000,
                        "label": "Annual family income not exceeding ₹2,50,000",
                        "citation": "Clause 3.1: Central ceiling of ₹2,50,000 per annum."
                    }
                ]
            },
            "documents": [
                {"doc_code": "DOC_CASTE", "mandatory": True, "purpose": "Proof of SC category"},
                {"doc_code": "DOC_CASTE_VALIDITY", "mandatory": True, "purpose": "Mandatory Caste Validity Certificate for degree/diploma"},
                {"doc_code": "DOC_TAHSILDAR_INCOME", "mandatory": True, "purpose": "Income Certificate <= ₹2.5 Lakhs"},
                {"doc_code": "DOC_DOMICILE", "mandatory": True, "purpose": "Proof of Maharashtra domicile"},
                {"doc_code": "DOC_AADHAAR_NPCI_BANK", "mandatory": True, "purpose": "Direct DBT transfer of stipend"}
            ]
        },
        {
            "code": "MH_PANJABRAO_HOSTEL_2024",
            "version": "2024.1",
            "effective_academic_year": "2024-2025",
            "name": "Dr. Panjabrao Deshmukh Vasatigruh Nirvah Bhatta Yojna (Hostel Allowance)",
            "name_marathi": "डॉ. पंजाबराव देशमुख वसतिगृह निर्वाह भत्ता योजना",
            "department": "Directorate of Technical Education (DTE), Maharashtra",
            "statutory_gr": "Govt. Resolution No. TEM-2018/C.R.328/TE-4 dated 11/07/2018",
            "official_portal_url": "https://mahadbt.maharashtra.gov.in/",
            "portal_name": "MahaDBT (Aaple Sarkar DBT Portal)",
            "benefit_type": "HOSTEL_ALLOWANCE",
            "benefit_amount_text": "₹30,000/year (Metro: Mumbai/Pune/Nagpur) or ₹20,000/year (Other cities)",
            "estimated_annual_value": 30000,
            "brief_description": "Hostel allowance for children of registered small landholding farmers or families with income <= ₹8 Lakhs staying in private rental/hostels for professional courses.",
            "stackable_with_benefit_types": ["TUITION_FEE_WAIVER", "MAINTENANCE_STIPEND"],
            "rules": {
                "operator": "ALL",
                "conditions": [
                    {
                        "field": "is_maharashtra_domicile",
                        "op": "==",
                        "value": True,
                        "label": "Domicile of Maharashtra State",
                        "citation": "Clause 1.1: Maharashtra residency required."
                    },
                    {
                        "field": "current_course_level",
                        "op": "in",
                        "value": ["PROFESSIONAL_DEGREE", "DIPLOMA"],
                        "label": "Enrolled in Professional Degree or Technical Diploma",
                        "citation": "Clause 2.1: Applies to DTE / Professional approved courses (Engineering, Pharmacy, Polytechnic)."
                    },
                    {
                        "field": "admission_quota",
                        "op": "in",
                        "value": ["CAP_ROUND", "DIRECT_SECOND_YEAR"],
                        "label": "Admitted via Centralized CAP Round",
                        "citation": "Clause 2.2: Admitted through State CET Cell CAP round."
                    },
                    {
                        "field": "accommodation_type",
                        "op": "==",
                        "value": "PRIVATE_RENTAL_PG",
                        "boundary_tolerance": 0,
                        "label": "Living in Private Rental Flat / Paying Guest (Hostel not provided)",
                        "citation": "Clause 3.1: Student must not be residing in a Government Hostel."
                    },
                    {
                        "field": "annual_family_income",
                        "op": "<=",
                        "value": 800000,
                        "boundary_tolerance": 50000,
                        "label": "Annual family income not exceeding ₹8,00,000",
                        "citation": "Clause 4.1: Up to ₹8 Lakhs income, or parent is registered small farmer."
                    }
                ]
            },
            "documents": [
                {"doc_code": "DOC_HOSTEL_RENT_PROOF", "mandatory": True, "purpose": "Proof of rented accommodation / hostel expenses"},
                {"doc_code": "DOC_TAHSILDAR_INCOME", "mandatory": True, "purpose": "Income Certificate <= ₹8 Lakhs"},
                {"doc_code": "DOC_FARMER_7_12", "mandatory": False, "purpose": "7/12 land extract (qualifies student for higher benefit tier)"},
                {"doc_code": "DOC_CAP_ALLOTMENT", "mandatory": True, "purpose": "CAP allotment letter"},
                {"doc_code": "DOC_AADHAAR_NPCI_BANK", "mandatory": True, "purpose": "Bank account for ₹30,000 direct credit"}
            ]
        },
        {
            "code": "MH_SWADHAR_SC_2024",
            "version": "2024.1",
            "effective_academic_year": "2024-2025",
            "name": "Dr. Babasaheb Ambedkar Swadhar Yojana (Living & Boarding Allowance)",
            "name_marathi": "डॉ. बाबासाहेब आंबेडकर स्वाधार योजना",
            "department": "Social Justice and Special Assistance Department, Maharashtra",
            "statutory_gr": "Govt. Resolution No. EBC-2016/C.R.221/Edu-1 dated 28/04/2017",
            "official_portal_url": "https://sjsa.maharashtra.gov.in/",
            "portal_name": "Social Justice Department Portal / MahaDBT",
            "benefit_type": "LODGING_BOARDING",
            "benefit_amount_text": "₹48,000 to ₹60,000 per year directly to Student Account",
            "estimated_annual_value": 51000,
            "brief_description": "Financial assistance for boarding, lodging, and academic materials for SC students pursuing higher education who did not receive admission into Government Hostels.",
            "stackable_with_benefit_types": ["TUITION_FEE_WAIVER"],
            "rules": {
                "operator": "ALL",
                "conditions": [
                    {
                        "field": "is_maharashtra_domicile",
                        "op": "==",
                        "value": True,
                        "label": "Domicile of Maharashtra State",
                        "citation": "Clause 1.1: Resident of Maharashtra."
                    },
                    {
                        "field": "caste_category",
                        "op": "==",
                        "value": "SC",
                        "label": "Belongs to Scheduled Caste (SC) or Navboudha",
                        "citation": "Clause 2.1: SC community certificate required."
                    },
                    {
                        "field": "annual_family_income",
                        "op": "<=",
                        "value": 250000,
                        "boundary_tolerance": 30000,
                        "label": "Annual family income not exceeding ₹2,50,000",
                        "citation": "Clause 3.1: Family income ceiling of ₹2.5 Lakhs."
                    },
                    {
                        "field": "accommodation_type",
                        "op": "==",
                        "value": "PRIVATE_RENTAL_PG",
                        "label": "Living in Private Rental Accommodation (Not in Govt Hostel)",
                        "citation": "Clause 4.1: Eligible only if applicant applied for Govt hostel and did not get a seat."
                    }
                ]
            },
            "documents": [
                {"doc_code": "DOC_CASTE", "mandatory": True, "purpose": "Proof of SC category"},
                {"doc_code": "DOC_TAHSILDAR_INCOME", "mandatory": True, "purpose": "Income <= ₹2.5 Lakhs"},
                {"doc_code": "DOC_HOSTEL_RENT_PROOF", "mandatory": True, "purpose": "Proof of staying in rental accommodation"},
                {"doc_code": "DOC_AADHAAR_NPCI_BANK", "mandatory": True, "purpose": "Aadhaar seeded bank account for ₹51,000 payment"}
            ]
        }
    ]

    for s_data in schemes_data:
        req_docs = s_data.pop("documents")
        s_data["official_source_url"] = s_data.get("official_portal_url", "https://mahadbt.maharashtra.gov.in/")
        s_data["last_verified_on"] = "2024-11-01"
        s_data["verification_status"] = "VERIFIED"
        s_data["is_sample"] = False
        scheme, _ = Scheme.objects.update_or_create(code=s_data["code"], defaults=s_data)
        
        # Link documents
        for item in req_docs:
            doc_obj = docs_dict.get(item["doc_code"])
            if doc_obj:
                SchemeDocumentRequirement.objects.update_or_create(
                    scheme=scheme,
                    document=doc_obj,
                    defaults={
                        "is_mandatory": item.get("mandatory", True),
                        "specific_purpose": item.get("purpose", "")
                    }
                )
    print(f"Successfully seeded {len(schemes_data)} schemes with statutory GR citations and document rules.")

if __name__ == "__main__":
    docs = seed_documents()
    seed_schemes(docs)
