<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../services/api';
import {
  Building2,
  Users,
  ShieldCheck,
  LogOut,
  Plus,
  Search,
  CheckCircle2,
  AlertTriangle,
  ChevronRight,
  Sparkles,
  AlertCircle,
  X,
  RefreshCw,
  CheckSquare,
  Square
} from '@lucide/vue';

// Demo accounts for instant 1-click testing
const DEMO_ACCOUNTS = [
  { username: 'counselor_sangli', name: 'Suresh Patil', role: 'Counselor', center: 'CSC Sangli (412)', code: 'CSC_SANGLI_412' },
  { username: 'supervisor_sangli', name: 'Anjali Deshmukh', role: 'Center Supervisor', center: 'CSC Sangli (412)', code: 'CSC_SANGLI_412' },
  { username: 'counselor_nashik', name: 'Rahul Shinde', role: 'Counselor (Other Kendra)', center: 'Kendra Nashik (108)', code: 'KENDRA_NASHIK_108' },
];

// Counselor Auth State
const counselorToken = ref(localStorage.getItem('yojnavia_counselor_token') || '');
const counselorUser = ref<any>(localStorage.getItem('yojnavia_counselor_user') ? JSON.parse(localStorage.getItem('yojnavia_counselor_user')!) : null);
const isLoggingIn = ref(false);
const loginError = ref('');
const loginUsername = ref('');
const loginPassword = ref('');

// Center Analytics State
const analyticsData = ref<any>(null);
const isLoadingAnalytics = ref(false);

// Citizen Cases State
const casesList = ref<any[]>([]);
const isLoadingCases = ref(false);
const searchQuery = ref('');
const statusFilter = ref('ALL');
const priorityFilter = ref('ALL');
const crossCenterWarning = ref('');

// Registration Modal State
const isRegisterModalOpen = ref(false);
const isRegistering = ref(false);
const registrationError = ref('');
const registrationForm = ref({
  citizen_name: '',
  citizen_mobile: '+91 ',
  target_scheme_category: 'Higher Education & Scholarships',
  priority: 'MEDIUM',
  follow_up_date: '',
  consent_method: 'IN_PERSON_VERBAL',
  initial_notes: '',
});

// Case Workspace Drawer / Modal State
const selectedCase = ref<any>(null);
const isLoadingCaseDetail = ref(false);
const activeTab = ref<'intake' | 'eligibility' | 'preflight' | 'notes' | 'handover' | 'audit'>('intake');

// Assisted Profile Intake State
const profileForm = ref<any>({
  age: 20,
  gender: 'MALE',
  state: 'Maharashtra',
  district: 'Sangli',
  caste_category: 'OBC',
  caste_name: '',
  annual_family_income: 120000,
  current_course_level: 'PROFESSIONAL_DEGREE',
  course_name: 'B.Tech / BE Engineering',
  admission_quota: 'CAP_ROUND',
  previous_year_percentage: 75.5,
  accommodation_type: 'DAY_SCHOLAR',
  parent_is_farmer: true,
  parent_land_acres: 2.5,
  has_aadhaar_seeded_bank: true,
});
const isUpdatingProfile = ref(false);
const profileUpdateSuccess = ref('');

// Eligibility Discovery State
const eligibilityResults = ref<any>(null);
const isEvaluatingEligibility = ref(false);

// Preflight & Document Checklist State
const selectedPreflightScheme = ref('MH_DTE_EBC_2024');
const preflightResult = ref<any>(null);
const isRunningPreflight = ref(false);
const documentChecklist = ref<any[]>([]);
const checkedDocCodes = ref<string[]>([]);
const isLoadingDocuments = ref(false);
const isSavingDocuments = ref(false);

// Notes State
const newNoteContent = ref('');
const newNoteType = ref('GENERAL_NOTE');
const isNotePinned = ref(false);
const isSubmittingNote = ref(false);

// Escalation State
const isEscalating = ref(false);
const escalationReason = ref('');

// Closure State
const isClosing = ref(false);
const closureSummary = ref('');

// Consent Withdrawal State
const isWithdrawing = ref(false);

// Helper to get auth headers
const getAuthHeaders = () => {
  return counselorToken.value ? { Authorization: `Bearer ${counselorToken.value}` } : {};
};

// -------------------------------------------------------------
// Authentication Actions
// -------------------------------------------------------------
const handleDemoLogin = async (username: string) => {
  isLoggingIn.value = true;
  loginError.value = '';
  crossCenterWarning.value = '';
  try {
    const res = await api.post('/counselor/auth/login/', { demo_user: username });
    counselorToken.value = res.data.token;
    counselorUser.value = res.data.user;
    localStorage.setItem('yojnavia_counselor_token', res.data.token);
    localStorage.setItem('yojnavia_counselor_user', JSON.stringify(res.data.user));
    await fetchCenterData();
  } catch (err: any) {
    loginError.value = err.response?.data?.error || 'Login failed. Please check credentials.';
  } finally {
    isLoggingIn.value = false;
  }
};

const handleCustomLogin = async () => {
  if (!loginUsername.value || !loginPassword.value) {
    loginError.value = 'Please provide username and password.';
    return;
  }
  isLoggingIn.value = true;
  loginError.value = '';
  try {
    const res = await api.post('/counselor/auth/login/', {
      username: loginUsername.value,
      password: loginPassword.value,
    });
    counselorToken.value = res.data.token;
    counselorUser.value = res.data.user;
    localStorage.setItem('yojnavia_counselor_token', res.data.token);
    localStorage.setItem('yojnavia_counselor_user', JSON.stringify(res.data.user));
    await fetchCenterData();
  } catch (err: any) {
    loginError.value = err.response?.data?.error || 'Authentication error. Please retry.';
  } finally {
    isLoggingIn.value = false;
  }
};

const handleLogout = () => {
  counselorToken.value = '';
  counselorUser.value = null;
  selectedCase.value = null;
  casesList.value = [];
  analyticsData.value = null;
  crossCenterWarning.value = '';
  localStorage.removeItem('yojnavia_counselor_token');
  localStorage.removeItem('yojnavia_counselor_user');
};

// -------------------------------------------------------------
// Data Fetching: Analytics & Cases
// -------------------------------------------------------------
const fetchCenterData = async () => {
  if (!counselorToken.value) return;
  await Promise.all([fetchAnalytics(), fetchCases()]);
};

const fetchAnalytics = async () => {
  isLoadingAnalytics.value = true;
  try {
    const res = await api.get('/counselor/analytics/', { headers: getAuthHeaders() });
    analyticsData.value = res.data;
  } catch (err: any) {
    console.error('Failed to fetch counselor analytics:', err);
  } finally {
    isLoadingAnalytics.value = false;
  }
};

const fetchCases = async () => {
  isLoadingCases.value = true;
  crossCenterWarning.value = '';
  try {
    const params: any = {};
    if (statusFilter.value !== 'ALL') params.status = statusFilter.value;
    if (priorityFilter.value !== 'ALL') params.priority = priorityFilter.value;
    if (searchQuery.value.trim()) params.search = searchQuery.value.trim();

    const res = await api.get('/counselor/cases/', {
      headers: getAuthHeaders(),
      params,
    });
    casesList.value = res.data.results || [];
  } catch (err: any) {
    console.error('Failed to fetch cases list:', err);
  } finally {
    isLoadingCases.value = false;
  }
};

// -------------------------------------------------------------
// Citizen Case Registration
// -------------------------------------------------------------
const openRegisterModal = () => {
  registrationForm.value = {
    citizen_name: '',
    citizen_mobile: '+91 ',
    target_scheme_category: 'Higher Education & Scholarships',
    priority: 'MEDIUM',
    follow_up_date: '',
    consent_method: 'IN_PERSON_VERBAL',
    initial_notes: '',
  };
  registrationError.value = '';
  isRegisterModalOpen.value = true;
};

const handleRegisterCase = async () => {
  if (!registrationForm.value.citizen_name.trim()) {
    registrationError.value = 'Citizen name is required.';
    return;
  }
  isRegistering.value = true;
  registrationError.value = '';
  try {
    const res = await api.post('/counselor/cases/', registrationForm.value, {
      headers: getAuthHeaders(),
    });
    isRegisterModalOpen.value = false;
    await fetchCenterData();
    // Automatically open the new case workspace
    if (res.data?.case?.id) {
      await openCaseWorkspace(res.data.case.id);
    }
  } catch (err: any) {
    registrationError.value = err.response?.data?.error || err.response?.data?.detail || 'Failed to register citizen case.';
  } finally {
    isRegistering.value = false;
  }
};

