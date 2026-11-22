<script setup lang="ts">
import { computed } from 'vue';
import type { EvaluatedScheme } from '../types';
import { 
  X, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  HelpCircle, 
  ExternalLink, 
  Scale, 
  FileCheck2, 
  Clock 
} from '@lucide/vue';

const props = defineProps<{
  scheme: EvaluatedScheme | null;
  isOpen: boolean;
}>();

const emit = defineEmits(['close']);

const statusBadgeClass = computed(() => {
  if (!props.scheme) return '';
  switch (props.scheme.status) {
    case 'LIKELY_ELIGIBLE': return 'bg-emerald-100 text-emerald-800 border-emerald-300';
    case 'NEAR_ELIGIBLE': return 'bg-amber-100 text-amber-800 border-amber-300';
    case 'NEEDS_CONFIRMATION': return 'bg-blue-100 text-blue-800 border-blue-300';
    default: return 'bg-rose-100 text-rose-800 border-rose-300';
  }
});
</script>

<template>
  <div v-if="isOpen && scheme" class="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-2xl max-w-3xl w-full max-h-[90vh] flex flex-col overflow-hidden border border-slate-200">
      
      <!-- Modal Header -->
      <div class="p-6 bg-slate-50 border-b border-slate-200 flex items-start justify-between gap-4">
        <div>
          <div class="flex items-center gap-2 mb-2">
            <span class="text-xs px-2.5 py-0.5 rounded-full border font-bold uppercase tracking-wider" :class="statusBadgeClass">
              {{ scheme.status.replace('_', ' ') }}
            </span>
            <span class="text-xs font-mono bg-slate-200 text-slate-700 px-2 py-0.5 rounded-md font-semibold">
              {{ scheme.code }} • AY {{ scheme.effective_academic_year }}
            </span>
          </div>
          <h3 class="text-xl font-bold text-slate-900 leading-snug">{{ scheme.name }}</h3>
          <p class="text-sm text-slate-600 mt-1 font-medium">{{ scheme.department }}</p>
        </div>

        <button 
          @click="emit('close')" 
          class="p-2 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 transition-colors"
        >
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Modal Body -->
      <div class="p-6 overflow-y-auto space-y-6">
        
        <!-- Statutory Authority Box -->
        <div class="p-4 rounded-xl bg-indigo-50/70 border border-indigo-200 flex items-start gap-3">
          <Scale class="w-5 h-5 text-indigo-700 shrink-0 mt-0.5" />
          <div>
            <h4 class="text-xs font-bold uppercase tracking-wider text-indigo-900">Official Government Authority & Resolution (GR)</h4>
            <p class="text-sm font-semibold text-indigo-950 mt-0.5">{{ scheme.statutory_gr }}</p>
            <p class="text-xs text-indigo-700 mt-1">
              Rule Version: <span class="font-mono font-medium">{{ scheme.version }}</span>. Certified against official Maharashtra Government Resolutions and MahaDBT rules. Zero artificial intelligence intervention in this legal evaluation.
            </p>
          </div>
        </div>

        <!-- Benefit Summary -->
        <div class="bg-emerald-50 rounded-xl p-4 border border-emerald-200">
          <div class="text-xs font-bold text-emerald-800 uppercase tracking-wider">Estimated Financial Assistance</div>
          <div class="text-lg font-bold text-emerald-950 mt-1">{{ scheme.benefit_amount_text }}</div>
          <p class="text-xs text-emerald-700 mt-0.5">{{ scheme.brief_description }}</p>
        </div>

        <!-- Criteria Audit Trail Breakdown -->
        <div>
          <h4 class="text-sm font-bold text-slate-900 mb-3 flex items-center gap-2">
            Deterministic Rule Evaluation Audit Trail
          </h4>

          <div class="space-y-3">
            <!-- Passed Criteria -->
            <div v-for="(item, idx) in scheme.passed_criteria" :key="'pass-' + idx" class="p-3.5 rounded-xl bg-emerald-50/50 border border-emerald-200 text-sm">
              <div class="flex items-start gap-2.5">
                <CheckCircle2 class="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <div class="space-y-1">
                  <div class="font-semibold text-emerald-950">{{ item.reason }}</div>
                  <div class="text-xs text-emerald-800 font-mono bg-emerald-100/60 px-2 py-0.5 rounded inline-block">
                    {{ item.citation }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Near Eligible Criteria -->
            <div v-for="(item, idx) in scheme.near_eligible_criteria" :key="'near-' + idx" class="p-3.5 rounded-xl bg-amber-50 border border-amber-300 text-sm">
              <div class="flex items-start gap-2.5">
                <AlertTriangle class="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                <div class="space-y-1">
                  <div class="font-semibold text-amber-950">{{ item.reason }}</div>
                  <div class="text-xs text-amber-800 font-mono bg-amber-100 px-2 py-0.5 rounded inline-block">
                    {{ item.citation }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Missing Criteria -->
            <div v-for="(item, idx) in scheme.missing_criteria" :key="'miss-' + idx" class="p-3.5 rounded-xl bg-blue-50 border border-blue-200 text-sm">
              <div class="flex items-start gap-2.5">
                <HelpCircle class="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                <div class="space-y-1">
                  <div class="font-semibold text-blue-950">{{ item.reason }}</div>
                  <div class="text-xs text-blue-700">{{ item.citation }}</div>
                </div>
              </div>
            </div>

            <!-- Failed Criteria -->
            <div v-for="(item, idx) in scheme.failed_criteria" :key="'fail-' + idx" class="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-sm">
              <div class="flex items-start gap-2.5">
                <XCircle class="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
                <div class="space-y-1">
                  <div class="font-semibold text-rose-950">{{ item.reason }}</div>
                  <div class="text-xs text-rose-800 font-mono bg-rose-100/80 px-2 py-0.5 rounded inline-block">
                    {{ item.citation }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Required Documents Section -->
        <div v-if="scheme.required_documents && scheme.required_documents.length > 0">
          <h4 class="text-sm font-bold text-slate-900 mb-3 flex items-center gap-2">
            <FileCheck2 class="w-4 h-4 text-slate-700" />
            Mandatory Documents & Issuing Authorities
          </h4>
          <div class="border border-slate-200 rounded-xl divide-y divide-slate-100 overflow-hidden">
            <div v-for="doc in scheme.required_documents" :key="doc.code" class="p-3 bg-white flex items-start justify-between gap-4 text-sm">
              <div>
                <div class="font-semibold text-slate-900">{{ doc.name }}</div>
                <div class="text-xs text-slate-500 mt-0.5">Issuing Authority: <span class="font-medium text-slate-700">{{ doc.issuing_authority }}</span></div>
                <div class="text-xs text-indigo-600 font-medium mt-0.5">Portal: {{ doc.procurement_portal }}</div>
              </div>
              <div class="text-right shrink-0">
                <span class="inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-md bg-slate-100 text-slate-700">
                  <Clock class="w-3 h-3 text-slate-500" />
                  {{ doc.estimated_sla_days }} days SLA
                </span>
                <div v-if="doc.is_mandatory" class="text-[10px] font-bold text-rose-600 uppercase tracking-wider mt-1">Mandatory</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="p-4 bg-slate-50 border-t border-slate-200 flex items-center justify-between gap-4">
        <span class="text-xs text-slate-500">Official Portal: {{ scheme.portal_name }}</span>
        <div class="flex items-center gap-2">
          <button 
            @click="emit('close')" 
            class="px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-200 rounded-xl transition-colors"
          >
            Close
          </button>
          <a 
            :href="scheme.official_portal_url" 
            target="_blank" 
            rel="noopener noreferrer" 
            class="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-sm font-semibold shadow-xs transition-colors"
          >
            Open {{ scheme.portal_name }}
            <ExternalLink class="w-4 h-4" />
          </a>
        </div>
      </div>

    </div>
  </div>
</template>
