<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useStudentStore } from '../stores/studentStore';
import PersonaBar from '../components/PersonaBar.vue';
import RejectionRecoveryModal from '../components/RejectionRecoveryModal.vue';
import type { ApplicationStatus } from '../types';
import { 
  CheckCircle2, 
  ExternalLink, 
  AlertCircle,
  ArrowRight,
  Info,
  Edit2,
  X,
  AlertTriangle,
  RotateCcw,
  Check
} from '@lucide/vue';

const store = useStudentStore();

onMounted(async () => {
  await store.fetchTracker();
});

// 7 Canonical Statuses (Requirement 2)
const statuses: Array<{ key: ApplicationStatus; label: string; class: string }> = [
  { key: 'NOT_STARTED', label: '1. Not Started', class: 'bg-slate-100 text-slate-700 border-slate-300' },
  { key: 'DOCUMENTS_PENDING', label: '2. Documents Pending', class: 'bg-amber-50 text-amber-800 border-amber-300' },
  { key: 'DOCUMENTS_READY', label: '3. Documents Ready', class: 'bg-blue-50 text-blue-800 border-blue-300' },
  { key: 'APPLIED', label: '4. Applied', class: 'bg-indigo-50 text-indigo-800 border-indigo-300' },
  { key: 'UNDER_REVIEW', label: '5. Under Review', class: 'bg-purple-50 text-purple-800 border-purple-300' },
  { key: 'APPROVED', label: '6. Approved', class: 'bg-emerald-50 text-emerald-800 border-emerald-300' },
  { key: 'REJECTED', label: '7. Rejected', class: 'bg-rose-50 text-rose-800 border-rose-300' }
];

// Edit modal state
const isEditModalOpen = ref(false);
const editingApp = ref<any>(null);
const editStatus = ref<ApplicationStatus>('NOT_STARTED');
const editRefNo = ref('');
const editAppliedDate = ref('');
const editSubmissionMode = ref('Online Portal');
const editNotes = ref('');

// Rejection Recovery Modal state
const isRecoveryOpen = ref(false);
const recoverySchemeCode = ref('');
const recoveryInitialRemark = ref('');

function openRejectionNavigator(schemeCode?: string, remark?: string) {
  recoverySchemeCode.value = schemeCode || 'MH_DTE_EBC_2024';
  recoveryInitialRemark.value = remark || '';
  isRecoveryOpen.value = true;
}

function openEditModal(app: any) {
  editingApp.value = app;
  editStatus.value = app.status || 'NOT_STARTED';
  editRefNo.value = app.application_reference_number || '';
  editAppliedDate.value = app.applied_date || '';
  editSubmissionMode.value = app.submission_mode || 'Online Portal';
  editNotes.value = app.notes || '';
  isEditModalOpen.value = true;
}

async function handleSaveDetails() {
  if (!editingApp.value) return;
  await store.updateTrackerRecord({
    scheme_code: editingApp.value.scheme_code,
    status: editStatus.value,
    application_reference_number: editRefNo.value,
    applied_date: editAppliedDate.value || undefined,
    submission_mode: editSubmissionMode.value,
    notes: editNotes.value
  });
  isEditModalOpen.value = false;
}

async function quickAdvanceStatus(app: any, newStatus: ApplicationStatus) {
  await store.updateTrackerRecord({
    scheme_code: app.scheme_code,
    status: newStatus,
    application_reference_number: app.application_reference_number,
    applied_date: app.applied_date,
    submission_mode: app.submission_mode,
    notes: app.notes,
    completed_documents: app.completed_documents
  });
}

