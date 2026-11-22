<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useStudentStore } from '../stores/studentStore';
import PersonaBar from '../components/PersonaBar.vue';
import { 
  Send, 
  Sparkles, 
  Bot, 
  User, 
  ArrowRight, 
  ShieldCheck, 
  Cpu, 
  AlertCircle,
  RotateCcw,
  Edit3,
  X,
  Lock,
  Award,
  CheckCircle2
} from '@lucide/vue';

const store = useStudentStore();
const router = useRouter();
const inputMessage = ref('');

// Edit field modal state
const isEditModalOpen = ref(false);
const editingFieldKey = ref('age');
const editingFieldValue = ref<any>('');

const samplePrompts = [
  "I am 21, from Sangli, Maharashtra, studying B.Tech Mechanical Engineering, and my family's annual income is around ₹1.2 Lakhs.",
  "I am an OBC student from Nashik in MCA. Our annual household income is ₹2.1 Lakhs, staying in a rented hostel.",
  "I am an SC student from Solapur doing Civil Diploma. Family income is ₹65,000 per year.",
  "I am an Open category girl student from Pune studying B.Pharm. Family income is ₹3.5 Lakhs, admitted via CAP round."
];

const fieldLabels: Record<string, string> = {
  age: "Age",
  state: "State",
  district: "District",
  occupation: "Occupation",
  education_level: "Education Level",
  income_band: "Annual Household Income Band",
  social_category: "Social Category (Volunteered)",
  disability_status: "Disability Status (Volunteered)",
  family_members: "Family Members"
};

const incomeBandOptions = [
  { value: "below_1_lakh", label: "Below ₹1 Lakh" },
  { value: "1_to_2_5_lakh", label: "₹1 – 2.5 Lakh" },
  { value: "2_5_to_5_lakh", label: "₹2.5 – 5 Lakh" },
  { value: "5_to_8_lakh", label: "₹5 – 8 Lakh" },
  { value: "above_8_lakh", label: "Above ₹8 Lakh" },
];

const educationOptions = [
  { value: "undergraduate", label: "Undergraduate (B.Tech / B.Sc / BA / B.Com)" },
  { value: "postgraduate", label: "Postgraduate (MCA / M.Tech / MBA / M.Sc)" },
  { value: "diploma", label: "Polytechnic Diploma" },
  { value: "12th_pass", label: "12th Pass / Junior College" },
  { value: "10th_pass", label: "10th Pass" },
  { value: "doctorate", label: "Doctorate (Ph.D)" },
  { value: "other", label: "Other" }
];

const socialCategoryOptions = [
  { value: "general", label: "General / Open" },
  { value: "obc", label: "Other Backward Class (OBC)" },
  { value: "sc", label: "Scheduled Caste (SC)" },
  { value: "st", label: "Scheduled Tribe (ST)" },
  { value: "ews", label: "Economically Weaker Section (EWS)" },
  { value: "vjnt", label: "VJNT (Vimukta Jati & Nomadic Tribes)" },
  { value: "sbc", label: "Special Backward Class (SBC)" },
  { value: "prefer_not_to_say", label: "Prefer Not to Say" }
];

const progressPercentage = computed(() => {
  const total = store.intakeState?.total_count || 1;
  const known = store.intakeState?.known_count || 0;
  return Math.min(100, Math.round((known / total) * 100));
});

const isEligibilityReady = computed(() => {
  return store.nextQuestion === null && (store.evaluatedSchemes.length > 0 || store.evaluationSummary !== null);
});

async function handleSendMessage() {
  if (!inputMessage.value.trim() || store.isLoading) return;
  const msg = inputMessage.value;
  inputMessage.value = '';
  await store.sendIntakeMessage(msg);
}

function handleUsePrompt(prompt: string) {
  inputMessage.value = prompt;
}

function handleSendChip(chipText: string) {
  store.sendIntakeMessage(chipText);
}

function openEditModal(fieldKey: string) {
  editingFieldKey.value = fieldKey;
  const currentVal = store.intakeState?.fields?.[fieldKey]?.value;
  editingFieldValue.value = currentVal !== null && currentVal !== undefined ? currentVal : '';
  isEditModalOpen.value = true;
}

watch(editingFieldKey, (newKey) => {
  const currentVal = store.intakeState?.fields?.[newKey]?.value;
  editingFieldValue.value = currentVal !== null && currentVal !== undefined ? currentVal : '';
});

