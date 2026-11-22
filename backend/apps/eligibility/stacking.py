"""
Scholarship Stacking & Conflict Detection Engine.
Finds the maximum legitimate, non-conflicting scholarship package for a student
while warning against mutually exclusive dual tuition fee claims under MahaDBT rules.
"""

from typing import List, Dict, Any

class StackingOptimizer:
    @staticmethod
    def optimize_bundle(evaluated_schemes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes evaluated schemes and returns:
        - recommended_bundle: List of complementary schemes that can be legitimately claimed together
        - total_package_value: Sum of annual rupee benefit from the bundle
        - conflicting_schemes: Schemes that conflict with the recommended bundle
        - guidance: Plain-language explanation of why this bundle was selected
        """
        # Consider schemes that are LIKELY_ELIGIBLE or NEAR_ELIGIBLE
        candidate_schemes = [
            s for s in evaluated_schemes 
            if s["status"] in ["LIKELY_ELIGIBLE", "NEAR_ELIGIBLE"]
        ]

        if not candidate_schemes:
            return {
                "recommended_bundle": [],
                "total_package_value": 0,
                "conflicting_schemes": [],
                "guidance": "No eligible or near-eligible schemes found for bundling yet."
            }

        # Segregate by benefit type
        tuition_schemes = [s for s in candidate_schemes if s["benefit_type"] == "TUITION_FEE_WAIVER"]
        living_hostel_schemes = [s for s in candidate_schemes if s["benefit_type"] in ["HOSTEL_ALLOWANCE", "LODGING_BOARDING", "MAINTENANCE_STIPEND"]]
        other_schemes = [s for s in candidate_schemes if s not in tuition_schemes and s not in living_hostel_schemes]

        bundle = []
        conflicts = []
        total_value = 0

        # Step 1: Select the single highest-value tuition fee waiver (Dual tuition claims prohibited by MahaDBT)
        if tuition_schemes:
            # Sort descending by estimated annual value
            sorted_tuition = sorted(tuition_schemes, key=lambda x: x["estimated_annual_value"], reverse=True)
            primary_tuition = sorted_tuition[0]
            bundle.append(primary_tuition)
            total_value += primary_tuition["estimated_annual_value"]

            # Remaining tuition schemes are conflicting
            for alt in sorted_tuition[1:]:
                conflicts.append({
                    "scheme_code": alt["code"],
                    "scheme_name": alt["name"],
                    "reason": f"MahaDBT rules strictly prohibit claiming two tuition fee waivers simultaneously. We prioritized '{primary_tuition['name']}' as it offers higher estimated coverage (₹{primary_tuition['estimated_annual_value']:,} vs ₹{alt['estimated_annual_value']:,})."
                })

        # Step 2: Select stackable living / hostel allowances (Stackable with tuition waiver)
        if living_hostel_schemes:
            sorted_living = sorted(living_hostel_schemes, key=lambda x: x["estimated_annual_value"], reverse=True)
            primary_living = sorted_living[0]
            bundle.append(primary_living)
            total_value += primary_living["estimated_annual_value"]

            for alt in sorted_living[1:]:
                conflicts.append({
                    "scheme_code": alt["code"],
                    "scheme_name": alt["name"],
                    "reason": f"Dual hostel/living allowance claims are restricted. We selected '{primary_living['name']}' (₹{primary_living['estimated_annual_value']:,}/year)."
                })

        # Step 3: Add other non-conflicting components
        for other in other_schemes:
            bundle.append(other)
            total_value += other["estimated_annual_value"]

        # Guidance message
        if len(bundle) > 1:
            names = " + ".join([b["name"].split("(")[0].strip() for b in bundle])
            guidance = f"Multi-benefit package unlocked! You can legally combine {names} for a total estimated financial support of ₹{total_value:,}/year."
        elif len(bundle) == 1:
            guidance = f"Your optimal scheme is '{bundle[0]['name']}' offering approximately ₹{total_value:,}/year."
        else:
            guidance = "Complete your profile to unlock stackable scholarship packages."

        return {
            "recommended_bundle": bundle,
            "total_package_value": total_value,
            "conflicting_schemes": conflicts,
            "guidance": guidance
        }
