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
  Check,
  Sliders 
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
      class="neo-box p-4 bg-amber-50 text-amber-950 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 animate-in fade-in"
    >
      <div class="flex items-start gap-3">
        <div class="p-2 bg-amber-200 rounded-lg border border-[#0B132B] text-amber-950 shrink-0 mt-0.5 shadow-[1.5px_1.5px_0_0_#0B132B]">
          <AlertTriangle class="w-5 h-5 text-amber-900" />
        </div>
        <div>
          <div class="font-black text-amber-950 text-xs sm:text-sm uppercase tracking-wider flex items-center gap-2">
            <span>Statutory Eligibility Rule Revision Detected ({{ store.reEvaluationAlerts.length }} Scheme(s))</span>
            <span class="neo-stamp neo-stamp-amber">Action Needed</span>
          </div>
          <p class="text-xs text-amber-900 font-medium mt-1">
            Department officers have updated statutory eligibility criteria for schemes saved in your application tracker. Click below to re-evaluate your qualification.
          </p>
        </div>
      </div>
      <button
        @click="handleReEvaluateAll"
        class="neo-btn neo-btn-saffron px-4 py-2 text-xs font-bold shrink-0 self-start sm:self-auto"
      >
        <RotateCcw class="w-3.5 h-3.5" />
        <span>Re-Evaluate Rules & Clear Alerts</span>
      </button>
    </div>

    <!-- Top Navigation Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <div class="inline-flex items-center gap-2 mb-1.5">
          <span class="neo-stamp neo-stamp-navy text-[10px]">
            <Scale class="w-3 h-3 text-amber-400" />
            Statutory Engine v2.5
          </span>
          <span class="text-xs text-slate-500 font-mono">GR-Certified</span>
        </div>
        <h1 class="text-2xl sm:text-3xl font-extrabold text-[#0B132B] tracking-tight">
          Recommended Schemes & Scholarships
        </h1>
        <p class="text-xs sm:text-sm text-slate-600 mt-1 font-medium">
          Matched deterministically against official Maharashtra Government criteria based on your verified profile facts.
        </p>
      </div>

      <div class="flex items-center gap-2 shrink-0">
        <router-link
          to="/what-if"
          class="neo-btn neo-btn-paper px-3.5 py-2 text-xs sm:text-sm font-bold text-[#0B132B]"
        >
          <Sliders class="w-3.5 h-3.5 text-amber-600" />
          <span>What-If Simulator 🔮</span>
        </router-link>

        <button
          @click="store.evaluateEligibility()"
          :disabled="store.isLoading"
          class="neo-btn neo-btn-saffron px-3.5 py-2 text-xs sm:text-sm font-bold"
        >
          <RotateCcw class="w-3.5 h-3.5" :class="{ 'animate-spin': store.isLoading }" />
          <span>Re-check Eligibility</span>
        </button>
      </div>
    </div>

    <!-- Informational Notice -->
    <div class="px-4 py-3 rounded-xl border-[1.5px] border-[#0B132B] bg-[#FFFBEB] text-amber-950 text-xs font-medium flex items-center gap-2.5 shadow-[2px_2px_0_0_#0B132B]">
      <AlertTriangle class="w-4 h-4 text-amber-700 shrink-0" />
      <span>Informational eligibility estimate based on published Government Resolutions (GRs). Final sanction is granted by the relevant department scrutinising authority.</span>
    </div>

    <!-- 1. Compact Profile Summary Bar -->
    <div class="neo-box px-5 py-3.5 flex flex-wrap items-center justify-between gap-3 bg-white">
      <div class="flex flex-wrap items-center gap-x-4 gap-y-1.5 text-xs sm:text-sm text-slate-700 font-medium">
        <span class="font-extrabold text-[#0B132B] flex items-center gap-1.5">
          <UserCheck class="w-4 h-4 text-amber-600" />
          {{ store.profile?.name || 'Citizen' }}
        </span>
        <span class="text-slate-300">•</span>
        <span>{{ store.profile?.age || 20 }} yrs</span>
        <span class="text-slate-300">•</span>
        <span>{{ store.profile?.district || 'Pune' }}, MH</span>
        <span class="text-slate-300">•</span>
        <span class="neo-stamp text-[10px] bg-slate-100 text-[#0B132B]">{{ store.profile?.caste_category || 'OPEN' }}</span>
        <span class="text-slate-300">•</span>
        <span class="font-bold text-emerald-800">₹{{ Number(store.profile?.annual_family_income || 0).toLocaleString('en-IN') }}/yr</span>
        <span class="text-slate-300">•</span>
        <span class="capitalize text-slate-600">{{ String(store.profile?.current_course_level || 'Undergraduate').toLowerCase().replace('_', ' ') }}</span>
      </div>

      <button
        @click="openEditProfileModal"
        class="neo-btn neo-btn-paper px-3 py-1.5 text-xs font-bold text-[#0B132B]"
      >
        <Edit2 class="w-3 h-3 text-amber-600" />
        <span>Edit Profile</span>
      </button>
    </div>

    <!-- 2. Summary Metrics Cards -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
      <!-- Likely Eligible -->
      <div 
        @click="activeTab = 'LIKELY_ELIGIBLE'" 
        class="neo-box-interactive p-4"
        :class="activeTab === 'LIKELY_ELIGIBLE' ? '!bg-[#ECFDF5] !shadow-[3px_3px_0_0_#0B132B] ring-2 ring-emerald-600' : 'bg-white'"
      >
        <div class="flex items-center justify-between">
          <span class="neo-stamp neo-stamp-emerald text-[10px]">Eligible</span>
          <CheckCircle2 class="w-4 h-4 text-emerald-700" />
        </div>
        <div class="text-2xl sm:text-3xl font-black text-[#0B132B] mt-2 font-heading">{{ likelyCount }}</div>
        <div class="text-[11px] text-emerald-800 font-semibold mt-0.5">Meets all criteria</div>
      </div>

      <!-- Needs Confirmation / Near Eligible -->
      <div 
        @click="activeTab = 'NEEDS_CONFIRMATION'" 
        class="neo-box-interactive p-4"
        :class="activeTab === 'NEEDS_CONFIRMATION' ? '!bg-[#FFFBEB] !shadow-[3px_3px_0_0_#0B132B] ring-2 ring-amber-600' : 'bg-white'"
      >
        <div class="flex items-center justify-between">
          <span class="neo-stamp neo-stamp-amber text-[10px]">Needs Info</span>
          <AlertTriangle class="w-4 h-4 text-amber-700" />
        </div>
        <div class="text-2xl sm:text-3xl font-black text-[#0B132B] mt-2 font-heading">{{ needsConfirmationCount }}</div>
        <div class="text-[11px] text-amber-800 font-semibold mt-0.5">Missing or boundary info</div>
      </div>

      <!-- Not Eligible -->
      <div 
        @click="activeTab = 'INELIGIBLE'" 
        class="neo-box-interactive p-4"
        :class="activeTab === 'INELIGIBLE' ? '!bg-[#FFF1F2] !shadow-[3px_3px_0_0_#0B132B] ring-2 ring-rose-600' : 'bg-white'"
      >
        <div class="flex items-center justify-between">
          <span class="neo-stamp neo-stamp-rose text-[10px]">Not Eligible</span>
          <XCircle class="w-4 h-4 text-rose-700" />
        </div>
        <div class="text-2xl sm:text-3xl font-black text-[#0B132B] mt-2 font-heading">{{ ineligibleCount }}</div>
        <div class="text-[11px] text-rose-800 font-semibold mt-0.5">Criteria not met</div>
      </div>

      <!-- Total Evaluated -->
      <div 
        @click="activeTab = 'ALL'" 
        class="neo-box-interactive p-4"
        :class="activeTab === 'ALL' ? '!bg-slate-100 !shadow-[3px_3px_0_0_#0B132B] ring-2 ring-[#0B132B]' : 'bg-white'"
      >
        <div class="flex items-center justify-between">
          <span class="neo-stamp neo-stamp-navy text-[10px]">Total Schemes</span>
          <Scale class="w-4 h-4 text-slate-700" />
        </div>
        <div class="text-2xl sm:text-3xl font-black text-[#0B132B] mt-2 font-heading">{{ activeStudentSchemes.length }}</div>
        <div class="text-[11px] text-slate-600 font-semibold mt-0.5">All reviewed schemes</div>
      </div>
    </div>

    <!-- 6. Key Documents to Prepare -->
    <div v-if="sharedDocumentsRanked.length > 0" class="neo-box p-5 space-y-3 bg-white">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2.5 border-b-[1.5px] border-[#0B132B]/15">
        <div>
          <h2 class="text-sm sm:text-base font-extrabold text-[#0B132B] flex items-center gap-2">
            <FileText class="w-4 h-4 text-amber-600" />
            Key Documents to Prepare (Cross-Scheme Matrix)
          </h2>
          <p class="text-xs text-slate-600 mt-0.5 font-medium">
            These statutory certificates are required across most of your eligible scholarships.
          </p>
        </div>
        <router-link
          to="/documents"
          class="neo-btn neo-btn-paper text-xs py-1 px-3 self-start sm:self-auto font-bold text-[#0B132B]"
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
          class="p-3.5 rounded-xl border-[1.5px] border-[#0B132B] bg-[#FBFBFA] shadow-[1.5px_1.5px_0_0_#0B132B] flex flex-col justify-between"
        >
          <div>
            <div class="flex items-center justify-between text-xs mb-1">
              <span class="neo-stamp neo-stamp-navy text-[9px]">
                Essential #{{ idx + 1 }}
              </span>
              <span class="text-slate-500 font-mono text-[11px] font-bold">
                ~{{ doc.sla_days }} days SLA
              </span>
            </div>
            <h3 class="font-extrabold text-[#0B132B] text-sm mt-1">{{ doc.name }}</h3>
            <p class="text-xs text-slate-600 mt-0.5 font-medium">Issuing Authority: {{ doc.issuing_authority }}</p>
          </div>

          <div class="mt-3 pt-2 border-t border-[#0B132B]/10 flex items-center justify-between text-xs">
            <span class="font-bold text-emerald-800">
              Unlocks {{ doc.scheme_codes.length }} scholarship(s)
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 3. Separate Sections & Tab Controls -->
    <div class="border-b-[1.5px] border-[#0B132B]/20 flex flex-wrap items-center justify-between gap-4 pb-2">
      <div class="flex gap-2 sm:gap-3 overflow-x-auto whitespace-nowrap scrollbar-none py-1">
        <button 
          @click="activeTab = 'LIKELY_ELIGIBLE'" 
          class="neo-btn px-3 py-1.5 text-xs font-bold"
          :class="activeTab === 'LIKELY_ELIGIBLE' ? 'neo-btn-emerald' : 'neo-btn-paper'"
        >
          <CheckCircle2 class="w-3.5 h-3.5" />
          <span>{{ t('badge_likely', store.locale) }} ({{ likelyCount }})</span>
        </button>

        <button 
          @click="activeTab = 'NEEDS_CONFIRMATION'" 
          class="neo-btn px-3 py-1.5 text-xs font-bold"
          :class="activeTab === 'NEEDS_CONFIRMATION' ? 'neo-btn-saffron' : 'neo-btn-paper'"
        >
          <AlertTriangle class="w-3.5 h-3.5" />
          <span>{{ t('badge_needs_info', store.locale) }} ({{ needsConfirmationCount }})</span>
        </button>

        <button 
          @click="activeTab = 'INELIGIBLE'" 
          class="neo-btn px-3 py-1.5 text-xs font-bold"
          :class="activeTab === 'INELIGIBLE' ? 'neo-btn-rose' : 'neo-btn-paper'"
        >
          <XCircle class="w-3.5 h-3.5" />
          <span>{{ t('badge_ineligible', store.locale) }} ({{ ineligibleCount }})</span>
        </button>

        <button 
          @click="activeTab = 'ALL'" 
          class="neo-btn px-3 py-1.5 text-xs font-bold"
          :class="activeTab === 'ALL' ? 'neo-btn-navy' : 'neo-btn-paper'"
        >
          <span>All Schemes ({{ activeStudentSchemes.length }})</span>
        </button>
      </div>

      <!-- Sample Schemes Toggle -->
      <label class="flex items-center gap-2 text-xs text-slate-700 font-semibold cursor-pointer select-none">
        <input 
          type="checkbox" 
          v-model="showSampleSchemes" 
          class="w-4 h-4 rounded border-[#0B132B] text-amber-600 focus:ring-amber-500" 
        />
        <span>Include Central / Sample Schemes (10)</span>
      </label>
    </div>

    <!-- 4. Scheme Cards List (Requirement 4) -->
    <div v-if="filteredSchemes.length > 0" class="space-y-5">
      <div 
        v-for="s in filteredSchemes" 
        :key="s.code" 
        class="neo-box p-6 sm:p-7 bg-white"
      >
        <div class="flex flex-col lg:flex-row items-start justify-between gap-6">
          <div class="space-y-3 flex-1 min-w-0">
            <!-- Header Badges -->
            <div class="flex flex-wrap items-center gap-2">
              <span 
                class="neo-stamp"
                :class="s.status === 'LIKELY_ELIGIBLE' 
                  ? 'neo-stamp-emerald' 
                  : ((s.status === 'NEAR_ELIGIBLE' || s.status === 'NEEDS_CONFIRMATION')
                      ? 'neo-stamp-amber' 
                      : 'neo-stamp-rose')"
              >
                {{ s.status === 'LIKELY_ELIGIBLE' ? t('badge_likely', store.locale) : (s.status === 'NEAR_ELIGIBLE' ? t('badge_near_eligible', store.locale) : (s.status === 'NEEDS_CONFIRMATION' ? t('badge_needs_info', store.locale) : t('badge_ineligible', store.locale))) }}
              </span>

              <span class="neo-stamp neo-stamp-navy font-mono text-[10px]">
                {{ s.code }}
              </span>

              <span class="text-xs font-bold text-slate-800 bg-[#F5F5F3] px-2.5 py-0.5 rounded-md border border-[#0B132B]/20">
                {{ s.department }}
              </span>

              <span 
                v-if="isSchemeNeedingReEval(s.code)"
                class="neo-stamp neo-stamp-amber animate-pulse"
              >
                <AlertTriangle class="w-3 h-3 text-amber-700" />
                <span>Criteria Revised - Re-Run Needed</span>
              </span>

              <span 
                v-if="isSchemeStale(s)"
                class="neo-stamp neo-stamp-amber"
                title="This scheme has not been re-verified in over 180 days. Official criteria may have changed."
              >
                <AlertTriangle class="w-3 h-3 text-amber-700" />
                <span>Stale Verification (>180d)</span>
              </span>

              <span 
                v-if="s.is_sample"
                class="neo-stamp bg-slate-100 text-slate-700"
              >
                Sample Data
              </span>
            </div>

            <!-- Title & Benefit -->
            <div>
              <h3 class="text-xl font-extrabold text-[#0B132B] leading-snug">{{ s.name }}</h3>
              <p v-if="s.name_marathi" class="text-xs text-slate-600 font-medium font-indic mt-0.5">{{ s.name_marathi }}</p>
            </div>

            <div class="text-xs sm:text-sm font-extrabold text-emerald-900 bg-emerald-50 border-[1.5px] border-[#0B132B] p-2.5 rounded-xl inline-block shadow-[1.5px_1.5px_0_0_#0B132B]">
              Direct Benefit: {{ s.benefit_amount_text }}
            </div>

            <p class="text-xs text-slate-700 leading-relaxed font-medium">{{ s.brief_description }}</p>

            <!-- WHY THE USER MATCHES (Passed Criteria) -->
            <div v-if="s.passed_criteria && s.passed_criteria.length > 0" class="p-3 bg-[#ECFDF5] rounded-xl border-[1.5px] border-[#0B132B] text-xs text-emerald-950 space-y-1.5 shadow-[1.5px_1.5px_0_0_#0B132B]">
              <div class="font-extrabold flex items-center gap-1.5 text-emerald-900">
                <CheckCircle2 class="w-4 h-4 text-emerald-700 shrink-0" />
                <span>Why You Match:</span>
              </div>
              <ul class="space-y-1 pl-4 list-disc font-medium">
                <li v-for="(p, i) in s.passed_criteria" :key="'p-' + i">
                  {{ p.reason }}
                </li>
              </ul>
            </div>

            <!-- MISSING OR FAILED CRITERIA -->
            <div v-if="s.failed_criteria && s.failed_criteria.length > 0" class="p-3 bg-[#FFF1F2] rounded-xl border-[1.5px] border-[#0B132B] text-xs text-rose-950 space-y-1.5 shadow-[1.5px_1.5px_0_0_#0B132B]">
              <div class="font-extrabold flex items-center gap-1.5 text-rose-900">
                <XCircle class="w-4 h-4 text-rose-700 shrink-0" />
                <span>Ineligibility Factors:</span>
              </div>
              <ul class="space-y-1 pl-4 list-disc font-medium">
                <li v-for="(f, i) in s.failed_criteria" :key="'f-' + i">
                  {{ f.reason }}
                </li>
              </ul>
            </div>

            <div v-if="s.missing_criteria && s.missing_criteria.length > 0" class="p-3 bg-blue-50 rounded-xl border-[1.5px] border-[#0B132B] text-xs text-blue-950 space-y-1.5 shadow-[1.5px_1.5px_0_0_#0B132B]">
              <div class="font-extrabold flex items-center gap-1.5 text-blue-900">
                <HelpCircle class="w-4 h-4 text-blue-700 shrink-0" />
                <span>Criteria Needing Confirmation:</span>
              </div>
              <ul class="space-y-1 pl-4 list-disc font-medium">
                <li v-for="(m, i) in s.missing_criteria" :key="'m-' + i">
                  {{ m.reason }}
                </li>
              </ul>
            </div>

            <!-- 7. ALMOST-ELIGIBLE GUIDANCE (Requirement 7) -->
            <div 
              v-if="(s.status === 'NEAR_ELIGIBLE' || s.status === 'NEEDS_CONFIRMATION') && (s.near_eligible_guidance || s.near_eligible_criteria?.length > 0)" 
              class="p-3.5 bg-[#FFFBEB] rounded-xl border-[1.5px] border-[#0B132B] text-xs text-amber-950 space-y-2 shadow-[2px_2px_0_0_#0B132B]"
            >
              <div class="font-extrabold flex items-center gap-1.5 text-amber-950">
                <AlertTriangle class="w-4 h-4 text-amber-700 shrink-0" />
                <span>Near-Eligible Guidance & Official Procurement Steps:</span>
              </div>
              <p class="leading-relaxed font-medium">
                {{ s.near_eligible_guidance || 'You are close to the qualifying boundary for this scholarship.' }}
              </p>
              <div class="p-2 bg-white rounded-lg border border-[#0B132B]/30 text-[11px] text-amber-950 leading-normal">
                <strong>Official Process:</strong> If you meet the boundary category, obtain the requisite Tahsildar Income or Domicile certificate via Aaple Sarkar portal (<span class="font-mono text-indigo-800 font-bold">aaplesarkar.mahaonline.gov.in</span>).
                <br />
                <span class="italic text-slate-600 font-semibold block mt-1">
                  * Notice: Procuring this document allows your application to be scrutinized by the issuing authority, but does not guarantee eligibility or sanction.
                </span>
              </div>
            </div>

            <!-- Metadata Footer: Official Source, Last Verified Date, Application Deadline -->
            <div class="pt-2 flex flex-wrap items-center gap-y-2 gap-x-5 text-xs text-slate-600 border-t border-[#0B132B]/10 font-medium">
              <div class="flex items-center gap-1">
                <Scale class="w-3.5 h-3.5 text-amber-600" />
                <span>Source: <strong class="text-[#0B132B] font-mono">{{ s.statutory_gr }}</strong></span>
              </div>
              <div class="flex items-center gap-1">
                <Calendar class="w-3.5 h-3.5 text-slate-500" />
                <span>Verified: <strong class="text-[#0B132B]">{{ s.last_verified_on || 'Nov 2024' }}</strong></span>
              </div>
              <div class="flex items-center gap-1">
                <Clock class="w-3.5 h-3.5 text-amber-600" />
                <span>Deadline: <strong class="text-amber-900">{{ s.application_deadline ? new Date(s.application_deadline).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : 'Rolling' }}</strong></span>
              </div>
            </div>
          </div>

          <!-- Actions Column -->
          <div class="flex lg:flex-col items-stretch lg:items-end justify-between w-full lg:w-48 gap-2.5 shrink-0 pt-4 lg:pt-0 border-t lg:border-t-0 border-[#0B132B]/10">
            <!-- View Full Scheme Details (Primary) -->
            <button
              @click="viewSchemeDetail(s.code)"
              class="neo-btn neo-btn-navy w-full py-2.5 px-3 text-xs font-bold"
            >
              <span>View Details & Steps</span>
              <ArrowRight class="w-3.5 h-3.5" />
            </button>

            <!-- Save / Track Application (Secondary) -->
            <div class="w-full">
              <button
                v-if="!isSchemeTracked(s.code)"
                @click="store.saveSchemeToTracker(s.code, 'NOT_STARTED')"
                class="neo-btn neo-btn-paper w-full py-2 px-3 text-xs font-bold text-[#0B132B]"
              >
                <BookmarkPlus class="w-3.5 h-3.5 text-amber-600" />
                <span>Save to Tracker</span>
              </button>

              <router-link
                v-else
                to="/tracker"
                class="neo-btn neo-btn-emerald w-full py-2 px-3 text-xs font-bold"
              >
                <Check class="w-3.5 h-3.5" />
                <span>Saved ({{ getTrackedStatus(s.code) }})</span>
              </router-link>
            </div>

            <!-- Quick Text Links -->
            <div class="w-full flex items-center justify-center gap-2.5 pt-1 text-[11px] text-slate-600 font-bold">
              <a
                :href="s.official_portal_url"
                target="_blank"
                rel="noopener noreferrer"
                class="hover:text-amber-700 inline-flex items-center gap-0.5 transition-colors"
              >
                <span>{{ s.portal_name || 'Portal' }}</span>
                <ExternalLink class="w-2.5 h-2.5" />
              </a>
              <span class="text-slate-300">•</span>
              <button
                @click="openStatutoryModal(s)"
                class="hover:text-amber-700 inline-flex items-center gap-0.5 transition-colors"
              >
                <span>GR Audit</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="neo-box text-center py-12 p-8 space-y-2 bg-white">
      <div class="w-12 h-12 rounded-xl bg-slate-100 border-[1.5px] border-[#0B132B] text-slate-600 flex items-center justify-center mx-auto shadow-[2px_2px_0_0_#0B132B]">
        <HelpCircle class="w-6 h-6" />
      </div>
      <h3 class="text-base font-extrabold text-[#0B132B] font-heading">No schemes found under this filter</h3>
      <p class="text-xs text-slate-600 font-medium max-w-md mx-auto">
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
      class="fixed inset-0 z-50 bg-[#0B132B]/60 backdrop-blur-xs flex items-center justify-center p-4 animate-in fade-in"
    >
      <div class="neo-box bg-white max-w-lg w-full p-6 shadow-[5px_5px_0_0_#0B132B] space-y-4">
        <div class="flex items-center justify-between pb-3 border-b-[1.5px] border-[#0B132B]/20">
          <h3 class="font-extrabold text-[#0B132B] text-base flex items-center gap-2 font-heading">
            <Edit2 class="w-4 h-4 text-amber-600" />
            Edit Profile Parameters
          </h3>
          <button @click="isEditProfileOpen = false" class="text-slate-400 hover:text-slate-700 p-1 font-bold">
            <X class="w-5 h-5" />
          </button>
        </div>

        <form @submit.prevent="saveProfileEdit" class="space-y-3.5 text-xs">
          <div>
            <label class="block font-bold text-[#0B132B] mb-1">Student Name / Tag:</label>
            <input 
              v-model="editName"
              type="text"
              class="neo-input w-full text-sm px-3 py-2"
              required
            />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block font-bold text-[#0B132B] mb-1">Age:</label>
              <input 
                v-model.number="editAge"
                type="number"
                min="0"
                max="120"
                class="neo-input w-full text-sm px-3 py-2 font-mono"
                required
              />
            </div>

            <div>
              <label class="block font-bold text-[#0B132B] mb-1">District (Maharashtra):</label>
              <input 
                v-model="editDistrict"
                type="text"
                class="neo-input w-full text-sm px-3 py-2"
                required
              />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block font-bold text-[#0B132B] mb-1">Caste Category:</label>
              <select 
                v-model="editCaste"
                class="neo-input w-full text-sm px-3 py-2"
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
              <label class="block font-bold text-[#0B132B] mb-1">Annual Family Income (₹):</label>
              <input 
                v-model.number="editIncome"
                type="number"
                min="0"
                step="1000"
                class="neo-input w-full text-sm px-3 py-2 font-mono"
                required
              />
            </div>
          </div>

          <div class="pt-2 flex items-center justify-end gap-2 border-t-[1.5px] border-[#0B132B]/15">
            <button
              type="button"
              @click="isEditProfileOpen = false"
              class="neo-btn neo-btn-paper px-4 py-2 text-xs font-bold text-[#0B132B]"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="store.isLoading"
              class="neo-btn neo-btn-saffron px-5 py-2 text-xs font-bold"
            >
              Save & Re-Evaluate
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
