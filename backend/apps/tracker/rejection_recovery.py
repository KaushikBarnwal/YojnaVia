"""
Rejection Recovery & Grievance Navigator Engine.
When a citizen reports an application rejection or scrutiny query on MahaDBT / government portals,
this service translates bureaucratic scrutiny remarks into plain language, determines whether
a 15-day scrutiny resubmission window applies, guides document rectification, and identifies
verified official grievance redressal and statutory appeal routes.
"""

from typing import Dict, Any, List


REJECTION_SCENARIOS: Dict[str, Dict[str, Any]] = {
    "INCOME_FY_MISMATCH": {
        "code": "INCOME_FY_MISMATCH",
        "title": "Income Certificate Financial Year Mismatch",
        "official_remark_patterns": [
            "Income certificate not for current financial year",
            "Submit income certificate for FY 2023-24",
            "Older financial year income certificate attached"
        ],
        "plain_language_explanation": (
            "The scrutiny officer flagged your application because your income certificate was issued for an older financial year. "
            "For Academic Year 2024-25, the Maharashtra Government Resolution strictly requires an income certificate assessing the previous financial year (FY 2023-24)."
        ),
        "can_resubmit_in_scrutiny_window": True,
        "resubmission_window_days": 15,
        "window_statutory_rule": "Under MahaDBT operational guidelines, applicants have 15 days from scrutiny return to re-upload corrected documents without losing their entitlement.",
        "corrective_actions": [
            "Do not start a fresh application. Your existing application has been sent back for rectification.",
            "Visit the Aaple Sarkar portal (aaplesarkar.mahaonline.gov.in) and apply for a Tahsildar Income Certificate for FY 2023-24 (15-day statutory SLA under RTS).",
            "Once received, log in to MahaDBT, navigate to 'My Applied Schemes', click 'Update / Re-submit', and upload the new digital barcode certificate.",
            "Submit the printout of the updated application acknowledgment to your college scholarship clerk."
        ],
        "document_remedy": {
            "name": "Tahsildar Income Certificate (FY 2023-24)",
            "issuing_authority": "Taluka Tahsildar / Revenue Department",
            "sla_days": 15,
            "statutory_fee_inr": 33.60,
            "portal": "https://aaplesarkar.mahaonline.gov.in"
        },
        "official_appeal_route": {
            "applicable": True,
            "condition": "If your income certificate was already for the correct financial year and rejected erroneously by the college clerk.",
            "authority_name": "Divisional Joint Director of Technical / Higher Education",
            "department": "Higher & Technical Education Department, Govt of Maharashtra",
            "official_portal": "https://grievance.maharashtra.gov.in",
            "grievance_mechanism": "MahaDBT Online Grievance Redressal / Aaple Sarkar Grievance Portal",
            "statutory_deadline": "Within 30 days of scrutiny order under the Maharashtra Right to Public Services Act (RTS 2015)."
        }
    },
    "CASTE_VALIDITY_MISSING": {
        "code": "CASTE_VALIDITY_MISSING",
        "title": "Caste Validity Certificate Missing for Professional Degree",
        "official_remark_patterns": [
            "Caste Validity Certificate not attached",
            "Submit caste validity certificate from scrutiny committee",
            "Only caste certificate submitted, validity required"
        ],
        "plain_language_explanation": (
            "For professional technical degree courses (Engineering, Pharmacy, MBA, Architecture), a Sub-Divisional Officer (SDO) Caste Certificate is not sufficient for scholarship sanction. "
            "State law mandatorily requires a Caste Scrutiny Committee Validity Certificate."
        ),
        "can_resubmit_in_scrutiny_window": True,
        "resubmission_window_days": 15,
        "window_statutory_rule": "College clerks can hold the scrutiny query open if you provide the official Caste Scrutiny Committee Application Receipt and College Undertaking Form.",
        "corrective_actions": [
            "If your Caste Validity is in process, obtain the official online Application Acknowledgment Receipt from BARTI / TRTI / CCVIS portal.",
            "Submit an Undertaking on College Letterhead stating that the validity certificate will be produced prior to final disbursement.",
            "Upload the Scrutiny Committee Receipt in the 'Caste Validity' slot on MahaDBT and resubmit to college clerk."
        ],
        "document_remedy": {
            "name": "Caste Validity Certificate (or BARTI/TRTI Acknowledgment)",
            "issuing_authority": "Divisional Caste Scrutiny Committee, Social Justice Department",
            "sla_days": 45,
            "statutory_fee_inr": 0,
            "portal": "https://barti.maharashtra.gov.in"
        },
        "official_appeal_route": {
            "applicable": True,
            "condition": "If college clerk refuses to accept the Scrutiny Committee undertaking receipt despite government relaxation GR.",
            "authority_name": "Assistant Commissioner of Social Welfare (District Social Welfare Officer)",
            "department": "Social Justice & Special Assistance Department",
            "official_portal": "https://sjsa.maharashtra.gov.in",
            "grievance_mechanism": "District Social Welfare Grievance Cell",
            "statutory_deadline": "Within 30 days of scrutiny rejection."
        }
    },
    "NON_CAP_ADMISSION": {
        "code": "NON_CAP_ADMISSION",
        "title": "Admission Quota Ineligible (Management / Institutional Seat)",
        "official_remark_patterns": [
            "Candidate admitted through Management Quota",
            "Non-CAP admission not eligible for EBC / Freeship",
            "Allotment letter not from Centralized Admission Process"
        ],
        "plain_language_explanation": (
            "Government tuition fee scholarships (EBC, OBC Freeship, SC Post-Matric) statutorily restrict fee reimbursements to students admitted through Centralized Admission Process (CAP Round) merit lists. "
            "Students admitted via management or institutional seats are legally excluded from State budget fee waivers under GR TEM-2018/CR-363."
        ),
        "can_resubmit_in_scrutiny_window": False,
        "resubmission_window_days": 0,
        "window_statutory_rule": "Statutory exclusion. Scrutiny officers cannot override the CAP round mandate.",
        "corrective_actions": [
            "Check your State CET Cell Allotment Letter. If you were actually admitted via CAP (e.g. CAP Round 1, 2, 3 or Direct Second Year CAP), the college clerk may have categorized your seat incorrectly.",
            "If you were admitted via CAP: Request your college registrar to update your admission category in the College ERP database to 'CAP_ROUND'.",
            "If you were admitted via institutional quota: Apply for university internal need-based scholarships or private CSR education grants (e.g., Tata Trusts, Leela Poonawalla, Vidyasaarathi)."
        ],
        "document_remedy": {
            "name": "State CET Cell CAP Final Allotment Letter",
            "issuing_authority": "State Common Entrance Test Cell, Maharashtra",
            "sla_days": 1,
            "statutory_fee_inr": 0,
            "portal": "https://cetcell.mahacet.org"
        },
        "official_appeal_route": {
            "applicable": True,
            "condition": "Strictly limited to cases where the candidate WAS admitted via CAP, but the college incorrectly coded the admission.",
            "authority_name": "Joint Director, Technical Education Regional Office (DTE RO)",
            "department": "Directorate of Technical Education, Maharashtra",
            "official_portal": "https://dte.maharashtra.gov.in",
            "grievance_mechanism": "DTE Grievance Portal & Regional Office Appeal",
            "statutory_deadline": "Within 15 days of quota dispute."
        }
    },
    "NCL_EXPIRED": {
        "code": "NCL_EXPIRED",
        "title": "Non-Creamy Layer (NCL) Certificate Expired",
        "official_remark_patterns": [
            "NCL certificate expired",
            "Submit valid non creamy layer certificate valid till 31/03/2025",
            "NCL validity period elapsed"
        ],
        "plain_language_explanation": (
            "Non-Creamy Layer certificates for OBC, VJNT, and SBC categories have an official expiration date (normally valid for 3 financial years up to March 31). "
            "Your uploaded certificate expired before the current academic year deadline."
        ),
        "can_resubmit_in_scrutiny_window": True,
        "resubmission_window_days": 15,
        "window_statutory_rule": "MahaDBT permits re-upload of renewed NCL certificates within 15 days of scrutiny notice.",
        "corrective_actions": [
            "Apply immediately for NCL renewal on Aaple Sarkar portal using your existing caste certificate and latest 3 years' income records.",
            "Attach the Aaple Sarkar token receipt in your scrutiny resubmission if the renewed certificate is pending dispatch."
        ],
        "document_remedy": {
            "name": "Non-Creamy Layer Certificate (Valid till 31/03/2025)",
            "issuing_authority": "Sub-Divisional Officer (SDO) / Taluka Tahsildar",
            "sla_days": 21,
            "statutory_fee_inr": 33.60,
            "portal": "https://aaplesarkar.mahaonline.gov.in"
        },
        "official_appeal_route": {
            "applicable": True,
            "condition": "If your NCL certificate is a 3-year certificate and was misread by the scrutiny clerk.",
            "authority_name": "District Social Welfare Officer",
            "department": "OBC Bahujan Welfare Directorate, Maharashtra",
            "official_portal": "https://grievance.maharashtra.gov.in",
            "grievance_mechanism": "MahaDBT Scrutiny Grievance Desk",
            "statutory_deadline": "Within 30 days."
        }
    },
    "AADHAAR_DBT_UNSEEDED": {
        "code": "AADHAAR_DBT_UNSEEDED",
        "title": "Bank Account Not Seeded with Aadhaar (NPCI Inactive)",
        "official_remark_patterns": [
            "Aadhaar bank seeding failed",
            "Bank account not linked with NPCI mapper",
            "DBT payment rejected by PFMS/treasury"
        ],
        "plain_language_explanation": (
            "Your scholarship was scrutinized and approved, but the state treasury could not disburse funds. "
            "Government disbursements use the Aadhaar Payment Bridge (APB), which requires your bank account to be actively mapped on the National Payments Corporation of India (NPCI) server."
        ),
        "can_resubmit_in_scrutiny_window": True,
        "resubmission_window_days": 30,
        "window_statutory_rule": "Treasury rejection does not cancel your scholarship. The department re-triggers disbursement once NPCI mapping is verified.",
        "corrective_actions": [
            "Visit your bank branch immediately with a physical copy of the 'Aadhaar DBT Seeding & Mandate Form'.",
            "Ask the bank officer specifically to enable 'NPCI Mapping for DBT Payments', not just standard KYC Aadhaar linkage.",
            "Verify active status on the UIDAI resident portal ('Check Aadhaar & Bank Account Linking Status').",
            "Log in to MahaDBT, navigate to Profile -> Bank Details, click 'Check Aadhaar Bank Linking Status', and refresh your profile."
        ],
        "document_remedy": {
            "name": "Bank Passbook with Manager Stamp & Aadhaar DBT Mandate Acknowledgment",
            "issuing_authority": "Nationalized Bank / Scheduled Commercial Bank",
            "sla_days": 2,
            "statutory_fee_inr": 0,
            "portal": "https://myaadhaar.uidai.gov.in"
        },
        "official_appeal_route": {
            "applicable": False,
            "condition": "Bank-level configuration issue. No departmental appeal needed; resolved directly via bank and MahaDBT profile re-sync.",
            "authority_name": "Bank Branch Manager / Lead District Manager (LDM)",
            "department": "Department of Financial Services, GoI",
            "official_portal": "https://resident.uidai.gov.in",
            "grievance_mechanism": "Banking Ombudsman / MahaDBT Technical Support Helpdesk",
            "statutory_deadline": "Disbursement re-triggered in next treasury cycle."
        }
    },
    "HOSTEL_CERT_MISSING": {
        "code": "HOSTEL_CERT_MISSING",
        "title": "Hostel Agreement / Warden Certificate Attestation Missing",
        "official_remark_patterns": [
            "Hostel certificate not signed by Principal",
            "Registered rent agreement missing for Panjabrao allowance",
            "Warden signature not verified"
        ],
        "plain_language_explanation": (
            "For hostel and maintenance allowances (Dr. Panjabrao Deshmukh Hostel Allowance or Dr. Ambedkar Swadhar Scheme), "
            "students staying in non-government rented rooms or private hostels must provide an official certificate counter-signed by their college principal and landlord/warden."
        ),
        "can_resubmit_in_scrutiny_window": True,
        "resubmission_window_days": 15,
        "window_statutory_rule": "MahaDBT permits re-submission of counter-signed hostel certificates within 15 days.",
        "corrective_actions": [
            "Download the prescribed 'Annexure-A: Hostel Residency & Distance Certificate' from the MahaDBT portal.",
            "Obtain signatures from your private PG owner/warden and your College Scholarship Officer/Principal.",
            "Re-upload to MahaDBT under 'Hostel Details' and resubmit."
        ],
        "document_remedy": {
            "name": "Annexure-A Counter-Signed Hostel Residency Certificate",
            "issuing_authority": "College Principal & Private Hostel Warden",
            "sla_days": 3,
            "statutory_fee_inr": 0,
            "portal": "https://mahadbt.maharashtra.gov.in"
        },
        "official_appeal_route": {
            "applicable": True,
            "condition": "If college authorities delay counter-signing the certificate.",
            "authority_name": "Student Welfare Officer / Joint Director Higher Education",
            "department": "Directorate of Higher Education, Maharashtra",
            "official_portal": "https://dhepune.gov.in",
            "grievance_mechanism": "University Student Grievance Redressal Cell (SGRC)",
            "statutory_deadline": "Within 15 days."
        }
    },
    "GAP_AFFIDAVIT_MISSING": {
        "code": "GAP_AFFIDAVIT_MISSING",
        "title": "Gap in Education Certificate / Affidavit Missing",
        "official_remark_patterns": [
            "Gap certificate missing",
            "Submit ₹100 stamp paper affidavit for study gap",
            "Year gap not explained"
        ],
        "plain_language_explanation": (
            "If you have a gap of one or more academic years between passing your previous qualifying examination (e.g. 12th or diploma) and your current degree admission, "
            "government rules require an explanatory affidavit on ₹100 non-judicial stamp paper stating the reason for the gap (e.g., preparation for entrance exam, medical reasons, or financial constraints)."
        ),
        "can_resubmit_in_scrutiny_window": True,
        "resubmission_window_days": 15,
        "window_statutory_rule": "Standard document query. Rectifiable within 15 days of scrutiny notice.",
        "corrective_actions": [
            "Visit any local notary or Aaple Sarkar Seva Kendra (CSC).",
            "Draft the standard Maharashtra education gap affidavit on a ₹100 stamp paper stating the academic gap reason.",
            "Have it notarized by an Executive Magistrate or Notary Advocate.",
            "Scan and upload the notarized affidavit on MahaDBT and submit."
        ],
        "document_remedy": {
            "name": "₹100 Notarized Education Gap Affidavit",
            "issuing_authority": "Notary Public / Executive Magistrate",
            "sla_days": 1,
            "statutory_fee_inr": 150.00,
            "portal": "https://aaplesarkar.mahaonline.gov.in"
        },
        "official_appeal_route": {
            "applicable": False,
            "condition": "Standard compliance requirement. Resubmission resolves the query.",
            "authority_name": "College Scholarship Scrutiny Desk",
            "department": "Department of Higher & Technical Education",
            "official_portal": "https://mahadbt.maharashtra.gov.in",
            "grievance_mechanism": "MahaDBT Student Portal Helpdesk",
            "statutory_deadline": "15 days from scrutiny query."
        }
    }
}


