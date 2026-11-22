<script setup lang="ts">
import { ref, watch } from 'vue';
import api from '../services/api';
import { useStudentStore } from '../stores/studentStore';
import { 
  X, 
  Map, 
  CheckCircle2, 
  Clock, 
  RotateCcw, 
  ExternalLink, 
  ShieldAlert,
  Loader2,
  Info
} from '@lucide/vue';

const props = defineProps<{
  isOpen: boolean;
  schemeCode: string;
  schemeName?: string;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
}>();

const store = useStudentStore();
const isLoading = ref(false);
const roadmapData = ref<any>(null);
const errorMessage = ref<string | null>(null);

async function fetchRoadmap() {
  if (!props.schemeCode) return;
  isLoading.value = true;
  errorMessage.value = null;
  try {
    const res = await api.get(`/tracker/lifecycle/roadmap/?session_token=${store.sessionToken}&scheme_code=${props.schemeCode}`);
    roadmapData.value = res.data;
  } catch (err: any) {
    console.error('Failed to load lifecycle roadmap:', err);
    errorMessage.value = err.response?.data?.error || 'Failed to load entitlement roadmap.';
  } finally {
    isLoading.value = false;
  }
}

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      fetchRoadmap();
    } else {
      roadmapData.value = null;
      errorMessage.value = null;
    }
  }
);
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
    <div class="bg-white rounded-3xl max-w-3xl w-full shadow-2xl border border-slate-200 overflow-hidden my-8">
      <!-- Modal Header -->
      <div class="px-6 py-5 bg-gradient-to-r from-slate-900 to-indigo-950 text-white flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-indigo-500/20 border border-indigo-400/30 rounded-xl">
            <Map class="w-6 h-6 text-indigo-300" />
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h3 class="text-lg font-bold text-white">Entitlement Lifecycle Roadmap</h3>
              <span class="text-xs px-2.5 py-0.5 rounded-full bg-indigo-500/30 text-indigo-200 border border-indigo-400/40 font-mono">
                Discover → Renew
              </span>
            </div>
            <p class="text-xs text-slate-300 mt-0.5">Full multi-year application journey, milestones, and statutory renewal schedules</p>
          </div>
        </div>
        <button @click="emit('close')" class="text-slate-400 hover:text-white p-1 rounded-lg transition-colors">
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Scheme Context Banner -->
      <div class="px-6 py-3 bg-slate-50 border-b border-slate-200 flex items-center justify-between text-xs text-slate-600">
        <div>
          <span class="font-bold text-slate-900">{{ schemeName || schemeCode }}</span>
          <span class="font-mono text-slate-400 ml-1.5">({{ schemeCode }})</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-slate-500 font-medium">Application Ref:</span>
          <span class="font-mono font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-100">
            {{ roadmapData?.application_reference_number || 'Pending Submission' }}
          </span>
        </div>
      </div>

      <!-- Modal Body -->
      <div class="p-6 max-h-[70vh] overflow-y-auto space-y-6">
        <div v-if="isLoading" class="py-12 flex flex-col items-center justify-center text-center space-y-3">
          <Loader2 class="w-8 h-8 text-indigo-600 animate-spin" />
          <p class="text-sm font-semibold text-slate-800">Calculating Lifecycle Stages & Renewal Dates...</p>
        </div>

        <div v-else-if="errorMessage" class="p-4 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800 flex items-start gap-2">
          <ShieldAlert class="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
          <div>{{ errorMessage }}</div>
        </div>

        <div v-else-if="roadmapData" class="space-y-6">
          <!-- Mandatory User-Reported Notice -->
          <div class="p-3.5 rounded-xl bg-blue-50 border border-blue-200 text-blue-950 text-xs font-medium flex items-start gap-2.5">
            <Info class="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
            <p class="leading-relaxed">
              {{ roadmapData.official_vs_user_reported_notice }}
            </p>
          </div>

          <!-- 6-Stage Visual Journey Stepper -->
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <h4 class="text-xs font-bold uppercase tracking-wider text-slate-700">
                The 6 Lifecycle Stages
              </h4>
              <span class="text-xs font-bold text-indigo-600">
                Progress: Stage {{ roadmapData.current_stage_order }} of 6 ({{ roadmapData.progress_pct }}%)
              </span>
            </div>

            <!-- Horizontal Stepper (Desktop) -->
            <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
              <div 
                v-for="stg in roadmapData.lifecycle_milestones" 
                :key="stg.id"
                class="p-3 rounded-xl border flex flex-col justify-between text-xs transition-all space-y-2"
                :class="stg.is_current 
                  ? 'bg-indigo-600 text-white border-indigo-600 shadow-md ring-2 ring-indigo-300' 
                  : stg.is_completed 
                    ? 'bg-emerald-50 text-emerald-950 border-emerald-200' 
                    : 'bg-slate-50 text-slate-600 border-slate-200'"
              >
                <div>
                  <div class="flex items-center justify-between pb-1">
                    <span class="text-[10px] font-bold uppercase tracking-wider opacity-80">Stage {{ stg.order }}</span>
                    <CheckCircle2 v-if="stg.is_completed" class="w-3.5 h-3.5 text-emerald-600" />
                    <Clock v-else-if="stg.is_current" class="w-3.5 h-3.5 text-indigo-200 animate-pulse" />
                  </div>
                  <div class="font-bold leading-tight">{{ stg.name }}</div>
                </div>
                <div class="text-[10px] opacity-75 leading-tight pt-1 border-t border-black/10">
                  {{ stg.typical_duration }}
                </div>
              </div>
            </div>
          </div>

          <!-- Active Stage Detailed Breakdown & Action Plan -->
          <div class="p-5 bg-gradient-to-r from-slate-50 to-indigo-50/40 rounded-2xl border border-slate-200 space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold uppercase tracking-wider text-indigo-900 flex items-center gap-1.5">
                <Clock class="w-4 h-4 text-indigo-600" />
                <span>Your Next Immediate Milestone Action:</span>
              </span>
              <span class="text-[10px] font-bold bg-indigo-100 text-indigo-800 px-2 py-0.5 rounded">
                Self-Reported Next Step
              </span>
            </div>
            <p class="text-sm font-bold text-slate-900 leading-snug">
              {{ roadmapData.next_immediate_action }}
            </p>
          </div>

          <!-- Milestones Checklist for All Stages -->
          <div class="space-y-3">
            <h4 class="text-xs font-bold uppercase tracking-wider text-slate-700">
              Detailed Milestone Checklist by Lifecycle Phase
            </h4>
            <div class="space-y-3">
              <div 
                v-for="stg in roadmapData.lifecycle_milestones" 
                :key="'det-' + stg.id"
                class="p-4 rounded-2xl border space-y-2 text-xs"
                :class="stg.is_current ? 'bg-indigo-50/40 border-indigo-200' : 'bg-white border-slate-200'"
              >
                <div class="flex items-center justify-between">
                  <div class="font-bold text-slate-900 text-xs flex items-center gap-2">
                    <span 
                      class="w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold"
                      :class="stg.is_current ? 'bg-indigo-600 text-white' : stg.is_completed ? 'bg-emerald-600 text-white' : 'bg-slate-200 text-slate-700'"
                    >
                      {{ stg.order }}
                    </span>
                    <span>{{ stg.name }}</span>
                    <span class="text-slate-400 font-normal">({{ stg.tagline }})</span>
                  </div>
                  <span class="text-[10px] px-2 py-0.5 rounded font-bold uppercase"
                    :class="stg.is_current ? 'bg-indigo-100 text-indigo-800' : stg.is_completed ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-500'">
                    {{ stg.state }}
                  </span>
                </div>

                <p class="text-[11px] text-slate-600">{{ stg.description }}</p>

                <ul class="space-y-1.5 pt-1 pl-2">
                  <li v-for="(m, mIdx) in stg.milestones" :key="mIdx" class="flex items-start gap-2">
                    <CheckCircle2 class="w-3.5 h-3.5 shrink-0 mt-0.5" 
                      :class="stg.is_completed ? 'text-emerald-600' : stg.is_current ? 'text-indigo-600' : 'text-slate-300'" />
                    <span :class="stg.is_completed ? 'text-slate-600 line-through' : 'text-slate-800 font-medium'">
                      {{ m.label }}
                    </span>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Renewal & Reapplication Intelligence Cards -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Renewal Intelligence -->
            <div class="p-4 bg-emerald-50/70 border border-emerald-200 rounded-2xl space-y-2 text-xs">
              <div class="flex items-center gap-2 text-emerald-900 font-bold uppercase tracking-wider text-[11px]">
                <RotateCcw class="w-4 h-4 text-emerald-700" />
                <span>Annual Renewal Intelligence</span>
              </div>
              <div class="space-y-1.5 pt-1">
                <div class="flex justify-between">
                  <span class="text-slate-500">Frequency:</span>
                  <span class="font-bold text-slate-800">{{ roadmapData.renewal_intelligence.renewal_frequency }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-slate-500">Next Renewal Window:</span>
                  <span class="font-bold text-emerald-800">{{ roadmapData.renewal_intelligence.next_academic_renewal_window_opens }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-slate-500">Income Cert Expiry:</span>
                  <span class="font-bold text-amber-800 font-mono">{{ roadmapData.renewal_intelligence.income_certificate_renewal_deadline }}</span>
                </div>
                <p class="text-[11px] text-emerald-900/90 pt-1 border-t border-emerald-200/60 leading-relaxed">
                  {{ roadmapData.renewal_intelligence.renewal_notes }}
                </p>
              </div>
            </div>

            <!-- Reapplication Intelligence -->
            <div class="p-4 bg-amber-50/70 border border-amber-200 rounded-2xl space-y-2 text-xs">
              <div class="flex items-center gap-2 text-amber-900 font-bold uppercase tracking-wider text-[11px]">
                <Clock class="w-4 h-4 text-amber-700" />
                <span>Reapplication & Appeals Guidance</span>
              </div>
              <div class="space-y-1.5 pt-1">
                <div class="flex justify-between">
                  <span class="text-slate-500">15-Day Scrutiny Window:</span>
                  <span class="font-bold text-amber-900">
                    {{ roadmapData.reapplication_intelligence.is_scrutiny_window_active ? 'Active (15 Days Left)' : 'Standard Portal Rules' }}
                  </span>
                </div>
                <div class="flex justify-between">
                  <span class="text-slate-500">Next Fresh Cycle:</span>
                  <span class="font-bold text-slate-800">{{ roadmapData.reapplication_intelligence.next_fresh_admission_cycle }}</span>
                </div>
                <div class="pt-1 border-t border-amber-200/60 text-[11px] text-amber-950 leading-relaxed">
                  <strong>Statutory Remedy:</strong> {{ roadmapData.reapplication_intelligence.appeal_route }}
                </div>
              </div>
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
          Close Roadmap
        </button>

        <a 
          v-if="roadmapData?.official_portal_url"
          :href="roadmapData.official_portal_url" 
          target="_blank" 
          rel="noopener noreferrer"
          class="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 shadow-sm transition-colors"
        >
          <span>Open {{ roadmapData.portal_name || 'MahaDBT' }} Portal</span>
          <ExternalLink class="w-3.5 h-3.5" />
        </a>
      </div>
    </div>
  </div>
</template>
