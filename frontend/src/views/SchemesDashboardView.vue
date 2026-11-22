<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useStudentStore } from '../stores/studentStore';
import { t } from '../utils/i18n';
import PersonaBar from '../components/PersonaBar.vue';
import StatutoryModal from '../components/StatutoryModal.vue';
import type { EvaluatedScheme } from '../types';
import { 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  ExternalLink, 
  Scale, 
  ArrowRight, 
  UserCheck, 
  Edit2, 
  X, 
  FileText, 
  Clock, 
  HelpCircle, 
  Calendar, 
  BookmarkPlus, 
  RotateCcw, 
  Check 
} from '@lucide/vue';

const store = useStudentStore();
const router = useRouter();

onMounted(async () => {
  if (store.evaluatedSchemes.length === 0) {
    await store.evaluateEligibility();
  }
});

// Tab filtering: 'LIKELY_ELIGIBLE' | 'NEEDS_CONFIRMATION' | 'INELIGIBLE' | 'ALL'
const activeTab = ref<'LIKELY_ELIGIBLE' | 'NEEDS_CONFIRMATION' | 'INELIGIBLE' | 'ALL'>('LIKELY_ELIGIBLE');

const selectedModalScheme = ref<EvaluatedScheme | null>(null);
const isModalOpen = ref(false);
const showSampleSchemes = ref(false);

// Edit Profile Modal
const isEditProfileOpen = ref(false);
const editName = ref('');
const editAge = ref<number | null>(null);
const editIncome = ref<number>(0);
const editDistrict = ref('');
const editCaste = ref<'OPEN' | 'OBC' | 'SC' | 'ST' | 'VJNT' | 'SBC' | 'EWS'>('OPEN');
const editCourse = ref<any>('PROFESSIONAL_DEGREE');

function openEditProfileModal() {
  if (store.profile) {
    editName.value = store.profile.name || '';
    editAge.value = store.profile.age;
    editIncome.value = store.profile.annual_family_income || 0;
    editDistrict.value = store.profile.district || 'Pune';
    editCaste.value = store.profile.caste_category || 'OPEN';
    editCourse.value = store.profile.current_course_level || 'PROFESSIONAL_DEGREE';
  }
  isEditProfileOpen.value = true;
}

async function saveProfileEdit() {
  await store.updateProfile({
    name: editName.value,
    age: editAge.value,
    annual_family_income: Number(editIncome.value),
    district: editDistrict.value,
    caste_category: editCaste.value,
    current_course_level: editCourse.value,
  });
  isEditProfileOpen.value = false;
}

// Active schemes (prioritizes authentic higher-education scholarships)
const activeStudentSchemes = computed(() => {
  if (showSampleSchemes.value) {
    return store.evaluatedSchemes;
  }
  return store.evaluatedSchemes.filter(s => !s.is_sample);
});

// Counts computed
const likelyCount = computed(() => {
  return activeStudentSchemes.value.filter(s => s.status === 'LIKELY_ELIGIBLE').length;
});

const needsConfirmationCount = computed(() => {
  return activeStudentSchemes.value.filter(s => s.status === 'NEEDS_CONFIRMATION' || s.status === 'NEAR_ELIGIBLE').length;
});

const ineligibleCount = computed(() => {
  return activeStudentSchemes.value.filter(s => s.status === 'INELIGIBLE').length;
});

const filteredSchemes = computed(() => {
  if (activeTab.value === 'ALL') {
    return activeStudentSchemes.value;
  }
  if (activeTab.value === 'LIKELY_ELIGIBLE') {
    return activeStudentSchemes.value.filter(s => s.status === 'LIKELY_ELIGIBLE');
  }
  if (activeTab.value === 'NEEDS_CONFIRMATION') {
    return activeStudentSchemes.value.filter(s => s.status === 'NEEDS_CONFIRMATION' || s.status === 'NEAR_ELIGIBLE');
  }
  if (activeTab.value === 'INELIGIBLE') {
    return activeStudentSchemes.value.filter(s => s.status === 'INELIGIBLE');
  }
  return activeStudentSchemes.value;
});

