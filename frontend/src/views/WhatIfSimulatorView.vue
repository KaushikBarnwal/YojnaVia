<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useStudentStore } from '../stores/studentStore';
import api from '../services/api';
import PersonaBar from '../components/PersonaBar.vue';
import { 
  Sparkles, 
  CheckCircle2, 
  XCircle, 
  ArrowRight, 
  TrendingUp, 
  TrendingDown, 
  Home, 
  GraduationCap, 
  MapPin, 
  Sliders, 
  RotateCcw, 
  AlertTriangle,
  Scale,
  Loader2
} from '@lucide/vue';

const store = useStudentStore();
const isLoading = ref(false);
const presets = ref<any[]>([]);
const selectedPresetId = ref<string>('cap_merit_admission');

// Custom sandbox state
const customCourseLevel = ref('PROFESSIONAL_DEGREE');
const customIncome = ref(150000);
const customAccommodation = ref('PRIVATE_RENTAL_PG');
const customQuota = ref('CAP_ROUND');
const customDomicile = ref(true);

const simulationResult = ref<any>(null);

const courseLevelOptions = [
  { value: 'HSC_12TH', label: '12th Pass / Junior College' },
  { value: 'DIPLOMA', label: 'Polytechnic diploma' },
  { value: 'PROFESSIONAL_DEGREE', label: 'Professional Degree (B.Tech / B.Pharm / MBBS)' },
  { value: 'NON_PROFESSIONAL_DEGREE', label: 'Arts, science or commerce degree (BA / B.Sc / B.Com)' },
  { value: 'POSTGRADUATE', label: 'Postgraduate (M.Tech / MCA / MBA / M.Sc)' }
];

const accommodationOptions = [
  { value: 'DAY_SCHOLAR', label: 'Day scholar (living with parents or commuting)' },
  { value: 'PRIVATE_RENTAL_PG', label: 'Rented room, PG or private hostel (more than 30 km from home)' },
  { value: 'GOVERNMENT_HOSTEL', label: 'Government or university hostel' }
];

const quotaOptions = [
  { value: 'CAP_ROUND', label: 'Merit round through the central admission process (CAP)' },
  { value: 'DIRECT_SECOND_YEAR', label: 'Direct second year admission (DSE)' },
  { value: 'MANAGEMENT_QUOTA', label: 'College management seat' }
];

async function fetchPresets() {
  try {
    const res = await api.get('/eligibility/what_if/presets/');
    presets.value = res.data.scenarios || [];
  } catch (err) {
    console.error('Failed to load presets:', err);
  }
}

async function runPresetSimulation(presetId: string) {
  selectedPresetId.value = presetId;
  const p = presets.value.find(x => x.id === presetId);
  if (!p) return;

  // Sync controls to preset
  if (p.modifications.current_course_level) customCourseLevel.value = p.modifications.current_course_level;
  if (p.modifications.annual_family_income) customIncome.value = p.modifications.annual_family_income;
  if (p.modifications.accommodation_type) customAccommodation.value = p.modifications.accommodation_type;
  if (p.modifications.admission_quota) customQuota.value = p.modifications.admission_quota;
  if (p.modifications.is_maharashtra_domicile !== undefined) customDomicile.value = p.modifications.is_maharashtra_domicile;

  isLoading.value = true;
  try {
    const res = await api.post('/eligibility/what_if/', {
      session_token: store.sessionToken,
      preset_scenario_id: presetId,
      modifications: p.modifications
    });
    simulationResult.value = res.data;
  } catch (err) {
    console.error('Failed to run what-if simulation:', err);
  } finally {
    isLoading.value = false;
  }
}

async function runCustomSimulation() {
  selectedPresetId.value = 'custom';
  isLoading.value = true;
  try {
    const modifications = {
      current_course_level: customCourseLevel.value,
      annual_family_income: Number(customIncome.value),
      accommodation_type: customAccommodation.value,
      admission_quota: customQuota.value,
      is_maharashtra_domicile: customDomicile.value
    };

    const res = await api.post('/eligibility/what_if/', {
      session_token: store.sessionToken,
      modifications: modifications
    });
    simulationResult.value = res.data;
  } catch (err) {
    console.error('Failed to run custom simulation:', err);
  } finally {
    isLoading.value = false;
  }
}