class RejectionRecoveryService:
    @classmethod
    def get_all_scenarios(cls) -> List[Dict[str, Any]]:
        """Returns list of canonical Maharashtra rejection scenarios for UI selection."""
        return list(REJECTION_SCENARIOS.values())

    @classmethod
    def diagnose_and_navigate(
        cls,
        rejection_code: str = None,
        custom_rejection_text: str = None,
        scheme_code: str = "MH_DTE_EBC_2024"
    ) -> Dict[str, Any]:
        """
        Diagnoses a rejection remark and returns the actionable recovery blueprint.
        Matches against canonical codes or pattern matches custom text.
        """
        scenario = None
        if rejection_code and rejection_code in REJECTION_SCENARIOS:
            scenario = REJECTION_SCENARIOS[rejection_code]
        elif custom_rejection_text:
            text_lower = custom_rejection_text.lower()
            for key, item in REJECTION_SCENARIOS.items():
                for pat in item["official_remark_patterns"]:
                    if pat.lower() in text_lower:
                        scenario = item
                        break
                if scenario:
                    break

        if not scenario:
            # Fallback to general grievance guidance
            scenario = {
                "code": "CUSTOM_SCRUTINY_QUERY",
                "title": "General Department Scrutiny Query",
                "plain_language_explanation": (
                    f"Your application for {scheme_code} was returned by the scrutiny clerk with remark: '{custom_rejection_text or 'Document Deficit'}'. "
                    "In Maharashtra, scrutiny queries can be corrected on the MahaDBT portal within 15 days without forfeiting your scholarship."
                ),
                "can_resubmit_in_scrutiny_window": True,
                "resubmission_window_days": 15,
                "window_statutory_rule": "Applicants are entitled to a 15-day rectification window before final cancellation.",
                "corrective_actions": [
                    "Review the exact remark in your college scholarship desk portal.",
                    "Obtain the attested or rectified document requested by the scrutiny clerk.",
                    "Re-upload via MahaDBT 'Update Application' and notify the college scholarship clerk."
                ],
                "document_remedy": {
                    "name": "Rectified Document as per Scrutiny Remark",
                    "issuing_authority": "Competent Authority",
                    "sla_days": 15,
                    "statutory_fee_inr": 0,
                    "portal": "https://aaplesarkar.mahaonline.gov.in"
                },
                "official_appeal_route": {
                    "applicable": True,
                    "condition": "If rejected arbitrarily without valid statutory justification.",
                    "authority_name": "Divisional Joint Director / Social Welfare Officer",
                    "department": "Government of Maharashtra",
                    "official_portal": "https://grievance.maharashtra.gov.in",
                    "grievance_mechanism": "Aaple Sarkar Online Grievance Redressal",
                    "statutory_deadline": "Within 30 days under Maharashtra RTS Act."
                }
            }

        return {
            "status": "RECOVERY_PLAN_READY",
            "scheme_code": scheme_code,
            "diagnosis": scenario,
            "summary_card": {
                "title": scenario["title"],
                "can_resubmit": scenario["can_resubmit_in_scrutiny_window"],
                "days_allowed": scenario["resubmission_window_days"],
                "appeal_available": scenario["official_appeal_route"]["applicable"]
            }
        }