// Document Dependency Intelligence: Ranked shared documents across matched schemes
const sharedDocumentsRanked = computed(() => {
  const docMap: Record<string, { code: string; name: string; issuing_authority: string; sla_days: number; scheme_codes: string[] }> = {};

  // Check likely and needs_confirmation schemes
  const eligibleOrNear = activeStudentSchemes.value.filter(s => s.status === 'LIKELY_ELIGIBLE' || s.status === 'NEAR_ELIGIBLE' || s.status === 'NEEDS_CONFIRMATION');
  
  eligibleOrNear.forEach(s => {
    (s.required_documents || []).forEach(doc => {
      if (!docMap[doc.code]) {
        docMap[doc.code] = {
          code: doc.code,
          name: doc.name,
          issuing_authority: doc.issuing_authority,
          sla_days: doc.estimated_sla_days,
          scheme_codes: []
        };
      }
      if (!docMap[doc.code].scheme_codes.includes(s.code)) {
        docMap[doc.code].scheme_codes.push(s.code);
      }
    });
  });

  return Object.values(docMap).sort((a, b) => b.scheme_codes.length - a.scheme_codes.length);
});

function openStatutoryModal(scheme: EvaluatedScheme) {
  selectedModalScheme.value = scheme;
  isModalOpen.value = true;
}

function viewSchemeDetail(code: string) {
  router.push(`/schemes/${code}`);
}

function isSchemeTracked(code: string) {
  return store.trackedApplications.some(a => a.scheme_code === code);
}

function getTrackedStatus(code: string) {
  const app = store.trackedApplications.find(a => a.scheme_code === code);
  return app?.status ? app.status.replace('_', ' ') : 'Tracked';
}

function isSchemeNeedingReEval(code: string) {
  const app = store.trackedApplications.find(a => a.scheme_code === code);
  return app?.needs_re_evaluation === true;
}

function isSchemeStale(scheme: EvaluatedScheme) {
  if (scheme.is_sample) return false;
  if (!scheme.last_verified_on) return true;
  const verifiedDate = new Date(scheme.last_verified_on).getTime();
  const diffDays = (Date.now() - verifiedDate) / (1000 * 3600 * 24);
  return diffDays > 180;
}

