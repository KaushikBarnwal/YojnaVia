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
  <div v-if="isOpen && scheme" class="fixed inset-0 z-50 overflow-y-auto bg-[#0B132B]/70 backdrop-blur-xs flex items-center justify-center p-4">
    <div class="bg-[#FBFBFA] rounded-xl shadow-[4px_4px_0_0_#0B132B] max-w-3xl w-full max-h-[90vh] flex flex-col overflow-hidden border-[2px] border-[#0B132B]">
      
      <!-- Modal Header -->
      <div class="p-6 bg-[#0B132B] text-white border-b-[1.5px] border-[#0B132B] flex items-start justify-between gap-4">
        <div>
          <div class="flex items-center gap-2 mb-2">
            <span class="text-xs px-2.5 py-0.5 rounded-sm border border-[#0B132B] font-black uppercase tracking-wider" :class="statusBadgeClass">
              {{ scheme.status.replace('_', ' ') }}
            </span>
            <span class="text-xs font-mono bg-[#1C2541] text-[#FBBF24] border border-[#D97706] px-2 py-0.5 rounded-sm font-bold">
              {{ scheme.code }} • Academic year {{ scheme.effective_academic_year }}
            </span>
          </div>
          <h3 class="text-xl font-black text-white leading-snug">{{ scheme.name }}</h3>
          <p class="text-sm text-slate-300 mt-1 font-medium">{{ scheme.department }}</p>
        </div>

        <button 
          @click="emit('close')" 
          class="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-[#1C2541] transition-colors cursor-pointer"
        >
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Modal Body -->
      <div class="p-6 overflow-y-auto space-y-6">
        
        <!-- Statutory Authority Box -->
        <div class="p-4 rounded-lg bg-white border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#0B132B] flex items-start gap-3">
          <Scale class="w-5 h-5 text-[#D97706] shrink-0 mt-0.5" />
          <div>
            <h4 class="text-xs font-black uppercase tracking-wider text-[#0B132B]">Official government order (GR)</h4>
            <p class="text-sm font-black text-[#0B132B] mt-0.5">{{ scheme.statutory_gr }}</p>
            <p class="text-xs text-[#475569] mt-1 font-medium">
              Rule version: <span class="font-mono font-bold text-[#0B132B]">{{ scheme.version }}</span>. Checked against official Maharashtra government orders and MahaDBT rules. No AI is used in this check.
            </p>
          </div>
        </div>

        <!-- Benefit Summary -->
        <div class="bg-[#ECFDF5] rounded-lg p-4 border-[1.5px] border-[#065F46] shadow-[2px_2px_0_0_#065F46]">
          <div class="text-xs font-black text-[#065F46] uppercase tracking-wider">Estimated money you get</div>
          <div class="text-xl font-black text-[#064E3B] mt-1 font-mono">{{ scheme.benefit_amount_text }}</div>
          <p class="text-xs text-[#065F46] mt-0.5 font-medium">{{ scheme.brief_description }}</p>
        </div>

        <!-- Criteria Audit Trail Breakdown -->
        <div>
          <h4 class="text-sm font-black text-[#0B132B] mb-3 flex items-center gap-2">
            How each rule was checked
          </h4>

          <div class="space-y-3">
            <!-- Passed Criteria -->
            <div v-for="(item, idx) in scheme.passed_criteria" :key="'pass-' + idx" class="p-3.5 rounded-lg bg-white border-[1.5px] border-[#0B132B] shadow-[1.5px_1.5px_0_0_#059669] text-xs">
              <div class="flex items-start gap-2.5">
                <CheckCircle2 class="w-4 h-4 text-[#059669] shrink-0 mt-0.5" />
                <div class="space-y-1">
                  <div class="font-bold text-[#0B132B]">{{ item.reason }}</div>
                  <div class="text-[11px] text-[#065F46] font-mono bg-[#ECFDF5] border border-[#A7F3D0] px-2 py-0.5 rounded-sm inline-block">
                    {{ item.citation }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Near Eligible Criteria -->
            <div v-for="(item, idx) in scheme.near_eligible_criteria" :key="'near-' + idx" class="p-3.5 rounded-lg bg-white border-[1.5px] border-[#0B132B] shadow-[1.5px_1.5px_0_0_#D97706] text-xs">
              <div class="flex items-start gap-2.5">
                <AlertTriangle class="w-4 h-4 text-[#D97706] shrink-0 mt-0.5" />
                <div class="space-y-1">
                  <div class="font-bold text-[#0B132B]">{{ item.reason }}</div>
                  <div class="text-[11px] text-[#92400E] font-mono bg-[#FEF3C7] border border-[#FDE68A] px-2 py-0.5 rounded-sm inline-block">
                    {{ item.citation }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Missing Criteria -->
            <div v-for="(item, idx) in scheme.missing_criteria" :key="'miss-' + idx" class="p-3.5 rounded-lg bg-white border-[1.5px] border-[#0B132B] shadow-[1.5px_1.5px_0_0_#2563EB] text-xs">
              <div class="flex items-start gap-2.5">
                <HelpCircle class="w-4 h-4 text-[#2563EB] shrink-0 mt-0.5" />
                <div class="space-y-1">
                  <div class="font-bold text-[#0B132B]">{{ item.reason }}</div>
                  <div class="text-[11px] text-[#1E40AF] font-mono bg-[#EFF6FF] border border-[#BFDBFE] px-2 py-0.5 rounded-sm inline-block">{{ item.citation }}</div>
                </div>
              </div>
            </div>

            <!-- Failed Criteria -->
            <div v-for="(item, idx) in scheme.failed_criteria" :key="'fail-' + idx" class="p-3.5 rounded-lg bg-white border-[1.5px] border-[#0B132B] shadow-[1.5px_1.5px_0_0_#DC2626] text-xs">
              <div class="flex items-start gap-2.5">
                <XCircle class="w-4 h-4 text-[#DC2626] shrink-0 mt-0.5" />
                <div class="space-y-1">
                  <div class="font-bold text-[#0B132B]">{{ item.reason }}</div>
                  <div class="text-[11px] text-[#991B1B] font-mono bg-[#FEF2F2] border border-[#FECACA] px-2 py-0.5 rounded-sm inline-block">
                    {{ item.citation }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Required Documents Section -->
        <div v-if="scheme.required_documents && scheme.required_documents.length > 0">
          <h4 class="text-sm font-black text-[#0B132B] mb-3 flex items-center gap-2">
            <FileCheck2 class="w-4 h-4 text-[#0B132B]" />
            Documents you must submit, and who issues them
          </h4>
          <div class="border-[1.5px] border-[#0B132B] rounded-lg divide-y divide-[#E2E8F0] overflow-hidden shadow-[2px_2px_0_0_#0B132B]">
            <div v-for="doc in scheme.required_documents" :key="doc.code" class="p-3 bg-white flex items-start justify-between gap-4 text-xs">
              <div>
                <div class="font-black text-[#0B132B]">{{ doc.name }}</div>
                <div class="text-[11px] text-[#64748B] mt-0.5">Issued by: <span class="font-bold text-[#0B132B]">{{ doc.issuing_authority }}</span></div>
                <div class="text-[11px] text-[#D97706] font-bold mt-0.5">Get it from: {{ doc.procurement_portal }}</div>
              </div>
              <div class="text-right shrink-0">
                <span class="inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded-sm bg-[#F1F5F9] text-[#0B132B] border border-[#CBD5E1]">
                  <Clock class="w-3 h-3 text-[#64748B]" />
                  usually takes {{ doc.estimated_sla_days }} days
                </span>
                <div v-if="doc.is_mandatory" class="text-[10px] font-black text-[#DC2626] uppercase tracking-wider mt-1">Required</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="p-4 bg-[#F1F5F9] border-t-[1.5px] border-[#0B132B] flex items-center justify-between gap-4">
        <span class="text-xs text-[#64748B] font-mono font-medium">Official website: {{ scheme.portal_name }}</span>
        <div class="flex items-center gap-2">
          <button 
            @click="emit('close')" 
            class="px-4 py-2 text-xs font-black text-[#0B132B] bg-white border-[1.5px] border-[#0B132B] shadow-[1.5px_1.5px_0_0_#0B132B] hover:bg-slate-100 rounded-lg transition-colors cursor-pointer"
          >
            Close
          </button>
          <a 
            :href="scheme.official_portal_url" 
            target="_blank" 
            rel="noopener noreferrer" 
            class="inline-flex items-center gap-2 px-4 py-2 bg-[#0B132B] hover:bg-[#1C2541] text-white border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#D97706] rounded-lg text-xs font-black transition-colors cursor-pointer"
          >
            Open {{ scheme.portal_name }}
            <ExternalLink class="w-3.5 h-3.5 text-[#F59E0B]" />
          </a>
        </div>
      </div>

    </div>
  </div>
</template>
