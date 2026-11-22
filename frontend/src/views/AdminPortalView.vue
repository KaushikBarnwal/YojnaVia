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
  { key: 'annual_family_income', label: 'Annual Family Income (₹)', defaultOp: '<=', defaultVal: 150000 },
  { key: 'caste_category', label: 'Caste Category (OPEN, OBC, SC, ST, VJNT)', defaultOp: 'in', defaultVal: ['OBC', 'SC', 'ST'] },
  { key: 'is_maharashtra_domicile', label: 'Maharashtra Domicile (Boolean)', defaultOp: '==', defaultVal: true },
  { key: 'age', label: 'Student Age (Years)', defaultOp: '<=', defaultVal: 25 },
  { key: 'current_course_level', label: 'Course Level', defaultOp: 'in', defaultVal: ['UNDERGRADUATE', 'PROFESSIONAL_DEGREE'] },
  { key: 'admission_quota', label: 'Admission Quota', defaultOp: '==', defaultVal: 'CAP_ROUND' },
  { key: 'accommodation_type', label: 'Accommodation Type', defaultOp: '==', defaultVal: 'PRIVATE_RENTAL_PG' },
  { key: 'parent_is_farmer', label: 'Parents are Farmers', defaultOp: '==', defaultVal: true },
  { key: 'parent_land_acres', label: 'Agricultural Land Holding (Acres)', defaultOp: '<=', defaultVal: 5 },
  { key: 'previous_year_percentage', label: 'Previous Year Percentage', defaultOp: '>=', defaultVal: 60 }
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
    loginError.value = err.response?.data?.error || 'Invalid officer credentials';
  }
}

async function handleDemoLogin(role: 'SCHEME_OFFICER' | 'SUPERADMIN') {
  loginError.value = '';
  try {
    await store.adminLogin(undefined, undefined, role);
  } catch (err: any) {
    loginError.value = 'Demo authentication error';
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
    alert(err.message);
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
    alert(err.message);
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
    alert("Please enter a summary of changes explaining the statutory revision.");
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
    alert(err.message);
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
    alert("Re-run matching failed: " + err.message);
  }
}