// -------------------------------------------------------------
// Case Workspace & Detail
// -------------------------------------------------------------
const openCaseWorkspace = async (caseId: string) => {
  isLoadingCaseDetail.value = true;
  selectedCase.value = null;
  crossCenterWarning.value = '';
  profileUpdateSuccess.value = '';
  eligibilityResults.value = null;
  preflightResult.value = null;
  activeTab.value = 'intake';

  try {
    const res = await api.get(`/counselor/cases/${caseId}/`, {
      headers: getAuthHeaders(),
    });
    selectedCase.value = res.data.case;

    // Populate profile form if profile exists
    if (selectedCase.value.profile) {
      const p = selectedCase.value.profile;
      profileForm.value = {
        age: p.age || 20,
        gender: p.gender || 'MALE',
        state: p.state || 'Maharashtra',
        district: p.district || counselorUser.value?.center?.district || 'Sangli',
        caste_category: p.caste_category || 'OBC',
        caste_name: p.caste_name || '',
        annual_family_income: p.annual_family_income || 120000,
        current_course_level: p.current_course_level || 'PROFESSIONAL_DEGREE',
        course_name: p.course_name || 'B.Tech / BE Engineering',
        admission_quota: p.admission_quota || 'CAP_ROUND',
        previous_year_percentage: p.previous_year_percentage || 75.0,
        accommodation_type: p.accommodation_type || 'DAY_SCHOLAR',
        parent_is_farmer: p.parent_is_farmer ?? true,
        parent_land_acres: p.parent_land_acres || 2.0,
        has_aadhaar_seeded_bank: p.has_aadhaar_seeded_bank ?? true,
      };
    }

    // Fetch initial document checklist
    await fetchDocuments();
  } catch (err: any) {
    if (err.response?.status === 403) {
      crossCenterWarning.value =
        err.response?.data?.detail ||
        'Cross-center access is strictly forbidden. Unauthorized attempt recorded in tamper-evident security audit log.';
    } else {
      console.error('Failed to open case detail:', err);
    }
  } finally {
    isLoadingCaseDetail.value = false;
  }
};

// -------------------------------------------------------------
// Profile Intake Update
// -------------------------------------------------------------
const handleUpdateProfile = async () => {
  if (!selectedCase.value) return;
  isUpdatingProfile.value = true;
  profileUpdateSuccess.value = '';
  try {
    const res = await api.post(
      `/counselor/cases/${selectedCase.value.id}/update_profile/`,
      { profile: profileForm.value },
      { headers: getAuthHeaders() }
    );
    profileUpdateSuccess.value = 'Citizen profile confirmed and synchronized with deterministic eligibility engine!';
    selectedCase.value = res.data.case;
    if (res.data.eligibility) {
      eligibilityResults.value = res.data.eligibility;
    }
    await fetchAnalytics();
  } catch (err: any) {
    alert(err.response?.data?.detail || err.response?.data?.error || 'Profile update failed.');
  } finally {
    isUpdatingProfile.value = false;
  }
};

// -------------------------------------------------------------
// Scheme Eligibility Evaluation
// -------------------------------------------------------------
const handleEvaluateEligibility = async () => {
  if (!selectedCase.value) return;
  isEvaluatingEligibility.value = true;
  try {
    const res = await api.post(
      `/counselor/cases/${selectedCase.value.id}/evaluate_eligibility/`,
      {},
      { headers: getAuthHeaders() }
    );
    eligibilityResults.value = res.data.eligibility;
    selectedCase.value.case_status = 'ELIGIBILITY_DISCOVERED';
    await fetchAnalytics();
  } catch (err: any) {
    alert(err.response?.data?.detail || err.response?.data?.error || 'Eligibility evaluation failed.');
  } finally {
    isEvaluatingEligibility.value = false;
  }
};

// -------------------------------------------------------------
// Preflight Scrutiny Audit
// -------------------------------------------------------------
const handleRunPreflight = async () => {
  if (!selectedCase.value) return;
  isRunningPreflight.value = true;
  try {
    const res = await api.post(
      `/counselor/cases/${selectedCase.value.id}/preflight/`,
      {
        scheme_code: selectedPreflightScheme.value,
        checked_documents: checkedDocCodes.value,
      },
      { headers: getAuthHeaders() }
    );
    preflightResult.value = res.data.preflight_audit;
  } catch (err: any) {
    alert(err.response?.data?.detail || err.response?.data?.error || 'Preflight audit failed.');
  } finally {
    isRunningPreflight.value = false;
  }
};

// -------------------------------------------------------------
// Document Checklist Handling
// -------------------------------------------------------------
const fetchDocuments = async () => {
  if (!selectedCase.value) return;
  isLoadingDocuments.value = true;
  try {
    const res = await api.get(
      `/counselor/cases/${selectedCase.value.id}/documents/?scheme_code=${selectedPreflightScheme.value}`,
      { headers: getAuthHeaders() }
    );
    documentChecklist.value = res.data.documents || [];
    checkedDocCodes.value = documentChecklist.value
      .filter((d: any) => d.status === 'VERIFIED')
      .map((d: any) => d.code);
  } catch (err: any) {
    console.error('Failed to load documents:', err);
  } finally {
    isLoadingDocuments.value = false;
  }
};

const toggleDocumentCheck = (docCode: string) => {
  if (checkedDocCodes.value.includes(docCode)) {
    checkedDocCodes.value = checkedDocCodes.value.filter((c) => c !== docCode);
  } else {
    checkedDocCodes.value.push(docCode);
  }
};

const handleSaveDocuments = async () => {
  if (!selectedCase.value) return;
  isSavingDocuments.value = true;
  try {
    const verifiedList = documentChecklist.value.map((doc) => ({
      document_code: doc.code,
      status: checkedDocCodes.value.includes(doc.code) ? 'VERIFIED' : 'PENDING',
    }));

    const res = await api.post(
      `/counselor/cases/${selectedCase.value.id}/documents/`,
      {
        scheme_code: selectedPreflightScheme.value,
        verified_documents: verifiedList,
      },
      { headers: getAuthHeaders() }
    );
    documentChecklist.value = res.data.documents;
    alert('Document procurement verification saved successfully.');
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Failed to save document checklist.');
  } finally {
    isSavingDocuments.value = false;
  }
};

// -------------------------------------------------------------
// Notes & Escalation
// -------------------------------------------------------------
const handleAddNote = async () => {
  if (!selectedCase.value || !newNoteContent.value.trim()) return;
  isSubmittingNote.value = true;
  try {
    const res = await api.post(
      `/counselor/cases/${selectedCase.value.id}/notes/`,
      {
        note_type: newNoteType.value,
        content: newNoteContent.value.trim(),
        is_pinned: isNotePinned.value,
      },
      { headers: getAuthHeaders() }
    );
    selectedCase.value.notes.unshift(res.data.note);
    newNoteContent.value = '';
    isNotePinned.value = false;
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Failed to add note.');
  } finally {
    isSubmittingNote.value = false;
  }
};

const handleEscalateCase = async () => {
  if (!selectedCase.value || !escalationReason.value.trim()) {
    alert('Please provide a specific reason for supervisor escalation.');
    return;
  }
  isEscalating.value = true;
  try {
    const res = await api.post(
      `/counselor/cases/${selectedCase.value.id}/escalate/`,
      { reason: escalationReason.value.trim() },
      { headers: getAuthHeaders() }
    );
    selectedCase.value = res.data.case;
    escalationReason.value = '';
    await fetchAnalytics();
    alert('Case has been successfully escalated to Center Supervisor with pinned remark.');
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Escalation failed.');
  } finally {
    isEscalating.value = false;
  }
};

// -------------------------------------------------------------
// Handover & Closure
// -------------------------------------------------------------
const handleCloseCase = async () => {
  if (!selectedCase.value || !closureSummary.value.trim()) {
    alert('Please enter a handover summary explaining documents handed over to the citizen.');
    return;
  }
  isClosing.value = true;
  try {
    const res = await api.post(
      `/counselor/cases/${selectedCase.value.id}/close/`,
      { summary: closureSummary.value.trim() },
      { headers: getAuthHeaders() }
    );
    selectedCase.value = res.data.case;
    closureSummary.value = '';
    await fetchAnalytics();
    alert('Case successfully closed and handed over to citizen.');
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Closure failed.');
  } finally {
    isClosing.value = false;
  }
};

// -------------------------------------------------------------
// Consent Withdrawal
// -------------------------------------------------------------
const handleWithdrawConsent = async () => {
  if (!selectedCase.value) return;
  const reason = prompt('Confirm citizen consent withdrawal. Enter reason for record:', 'Citizen requested independent portal application.');
  if (reason === null) return;

  isWithdrawing.value = true;
  try {
    const res = await api.post(
      `/counselor/cases/${selectedCase.value.id}/withdraw_consent/`,
      { reason: reason || 'Citizen withdrew consent at Kendra desk.' },
      { headers: getAuthHeaders() }
    );
    selectedCase.value.consent.consent_status = 'WITHDRAWN';
    alert(res.data.message);
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Consent withdrawal failed.');
  } finally {
    isWithdrawing.value = false;
  }
};

