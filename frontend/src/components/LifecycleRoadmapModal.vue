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
    errorMessage.value = err.response?.data?.error || 'Something went wrong. Please try again in a few minutes.';
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
  <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto bg-[#0B132B]/70 backdrop-blur-xs flex items-center justify-center p-4">
    <div class="bg-[#FBFBFA] rounded-xl max-w-3xl w-full shadow-[4px_4px_0_0_#0B132B] border-[2px] border-[#0B132B] overflow-hidden my-8">
      <!-- Modal Header -->
      <div class="px-6 py-5 bg-[#0B132B] text-white flex items-center justify-between border-b-[1.5px] border-[#0B132B]">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-[#1C2541] border border-slate-700 rounded-lg">
            <Map class="w-6 h-6 text-[#F59E0B]" />
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h3 class="text-lg font-black text-white">Your scholarship journey</h3>
              <span class="text-xs px-2.5 py-0.5 rounded-sm bg-[#1C2541] text-[#FBBF24] border border-[#D97706] font-mono font-bold">
                Discover → Renew
              </span>
            </div>
            <p class="text-xs text-slate-300 mt-0.5">The full journey over several years: steps, milestones and renewal dates</p>
          </div>
        </div>
        <button @click="emit('close')" class="text-slate-400 hover:text-white p-1 rounded-lg transition-colors cursor-pointer">
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Scheme Context Banner -->
      <div class="px-6 py-3 bg-[#F1F5F9] border-b-[1.5px] border-[#0B132B] flex items-center justify-between text-xs text-[#475569]">
        <div>
          <span class="font-bold text-[#0B132B]">{{ schemeName || schemeCode }}</span>
          <span class="font-mono text-[#64748B] ml-1.5">({{ schemeCode }})</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-[#475569] font-medium">Application number:</span>
          <span class="font-mono font-bold text-[#0B132B] bg-white px-2 py-0.5 rounded-sm border border-[#0B132B]">
            {{ roadmapData?.application_reference_number || 'Not submitted yet' }}
          </span>
        </div>
      </div>

      <!-- Modal Body -->
      <div class="p-6 max-h-[70vh] overflow-y-auto space-y-6">
        <div v-if="isLoading" class="py-12 flex flex-col items-center justify-center text-center space-y-3">
          <Loader2 class="w-8 h-8 text-[#0B132B] animate-spin" />
          <p class="text-sm font-bold text-[#0B132B]">Working out your stages and renewal dates...</p>
        </div>

        <div v-else-if="errorMessage" class="p-4 bg-[#FEF2F2] border-[1.5px] border-[#DC2626] rounded-lg text-xs text-[#991B1B] flex items-start gap-2 shadow-[2px_2px_0_0_#DC2626]">
          <ShieldAlert class="w-5 h-5 text-[#DC2626] shrink-0 mt-0.5" />
          <div>{{ errorMessage }}</div>
        </div>

        <div v-else-if="roadmapData" class="space-y-6">
          <!-- Mandatory User-Reported Notice -->
          <div class="p-3.5 rounded-lg bg-[#FEF3C7] border border-[#D97706] text-[#92400E] text-xs font-medium flex items-start gap-2.5">
            <Info class="w-4 h-4 text-[#D97706] shrink-0 mt-0.5" />
            <p class="leading-relaxed">
              {{ roadmapData.official_vs_user_reported_notice }}
            </p>
          </div>

          <!-- 6-Stage Visual Journey Stepper -->
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <h4 class="text-xs font-black uppercase tracking-wider text-[#0B132B]">
                The 6 stages
              </h4>
              <span class="text-xs font-black text-[#D97706]">
                Progress: Stage {{ roadmapData.current_stage_order }} of 6 ({{ roadmapData.progress_pct }}%)
              </span>
            </div>

            <!-- Horizontal Stepper (Desktop) -->
            <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
              <div 
                v-for="stg in roadmapData.lifecycle_milestones" 
                :key="stg.id"
                class="p-3 rounded-lg border-[1.5px] border-[#0B132B] flex flex-col justify-between text-xs transition-all space-y-2 shadow-[1.5px_1.5px_0_0_#0B132B]"
                :class="stg.is_current 
                  ? 'bg-[#0B132B] text-white shadow-[2.5px_2.5px_0_0_#D97706]' 
                  : stg.is_completed 
                    ? 'bg-[#ECFDF5] text-[#064E3B]' 
                    : 'bg-white text-[#475569]'"
              >
                <div>
                  <div class="flex items-center justify-between pb-1">
                    <span class="text-[10px] font-black uppercase tracking-wider opacity-80">Stage {{ stg.order }}</span>
                    <CheckCircle2 v-if="stg.is_completed" class="w-3.5 h-3.5 text-[#059669]" />
                    <Clock v-else-if="stg.is_current" class="w-3.5 h-3.5 text-[#F59E0B] animate-pulse" />
                  </div>
                  <div class="font-black leading-tight">{{ stg.name }}</div>
                </div>
                <div class="text-[10px] opacity-75 leading-tight pt-1 border-t border-black/10">
                  {{ stg.typical_duration }}
                </div>
              </div>
            </div>
          </div>

          <!-- Active Stage Detailed Breakdown & Action Plan -->
          <div class="p-5 bg-white rounded-lg border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#0B132B] space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-xs font-black uppercase tracking-wider text-[#0B132B] flex items-center gap-1.5">
                <Clock class="w-4 h-4 text-[#D97706]" />
                <span>Your next step:</span>
              </span>
              <span class="text-[10px] font-black bg-[#F1F5F9] text-[#0B132B] px-2 py-0.5 rounded-sm border border-[#CBD5E1]">
                Entered by you
              </span>
            </div>
            <p class="text-sm font-black text-[#0B132B] leading-snug">
              {{ roadmapData.next_immediate_action }}
            </p>
          </div>

          <!-- Milestones Checklist for All Stages -->
          <div class="space-y-3">
            <h4 class="text-xs font-black uppercase tracking-wider text-[#0B132B]">
              Checklist for each stage
            </h4>
            <div class="space-y-3">
              <div 
                v-for="stg in roadmapData.lifecycle_milestones" 
                :key="'det-' + stg.id"
                class="p-4 rounded-lg border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#0B132B] space-y-2 text-xs"
                :class="stg.is_current ? 'bg-[#FEF3C7]/40 border-[#0B132B]' : 'bg-white border-[#0B132B]'"
              >
                <div class="flex items-center justify-between">
                  <div class="font-black text-[#0B132B] text-xs flex items-center gap-2">
                    <span 
                      class="w-5 h-5 rounded-sm flex items-center justify-center text-[10px] font-black border border-[#0B132B]"
                      :class="stg.is_current ? 'bg-[#D97706] text-white' : stg.is_completed ? 'bg-[#059669] text-white' : 'bg-slate-200 text-slate-700'"
                    >
                      {{ stg.order }}
                    </span>
                    <span>{{ stg.name }}</span>
                    <span class="text-[#64748B] font-normal">({{ stg.tagline }})</span>
                  </div>
                  <span class="text-[10px] px-2 py-0.5 rounded-sm font-black uppercase border border-[#0B132B]"
                    :class="stg.is_current ? 'bg-[#FEF3C7] text-[#92400E]' : stg.is_completed ? 'bg-[#D1FAE5] text-[#065F46]' : 'bg-slate-100 text-slate-500'">
                    {{ stg.state }}
                  </span>
                </div>

                <p class="text-[11px] text-[#475569] font-medium">{{ stg.description }}</p>

                <ul class="space-y-1.5 pt-1 pl-2">
                  <li v-for="(m, mIdx) in stg.milestones" :key="mIdx" class="flex items-start gap-2">
                    <CheckCircle2 class="w-3.5 h-3.5 shrink-0 mt-0.5" 
                      :class="stg.is_completed ? 'text-[#059669]' : stg.is_current ? 'text-[#D97706]' : 'text-slate-300'" />
                    <span :class="stg.is_completed ? 'text-[#64748B] line-through' : 'text-[#0B132B] font-bold'">
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
            <div class="p-4 bg-white border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#059669] rounded-lg space-y-2 text-xs">
              <div class="flex items-center gap-2 text-[#065F46] font-black uppercase tracking-wider text-[11px]">
                <RotateCcw class="w-4 h-4 text-[#059669]" />
                <span>Yearly renewal</span>
              </div>
              <div class="space-y-1.5 pt-1">
                <div class="flex justify-between">
                  <span class="text-[#64748B]">How often:</span>
                  <span class="font-bold text-[#0B132B]">{{ roadmapData.renewal_intelligence.renewal_frequency }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-[#64748B]">Next renewal opens:</span>
                  <span class="font-bold text-[#059669]">{{ roadmapData.renewal_intelligence.next_academic_renewal_window_opens }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-[#64748B]">Income certificate expires:</span>
                  <span class="font-black text-[#D97706] font-mono">{{ roadmapData.renewal_intelligence.income_certificate_renewal_deadline }}</span>
                </div>
                <p class="text-[11px] text-[#064E3B] pt-1 border-t border-[#CBD5E1] leading-relaxed font-medium">
                  {{ roadmapData.renewal_intelligence.renewal_notes }}
                </p>
              </div>
            </div>

            <!-- Reapplication Intelligence -->
            <div class="p-4 bg-white border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#D97706] rounded-lg space-y-2 text-xs">
              <div class="flex items-center gap-2 text-[#92400E] font-black uppercase tracking-wider text-[11px]">
                <Clock class="w-4 h-4 text-[#D97706]" />
                <span>Applying again and appeals</span>
              </div>
              <div class="space-y-1.5 pt-1">
                <div class="flex justify-between">
                  <span class="text-[#64748B]">15-day window to fix errors:</span>
                  <span class="font-black text-[#92400E]">
                    {{ roadmapData.reapplication_intelligence.is_scrutiny_window_active ? 'Open (15 days left)' : 'Normal rules' }}
                  </span>
                </div>
                <div class="flex justify-between">
                  <span class="text-[#64748B]">Next new round:</span>
                  <span class="font-bold text-[#0B132B]">{{ roadmapData.reapplication_intelligence.next_fresh_admission_cycle }}</span>
                </div>
                <div class="pt-1 border-t border-[#CBD5E1] text-[11px] text-[#78350F] leading-relaxed">
                  <strong>How to appeal:</strong> {{ roadmapData.reapplication_intelligence.appeal_route }}
                </div>
              </div>
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
          Close Roadmap
        </button>

        <a 
          v-if="roadmapData?.official_portal_url"
          :href="roadmapData.official_portal_url" 
          target="_blank" 
          rel="noopener noreferrer"
          class="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-black text-white bg-[#0B132B] hover:bg-[#1C2541] border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#D97706] transition-colors cursor-pointer"
        >
          <span>Open {{ roadmapData.portal_name || 'MahaDBT' }} website</span>
          <ExternalLink class="w-3.5 h-3.5 text-[#F59E0B]" />
        </a>
      </div>
    </div>
  </div>
</template>
