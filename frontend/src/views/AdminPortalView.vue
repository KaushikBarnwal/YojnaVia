<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useStudentStore } from '../stores/studentStore';
import { 
  ShieldCheck, 
  Lock, 
  LogOut, 
  Plus, 
  Edit, 
  Sliders, 
  History, 
  RefreshCw, 
  CheckCircle2, 
  AlertTriangle, 
  Scale, 
  Search, 
  X, 
  Save, 
  Building,
  UserCheck
} from '@lucide/vue';
import type { SchemeRuleVersion } from '../types';

const store = useStudentStore();

// Login state
const loginUsername = ref('');
const loginPassword = ref('');
const loginError = ref('');

// Filter & search
const searchQuery = ref('');
const statusFilter = ref<'ALL' | 'ACTIVE' | 'INACTIVE'>('ALL');
const verificationFilter = ref<'ALL' | 'VERIFIED' | 'UNVERIFIED' | 'NEEDS_REVIEW'>('ALL');

// Modals
const isCreateModalOpen = ref(false);
const isEditModalOpen = ref(false);
const isRuleModalOpen = ref(false);
const isHistoryModalOpen = ref(false);
const isReRunModalOpen = ref(false);

const selectedScheme = ref<any>(null);
const schemeHistory = ref<SchemeRuleVersion[]>([]);
const reRunResults = ref<any>(null);

// Form states
const schemeForm = ref({
  code: '',
  name: '',
  name_marathi: '',
  department: 'Higher & Technical Education Department',
  category: 'EDUCATION',
  jurisdiction: 'STATE',
  state: 'Maharashtra',
  statutory_gr: '',
  official_portal_url: 'https://mahadbt.maharashtra.gov.in',
  official_source_url: '',
  portal_name: 'MahaDBT',
  benefit_type: 'TUITION_FEE_WAIVER',
  benefit_amount_text: '100% Tuition Fee Waiver',
  estimated_annual_value: 60000,
  brief_description: '',
  verification_status: 'UNVERIFIED',
  last_verified_on: '',
  is_sample: false,
  is_active: true,
  change_summary: ''
});

// Structured Rule Form State
const ruleForm = ref<{
  operator: 'ALL' | 'ANY';
  conditions: Array<{
    field: string;
    op: string;
    value: any;
    label: string;
    citation: string;
    boundary_tolerance: number;
  }>;
  change_summary: string;
}>({
  operator: 'ALL',
  conditions: [],
  change_summary: ''
});

const availableFields = [
  { key: 'annual_family_income', label: 'Annual family income (₹)', defaultOp: '<=', defaultVal: 150000 },
  { key: 'caste_category', label: 'Caste Category (OPEN, OBC, SC, ST, VJNT)', defaultOp: 'in', defaultVal: ['OBC', 'SC', 'ST'] },
  { key: 'is_maharashtra_domicile', label: 'Lives in Maharashtra (yes/no)', defaultOp: '==', defaultVal: true },
  { key: 'age', label: 'Student age (years)', defaultOp: '<=', defaultVal: 25 },
  { key: 'current_course_level', label: 'Course Level', defaultOp: 'in', defaultVal: ['UNDERGRADUATE', 'PROFESSIONAL_DEGREE'] },
  { key: 'admission_quota', label: 'Admission Quota', defaultOp: '==', defaultVal: 'CAP_ROUND' },
  { key: 'accommodation_type', label: 'Accommodation Type', defaultOp: '==', defaultVal: 'PRIVATE_RENTAL_PG' },
  { key: 'parent_is_farmer', label: 'Parents are Farmers', defaultOp: '==', defaultVal: true },
  { key: 'parent_land_acres', label: 'Farm land owned (acres)', defaultOp: '<=', defaultVal: 5 },
  { key: 'previous_year_percentage', label: 'Marks in last year (%)', defaultOp: '>=', defaultVal: 60 }
];

onMounted(async () => {
  if (store.adminUser) {
    await store.fetchAdminSchemes();
  }
});

async function handleLogin() {
  loginError.value = '';
  try {
    await store.adminLogin(loginUsername.value, loginPassword.value);
  } catch (err: any) {
    loginError.value = err.response?.data?.error || 'Wrong username or password. Please try again.';
  }
}

async function handleDemoLogin(role: 'SCHEME_OFFICER' | 'SUPERADMIN') {
  loginError.value = '';
  try {
    await store.adminLogin(undefined, undefined, role);
  } catch (err: any) {
    loginError.value = 'Something went wrong. Please try again in a few minutes.';
  }
}

function handleLogout() {
  store.adminLogout();
}

// Filtered schemes computed
const filteredAdminSchemes = computed(() => {
  return store.adminSchemes.filter(s => {
    if (statusFilter.value === 'ACTIVE' && !s.is_active) return false;
    if (statusFilter.value === 'INACTIVE' && s.is_active) return false;
    if (verificationFilter.value !== 'ALL' && s.verification_status !== verificationFilter.value) return false;
    if (searchQuery.value) {
      const q = searchQuery.value.toLowerCase();
      const match = s.name.toLowerCase().includes(q) || s.code.toLowerCase().includes(q) || s.department.toLowerCase().includes(q);
      if (!match) return false;
    }
    return true;
  });
});

const verifiedCount = computed(() => store.adminSchemes.filter(s => s.verification_status === 'VERIFIED').length);
const activeCount = computed(() => store.adminSchemes.filter(s => s.is_active).length);

