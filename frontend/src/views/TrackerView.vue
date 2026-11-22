<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useStudentStore } from '../stores/studentStore';
import PersonaBar from '../components/PersonaBar.vue';
import RejectionRecoveryModal from '../components/RejectionRecoveryModal.vue';
import LifecycleRoadmapModal from '../components/LifecycleRoadmapModal.vue';
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
  Check,
  MapPin,
  Bell,
  MessageSquare
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

// Entitlement Lifecycle Roadmap Modal state
const isLifecycleOpen = ref(false);
const lifecycleSchemeCode = ref('');
const lifecycleSchemeName = ref('');

function openLifecycleRoadmap(schemeCode: string, schemeName: string) {
  lifecycleSchemeCode.value = schemeCode;
  lifecycleSchemeName.value = schemeName;
  isLifecycleOpen.value = true;
}

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
        <div class="inline-flex items-center gap-2 mb-1.5">
          <span class="neo-stamp neo-stamp-navy text-[10px]">
            <CheckCircle2 class="w-3 h-3 text-emerald-400" />
            Milestone Follow-Up Log
          </span>
          <span class="text-xs text-slate-500 font-mono">Stage 5 of 5</span>
        </div>
        <h1 class="text-2xl sm:text-3xl font-extrabold text-[#0B132B] tracking-tight">
          My Saved Applications & Milestone Tracker
        </h1>
        <p class="text-xs sm:text-sm text-slate-600 mt-1 max-w-3xl font-medium">
          Track your progress across self-reported offline and online milestones (from Aaple Sarkar certificate procurement to MahaDBT College Clerk submission).
        </p>
      </div>

      <router-link
        to="/schemes"
        class="neo-btn neo-btn-navy px-4 py-2.5 text-xs sm:text-sm font-bold shrink-0 self-start md:self-auto"
      >
        <span>Discover & Save Schemes</span>
        <ArrowRight class="w-4 h-4" />
      </router-link>
    </div>

    <!-- MANDATORY LEGAL / USER-REPORTED NOTICE (Requirements 4 & 5) -->
    <div class="p-4 rounded-xl border-[1.5px] border-[#0B132B] bg-[#FFFBEB] text-amber-950 text-xs sm:text-sm font-medium flex items-start gap-3 shadow-[2px_2px_0_0_#0B132B]">
      <Info class="w-5 h-5 text-amber-800 shrink-0 mt-0.5" />
      <div>
        <strong class="font-bold block text-amber-950 mb-0.5">User-Reported Application Status Notice (Self-Managed):</strong>
        <span class="text-amber-900 font-medium">"This tracker is a personal planning and document-readiness log. YOJNAVIA does not integrate with internal government sanction databases and does not claim official departmental application status. All milestone stages, application dates, and reference numbers are user-reported."</span>
      </div>
    </div>

    <!-- REJECTION RECOVERY & GRIEVANCE NAVIGATOR BANNER -->
    <div class="neo-box p-4 bg-[#FFF1F2] text-rose-950 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
      <div class="flex items-start gap-3">
        <div class="p-2 bg-rose-200 rounded-lg border border-[#0B132B] text-rose-900 shrink-0 mt-0.5 shadow-[1.5px_1.5px_0_0_#0B132B]">
          <RotateCcw class="w-5 h-5" />
        </div>
        <div>
          <div class="font-extrabold text-[#0B132B] text-sm flex items-center gap-2">
            <span>MahaDBT Scrutiny Query or Application Rejected?</span>
            <span class="neo-stamp neo-stamp-rose text-[9px]">15-Day Resubmission Window</span>
          </div>
          <p class="text-xs text-rose-900 mt-0.5 font-medium">
            Translate confusing scrutiny remarks into plain language, verify your 15-day resubmission window, and discover verified statutory appeal routes under the Maharashtra RTS Act 2015.
          </p>
        </div>
      </div>
      <button 
        @click="openRejectionNavigator()" 
        class="neo-btn neo-btn-rose px-4 py-2 text-xs font-bold shrink-0 self-start sm:self-auto"
      >
        <span>Launch Rejection Navigator</span>
        <ArrowRight class="w-3.5 h-3.5" />
      </button>
    </div>

    <!-- WHATSAPP & SMS DEADLINE REMINDERS BANNER -->
    <div class="neo-box p-4 bg-[#ECFDF5] text-emerald-950 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
      <div class="flex items-start gap-3">
        <div class="p-2 bg-emerald-200 rounded-lg border border-[#0B132B] text-emerald-900 shrink-0 mt-0.5 shadow-[1.5px_1.5px_0_0_#0B132B]">
          <Bell class="w-5 h-5" />
        </div>
        <div>
          <div class="font-extrabold text-[#0B132B] text-sm flex items-center gap-2">
            <span>Automated WhatsApp & SMS Deadline Reminders</span>
            <span class="neo-stamp neo-stamp-emerald text-[9px]">Consent-Driven</span>
          </div>
          <p class="text-xs text-emerald-900 mt-0.5 font-medium">
            Receive verified portal cutoff alerts (7d/2d/0d), missing document SLA warnings, 15-day scrutiny resubmission clocks, and annual March 31 renewals directly to WhatsApp or SMS.
          </p>
        </div>
      </div>
      <router-link 
        to="/notifications" 
        class="neo-btn neo-btn-emerald px-4 py-2 text-xs font-bold shrink-0 self-start sm:self-auto"
      >
        <MessageSquare class="w-3.5 h-3.5" />
        <span>Manage Notification Alerts</span>
        <ArrowRight class="w-3.5 h-3.5" />
      </router-link>
    </div>

    <!-- Active Tracked Applications -->
    <div v-if="store.trackedApplications.length > 0" class="space-y-6">
      <div 
        v-for="app in store.trackedApplications" 
        :key="app.id"
        class="neo-box p-6 sm:p-7 overflow-hidden space-y-5 bg-white"
      >
        <!-- RULE CHANGE ALERT (Rule Change Handling 2, 3, 4) -->
        <div 
          v-if="app.needs_re_evaluation" 
          class="p-4 rounded-xl border-[1.5px] border-[#0B132B] bg-amber-50 text-amber-950 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-[2px_2px_0_0_#0B132B] animate-in fade-in"
        >
          <div class="flex items-start gap-3">
            <AlertTriangle class="w-5 h-5 text-amber-700 shrink-0 mt-0.5" />
            <div>
              <div class="font-bold text-amber-950 text-xs uppercase tracking-wider flex items-center gap-1.5">
                <span>Statutory Eligibility Rule Revision Detected</span>
                <span class="neo-stamp neo-stamp-amber text-[9px]">Action Needed</span>
              </div>
              <p class="text-xs text-amber-900 mt-1 font-medium">
                {{ app.re_evaluation_reason || 'Eligibility criteria for this scheme were recently updated by the department.' }}
              </p>
            </div>
          </div>
          <button
            @click="handleReEvaluateApp(app.scheme_code)"
            class="neo-btn neo-btn-saffron px-4 py-2 text-xs font-bold shrink-0"
          >
            <RotateCcw class="w-3.5 h-3.5" />
            <span>Re-Evaluate Rules</span>
          </button>
        </div>

        <!-- Application Top Header -->
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-4 border-b-[1.5px] border-[#0B132B]/15">
          <div>
            <div class="flex flex-wrap items-center gap-2">
              <span class="neo-stamp neo-stamp-navy font-mono text-[10px]">
                {{ app.scheme_code }}
              </span>
              <span class="neo-stamp text-[10px] bg-indigo-50 text-indigo-900">
                {{ app.portal_name }}
              </span>
              <span class="text-[10px] bg-[#F5F5F3] text-slate-700 px-2 py-0.5 rounded border border-[#0B132B]/20 font-bold">
                User-Reported (Self-Managed)
              </span>
            </div>
            <h2 class="text-xl font-extrabold text-[#0B132B] mt-1.5">{{ app.scheme_name }}</h2>
            <div class="text-xs font-extrabold text-emerald-800 font-mono mt-0.5">{{ app.scheme_benefit }}</div>
          </div>

          <div class="flex flex-wrap items-center gap-2 shrink-0">
            <button
              @click="openLifecycleRoadmap(app.scheme_code, app.scheme_name)"
              class="neo-btn neo-btn-paper px-3.5 py-2 text-xs font-bold text-[#0B132B]"
            >
              <MapPin class="w-3.5 h-3.5 text-amber-600" />
              <span>Lifecycle Roadmap 🗺️</span>
            </button>

            <button
              v-if="app.status === 'REJECTED' || app.status === 'UNDER_REVIEW'"
              @click="openRejectionNavigator(app.scheme_code, app.notes)"
              class="neo-btn neo-btn-rose px-3.5 py-2 text-xs font-bold"
            >
              <RotateCcw class="w-3.5 h-3.5" />
              <span>Diagnose Query</span>
            </button>

            <button
              @click="openEditModal(app)"
              class="neo-btn neo-btn-paper px-3.5 py-2 text-xs font-bold text-[#0B132B]"
            >
              <Edit2 class="w-3.5 h-3.5 text-slate-600" />
              <span>Record Ref & Date</span>
            </button>

            <a 
              :href="app.official_portal_url"
              target="_blank" 
              rel="noopener noreferrer"
              class="neo-btn neo-btn-navy px-4 py-2 text-xs font-bold"
            >
              <span>Open {{ app.portal_name }}</span>
              <ExternalLink class="w-3.5 h-3.5" />
            </a>
          </div>
        </div>

        <!-- Next Immediate Action Box -->
        <div class="p-4 rounded-xl border-[1.5px] border-[#0B132B] bg-[#FFFBEB] text-amber-950 flex items-start gap-3 shadow-[2px_2px_0_0_#0B132B]">
          <AlertCircle class="w-5 h-5 text-amber-700 shrink-0 mt-0.5" />
          <div class="space-y-0.5">
            <div class="text-xs font-bold text-amber-950 uppercase tracking-wider">Your Next Immediate Action:</div>
            <p class="text-sm font-extrabold text-[#0B132B]">{{ app.next_immediate_action }}</p>
            <p class="text-xs text-amber-900 font-medium">
              Handover of physical attested documents to your college scholarship clerk is mandatory under Maharashtra Government rules.
            </p>
          </div>
        </div>

        <!-- 7 Canonical Status Pipeline Buttons (Requirement 2) -->
        <div>
          <div class="text-xs font-bold text-[#0B132B] uppercase tracking-wider mb-2 flex items-center justify-between">
            <span>Status Pipeline (Click to advance milestone):</span>
            <span class="text-slate-500 font-mono text-[11px]">7 Canonical Stages</span>
          </div>
          <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2">
            <button
              v-for="stg in statuses"
              :key="stg.key"
              @click="quickAdvanceStatus(app, stg.key)"
              class="p-2.5 rounded-xl border-[1.5px] border-[#0B132B] text-xs font-bold transition-all text-center flex flex-col items-center justify-center gap-1 cursor-pointer"
              :class="app.status === stg.key 
                ? 'bg-[#0B132B] text-white shadow-[2px_2px_0_0_#D97706] ring-2 ring-amber-500 translate-y-[-1px]' 
                : 'bg-white text-slate-700 hover:bg-slate-50 shadow-[1.5px_1.5px_0_0_#0B132B]'"
            >
              <Check v-if="app.status === stg.key" class="w-3.5 h-3.5 text-amber-400" />
              <span>{{ stg.label }}</span>
            </button>
          </div>
        </div>

        <!-- Application Metadata Strip (Requirement 3) -->
        <div class="pt-4 border-t-[1.5px] border-[#0B132B]/10 grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs text-slate-600">
          <div>
            <span class="text-slate-500 block text-[11px] font-bold">Application Reference:</span>
            <span class="font-mono font-bold text-[#0B132B] text-sm mt-0.5 block truncate">
              {{ app.application_reference_number || 'Pending Submission' }}
            </span>
          </div>

          <div>
            <span class="text-slate-500 block text-[11px] font-bold">Date Applied:</span>
            <span class="font-bold text-[#0B132B] text-sm mt-0.5 block">
              {{ app.applied_date ? new Date(app.applied_date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : 'Not yet applied' }}
            </span>
          </div>

          <div>
            <span class="text-slate-500 block text-[11px] font-bold">Submission Mode:</span>
            <span class="font-semibold text-slate-800 text-xs mt-0.5 block">
              {{ app.submission_mode || 'Online Portal' }}
            </span>
          </div>

          <div>
            <span class="text-slate-500 block text-[11px] font-bold">Last Updated:</span>
            <span class="text-slate-700 text-xs mt-0.5 block font-mono">
              {{ new Date(app.updated_at).toLocaleDateString() }}
            </span>
          </div>
        </div>

        <div v-if="app.notes" class="text-xs text-slate-700 bg-[#FBFBFA] p-3 rounded-xl border-[1.5px] border-[#0B132B]/20 font-medium">
          <strong class="text-[#0B132B]">Student Notes:</strong> {{ app.notes }}
        </div>

      </div>
    </div>

    <!-- Empty State (Requirement 1) -->
    <div v-else class="neo-box text-center py-16 p-8 space-y-4 bg-white">
      <div class="w-14 h-14 rounded-2xl bg-amber-50 border-[1.5px] border-[#0B132B] text-amber-700 flex items-center justify-center mx-auto shadow-[2px_2px_0_0_#0B132B]">
        <CheckCircle2 class="w-8 h-8" />
      </div>
      <div>
        <h2 class="text-xl font-extrabold text-[#0B132B] font-heading">No Saved Applications in Your Tracker Yet</h2>
        <p class="text-xs text-slate-600 max-w-md mx-auto mt-1 font-medium">
          Explore eligible scholarships under Step 3 and click "Save to Application Tracker" to generate your actionable milestone checklist.
        </p>
      </div>
      <router-link
        to="/schemes"
        class="neo-btn neo-btn-saffron px-6 py-3 text-sm font-bold"
      >
        <span>Discover Matched Schemes</span>
        <ArrowRight class="w-4 h-4" />
      </router-link>
    </div>

    <!-- MODAL: EDIT APPLICATION REFERENCE & DATES (Requirement 3) -->
    <div v-if="isEditModalOpen" class="fixed inset-0 z-50 bg-[#0B132B]/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div class="neo-box bg-white max-w-lg w-full p-6 shadow-[5px_5px_0_0_#0B132B] space-y-4">
        <div class="flex items-center justify-between pb-3 border-b-[1.5px] border-[#0B132B]/15">
          <div>
            <h2 class="text-base font-extrabold text-[#0B132B] flex items-center gap-2 font-heading">
              <Edit2 class="w-4 h-4 text-amber-600" />
              Update Tracker Record ({{ editingApp?.scheme_code }})
            </h2>
            <p class="text-xs text-slate-500 font-medium">Record self-reported application reference, submission date, and notes.</p>
          </div>
          <button @click="isEditModalOpen = false" class="text-slate-400 hover:text-slate-700 p-1 font-bold">
            <X class="w-5 h-5" />
          </button>
        </div>

        <form @submit.prevent="handleSaveDetails" class="space-y-4 text-xs">
          <div>
            <label class="block font-bold text-[#0B132B] mb-1">Status Milestone</label>
            <select v-model="editStatus" class="neo-input w-full px-3 py-2 bg-white font-bold text-xs">
              <option v-for="stg in statuses" :key="stg.key" :value="stg.key">{{ stg.label }}</option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block font-bold text-[#0B132B] mb-1">Application Reference No.</label>
              <input
                v-model="editRefNo"
                type="text"
                placeholder="e.g. MHD-2024-889900"
                class="neo-input w-full px-3 py-2 font-mono text-xs"
              />
            </div>

            <div>
              <label class="block font-bold text-[#0B132B] mb-1">Date Submitted / Applied</label>
              <input
                v-model="editAppliedDate"
                type="date"
                class="neo-input w-full px-3 py-2 font-mono text-xs"
              />
            </div>
          </div>

          <div>
            <label class="block font-bold text-[#0B132B] mb-1">Submission Mode / Channel</label>
            <select v-model="editSubmissionMode" class="neo-input w-full px-3 py-2 bg-white text-xs font-medium">
              <option value="Online MahaDBT Portal">Online MahaDBT Portal</option>
              <option value="College Scholarship Clerk Desk">College Scholarship Clerk Desk</option>
              <option value="Aaple Sarkar Seva Kendra (Offline CSC)">Aaple Sarkar Seva Kendra (Offline CSC)</option>
              <option value="District Social Welfare Office">District Social Welfare Office</option>
            </select>
          </div>

          <div>
            <label class="block font-bold text-[#0B132B] mb-1">Personal Follow-Up Notes</label>
            <textarea
              v-model="editNotes"
              rows="3"
              placeholder="e.g. Handover done to Clerk Mr. Deshmukh on 18th Nov. Awaiting principal signature."
              class="neo-input w-full px-3 py-2 text-xs"
            ></textarea>
          </div>

          <div class="p-3 rounded-xl border border-[#0B132B]/20 bg-[#FBFBFA] text-[11px] text-slate-600 font-medium">
            <strong class="text-[#0B132B]">Notice:</strong> All statuses and dates saved here are for personal student follow-up. This tool does not claim or reflect official government sanction approval.
          </div>

          <div class="pt-3 border-t-[1.5px] border-[#0B132B]/15 flex items-center justify-end gap-2">
            <button
              type="button"
              @click="isEditModalOpen = false"
              class="neo-btn neo-btn-paper px-4 py-2 text-xs font-bold text-[#0B132B]"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="neo-btn neo-btn-saffron px-5 py-2 text-xs font-bold"
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

    <!-- Entitlement Lifecycle Roadmap Modal -->
    <LifecycleRoadmapModal
      :is-open="isLifecycleOpen"
      :scheme-code="lifecycleSchemeCode"
      :scheme-name="lifecycleSchemeName"
      @close="isLifecycleOpen = false"
    />

  </div>
</template>
