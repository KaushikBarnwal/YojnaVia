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
  <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl max-w-2xl w-full shadow-2xl border border-slate-200 overflow-hidden my-8">
      <!-- Modal Header -->
      <div class="px-6 py-5 bg-gradient-to-r from-slate-900 to-indigo-950 text-white flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-indigo-500/20 border border-indigo-400/30 rounded-lg">
            <ShieldCheck class="w-6 h-6 text-indigo-300" />
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h3 class="text-lg font-bold text-white">Application Preflight Audit</h3>
              <span class="text-xs px-2 py-0.5 rounded-full bg-indigo-500/30 text-indigo-200 border border-indigo-400/40 font-mono">
                Deterministic
              </span>
            </div>
            <p class="text-xs text-slate-300 mt-0.5">Pre-submission verification against MahaDBT scrutiny rules</p>
          </div>
        </div>
        <button @click="emit('close')" class="text-slate-400 hover:text-white p-1 rounded-lg transition-colors">
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Scheme Context Bar -->
      <div class="px-6 py-3 bg-slate-50 border-b border-slate-200 flex items-center justify-between text-xs text-slate-600">
        <div>
          <span class="font-medium text-slate-900">{{ schemeTitle || schemeCode }}</span>
          <span class="font-mono text-slate-400 ml-1.5">({{ schemeCode }})</span>
        </div>
        <div class="flex items-center gap-1.5 text-slate-500 font-medium">
          <Clock class="w-3.5 h-3.5" />
          Target: MahaDBT Portal
        </div>
      </div>

      <!-- Modal Body -->
      <div class="p-6 max-h-[70vh] overflow-y-auto space-y-6">
        <!-- Loading State -->
        <div v-if="isLoading" class="py-12 flex flex-col items-center justify-center text-center space-y-3">
          <Loader2 class="w-8 h-8 text-indigo-600 animate-spin" />
          <p class="text-sm font-semibold text-slate-800">Running 6-Point Scrutiny Audit...</p>
          <p class="text-xs text-slate-500 max-w-sm">Checking civil certificate financial years, admission quota eligibility, issuing authorities and mandatory document trees.</p>
        </div>

        <!-- Error State -->
        <div v-else-if="errorMessage" class="p-4 bg-rose-50 border border-rose-200 rounded-xl text-sm text-rose-700 flex items-start gap-3">
          <ShieldAlert class="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
          <div>
            <p class="font-semibold">Audit Check Failed</p>
            <p class="text-xs mt-1">{{ errorMessage }}</p>
          </div>
        </div>

        <!-- Audit Results Content -->
        <div v-else-if="preflightData" class="space-y-6">
          <!-- Score Banner -->
          <div 
            class="p-5 rounded-2xl border flex items-center justify-between"
            :class="{
              'bg-emerald-50/70 border-emerald-200': preflightData.status === 'READY',
              'bg-amber-50/70 border-amber-200': preflightData.status === 'WARNINGS',
              'bg-rose-50/70 border-rose-200': preflightData.status === 'BLOCKED'
            }"
          >
            <div class="space-y-1">
              <div class="flex items-center gap-2">
                <span 
                  class="text-xs font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full"
                  :class="{
                    'bg-emerald-200 text-emerald-900': preflightData.status === 'READY',
                    'bg-amber-200 text-amber-900': preflightData.status === 'WARNINGS',
                    'bg-rose-200 text-rose-900': preflightData.status === 'BLOCKED'
                  }"
                >
                  {{ preflightData.status === 'READY' ? 'Ready to Submit' : preflightData.status === 'WARNINGS' ? 'Advisory Warnings' : 'Scrutiny Blockers' }}
                </span>
                <span class="text-xs text-slate-500">Readiness Evaluation</span>
              </div>
              <h4 class="text-base font-bold text-slate-900">
                {{ preflightData.status === 'READY' 
                    ? 'Application looks solid for portal submission.' 
                    : preflightData.status === 'WARNINGS' 
                      ? 'Minor items should be double-checked before upload.' 
                      : 'Fatal issues detected that will trigger scrutiny rejection.' }}
              </h4>
            </div>

            <div class="flex items-center gap-3">
              <div class="text-right">
                <div class="text-3xl font-black" :class="{
                  'text-emerald-700': preflightData.status === 'READY',
                  'text-amber-700': preflightData.status === 'WARNINGS',
                  'text-rose-700': preflightData.status === 'BLOCKED'
                }">
                  {{ preflightData.readiness_score_pct }}%
                </div>
                <div class="text-[10px] font-medium text-slate-500">Readiness Score</div>
              </div>
            </div>
          </div>

          <!-- Section 1: Fatal Blockers -->
          <div v-if="preflightData.blockers && preflightData.blockers.length > 0" class="space-y-3">
            <h5 class="text-xs font-bold uppercase tracking-wider text-rose-700 flex items-center gap-1.5">
              <ShieldAlert class="w-4 h-4 text-rose-600" />
              Scrutiny Blockers (Must resolve before submission)
            </h5>
            <div class="space-y-2.5">
              <div 
                v-for="(blocker, idx) in preflightData.blockers" 
                :key="idx"
                class="p-4 bg-rose-50/80 border border-rose-200 rounded-xl space-y-2 text-xs"
              >
                <div class="flex items-start justify-between">
                  <div class="font-bold text-rose-900 text-sm flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-rose-600 shrink-0"></span>
                    {{ blocker.title }}
                  </div>
                  <span v-if="blocker.rule_basis" class="text-[10px] bg-rose-200/70 text-rose-800 px-2 py-0.5 rounded font-mono">
                    {{ blocker.rule_basis }}
                  </span>
                </div>
                <p class="text-rose-800 leading-relaxed">{{ blocker.description }}</p>
                <div v-if="blocker.resolution" class="p-2.5 bg-white/80 rounded-lg border border-rose-200 text-slate-800 font-medium flex items-start gap-2">
                  <ArrowRight class="w-3.5 h-3.5 text-rose-600 shrink-0 mt-0.5" />
                  <span><strong>Fix:</strong> {{ blocker.resolution }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Section 2: Scrutiny Warnings -->
          <div v-if="preflightData.warnings && preflightData.warnings.length > 0" class="space-y-3">
            <h5 class="text-xs font-bold uppercase tracking-wider text-amber-700 flex items-center gap-1.5">
              <AlertTriangle class="w-4 h-4 text-amber-600" />
              Scrutiny Advisories (Potential Query Risks)
            </h5>
            <div class="space-y-2.5">
              <div 
                v-for="(warning, idx) in preflightData.warnings" 
                :key="idx"
                class="p-3.5 bg-amber-50/80 border border-amber-200 rounded-xl space-y-1.5 text-xs"
              >
                <div class="font-bold text-amber-900 text-xs flex items-center gap-2">
                  <span class="w-1.5 h-1.5 rounded-full bg-amber-500 shrink-0"></span>
                  {{ warning.title }}
                </div>
                <p class="text-amber-800 leading-relaxed">{{ warning.description }}</p>
                <div v-if="warning.recommendation" class="text-slate-700 bg-white/70 p-2 rounded border border-amber-200 font-medium">
                  <strong>Recommendation:</strong> {{ warning.recommendation }}
                </div>
              </div>
            </div>
          </div>

          <!-- Section 3: Cleared Checks -->
          <div v-if="preflightData.cleared_checks && preflightData.cleared_checks.length > 0" class="space-y-3">
            <h5 class="text-xs font-bold uppercase tracking-wider text-emerald-700 flex items-center gap-1.5">
              <CheckCircle2 class="w-4 h-4 text-emerald-600" />
              Verified & Cleared Requirements ({{ preflightData.cleared_checks.length }})
            </h5>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <div 
                v-for="(cleared, idx) in preflightData.cleared_checks" 
                :key="idx"
                class="p-2.5 bg-emerald-50/50 border border-emerald-200/70 rounded-lg flex items-center gap-2 text-xs text-emerald-900"
              >
                <CheckCircle2 class="w-4 h-4 text-emerald-600 shrink-0" />
                <span class="font-medium truncate">{{ cleared }}</span>
              </div>
            </div>
          </div>

          <!-- Section 4: Action Plan -->
          <div v-if="preflightData.action_plan && preflightData.action_plan.length > 0" class="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
            <h5 class="text-xs font-bold uppercase tracking-wider text-slate-800 flex items-center gap-1.5">
              <FileText class="w-4 h-4 text-slate-600" />
              Immediate Preparation Action Plan
            </h5>
            <ol class="space-y-2 text-xs text-slate-700 list-decimal list-inside">
              <li v-for="(action, idx) in preflightData.action_plan" :key="idx" class="leading-relaxed">
                <span class="font-medium text-slate-900">{{ action }}</span>
              </li>
            </ol>
          </div>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="px-6 py-4 bg-slate-50 border-t border-slate-200 flex items-center justify-between">
        <button 
          @click="emit('close')" 
          class="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-slate-200 transition-colors"
        >
          Close Audit
        </button>

        <a 
          v-if="officialUrl"
          :href="officialUrl" 
          target="_blank" 
          rel="noopener noreferrer"
          class="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 shadow-sm transition-colors"
        >
          <span>Open Official Portal</span>
          <ExternalLink class="w-3.5 h-3.5" />
        </a>
      </div>
    </div>
  </div>
</template>