function openCreateModal() {
  schemeForm.value = {
    code: `MHT-NEW-${Math.floor(1000 + Math.random() * 9000)}`,
    name: '',
    name_marathi: '',
    department: 'Directorate of Higher Education, Maharashtra',
    category: 'EDUCATION',
    jurisdiction: 'STATE',
    state: 'Maharashtra',
    statutory_gr: 'Govt Resolution No. ED-2024/CR-',
    official_portal_url: 'https://mahadbt.maharashtra.gov.in',
    official_source_url: '',
    portal_name: 'MahaDBT',
    benefit_type: 'TUITION_FEE_WAIVER',
    benefit_amount_text: '100% Tuition Fee Waiver',
    estimated_annual_value: 50000,
    brief_description: '',
    verification_status: 'UNVERIFIED',
    last_verified_on: '',
    is_sample: false,
    is_active: true,
    change_summary: 'Initial scheme registration'
  };
  isCreateModalOpen.value = true;
}

async function handleCreateScheme() {
  try {
    await store.createAdminScheme(schemeForm.value);
    isCreateModalOpen.value = false;
  } catch (err: any) {
    alert('Something went wrong. Please try again in a few minutes.');
  }
}

function openEditModal(scheme: any) {
  selectedScheme.value = scheme;
  schemeForm.value = {
    code: scheme.code,
    name: scheme.name,
    name_marathi: scheme.name_marathi || '',
    department: scheme.department,
    category: scheme.category || 'EDUCATION',
    jurisdiction: scheme.jurisdiction || 'STATE',
    state: scheme.state || 'Maharashtra',
    statutory_gr: scheme.statutory_gr,
    official_portal_url: scheme.official_portal_url,
    official_source_url: scheme.official_source_url || '',
    portal_name: scheme.portal_name,
    benefit_type: scheme.benefit_type,
    benefit_amount_text: scheme.benefit_amount_text,
    estimated_annual_value: scheme.estimated_annual_value,
    brief_description: scheme.brief_description,
    verification_status: scheme.verification_status || 'UNVERIFIED',
    last_verified_on: scheme.last_verified_on || '',
    is_sample: scheme.is_sample || false,
    is_active: scheme.is_active,
    change_summary: 'Updated scheme details and verification status'
  };
  isEditModalOpen.value = true;
}

async function handleUpdateScheme() {
  if (!selectedScheme.value) return;
  try {
    await store.updateAdminScheme(selectedScheme.value.code, schemeForm.value);
    isEditModalOpen.value = false;
  } catch (err: any) {
    alert('Something went wrong. Please try again in a few minutes.');
  }
}

function openRuleEditor(scheme: any) {
  selectedScheme.value = scheme;
  const currentRules = scheme.rules || {};
  ruleForm.value = {
    operator: currentRules.operator || 'ALL',
    conditions: (currentRules.conditions || []).map((c: any) => ({
      field: c.field,
      op: c.op,
      value: Array.isArray(c.value) ? c.value.join(', ') : c.value,
      label: c.label || c.field,
      citation: c.citation || scheme.statutory_gr,
      boundary_tolerance: c.boundary_tolerance || 0
    })),
    change_summary: ''
  };
  isRuleModalOpen.value = true;
}

function addCondition() {
  ruleForm.value.conditions.push({
    field: 'annual_family_income',
    op: '<=',
    value: 150000,
    label: 'Annual Family Income <= ₹1.5L',
    citation: selectedScheme.value?.statutory_gr || 'Govt Resolution Para 4.1',
    boundary_tolerance: 15000
  });
}

function removeCondition(idx: number) {
  ruleForm.value.conditions.splice(idx, 1);
}

async function handleSaveRules() {
  if (!selectedScheme.value) return;
  if (!ruleForm.value.change_summary.trim()) {
    alert("Please explain why you are changing this rule.");
    return;
  }

  // Parse conditions
  const parsedConditions = ruleForm.value.conditions.map(c => {
    let val = c.value;
    if (c.op === 'in' || c.op === 'not_in') {
      if (typeof val === 'string') {
        val = val.split(',').map(s => s.trim().toUpperCase());
      }
    } else if (c.op === '<=' || c.op === '>=' || c.op === '<' || c.op === '>') {
      val = Number(val);
    } else if (val === 'true' || val === true) {
      val = true;
    } else if (val === 'false' || val === false) {
      val = false;
    }

    return {
      field: c.field,
      op: c.op,
      value: val,
      label: c.label,
      citation: c.citation,
      boundary_tolerance: Number(c.boundary_tolerance) || 0
    };
  });

  const newRules = {
    operator: ruleForm.value.operator,
    conditions: parsedConditions
  };

  try {
    const res = await store.updateAdminSchemeRules(
      selectedScheme.value.code,
      newRules,
      ruleForm.value.change_summary
    );
    alert(`Success: ${res.message}`);
    isRuleModalOpen.value = false;
  } catch (err: any) {
    alert('Something went wrong. Please try again in a few minutes.');
  }
}

async function openHistory(scheme: any) {
  selectedScheme.value = scheme;
  schemeHistory.value = await store.fetchSchemeHistory(scheme.code);
  isHistoryModalOpen.value = true;
}

async function triggerReRun(scheme: any) {
  selectedScheme.value = scheme;
  try {
    reRunResults.value = await store.reRunSchemeMatching(scheme.code);
    isReRunModalOpen.value = true;
  } catch (err: any) {
    alert("Could not check students again. Please try again in a few minutes.");
  }
}

