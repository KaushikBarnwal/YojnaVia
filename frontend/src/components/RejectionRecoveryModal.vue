<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import api from '../services/api';
import { 
  X, 
  RotateCcw, 
  AlertOctagon, 
  Scale, 
  FileCheck2, 
  Clock, 
  ExternalLink,
  Building2,
  Loader2
} from '@lucide/vue';

const props = defineProps<{
  isOpen: boolean;
  schemeCode?: string;
  initialRejectionRemark?: string;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
}>();

const scenarios = ref<any[]>([]);
const selectedCode = ref<string>('INCOME_FY_MISMATCH');
const customRemark = ref<string>('');
const isCustomMode = ref<boolean>(false);
const isLoading = ref<boolean>(false);
const recoveryData = ref<any>(null);

async function fetchScenarios() {
  try {
    const res = await api.get('/tracker/rejection_scenarios/');
    scenarios.value = res.data.scenarios || [];
  } catch (err) {
    console.error('Failed to load rejection scenarios:', err);
  }
}

async function loadRecoveryPlan() {
  isLoading.value = true;
  try {
    const payload = isCustomMode.value
      ? { custom_rejection_text: customRemark.value, scheme_code: props.schemeCode || 'MH_DTE_EBC_2024' }
      : { rejection_code: selectedCode.value, scheme_code: props.schemeCode || 'MH_DTE_EBC_2024' };

    const res = await api.post('/tracker/rejection_recovery/', payload);
    recoveryData.value = res.data;
  } catch (err) {
    console.error('Failed to diagnose rejection:', err);
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  fetchScenarios();
});

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      if (props.initialRejectionRemark) {
        customRemark.value = props.initialRejectionRemark;
        isCustomMode.value = true;
      }
      loadRecoveryPlan();
    }
  }
);