async function handleReEvaluateAll() {
  await store.acknowledgeReEvaluation();
  await store.evaluateEligibility();
  alert("Re-evaluation complete! Your scheme match results have been refreshed against the latest statutory rules.");
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
    <PersonaBar />

    <!-- RULE CHANGE RE-EVALUATION NOTIFICATION BANNER (Rule Change Handling 4) -->
    <div 
      v-if="store.reEvaluationAlerts.length > 0" 
      class="p-4 rounded-2xl bg-amber-500/10 border-2 border-amber-500 text-amber-950 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-xs animate-in fade-in"
    >
      <div class="flex items-start gap-3">
        <AlertTriangle class="w-6 h-6 text-amber-600 shrink-0 mt-0.5" />
        <div>
          <div class="font-black text-amber-900 text-sm uppercase tracking-wider flex items-center gap-2">
            <span>Statutory Eligibility Rule Revision Detected ({{ store.reEvaluationAlerts.length }} Scheme(s))</span>
            <span class="text-[10px] bg-amber-200 text-amber-900 px-2 py-0.2 rounded-full font-bold">Action Needed</span>
          </div>
          <p class="text-xs text-amber-900 mt-1">
            Department officers have updated statutory eligibility criteria for schemes saved in your application tracker. Click below to re-evaluate your qualification.
          </p>
        </div>
      </div>
      <button
        @click="handleReEvaluateAll"
        class="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs rounded-xl shadow-xs shrink-0 flex items-center gap-1.5 transition-transform active:scale-95"
      >
        <RotateCcw class="w-3.5 h-3.5" />
        <span>Re-Evaluate Rules & Clear Alerts</span>
      </button>
    </div>

    <!-- Top Navigation Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Recommended Schemes & Scholarships
        </h1>
        <p class="text-sm text-slate-600 mt-1">
          Matched against official Maharashtra Government criteria based on your profile facts.
        </p>
      </div>

      <div class="flex items-center gap-2 shrink-0">
        <button
          @click="store.evaluateEligibility()"
          :disabled="store.isLoading"
          class="px-3.5 py-2 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 rounded-xl text-xs sm:text-sm font-semibold transition-colors flex items-center gap-1.5 shadow-xs"
        >
          <RotateCcw class="w-3.5 h-3.5 text-indigo-600" :class="{ 'animate-spin': store.isLoading }" />
          <span>Re-check Eligibility</span>
        </button>
      </div>
    </div>

    <!-- Informational Notice -->
    <div class="px-4 py-2.5 rounded-xl bg-amber-50/80 border border-amber-200 text-amber-900 text-xs flex items-center gap-2">
      <AlertTriangle class="w-4 h-4 text-amber-600 shrink-0" />
      <span>Informational eligibility estimate based on Government Resolutions. Final sanction is granted by the department.</span>
    </div>

    <!-- 1. Compact Profile Summary Bar -->
    <div class="bg-white rounded-2xl border border-slate-200 shadow-xs px-5 py-3.5 flex flex-wrap items-center justify-between gap-3">
      <div class="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs sm:text-sm text-slate-600">
        <span class="font-bold text-slate-900 flex items-center gap-1.5">
          <UserCheck class="w-4 h-4 text-indigo-600" />
          {{ store.profile?.name || 'Citizen' }}
        </span>
        <span class="text-slate-300">•</span>
        <span>{{ store.profile?.age || 20 }} yrs</span>
        <span class="text-slate-300">•</span>
        <span>{{ store.profile?.district || 'Pune' }}, MH</span>
        <span class="text-slate-300">•</span>
        <span class="font-semibold text-indigo-700">{{ store.profile?.caste_category || 'OPEN' }}</span>
        <span class="text-slate-300">•</span>
        <span class="font-semibold text-emerald-700">₹{{ Number(store.profile?.annual_family_income || 0).toLocaleString('en-IN') }}/yr</span>
        <span class="text-slate-300">•</span>
        <span class="capitalize">{{ String(store.profile?.current_course_level || 'Undergraduate').toLowerCase().replace('_', ' ') }}</span>
      </div>

      <button
        @click="openEditProfileModal"
        class="inline-flex items-center gap-1 px-3 py-1 rounded-lg border border-slate-200 hover:border-indigo-300 bg-slate-50 hover:bg-indigo-50 text-slate-700 hover:text-indigo-700 text-xs font-semibold transition-colors shadow-xs"
      >
        <Edit2 class="w-3 h-3 text-indigo-600" />
        <span>Edit Profile</span>
      </button>
    </div>

    <!-- 2. Summary Metrics Cards -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
      <!-- Likely Eligible -->
      <div 
        @click="activeTab = 'LIKELY_ELIGIBLE'" 
        class="cursor-pointer p-4 rounded-2xl border transition-all shadow-xs"
        :class="activeTab === 'LIKELY_ELIGIBLE' ? 'bg-emerald-50 border-emerald-400 ring-2 ring-emerald-300' : 'bg-white border-slate-200 hover:bg-slate-50'"
      >
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold uppercase tracking-wider text-emerald-800">Eligible</span>
          <CheckCircle2 class="w-4 h-4 text-emerald-600" />
        </div>
        <div class="text-2xl sm:text-3xl font-black text-emerald-950 mt-1">{{ likelyCount }}</div>
        <div class="text-[11px] text-emerald-700 mt-0.5">Meets all criteria</div>
      </div>

      <!-- Needs Confirmation / Near Eligible -->
      <div 
        @click="activeTab = 'NEEDS_CONFIRMATION'" 
        class="cursor-pointer p-4 rounded-2xl border transition-all shadow-xs"
        :class="activeTab === 'NEEDS_CONFIRMATION' ? 'bg-amber-50 border-amber-400 ring-2 ring-amber-300' : 'bg-white border-slate-200 hover:bg-slate-50'"
      >
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold uppercase tracking-wider text-amber-800">Needs Info</span>
          <AlertTriangle class="w-4 h-4 text-amber-600" />
        </div>
        <div class="text-2xl sm:text-3xl font-black text-amber-950 mt-1">{{ needsConfirmationCount }}</div>
        <div class="text-[11px] text-amber-700 mt-0.5">Missing or borderline details</div>
      </div>

      <!-- Not Eligible -->
      <div 
        @click="activeTab = 'INELIGIBLE'" 
        class="cursor-pointer p-4 rounded-2xl border transition-all shadow-xs"
        :class="activeTab === 'INELIGIBLE' ? 'bg-rose-50 border-rose-400 ring-2 ring-rose-300' : 'bg-white border-slate-200 hover:bg-slate-50'"
      >
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold uppercase tracking-wider text-rose-800">Not Eligible</span>
          <XCircle class="w-4 h-4 text-rose-600" />
        </div>
        <div class="text-2xl sm:text-3xl font-black text-rose-950 mt-1">{{ ineligibleCount }}</div>
        <div class="text-[11px] text-rose-700 mt-0.5">Criteria not met</div>
      </div>

      <!-- Total Evaluated -->
      <div 
        @click="activeTab = 'ALL'" 
        class="cursor-pointer p-4 rounded-2xl border transition-all shadow-xs"
        :class="activeTab === 'ALL' ? 'bg-indigo-50 border-indigo-400 ring-2 ring-indigo-300' : 'bg-white border-slate-200 hover:bg-slate-50'"
      >
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold uppercase tracking-wider text-indigo-900">Total Schemes</span>
          <Scale class="w-4 h-4 text-indigo-600" />
        </div>
        <div class="text-2xl sm:text-3xl font-black text-slate-900 mt-1">{{ activeStudentSchemes.length }}</div>
        <div class="text-[11px] text-indigo-700 mt-0.5">All reviewed schemes</div>
      </div>
    </div>

    <!-- 6. Key Documents to Prepare -->
    <div v-if="sharedDocumentsRanked.length > 0" class="bg-white rounded-2xl border border-slate-200 shadow-xs p-5 space-y-3">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2.5 border-b border-slate-100">
        <div>
          <h2 class="text-sm sm:text-base font-bold text-slate-900 flex items-center gap-2">
            <FileText class="w-4 h-4 text-indigo-600" />
            Key Documents to Prepare
          </h2>
          <p class="text-xs text-slate-500 mt-0.5">
            These certificates are required across most of your eligible scholarships.
          </p>
        </div>
        <router-link
          to="/documents"
          class="text-xs font-semibold text-indigo-600 hover:text-indigo-800 flex items-center gap-1 self-start sm:self-auto"
        >
          <span>View All Required Documents</span>
          <ArrowRight class="w-3.5 h-3.5" />
        </router-link>
      </div>

      <!-- Ranked Documents Grid -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-3 pt-1">
        <div 
          v-for="(doc, idx) in sharedDocumentsRanked.slice(0, 3)" 
          :key="doc.code"
          class="p-3.5 rounded-xl border border-slate-200/80 bg-slate-50/50 hover:bg-white hover:shadow-xs transition-all flex flex-col justify-between"
        >
          <div>
            <div class="flex items-center justify-between text-xs mb-1">
              <span class="font-semibold text-indigo-700 bg-indigo-50 border border-indigo-100 px-2 py-0.5 rounded text-[10px]">
                Essential #{{ idx + 1 }}
              </span>
              <span class="text-slate-400 text-[11px]">
                ~{{ doc.sla_days }} days
              </span>
            </div>
            <h3 class="font-bold text-slate-900 text-sm mt-1">{{ doc.name }}</h3>
            <p class="text-xs text-slate-500 mt-0.5">Authority: {{ doc.issuing_authority }}</p>
          </div>

          <div class="mt-3 pt-2 border-t border-slate-100 flex items-center justify-between text-xs">
            <span class="font-semibold text-emerald-700">
              Unlocks {{ doc.scheme_codes.length }} scholarship(s)
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 3. Separate Sections & Tab Controls -->
    <div class="border-b border-slate-200 flex flex-wrap items-center justify-between gap-4">
      <div class="flex gap-2 sm:gap-4 overflow-x-auto whitespace-nowrap scrollbar-none">
        <button 
          @click="activeTab = 'LIKELY_ELIGIBLE'" 
          class="pb-3 text-sm font-bold border-b-2 transition-colors flex items-center gap-2"
          :class="activeTab === 'LIKELY_ELIGIBLE' ? 'border-emerald-600 text-emerald-800' : 'border-transparent text-slate-500 hover:text-slate-800'"
        >
          <CheckCircle2 class="w-4 h-4 text-emerald-600" />
          <span>{{ t('badge_likely', store.locale) }} ({{ likelyCount }})</span>
        </button>

        <button 
          @click="activeTab = 'NEEDS_CONFIRMATION'" 
          class="pb-3 text-sm font-bold border-b-2 transition-colors flex items-center gap-2"
          :class="activeTab === 'NEEDS_CONFIRMATION' ? 'border-amber-600 text-amber-800' : 'border-transparent text-slate-500 hover:text-slate-800'"
        >
          <AlertTriangle class="w-4 h-4 text-amber-600" />
          <span>{{ t('badge_needs_info', store.locale) }} ({{ needsConfirmationCount }})</span>
        </button>

        <button 
          @click="activeTab = 'INELIGIBLE'" 
          class="pb-3 text-sm font-bold border-b-2 transition-colors flex items-center gap-2"
          :class="activeTab === 'INELIGIBLE' ? 'border-rose-600 text-rose-800' : 'border-transparent text-slate-500 hover:text-slate-800'"
        >
          <XCircle class="w-4 h-4 text-rose-600" />
          <span>{{ t('badge_ineligible', store.locale) }} ({{ ineligibleCount }})</span>
        </button>

        <button 
          @click="activeTab = 'ALL'" 
          class="pb-3 text-sm font-bold border-b-2 transition-colors flex items-center gap-2"
          :class="activeTab === 'ALL' ? 'border-indigo-600 text-indigo-800' : 'border-transparent text-slate-500 hover:text-slate-800'"
        >
          <span>All Schemes ({{ activeStudentSchemes.length }})</span>
        </button>
      </div>

      <!-- Sample Schemes Toggle -->
      <label class="pb-2 flex items-center gap-2 text-xs text-slate-500 cursor-pointer select-none hover:text-slate-700">
        <input 
          type="checkbox" 
          v-model="showSampleSchemes" 
          class="w-3.5 h-3.5 rounded text-indigo-600 border-slate-300 focus:ring-indigo-500" 
        />
        <span>Include Central / Sample Schemes (10)</span>
      </label>
    </div>

    <!-- 4. Scheme Cards List (Requirement 4) -->
    <div v-if="filteredSchemes.length > 0" class="space-y-5">
      <div 
        v-for="s in filteredSchemes" 
        :key="s.code" 
        class="bg-white rounded-3xl border border-slate-200 shadow-sm p-6 sm:p-7 hover:shadow-md transition-shadow"
      >
        <div class="flex flex-col lg:flex-row items-start justify-between gap-6">
          <div class="space-y-3 flex-1 min-w-0">
            <!-- Header Badges -->
            <div class="flex flex-wrap items-center gap-2">
              <span 
                class="text-xs px-3 py-0.5 rounded-full font-bold uppercase tracking-wider border"
                :class="s.status === 'LIKELY_ELIGIBLE' 
                  ? 'bg-emerald-50 text-emerald-800 border-emerald-300' 
                  : ((s.status === 'NEAR_ELIGIBLE' || s.status === 'NEEDS_CONFIRMATION')
                      ? 'bg-amber-50 text-amber-800 border-amber-300' 
                      : 'bg-rose-50 text-rose-800 border-rose-300')"
              >
                {{ s.status === 'LIKELY_ELIGIBLE' ? t('badge_likely', store.locale) : (s.status === 'NEAR_ELIGIBLE' ? t('badge_near_eligible', store.locale) : (s.status === 'NEEDS_CONFIRMATION' ? t('badge_needs_info', store.locale) : t('badge_ineligible', store.locale))) }}
              </span>

              <span class="text-xs font-mono font-semibold text-slate-500 bg-slate-100 px-2.5 py-0.5 rounded-md">
                {{ s.code }}
              </span>

              <span class="text-xs text-indigo-800 font-semibold bg-indigo-50 px-2.5 py-0.5 rounded-full border border-indigo-100">
                {{ s.department }}
              </span>

              <span 
                v-if="isSchemeNeedingReEval(s.code)"
                class="text-[10px] font-bold bg-amber-100 text-amber-900 border border-amber-300 px-2 py-0.5 rounded-full animate-pulse flex items-center gap-1"
              >
                <AlertTriangle class="w-3 h-3 text-amber-600" />
                <span>Criteria Revised - Re-Run Needed</span>
              </span>

              <span 
                v-if="isSchemeStale(s)"
                class="text-[10px] font-bold bg-amber-50 text-amber-900 border border-amber-300 px-2 py-0.5 rounded-full flex items-center gap-1"
                title="This scheme has not been re-verified in over 180 days. Official criteria may have changed."
              >
                <AlertTriangle class="w-3 h-3 text-amber-600" />
                <span>Stale Verification (>180d)</span>
              </span>

              <span 
                v-if="s.is_sample"
                class="text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-300 px-2 py-0.5 rounded-full flex items-center gap-1"
              >
                Sample Data
              </span>
            </div>

            <!-- Title & Benefit -->
            <div>
              <h3 class="text-xl font-bold text-slate-900 leading-snug">{{ s.name }}</h3>
              <p v-if="s.name_marathi" class="text-xs text-slate-500 font-medium mt-0.5">{{ s.name_marathi }}</p>
            </div>

            <div class="text-sm font-extrabold text-emerald-900 bg-emerald-50/80 border border-emerald-200 p-2.5 rounded-xl inline-block">
              Benefit: {{ s.benefit_amount_text }}
            </div>

            <p class="text-xs text-slate-600 leading-relaxed">{{ s.brief_description }}</p>

            <!-- WHY THE USER MATCHES (Passed Criteria) -->
            <div v-if="s.passed_criteria && s.passed_criteria.length > 0" class="p-3 bg-emerald-50/60 rounded-xl border border-emerald-200 text-xs text-emerald-950 space-y-1.5">
              <div class="font-bold flex items-center gap-1 text-emerald-900">
                <CheckCircle2 class="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                <span>Why You Match:</span>
              </div>
              <ul class="space-y-1 pl-4 list-disc">
                <li v-for="(p, i) in s.passed_criteria" :key="'p-' + i">
                  {{ p.reason }}
                </li>
              </ul>
            </div>

            <!-- MISSING OR FAILED CRITERIA -->
            <div v-if="s.failed_criteria && s.failed_criteria.length > 0" class="p-3 bg-rose-50 rounded-xl border border-rose-200 text-xs text-rose-950 space-y-1.5">
              <div class="font-bold flex items-center gap-1 text-rose-900">
                <XCircle class="w-3.5 h-3.5 text-rose-600 shrink-0" />
                <span>Ineligibility Factors:</span>
              </div>
              <ul class="space-y-1 pl-4 list-disc">
                <li v-for="(f, i) in s.failed_criteria" :key="'f-' + i">
                  {{ f.reason }}
                </li>
              </ul>
            </div>

            <div v-if="s.missing_criteria && s.missing_criteria.length > 0" class="p-3 bg-blue-50 rounded-xl border border-blue-200 text-xs text-blue-950 space-y-1.5">
              <div class="font-bold flex items-center gap-1 text-blue-900">
                <HelpCircle class="w-3.5 h-3.5 text-blue-600 shrink-0" />
                <span>Criteria Needing Confirmation:</span>
              </div>
              <ul class="space-y-1 pl-4 list-disc">
                <li v-for="(m, i) in s.missing_criteria" :key="'m-' + i">
                  {{ m.reason }}
                </li>
              </ul>
            </div>

            <!-- 7. ALMOST-ELIGIBLE GUIDANCE (Requirement 7) -->
            <div 
              v-if="(s.status === 'NEAR_ELIGIBLE' || s.status === 'NEEDS_CONFIRMATION') && (s.near_eligible_guidance || s.near_eligible_criteria?.length > 0)" 
              class="p-3.5 bg-amber-50 rounded-2xl border border-amber-300 text-xs text-amber-950 space-y-2"
            >
              <div class="font-bold flex items-center gap-1.5 text-amber-900">
                <AlertTriangle class="w-4 h-4 text-amber-600 shrink-0" />
                <span>Near-Eligible Guidance & Official Procurement Steps:</span>
              </div>
              <p class="leading-relaxed">
                {{ s.near_eligible_guidance || 'You are close to the qualifying boundary for this scholarship.' }}
              </p>
              <div class="p-2 bg-white/80 rounded-lg border border-amber-200 text-[11px] text-amber-900 leading-normal">
                <strong>Official Process:</strong> If you meet the boundary category, obtain the requisite Tahsildar Income or Domicile certificate via Aaple Sarkar portal (<span class="font-mono text-indigo-700">aaplesarkar.mahaonline.gov.in</span>).
                <br />
                <span class="italic text-slate-500 font-semibold block mt-1">
                  * Notice: Procuring this document allows your application to be scrutinized by the issuing authority, but does not guarantee eligibility or sanction.
                </span>
              </div>
            </div>

            <!-- Metadata Footer: Official Source, Last Verified Date, Application Deadline -->
            <div class="pt-2 flex flex-wrap items-center gap-y-2 gap-x-5 text-xs text-slate-500 border-t border-slate-100">
              <div class="flex items-center gap-1">
                <Scale class="w-3.5 h-3.5 text-indigo-600" />
                <span>Source: <strong class="text-slate-800">{{ s.statutory_gr }}</strong></span>
              </div>
              <div class="flex items-center gap-1">
                <Calendar class="w-3.5 h-3.5 text-slate-400" />
                <span>Verified: <strong class="text-slate-700">{{ s.last_verified_on || 'Nov 2024' }}</strong></span>
              </div>
              <div class="flex items-center gap-1">
                <Clock class="w-3.5 h-3.5 text-amber-600" />
                <span>Deadline: <strong class="text-amber-800">{{ s.application_deadline ? new Date(s.application_deadline).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : 'Rolling' }}</strong></span>
              </div>
            </div>
          </div>

          <!-- Actions Column -->
          <div class="flex lg:flex-col items-stretch lg:items-end justify-between w-full lg:w-48 gap-2 shrink-0 pt-4 lg:pt-0 border-t lg:border-t-0 border-slate-100">
            <!-- View Full Scheme Details (Primary) -->
            <button
              @click="viewSchemeDetail(s.code)"
              class="w-full py-2.5 px-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs rounded-xl flex items-center justify-center gap-1.5 transition-all shadow-xs"
            >
              <span>View Details & Steps</span>
              <ArrowRight class="w-3.5 h-3.5" />
            </button>

            <!-- Save / Track Application (Secondary) -->
            <div class="w-full">
              <button
                v-if="!isSchemeTracked(s.code)"
                @click="store.saveSchemeToTracker(s.code, 'NOT_STARTED')"
                class="w-full py-2 px-3 bg-slate-50 hover:bg-slate-100 text-slate-700 font-semibold text-xs rounded-xl flex items-center justify-center gap-1.5 transition-colors border border-slate-200"
              >
                <BookmarkPlus class="w-3.5 h-3.5 text-indigo-600" />
                <span>Save to Tracker</span>
              </button>

              <router-link
                v-else
                to="/tracker"
                class="w-full py-2 px-3 bg-emerald-50 text-emerald-800 text-xs font-semibold rounded-xl flex items-center justify-center gap-1.5 transition-colors border border-emerald-200"
              >
                <Check class="w-3.5 h-3.5 text-emerald-600" />
                <span>Saved ({{ getTrackedStatus(s.code) }})</span>
              </router-link>
            </div>

            <!-- Quick Text Links -->
            <div class="w-full flex items-center justify-center gap-2.5 pt-1 text-[11px] text-slate-500">
              <a
                :href="s.official_portal_url"
                target="_blank"
                rel="noopener noreferrer"
                class="hover:text-indigo-600 inline-flex items-center gap-0.5 font-medium transition-colors"
              >
                <span>{{ s.portal_name || 'Portal' }}</span>
                <ExternalLink class="w-2.5 h-2.5" />
              </a>
              <span class="text-slate-300">•</span>
              <button
                @click="openStatutoryModal(s)"
                class="hover:text-indigo-600 inline-flex items-center gap-0.5 font-medium transition-colors"
              >
                <span>GR Audit</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-12 bg-white rounded-3xl border border-slate-200 p-8 space-y-2">
      <div class="w-12 h-12 rounded-full bg-slate-100 text-slate-400 flex items-center justify-center mx-auto">
        <HelpCircle class="w-6 h-6" />
      </div>
      <h3 class="text-base font-bold text-slate-800">No schemes found under this filter</h3>
      <p class="text-xs text-slate-500 max-w-md mx-auto">
        Switch tabs or adjust your profile parameters using the Edit Profile option above.
      </p>
    </div>

    <!-- Quick In-Place Statutory GR Audit Modal -->
    <StatutoryModal 
      :scheme="selectedModalScheme" 
      :isOpen="isModalOpen" 
      @close="isModalOpen = false" 
    />

    <!-- Edit Profile Modal -->
    <div 
      v-if="isEditProfileOpen"
      class="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 animate-in fade-in"
    >
      <div class="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 space-y-4">
        <div class="flex items-center justify-between pb-3 border-b border-slate-100">
          <h3 class="font-bold text-slate-900 text-base flex items-center gap-2">
            <Edit2 class="w-4 h-4 text-indigo-600" />
            Edit Profile Parameters
          </h3>
          <button @click="isEditProfileOpen = false" class="text-slate-400 hover:text-slate-600 p-1">
            <X class="w-4 h-4" />
          </button>
        </div>

        <form @submit.prevent="saveProfileEdit" class="space-y-3.5 text-xs">
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Student Name / Tag:</label>
            <input 
              v-model="editName"
              type="text"
              class="w-full text-sm border border-slate-300 rounded-xl px-3 py-2 focus:ring-2 focus:ring-indigo-500"
              required
            />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block font-semibold text-slate-700 mb-1">Age:</label>
              <input 
                v-model.number="editAge"
                type="number"
                min="0"
                max="120"
                class="w-full text-sm border border-slate-300 rounded-xl px-3 py-2 focus:ring-2 focus:ring-indigo-500"
                required
              />
            </div>

            <div>
              <label class="block font-semibold text-slate-700 mb-1">District (Maharashtra):</label>
              <input 
                v-model="editDistrict"
                type="text"
                class="w-full text-sm border border-slate-300 rounded-xl px-3 py-2 focus:ring-2 focus:ring-indigo-500"
                required
              />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block font-semibold text-slate-700 mb-1">Caste Category:</label>
              <select 
                v-model="editCaste"
                class="w-full text-sm border border-slate-300 rounded-xl px-3 py-2 focus:ring-2 focus:ring-indigo-500"
              >
                <option value="OPEN">Open / General</option>
                <option value="OBC">OBC</option>
                <option value="SC">SC</option>
                <option value="ST">ST</option>
                <option value="VJNT">VJNT</option>
                <option value="SBC">SBC</option>
                <option value="EWS">EWS</option>
              </select>
            </div>

            <div>
              <label class="block font-semibold text-slate-700 mb-1">Annual Family Income (₹):</label>
              <input 
                v-model.number="editIncome"
                type="number"
                min="0"
                step="1000"
                class="w-full text-sm border border-slate-300 rounded-xl px-3 py-2 focus:ring-2 focus:ring-indigo-500 font-mono"
                required
              />
            </div>
          </div>

          <div class="pt-2 flex items-center justify-end gap-2 border-t border-slate-100">
            <button
              type="button"
              @click="isEditProfileOpen = false"
              class="px-4 py-2 border border-slate-300 rounded-xl font-semibold text-slate-700 hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="store.isLoading"
              class="px-5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl shadow-xs transition-colors"
            >
              Save & Re-Evaluate
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
