"""
Cross-Scheme Document Dependency Graph and Multiplier Service.
Analyzes relationships between civil documents, issuing authorities,
procurement SLAs, and their cumulative financial unlocking power across schemes.
"""

from typing import Dict, Any, List
from collections import defaultdict
from django.core.cache import cache
from apps.documents.models import Document, SchemeDocumentRequirement
from apps.schemes.models import Scheme

DOC_GRAPH_CACHE_KEY = 'document_dependency_graph'

class DocumentGraphService:
    @classmethod
    def get_document_dependency_graph(cls) -> Dict[str, Any]:
        """
        Builds the complete cross-scheme document graph:
        - nodes: documents and schemes
        - edges: requirements and prerequisites
        - document_multipliers: which document unlocks how many rupees across which schemes
        """
        cached = cache.get(DOC_GRAPH_CACHE_KEY)
        if cached is not None:
            return cached

        documents = Document.objects.filter(is_active=True)
        schemes = Scheme.objects.filter(is_active=True).prefetch_related('document_requirements__document')

        doc_usage_map = defaultdict(list)
        doc_value_map = defaultdict(int)

        for scheme in schemes:
            for req in scheme.document_requirements.all():
                doc_code = req.document.code
                doc_usage_map[doc_code].append({
                    "scheme_code": scheme.code,
                    "scheme_name": scheme.name,
                    "benefit_type": scheme.benefit_type,
                    "estimated_value": scheme.estimated_annual_value,
                    "is_mandatory": req.is_mandatory,
                    "purpose": req.specific_purpose
                })
                doc_value_map[doc_code] += scheme.estimated_annual_value

        doc_nodes = []
        for doc in documents:
            usages = doc_usage_map.get(doc.code, [])
            total_unlocked_val = doc_value_map.get(doc.code, 0)
            
            doc_nodes.append({
                "code": doc.code,
                "name": doc.name,
                "name_marathi": doc.name_marathi,
                "issuing_authority": doc.issuing_authority,
                "procurement_portal": doc.procurement_portal,
                "estimated_sla_days": doc.estimated_sla_days,
                "validity_duration": doc.validity_duration,
                "prerequisites": doc.prerequisite_documents or [],
                "how_to_obtain": doc.how_to_obtain_steps or [],
                "schemes_count": len(usages),
                "total_financial_value_unlocked": total_unlocked_val,
                "unlocks_schemes": usages
            })

        # Sort documents by multiplier impact (highest financial value unlocked first)
        sorted_doc_nodes = sorted(doc_nodes, key=lambda x: (x["total_financial_value_unlocked"], x["schemes_count"]), reverse=True)

        res = {
            "documents": sorted_doc_nodes,
            "top_multiplier_document": sorted_doc_nodes[0] if sorted_doc_nodes else None,
            "total_schemes_analyzed": len(schemes)
        }
        cache.set(DOC_GRAPH_CACHE_KEY, res, 300)
        return res