async function toggleActive(code: string) {
  await store.toggleAdminSchemeStatus(code);
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
    
    <!-- AUTHENTICATION SCREEN IF NOT LOGGED IN (Requirement 1) -->
    <div v-if="!store.adminUser" class="max-w-md mx-auto my-12 bg-[#FBFBFA] rounded-xl border-[2px] border-[#0B132B] shadow-[4px_4px_0_0_#0B132B] p-8 space-y-6">
      <div class="text-center space-y-2">
        <div class="w-14 h-14 rounded-lg bg-[#0B132B] text-white flex items-center justify-center mx-auto border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#D97706]">
          <ShieldCheck class="w-8 h-8 text-[#F59E0B]" />
        </div>
        <h1 class="text-2xl font-black text-[#0B132B] tracking-tight">Admin & Officer Portal</h1>
        <p class="text-xs text-[#64748B] font-medium">Manage government scholarships and the rules that decide who gets them</p>
      </div>

      <!-- Quick 1-Click Demo Login for Judges -->
      <div class="p-4 rounded-lg bg-[#FEF3C7] border-[1.5px] border-[#D97706] shadow-[2px_2px_0_0_#D97706] space-y-3">
        <div class="flex items-center gap-2 text-[#92400E] font-black text-xs uppercase tracking-wider">
          <Lock class="w-3.5 h-3.5" />
          <span>Demo login (one click)</span>
        </div>
        <div class="grid grid-cols-2 gap-2">
          <button
            @click="handleDemoLogin('SCHEME_OFFICER')"
            class="p-2.5 bg-white hover:bg-[#F8FAFC] text-[#0B132B] font-black text-xs rounded-lg border-[1.5px] border-[#0B132B] shadow-[1.5px_1.5px_0_0_#0B132B] flex flex-col items-center gap-1 transition-all cursor-pointer"
          >
            <UserCheck class="w-4 h-4 text-[#D97706]" />
            <span>Scheme Officer</span>
            <span class="text-[10px] text-[#64748B] font-normal">MahaDBT Desk</span>
          </button>

          <button
            @click="handleDemoLogin('SUPERADMIN')"
            class="p-2.5 bg-white hover:bg-[#F8FAFC] text-[#0B132B] font-black text-xs rounded-lg border-[1.5px] border-[#0B132B] shadow-[1.5px_1.5px_0_0_#0B132B] flex flex-col items-center gap-1 transition-all cursor-pointer"
          >
            <Building class="w-4 h-4 text-[#7C3AED]" />
            <span>Superadmin</span>
            <span class="text-[10px] text-[#64748B] font-normal">Principal Secretary</span>
          </button>
        </div>
      </div>

      <!-- Standard Manual Form -->
      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-xs font-black text-[#0B132B] uppercase tracking-wider mb-1">Username</label>
          <input
            v-model="loginUsername"
            type="text"
            placeholder="officer or admin"
            class="w-full text-xs font-bold border-[1.5px] border-[#0B132B] rounded-lg px-3.5 py-2.5 bg-white text-[#0B132B] focus:outline-hidden shadow-[1.5px_1.5px_0_0_#0B132B]"
            required
          />
        </div>

        <div>
          <label class="block text-xs font-black text-[#0B132B] uppercase tracking-wider mb-1">Password</label>
          <input
            v-model="loginPassword"
            type="password"
            placeholder="officer123 or admin123"
            class="w-full text-xs font-bold border-[1.5px] border-[#0B132B] rounded-lg px-3.5 py-2.5 bg-white text-[#0B132B] focus:outline-hidden shadow-[1.5px_1.5px_0_0_#0B132B]"
            required
          />
        </div>

        <div v-if="loginError" class="text-xs text-[#991B1B] font-black bg-[#FEF2F2] p-2.5 rounded-lg border border-[#DC2626]">
          {{ loginError }}
        </div>

        <button
          type="submit"
          :disabled="store.isLoading"
          class="w-full py-3 bg-[#0B132B] hover:bg-[#1C2541] text-white font-black rounded-lg text-xs uppercase tracking-wider transition-colors border-[1.5px] border-[#0B132B] shadow-[2.5px_2.5px_0_0_#D97706] flex items-center justify-center gap-2 cursor-pointer"
        >
          <Lock class="w-4 h-4 text-[#F59E0B]" />
          <span>Sign In to Admin Panel</span>
        </button>
      </form>
    </div>

    <!-- MAIN ADMIN PANEL (When Logged In) -->
    <div v-else class="space-y-6">
      
      <!-- Top Officer Header Bar -->
      <div class="bg-[#0B132B] rounded-xl p-6 text-white shadow-[3.5px_3.5px_0_0_#D97706] border-[1.5px] border-[#0B132B] flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div class="space-y-1">
          <div class="flex items-center gap-2">
            <span class="px-2.5 py-0.5 rounded-sm text-xs font-mono font-black uppercase tracking-wider bg-[#1C2541] text-[#FBBF24] border border-[#F59E0B]">
              {{ store.adminUser.role }}
            </span>
            <span class="text-xs text-[#34D399] font-black flex items-center gap-1">
              <span class="w-2 h-2 rounded-full bg-[#34D399] animate-pulse"></span>
              Signed in
            </span>
          </div>
          <h1 class="text-2xl font-black tracking-tight text-white">
            {{ store.adminUser.name }}
          </h1>
          <p class="text-xs text-slate-300">{{ store.adminUser.department }}</p>
        </div>

        <div class="flex items-center gap-3">
          <button
            @click="openCreateModal"
            class="px-4 py-2.5 bg-[#D97706] hover:bg-[#B45309] text-white font-black text-xs rounded-lg border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#000] flex items-center gap-1.5 transition-transform active:scale-95 cursor-pointer"
          >
            <Plus class="w-4 h-4" />
            <span>Add a new scheme</span>
          </button>

          <button
            @click="handleLogout"
            class="px-3.5 py-2.5 bg-[#1C2541] hover:bg-[#253256] text-white text-xs font-bold rounded-lg border border-slate-700 flex items-center gap-1.5 transition-colors cursor-pointer"
          >
            <LogOut class="w-4 h-4 text-[#F87171]" />
            <span>Sign Out</span>
          </button>
        </div>
      </div>

      <!-- Stats Counters -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div class="bg-[#FBFBFA] rounded-xl p-4 border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#0B132B]">
          <span class="text-xs font-black text-[#64748B] block uppercase tracking-wider">Total schemes</span>
          <span class="text-2xl font-black text-[#0B132B] mt-1 block font-mono">{{ store.adminSchemes.length }}</span>
        </div>

        <div class="bg-[#FBFBFA] rounded-xl p-4 border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#0B132B]">
          <span class="text-xs font-black text-[#64748B] block uppercase tracking-wider">Open to students now</span>
          <span class="text-2xl font-black text-[#059669] mt-1 block font-mono">{{ activeCount }}</span>
        </div>

        <div class="bg-[#FBFBFA] rounded-xl p-4 border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#0B132B]">
          <span class="text-xs font-black text-[#64748B] block uppercase tracking-wider">Officially checked</span>
          <span class="text-2xl font-black text-[#0B132B] mt-1 block font-mono">{{ verifiedCount }}</span>
        </div>

        <div class="bg-[#FBFBFA] rounded-xl p-4 border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#0B132B]">
          <span class="text-xs font-black text-[#64748B] block uppercase tracking-wider">Student applications</span>
          <span class="text-2xl font-black text-[#D97706] mt-1 block font-mono">{{ store.trackedApplications.length }}</span>
        </div>
      </div>

      <!-- Search & Filters Toolbar -->
      <div class="bg-[#FBFBFA] rounded-xl p-4 border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#0B132B] flex flex-col md:flex-row items-center justify-between gap-3">
        <div class="relative w-full md:w-80">
          <Search class="w-4 h-4 text-[#64748B] absolute left-3.5 top-3" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search by scheme name, code or department..."
            class="w-full pl-9 pr-3.5 py-2 text-xs font-bold border-[1.5px] border-[#0B132B] rounded-lg bg-white text-[#0B132B] focus:outline-hidden"
          />
        </div>

        <div class="flex flex-wrap items-center gap-2 w-full md:w-auto">
          <select
            v-model="statusFilter"
            class="text-xs border-[1.5px] border-[#0B132B] rounded-lg px-3 py-2 bg-white text-[#0B132B] font-bold"
          >
            <option value="ALL">All Statuses</option>
            <option value="ACTIVE">Only active</option>
            <option value="INACTIVE">Only inactive</option>
          </select>

          <select
            v-model="verificationFilter"
            class="text-xs border-[1.5px] border-[#0B132B] rounded-lg px-3 py-2 bg-white text-[#0B132B] font-bold"
          >
            <option value="ALL">All checks</option>
            <option value="VERIFIED">Officially checked only</option>
            <option value="UNVERIFIED">Not checked yet</option>
            <option value="NEEDS_REVIEW">Needs Review</option>
          </select>

          <button
            @click="store.fetchAdminSchemes()"
            class="p-2 border-[1.5px] border-[#0B132B] rounded-lg text-[#0B132B] bg-white hover:bg-slate-50 cursor-pointer shadow-[1.5px_1.5px_0_0_#0B132B]"
            title="Refresh"
          >
            <RefreshCw class="w-4 h-4" />
          </button>
        </div>
      </div>

      <!-- Schemes Management Table (Requirements 2, 3, 5, 6, 7, 8) -->
      <div class="bg-white rounded-xl border-[1.5px] border-[#0B132B] shadow-[2.5px_2.5px_0_0_#0B132B] overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs bg-white">
            <thead class="bg-[#F1F5F9] border-b-[1.5px] border-[#0B132B] text-[#0B132B] font-black uppercase tracking-wider text-[11px]">
              <tr>
                <th class="py-3.5 px-4">Scheme name and code</th>
                <th class="py-3.5 px-4">Department and order</th>
                <th class="py-3.5 px-4">Benefit</th>
                <th class="py-3.5 px-4">Checked</th>
                <th class="py-3.5 px-4">Version</th>
                <th class="py-3.5 px-4">Status</th>
                <th class="py-3.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[#E2E8F0]">
              <tr 
                v-for="s in filteredAdminSchemes" 
                :key="s.code"
                class="hover:bg-[#F8FAFC] transition-colors"
              >
                <!-- Code & Name -->
                <td class="py-3.5 px-4">
                  <div class="font-mono font-black text-[#0B132B]">{{ s.code }}</div>
                  <div class="font-bold text-[#0B132B] mt-0.5 line-clamp-1">{{ s.name }}</div>
                  <div v-if="s.name_marathi" class="text-[11px] text-[#64748B] line-clamp-1 font-medium">{{ s.name_marathi }}</div>
                </td>

                <!-- Department & GR -->
                <td class="py-3.5 px-4">
                  <div class="text-[#334155] font-bold line-clamp-1">{{ s.department }}</div>
                  <div class="text-[11px] text-[#64748B] font-mono mt-0.5 flex items-center gap-1">
                    <Scale class="w-3 h-3 text-[#64748B]" />
                    <span>{{ s.statutory_gr }}</span>
                  </div>
                </td>

                <!-- Benefit -->
                <td class="py-3.5 px-4">
                  <div class="font-black text-[#059669] font-mono">{{ s.benefit_amount_text }}</div>
                  <div class="text-[11px] text-[#64748B] font-mono">₹{{ Number(s.estimated_annual_value || 0).toLocaleString('en-IN') }}/yr</div>
                </td>

                <!-- Verification (Requirement 7) -->
                <td class="py-3.5 px-4">
                  <span
                    class="px-2 py-0.5 rounded-sm font-black uppercase text-[10px] inline-flex items-center gap-1 border border-[#0B132B]"
                    :class="s.verification_status === 'VERIFIED'
                      ? 'bg-[#D1FAE5] text-[#065F46]'
                      : (s.verification_status === 'NEEDS_REVIEW' ? 'bg-[#FEF3C7] text-[#92400E]' : 'bg-[#F1F5F9] text-[#475569]')"
                  >
                    <CheckCircle2 v-if="s.verification_status === 'VERIFIED'" class="w-3 h-3 text-[#059669]" />
                    <AlertTriangle v-else class="w-3 h-3 text-[#D97706]" />
                    {{ s.verification_status || 'UNVERIFIED' }}
                  </span>
                  <div v-if="s.last_verified_on" class="text-[10px] text-[#64748B] font-mono mt-1">
                    {{ s.last_verified_on }}
                  </div>
                </td>

                <!-- Rule Version (Rule Change Handling 1) -->
                <td class="py-3.5 px-4">
                  <span class="font-mono bg-[#F1F5F9] text-[#0B132B] px-2 py-0.5 rounded-sm text-[11px] font-bold border border-[#CBD5E1]">
                    v{{ s.version }}
                  </span>
                  <div class="text-[10px] text-[#64748B] font-mono mt-0.5">
                    {{ (s.rules?.conditions || []).length }} rules
                  </div>
                </td>

                <!-- Active Toggle (Requirement 2) -->
                <td class="py-3.5 px-4">
                  <button
                    @click="toggleActive(s.code)"
                    class="px-2.5 py-1 rounded-sm text-[11px] font-black transition-colors flex items-center gap-1 border border-[#0B132B] cursor-pointer"
                    :class="s.is_active
                      ? 'bg-[#D1FAE5] text-[#065F46] hover:bg-[#A7F3D0]'
                      : 'bg-[#FEE2E2] text-[#991B1B] hover:bg-[#FECACA]'"
                  >
                    <span class="w-1.5 h-1.5 rounded-full" :class="s.is_active ? 'bg-[#059669]' : 'bg-[#DC2626]'"></span>
                    <span>{{ s.is_active ? 'Active' : 'Inactive' }}</span>
                  </button>
                </td>

                <!-- Actions -->
                <td class="py-3.5 px-4 text-right">
                  <div class="flex items-center justify-end gap-1.5">
                    <!-- Edit Rules AST -->
                    <button
                      @click="openRuleEditor(s)"
                      class="p-1.5 rounded-lg bg-white hover:bg-slate-100 text-[#0B132B] border-[1.5px] border-[#0B132B] shadow-[1px_1px_0_0_#0B132B] cursor-pointer"
                      title="Edit eligibility rules"
                    >
                      <Sliders class="w-3.5 h-3.5" />
                    </button>

                    <!-- Edit Scheme Metadata -->
                    <button
                      @click="openEditModal(s)"
                      class="p-1.5 rounded-lg bg-white hover:bg-slate-100 text-[#0B132B] border-[1.5px] border-[#0B132B] shadow-[1px_1px_0_0_#0B132B] cursor-pointer"
                      title="Edit Scheme Details"
                    >
                      <Edit class="w-3.5 h-3.5" />
                    </button>

                    <!-- Re-Run Matching -->
                    <button
                      @click="triggerReRun(s)"
                      class="p-1.5 rounded-lg bg-[#ECFDF5] hover:bg-[#D1FAE5] text-[#065F46] border-[1.5px] border-[#065F46] shadow-[1px_1px_0_0_#065F46] cursor-pointer"
                      title="Check all students again against this scheme"
                    >
                      <RefreshCw class="w-3.5 h-3.5" />
                    </button>

                    <!-- Version History -->
                    <button
                      @click="openHistory(s)"
                      class="p-1.5 rounded-lg bg-[#FAF5FF] hover:bg-[#F3E8FF] text-[#6B21A8] border-[1.5px] border-[#6B21A8] shadow-[1px_1px_0_0_#6B21A8] cursor-pointer"
                      title="View change history"
                    >
                      <History class="w-3.5 h-3.5" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>

    <!-- MODAL 1: STRUCTURED ELIGIBILITY RULE EDITOR (Requirement 3 & Rule Change Handling 1, 2, 3) -->
    <div v-if="isRuleModalOpen" class="fixed inset-0 z-50 bg-[#0B132B]/70 backdrop-blur-xs flex items-center justify-center p-4">
      <div class="bg-[#FBFBFA] rounded-xl max-w-3xl w-full p-6 shadow-[4px_4px_0_0_#0B132B] border-[2px] border-[#0B132B] max-h-[90vh] flex flex-col">
        <div class="flex items-center justify-between pb-3 border-b-[1.5px] border-[#0B132B]">
          <div>
            <h2 class="text-base font-black text-[#0B132B] flex items-center gap-2">
              <Sliders class="w-4 h-4 text-[#D97706]" />
              Eligibility rules for: {{ selectedScheme?.code }}
            </h2>
            <p class="text-xs text-[#64748B] font-medium">Change the rules that decide eligibility. Each rule should cite its official order.</p>
          </div>
          <button @click="isRuleModalOpen = false" class="text-[#64748B] hover:text-[#0B132B] font-bold cursor-pointer">
            <X class="w-5 h-5" />
          </button>
        </div>

        <div class="flex-1 overflow-y-auto py-4 space-y-4">
          <!-- Top Root Operator -->
          <div class="flex items-center justify-between bg-white p-3 rounded-lg border-[1.5px] border-[#0B132B] shadow-[1.5px_1.5px_0_0_#0B132B]">
            <div>
              <span class="text-xs font-black text-[#0B132B] uppercase tracking-wider">Match type:</span>
              <p class="text-[11px] text-[#64748B] font-medium">Choose whether a student must meet all rules, or just one.</p>
            </div>
            <select
              v-model="ruleForm.operator"
              class="text-xs font-bold px-3 py-1.5 rounded-lg border border-[#0B132B] bg-white text-[#0B132B]"
            >
              <option value="ALL">ALL (must meet every rule)</option>
              <option value="ANY">ANY (meet at least one rule)</option>
            </select>
          </div>

          <!-- Conditions List -->
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-xs font-black uppercase tracking-wider text-[#0B132B]">Rules ({{ ruleForm.conditions.length }})</span>
              <button
                @click="addCondition"
                class="px-3 py-1.5 bg-[#FEF3C7] hover:bg-[#FDE68A] text-[#92400E] font-black text-xs rounded-lg flex items-center gap-1 border border-[#D97706] shadow-[1px_1px_0_0_#D97706] cursor-pointer"
              >
                <Plus class="w-3.5 h-3.5" />
                <span>Add a rule</span>
              </button>
            </div>

            <div 
              v-for="(cond, idx) in ruleForm.conditions" 
              :key="idx"
              class="p-4 rounded-lg bg-white border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#0B132B] space-y-3"
            >
              <div class="flex items-center justify-between">
                <span class="text-xs font-black text-[#0B132B]">Rule #{{ idx + 1 }}</span>
                <button @click="removeCondition(idx)" class="text-xs text-[#DC2626] hover:text-[#991B1B] font-bold cursor-pointer">
                  Remove
                </button>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-3 gap-2.5 text-xs">
                <div>
                  <label class="block font-bold text-[#475569] mb-1">What to check</label>
                  <select v-model="cond.field" class="w-full px-2.5 py-1.5 rounded-lg border border-[#0B132B] bg-white font-bold text-[#0B132B]">
                    <option v-for="f in availableFields" :key="f.key" :value="f.key">{{ f.label }}</option>
                  </select>
                </div>

                <div>
                  <label class="block font-bold text-[#475569] mb-1">Comparison</label>
                  <select v-model="cond.op" class="w-full px-2.5 py-1.5 rounded-lg border border-[#0B132B] bg-white font-mono font-bold text-[#0B132B]">
                    <option value="<=">&lt;= (at most)</option>
                    <option value=">=">&gt;= (at least)</option>
                    <option value="==">== (exactly equal)</option>
                    <option value="!=">!= (not equal)</option>
                    <option value="in">in (one of these)</option>
                    <option value="not_in">not in (none of these)</option>
                  </select>
                </div>

                <div>
                  <label class="block font-bold text-[#475569] mb-1">Value</label>
                  <input
                    v-model="cond.value"
                    type="text"
                    placeholder="e.g. 150000 or OBC, SC"
                    class="w-full px-2.5 py-1.5 rounded-lg border border-[#0B132B] bg-white font-mono font-bold text-[#0B132B]"
                  />
                </div>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-xs">
                <div>
                  <label class="block font-bold text-[#475569] mb-1">Label for this rule</label>
                  <input v-model="cond.label" type="text" class="w-full px-2.5 py-1.5 rounded-lg border border-[#0B132B] bg-white font-bold text-[#0B132B]" />
                </div>

                <div>
                  <label class="block font-bold text-[#475569] mb-1">Official order reference</label>
                  <input v-model="cond.citation" type="text" class="w-full px-2.5 py-1.5 rounded-lg border border-[#0B132B] bg-white font-mono text-[11px] text-[#0B132B]" />
                </div>
              </div>
            </div>
          </div>

          <!-- Change Summary (Rule Change Handling 1) -->
          <div class="pt-2">
            <label class="block text-xs font-black text-[#0B132B] uppercase tracking-wider mb-1">
              Reason for this change (required, shown in change history):
            </label>
            <textarea
              v-model="ruleForm.change_summary"
              rows="2"
              placeholder="e.g. Lowered annual income limit from ₹8L to ₹1.5L as per Finance Department GR No. ED-2024/CR-99"
              class="w-full text-xs font-bold p-3 rounded-lg border-[1.5px] border-[#0B132B] bg-white text-[#0B132B] focus:outline-hidden shadow-[1.5px_1.5px_0_0_#0B132B]"
              required
            ></textarea>
            <p class="text-[11px] text-[#92400E] font-medium mt-1">
              Saving creates a new version, keeps a copy of the old rules, and marks saved student applications to check again.
            </p>
          </div>
        </div>

        <div class="pt-4 border-t-[1.5px] border-[#0B132B] flex items-center justify-end gap-2">
          <button
            @click="isRuleModalOpen = false"
            class="px-4 py-2 border-[1.5px] border-[#0B132B] rounded-lg text-xs font-black text-[#0B132B] bg-white hover:bg-slate-50 cursor-pointer shadow-[1px_1px_0_0_#0B132B]"
          >
            Cancel
          </button>
          <button
            @click="handleSaveRules"
            :disabled="store.isLoading"
            class="px-5 py-2 bg-[#D97706] hover:bg-[#B45309] text-white font-black rounded-lg text-xs flex items-center gap-1.5 border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#0B132B] cursor-pointer"
          >
            <Save class="w-4 h-4" />
            <span>Save changes and recheck students</span>
          </button>
        </div>
      </div>
    </div>

    <!-- MODAL 2: SCHEME DETAILS & VERIFICATION STATUS (Requirements 4, 5, 7) -->
    <div v-if="isEditModalOpen || isCreateModalOpen" class="fixed inset-0 z-50 bg-[#0B132B]/70 backdrop-blur-xs flex items-center justify-center p-4">
      <div class="bg-[#FBFBFA] rounded-xl max-w-2xl w-full p-6 shadow-[4px_4px_0_0_#0B132B] border-[2px] border-[#0B132B] max-h-[90vh] flex flex-col">
        <div class="flex items-center justify-between pb-3 border-b-[1.5px] border-[#0B132B]">
          <h2 class="text-base font-black text-[#0B132B] flex items-center gap-2">
            <Edit class="w-4 h-4 text-[#D97706]" />
            {{ isCreateModalOpen ? 'Add a new scheme' : `Edit Scheme: ${schemeForm.code}` }}
          </h2>
          <button @click="isEditModalOpen = false; isCreateModalOpen = false" class="text-[#64748B] hover:text-[#0B132B] font-bold cursor-pointer">
            <X class="w-5 h-5" />
          </button>
        </div>

        <form @submit.prevent="isCreateModalOpen ? handleCreateScheme() : handleUpdateScheme()" class="flex-1 overflow-y-auto py-4 space-y-4">
          <div class="grid grid-cols-2 gap-3 text-xs">
            <div>
              <label class="block font-black text-[#0B132B] uppercase tracking-wider mb-1">Scheme Code</label>
              <input v-model="schemeForm.code" :disabled="!isCreateModalOpen" type="text" class="w-full px-3 py-2 border-[1.5px] border-[#0B132B] rounded-lg bg-white font-mono font-bold text-[#0B132B]" required />
            </div>

            <div>
              <label class="block font-black text-[#0B132B] uppercase tracking-wider mb-1">Department</label>
              <input v-model="schemeForm.department" type="text" class="w-full px-3 py-2 border-[1.5px] border-[#0B132B] rounded-lg bg-white font-bold text-[#0B132B]" required />
            </div>
          </div>

          <div class="text-xs">
            <label class="block font-black text-[#0B132B] uppercase tracking-wider mb-1">Official Scheme Name (English)</label>
            <input v-model="schemeForm.name" type="text" class="w-full px-3 py-2 border-[1.5px] border-[#0B132B] rounded-lg bg-white font-bold text-[#0B132B]" required />
          </div>

          <div class="text-xs">
            <label class="block font-black text-[#0B132B] uppercase tracking-wider mb-1">Official Marathi Name</label>
            <input v-model="schemeForm.name_marathi" type="text" class="w-full px-3 py-2 border-[1.5px] border-[#0B132B] rounded-lg bg-white font-bold text-[#0B132B]" />
          </div>

          <div class="grid grid-cols-2 gap-3 text-xs">
            <div>
              <label class="block font-black text-[#0B132B] uppercase tracking-wider mb-1">Official order number</label>
              <input v-model="schemeForm.statutory_gr" type="text" class="w-full px-3 py-2 border-[1.5px] border-[#0B132B] rounded-lg bg-white font-mono font-bold text-[#0B132B]" required />
            </div>

            <div>
              <label class="block font-black text-[#0B132B] uppercase tracking-wider mb-1">Estimated yearly value (₹)</label>
              <input v-model.number="schemeForm.estimated_annual_value" type="number" class="w-full px-3 py-2 border-[1.5px] border-[#0B132B] rounded-lg bg-white font-mono font-bold text-[#0B132B]" required />
            </div>
          </div>

          <!-- VERIFICATION STATUS & SCHEDULE (Requirements 5 & 7) -->
          <div class="p-4 rounded-lg bg-[#FEF3C7] border-[1.5px] border-[#D97706] space-y-3 text-xs shadow-[2px_2px_0_0_#D97706]">
            <div class="font-black text-[#92400E] flex items-center gap-1.5 uppercase tracking-wider">
              <Scale class="w-4 h-4 text-[#D97706]" />
              <span>Official check date and source link</span>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block font-bold text-[#92400E] mb-1">Check status</label>
                <select v-model="schemeForm.verification_status" class="w-full px-3 py-2 border border-[#0B132B] rounded-lg bg-white font-black text-[#0B132B]">
                  <option value="UNVERIFIED">Not checked yet</option>
                  <option value="NEEDS_REVIEW">Needs Review</option>
                  <option value="VERIFIED">Checked (needs official link and date)</option>
                </select>
              </div>

              <div>
                <label class="block font-bold text-[#92400E] mb-1">Last checked on</label>
                <input v-model="schemeForm.last_verified_on" type="date" class="w-full px-3 py-2 border border-[#0B132B] rounded-lg bg-white font-mono font-bold text-[#0B132B]" />
              </div>
            </div>

            <div>
              <label class="block font-bold text-[#92400E] mb-1">Official source link (required when checked)</label>
              <input v-model="schemeForm.official_source_url" type="url" placeholder="https://gr.maharashtra.gov.in/..." class="w-full px-3 py-2 border border-[#0B132B] rounded-lg bg-white font-mono font-bold text-[#0B132B]" />
            </div>
          </div>

          <div class="text-xs">
            <label class="block font-black text-[#0B132B] uppercase tracking-wider mb-1">Brief Description</label>
            <textarea v-model="schemeForm.brief_description" rows="2" class="w-full px-3 py-2 border-[1.5px] border-[#0B132B] rounded-lg bg-white font-medium text-[#0B132B]"></textarea>
          </div>

          <div class="pt-4 border-t-[1.5px] border-[#0B132B] flex items-center justify-end gap-2">
            <button
              type="button"
              @click="isEditModalOpen = false; isCreateModalOpen = false"
              class="px-4 py-2 border-[1.5px] border-[#0B132B] rounded-lg text-xs font-black text-[#0B132B] bg-white hover:bg-slate-50 cursor-pointer shadow-[1px_1px_0_0_#0B132B]"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="px-5 py-2 bg-[#059669] hover:bg-[#047857] text-white font-black rounded-lg text-xs border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#0B132B] cursor-pointer"
            >
              {{ isCreateModalOpen ? 'Create Scheme' : 'Save Changes' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL 3: VERSION HISTORY DRAWER (Requirement 6 & Rule Change Handling 1) -->
    <div v-if="isHistoryModalOpen" class="fixed inset-0 z-50 bg-[#0B132B]/70 backdrop-blur-xs flex items-center justify-center p-4">
      <div class="bg-[#FBFBFA] rounded-xl max-w-2xl w-full p-6 shadow-[4px_4px_0_0_#0B132B] border-[2px] border-[#0B132B] max-h-[85vh] flex flex-col">
        <div class="flex items-center justify-between pb-3 border-b-[1.5px] border-[#0B132B]">
          <div>
            <h2 class="text-base font-black text-[#0B132B] flex items-center gap-2">
              <History class="w-4 h-4 text-[#7C3AED]" />
              Change history for: {{ selectedScheme?.code }}
            </h2>
            <p class="text-xs text-[#64748B] font-medium">Who changed this scheme, what changed, and how many applications were affected.</p>
          </div>
          <button @click="isHistoryModalOpen = false" class="text-[#64748B] hover:text-[#0B132B] font-bold cursor-pointer">
            <X class="w-5 h-5" />
          </button>
        </div>

        <div class="flex-1 overflow-y-auto py-4 space-y-3">
          <div 
            v-for="v in schemeHistory" 
            :key="v.id"
            class="p-4 rounded-lg bg-white border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#0B132B] space-y-2 text-xs"
          >
            <div class="flex items-center justify-between">
              <span class="font-black text-[#0B132B] text-sm">v{{ v.version }} ({{ v.change_type }})</span>
              <span class="text-[#64748B] font-mono text-[11px]">{{ new Date(v.changed_at).toLocaleString('en-IN') }}</span>
            </div>

            <p class="text-[#334155] font-medium leading-relaxed">{{ v.change_summary }}</p>

            <div class="flex items-center justify-between text-[11px] text-[#64748B] pt-1 border-t border-[#E2E8F0]">
              <span>Changed by: <strong class="text-[#0B132B]">{{ v.changed_by }}</strong></span>
              <span v-if="v.affected_applications_count > 0" class="text-[#D97706] font-black">
                ⚠️ {{ v.affected_applications_count }} application(s) marked to check again
              </span>
            </div>
          </div>

          <div v-if="schemeHistory.length === 0" class="text-center py-8 text-xs text-[#64748B] font-medium">
            No earlier changes have been recorded for this scheme yet.
          </div>
        </div>

        <div class="pt-3 border-t-[1.5px] border-[#0B132B] text-right">
          <button
            @click="isHistoryModalOpen = false"
            class="px-4 py-2 bg-white hover:bg-slate-100 text-[#0B132B] rounded-lg text-xs font-black border-[1.5px] border-[#0B132B] shadow-[1.5px_1.5px_0_0_#0B132B] cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>

    <!-- MODAL 4: RE-RUN MATCHING REPORT (Requirement 8) -->
    <div v-if="isReRunModalOpen && reRunResults" class="fixed inset-0 z-50 bg-[#0B132B]/70 backdrop-blur-xs flex items-center justify-center p-4">
      <div class="bg-[#FBFBFA] rounded-xl max-w-xl w-full p-6 shadow-[4px_4px_0_0_#0B132B] border-[2px] border-[#0B132B] space-y-4">
        <div class="flex items-center justify-between pb-3 border-b-[1.5px] border-[#0B132B]">
          <div class="flex items-center gap-2 font-black text-[#0B132B] text-base">
            <RefreshCw class="w-4 h-4 text-[#059669]" />
            Student check report ({{ reRunResults.scheme_code }})
          </div>
          <button @click="isReRunModalOpen = false" class="text-[#64748B] hover:text-[#0B132B] font-bold cursor-pointer">
            <X class="w-5 h-5" />
          </button>
        </div>

        <div class="grid grid-cols-4 gap-2 text-center text-xs">
          <div class="p-2.5 rounded-lg bg-white border-[1.5px] border-[#0B132B] shadow-[1px_1px_0_0_#0B132B]">
            <span class="text-[#64748B] block text-[10px] font-black uppercase">Students checked</span>
            <span class="text-lg font-black text-[#0B132B] font-mono">{{ reRunResults.total_applications_re_evaluated }}</span>
          </div>
          <div class="p-2.5 rounded-lg bg-[#ECFDF5] border-[1.5px] border-[#065F46] shadow-[1px_1px_0_0_#065F46]">
            <span class="text-[#065F46] block text-[10px] font-black uppercase">Likely Eligible</span>
            <span class="text-lg font-black text-[#065F46] font-mono">{{ reRunResults.summary.LIKELY_ELIGIBLE || 0 }}</span>
          </div>
          <div class="p-2.5 rounded-lg bg-[#FEF3C7] border-[1.5px] border-[#D97706] shadow-[1px_1px_0_0_#D97706]">
            <span class="text-[#92400E] block text-[10px] font-black uppercase">Near-Eligible</span>
            <span class="text-lg font-black text-[#92400E] font-mono">{{ reRunResults.summary.NEAR_ELIGIBLE || 0 }}</span>
          </div>
          <div class="p-2.5 rounded-lg bg-[#FEF2F2] border-[1.5px] border-[#DC2626] shadow-[1px_1px_0_0_#DC2626]">
            <span class="text-[#991B1B] block text-[10px] font-black uppercase">Ineligible</span>
            <span class="text-lg font-black text-[#991B1B] font-mono">{{ reRunResults.summary.INELIGIBLE || 0 }}</span>
          </div>
        </div>

        <div class="max-h-60 overflow-y-auto space-y-2 text-xs border-[1.5px] border-[#0B132B] rounded-lg p-2 bg-white">
          <div
            v-for="(item, idx) in reRunResults.details"
            :key="idx"
            class="p-2.5 rounded-md bg-[#F8FAFC] border border-[#CBD5E1] flex items-center justify-between"
          >
            <div>
              <span class="font-black text-[#0B132B]">{{ item.student_name }}</span>
              <span class="text-[#64748B] ml-2 font-mono text-[11px]">({{ item.previous_tracker_status }})</span>
            </div>
            <span
              class="px-2 py-0.5 rounded-sm text-[10px] font-black uppercase border border-[#0B132B]"
              :class="item.new_evaluation_status === 'LIKELY_ELIGIBLE' ? 'bg-[#D1FAE5] text-[#065F46]' : 'bg-[#FEE2E2] text-[#991B1B]'"
            >
              {{ item.new_evaluation_status.replace('_', ' ') }}
            </span>
          </div>
        </div>

        <div class="pt-3 border-t-[1.5px] border-[#0B132B] text-right">
          <button
            @click="isReRunModalOpen = false"
            class="px-4 py-2 bg-[#0B132B] hover:bg-[#1C2541] text-white rounded-lg text-xs font-black border-[1.5px] border-[#0B132B] shadow-[1.5px_1.5px_0_0_#D97706] cursor-pointer"
          >
            Close report
          </button>
        </div>
      </div>
    </div>

  </div>
</template>
