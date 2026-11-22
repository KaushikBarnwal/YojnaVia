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
  <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl max-w-2xl w-full shadow-2xl border border-slate-200 overflow-hidden my-8">
      <!-- Modal Header -->
      <div class="px-6 py-5 bg-gradient-to-r from-rose-900 to-slate-900 text-white flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-rose-500/20 border border-rose-400/30 rounded-lg">
            <RotateCcw class="w-6 h-6 text-rose-300" />
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h3 class="text-lg font-bold text-white">Rejection Recovery & Grievance Navigator</h3>
              <span class="text-xs px-2 py-0.5 rounded-full bg-rose-500/30 text-rose-200 border border-rose-400/40 font-mono">
                RTS Act 2015
              </span>
            </div>
            <p class="text-xs text-rose-200 mt-0.5">Translate college scrutiny queries, explain resubmission windows, and recover rejected applications</p>
          </div>
        </div>
        <button @click="emit('close')" class="text-slate-400 hover:text-white p-1 rounded-lg transition-colors">
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Scrutiny Selector Tabs -->
      <div class="p-4 bg-slate-50 border-b border-slate-200 space-y-3">
        <div class="flex items-center justify-between">
          <label class="text-xs font-bold text-slate-700 uppercase tracking-wider">
            Select Scrutiny Remark Received:
          </label>
          <button 
            @click="isCustomMode = !isCustomMode; if (isCustomMode) { recoveryData = null; } else { loadRecoveryPlan(); }"
            class="text-xs text-indigo-600 font-semibold hover:underline"
          >
            {{ isCustomMode ? '← Pick from Common Scenarios' : 'Or enter custom remark from clerk →' }}
          </button>
        </div>

        <div v-if="!isCustomMode" class="grid grid-cols-1 sm:grid-cols-2 gap-2">
          <button 
            v-for="sc in scenarios" 
            :key="sc.code"
            @click="selectedCode = sc.code; loadRecoveryPlan()"
            class="text-left p-2.5 rounded-xl border text-xs transition-all flex items-start gap-2"
            :class="selectedCode === sc.code 
              ? 'bg-rose-50 border-rose-300 text-rose-950 font-semibold shadow-xs' 
              : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-100/60'"
          >
            <AlertOctagon class="w-4 h-4 shrink-0 mt-0.5" :class="selectedCode === sc.code ? 'text-rose-600' : 'text-slate-400'" />
            <span class="line-clamp-2">{{ sc.title }}</span>
          </button>
        </div>

        <div v-else class="space-y-2">
          <textarea 
            v-model="customRemark" 
            rows="2"
            placeholder="e.g. Scrutiny query: Caste validity certificate not attached for B.Tech admission..."
            class="w-full text-xs p-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-rose-500"
          ></textarea>
          <div class="flex justify-end">
            <button 
              @click="loadRecoveryPlan" 
              class="px-4 py-1.5 rounded-lg text-xs font-bold bg-rose-600 text-white hover:bg-rose-700 transition-colors"
            >
              Diagnose Custom Remark
            </button>
          </div>
        </div>
      </div>

      <!-- Recovery Content -->
      <div class="p-6 max-h-[60vh] overflow-y-auto space-y-6">
        <div v-if="isLoading" class="py-12 flex flex-col items-center justify-center text-center space-y-3">
          <Loader2 class="w-8 h-8 text-rose-600 animate-spin" />
          <p class="text-sm font-semibold text-slate-800">Analyzing Scrutiny Case & Statutory Routes...</p>
        </div>

        <div v-else-if="recoveryData?.diagnosis" class="space-y-6">
          <!-- 15-Day Resubmission Window Badge -->
          <div 
            class="p-4 rounded-xl border flex items-start justify-between"
            :class="recoveryData.diagnosis.can_resubmit_in_scrutiny_window 
              ? 'bg-emerald-50 border-emerald-200' 
              : 'bg-rose-50 border-rose-200'"
          >
            <div class="space-y-1">
              <div class="flex items-center gap-2">
                <span 
                  class="text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded-full"
                  :class="recoveryData.diagnosis.can_resubmit_in_scrutiny_window 
                    ? 'bg-emerald-200 text-emerald-900' 
                    : 'bg-rose-200 text-rose-900'"
                >
                  {{ recoveryData.diagnosis.can_resubmit_in_scrutiny_window ? '15-Day Resubmission Window Active' : 'Department Appeal Required' }}
                </span>
                <span class="text-xs text-slate-500">MahaDBT Operational Guidelines</span>
              </div>
              <p class="text-xs text-slate-700 leading-relaxed font-medium">
                {{ recoveryData.diagnosis.window_statutory_rule }}
              </p>
            </div>
            <div v-if="recoveryData.diagnosis.can_resubmit_in_scrutiny_window" class="text-right shrink-0 ml-4">
              <span class="text-2xl font-black text-emerald-700">{{ recoveryData.diagnosis.resubmission_window_days }}</span>
              <span class="text-[10px] text-slate-500 block">Days Window</span>
            </div>
          </div>

          <!-- Plain Language Translation -->
          <div class="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
            <h4 class="text-xs font-bold uppercase tracking-wider text-slate-800 flex items-center gap-1.5">
              <Scale class="w-4 h-4 text-indigo-600" />
              Plain-Language Explanation (What This Means)
            </h4>
            <p class="text-xs text-slate-700 leading-relaxed">
              {{ recoveryData.diagnosis.plain_language_explanation }}
            </p>
          </div>

          <!-- Document Procurement Remedy -->
          <div v-if="recoveryData.diagnosis.document_remedy" class="p-4 bg-blue-50/60 border border-blue-200 rounded-xl space-y-3">
            <h4 class="text-xs font-bold uppercase tracking-wider text-blue-900 flex items-center gap-1.5">
              <FileCheck2 class="w-4 h-4 text-blue-700" />
              Document Procurement Remedy
            </h4>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
              <div class="bg-white p-2.5 rounded-lg border border-blue-100">
                <span class="text-[10px] text-slate-500 block">Required Document</span>
                <span class="font-bold text-slate-900 line-clamp-1">{{ recoveryData.diagnosis.document_remedy.name }}</span>
              </div>
              <div class="bg-white p-2.5 rounded-lg border border-blue-100">
                <span class="text-[10px] text-slate-500 block">Issuing Authority</span>
                <span class="font-bold text-slate-900 line-clamp-1">{{ recoveryData.diagnosis.document_remedy.issuing_authority }}</span>
              </div>
              <div class="bg-white p-2.5 rounded-lg border border-blue-100">
                <span class="text-[10px] text-slate-500 block">RTS SLA Period</span>
                <span class="font-bold text-slate-900">{{ recoveryData.diagnosis.document_remedy.sla_days }} Days</span>
              </div>
              <div class="bg-white p-2.5 rounded-lg border border-blue-100">
                <span class="text-[10px] text-slate-500 block">Statutory Fee</span>
                <span class="font-bold text-slate-900">₹{{ recoveryData.diagnosis.document_remedy.statutory_fee_inr }}</span>
              </div>
            </div>
            <div class="flex justify-end">
              <a 
                :href="recoveryData.diagnosis.document_remedy.portal" 
                target="_blank" 
                rel="noopener noreferrer"
                class="inline-flex items-center gap-1.5 text-xs font-bold text-blue-700 hover:text-blue-900"
              >
                <span>Apply on Aaple Sarkar Portal</span>
                <ExternalLink class="w-3 h-3" />
              </a>
            </div>
          </div>

          <!-- Step-by-Step Corrective Actions -->
          <div class="space-y-2">
            <h4 class="text-xs font-bold uppercase tracking-wider text-slate-800 flex items-center gap-1.5">
              <Clock class="w-4 h-4 text-slate-600" />
              Immediate Recovery Steps
            </h4>
            <ol class="space-y-2 text-xs text-slate-700 list-decimal list-inside bg-slate-50 p-4 rounded-xl border border-slate-200">
              <li v-for="(act, idx) in recoveryData.diagnosis.corrective_actions" :key="idx" class="leading-relaxed">
                <span class="text-slate-900 font-medium">{{ act }}</span>
              </li>
            </ol>
          </div>

          <!-- Official Grievance & Appeal Route -->
          <div v-if="recoveryData.diagnosis.official_appeal_route?.applicable" class="p-4 bg-amber-50/70 border border-amber-200 rounded-xl space-y-2.5">
            <div class="flex items-center justify-between">
              <h4 class="text-xs font-bold uppercase tracking-wider text-amber-900 flex items-center gap-1.5">
                <Building2 class="w-4 h-4 text-amber-700" />
                Statutory Appeal Route (Maharashtra RTS Act 2015)
              </h4>
              <span class="text-[10px] bg-amber-200/80 text-amber-900 px-2 py-0.5 rounded font-mono font-bold">
                Appellate Authority
              </span>
            </div>
            <p class="text-xs text-slate-700">
              <strong>When applicable:</strong> {{ recoveryData.diagnosis.official_appeal_route.condition }}
            </p>
            <div class="p-3 bg-white/90 rounded-lg border border-amber-200 text-xs space-y-1">
              <div><strong>Appellate Officer:</strong> {{ recoveryData.diagnosis.official_appeal_route.authority_name }}</div>
              <div><strong>Department:</strong> {{ recoveryData.diagnosis.official_appeal_route.department }}</div>
              <div><strong>Statutory Deadline:</strong> {{ recoveryData.diagnosis.official_appeal_route.statutory_deadline }}</div>
            </div>
            <div class="flex justify-end pt-1">
              <a 
                :href="recoveryData.diagnosis.official_appeal_route.official_portal" 
                target="_blank" 
                rel="noopener noreferrer"
                class="inline-flex items-center gap-1.5 text-xs font-bold text-amber-800 hover:text-amber-950"
              >
                <span>Lodge Grievance on grievance.maharashtra.gov.in</span>
                <ExternalLink class="w-3 h-3" />
              </a>
            </div>
          </div>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="px-6 py-4 bg-slate-50 border-t border-slate-200 flex items-center justify-between">
        <button 
          @click="emit('close')" 
          class="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-slate-200 transition-colors"
        >
          Close Navigator
        </button>

        <a 
          href="https://mahadbt.maharashtra.gov.in" 
          target="_blank" 
          rel="noopener noreferrer"
          class="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold text-white bg-slate-900 hover:bg-black shadow-sm transition-colors"
        >
          <span>Open MahaDBT Portal</span>
          <ExternalLink class="w-3.5 h-3.5" />
        </a>
      </div>
    </div>
  </div>
</template>
