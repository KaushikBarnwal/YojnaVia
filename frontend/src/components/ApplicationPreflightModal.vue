<script setup lang="ts">
import { ref, watch } from 'vue';
import api from '../services/api';
import { useStudentStore } from '../stores/studentStore';
import { 
  X, 
  ShieldAlert, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  ExternalLink,
  Loader2,
  FileText,
  Clock,
  ArrowRight
} from '@lucide/vue';

const props = defineProps<{
  isOpen: boolean;
  schemeCode: string;
  schemeTitle?: string;
  officialUrl?: string;
  checkedDocs?: Record<string, boolean>;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
}>();

const store = useStudentStore();
const isLoading = ref(false);
const preflightData = ref<any>(null);
const errorMessage = ref<string | null>(null);

async function runPreflight() {
  if (!props.schemeCode) return;
  isLoading.value = true;
  errorMessage.value = null;
  try {
    const checkedDocCodes = props.checkedDocs
      ? Object.entries(props.checkedDocs).filter(([_, v]) => v).map(([k]) => k)
      : [];

    const res = await api.post('/eligibility/preflight/', {
      scheme_code: props.schemeCode,
      session_token: store.sessionToken,
      checked_documents: checkedDocCodes
    });
    preflightData.value = res.data;
  } catch (err: any) {
    console.error('Preflight audit failed:', err);
    errorMessage.value = err.response?.data?.error || 'Failed to complete preflight audit.';
  } finally {
    isLoading.value = false;
  }
}

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      runPreflight();
    } else {
      preflightData.value = null;
      errorMessage.value = null;
    }
  }
);
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto bg-[#0B132B]/70 backdrop-blur-xs flex items-center justify-center p-4">
    <div class="bg-[#FBFBFA] rounded-xl max-w-2xl w-full shadow-[4px_4px_0_0_#0B132B] border-[2px] border-[#0B132B] overflow-hidden my-8">
      <!-- Modal Header -->
      <div class="px-6 py-5 bg-[#0B132B] text-white flex items-center justify-between border-b-[1.5px] border-[#0B132B]">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-[#1C2541] border border-slate-700 rounded-lg">
            <ShieldCheck class="w-6 h-6 text-[#F59E0B]" />
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h3 class="text-lg font-black text-white">Application Preflight Audit</h3>
              <span class="text-xs px-2 py-0.5 rounded-sm bg-[#1C2541] text-[#FBBF24] border border-[#D97706] font-mono font-bold">
                Deterministic
              </span>
            </div>
            <p class="text-xs text-slate-300 mt-0.5">Pre-submission verification against MahaDBT scrutiny rules</p>
          </div>
        </div>
        <button @click="emit('close')" class="text-slate-400 hover:text-white p-1 rounded-lg transition-colors cursor-pointer">
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Scheme Context Bar -->
      <div class="px-6 py-3 bg-[#F1F5F9] border-b-[1.5px] border-[#0B132B] flex items-center justify-between text-xs text-[#475569]">
        <div>
          <span class="font-bold text-[#0B132B]">{{ schemeTitle || schemeCode }}</span>
          <span class="font-mono text-[#64748B] ml-1.5">({{ schemeCode }})</span>
        </div>
        <div class="flex items-center gap-1.5 text-[#0B132B] font-bold">
          <Clock class="w-3.5 h-3.5 text-[#D97706]" />
          Target: MahaDBT Portal
        </div>
      </div>

      <!-- Modal Body -->
      <div class="p-6 max-h-[70vh] overflow-y-auto space-y-6">
        <!-- Loading State -->
        <div v-if="isLoading" class="py-12 flex flex-col items-center justify-center text-center space-y-3">
          <Loader2 class="w-8 h-8 text-[#0B132B] animate-spin" />
          <p class="text-sm font-bold text-[#0B132B]">Running 6-Point Scrutiny Audit...</p>
          <p class="text-xs text-[#64748B] max-w-sm">Checking civil certificate financial years, admission quota eligibility, issuing authorities and mandatory document trees.</p>
        </div>

        <!-- Error State -->
        <div v-else-if="errorMessage" class="p-4 bg-[#FEF2F2] border-[1.5px] border-[#DC2626] rounded-lg text-xs text-[#991B1B] flex items-start gap-3 shadow-[2px_2px_0_0_#DC2626]">
          <ShieldAlert class="w-5 h-5 text-[#DC2626] shrink-0 mt-0.5" />
          <div>
            <p class="font-black">Audit Check Failed</p>
            <p class="text-xs mt-1">{{ errorMessage }}</p>
          </div>
        </div>

        <!-- Audit Results Content -->
        <div v-else-if="preflightData" class="space-y-6">
          <!-- Score Banner -->
          <div 
            class="p-5 rounded-lg border-[1.5px] border-[#0B132B] shadow-[2.5px_2.5px_0_0_#0B132B] flex items-center justify-between"
            :class="{
              'bg-[#ECFDF5]': preflightData.status === 'READY',
              'bg-[#FEF3C7]': preflightData.status === 'WARNINGS',
              'bg-[#FEF2F2]': preflightData.status === 'BLOCKED'
            }"
          >
            <div class="space-y-1">
              <div class="flex items-center gap-2">
                <span 
                  class="text-xs font-black uppercase tracking-wider px-2.5 py-0.5 rounded-sm border border-[#0B132B]"
                  :class="{
                    'bg-[#D1FAE5] text-[#065F46]': preflightData.status === 'READY',
                    'bg-[#FDE68A] text-[#92400E]': preflightData.status === 'WARNINGS',
                    'bg-[#FEE2E2] text-[#991B1B]': preflightData.status === 'BLOCKED'
                  }"
                >
                  {{ preflightData.status === 'READY' ? 'Ready to Submit' : preflightData.status === 'WARNINGS' ? 'Advisory Warnings' : 'Scrutiny Blockers' }}
                </span>
                <span class="text-xs font-bold text-[#64748B]">Readiness Evaluation</span>
              </div>
              <h4 class="text-base font-black text-[#0B132B]">
                {{ preflightData.status === 'READY' 
                    ? 'Application looks solid for portal submission.' 
                    : preflightData.status === 'WARNINGS' 
                      ? 'Minor items should be double-checked before upload.' 
                      : 'Fatal issues detected that will trigger scrutiny rejection.' }}
              </h4>
            </div>

            <div class="flex items-center gap-3">
              <div class="text-right">
                <div class="text-3xl font-black font-mono" :class="{
                  'text-[#059669]': preflightData.status === 'READY',
                  'text-[#D97706]': preflightData.status === 'WARNINGS',
                  'text-[#DC2626]': preflightData.status === 'BLOCKED'
                }">
                  {{ preflightData.readiness_score_pct }}%
                </div>
                <div class="text-[10px] font-bold text-[#64748B] uppercase">Readiness Score</div>
              </div>
            </div>
          </div>

          <!-- Section 1: Fatal Blockers -->
          <div v-if="preflightData.blockers && preflightData.blockers.length > 0" class="space-y-3">
            <h5 class="text-xs font-black uppercase tracking-wider text-[#991B1B] flex items-center gap-1.5">
              <ShieldAlert class="w-4 h-4 text-[#DC2626]" />
              Scrutiny Blockers (Must resolve before submission)
            </h5>
            <div class="space-y-2.5">
              <div 
                v-for="(blocker, idx) in preflightData.blockers" 
                :key="idx"
                class="p-4 bg-white border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#DC2626] rounded-lg space-y-2 text-xs"
              >
                <div class="flex items-start justify-between">
                  <div class="font-black text-[#991B1B] text-sm flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-[#DC2626] shrink-0"></span>
                    {{ blocker.title }}
                  </div>
                  <span v-if="blocker.rule_basis" class="text-[10px] bg-[#FEE2E2] text-[#991B1B] px-2 py-0.5 rounded-sm font-mono font-bold border border-[#DC2626]">
                    {{ blocker.rule_basis }}
                  </span>
                </div>
                <p class="text-[#334155] leading-relaxed">{{ blocker.description }}</p>
                <div v-if="blocker.resolution" class="p-2.5 bg-[#FEF2F2] rounded-md border border-[#FCA5A5] text-[#991B1B] font-bold flex items-start gap-2">
                  <ArrowRight class="w-3.5 h-3.5 text-[#DC2626] shrink-0 mt-0.5" />
                  <span><strong>Fix:</strong> {{ blocker.resolution }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Section 2: Scrutiny Warnings -->
          <div v-if="preflightData.warnings && preflightData.warnings.length > 0" class="space-y-3">
            <h5 class="text-xs font-black uppercase tracking-wider text-[#92400E] flex items-center gap-1.5">
              <AlertTriangle class="w-4 h-4 text-[#D97706]" />
              Scrutiny Advisories (Potential Query Risks)
            </h5>
            <div class="space-y-2.5">
              <div 
                v-for="(warning, idx) in preflightData.warnings" 
                :key="idx"
                class="p-3.5 bg-white border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#D97706] rounded-lg space-y-1.5 text-xs"
              >
                <div class="font-black text-[#92400E] text-xs flex items-center gap-2">
                  <span class="w-1.5 h-1.5 rounded-full bg-[#D97706] shrink-0"></span>
                  {{ warning.title }}
                </div>
                <p class="text-[#334155] leading-relaxed">{{ warning.description }}</p>
                <div v-if="warning.recommendation" class="text-[#78350F] bg-[#FEF3C7] p-2 rounded-md border border-[#FCD34D] font-bold">
                  <strong>Recommendation:</strong> {{ warning.recommendation }}
                </div>
              </div>
            </div>
          </div>

          <!-- Section 3: Cleared Checks -->
          <div v-if="preflightData.cleared_checks && preflightData.cleared_checks.length > 0" class="space-y-3">
            <h5 class="text-xs font-black uppercase tracking-wider text-[#065F46] flex items-center gap-1.5">
              <CheckCircle2 class="w-4 h-4 text-[#059669]" />
              Verified & Cleared Requirements ({{ preflightData.cleared_checks.length }})
            </h5>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <div 
                v-for="(cleared, idx) in preflightData.cleared_checks" 
                :key="idx"
                class="p-2.5 bg-white border border-[#059669] rounded-md flex items-center gap-2 text-xs text-[#065F46] font-bold shadow-[1px_1px_0_0_#059669]"
              >
                <CheckCircle2 class="w-4 h-4 text-[#059669] shrink-0" />
                <span class="truncate">{{ cleared }}</span>
              </div>
            </div>
          </div>

          <!-- Section 4: Action Plan -->
          <div v-if="preflightData.action_plan && preflightData.action_plan.length > 0" class="p-4 bg-white border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#0B132B] rounded-lg space-y-2">
            <h5 class="text-xs font-black uppercase tracking-wider text-[#0B132B] flex items-center gap-1.5">
              <FileText class="w-4 h-4 text-[#0B132B]" />
              Immediate Preparation Action Plan
            </h5>
            <ol class="space-y-2 text-xs text-[#334155] list-decimal list-inside font-medium">
              <li v-for="(action, idx) in preflightData.action_plan" :key="idx" class="leading-relaxed">
                <span class="font-bold text-[#0B132B]">{{ action }}</span>
              </li>
            </ol>
          </div>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="px-6 py-4 bg-[#F1F5F9] border-t-[1.5px] border-[#0B132B] flex items-center justify-between">
        <button 
          @click="emit('close')" 
          class="px-4 py-2 rounded-lg text-xs font-black text-[#0B132B] bg-white border-[1.5px] border-[#0B132B] shadow-[1.5px_1.5px_0_0_#0B132B] hover:bg-slate-100 transition-colors cursor-pointer"
        >
          Close Audit
        </button>

        <a 
          v-if="officialUrl"
          :href="officialUrl" 
          target="_blank" 
          rel="noopener noreferrer"
          class="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-black text-white bg-[#0B132B] hover:bg-[#1C2541] border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#D97706] transition-colors cursor-pointer"
        >
          <span>Open Official Portal</span>
          <ExternalLink class="w-3.5 h-3.5 text-[#F59E0B]" />
        </a>
      </div>
    </div>
  </div>
</template>