async function handleReEvaluateApp(schemeCode: string) {
  await store.acknowledgeReEvaluation(schemeCode);
  await store.evaluateEligibility();
  alert("Re-evaluation complete! Your application results have been refreshed against the latest statutory rules.");
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
    <PersonaBar />

    <!-- Page Title Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-bold uppercase tracking-wider mb-2">
          <CheckCircle2 class="w-3.5 h-3.5 text-emerald-600" />
          Step 5 of 5: Application Progress & Milestone Follow-Up Tracker
        </div>
        <h1 class="text-2xl sm:text-3xl font-extrabold text-slate-900">
          My Saved Applications & Milestone Tracker
        </h1>
        <p class="text-sm text-slate-600 mt-1 max-w-3xl">
          Track your progress across self-reported offline and online milestones (from Aaple Sarkar certificate procurement to MahaDBT College Clerk submission).
        </p>
      </div>

      <router-link
        to="/schemes"
        class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs sm:text-sm font-bold transition-colors flex items-center gap-1.5 shadow-xs shrink-0 self-start md:self-auto"
      >
        <span>Discover & Save Schemes</span>
        <ArrowRight class="w-4 h-4" />
      </router-link>
    </div>

    <!-- MANDATORY LEGAL / USER-REPORTED NOTICE (Requirements 4 & 5) -->
    <div class="p-4 rounded-2xl bg-blue-50 border border-blue-200 text-blue-950 text-xs sm:text-sm font-medium flex items-start gap-3 shadow-xs">
      <Info class="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
      <div>
        <strong class="font-bold block text-blue-900 mb-0.5">User-Reported Application Status Notice (Self-Managed):</strong>
        <span>"This tracker is a personal planning and document-readiness log. YOJNAVIA does not integrate with internal government sanction databases and does not claim official departmental application status. All milestone stages, application dates, and reference numbers are user-reported."</span>
      </div>
    </div>

    <!-- REJECTION RECOVERY & GRIEVANCE NAVIGATOR BANNER -->
    <div class="p-4 rounded-2xl bg-gradient-to-r from-rose-50 to-orange-50 border border-rose-200 text-rose-950 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-xs">
      <div class="flex items-start gap-3">
        <div class="p-2 bg-rose-100 rounded-xl text-rose-700 shrink-0 mt-0.5">
          <RotateCcw class="w-5 h-5" />
        </div>
        <div>
          <div class="font-bold text-rose-900 text-sm flex items-center gap-2">
            <span>MahaDBT Scrutiny Query or Application Rejected?</span>
            <span class="text-[10px] bg-rose-200 text-rose-900 px-2 py-0.5 rounded-full font-bold">15-Day Resubmission Window</span>
          </div>
          <p class="text-xs text-rose-800 mt-0.5">
            Translate confusing scrutiny remarks into plain language, verify your 15-day resubmission window, and discover verified statutory appeal routes under the Maharashtra RTS Act 2015.
          </p>
        </div>
      </div>
      <button 
        @click="openRejectionNavigator()" 
        class="px-4 py-2 bg-rose-700 hover:bg-rose-800 text-white font-bold text-xs rounded-xl shadow-xs shrink-0 flex items-center gap-1.5 transition-colors self-start sm:self-auto"
      >
        <span>Launch Rejection Navigator</span>
        <ArrowRight class="w-3.5 h-3.5" />
      </button>
    </div>

    <!-- Active Tracked Applications -->
    <div v-if="store.trackedApplications.length > 0" class="space-y-6">
      <div 
        v-for="app in store.trackedApplications" 
        :key="app.id"
        class="bg-white rounded-3xl border border-slate-200 shadow-sm p-6 sm:p-7 overflow-hidden space-y-5"
      >
        <!-- RULE CHANGE ALERT (Rule Change Handling 2, 3, 4) -->
        <div 
          v-if="app.needs_re_evaluation" 
          class="p-4 rounded-2xl bg-amber-500/10 border-2 border-amber-500 text-amber-950 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 animate-in fade-in"
        >
          <div class="flex items-start gap-3">
            <AlertTriangle class="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
            <div>
              <div class="font-bold text-amber-900 text-xs uppercase tracking-wider flex items-center gap-1.5">
                <span>Statutory Eligibility Rule Revision Detected</span>
                <span class="text-[10px] bg-amber-200 text-amber-900 px-2 py-0.2 rounded-full font-bold">Action Needed</span>
              </div>
              <p class="text-xs text-amber-900 mt-1">
                {{ app.re_evaluation_reason || 'Eligibility criteria for this scheme were recently updated by the department.' }}
              </p>
            </div>
          </div>
          <button
            @click="handleReEvaluateApp(app.scheme_code)"
            class="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs rounded-xl shadow-xs shrink-0 flex items-center gap-1.5 transition-transform active:scale-95"
          >
            <RotateCcw class="w-3.5 h-3.5" />
            <span>Re-Evaluate Rules</span>
          </button>
        </div>

        <!-- Application Top Header -->
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-4 border-b border-slate-100">
          <div>
            <div class="flex flex-wrap items-center gap-2">
              <span class="text-xs font-mono font-bold bg-slate-100 text-slate-700 px-2.5 py-0.5 rounded">
                {{ app.scheme_code }}
              </span>
              <span class="text-xs text-indigo-700 font-semibold bg-indigo-50 px-2.5 py-0.5 rounded-full border border-indigo-100">
                {{ app.portal_name }}
              </span>
              <span class="text-[10px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full font-medium">
                User-Reported (Self-Managed)
              </span>
            </div>
            <h2 class="text-xl font-bold text-slate-900 mt-1.5">{{ app.scheme_name }}</h2>
            <div class="text-xs font-bold text-emerald-700 font-mono mt-0.5">{{ app.scheme_benefit }}</div>
          </div>

          <div class="flex items-center gap-2 shrink-0">
            <button
              v-if="app.status === 'REJECTED' || app.status === 'UNDER_REVIEW'"
              @click="openRejectionNavigator(app.scheme_code, app.notes)"
              class="px-3.5 py-2 bg-rose-50 hover:bg-rose-100 text-rose-800 border border-rose-200 text-xs font-bold rounded-xl flex items-center gap-1.5 transition-colors"
            >
              <RotateCcw class="w-3.5 h-3.5 text-rose-600" />
              <span>Diagnose Query</span>
            </button>

            <button
              @click="openEditModal(app)"
              class="px-3.5 py-2 border border-slate-300 hover:bg-slate-50 text-slate-700 text-xs font-semibold rounded-xl flex items-center gap-1.5 transition-colors"
            >
              <Edit2 class="w-3.5 h-3.5 text-slate-500" />
              <span>Record Reference & Date</span>
            </button>

            <a 
              :href="app.official_portal_url"
              target="_blank" 
              rel="noopener noreferrer"
              class="px-4 py-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 text-xs font-bold rounded-xl flex items-center gap-1.5 transition-colors"
            >
              <span>Open {{ app.portal_name }}</span>
              <ExternalLink class="w-3.5 h-3.5" />
            </a>
          </div>
        </div>

        <!-- Next Immediate Action Box -->
        <div class="p-4 rounded-2xl bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-300 flex items-start gap-3">
          <AlertCircle class="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
          <div class="space-y-0.5">
            <div class="text-xs font-bold text-amber-900 uppercase tracking-wider">Your Next Immediate Action:</div>
            <p class="text-sm font-bold text-amber-950">{{ app.next_immediate_action }}</p>
            <p class="text-xs text-amber-800">
              Handover of physical attested documents to your college scholarship clerk is mandatory under Maharashtra Government rules.
            </p>
          </div>
        </div>

        <!-- 7 Canonical Status Pipeline Buttons (Requirement 2) -->
        <div>
          <div class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 flex items-center justify-between">
            <span>Status Pipeline (Click to update milestone):</span>
            <span class="text-slate-400 font-normal">7 Canonical Stages</span>
          </div>
          <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2">
            <button
              v-for="stg in statuses"
              :key="stg.key"
              @click="quickAdvanceStatus(app, stg.key)"
              class="p-2.5 rounded-xl border text-xs font-bold transition-all text-center flex flex-col items-center justify-center gap-1"
              :class="app.status === stg.key 
                ? 'bg-indigo-600 text-white border-indigo-600 shadow-md ring-2 ring-indigo-300' 
                : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'"
            >
              <Check v-if="app.status === stg.key" class="w-3.5 h-3.5 text-white" />
              <span>{{ stg.label }}</span>
            </button>
          </div>
        </div>

        <!-- Application Metadata Strip (Requirement 3) -->
        <div class="pt-4 border-t border-slate-100 grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs text-slate-600">
          <div>
            <span class="text-slate-400 block text-[11px]">Application Reference:</span>
            <span class="font-mono font-bold text-slate-900 text-sm mt-0.5 block truncate">
              {{ app.application_reference_number || 'Pending Submission' }}
            </span>
          </div>

          <div>
            <span class="text-slate-400 block text-[11px]">Date Applied:</span>
            <span class="font-bold text-slate-800 text-sm mt-0.5 block">
              {{ app.applied_date ? new Date(app.applied_date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : 'Not yet applied' }}
            </span>
          </div>

          <div>
            <span class="text-slate-400 block text-[11px]">Submission Mode:</span>
            <span class="font-medium text-slate-800 text-xs mt-0.5 block">
              {{ app.submission_mode || 'Online Portal' }}
            </span>
          </div>

          <div>
            <span class="text-slate-400 block text-[11px]">Last Updated:</span>
            <span class="text-slate-600 text-xs mt-0.5 block">
              {{ new Date(app.updated_at).toLocaleDateString() }}
            </span>
          </div>
        </div>

        <div v-if="app.notes" class="text-xs text-slate-600 bg-slate-50 p-3 rounded-xl border border-slate-100">
          <strong>Student Notes:</strong> {{ app.notes }}
        </div>

      </div>
    </div>

    <!-- Empty State (Requirement 1) -->
    <div v-else class="text-center py-16 bg-white rounded-3xl border border-slate-200 p-8 shadow-xs space-y-4">
      <div class="w-14 h-14 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center mx-auto">
        <CheckCircle2 class="w-8 h-8" />
      </div>
      <div>
        <h2 class="text-xl font-bold text-slate-900">No Saved Applications in Your Tracker Yet</h2>
        <p class="text-xs text-slate-500 max-w-md mx-auto mt-1">
          Explore eligible scholarships under Step 3 and click "Save to Application Tracker" to generate your actionable milestone checklist.
        </p>
      </div>
      <router-link
        to="/schemes"
        class="inline-flex items-center gap-2 px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl text-sm transition-colors shadow-xs"
      >
        <span>Discover Matched Schemes</span>
        <ArrowRight class="w-4 h-4" />
      </router-link>
    </div>

    <!-- MODAL: EDIT APPLICATION REFERENCE & DATES (Requirement 3) -->
    <div v-if="isEditModalOpen" class="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div class="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 space-y-4">
        <div class="flex items-center justify-between pb-3 border-b border-slate-100">
          <div>
            <h2 class="text-base font-extrabold text-slate-900 flex items-center gap-2">
              <Edit2 class="w-4 h-4 text-indigo-600" />
              Update Tracker Record ({{ editingApp?.scheme_code }})
            </h2>
            <p class="text-xs text-slate-500">Record self-reported application reference, submission date, and notes.</p>
          </div>
          <button @click="isEditModalOpen = false" class="text-slate-400 hover:text-slate-600">
            <X class="w-5 h-5" />
          </button>
        </div>

        <form @submit.prevent="handleSaveDetails" class="space-y-4 text-xs">
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Status Milestone</label>
            <select v-model="editStatus" class="w-full px-3 py-2 border border-slate-300 rounded-xl bg-white font-bold">
              <option v-for="stg in statuses" :key="stg.key" :value="stg.key">{{ stg.label }}</option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block font-semibold text-slate-700 mb-1">Application Reference No.</label>
              <input
                v-model="editRefNo"
                type="text"
                placeholder="e.g. MHD-2024-889900"
                class="w-full px-3 py-2 border border-slate-300 rounded-xl font-mono"
              />
            </div>

            <div>
              <label class="block font-semibold text-slate-700 mb-1">Date Submitted / Applied</label>
              <input
                v-model="editAppliedDate"
                type="date"
                class="w-full px-3 py-2 border border-slate-300 rounded-xl font-mono"
              />
            </div>
          </div>

          <div>
            <label class="block font-semibold text-slate-700 mb-1">Submission Mode / Channel</label>
            <select v-model="editSubmissionMode" class="w-full px-3 py-2 border border-slate-300 rounded-xl bg-white">
              <option value="Online MahaDBT Portal">Online MahaDBT Portal</option>
              <option value="College Scholarship Clerk Desk">College Scholarship Clerk Desk</option>
              <option value="Aaple Sarkar Seva Kendra (Offline CSC)">Aaple Sarkar Seva Kendra (Offline CSC)</option>
              <option value="District Social Welfare Office">District Social Welfare Office</option>
            </select>
          </div>

          <div>
            <label class="block font-semibold text-slate-700 mb-1">Personal Follow-Up Notes</label>
            <textarea
              v-model="editNotes"
              rows="3"
              placeholder="e.g. Handover done to Clerk Mr. Deshmukh on 18th Nov. Awaiting principal signature."
              class="w-full px-3 py-2 border border-slate-300 rounded-xl"
            ></textarea>
          </div>

          <div class="p-3 rounded-xl bg-slate-50 border border-slate-200 text-[11px] text-slate-500">
            <strong>Notice:</strong> All statuses and dates saved here are for personal student follow-up. This tool does not claim or reflect official government sanction approval.
          </div>

          <div class="pt-3 border-t border-slate-100 flex items-center justify-end gap-2">
            <button
              type="button"
              @click="isEditModalOpen = false"
              class="px-4 py-2 border border-slate-300 rounded-xl text-slate-700 font-semibold"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="px-5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl shadow-xs"
            >
              Save Tracker Details
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Rejection Recovery & Grievance Navigator Modal -->
    <RejectionRecoveryModal
      :is-open="isRecoveryOpen"
      :scheme-code="recoverySchemeCode"
      :initial-rejection-remark="recoveryInitialRemark"
      @close="isRecoveryOpen = false"
    />

  </div>
</template>