async function handleSaveCorrection() {
  if (editingFieldValue.value === '' || editingFieldValue.value === null) return;
  let val = editingFieldValue.value;
  if (editingFieldKey.value === 'age') {
    val = parseInt(val, 10);
  } else if (editingFieldKey.value === 'disability_status') {
    val = val === 'true' || val === true;
  }
  await store.correctIntakeField(editingFieldKey.value, val);
  isEditModalOpen.value = false;
}

async function handleRestart() {
  if (confirm("Restart conversational discovery? All conversation turns will be reset.")) {
    await store.restartIntake();
  }
}

function proceedToSchemes() {
  router.push('/schemes');
}

function formatFieldValue(key: string, value: any): string {
  if (value === null || value === undefined || value === '') return 'Not provided';
  if (key === 'income_band') {
    const found = incomeBandOptions.find(o => o.value === value);
    return found ? found.label : String(value);
  }
  if (key === 'education_level') {
    const found = educationOptions.find(o => o.value === value);
    return found ? found.label : String(value);
  }
  if (key === 'social_category') {
    const found = socialCategoryOptions.find(o => o.value === value);
    return found ? found.label : String(value);
  }
  if (typeof value === 'boolean') {
    return value ? 'Yes' : 'No';
  }
  if (key === 'family_members' && Array.isArray(value)) {
    return `${value.length} member(s)`;
  }
  return String(value);
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <!-- Demo Persona Bar -->
    <PersonaBar />

    <!-- Hero Header -->
    <div class="text-center max-w-2xl mx-auto mb-5">
      <h1 class="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
        Discover Government Schemes & Scholarships
      </h1>
      <p class="text-slate-600 text-sm mt-1.5">
        Tell us about your education and family background, or select a demo profile above to discover what you qualify for.
      </p>
    </div>

    <!-- Intake Progress Indicator Bar -->
    <div class="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-3.5 mb-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 rounded-xl bg-indigo-50 text-indigo-700 flex items-center justify-center font-bold text-xs shrink-0">
          {{ progressPercentage }}%
        </div>
        <div>
          <div class="text-xs font-semibold text-slate-800">
            Profile Completion: <span class="text-indigo-600 font-bold">{{ store.intakeState?.known_count || 0 }}</span> of <span class="text-slate-600">{{ store.intakeState?.total_count || 1 }}</span> key details
          </div>
          <div class="w-36 sm:w-48 bg-slate-100 rounded-full h-1.5 overflow-hidden mt-1">
            <div 
              class="bg-indigo-600 h-1.5 rounded-full transition-all duration-500"
              :style="{ width: `${progressPercentage}%` }"
            ></div>
          </div>
        </div>
      </div>
      
      <div class="flex items-center gap-2 self-end sm:self-auto">
        <span 
          class="text-xs font-medium px-2.5 py-1 rounded-full border inline-flex items-center gap-1.5"
          :class="isEligibilityReady ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-slate-50 text-slate-600 border-slate-200'"
        >
          <span class="w-1.5 h-1.5 rounded-full" :class="isEligibilityReady ? 'bg-emerald-500' : 'bg-indigo-500 animate-pulse'"></span>
          {{ isEligibilityReady ? 'Ready for Matching' : 'Gathering Details' }}
        </span>
        <button
          @click="handleRestart"
          title="Reset conversation"
          class="inline-flex items-center gap-1 text-xs text-slate-500 hover:text-rose-600 border border-slate-200 hover:border-rose-200 px-2.5 py-1 rounded-lg transition-colors bg-white shadow-xs"
        >
          <RotateCcw class="w-3 h-3" />
          <span>Reset</span>
        </button>
      </div>
    </div>

    <!-- Eligibility Ready Notification Bar -->
    <div 
      v-if="isEligibilityReady"
      class="mb-5 bg-gradient-to-r from-emerald-600 to-teal-700 rounded-2xl px-5 py-3.5 text-white shadow-sm flex flex-col sm:flex-row items-center justify-between gap-3 animate-in fade-in"
    >
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-xl bg-white/20 flex items-center justify-center shrink-0">
          <Award class="w-5 h-5 text-white" />
        </div>
        <div>
          <div class="text-sm font-bold">
            Matching complete! {{ store.evaluationSummary?.likely_eligible || 0 }} eligible scholarships found
          </div>
          <div class="text-xs text-emerald-100">
            Based on official Maharashtra government resolution rules
          </div>
        </div>
      </div>
      <button
        @click="proceedToSchemes"
        class="px-4 py-2 bg-white text-emerald-800 hover:bg-emerald-50 font-bold rounded-xl text-xs sm:text-sm flex items-center gap-1.5 shadow-sm transition-all shrink-0"
      >
        <span>View Matched Schemes</span>
        <ArrowRight class="w-4 h-4" />
      </button>
    </div>

    <!-- Main Grid: Conversational Chat Interface (7 cols) & Extracted Profile (5 cols) -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
      
      <!-- Conversational Chat Interface -->
      <div class="lg:col-span-7 bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col h-[520px] sm:h-[640px] overflow-hidden">
        
        <!-- Chat Header -->
        <div class="px-4 py-3 bg-slate-50/80 border-b border-slate-200 flex items-center justify-between">
          <div class="flex items-center gap-2.5">
            <div class="w-8 h-8 rounded-xl bg-indigo-600 text-white flex items-center justify-center shadow-xs">
              <Bot class="w-4 h-4" />
            </div>
            <div>
              <div class="text-sm font-bold text-slate-900">YojnaVia Assistant</div>
              <div class="text-[11px] text-emerald-600 flex items-center gap-1 font-medium">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                Official Maharashtra Scheme Guide
              </div>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs text-slate-500 inline-flex items-center gap-1 bg-white border border-slate-200 px-2.5 py-1 rounded-full shadow-xs">
              <Lock class="w-3 h-3 text-emerald-600" />
              <span>Safe Demo • No Aadhaar</span>
            </span>
          </div>
        </div>

        <!-- Chat Messages Area -->
        <div class="flex-1 p-4 overflow-y-auto space-y-3.5">
          <div 
            v-for="(msg, index) in store.chatMessages" 
            :key="index"
            class="flex items-start gap-3"
            :class="msg.sender === 'user' ? 'flex-row-reverse' : ''"
          >
            <div 
              class="w-7 h-7 rounded-full flex items-center justify-center shrink-0 text-white text-xs font-bold"
              :class="msg.sender === 'user' ? 'bg-indigo-600' : (msg.isSensitiveRefusal ? 'bg-amber-600' : 'bg-slate-800')"
            >
              <User v-if="msg.sender === 'user'" class="w-3.5 h-3.5" />
              <ShieldCheck v-else-if="msg.isSensitiveRefusal" class="w-3.5 h-3.5" />
              <Bot v-else class="w-3.5 h-3.5" />
            </div>

            <div 
              class="max-w-[85%] rounded-2xl p-3.5 text-sm shadow-xs"
              :class="msg.sender === 'user' 
                ? 'bg-indigo-600 text-white rounded-tr-xs' 
                : (msg.isSensitiveRefusal 
                    ? 'bg-amber-50 text-amber-900 border border-amber-200 rounded-tl-xs'
                    : 'bg-slate-100 text-slate-900 rounded-tl-xs border border-slate-200/80')"
            >
              <p class="leading-relaxed whitespace-pre-line">{{ msg.text }}</p>

              <!-- Optional Error Banner if extraction failed or timed out -->
              <div v-if="msg.error" class="mt-2 text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded p-1.5 flex items-center gap-1.5">
                <AlertCircle class="w-3.5 h-3.5 text-amber-600 shrink-0" />
                <span>{{ msg.error }}</span>
              </div>
            </div>
          </div>

          <!-- Typing Indicator -->
          <div v-if="store.isLoading" class="flex items-center gap-2 text-slate-500 text-xs italic pl-10 py-1">
            <span class="w-2 h-2 rounded-full bg-indigo-600 animate-ping"></span>
            <span>Checking your details against Maharashtra scheme criteria...</span>
          </div>
        </div>

        <!-- Suggested Answers Chips (Dynamic from Next Question) -->
        <div 
          v-if="store.nextQuestion && store.nextQuestion.suggested_answers && store.nextQuestion.suggested_answers.length > 0"
          class="px-4 py-2.5 bg-indigo-50/70 border-t border-indigo-100"
        >
          <div class="text-[11px] font-bold text-indigo-900 mb-1.5 flex items-center gap-1">
            <Sparkles class="w-3 h-3 text-indigo-600" />
            Suggested Quick Answers:
          </div>
          <div class="flex flex-wrap gap-1.5">
            <button
              v-for="(chip, chipIdx) in store.nextQuestion.suggested_answers"
              :key="chipIdx"
              @click="handleSendChip(chip)"
              class="text-xs bg-white hover:bg-indigo-600 hover:text-white border border-indigo-200 text-indigo-800 font-medium px-3 py-1 rounded-full transition-colors shadow-xs"
            >
              {{ chip }}
            </button>
          </div>
        </div>

        <!-- Starter Prompt Suggestions (When chat just started) -->
        <div 
          v-else-if="store.chatMessages.length <= 2"
          class="px-4 py-2 bg-slate-50 border-t border-slate-200 overflow-x-auto whitespace-nowrap scrollbar-none flex gap-2"
        >
          <button
            v-for="(sp, idx) in samplePrompts"
            :key="idx"
            @click="handleUsePrompt(sp)"
            class="text-[11px] bg-white border border-slate-200 hover:border-indigo-400 hover:text-indigo-700 px-3 py-1 rounded-full text-slate-600 transition-colors shrink-0"
          >
            "{{ sp.substring(0, 36) }}..."
          </button>
        </div>

        <!-- Chat Input Form -->
        <form @submit.prevent="handleSendMessage" class="p-3 bg-white border-t border-slate-200 flex items-center gap-2">
          <input
            v-model="inputMessage"
            type="text"
            placeholder="Describe your age, college, location, income or caste..."
            class="flex-1 text-sm px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          />
          <button
            type="submit"
            :disabled="!inputMessage.trim() || store.isLoading"
            class="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-xl font-medium text-sm flex items-center gap-1.5 transition-colors shadow-xs shrink-0"
          >
            <span>Send</span>
            <Send class="w-4 h-4" />
          </button>
        </form>
      </div>

      <!-- Real-Time Extracted Profile State & Action Card (5 cols) -->
      <div class="lg:col-span-5 space-y-4">
        <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-5">
          <div class="flex items-center justify-between pb-3 border-b border-slate-100">
            <div>
              <h2 class="text-sm sm:text-base font-bold text-slate-900">Your Profile Summary</h2>
              <p class="text-xs text-slate-500">Details used to match your eligible schemes</p>
            </div>
            <span 
              class="text-xs font-semibold px-2.5 py-0.5 rounded-full border flex items-center gap-1"
              :class="isEligibilityReady ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-slate-50 text-slate-600 border-slate-200'"
            >
              <CheckCircle2 v-if="isEligibilityReady" class="w-3.5 h-3.5 text-emerald-600" />
              <Cpu v-else class="w-3.5 h-3.5 text-indigo-600" />
              {{ store.intakeState?.known_count || 0 }} Confirmed
            </span>
          </div>

          <!-- Structured Fields List -->
          <div class="divide-y divide-slate-100 text-sm mt-1 max-h-[460px] overflow-y-auto pr-1">
            <div 
              v-for="(label, key) in fieldLabels" 
              :key="key"
              class="py-2.5 flex items-start justify-between gap-2"
            >
              <div class="flex-1 min-w-0">
                <div class="text-[11px] text-slate-500 font-medium">{{ label }}</div>
                <div class="font-semibold text-slate-900 text-sm flex items-center gap-1.5 mt-0.5">
                  <span class="truncate">{{ formatFieldValue(key, store.intakeState?.fields?.[key]?.value) }}</span>
                  
                  <!-- Clean Status Badges -->
                  <span 
                    v-if="store.intakeState?.fields?.[key]?.status === 'known'" 
                    class="text-[10px] font-semibold px-1.5 py-0.2 rounded border bg-emerald-50 text-emerald-700 border-emerald-200"
                  >
                    Saved
                  </span>
                  <span 
                    v-else
                    class="text-[11px] text-slate-400 font-normal italic"
                  >
                    Not provided yet
                  </span>
                </div>
              </div>

              <!-- Inline Edit Button -->
              <button
                @click="openEditModal(key)"
                class="p-1 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-md transition-colors mt-1"
                title="Edit this detail"
              >
                <Edit3 class="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          <!-- Action Buttons Area -->
          <div class="mt-4 pt-3.5 border-t border-slate-100 space-y-2">
            <button
              @click="proceedToSchemes"
              class="w-full py-2.5 px-4 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl shadow-xs flex items-center justify-center gap-2 transition-all text-sm"
            >
              <span>View Recommended Schemes</span>
              <ArrowRight class="w-4 h-4" />
            </button>
            <p class="text-[11px] text-center text-slate-500">
              Matches official Maharashtra Government criteria.
            </p>
          </div>
        </div>

        <!-- Privacy & Safety Note -->
        <div class="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-600 flex items-start gap-2.5">
          <ShieldCheck class="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
          <div class="space-y-1">
            <div class="font-bold text-slate-800">Safety & Privacy Guarantee</div>
            <p class="text-slate-500 leading-normal">
              This prototype evaluates sample profiles. Never enter your Aadhaar number or confidential financial passwords. Official applications take place directly on the MahaDBT government portal.
            </p>
          </div>
        </div>

      </div>

    </div>

    <!-- Edit / Correction Modal -->
    <div 
      v-if="isEditModalOpen"
      class="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4 animate-in fade-in"
    >
      <div class="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-slate-200">
        <div class="flex items-center justify-between pb-3 border-b border-slate-100">
          <div class="flex items-center gap-2 font-bold text-slate-900 text-base">
            <Edit3 class="w-4 h-4 text-indigo-600" />
            Edit / Correct Parameter
          </div>
          <button 
            @click="isEditModalOpen = false"
            class="text-slate-400 hover:text-slate-600 p-1 rounded-lg"
          >
            <X class="w-4 h-4" />
          </button>
        </div>

        <form @submit.prevent="handleSaveCorrection" class="space-y-4 mt-4">
          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">
              Field to Update:
            </label>
            <select 
              v-model="editingFieldKey"
              class="w-full text-sm border border-slate-300 rounded-xl px-3 py-2 bg-slate-50 text-slate-800 font-medium"
            >
              <option v-for="(lbl, k) in fieldLabels" :key="k" :value="k">
                {{ lbl }}
              </option>
            </select>
          </div>

          <!-- Dynamic Input Based on Field Type -->
          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">
              Corrected Value:
            </label>

            <!-- Age Input -->
            <input 
              v-if="editingFieldKey === 'age'"
              v-model.number="editingFieldValue"
              type="number"
              min="0"
              max="120"
              placeholder="e.g. 21"
              class="w-full text-sm border border-slate-300 rounded-xl px-3.5 py-2 focus:ring-2 focus:ring-indigo-500"
              required
            />

            <!-- Income Band Input -->
            <select 
              v-else-if="editingFieldKey === 'income_band'"
              v-model="editingFieldValue"
              class="w-full text-sm border border-slate-300 rounded-xl px-3.5 py-2 focus:ring-2 focus:ring-indigo-500"
              required
            >
              <option value="" disabled>Select Annual Income Band</option>
              <option v-for="opt in incomeBandOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>

            <!-- Education Level Input -->
            <select 
              v-else-if="editingFieldKey === 'education_level'"
              v-model="editingFieldValue"
              class="w-full text-sm border border-slate-300 rounded-xl px-3.5 py-2 focus:ring-2 focus:ring-indigo-500"
              required
            >
              <option value="" disabled>Select Education Level</option>
              <option v-for="opt in educationOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>

            <!-- Social Category Input -->
            <select 
              v-else-if="editingFieldKey === 'social_category'"
              v-model="editingFieldValue"
              class="w-full text-sm border border-slate-300 rounded-xl px-3.5 py-2 focus:ring-2 focus:ring-indigo-500"
              required
            >
              <option value="" disabled>Select Social Category</option>
              <option v-for="opt in socialCategoryOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>

            <!-- Disability Status Input -->
            <select 
              v-else-if="editingFieldKey === 'disability_status'"
              v-model="editingFieldValue"
              class="w-full text-sm border border-slate-300 rounded-xl px-3.5 py-2 focus:ring-2 focus:ring-indigo-500"
              required
            >
              <option :value="false">No (False)</option>
              <option :value="true">Yes (True)</option>
            </select>

            <!-- Default String Input (State, District, Occupation) -->
            <input 
              v-else
              v-model="editingFieldValue"
              type="text"
              placeholder="Enter value..."
              class="w-full text-sm border border-slate-300 rounded-xl px-3.5 py-2 focus:ring-2 focus:ring-indigo-500"
              required
            />
          </div>

          <div class="text-[11px] text-slate-500 bg-slate-50 p-2.5 rounded-lg border border-slate-200">
            <strong>Note:</strong> User-confirmed values have 100% confidence and will never be overwritten by AI extraction.
          </div>

          <div class="flex items-center justify-end gap-2 pt-2">
            <button
              type="button"
              @click="isEditModalOpen = false"
              class="px-4 py-2 border border-slate-300 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="store.isLoading"
              class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold shadow-xs transition-colors"
            >
              Save & Confirm
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