onMounted(async () => {
  await fetchPresets();
  if (store.profile) {
    customIncome.value = store.profile.annual_family_income || 150000;
    customCourseLevel.value = store.profile.current_course_level || 'PROFESSIONAL_DEGREE';
    customAccommodation.value = store.profile.accommodation_type || 'PRIVATE_RENTAL_PG';
    customQuota.value = store.profile.admission_quota || 'CAP_ROUND';
    customDomicile.value = store.profile.is_maharashtra_domicile ?? true;
  }
  // Run default scenario
  runPresetSimulation('move_to_hostel');
});

// Re-run simulation when persona changes
watch(() => store.profile?.name, () => {
  if (selectedPresetId.value && selectedPresetId.value !== 'custom') {
    runPresetSimulation(selectedPresetId.value);
  } else {
    runCustomSimulation();
  }
});

function getIcon(iconName: string) {
  switch (iconName) {
    case 'Home': return Home;
    case 'GraduationCap': return GraduationCap;
    case 'TrendingDown': return TrendingDown;
    case 'TrendingUp': return TrendingUp;
    case 'CheckCircle2': return CheckCircle2;
    case 'MapPin': return MapPin;
    default: return Sparkles;
  }
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
    <PersonaBar />

    <!-- Page Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <div class="inline-flex items-center gap-2 mb-1.5">
          <span class="neo-stamp neo-stamp-navy text-[10px]">
            <Sparkles class="w-3 h-3 text-amber-400" />
            Interactive Future Planning Sandbox
          </span>
          <span class="text-xs text-slate-500 font-mono">Rule-based check</span>
        </div>
        <h1 class="text-2xl sm:text-3xl font-extrabold text-[#0B132B] tracking-tight font-heading">
          What-If Eligibility Simulator
        </h1>
        <p class="text-xs sm:text-sm text-slate-600 mt-1 max-w-3xl font-medium">
          See how your scholarships could change if your situation changes, like starting a degree, earning more, or moving to a hostel. Your real profile stays the same.
        </p>
      </div>

      <router-link
        to="/schemes"
        class="neo-btn neo-btn-paper px-4 py-2 text-xs sm:text-sm font-bold text-[#0B132B] shrink-0 self-start md:self-auto"
      >
        <span>Back to my schemes</span>
        <ArrowRight class="w-4 h-4" />
      </router-link>
    </div>

    <!-- MANDATORY LEGAL / ETHICAL GUARDRAIL NOTICE -->
    <div class="p-4 rounded-xl border-[1.5px] border-[#0B132B] bg-[#FFFBEB] text-amber-950 text-xs sm:text-sm font-medium flex items-start gap-3 shadow-[2px_2px_0_0_#0B132B]">
      <AlertTriangle class="w-5 h-5 text-amber-700 shrink-0 mt-0.5" />
      <div>
        <strong class="font-bold block text-amber-950 mb-0.5">Please note:</strong>
        <span class="text-amber-900 font-medium">"This is a planning tool to help you make choices about study and money. Never give wrong details on official government websites. Official submissions need valid, digitally signed certificates from the revenue office."</span>
      </div>
    </div>

    <!-- 1-Click Preset Scenarios Grid -->
    <div class="space-y-3">
      <div class="flex items-center justify-between">
        <h2 class="text-xs font-extrabold uppercase tracking-widest text-[#0B132B] flex items-center gap-2 font-heading">
          <Sparkles class="w-4 h-4 text-amber-600" />
          <span>Quick what-if scenarios</span>
        </h2>
        <span class="text-xs text-slate-500 font-medium">Click any scenario to see the result</span>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        <button
          v-for="preset in presets"
          :key="preset.id"
          @click="runPresetSimulation(preset.id)"
          class="neo-box-interactive p-4 text-left flex flex-col justify-between gap-3"
          :class="selectedPresetId === preset.id 
            ? '!bg-[#FEF3C7] !shadow-[3px_3px_0_0_#0B132B] ring-2 ring-amber-600' 
            : 'bg-white'"
        >
          <div class="space-y-1.5">
            <div class="flex items-center justify-between">
              <span class="neo-stamp text-[9px]"
                :class="selectedPresetId === preset.id ? 'neo-stamp-amber' : 'bg-[#F5F5F3] text-slate-700'">
                {{ preset.category }}
              </span>
              <component :is="getIcon(preset.icon)" class="w-4 h-4" :class="selectedPresetId === preset.id ? 'text-amber-700' : 'text-slate-500'" />
            </div>
            <h3 class="text-xs sm:text-sm font-extrabold text-[#0B132B] line-clamp-2 leading-snug font-heading">
              {{ preset.title }}
            </h3>
            <p class="text-[11px] text-slate-600 leading-relaxed line-clamp-2 font-medium">
              {{ preset.description }}
            </p>
          </div>
          <div class="text-[11px] font-bold text-amber-800 flex items-center gap-1 pt-1 border-t border-[#0B132B]/10">
            <span>See result</span>
            <ArrowRight class="w-3 h-3" />
          </div>
        </button>
      </div>
    </div>

    <!-- Interactive Custom Sandbox Controls -->
    <div class="neo-box p-6 bg-white space-y-5">
      <div class="flex items-center justify-between border-b-[1.5px] border-[#0B132B]/15 pb-3">
        <div class="flex items-center gap-2">
          <Sliders class="w-5 h-5 text-amber-600" />
          <h2 class="text-sm sm:text-base font-extrabold text-[#0B132B] font-heading">Try your own situation</h2>
        </div>
        <button 
          @click="runCustomSimulation"
          class="neo-btn neo-btn-saffron px-4 py-2 text-xs font-bold"
        >
          <RotateCcw class="w-3.5 h-3.5" />
          <span>Run my own check</span>
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
        <!-- Education Level -->
        <div class="space-y-1.5">
          <label class="font-bold text-[#0B132B]">Course or degree</label>
          <select 
            v-model="customCourseLevel"
            @change="runCustomSimulation"
            class="neo-input w-full p-2.5 bg-white font-medium"
          >
            <option v-for="opt in courseLevelOptions" :key="opt.value" :value="opt.value">
              {{ opt.label }}
            </option>
          </select>
        </div>

        <!-- Accommodation Type -->
        <div class="space-y-1.5">
          <label class="font-bold text-[#0B132B]">Living Arrangement</label>
          <select 
            v-model="customAccommodation"
            @change="runCustomSimulation"
            class="neo-input w-full p-2.5 bg-white font-medium"
          >
            <option v-for="opt in accommodationOptions" :key="opt.value" :value="opt.value">
              {{ opt.label }}
            </option>
          </select>
        </div>

        <!-- Admission Quota -->
        <div class="space-y-1.5">
          <label class="font-bold text-[#0B132B]">How you get admission</label>
          <select 
            v-model="customQuota"
            @change="runCustomSimulation"
            class="neo-input w-full p-2.5 bg-white font-medium"
          >
            <option v-for="opt in quotaOptions" :key="opt.value" :value="opt.value">
              {{ opt.label }}
            </option>
          </select>
        </div>

        <!-- Annual Income Slider -->
        <div class="space-y-1.5">
          <div class="flex items-center justify-between font-bold text-[#0B132B]">
            <span>Annual family income:</span>
            <span class="text-emerald-800 font-mono font-extrabold">₹{{ Number(customIncome).toLocaleString('en-IN') }}</span>
          </div>
          <input 
            type="range" 
            v-model.number="customIncome"
            @change="runCustomSimulation"
            min="40000" 
            max="1000000" 
            step="20000"
            class="w-full accent-amber-600 cursor-pointer"
          />
          <div class="flex justify-between text-[10px] text-slate-500 font-bold">
            <span>₹40k (below poverty line)</span>
            <span>₹1.5L</span>
            <span>₹8L (OBC income limit)</span>
            <span>₹10L</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Simulation Results & Impact Analysis -->
    <div v-if="isLoading" class="neo-box p-12 text-center space-y-3 bg-white">
      <Loader2 class="w-8 h-8 text-amber-600 animate-spin mx-auto" />
      <h3 class="text-base font-extrabold text-[#0B132B] font-heading">Checking what changes...</h3>
      <p class="text-xs text-slate-600 font-medium">Checking all Maharashtra schemes with your changes.</p>
    </div>

    <div v-else-if="simulationResult" class="space-y-6">
      <!-- Financial Impact Delta Banner -->
      <div 
        class="neo-box p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 min-w-0 w-full"
        :class="simulationResult.financial_impact.delta_inr > 0 
          ? 'bg-[#ECFDF5]' 
          : simulationResult.financial_impact.delta_inr < 0 
            ? 'bg-[#FFF1F2]'
            : 'bg-[#FBFBFA]'"
      >
        <div class="space-y-1">
          <div class="flex items-center gap-2">
            <span class="neo-stamp neo-stamp-navy text-[9px]">
              Scenario: {{ simulationResult.scenario_title }}
            </span>
            <span class="text-xs text-slate-600 font-bold">Impact comparison</span>
          </div>
          <h3 class="text-xl sm:text-2xl font-extrabold text-[#0B132B] font-heading">
            {{ simulationResult.financial_impact.delta_inr > 0 
                ? 'This scenario gets you more government money!' 
                : simulationResult.financial_impact.delta_inr < 0 
                  ? 'This scenario may cost you some benefits.' 
                  : 'Your benefits stay the same.' }}
          </h3>
          <p class="text-xs text-slate-700 max-w-2xl leading-relaxed font-medium">
            Comparing your current profile with this what-if situation.
          </p>
        </div>

        <!-- Delta Numbers Box -->
        <div class="bg-white p-4 rounded-xl border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#0B132B] flex flex-col sm:flex-row sm:items-center gap-4 w-full sm:w-auto min-w-0 shrink-0">
          <div class="text-center pb-3 sm:pb-0 sm:pr-4 border-b sm:border-b-0 sm:border-r border-[#0B132B]/15 w-full sm:w-auto min-w-0">
            <span class="text-[10px] text-slate-500 block uppercase font-bold">Current total</span>
            <span class="text-base font-bold text-slate-700 font-mono break-words">₹{{ simulationResult.financial_impact.baseline_total_inr.toLocaleString('en-IN') }}</span>
          </div>
          <div class="text-center pb-3 sm:pb-0 sm:pr-4 border-b sm:border-b-0 sm:border-r border-[#0B132B]/15 w-full sm:w-auto min-w-0">
            <span class="text-[10px] text-slate-500 block uppercase font-bold">New total</span>
            <span class="text-base font-extrabold text-[#0B132B] font-mono break-words">₹{{ simulationResult.financial_impact.simulated_total_inr.toLocaleString('en-IN') }}</span>
          </div>
          <div class="text-center w-full sm:w-auto min-w-0">
            <span class="text-[10px] text-slate-600 block uppercase font-bold">Difference per year</span>
            <span 
              class="block text-2xl font-black font-mono font-heading break-words"
              :class="simulationResult.financial_impact.delta_inr > 0 ? 'text-emerald-800' : simulationResult.financial_impact.delta_inr < 0 ? 'text-rose-800' : 'text-[#0B132B]'"
            >
              {{ simulationResult.financial_impact.delta_formatted }}/year
            </span>
          </div>
        </div>
      </div>

      <!-- Section: Newly Unlocked Schemes -->
      <div v-if="simulationResult.newly_unlocked_schemes.length > 0" class="space-y-3">
        <h3 class="text-xs font-extrabold uppercase tracking-wider text-emerald-800 flex items-center gap-1.5 font-heading">
          <CheckCircle2 class="w-4 h-4 text-emerald-700" />
          <span>New schemes you can get ({{ simulationResult.newly_unlocked_schemes.length }})</span>
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div 
            v-for="s in simulationResult.newly_unlocked_schemes" 
            :key="s.code"
            class="neo-box p-5 bg-[#ECFDF5] space-y-2.5"
          >
            <div class="flex items-start justify-between">
              <div>
                <span class="neo-stamp neo-stamp-navy font-mono text-[9px]">
                  {{ s.code }}
                </span>
                <h4 class="text-sm font-extrabold text-[#0B132B] mt-1 font-heading">{{ s.name }}</h4>
              </div>
              <span class="neo-stamp neo-stamp-emerald text-xs">
                {{ s.benefit_amount_text }}
              </span>
            </div>

            <div class="p-2.5 bg-white rounded-xl border border-[#0B132B]/20 text-xs text-emerald-950 space-y-1">
              <strong class="text-[11px] uppercase tracking-wider text-emerald-900 block font-bold">Why you now qualify:</strong>
              <div v-for="(crit, idx) in s.flipped_to_pass" :key="idx" class="flex items-center gap-1.5 font-medium">
                <CheckCircle2 class="w-3.5 h-3.5 text-emerald-700 shrink-0" />
                <span>{{ crit.reason }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Section: Lost Schemes -->
      <div v-if="simulationResult.lost_schemes.length > 0" class="space-y-3">
        <h3 class="text-xs font-extrabold uppercase tracking-wider text-rose-800 flex items-center gap-1.5 font-heading">
          <XCircle class="w-4 h-4 text-rose-700" />
          <span>Schemes you would not qualify for ({{ simulationResult.lost_schemes.length }})</span>
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div 
            v-for="s in simulationResult.lost_schemes" 
            :key="s.code"
            class="neo-box p-5 bg-[#FFF1F2] space-y-2.5"
          >
            <div class="flex items-start justify-between">
              <div>
                <span class="neo-stamp neo-stamp-navy font-mono text-[9px]">
                  {{ s.code }}
                </span>
                <h4 class="text-sm font-extrabold text-[#0B132B] mt-1 font-heading">{{ s.name }}</h4>
              </div>
              <span class="neo-stamp neo-stamp-rose text-xs">
                Not eligible
              </span>
            </div>

            <div class="p-2.5 bg-white rounded-xl border border-[#0B132B]/20 text-xs text-rose-950 space-y-1">
              <strong class="text-[11px] uppercase tracking-wider text-rose-900 block font-bold">Why you no longer qualify:</strong>
              <div v-for="(crit, idx) in s.flipped_to_fail" :key="idx" class="flex items-center gap-1.5 font-medium">
                <XCircle class="w-3.5 h-3.5 text-rose-700 shrink-0" />
                <span>{{ crit.reason }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Section: Detailed Criteria Diff Table -->
      <div class="neo-box p-6 space-y-4 bg-white">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <Scale class="w-5 h-5 text-amber-600" />
            <h3 class="text-xs sm:text-sm font-extrabold text-[#0B132B] uppercase tracking-wider font-heading">
              Rule-by-rule check
            </h3>
          </div>
          <span class="text-xs text-slate-500">Shows all schemes checked and any change</span>
        </div>

        <div class="w-full min-w-0 overflow-x-auto">
          <table class="w-full text-left text-xs border-collapse break-words">
            <thead>
              <tr class="border-b border-slate-200 text-slate-500 font-bold uppercase text-[10px] tracking-wider bg-slate-50/80">
                <th class="p-3">Scheme</th>
                <th class="p-3">Current status</th>
                <th class="p-3">New status</th>
                <th class="p-3">What changed</th>
                <th class="p-3">Official source</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr 
                v-for="s in simulationResult.all_scheme_diffs" 
                :key="s.code"
                class="hover:bg-slate-50/50 transition-colors"
                :class="s.status_changed ? 'bg-indigo-50/30' : ''"
              >
                <td class="p-3">
                  <div class="font-bold text-slate-900">{{ s.name }}</div>
                  <span class="text-[10px] font-mono text-slate-400">{{ s.code }}</span>
                </td>
                <td class="p-3">
                  <span 
                    class="px-2 py-0.5 rounded text-[10px] font-bold uppercase"
                    :class="s.baseline_status === 'LIKELY_ELIGIBLE' ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-600'"
                  >
                    {{ s.baseline_status }}
                  </span>
                </td>
                <td class="p-3">
                  <span 
                    class="px-2 py-0.5 rounded text-[10px] font-bold uppercase"
                    :class="s.simulated_status === 'LIKELY_ELIGIBLE' ? 'bg-emerald-100 text-emerald-800' : s.simulated_status === 'NEAR_ELIGIBLE' ? 'bg-amber-100 text-amber-800' : 'bg-rose-100 text-rose-800'"
                  >
                    {{ s.simulated_status }}
                  </span>
                </td>
                <td class="p-3">
                  <span v-if="s.status_changed" class="font-semibold text-indigo-700">
                    {{ s.flipped_to_pass.length > 0 ? 'You meet ' + s.flipped_to_pass.length + ' new rule(s)' : 'Now you fail a rule' }}
                  </span>
                  <span v-else class="text-slate-400">No change</span>
                </td>
                <td class="p-3 text-[11px] text-slate-500 font-mono">
                  {{ s.gr_citation || 'Maharashtra government order' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>