async function toggleActive(code: string) {
  await store.toggleAdminSchemeStatus(code);
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
    
    <!-- AUTHENTICATION SCREEN IF NOT LOGGED IN (Requirement 1) -->
    <div v-if="!store.adminUser" class="max-w-md mx-auto my-12 bg-white rounded-3xl border border-slate-200 shadow-xl p-8 space-y-6">
      <div class="text-center space-y-2">
        <div class="w-14 h-14 rounded-2xl bg-indigo-600 text-white flex items-center justify-center mx-auto shadow-lg shadow-indigo-200">
          <ShieldCheck class="w-8 h-8" />
        </div>
        <h1 class="text-2xl font-black text-slate-900 tracking-tight">Admin & Officer Portal</h1>
        <p class="text-xs text-slate-500">Government Benefits Management & Statutory Rule Configuration</p>
      </div>

      <!-- Quick 1-Click Demo Login for Judges -->
      <div class="p-4 rounded-2xl bg-indigo-50 border border-indigo-200 space-y-3">
        <div class="flex items-center gap-2 text-indigo-900 font-bold text-xs uppercase tracking-wider">
          <Lock class="w-3.5 h-3.5" />
          <span>Hackathon Demo 1-Click Role Login</span>
        </div>
        <div class="grid grid-cols-2 gap-2">
          <button
            @click="handleDemoLogin('SCHEME_OFFICER')"
            class="p-2.5 bg-white hover:bg-slate-50 text-indigo-700 font-bold text-xs rounded-xl border border-indigo-200 shadow-xs flex flex-col items-center gap-1 transition-all"
          >
            <UserCheck class="w-4 h-4 text-indigo-600" />
            <span>Scheme Officer</span>
            <span class="text-[10px] text-slate-500 font-normal">MahaDBT Desk</span>
          </button>

          <button
            @click="handleDemoLogin('SUPERADMIN')"
            class="p-2.5 bg-white hover:bg-slate-50 text-indigo-700 font-bold text-xs rounded-xl border border-indigo-200 shadow-xs flex flex-col items-center gap-1 transition-all"
          >
            <Building class="w-4 h-4 text-purple-600" />
            <span>Superadmin</span>
            <span class="text-[10px] text-slate-500 font-normal">Principal Secretary</span>
          </button>
        </div>
      </div>

      <!-- Standard Manual Form -->
      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-xs font-semibold text-slate-700 mb-1">Username</label>
          <input
            v-model="loginUsername"
            type="text"
            placeholder="officer or admin"
            class="w-full text-sm border border-slate-300 rounded-xl px-3.5 py-2.5 focus:ring-2 focus:ring-indigo-500"
            required
          />
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-700 mb-1">Password</label>
          <input
            v-model="loginPassword"
            type="password"
            placeholder="officer123 or admin123"
            class="w-full text-sm border border-slate-300 rounded-xl px-3.5 py-2.5 focus:ring-2 focus:ring-indigo-500"
            required
          />
        </div>

        <div v-if="loginError" class="text-xs text-rose-600 font-semibold bg-rose-50 p-2.5 rounded-xl border border-rose-200">
          {{ loginError }}
        </div>

        <button
          type="submit"
          :disabled="store.isLoading"
          class="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl text-sm transition-colors shadow-md shadow-indigo-100 flex items-center justify-center gap-2"
        >
          <Lock class="w-4 h-4" />
          <span>Sign In to Admin Panel</span>
        </button>
      </form>
    </div>

    <!-- MAIN ADMIN PANEL (When Logged In) -->
    <div v-else class="space-y-6">
      
      <!-- Top Officer Header Bar -->
      <div class="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 rounded-3xl p-6 text-white shadow-xl border border-indigo-900/50 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div class="space-y-1">
          <div class="flex items-center gap-2">
            <span class="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold uppercase tracking-wider bg-indigo-500/30 text-indigo-300 border border-indigo-400/30">
              {{ store.adminUser.role }}
            </span>
            <span class="text-xs text-emerald-400 font-semibold flex items-center gap-1">
              <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              Authenticated Session
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
            class="px-4 py-2.5 bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold text-xs rounded-xl shadow-md flex items-center gap-1.5 transition-transform active:scale-95"
          >
            <Plus class="w-4 h-4" />
            <span>Create New Scheme</span>
          </button>

          <button
            @click="handleLogout"
            class="px-3.5 py-2.5 bg-white/10 hover:bg-white/20 text-white text-xs font-semibold rounded-xl border border-white/20 flex items-center gap-1.5 transition-colors"
          >
            <LogOut class="w-4 h-4 text-rose-400" />
            <span>Sign Out</span>
          </button>
        </div>
      </div>

      <!-- Stats Counters -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div class="bg-white rounded-2xl p-4 border border-slate-200 shadow-xs">
          <span class="text-xs text-slate-500 block">Total Catalog Schemes</span>
          <span class="text-2xl font-black text-slate-900 mt-1 block">{{ store.adminSchemes.length }}</span>
        </div>

        <div class="bg-white rounded-2xl p-4 border border-slate-200 shadow-xs">
          <span class="text-xs text-slate-500 block">Active In Production</span>
          <span class="text-2xl font-black text-emerald-700 mt-1 block">{{ activeCount }}</span>
        </div>

        <div class="bg-white rounded-2xl p-4 border border-slate-200 shadow-xs">
          <span class="text-xs text-slate-500 block">Statutorily Verified</span>
          <span class="text-2xl font-black text-indigo-700 mt-1 block">{{ verifiedCount }}</span>
        </div>

        <div class="bg-white rounded-2xl p-4 border border-slate-200 shadow-xs">
          <span class="text-xs text-slate-500 block">Tracked User Applications</span>
          <span class="text-2xl font-black text-amber-700 mt-1 block">{{ store.trackedApplications.length }}</span>
        </div>
      </div>

      <!-- Search & Filters Toolbar -->
      <div class="bg-white rounded-2xl p-4 border border-slate-200 shadow-xs flex flex-col md:flex-row items-center justify-between gap-3">
        <div class="relative w-full md:w-80">
          <Search class="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search by code, scheme, or department..."
            class="w-full pl-9 pr-3.5 py-2 text-xs border border-slate-300 rounded-xl focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <div class="flex flex-wrap items-center gap-2 w-full md:w-auto">
          <select
            v-model="statusFilter"
            class="text-xs border border-slate-300 rounded-xl px-3 py-2 bg-slate-50 text-slate-700 font-medium"
          >
            <option value="ALL">All Statuses</option>
            <option value="ACTIVE">Active Only</option>
            <option value="INACTIVE">Inactive Only</option>
          </select>

          <select
            v-model="verificationFilter"
            class="text-xs border border-slate-300 rounded-xl px-3 py-2 bg-slate-50 text-slate-700 font-medium"
          >
            <option value="ALL">All Verification</option>
            <option value="VERIFIED">Verified Only</option>
            <option value="UNVERIFIED">Unverified</option>
            <option value="NEEDS_REVIEW">Needs Review</option>
          </select>

          <button
            @click="store.fetchAdminSchemes()"
            class="p-2 border border-slate-300 rounded-xl text-slate-600 hover:bg-slate-50"
            title="Refresh"
          >
            <RefreshCw class="w-4 h-4" />
          </button>
        </div>
      </div>

      <!-- Schemes Management Table (Requirements 2, 3, 5, 6, 7, 8) -->
      <div class="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead class="bg-slate-50 border-b border-slate-200 text-slate-600 font-bold uppercase tracking-wider text-[11px]">
              <tr>
                <th class="py-3.5 px-4">Scheme Code & Name</th>
                <th class="py-3.5 px-4">Department & GR</th>
                <th class="py-3.5 px-4">Benefit Type</th>
                <th class="py-3.5 px-4">Verification</th>
                <th class="py-3.5 px-4">Rule Ver</th>
                <th class="py-3.5 px-4">Status</th>
                <th class="py-3.5 px-4 text-right">Administrative Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr 
                v-for="s in filteredAdminSchemes" 
                :key="s.code"
                class="hover:bg-slate-50/70 transition-colors"
              >
                <!-- Code & Name -->
                <td class="py-3.5 px-4">
                  <div class="font-mono font-bold text-indigo-700">{{ s.code }}</div>
                  <div class="font-bold text-slate-900 mt-0.5 line-clamp-1">{{ s.name }}</div>
                  <div v-if="s.name_marathi" class="text-[11px] text-slate-500 line-clamp-1">{{ s.name_marathi }}</div>
                </td>

                <!-- Department & GR -->
                <td class="py-3.5 px-4">
                  <div class="text-slate-800 font-medium line-clamp-1">{{ s.department }}</div>
                  <div class="text-[11px] text-slate-500 font-mono mt-0.5 flex items-center gap-1">
                    <Scale class="w-3 h-3 text-slate-400" />
                    <span>{{ s.statutory_gr }}</span>
                  </div>
                </td>

                <!-- Benefit -->
                <td class="py-3.5 px-4">
                  <div class="font-bold text-emerald-800 font-mono">{{ s.benefit_amount_text }}</div>
                  <div class="text-[11px] text-slate-500">₹{{ Number(s.estimated_annual_value || 0).toLocaleString('en-IN') }}/yr</div>
                </td>

                <!-- Verification (Requirement 7) -->
                <td class="py-3.5 px-4">
                  <span
                    class="px-2 py-0.5 rounded-full font-bold uppercase text-[10px] inline-flex items-center gap-1 border"
                    :class="s.verification_status === 'VERIFIED'
                      ? 'bg-emerald-50 text-emerald-800 border-emerald-300'
                      : (s.verification_status === 'NEEDS_REVIEW' ? 'bg-amber-50 text-amber-800 border-amber-300' : 'bg-slate-100 text-slate-700 border-slate-300')"
                  >
                    <CheckCircle2 v-if="s.verification_status === 'VERIFIED'" class="w-3 h-3 text-emerald-600" />
                    <AlertTriangle v-else class="w-3 h-3 text-amber-600" />
                    {{ s.verification_status || 'UNVERIFIED' }}
                  </span>
                  <div v-if="s.last_verified_on" class="text-[10px] text-slate-400 mt-1">
                    {{ s.last_verified_on }}
                  </div>
                </td>

                <!-- Rule Version (Rule Change Handling 1) -->
                <td class="py-3.5 px-4">
                  <span class="font-mono bg-slate-100 text-slate-700 px-2 py-0.5 rounded text-[11px] font-bold">
                    v{{ s.version }}
                  </span>
                  <div class="text-[10px] text-slate-400 mt-0.5">
                    {{ (s.rules?.conditions || []).length }} rules
                  </div>
                </td>

                <!-- Active Toggle (Requirement 2) -->
                <td class="py-3.5 px-4">
                  <button
                    @click="toggleActive(s.code)"
                    class="px-2.5 py-1 rounded-full text-[11px] font-bold transition-colors flex items-center gap-1 border"
                    :class="s.is_active
                      ? 'bg-emerald-50 text-emerald-700 border-emerald-200 hover:bg-emerald-100'
                      : 'bg-rose-50 text-rose-700 border-rose-200 hover:bg-rose-100'"
                  >
                    <span class="w-1.5 h-1.5 rounded-full" :class="s.is_active ? 'bg-emerald-500' : 'bg-rose-500'"></span>
                    <span>{{ s.is_active ? 'Active' : 'Inactive' }}</span>
                  </button>
                </td>

                <!-- Actions -->
                <td class="py-3.5 px-4 text-right">
                  <div class="flex items-center justify-end gap-1.5">
                    <!-- Edit Rules AST -->
                    <button
                      @click="openRuleEditor(s)"
                      class="p-1.5 rounded-lg bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200"
                      title="Edit Eligibility Rules AST"
                    >
                      <Sliders class="w-3.5 h-3.5" />
                    </button>

                    <!-- Edit Scheme Metadata -->
                    <button
                      @click="openEditModal(s)"
                      class="p-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-300"
                      title="Edit Scheme Details"
                    >
                      <Edit class="w-3.5 h-3.5" />
                    </button>

                    <!-- Re-Run Matching -->
                    <button
                      @click="triggerReRun(s)"
                      class="p-1.5 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200"
                      title="Re-Run Matching Against Student Records"
                    >
                      <RefreshCw class="w-3.5 h-3.5" />
                    </button>

                    <!-- Version History -->
                    <button
                      @click="openHistory(s)"
                      class="p-1.5 rounded-lg bg-purple-50 hover:bg-purple-100 text-purple-700 border border-purple-200"
                      title="View Version Change History"
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
    <div v-if="isRuleModalOpen" class="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div class="bg-white rounded-3xl max-w-3xl w-full p-6 shadow-2xl border border-slate-200 max-h-[90vh] flex flex-col">
        <div class="flex items-center justify-between pb-3 border-b border-slate-100">
          <div>
            <h2 class="text-base font-extrabold text-slate-900 flex items-center gap-2">
              <Sliders class="w-4 h-4 text-indigo-600" />
              Structured Eligibility Rule AST Editor: {{ selectedScheme?.code }}
            </h2>
            <p class="text-xs text-slate-500">Edit certified Python deterministic rules with statutory citations.</p>
          </div>
          <button @click="isRuleModalOpen = false" class="text-slate-400 hover:text-slate-600">
            <X class="w-5 h-5" />
          </button>
        </div>

        <div class="flex-1 overflow-y-auto py-4 space-y-4">
          <!-- Top Root Operator -->
          <div class="flex items-center justify-between bg-slate-50 p-3 rounded-2xl border border-slate-200">
            <div>
              <span class="text-xs font-bold text-slate-800">Root Evaluation Operator:</span>
              <p class="text-[11px] text-slate-500">Determines whether all conditions must pass or any single condition passes.</p>
            </div>
            <select
              v-model="ruleForm.operator"
              class="text-xs font-bold px-3 py-1.5 rounded-xl border border-slate-300 bg-white"
            >
              <option value="ALL">ALL (Mandatory criteria conjunction)</option>
              <option value="ANY">ANY (Disjunctive concession criteria)</option>
            </select>
          </div>

          <!-- Conditions List -->
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold uppercase tracking-wider text-slate-600">Criteria Conditions ({{ ruleForm.conditions.length }})</span>
              <button
                @click="addCondition"
                class="px-3 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-bold text-xs rounded-xl flex items-center gap-1 border border-indigo-200"
              >
                <Plus class="w-3.5 h-3.5" />
                <span>Add Condition</span>
              </button>
            </div>

            <div 
              v-for="(cond, idx) in ruleForm.conditions" 
              :key="idx"
              class="p-4 rounded-2xl bg-slate-50/70 border border-slate-200 space-y-3"
            >
              <div class="flex items-center justify-between">
                <span class="text-xs font-bold text-indigo-700">Condition #{{ idx + 1 }}</span>
                <button @click="removeCondition(idx)" class="text-xs text-rose-600 hover:text-rose-800 font-semibold">
                  Remove
                </button>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-3 gap-2.5 text-xs">
                <div>
                  <label class="block font-semibold text-slate-600 mb-1">Target Field</label>
                  <select v-model="cond.field" class="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 bg-white">
                    <option v-for="f in availableFields" :key="f.key" :value="f.key">{{ f.label }}</option>
                  </select>
                </div>

                <div>
                  <label class="block font-semibold text-slate-600 mb-1">Operator</label>
                  <select v-model="cond.op" class="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 bg-white font-mono">
                    <option value="<=">&lt;= (Less than or equal ceiling)</option>
                    <option value=">=">&gt;= (Greater than or equal)</option>
                    <option value="==">== (Exact match)</option>
                    <option value="!=">!= (Must not match)</option>
                    <option value="in">in (Set membership e.g. categories)</option>
                    <option value="not_in">not_in (Excluded categories)</option>
                  </select>
                </div>

                <div>
                  <label class="block font-semibold text-slate-600 mb-1">Target Value</label>
                  <input
                    v-model="cond.value"
                    type="text"
                    placeholder="e.g. 150000 or OBC, SC"
                    class="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 bg-white font-mono"
                  />
                </div>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-xs">
                <div>
                  <label class="block font-semibold text-slate-600 mb-1">Human-Friendly Requirement Label</label>
                  <input v-model="cond.label" type="text" class="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 bg-white" />
                </div>

                <div>
                  <label class="block font-semibold text-slate-600 mb-1">Statutory GR Citation Reference</label>
                  <input v-model="cond.citation" type="text" class="w-full px-2.5 py-1.5 rounded-lg border border-slate-300 bg-white font-mono text-[11px]" />
                </div>
              </div>
            </div>
          </div>

          <!-- Change Summary (Rule Change Handling 1) -->
          <div class="pt-2">
            <label class="block text-xs font-bold text-slate-700 mb-1">
              Statutory Change Summary / Justification (Mandatory for Version History):
            </label>
            <textarea
              v-model="ruleForm.change_summary"
              rows="2"
              placeholder="e.g. Lowered annual income limit from ₹8L to ₹1.5L as per Finance Department GR No. ED-2024/CR-99"
              class="w-full text-xs p-3 rounded-xl border border-slate-300 focus:ring-2 focus:ring-indigo-500"
              required
            ></textarea>
            <p class="text-[11px] text-amber-700 mt-1">
              Saving will increment the scheme version, snapshot the previous rule AST, and automatically flag all saved student applications for re-evaluation.
            </p>
          </div>
        </div>

        <div class="pt-4 border-t border-slate-100 flex items-center justify-end gap-2">
          <button
            @click="isRuleModalOpen = false"
            class="px-4 py-2 border border-slate-300 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-50"
          >
            Cancel
          </button>
          <button
            @click="handleSaveRules"
            :disabled="store.isLoading"
            class="px-5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl text-xs flex items-center gap-1.5 shadow-md shadow-indigo-100"
          >
            <Save class="w-4 h-4" />
            <span>Save Rule Revision & Invalidate Outdated Matches</span>
          </button>
        </div>
      </div>
    </div>

    <!-- MODAL 2: SCHEME DETAILS & VERIFICATION STATUS (Requirements 4, 5, 7) -->
    <div v-if="isEditModalOpen || isCreateModalOpen" class="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div class="bg-white rounded-3xl max-w-2xl w-full p-6 shadow-2xl border border-slate-200 max-h-[90vh] flex flex-col">
        <div class="flex items-center justify-between pb-3 border-b border-slate-100">
          <h2 class="text-base font-extrabold text-slate-900 flex items-center gap-2">
            <Edit class="w-4 h-4 text-indigo-600" />
            {{ isCreateModalOpen ? 'Create New Scheme' : `Edit Scheme: ${schemeForm.code}` }}
          </h2>
          <button @click="isEditModalOpen = false; isCreateModalOpen = false" class="text-slate-400 hover:text-slate-600">
            <X class="w-5 h-5" />
          </button>
        </div>

        <form @submit.prevent="isCreateModalOpen ? handleCreateScheme() : handleUpdateScheme()" class="flex-1 overflow-y-auto py-4 space-y-4">
          <div class="grid grid-cols-2 gap-3 text-xs">
            <div>
              <label class="block font-semibold text-slate-700 mb-1">Scheme Code</label>
              <input v-model="schemeForm.code" :disabled="!isCreateModalOpen" type="text" class="w-full px-3 py-2 border border-slate-300 rounded-xl font-mono" required />
            </div>

            <div>
              <label class="block font-semibold text-slate-700 mb-1">Department</label>
              <input v-model="schemeForm.department" type="text" class="w-full px-3 py-2 border border-slate-300 rounded-xl" required />
            </div>
          </div>

          <div class="text-xs">
            <label class="block font-semibold text-slate-700 mb-1">Official Scheme Name (English)</label>
            <input v-model="schemeForm.name" type="text" class="w-full px-3 py-2 border border-slate-300 rounded-xl" required />
          </div>

          <div class="text-xs">
            <label class="block font-semibold text-slate-700 mb-1">Official Marathi Name</label>
            <input v-model="schemeForm.name_marathi" type="text" class="w-full px-3 py-2 border border-slate-300 rounded-xl" />
          </div>

          <div class="grid grid-cols-2 gap-3 text-xs">
            <div>
              <label class="block font-semibold text-slate-700 mb-1">Statutory GR Reference</label>
              <input v-model="schemeForm.statutory_gr" type="text" class="w-full px-3 py-2 border border-slate-300 rounded-xl font-mono" required />
            </div>

            <div>
              <label class="block font-semibold text-slate-700 mb-1">Estimated Annual Value (₹)</label>
              <input v-model.number="schemeForm.estimated_annual_value" type="number" class="w-full px-3 py-2 border border-slate-300 rounded-xl font-mono" required />
            </div>
          </div>

          <!-- VERIFICATION STATUS & SCHEDULE (Requirements 5 & 7) -->
          <div class="p-4 rounded-2xl bg-amber-50/80 border border-amber-300 space-y-3 text-xs">
            <div class="font-bold text-amber-950 flex items-center gap-1.5">
              <Scale class="w-4 h-4 text-amber-700" />
              <span>Statutory Verification Schedule & URL Invariant</span>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block font-semibold text-amber-900 mb-1">Verification Status</label>
                <select v-model="schemeForm.verification_status" class="w-full px-3 py-2 border border-amber-300 rounded-xl bg-white font-bold">
                  <option value="UNVERIFIED">Unverified</option>
                  <option value="NEEDS_REVIEW">Needs Review</option>
                  <option value="VERIFIED">Verified (Requires Gazette Source URL & Date)</option>
                </select>
              </div>

              <div>
                <label class="block font-semibold text-amber-900 mb-1">Last Verified On</label>
                <input v-model="schemeForm.last_verified_on" type="date" class="w-full px-3 py-2 border border-amber-300 rounded-xl bg-white font-mono" />
              </div>
            </div>

            <div>
              <label class="block font-semibold text-amber-900 mb-1">Official Gazette / Source URL (Mandatory for VERIFIED)</label>
              <input v-model="schemeForm.official_source_url" type="url" placeholder="https://gr.maharashtra.gov.in/..." class="w-full px-3 py-2 border border-amber-300 rounded-xl bg-white font-mono" />
            </div>
          </div>

          <div class="text-xs">
            <label class="block font-semibold text-slate-700 mb-1">Brief Description</label>
            <textarea v-model="schemeForm.brief_description" rows="2" class="w-full px-3 py-2 border border-slate-300 rounded-xl"></textarea>
          </div>

          <div class="pt-4 border-t border-slate-100 flex items-center justify-end gap-2">
            <button
              type="button"
              @click="isEditModalOpen = false; isCreateModalOpen = false"
              class="px-4 py-2 border border-slate-300 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="px-5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl text-xs shadow-xs"
            >
              {{ isCreateModalOpen ? 'Create Scheme' : 'Save Changes' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL 3: VERSION HISTORY DRAWER (Requirement 6 & Rule Change Handling 1) -->
    <div v-if="isHistoryModalOpen" class="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div class="bg-white rounded-3xl max-w-2xl w-full p-6 shadow-2xl border border-slate-200 max-h-[85vh] flex flex-col">
        <div class="flex items-center justify-between pb-3 border-b border-slate-100">
          <div>
            <h2 class="text-base font-extrabold text-slate-900 flex items-center gap-2">
              <History class="w-4 h-4 text-purple-600" />
              Statutory Version History: {{ selectedScheme?.code }}
            </h2>
            <p class="text-xs text-slate-500">Record of who edited this scheme, what changed, and affected application counts.</p>
          </div>
          <button @click="isHistoryModalOpen = false" class="text-slate-400 hover:text-slate-600">
            <X class="w-5 h-5" />
          </button>
        </div>

        <div class="flex-1 overflow-y-auto py-4 space-y-3">
          <div 
            v-for="v in schemeHistory" 
            :key="v.id"
            class="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2 text-xs"
          >
            <div class="flex items-center justify-between">
              <span class="font-bold text-slate-900 text-sm">v{{ v.version }} ({{ v.change_type }})</span>
              <span class="text-slate-400">{{ new Date(v.changed_at).toLocaleString('en-IN') }}</span>
            </div>

            <p class="text-slate-700 font-medium">{{ v.change_summary }}</p>

            <div class="flex items-center justify-between text-[11px] text-slate-500 pt-1 border-t border-slate-200/80">
              <span>Changed by: <strong class="text-slate-700">{{ v.changed_by }}</strong></span>
              <span v-if="v.affected_applications_count > 0" class="text-amber-700 font-bold">
                ⚠️ {{ v.affected_applications_count }} application(s) marked for re-evaluation
              </span>
            </div>
          </div>

          <div v-if="schemeHistory.length === 0" class="text-center py-8 text-xs text-slate-400">
            No previous rule revisions recorded for this scheme yet.
          </div>
        </div>

        <div class="pt-3 border-t border-slate-100 text-right">
          <button
            @click="isHistoryModalOpen = false"
            class="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-semibold"
          >
            Close History
          </button>
        </div>
      </div>
    </div>

    <!-- MODAL 4: RE-RUN MATCHING REPORT (Requirement 8) -->
    <div v-if="isReRunModalOpen && reRunResults" class="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div class="bg-white rounded-3xl max-w-xl w-full p-6 shadow-2xl border border-slate-200 space-y-4">
        <div class="flex items-center justify-between pb-3 border-b border-slate-100">
          <div class="flex items-center gap-2 font-bold text-slate-900 text-base">
            <RefreshCw class="w-4 h-4 text-emerald-600" />
            Re-Run Matching Report ({{ reRunResults.scheme_code }})
          </div>
          <button @click="isReRunModalOpen = false" class="text-slate-400 hover:text-slate-600">
            <X class="w-5 h-5" />
          </button>
        </div>

        <div class="grid grid-cols-4 gap-2 text-center text-xs">
          <div class="p-2.5 rounded-xl bg-slate-50 border border-slate-200">
            <span class="text-slate-500 block text-[10px]">Total Scanned</span>
            <span class="text-lg font-bold text-slate-900">{{ reRunResults.total_applications_re_evaluated }}</span>
          </div>
          <div class="p-2.5 rounded-xl bg-emerald-50 border border-emerald-200">
            <span class="text-emerald-700 block text-[10px]">Likely Eligible</span>
            <span class="text-lg font-bold text-emerald-800">{{ reRunResults.summary.LIKELY_ELIGIBLE || 0 }}</span>
          </div>
          <div class="p-2.5 rounded-xl bg-amber-50 border border-amber-200">
            <span class="text-amber-700 block text-[10px]">Near-Eligible</span>
            <span class="text-lg font-bold text-amber-800">{{ reRunResults.summary.NEAR_ELIGIBLE || 0 }}</span>
          </div>
          <div class="p-2.5 rounded-xl bg-rose-50 border border-rose-200">
            <span class="text-rose-700 block text-[10px]">Ineligible</span>
            <span class="text-lg font-bold text-rose-800">{{ reRunResults.summary.INELIGIBLE || 0 }}</span>
          </div>
        </div>

        <div class="max-h-60 overflow-y-auto space-y-2 text-xs">
          <div
            v-for="(item, idx) in reRunResults.details"
            :key="idx"
            class="p-3 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between"
          >
            <div>
              <span class="font-bold text-slate-900">{{ item.student_name }}</span>
              <span class="text-slate-400 ml-2">({{ item.previous_tracker_status }})</span>
            </div>
            <span
              class="px-2 py-0.5 rounded text-[10px] font-bold uppercase"
              :class="item.new_evaluation_status === 'LIKELY_ELIGIBLE' ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'"
            >
              {{ item.new_evaluation_status.replace('_', ' ') }}
            </span>
          </div>
        </div>

        <div class="pt-3 border-t border-slate-100 text-right">
          <button
            @click="isReRunModalOpen = false"
            class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold"
          >
            Dismiss Report
          </button>
        </div>
      </div>
    </div>

  </div>
</template>