watch([selectedCode, isCustomMode], () => {
  if (props.isOpen && !isCustomMode.value) {
    loadRecoveryPlan();
  }
});
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto bg-[#0B132B]/70 backdrop-blur-xs flex items-center justify-center p-4">
    <div class="bg-[#FBFBFA] rounded-xl max-w-2xl w-full shadow-[4px_4px_0_0_#0B132B] border-[2px] border-[#0B132B] overflow-hidden my-8">
      <!-- Modal Header -->
      <div class="px-6 py-5 bg-[#0B132B] text-white flex items-center justify-between border-b-[1.5px] border-[#0B132B]">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-[#1C2541] border border-slate-700 rounded-lg">
            <RotateCcw class="w-6 h-6 text-[#DC2626]" />
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h3 class="text-lg font-black text-white">Rejection Recovery & Grievance Navigator</h3>
              <span class="text-xs px-2 py-0.5 rounded-sm bg-[#1C2541] text-[#FCA5A5] border border-[#DC2626] font-mono font-bold">
                RTS Act 2015
              </span>
            </div>
            <p class="text-xs text-slate-300 mt-0.5">Translate college scrutiny queries, explain resubmission windows, and recover rejected applications</p>
          </div>
        </div>
        <button @click="emit('close')" class="text-slate-400 hover:text-white p-1 rounded-lg transition-colors cursor-pointer">
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Scrutiny Selector Tabs -->
      <div class="p-4 bg-[#F1F5F9] border-b-[1.5px] border-[#0B132B] space-y-3">
        <div class="flex items-center justify-between">
          <label class="text-xs font-black text-[#0B132B] uppercase tracking-wider">
            Select Scrutiny Remark Received:
          </label>
          <button 
            @click="isCustomMode = !isCustomMode; if (isCustomMode) { recoveryData = null; } else { loadRecoveryPlan(); }"
            class="text-xs text-[#D97706] font-black hover:underline cursor-pointer"
          >
            {{ isCustomMode ? '← Pick from Common Scenarios' : 'Or enter custom remark from clerk →' }}
          </button>
        </div>

        <div v-if="!isCustomMode" class="grid grid-cols-1 sm:grid-cols-2 gap-2">
          <button 
            v-for="sc in scenarios" 
            :key="sc.code"
            @click="selectedCode = sc.code; loadRecoveryPlan()"
            class="text-left p-2.5 rounded-lg border-[1.5px] text-xs transition-all flex items-start gap-2 cursor-pointer shadow-[1px_1px_0_0_#0B132B]"
            :class="selectedCode === sc.code 
              ? 'bg-[#FEF2F2] border-[#DC2626] text-[#991B1B] font-bold' 
              : 'bg-white border-[#0B132B] text-[#0B132B] hover:bg-slate-50'"
          >
            <AlertOctagon class="w-4 h-4 shrink-0 mt-0.5" :class="selectedCode === sc.code ? 'text-[#DC2626]' : 'text-[#64748B]'" />
            <span class="line-clamp-2">{{ sc.title }}</span>
          </button>
        </div>

        <div v-else class="space-y-2">
          <textarea 
            v-model="customRemark" 
            rows="2"
            placeholder="e.g. Scrutiny query: Caste validity certificate not attached for B.Tech admission..."
            class="w-full text-xs font-bold p-3 rounded-lg border-[1.5px] border-[#0B132B] bg-white text-[#0B132B] focus:outline-hidden"
          ></textarea>
          <div class="flex justify-end">
            <button 
              @click="loadRecoveryPlan" 
              class="px-4 py-1.5 rounded-lg text-xs font-black bg-[#DC2626] text-white hover:bg-[#B91C1C] border border-[#7F1D1D] shadow-[1.5px_1.5px_0_0_#7F1D1D] transition-colors cursor-pointer"
            >
              Diagnose Custom Remark
            </button>
          </div>
        </div>
      </div>

      <!-- Recovery Content -->
      <div class="p-6 max-h-[60vh] overflow-y-auto space-y-6">
        <div v-if="isLoading" class="py-12 flex flex-col items-center justify-center text-center space-y-3">
          <Loader2 class="w-8 h-8 text-[#0B132B] animate-spin" />
          <p class="text-sm font-bold text-[#0B132B]">Analyzing Scrutiny Case & Statutory Routes...</p>
        </div>

        <div v-else-if="recoveryData?.diagnosis" class="space-y-6">
          <!-- 15-Day Resubmission Window Badge -->
          <div 
            class="p-4 rounded-lg border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#0B132B] flex items-start justify-between"
            :class="recoveryData.diagnosis.can_resubmit_in_scrutiny_window 
              ? 'bg-[#ECFDF5]' 
              : 'bg-[#FEF2F2]'"
          >
            <div class="space-y-1">
              <div class="flex items-center gap-2">
                <span 
                  class="text-xs font-black uppercase tracking-wider px-2 py-0.5 rounded-sm border border-[#0B132B]"
                  :class="recoveryData.diagnosis.can_resubmit_in_scrutiny_window 
                    ? 'bg-[#D1FAE5] text-[#065F46]' 
                    : 'bg-[#FEE2E2] text-[#991B1B]'"
                >
                  {{ recoveryData.diagnosis.can_resubmit_in_scrutiny_window ? '15-Day Resubmission Window Active' : 'Department Appeal Required' }}
                </span>
                <span class="text-xs font-bold text-[#64748B]">MahaDBT Operational Guidelines</span>
              </div>
              <p class="text-xs text-[#334155] leading-relaxed font-medium">
                {{ recoveryData.diagnosis.window_statutory_rule }}
              </p>
            </div>
            <div v-if="recoveryData.diagnosis.can_resubmit_in_scrutiny_window" class="text-right shrink-0 ml-4">
              <span class="text-2xl font-black text-[#059669] font-mono">{{ recoveryData.diagnosis.resubmission_window_days }}</span>
              <span class="text-[10px] text-[#64748B] font-bold uppercase block">Days Window</span>
            </div>
          </div>

          <!-- Plain Language Translation -->
          <div class="p-4 bg-white border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#0B132B] rounded-lg space-y-2">
            <h4 class="text-xs font-black uppercase tracking-wider text-[#0B132B] flex items-center gap-1.5">
              <Scale class="w-4 h-4 text-[#D97706]" />
              Plain-Language Explanation (What This Means)
            </h4>
            <p class="text-xs text-[#334155] leading-relaxed font-medium">
              {{ recoveryData.diagnosis.plain_language_explanation }}
            </p>
          </div>

          <!-- Document Procurement Remedy -->
          <div v-if="recoveryData.diagnosis.document_remedy" class="p-4 bg-white border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#2563EB] rounded-lg space-y-3">
            <h4 class="text-xs font-black uppercase tracking-wider text-[#1E40AF] flex items-center gap-1.5">
              <FileCheck2 class="w-4 h-4 text-[#2563EB]" />
              Document Procurement Remedy
            </h4>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
              <div class="bg-[#F8FAFC] p-2.5 rounded-lg border border-[#CBD5E1]">
                <span class="text-[10px] text-[#64748B] block font-bold uppercase">Required Document</span>
                <span class="font-bold text-[#0B132B] line-clamp-1">{{ recoveryData.diagnosis.document_remedy.name }}</span>
              </div>
              <div class="bg-[#F8FAFC] p-2.5 rounded-lg border border-[#CBD5E1]">
                <span class="text-[10px] text-[#64748B] block font-bold uppercase">Issuing Authority</span>
                <span class="font-bold text-[#0B132B] line-clamp-1">{{ recoveryData.diagnosis.document_remedy.issuing_authority }}</span>
              </div>
              <div class="bg-[#F8FAFC] p-2.5 rounded-lg border border-[#CBD5E1]">
                <span class="text-[10px] text-[#64748B] block font-bold uppercase">RTS SLA Period</span>
                <span class="font-black text-[#0B132B]">{{ recoveryData.diagnosis.document_remedy.sla_days }} Days</span>
              </div>
              <div class="bg-[#F8FAFC] p-2.5 rounded-lg border border-[#CBD5E1]">
                <span class="text-[10px] text-[#64748B] block font-bold uppercase">Statutory Fee</span>
                <span class="font-black text-[#059669]">₹{{ recoveryData.diagnosis.document_remedy.statutory_fee_inr }}</span>
              </div>
            </div>
            <div class="flex justify-end">
              <a 
                :href="recoveryData.diagnosis.document_remedy.portal" 
                target="_blank" 
                rel="noopener noreferrer"
                class="inline-flex items-center gap-1.5 text-xs font-black text-[#2563EB] hover:text-[#1D4ED8]"
              >
                <span>Apply on Aaple Sarkar Portal</span>
                <ExternalLink class="w-3 h-3" />
              </a>
            </div>
          </div>

          <!-- Step-by-Step Corrective Actions -->
          <div class="space-y-2">
            <h4 class="text-xs font-black uppercase tracking-wider text-[#0B132B] flex items-center gap-1.5">
              <Clock class="w-4 h-4 text-[#0B132B]" />
              Immediate Recovery Steps
            </h4>
            <ol class="space-y-2 text-xs text-[#334155] list-decimal list-inside bg-white p-4 rounded-lg border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#0B132B]">
              <li v-for="(act, idx) in recoveryData.diagnosis.corrective_actions" :key="idx" class="leading-relaxed">
                <span class="text-[#0B132B] font-bold">{{ act }}</span>
              </li>
            </ol>
          </div>

          <!-- Official Grievance & Appeal Route -->
          <div v-if="recoveryData.diagnosis.official_appeal_route?.applicable" class="p-4 bg-white border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#D97706] rounded-lg space-y-2.5">
            <div class="flex items-center justify-between">
              <h4 class="text-xs font-black uppercase tracking-wider text-[#92400E] flex items-center gap-1.5">
                <Building2 class="w-4 h-4 text-[#D97706]" />
                Statutory Appeal Route (Maharashtra RTS Act 2015)
              </h4>
              <span class="text-[10px] bg-[#FEF3C7] text-[#92400E] px-2 py-0.5 rounded-sm font-mono font-black border border-[#D97706]">
                Appellate Authority
              </span>
            </div>
            <p class="text-xs text-[#334155] font-medium">
              <strong>When applicable:</strong> {{ recoveryData.diagnosis.official_appeal_route.condition }}
            </p>
            <div class="p-3 bg-[#FFFBEB] rounded-lg border border-[#FCD34D] text-xs space-y-1">
              <div><strong>Appellate Officer:</strong> {{ recoveryData.diagnosis.official_appeal_route.authority_name }}</div>
              <div><strong>Department:</strong> {{ recoveryData.diagnosis.official_appeal_route.department }}</div>
              <div><strong>Statutory Deadline:</strong> {{ recoveryData.diagnosis.official_appeal_route.statutory_deadline }}</div>
            </div>
            <div class="flex justify-end pt-1">
              <a 
                :href="recoveryData.diagnosis.official_appeal_route.official_portal" 
                target="_blank" 
                rel="noopener noreferrer"
                class="inline-flex items-center gap-1.5 text-xs font-black text-[#D97706] hover:text-[#B45309]"
              >
                <span>Lodge Grievance on grievance.maharashtra.gov.in</span>
                <ExternalLink class="w-3 h-3" />
              </a>
            </div>
          </div>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="px-6 py-4 bg-[#F1F5F9] border-t-[1.5px] border-[#0B132B] flex items-center justify-between">
        <button 
          @click="emit('close')" 
          class="px-4 py-2 rounded-lg text-xs font-black text-[#0B132B] bg-white border-[1.5px] border-[#0B132B] shadow-[1.5px_1.5px_0_0_#0B132B] hover:bg-slate-100 transition-colors cursor-pointer"
        >
          Close Navigator
        </button>

        <a 
          href="https://mahadbt.maharashtra.gov.in" 
          target="_blank" 
          rel="noopener noreferrer"
          class="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-black text-white bg-[#0B132B] hover:bg-[#1C2541] border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#D97706] transition-colors cursor-pointer"
        >
          <span>Open MahaDBT Portal</span>
          <ExternalLink class="w-3.5 h-3.5 text-[#F59E0B]" />
        </a>
      </div>
    </div>
  </div>
</template>