// Initialize
onMounted(async () => {
  if (!counselorToken.value) {
    // Default to Sangli counselor for instant demonstration
    await handleDemoLogin('counselor_sangli');
  } else {
    await fetchCenterData();
  }
});
</script>

<template>
  <div class="min-h-screen bg-[#FBFBFA] text-slate-800 pb-16">
    <!-- Top CSC Center Header Strip -->
    <header class="bg-white border-b-[1.5px] border-[#0B132B] sticky top-16 z-30 shadow-[0_2px_0_0_#0B132B]/10">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <!-- Kendra Info & Operator -->
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-amber-500/10 border-[1.5px] border-[#0B132B] text-amber-700 flex items-center justify-center shrink-0 shadow-[1.5px_1.5px_0_0_#0B132B]">
              <Building2 class="w-5 h-5" />
            </div>
            <div>
              <div class="flex items-center gap-2 flex-wrap">
                <h1 class="text-base font-extrabold tracking-tight text-[#0B132B] font-heading">
                  {{ counselorUser?.center?.name || 'CSC Seva Kendra Assisted Desk' }}
                </h1>
                <span class="neo-stamp neo-stamp-navy font-mono text-[9px]">
                  {{ counselorUser?.center?.code || 'CSC_SANGLI_412' }}
                </span>
                <span
                  class="neo-stamp text-[9px]"
                  :class="counselorUser?.role === 'CENTER_SUPERVISOR' ? 'neo-stamp-amber' : 'neo-stamp-emerald'"
                >
                  {{ counselorUser?.role?.replace('_', ' ') || 'Counselor' }}
                </span>
              </div>
              <p class="text-xs text-slate-600 flex items-center gap-2 mt-0.5 font-medium">
                <span>VLE ID: <strong class="text-[#0B132B] font-mono">{{ counselorUser?.center?.vle_id || 'VLE-MH-SNG-412' }}</strong></span>
                <span>•</span>
                <span>Operator: <strong class="text-[#0B132B]">{{ counselorUser?.name || 'Suresh Patil' }}</strong></span>
                <span>•</span>
                <span>Taluka: <strong class="text-[#0B132B]">{{ counselorUser?.center?.taluka || 'Miraj' }}, {{ counselorUser?.center?.district || 'Sangli' }}</strong></span>
              </p>
            </div>
          </div>

          <!-- Account Switcher & Actions -->
          <div class="flex items-center gap-2 flex-wrap">
            <div class="text-[11px] font-bold text-slate-500 uppercase tracking-wider hidden sm:block">Demo Switch:</div>
            <div class="flex items-center gap-1 bg-[#F5F5F3] p-1 rounded-xl border-[1.5px] border-[#0B132B] shadow-[1.5px_1.5px_0_0_#0B132B]">
              <button
                v-for="acc in DEMO_ACCOUNTS"
                :key="acc.username"
                @click="handleDemoLogin(acc.username)"
                class="px-2.5 py-1 text-xs font-bold rounded-lg transition-all cursor-pointer"
                :class="counselorUser?.username === acc.username ? 'bg-[#0B132B] text-white shadow-xs' : 'text-slate-700 hover:text-black'"
              >
                {{ acc.name.split(' ')[0] }} ({{ acc.role === 'Center Supervisor' ? 'Sup.' : acc.code.split('_')[1] }})
              </button>
            </div>

            <button
              @click="fetchCenterData"
              class="p-2 text-slate-700 hover:text-black bg-white border-[1.5px] border-[#0B132B] rounded-xl shadow-[1.5px_1.5px_0_0_#0B132B] transition-transform active:translate-x-0.5 active:translate-y-0.5"
              title="Refresh Center Data"
            >
              <RefreshCw class="w-4 h-4" :class="isLoadingCases ? 'animate-spin' : ''" />
            </button>

            <button
              @click="handleLogout"
              class="p-2 text-slate-700 hover:text-red-700 bg-white border-[1.5px] border-[#0B132B] rounded-xl shadow-[1.5px_1.5px_0_0_#0B132B] transition-transform active:translate-x-0.5 active:translate-y-0.5"
              title="Sign Out of Counselor Desk"
            >
              <LogOut class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Logged Out Sign-in State -->
    <div v-if="!counselorUser" class="max-w-md mx-auto px-4 pt-16">
      <div class="neo-box bg-white p-6 text-center space-y-4">
        <div class="w-12 h-12 bg-amber-500/10 text-amber-700 border-[1.5px] border-[#0B132B] rounded-2xl flex items-center justify-center mx-auto shadow-[2px_2px_0_0_#0B132B]">
          <Building2 class="w-6 h-6" />
        </div>
        <div>
          <h2 class="text-lg font-extrabold text-[#0B132B] font-heading">CSC Counselor Assisted Desk</h2>
          <p class="text-xs text-slate-600 mt-1 font-medium">Sign in with your Kendra credentials or choose a demo operator.</p>
        </div>

        <div v-if="loginError" class="p-3 bg-red-50 border-[1.5px] border-[#0B132B] text-red-900 text-xs rounded-xl font-bold shadow-[2px_2px_0_0_#0B132B]">
          {{ loginError }}
        </div>

        <!-- 1-Click Demo Select -->
        <div class="space-y-2 pt-2">
          <div class="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Quick Demo Operator</div>
          <button
            v-for="acc in DEMO_ACCOUNTS"
            :key="acc.username"
            @click="handleDemoLogin(acc.username)"
            class="neo-btn neo-btn-paper w-full py-2 px-3 text-xs font-bold text-slate-800 flex items-center justify-between"
          >
            <span>{{ acc.name }} ({{ acc.role }})</span>
            <span class="text-[10px] text-slate-500 font-mono">{{ acc.code }}</span>
          </button>
        </div>

        <!-- Or Manual Login Form -->
        <form @submit.prevent="handleCustomLogin" class="pt-4 border-t-[1.5px] border-[#0B132B]/15 space-y-3 text-left">
          <div class="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Custom Operator Login</div>
          <div>
            <label class="block text-xs font-bold text-[#0B132B] mb-1">Username</label>
            <input
              v-model="loginUsername"
              type="text"
              placeholder="e.g. counselor_sangli"
              class="neo-input w-full px-3 py-1.5 text-xs"
            />
          </div>
          <div>
            <label class="block text-xs font-bold text-[#0B132B] mb-1">Password</label>
            <input
              v-model="loginPassword"
              type="password"
              placeholder="••••••••"
              class="neo-input w-full px-3 py-1.5 text-xs"
            />
          </div>
          <button
            type="submit"
            :disabled="isLoggingIn"
            class="neo-btn neo-btn-saffron w-full py-2 text-xs font-bold disabled:opacity-50"
          >
            {{ isLoggingIn ? 'Signing in...' : 'Sign In with Credentials' }}
          </button>
        </form>
      </div>
    </div>

    <!-- Cross-Center Block Alert (Demonstrates Partition Integrity) -->
    <div v-if="crossCenterWarning" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4">
      <div class="neo-box bg-[#FFF1F2] text-red-950 p-4 flex items-start gap-3">
        <AlertTriangle class="w-5 h-5 text-red-700 shrink-0 mt-0.5" />
        <div class="flex-1">
          <h4 class="text-sm font-extrabold text-[#0B132B]">Security Boundary Enforced (HTTP 403 Forbidden)</h4>
          <p class="text-xs text-red-900 mt-0.5 font-medium">{{ crossCenterWarning }}</p>
          <p class="text-[11px] text-red-700 mt-1 font-mono font-bold">
            Audit Event: UNAUTHORIZED_ACCESS_BLOCKED • Kendra partition strictly prevents cross-taluka profile tampering.
          </p>
        </div>
        <button @click="crossCenterWarning = ''" class="text-red-700 hover:text-black font-bold">
          <X class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Main Content Container -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6 space-y-6">
      
      <!-- Top Analytics Strip (Aggregated, Zero PII) -->
      <section class="neo-box bg-white p-5">
        <div class="flex items-center justify-between mb-4 pb-2 border-b-[1.5px] border-[#0B132B]/15 flex-wrap gap-2">
          <div class="flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full bg-emerald-600"></span>
            <h2 class="text-xs font-extrabold text-[#0B132B] uppercase tracking-wider font-heading">
              Kendra Assisted Performance Metrics
            </h2>
          </div>
          <div class="flex items-center gap-2">
            <span class="neo-stamp neo-stamp-emerald text-[10px]">
              <ShieldCheck class="w-3.5 h-3.5 text-emerald-700" />
              Zero-PII Aggregation • Privacy Protected
            </span>
          </div>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div class="bg-[#FBFBFA] border-[1.5px] border-[#0B132B] rounded-xl p-3 shadow-[1.5px_1.5px_0_0_#0B132B]">
            <div class="text-[11px] font-bold text-slate-500">Total Cases</div>
            <div class="text-xl font-extrabold text-[#0B132B] mt-1 font-heading">
              {{ analyticsData?.metrics?.total_cases_handled ?? '—' }}
            </div>
            <div class="text-[10px] text-slate-500 mt-0.5 font-medium">Assisted to date</div>
          </div>

          <div class="bg-amber-50 border-[1.5px] border-[#0B132B] rounded-xl p-3 shadow-[1.5px_1.5px_0_0_#0B132B]">
            <div class="text-[11px] font-bold text-amber-900">Intake Pending</div>
            <div class="text-xl font-extrabold text-amber-950 mt-1 font-heading">
              {{ analyticsData?.metrics?.intake_pending ?? '—' }}
            </div>
            <div class="text-[10px] text-amber-800 mt-0.5 font-medium">Needs interview</div>
          </div>

          <div class="bg-blue-50 border-[1.5px] border-[#0B132B] rounded-xl p-3 shadow-[1.5px_1.5px_0_0_#0B132B]">
            <div class="text-[11px] font-bold text-blue-900">Eligibility Found</div>
            <div class="text-xl font-extrabold text-blue-950 mt-1 font-heading">
              {{ analyticsData?.metrics?.eligibility_discovered ?? '—' }}
            </div>
            <div class="text-[10px] text-blue-800 mt-0.5 font-medium">Schemes identified</div>
          </div>

          <div class="bg-orange-50 border-[1.5px] border-[#0B132B] rounded-xl p-3 shadow-[1.5px_1.5px_0_0_#0B132B]">
            <div class="text-[11px] font-bold text-orange-900">Docs Pending</div>
            <div class="text-xl font-extrabold text-orange-950 mt-1 font-heading">
              {{ analyticsData?.metrics?.documents_pending ?? '—' }}
            </div>
            <div class="text-[10px] text-orange-800 mt-0.5 font-medium">Awaiting certificates</div>
          </div>

          <div class="bg-emerald-50 border-[1.5px] border-[#0B132B] rounded-xl p-3 shadow-[1.5px_1.5px_0_0_#0B132B]">
            <div class="text-[11px] font-bold text-emerald-900">Ready to Apply</div>
            <div class="text-xl font-extrabold text-emerald-950 mt-1 font-heading">
              {{ analyticsData?.metrics?.ready_for_application ?? '—' }}
            </div>
            <div class="text-[10px] text-emerald-800 mt-0.5 font-medium">Preflight passed</div>
          </div>

          <div class="bg-purple-50 border-[1.5px] border-[#0B132B] rounded-xl p-3 shadow-[1.5px_1.5px_0_0_#0B132B]">
            <div class="text-[11px] font-bold text-purple-900">Supervisor Escalated</div>
            <div class="text-xl font-extrabold text-purple-950 mt-1 font-heading">
              {{ analyticsData?.metrics?.escalated_to_supervisor ?? '—' }}
            </div>
            <div class="text-[10px] text-purple-800 mt-0.5 font-medium">Under VLE review</div>
          </div>
        </div>

        <!-- Top Scheme Categories Banner -->
        <div v-if="analyticsData?.top_categories?.length" class="mt-4 pt-3 border-t-[1.5px] border-[#0B132B]/10 flex items-center gap-2 flex-wrap">
          <span class="text-xs font-bold text-slate-600">Frequently Requested Streams:</span>
          <span
            v-for="cat in analyticsData.top_categories"
            :key="cat.target_scheme_category"
            class="text-xs font-bold px-2.5 py-1 bg-[#F5F5F3] text-slate-800 rounded-lg border border-[#0B132B]/20"
          >
            {{ cat.target_scheme_category }} ({{ cat.count }})
          </span>
        </div>
      </section>

      <!-- Citizen Case Registry Section -->
      <section class="neo-box bg-white p-5">
        
        <!-- Controls Bar: Title, Search, Filter & Register CTA -->
        <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4 border-b-[1.5px] border-[#0B132B]/15">
          <div>
            <h3 class="text-base font-extrabold text-[#0B132B] flex items-center gap-2 font-heading">
              <Users class="w-4 h-4 text-amber-600" />
              Citizen Case Desk
            </h3>
            <p class="text-xs text-slate-600 mt-0.5 font-medium">
              Assisted intake, scheme discovery, certificate checklists and preflight audit.
            </p>
          </div>

          <div class="flex items-center gap-2 flex-wrap">
            <!-- Search Input -->
            <div class="relative w-full sm:w-64">
              <Search class="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                v-model="searchQuery"
                @keyup.enter="fetchCases"
                type="text"
                placeholder="Search citizen or case #..."
                class="neo-input w-full pl-9 pr-3 py-1.5 text-xs"
              />
            </div>

            <!-- Priority Filter -->
            <select
              v-model="priorityFilter"
              @change="fetchCases"
              class="neo-input text-xs px-2.5 py-1.5 text-slate-700 font-bold"
            >
              <option value="ALL">All Priorities</option>
              <option value="URGENT">Urgent (&lt;7 Days)</option>
              <option value="HIGH">High Priority</option>
              <option value="MEDIUM">Medium Priority</option>
              <option value="LOW">Low Priority</option>
            </select>

            <!-- Register New Citizen Case Button -->
            <button
              @click="openRegisterModal"
              class="neo-btn neo-btn-saffron px-3 py-1.5 text-xs font-bold"
            >
              <Plus class="w-4 h-4" />
              <span>Register Citizen</span>
            </button>
          </div>
        </div>

        <!-- Status Filter Tabs -->
        <div class="flex items-center gap-1.5 mt-3 overflow-x-auto pb-1 text-xs">
          <button
            v-for="st in [
              { key: 'ALL', label: 'All Cases' },
              { key: 'INTAKE_PENDING', label: 'Intake Pending' },
              { key: 'ELIGIBILITY_DISCOVERED', label: 'Discovered' },
              { key: 'DOCUMENTS_PENDING', label: 'Docs Pending' },
              { key: 'READY_FOR_APPLICATION', label: 'Ready to Apply' },
              { key: 'ESCALATED_SUPERVISOR', label: 'Supervisor Escalated' },
              { key: 'CLOSED_HANDOVER', label: 'Closed' },
            ]"
            :key="st.key"
            @click="statusFilter = st.key; fetchCases();"
            class="neo-btn px-3 py-1.5 text-xs font-bold"
            :class="statusFilter === st.key ? 'neo-btn-navy' : 'neo-btn-paper text-slate-700'"
          >
            {{ st.label }}
          </button>
        </div>

        <!-- Cases Table -->
        <div class="mt-4 overflow-x-auto">
          <div v-if="isLoadingCases" class="py-12 text-center text-slate-400">
            <RefreshCw class="w-6 h-6 animate-spin mx-auto mb-2 text-amber-600" />
            <p class="text-xs">Loading Kendra registry...</p>
          </div>

          <div v-else-if="casesList.length === 0" class="py-12 text-center text-slate-400 border border-dashed border-slate-200 rounded-xl">
            <Users class="w-8 h-8 mx-auto mb-2 text-slate-300" />
            <p class="text-sm font-bold text-slate-700">No Citizen Cases Found</p>
            <p class="text-xs text-slate-500 mt-0.5">Click "Register Citizen" above to open a new assisted intake case.</p>
          </div>

          <table v-else class="w-full text-left text-xs">
            <thead>
              <tr class="border-b border-slate-200 text-slate-500 uppercase tracking-wider text-[10px] font-bold">
                <th class="py-2.5 px-3">Case ID</th>
                <th class="py-2.5 px-3">Citizen Contact</th>
                <th class="py-2.5 px-3">Category</th>
                <th class="py-2.5 px-3">Priority</th>
                <th class="py-2.5 px-3">Status</th>
                <th class="py-2.5 px-3">Consent</th>
                <th class="py-2.5 px-3">Counselor</th>
                <th class="py-2.5 px-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr
                v-for="c in casesList"
                :key="c.id"
                class="hover:bg-slate-50/80 transition-colors group"
              >
                <!-- Case ID -->
                <td class="py-3 px-3 font-mono font-bold text-slate-900">
                  {{ c.case_number }}
                  <div class="text-[10px] font-sans font-normal text-slate-400">
                    {{ new Date(c.created_at).toLocaleDateString() }}
                  </div>
                </td>

                <!-- Citizen Contact -->
                <td class="py-3 px-3">
                  <div class="font-bold text-slate-900">{{ c.citizen_name }}</div>
                  <div class="text-[11px] text-slate-500">{{ c.citizen_mobile || 'No Phone' }}</div>
                </td>

                <!-- Category -->
                <td class="py-3 px-3 text-slate-600">
                  {{ c.target_scheme_category }}
                </td>

                <!-- Priority Badge -->
                <td class="py-3 px-3">
                  <span
                    class="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-full"
                    :class="{
                      'bg-red-100 text-red-800 border border-red-200': c.priority === 'URGENT',
                      'bg-amber-100 text-amber-800 border border-amber-200': c.priority === 'HIGH',
                      'bg-blue-100 text-blue-800 border border-blue-200': c.priority === 'MEDIUM',
                      'bg-slate-100 text-slate-600': c.priority === 'LOW',
                    }"
                  >
                    {{ c.priority }}
                  </span>
                </td>

                <!-- Status Badge -->
                <td class="py-3 px-3">
                  <span
                    class="text-[10px] font-bold px-2 py-0.5 rounded-full"
                    :class="{
                      'bg-amber-50 text-amber-800 border border-amber-200': c.case_status === 'INTAKE_PENDING',
                      'bg-blue-50 text-blue-800 border border-blue-200': c.case_status === 'ELIGIBILITY_DISCOVERED',
                      'bg-orange-50 text-orange-800 border border-orange-200': c.case_status === 'DOCUMENTS_PENDING',
                      'bg-emerald-50 text-emerald-800 border border-emerald-200': c.case_status === 'READY_FOR_APPLICATION',
                      'bg-purple-50 text-purple-800 border border-purple-200': c.case_status === 'ESCALATED_SUPERVISOR',
                      'bg-slate-100 text-slate-600': c.case_status === 'CLOSED_HANDOVER',
                    }"
                  >
                    {{ c.case_status.replace(/_/g, ' ') }}
                  </span>
                </td>

                <!-- Consent Status -->
                <td class="py-3 px-3">
                  <span
                    class="text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1 w-max"
                    :class="c.consent_status === 'ACTIVE' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-red-50 text-red-700 border border-red-200'"
                  >
                    <ShieldCheck class="w-3 h-3" />
                    {{ c.consent_status }}
                  </span>
                </td>

                <!-- Counselor -->
                <td class="py-3 px-3 text-slate-500 text-[11px]">
                  {{ c.assigned_counselor_name || 'Unassigned' }}
                </td>

                <!-- Actions -->
                <td class="py-3 px-3 text-right">
                  <button
                    @click="openCaseWorkspace(c.id)"
                    class="px-2.5 py-1 text-xs font-bold text-amber-700 bg-amber-50 hover:bg-amber-100 border border-amber-200 rounded-lg transition-colors inline-flex items-center gap-1"
                  >
                    <span>Open Desk</span>
                    <ChevronRight class="w-3.5 h-3.5" />
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

    </main>

    <!-- Register Citizen Case Modal -->
    <div
      v-if="isRegisterModalOpen"
      class="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4"
    >
      <div class="bg-white rounded-2xl max-w-lg w-full border border-slate-200 shadow-xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        <div class="px-5 py-4 border-b border-slate-100 flex items-center justify-between bg-amber-50/50">
          <div class="flex items-center gap-2">
            <Building2 class="w-5 h-5 text-amber-600" />
            <h3 class="text-sm font-bold text-slate-900">Register Citizen for Assisted Welfare Desk</h3>
          </div>
          <button @click="isRegisterModalOpen = false" class="text-slate-400 hover:text-slate-700">
            <X class="w-5 h-5" />
          </button>
        </div>

        <form @submit.prevent="handleRegisterCase" class="p-5 space-y-4">
          <div v-if="registrationError" class="p-3 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700">
            {{ registrationError }}
          </div>

          <!-- Citizen Name & Mobile -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-bold text-slate-700 mb-1">Citizen Full Name *</label>
              <input
                v-model="registrationForm.citizen_name"
                type="text"
                required
                placeholder="e.g. Tanvi Jadhav"
                class="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-hidden focus:ring-2 focus:ring-amber-500/20"
              />
            </div>

            <div>
              <label class="block text-xs font-bold text-slate-700 mb-1">Mobile Contact</label>
              <input
                v-model="registrationForm.citizen_mobile"
                type="text"
                placeholder="+91 98XXXXXXXX"
                class="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-hidden focus:ring-2 focus:ring-amber-500/20"
              />
            </div>
          </div>

          <!-- Target Stream & Priority -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-bold text-slate-700 mb-1">Target Welfare Category</label>
              <select
                v-model="registrationForm.target_scheme_category"
                class="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-hidden"
              >
                <option value="Higher Education & Scholarships">Higher Education & Scholarships</option>
                <option value="Agriculture & Farmer Subsidies">Agriculture & Farmer Subsidies</option>
                <option value="Social Justice & Minority Welfare">Social Justice & Minority Welfare</option>
                <option value="Skill Training & Self-Employment">Skill Training & Self-Employment</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-bold text-slate-700 mb-1">Priority Level</label>
              <select
                v-model="registrationForm.priority"
                class="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-hidden"
              >
                <option value="MEDIUM">Medium</option>
                <option value="HIGH">High</option>
                <option value="URGENT">Urgent (Portal Deadline &lt;7d)</option>
                <option value="LOW">Low</option>
              </select>
            </div>
          </div>

          <!-- Mandatory Citizen Consent Card (Mandatory Requirement) -->
          <div class="bg-amber-50 border border-amber-200 rounded-xl p-3.5 space-y-2">
            <div class="flex items-center gap-1.5 text-amber-900 font-bold text-xs">
              <ShieldCheck class="w-4 h-4 text-amber-600" />
              <span>Mandatory Citizen Consent & Privacy Authorization</span>
            </div>
            <p class="text-[11px] text-amber-800 leading-relaxed">
              Citizen explicitly authorizes the CSC Counselor to review demographic profile, income band, certificate needs and portal tracking solely for scheme discovery.
              <strong class="text-amber-950 font-bold block mt-1">Zero-Aadhaar Rule: Aadhaar numbers, biometric OTPs and bank passwords will NEVER be recorded.</strong>
            </p>

            <div class="pt-2 border-t border-amber-200/60">
              <label class="block text-[11px] font-bold text-amber-900 mb-1">Consent Recording Method *</label>
              <select
                v-model="registrationForm.consent_method"
                class="w-full px-2.5 py-1 text-xs bg-white border border-amber-300 rounded-lg text-amber-900 font-semibold focus:outline-hidden"
              >
                <option value="IN_PERSON_VERBAL">In-Person Verbal Consent (Counselor Attested)</option>
                <option value="PHYSICAL_SLIP">Physical Signature Slip on File at Center</option>
                <option value="DIGITAL_ACK">Digital Acknowledgment on Kendra Terminal</option>
              </select>
            </div>
          </div>

          <!-- Initial Notes -->
          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">Initial Counselor Notes</label>
            <textarea
              v-model="registrationForm.initial_notes"
              rows="2"
              placeholder="e.g. Student inquiring for BE First Year Tuition Fee Waiver (EBC)..."
              class="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-hidden"
            ></textarea>
          </div>

          <!-- Form Actions -->
          <div class="pt-2 flex items-center justify-end gap-2 border-t border-slate-100">
            <button
              type="button"
              @click="isRegisterModalOpen = false"
              class="px-3 py-1.5 text-xs font-bold text-slate-600 hover:bg-slate-100 rounded-xl"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="isRegistering"
              class="px-4 py-1.5 text-xs font-bold bg-amber-600 hover:bg-amber-700 text-white rounded-xl shadow-xs disabled:opacity-50"
            >
              {{ isRegistering ? 'Registering...' : 'Register & Open Desk' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Case Workspace Drawer / Modal -->
    <div
      v-if="selectedCase"
      class="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex justify-end"
    >
      <div class="bg-white w-full max-w-4xl h-full shadow-2xl flex flex-col border-l border-slate-200 animate-in slide-in-from-right duration-200">
        
        <!-- Workspace Header -->
        <div class="px-6 py-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between shrink-0">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-amber-600 text-white flex items-center justify-center font-black">
              {{ selectedCase.citizen_name.charAt(0) }}
            </div>
            <div>
              <div class="flex items-center gap-2 flex-wrap">
                <h3 class="text-base font-black text-slate-900">{{ selectedCase.citizen_name }}</h3>
                <span class="font-mono text-xs px-2 py-0.5 rounded-md bg-white border border-slate-200 text-slate-700 font-bold">
                  {{ selectedCase.case_number }}
                </span>
                <span
                  class="text-[10px] font-bold px-2 py-0.5 rounded-full"
                  :class="selectedCase.consent?.consent_status === 'ACTIVE' ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'"
                >
                  Consent: {{ selectedCase.consent?.consent_status }}
                </span>
              </div>
              <p class="text-xs text-slate-500 mt-0.5">
                Contact: <strong class="text-slate-700">{{ selectedCase.citizen_mobile || 'None' }}</strong> •
                Center: <strong class="text-slate-700">{{ selectedCase.center?.name }}</strong>
              </p>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <button
              @click="selectedCase = null"
              class="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-200 rounded-xl transition-colors"
            >
              <X class="w-5 h-5" />
            </button>
          </div>
        </div>

        <!-- Consent Revocation Notice Banner -->
        <div
          v-if="selectedCase.consent?.consent_status === 'WITHDRAWN'"
          class="bg-red-50 border-b border-red-200 px-6 py-2.5 text-xs text-red-800 flex items-center gap-2"
        >
          <AlertTriangle class="w-4 h-4 text-red-600 shrink-0" />
          <span>Citizen consent has been withdrawn. Assisted profile editing and scheme discovery are legally locked.</span>
        </div>

        <!-- Workspace Tabs Navigation -->
        <div class="px-6 border-b border-slate-200 bg-white flex items-center gap-2 overflow-x-auto text-xs shrink-0">
          <button
            v-for="tb in [
              { key: 'intake', label: '1. Assisted Intake Form' },
              { key: 'eligibility', label: '2. Eligibility Discovery' },
              { key: 'preflight', label: '3. Preflight & Documents' },
              { key: 'notes', label: '4. Case Notes & Escalation' },
              { key: 'handover', label: '5. Handover & Closure' },
              { key: 'audit', label: '6. Consent & Audit Trail' },
            ]"
            :key="tb.key"
            @click="activeTab = tb.key as any"
            class="py-3 px-3 font-bold border-b-2 whitespace-nowrap transition-colors"
            :class="activeTab === tb.key ? 'border-amber-600 text-amber-700' : 'border-transparent text-slate-500 hover:text-slate-800'"
          >
            {{ tb.label }}
          </button>
        </div>

        <!-- Workspace Body Container -->
        <div class="flex-1 overflow-y-auto p-6 space-y-6">
          
          <!-- TAB 1: Assisted Citizen Intake Form -->
          <div v-if="activeTab === 'intake'" class="space-y-4">
            <div class="flex items-center justify-between pb-2 border-b border-slate-100">
              <div>
                <h4 class="text-sm font-bold text-slate-900">Demographic & Educational Intake</h4>
                <p class="text-xs text-slate-500">Collects verified facts for deterministic scheme rule matching.</p>
              </div>
              <span class="text-xs text-slate-400">Syncs directly with deterministic engine</span>
            </div>

            <div v-if="profileUpdateSuccess" class="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl text-xs flex items-center gap-2">
              <CheckCircle2 class="w-4 h-4 text-emerald-600 shrink-0" />
              <span>{{ profileUpdateSuccess }}</span>
            </div>

            <form @submit.prevent="handleUpdateProfile" class="space-y-4">
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label class="block text-xs font-bold text-slate-700 mb-1">Age</label>
                  <input
                    v-model.number="profileForm.age"
                    type="number"
                    min="14"
                    max="65"
                    class="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-xl"
                  />
                </div>
                <div>
                  <label class="block text-xs font-bold text-slate-700 mb-1">Gender</label>
                  <select v-model="profileForm.gender" class="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-xl">
                    <option value="MALE">Male</option>
                    <option value="FEMALE">Female</option>
                    <option value="OTHER">Other</option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-bold text-slate-700 mb-1">District (Maharashtra)</label>
                  <input
                    v-model="profileForm.district"
                    type="text"
                    class="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-xl"
                  />
                </div>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label class="block text-xs font-bold text-slate-700 mb-1">Caste Category</label>
                  <select v-model="profileForm.caste_category" class="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-xl">
                    <option value="OPEN">Open / General</option>
                    <option value="OBC">Other Backward Class (OBC)</option>
                    <option value="SC">Scheduled Caste (SC)</option>
                    <option value="ST">Scheduled Tribe (ST)</option>
                    <option value="VJNT">VJNT</option>
                    <option value="SBC">Special Backward Class</option>
                    <option value="EWS">Economically Weaker Section (EWS)</option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-bold text-slate-700 mb-1">Sub-Caste (Optional)</label>
                  <input
                    v-model="profileForm.caste_name"
                    type="text"
                    placeholder="e.g. Maratha / Kunbi / Mali"
                    class="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-xl"
                  />
                </div>
                <div>
                  <label class="block text-xs font-bold text-slate-700 mb-1">Annual Family Income (₹)</label>
                  <input
                    v-model.number="profileForm.annual_family_income"
                    type="number"
                    step="1000"
                    class="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-xl"
                  />
                </div>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label class="block text-xs font-bold text-slate-700 mb-1">Course Level</label>
                  <select v-model="profileForm.current_course_level" class="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-xl">
                    <option value="11TH_12TH">11th / 12th Junior College</option>
                    <option value="DIPLOMA">Polytechnic Diploma</option>
                    <option value="UNDERGRADUATE">Undergraduate (BA/B.Sc/B.Com)</option>
                    <option value="PROFESSIONAL_DEGREE">Professional Degree (Engineering/Medical)</option>
                    <option value="POSTGRADUATE">Postgraduate</option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-bold text-slate-700 mb-1">Admission Quota</label>
                  <select v-model="profileForm.admission_quota" class="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-xl">
                    <option value="CAP_ROUND">Centralized Admission Process (CAP)</option>
                    <option value="INSTITUTE_QUOTA">Institutional / Management Quota</option>
                    <option value="DIRECT_SECOND_YEAR">Direct Second Year (DSE)</option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-bold text-slate-700 mb-1">Prev. Year Marks (%)</label>
                  <input
                    v-model.number="profileForm.previous_year_percentage"
                    type="number"
                    step="0.1"
                    class="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-xl"
                  />
                </div>
              </div>

              <!-- Toggles: Bank Aadhaar Seeded, Farmer Family -->
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs">
                <label class="flex items-center gap-2 cursor-pointer font-semibold text-slate-700">
                  <input
                    v-model="profileForm.has_aadhaar_seeded_bank"
                    type="checkbox"
                    class="rounded text-amber-600 focus:ring-amber-500"
                  />
                  <span>Bank Account NPCI/DBT Seeded</span>
                </label>
                <label class="flex items-center gap-2 cursor-pointer font-semibold text-slate-700">
                  <input
                    v-model="profileForm.parent_is_farmer"
                    type="checkbox"
                    class="rounded text-amber-600 focus:ring-amber-500"
                  />
                  <span>Farmer / Agricultural Household</span>
                </label>
              </div>

              <div class="flex items-center justify-end gap-2 pt-2">
                <button
                  type="submit"
                  :disabled="isUpdatingProfile || selectedCase.consent?.consent_status !== 'ACTIVE'"
                  class="px-4 py-2 text-xs font-bold bg-amber-600 hover:bg-amber-700 text-white rounded-xl shadow-xs disabled:opacity-50"
                >
                  {{ isUpdatingProfile ? 'Saving & Syncing...' : 'Save Profile & Sync with Engine' }}
                </button>
              </div>
            </form>
          </div>

          <!-- TAB 2: Eligibility Discovery -->
          <div v-if="activeTab === 'eligibility'" class="space-y-4">
            <div class="flex items-center justify-between pb-2 border-b border-slate-100">
              <div>
                <h4 class="text-sm font-bold text-slate-900">Deterministic Welfare Eligibility</h4>
                <p class="text-xs text-slate-500">Evaluates current citizen facts against published Maharashtra schemes.</p>
              </div>
              <button
                @click="handleEvaluateEligibility"
                :disabled="isEvaluatingEligibility || selectedCase.consent?.consent_status !== 'ACTIVE'"
                class="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-xl shadow-xs disabled:opacity-50 flex items-center gap-1.5"
              >
                <Sparkles class="w-3.5 h-3.5" />
                <span>{{ isEvaluatingEligibility ? 'Evaluating...' : 'Discover Eligible Schemes' }}</span>
              </button>
            </div>

            <!-- Results Summary -->
            <div v-if="eligibilityResults" class="space-y-4">
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div class="bg-emerald-50 border border-emerald-200 rounded-xl p-3">
                  <div class="text-[11px] font-bold text-emerald-800">Likely Eligible Schemes</div>
                  <div class="text-2xl font-black text-emerald-900 mt-0.5">
                    {{ eligibilityResults.summary?.likely_eligible ?? 0 }}
                  </div>
                </div>
                <div class="bg-amber-50 border border-amber-200 rounded-xl p-3">
                  <div class="text-[11px] font-bold text-amber-800">Near-Eligible Schemes</div>
                  <div class="text-2xl font-black text-amber-900 mt-0.5">
                    {{ eligibilityResults.summary?.near_eligible ?? 0 }}
                  </div>
                </div>
                <div class="bg-indigo-50 border border-indigo-200 rounded-xl p-3">
                  <div class="text-[11px] font-bold text-indigo-800">Potential Total Benefit</div>
                  <div class="text-2xl font-black text-indigo-900 mt-0.5">
                    ₹{{ (eligibilityResults.summary?.potential_annual_benefit || 0).toLocaleString() }}
                  </div>
                </div>
              </div>

              <!-- Matched Schemes Cards -->
              <div class="space-y-3">
                <div
                  v-for="s in eligibilityResults.results"
                  :key="s.code"
                  class="bg-white border rounded-xl p-4 shadow-xs space-y-2"
                  :class="s.eligibility_status === 'LIKELY_ELIGIBLE' ? 'border-emerald-200 bg-emerald-50/20' : 'border-slate-200'"
                >
                  <div class="flex items-start justify-between gap-2">
                    <div>
                      <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-bold">
                        {{ s.code }}
                      </span>
                      <h5 class="text-sm font-bold text-slate-900 mt-1">{{ s.name }}</h5>
                      <p class="text-xs text-slate-500">{{ s.department }}</p>
                    </div>
                    <span
                      class="text-[10px] font-extrabold uppercase px-2.5 py-1 rounded-full whitespace-nowrap"
                      :class="s.eligibility_status === 'LIKELY_ELIGIBLE' ? 'bg-emerald-100 text-emerald-800 border border-emerald-200' : 'bg-amber-100 text-amber-800 border border-amber-200'"
                    >
                      {{ s.eligibility_status.replace(/_/g, ' ') }}
                    </span>
                  </div>

                  <div class="text-xs text-slate-600 bg-white/80 p-2.5 rounded-lg border border-slate-100">
                    <strong>Estimated Benefit:</strong> {{ s.estimated_benefit_amount || 'Tuition & Exam Fee Waiver' }}
                  </div>

                  <!-- Statutory GR Citation -->
                  <div v-if="s.statutory_gr" class="text-[11px] text-slate-500 font-mono">
                    Statutory GR: <strong>{{ s.statutory_gr }}</strong>
                  </div>
                </div>
              </div>
            </div>

            <div v-else class="text-center py-8 text-slate-400">
              <Sparkles class="w-8 h-8 mx-auto mb-2 text-slate-300" />
              <p class="text-xs">Click "Discover Eligible Schemes" above to evaluate matching benefits.</p>
            </div>
          </div>

          <!-- TAB 3: Preflight Audit & Document Checklist -->
          <div v-if="activeTab === 'preflight'" class="space-y-6">
            <!-- 6-Point Preflight Scrutiny Review Box -->
            <div class="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-3">
              <div class="flex items-center justify-between flex-wrap gap-2">
                <div>
                  <h4 class="text-sm font-bold text-slate-900">Application Preflight Scrutiny Audit</h4>
                  <p class="text-xs text-slate-500">
                    Simulates government scrutiny clerk checks to catch document mismatches before portal submission.
                  </p>
                </div>
                <div class="flex items-center gap-2">
                  <select
                    v-model="selectedPreflightScheme"
                    @change="fetchDocuments"
                    class="text-xs bg-white border border-slate-300 rounded-xl px-2.5 py-1 text-slate-800 font-semibold"
                  >
                    <option value="MH_DTE_EBC_2024">EBC Tuition Fee Waiver (DTE)</option>
                    <option value="MH_SJW_GOI_POSTMATRIC_SC">SC Post-Matric Scholarship</option>
                    <option value="MH_OBC_POSTMATRIC_TUITION">OBC Post-Matric Scholarship</option>
                  </select>
                  <button
                    @click="handleRunPreflight"
                    :disabled="isRunningPreflight || selectedCase.consent?.consent_status !== 'ACTIVE'"
                    class="px-3 py-1 bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold rounded-xl shadow-xs disabled:opacity-50"
                  >
                    {{ isRunningPreflight ? 'Auditing...' : 'Run Audit' }}
                  </button>
                </div>
              </div>

              <!-- Preflight Score & Findings -->
              <div v-if="preflightResult" class="space-y-3 pt-2">
                <div class="flex items-center gap-4 bg-white p-3 rounded-xl border border-slate-200">
                  <div class="text-center">
                    <div class="text-2xl font-black text-amber-600">
                      {{ preflightResult.readiness_score_pct }}%
                    </div>
                    <div class="text-[10px] uppercase font-bold text-slate-400">Readiness Score</div>
                  </div>
                  <div class="border-l border-slate-200 pl-4">
                    <div class="text-xs font-bold text-slate-800">
                      Audit Status:
                      <span
                        class="px-2 py-0.5 rounded text-[10px] font-extrabold uppercase ml-1"
                        :class="preflightResult.status === 'READY' ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'"
                      >
                        {{ preflightResult.status }}
                      </span>
                    </div>
                    <p class="text-[11px] text-slate-500 mt-0.5">
                      {{ preflightResult.blockers?.length || 0 }} Fatal Blockers •
                      {{ preflightResult.warnings?.length || 0 }} Scrutiny Warnings •
                      {{ preflightResult.cleared_checks?.length || 0 }} Cleared
                    </p>
                  </div>
                </div>

                <!-- Fatal Blockers -->
                <div v-if="preflightResult.blockers?.length" class="space-y-2">
                  <h5 class="text-xs font-bold text-red-800 uppercase tracking-wider">Fatal Rejection Blockers</h5>
                  <div
                    v-for="(b, idx) in preflightResult.blockers"
                    :key="idx"
                    class="bg-red-50 border border-red-200 rounded-xl p-3 text-xs space-y-1"
                  >
                    <div class="font-bold text-red-900 flex items-center gap-1.5">
                      <AlertCircle class="w-4 h-4 text-red-600 shrink-0" />
                      <span>{{ b.title }}</span>
                    </div>
                    <p class="text-red-700 text-[11px]">{{ b.description }}</p>
                    <p class="text-red-900 text-[11px] font-semibold">Route: {{ b.fix_route }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Tailored Document Procurement Checklist -->
            <div class="space-y-3">
              <div class="flex items-center justify-between pb-2 border-b border-slate-100">
                <div>
                  <h4 class="text-sm font-bold text-slate-900">Tailored Document Procurement Checklist</h4>
                  <p class="text-xs text-slate-500">Statutory SLA, issuing authority and procurement status.</p>
                </div>
                <button
                  @click="handleSaveDocuments"
                  :disabled="isSavingDocuments || selectedCase.consent?.consent_status !== 'ACTIVE'"
                  class="px-3 py-1 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow-xs disabled:opacity-50"
                >
                  {{ isSavingDocuments ? 'Saving...' : 'Save Checklist' }}
                </button>
              </div>

              <div class="space-y-2">
                <div
                  v-for="doc in documentChecklist"
                  :key="doc.code"
                  class="bg-white border border-slate-200 rounded-xl p-3 flex items-start gap-3 hover:border-amber-300 transition-colors"
                >
                  <button
                    type="button"
                    @click="toggleDocumentCheck(doc.code)"
                    class="mt-0.5 text-amber-600 hover:text-amber-700"
                  >
                    <CheckSquare v-if="checkedDocCodes.includes(doc.code)" class="w-5 h-5 text-emerald-600" />
                    <Square v-else class="w-5 h-5 text-slate-300" />
                  </button>
                  <div class="flex-1">
                    <div class="flex items-center justify-between">
                      <span class="text-xs font-bold text-slate-900">{{ doc.name }}</span>
                      <span class="text-[10px] text-slate-500 font-mono">SLA: {{ doc.sla_days }} Days</span>
                    </div>
                    <div class="text-[11px] text-slate-500 mt-0.5">
                      Authority: <strong class="text-slate-700">{{ doc.issuing_authority }}</strong> •
                      Portal: <strong class="text-slate-700">{{ doc.procurement_portal }}</strong>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- TAB 4: Case Notes & Escalation -->
          <div v-if="activeTab === 'notes'" class="space-y-6">
            <!-- Add New Note -->
            <div class="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-3">
              <h4 class="text-xs font-bold text-slate-800 uppercase tracking-wider">Record Counselor Note</h4>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <select v-model="newNoteType" class="text-xs bg-white border border-slate-200 rounded-xl px-2.5 py-1.5 font-semibold">
                  <option value="GENERAL_NOTE">General Note</option>
                  <option value="DOCUMENT_FOLLOWUP">Document Procurement Follow-up</option>
                  <option value="CITIZEN_QUERY">Citizen Query / Question</option>
                  <option value="SUPERVISOR_REMARK">Supervisor Remark</option>
                </select>
                <label class="flex items-center gap-2 text-xs font-semibold text-slate-700 cursor-pointer">
                  <input v-model="isNotePinned" type="checkbox" class="rounded text-amber-600" />
                  <span>Pin this note to top</span>
                </label>
              </div>
              <textarea
                v-model="newNoteContent"
                rows="2"
                placeholder="Enter counseling remarks, pending certificates or citizen commitments..."
                class="w-full px-3 py-1.5 text-xs bg-white border border-slate-200 rounded-xl focus:outline-hidden"
              ></textarea>
              <div class="flex justify-end">
                <button
                  @click="handleAddNote"
                  :disabled="isSubmittingNote || !newNoteContent.trim()"
                  class="px-3 py-1.5 bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold rounded-xl shadow-xs disabled:opacity-50"
                >
                  {{ isSubmittingNote ? 'Saving...' : 'Add Case Note' }}
                </button>
              </div>
            </div>

            <!-- Escalation to Supervisor Box -->
            <div class="bg-purple-50/60 border border-purple-200 rounded-xl p-4 space-y-3">
              <div class="flex items-center gap-2 text-purple-900 font-bold text-xs">
                <AlertTriangle class="w-4 h-4 text-purple-600" />
                <span>Escalate Case to Center Supervisor (VLE Lead)</span>
              </div>
              <p class="text-xs text-purple-800">
                Use when income borderline disputes, non-standard quota certificates or Right to Services (RTS) appeals require lead intervention.
              </p>
              <div v-if="selectedCase.escalated_to_supervisor" class="p-2.5 bg-white border border-purple-200 rounded-xl text-xs text-purple-900 font-semibold">
                Case currently escalated: "{{ selectedCase.escalation_reason }}"
              </div>
              <div v-else class="space-y-2">
                <input
                  v-model="escalationReason"
                  type="text"
                  placeholder="Reason for supervisor review (e.g. Income border case exceeds limit by ₹5k)..."
                  class="w-full px-3 py-1.5 text-xs bg-white border border-purple-300 rounded-xl text-purple-950 focus:outline-hidden"
                />
                <button
                  @click="handleEscalateCase"
                  :disabled="isEscalating"
                  class="px-3 py-1.5 bg-purple-600 hover:bg-purple-700 text-white text-xs font-bold rounded-xl shadow-xs disabled:opacity-50"
                >
                  {{ isEscalating ? 'Escalating...' : 'Escalate to Supervisor' }}
                </button>
              </div>
            </div>

            <!-- Notes Timeline -->
            <div class="space-y-3">
              <h5 class="text-xs font-bold text-slate-700 uppercase tracking-wider">Case History Timeline</h5>
              <div v-if="!selectedCase.notes?.length" class="text-xs text-slate-400 py-4 text-center">
                No notes logged yet.
              </div>
              <div
                v-for="note in selectedCase.notes"
                :key="note.id"
                class="bg-white border rounded-xl p-3 space-y-1 shadow-xs"
                :class="note.is_pinned ? 'border-amber-300 bg-amber-50/30' : 'border-slate-200'"
              >
                <div class="flex items-center justify-between text-[11px]">
                  <span class="font-bold text-slate-800">
                    {{ note.counselor_name }} ({{ note.counselor_role }})
                  </span>
                  <span class="text-slate-400 font-mono">{{ new Date(note.created_at).toLocaleString() }}</span>
                </div>
                <p class="text-xs text-slate-700 leading-relaxed">{{ note.content }}</p>
              </div>
            </div>
          </div>

          <!-- TAB 5: Handover & Case Closure -->
          <div v-if="activeTab === 'handover'" class="space-y-4">
            <div class="pb-2 border-b border-slate-100">
              <h4 class="text-sm font-bold text-slate-900">Case Closure & Handover Protocol</h4>
              <p class="text-xs text-slate-500">Record printed documents and guidance handed over to citizen.</p>
            </div>

            <div v-if="selectedCase.case_status === 'CLOSED_HANDOVER'" class="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
              <div class="flex items-center gap-2 text-emerald-700 font-bold text-xs">
                <CheckCircle2 class="w-4 h-4 text-emerald-600" />
                <span>Case Closed & Handed Over</span>
              </div>
              <p class="text-xs text-slate-600"><strong>Summary:</strong> {{ selectedCase.closure_summary }}</p>
              <div class="text-[11px] text-slate-400">Closed At: {{ new Date(selectedCase.closed_at).toLocaleString() }}</div>
            </div>

            <div v-else class="space-y-3">
              <textarea
                v-model="closureSummary"
                rows="3"
                placeholder="e.g. Handed over printed document checklist, guided student to MahaDBT portal login with Aaple Sarkar token..."
                class="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-hidden"
              ></textarea>
              <button
                @click="handleCloseCase"
                :disabled="isClosing"
                class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow-xs disabled:opacity-50"
              >
                {{ isClosing ? 'Closing Case...' : 'Complete Handover & Close Case' }}
              </button>
            </div>
          </div>

          <!-- TAB 6: Consent & Tamper-Evident Audit Trail -->
          <div v-if="activeTab === 'audit'" class="space-y-6">
            <!-- Active Consent Record -->
            <div class="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-3">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <ShieldCheck class="w-5 h-5 text-emerald-600" />
                  <h4 class="text-sm font-bold text-slate-900">Recorded Citizen Consent</h4>
                </div>
                <button
                  v-if="selectedCase.consent?.consent_status === 'ACTIVE'"
                  @click="handleWithdrawConsent"
                  :disabled="isWithdrawing"
                  class="px-3 py-1 bg-red-50 hover:bg-red-100 text-red-700 border border-red-200 text-xs font-bold rounded-xl"
                >
                  {{ isWithdrawing ? 'Withdrawing...' : 'Withdraw Consent' }}
                </button>
              </div>

              <div class="text-xs text-slate-600 space-y-1">
                <div>Status: <strong class="text-slate-800">{{ selectedCase.consent?.consent_status }}</strong></div>
                <div>Method: <strong class="text-slate-800">{{ selectedCase.consent?.consent_method }}</strong></div>
                <div>Attesting Counselor: <strong class="text-slate-800">{{ selectedCase.consent?.attesting_counselor_name }}</strong></div>
                <div>Granted: <span class="font-mono">{{ new Date(selectedCase.consent?.granted_at).toLocaleString() }}</span></div>
                <p class="text-[11px] text-slate-500 mt-2 bg-white p-2.5 rounded-lg border border-slate-200">
                  {{ selectedCase.consent?.scope_description }}
                </p>
              </div>
            </div>

            <!-- Tamper-Evident Audit Trail Table -->
            <div class="space-y-2">
              <h5 class="text-xs font-bold text-slate-700 uppercase tracking-wider">Tamper-Evident Access Audit Trail</h5>
              <div class="overflow-x-auto border border-slate-200 rounded-xl">
                <table class="w-full text-left text-xs">
                  <thead class="bg-slate-50 text-slate-500 text-[10px] uppercase font-bold border-b border-slate-200">
                    <tr>
                      <th class="py-2 px-3">Timestamp</th>
                      <th class="py-2 px-3">Operator</th>
                      <th class="py-2 px-3">Action</th>
                      <th class="py-2 px-3">Details</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-slate-100">
                    <tr v-for="log in selectedCase.audit_logs" :key="log.id" class="hover:bg-slate-50">
                      <td class="py-2 px-3 font-mono text-[11px] text-slate-500 whitespace-nowrap">
                        {{ new Date(log.timestamp).toLocaleTimeString() }}
                      </td>
                      <td class="py-2 px-3 font-semibold text-slate-800">{{ log.counselor_name }}</td>
                      <td class="py-2 px-3">
                        <span
                          class="px-2 py-0.5 rounded text-[10px] font-bold"
                          :class="log.action === 'UNAUTHORIZED_ACCESS_BLOCKED' ? 'bg-red-100 text-red-800' : 'bg-slate-100 text-slate-700'"
                        >
                          {{ log.action }}
                        </span>
                      </td>
                      <td class="py-2 px-3 text-[11px] text-slate-500 font-mono">
                        {{ JSON.stringify(log.details) }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>

  </div>
</template>
