<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../services/api';
import PersonaBar from '../components/PersonaBar.vue';
import { 
  ShieldCheck, 
  Users, 
  FileText, 
  AlertTriangle, 
  TrendingDown, 
  HelpCircle, 
  MapPin, 
  Search,
  CheckCircle2,
  Lock,
  Loader2
} from '@lucide/vue';

const isLoading = ref(true);
const selectedDistrict = ref('All');
const reportData = ref<any>(null);
const errorMessage = ref<string | null>(null);

const districts = [
  'All',
  'Pune',
  'Nashik',
  'Sangli',
  'Solapur',
  'Nagpur',
  'Chhatrapati Sambhajinagar'
];

async function fetchReport() {
  isLoading.value = true;
  errorMessage.value = null;
  try {
    const res = await api.get(`/tracker/community_intelligence/?district=${selectedDistrict.value}`);
    reportData.value = res.data;
  } catch (err: any) {
    console.error('Failed to load community gap report:', err);
    errorMessage.value = 'Failed to load community intelligence data.';
  } finally {
    isLoading.value = false;
  }
}

onMounted(async () => {
  await fetchReport();
});
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
    <PersonaBar />

    <!-- Page Header with Civic Tech Title & District Filter -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-200">
      <div>
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-800 text-xs font-bold uppercase tracking-wider mb-2">
          <Users class="w-3.5 h-3.5 text-indigo-600" />
          Civil Society & NGO Support Telemetry
        </div>
        <h1 class="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Community Benefits Gap Intelligence
        </h1>
        <p class="text-sm text-slate-600 mt-1 max-w-3xl">
          Anonymised and aggregated telemetry to help social workers, CSC counselors, and NGOs identify systemic document bottlenecks, drop-off phases, and portal confusion hotspots.
        </p>
      </div>

      <!-- District Selector -->
      <div class="flex items-center gap-2 shrink-0 bg-white p-2 rounded-2xl border border-slate-200 shadow-xs">
        <MapPin class="w-4 h-4 text-slate-500 ml-2" />
        <label class="text-xs font-bold text-slate-700">District:</label>
        <select 
          v-model="selectedDistrict" 
          @change="fetchReport"
          class="px-3 py-1.5 text-xs font-bold text-slate-800 bg-slate-50 border border-slate-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:outline-hidden"
        >
          <option v-for="d in districts" :key="d" :value="d">{{ d === 'All' ? 'All Maharashtra (Aggregated)' : d }}</option>
        </select>
      </div>
    </div>

    <!-- PRIVACY SAFEGUARD NOTICE: K-ANONYMITY BANNER -->
    <div class="p-4 rounded-2xl bg-emerald-50/90 border border-emerald-200 text-emerald-950 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-xs">
      <div class="flex items-start gap-3">
        <div class="p-2 bg-emerald-100 rounded-xl text-emerald-700 shrink-0 mt-0.5">
          <ShieldCheck class="w-5 h-5" />
        </div>
        <div>
          <div class="font-bold text-emerald-900 text-sm flex items-center gap-2">
            <span>Privacy-Preserving Aggregation Guarantee (k-Anonymity Standard, k = 5)</span>
            <span class="text-[10px] bg-emerald-200 text-emerald-900 px-2 py-0.5 rounded-full font-bold">Zero-PII</span>
          </div>
          <p class="text-xs text-emerald-800 mt-0.5">
            Strict statistical cell suppression is enforced: any cohort with fewer than 5 citizens is suppressed to prevent re-identification. No student names, Aadhaar numbers, or individual records are ever stored or exposed.
          </p>
        </div>
      </div>
      <div class="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-800 bg-white px-3 py-1.5 rounded-xl border border-emerald-300 shrink-0">
        <Lock class="w-3.5 h-3.5 text-emerald-600" />
        <span>Suppression Active</span>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="py-20 text-center space-y-3">
      <Loader2 class="w-10 h-10 animate-spin text-indigo-600 mx-auto" />
      <p class="text-sm font-semibold text-slate-600">Aggregating community access telemetry...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="errorMessage" class="p-6 bg-rose-50 border border-rose-200 rounded-2xl text-rose-800 text-center">
      <p class="font-bold">{{ errorMessage }}</p>
      <button @click="fetchReport" class="mt-3 px-4 py-2 bg-rose-600 text-white rounded-xl text-xs font-bold">Retry</button>
    </div>

    <!-- Main Content -->
    <div v-else-if="reportData" class="space-y-8">

      <!-- 1. Top 4 Metric Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-1">
          <div class="flex items-center justify-between text-slate-500">
            <span class="text-xs font-bold uppercase tracking-wider">Top Barrier Document</span>
            <FileText class="w-4 h-4 text-rose-500" />
          </div>
          <div class="text-lg font-black text-slate-900 truncate">Tahsildar Income Cert</div>
          <p class="text-xs text-rose-600 font-semibold">82% of applicants face delay friction</p>
        </div>

        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-1">
          <div class="flex items-center justify-between text-slate-500">
            <span class="text-xs font-bold uppercase tracking-wider">Highest Drop-off Phase</span>
            <TrendingDown class="w-4 h-4 text-amber-500" />
          </div>
          <div class="text-lg font-black text-slate-900 truncate">Civil Document Procurement</div>
          <p class="text-xs text-amber-600 font-semibold">38% abandon before applying</p>
        </div>

        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-1">
          <div class="flex items-center justify-between text-slate-500">
            <span class="text-xs font-bold uppercase tracking-wider">Most Demanded Scheme</span>
            <Search class="w-4 h-4 text-indigo-500" />
          </div>
          <div class="text-lg font-black text-slate-900 truncate">Ladki Bahin Yojana</div>
          <p class="text-xs text-indigo-600 font-semibold">Demand Index: 96 / 100</p>
        </div>

        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-1">
          <div class="flex items-center justify-between text-slate-500">
            <span class="text-xs font-bold uppercase tracking-wider">Overall Abandonment Rate</span>
            <AlertTriangle class="w-4 h-4 text-purple-500" />
          </div>
          <div class="text-lg font-black text-slate-900">{{ reportData.summary_metrics.average_abandonment_rate_pct }}%</div>
          <p class="text-xs text-purple-600 font-semibold">Across higher education schemes</p>
        </div>

      </div>

      <!-- 2. Preparation Abandonment Funnel (Where Users Leave) -->
      <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-6">
        <div>
          <h2 class="text-lg font-bold text-slate-900 flex items-center gap-2">
            <TrendingDown class="w-5 h-5 text-indigo-600" />
            Citizen Application Preparation Abandonment Funnel
          </h2>
          <p class="text-xs text-slate-500 mt-0.5">
            Identifies the precise lifecycle stage where students stall or abandon application preparation.
          </p>
        </div>

        <div class="space-y-4">
          <div 
            v-for="stage in reportData.preparation_abandonment_funnel" 
            :key="stage.stage_id"
            class="space-y-1.5"
          >
            <div class="flex items-center justify-between text-xs font-bold">
              <span class="text-slate-800">{{ stage.stage_name }}</span>
              <div class="flex items-center gap-3">
                <span v-if="stage.drop_off_pct > 0" class="text-rose-600 font-extrabold">
                  -{{ stage.drop_off_pct }}% Drop-off
                </span>
                <span class="text-indigo-700 bg-indigo-50 px-2.5 py-0.5 rounded-full border border-indigo-100 font-mono">
                  {{ stage.retention_pct }}% Retained
                </span>
              </div>
            </div>

            <!-- Progress bar -->
            <div class="w-full bg-slate-100 h-3 rounded-full overflow-hidden flex">
              <div 
                class="h-full rounded-full transition-all duration-500"
                :class="stage.retention_pct > 60 ? 'bg-indigo-600' : (stage.retention_pct > 35 ? 'bg-amber-500' : 'bg-rose-500')"
                :style="{ width: `${stage.retention_pct}%` }"
              ></div>
            </div>

            <p class="text-[11px] text-slate-500 flex items-center gap-1.5">
              <AlertTriangle v-if="stage.drop_off_pct > 10" class="w-3 h-3 text-amber-500 shrink-0" />
              <span>{{ stage.drop_off_reason }}</span>
            </p>
          </div>
        </div>
      </div>

      <!-- 3. Document Barrier Leaderboard (Which Documents Block Access) -->
      <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-6">
        <div>
          <h2 class="text-lg font-bold text-slate-900 flex items-center gap-2">
            <FileText class="w-5 h-5 text-rose-600" />
            Common Document Barriers & Revenue SLA Bottlenecks
          </h2>
          <p class="text-xs text-slate-500 mt-0.5">
            Ranked by access friction score, comparing official RTS Act delivery SLAs against actual field processing delays.
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div 
            v-for="doc in reportData.common_document_barriers" 
            :key="doc.document_code"
            class="p-4 rounded-2xl border border-slate-200 hover:border-slate-300 transition-all bg-slate-50/50 space-y-3"
          >
            <div class="flex items-start justify-between gap-2">
              <div>
                <h3 class="font-bold text-slate-900 text-sm">{{ doc.document_name }}</h3>
                <span class="text-[11px] text-slate-500 block mt-0.5">{{ doc.issuing_authority }}</span>
              </div>
              <span class="px-2.5 py-1 rounded-full text-xs font-extrabold shrink-0"
                :class="doc.friction_score_pct >= 75 ? 'bg-rose-100 text-rose-800' : (doc.friction_score_pct >= 60 ? 'bg-amber-100 text-amber-800' : 'bg-blue-100 text-blue-800')"
              >
                {{ doc.friction_score_pct }}% Friction
              </span>
            </div>

            <!-- SLA comparison -->
            <div class="grid grid-cols-2 gap-2 text-xs py-2 px-3 rounded-xl bg-white border border-slate-100">
              <div>
                <span class="text-slate-400 block text-[10px]">Statutory RTS SLA:</span>
                <span class="font-bold text-slate-800">{{ doc.statutory_sla_days }} Days</span>
              </div>
              <div>
                <span class="text-slate-400 block text-[10px]">Actual Field Delay:</span>
                <span class="font-bold text-rose-700">{{ doc.avg_delay_days }} Days (+{{ doc.avg_delay_days - doc.statutory_sla_days }}d over)</span>
              </div>
            </div>

            <p class="text-xs text-slate-600 leading-relaxed">
              <strong>Bottleneck:</strong> {{ doc.primary_barrier_reason }}
            </p>

            <div class="p-2.5 rounded-xl bg-indigo-50/80 border border-indigo-100 text-[11px] text-indigo-950">
              <strong class="font-bold text-indigo-900">NGO Counselor Guidance:</strong> {{ doc.ngo_intervention_guidance }}
            </div>
          </div>
        </div>
      </div>

      <!-- 4. Confusion Hotspots & Frequently Misunderstood Instructions -->
      <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-6">
        <div>
          <h2 class="text-lg font-bold text-slate-900 flex items-center gap-2">
            <HelpCircle class="w-5 h-5 text-amber-600" />
            Official Instructions Repeatedly Causing Confusion
          </h2>
          <p class="text-xs text-slate-500 mt-0.5">
            Identifies ambiguous department circular clauses where students repeatedly get rejected or trapped in scrutiny queries.
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div 
            v-for="(hotspot, idx) in reportData.confusion_hotspots" 
            :key="idx"
            class="p-5 rounded-2xl border border-amber-200 bg-amber-50/40 space-y-3"
          >
            <div class="flex items-start justify-between gap-2">
              <div>
                <span class="text-[10px] font-mono font-bold text-amber-800 bg-amber-100 px-2 py-0.5 rounded">
                  {{ hotspot.scheme }}
                </span>
                <h3 class="font-bold text-slate-900 text-sm mt-1">{{ hotspot.title }}</h3>
              </div>
              <span class="text-xs font-extrabold text-amber-800 bg-white px-2.5 py-1 rounded-full border border-amber-200 shrink-0">
                {{ hotspot.confusion_rate_pct }}% Confusion
              </span>
            </div>

            <p class="text-xs text-slate-700 leading-relaxed">
              {{ hotspot.issue_summary }}
            </p>

            <div class="pt-2 border-t border-amber-200/60 text-xs font-medium text-amber-950 flex items-start gap-1.5">
              <CheckCircle2 class="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
              <span><strong>Actionable Intervention:</strong> {{ hotspot.ngo_action }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 5. Frequently Searched & Tracked Schemes (Demand Index) -->
      <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-6">
        <div>
          <h2 class="text-lg font-bold text-slate-900 flex items-center gap-2">
            <Search class="w-5 h-5 text-indigo-600" />
            Community Demand & Scheme Search Frequency
          </h2>
          <p class="text-xs text-slate-500 mt-0.5">
            Public interest rankings across Maharashtra welfare and scholarship programs.
          </p>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs">
            <thead>
              <tr class="border-b border-slate-200 text-slate-400 font-bold uppercase tracking-wider text-[10px]">
                <th class="py-3 px-3">Scheme & Department</th>
                <th class="py-3 px-3">Target Category</th>
                <th class="py-3 px-3">Demand Index</th>
                <th class="py-3 px-3">Local Tracked Cohort</th>
                <th class="py-3 px-3">Benefit Entitlement</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 text-slate-700">
              <tr v-for="s in reportData.frequently_searched_schemes" :key="s.code" class="hover:bg-slate-50 transition-colors">
                <td class="py-3 px-3">
                  <div class="font-bold text-slate-900">{{ s.name }}</div>
                  <div class="text-[11px] text-slate-500">{{ s.department }}</div>
                </td>
                <td class="py-3 px-3 font-medium">{{ s.target_category }}</td>
                <td class="py-3 px-3">
                  <div class="flex items-center gap-2">
                    <span class="font-bold font-mono text-indigo-700">{{ s.interest_index }}/100</span>
                    <div class="w-16 bg-slate-100 h-2 rounded-full overflow-hidden">
                      <div class="bg-indigo-600 h-full rounded-full" :style="{ width: `${s.interest_index}%` }"></div>
                    </div>
                  </div>
                </td>
                <td class="py-3 px-3 font-mono">
                  <span v-if="s.is_suppressed" class="text-slate-400 bg-slate-100 px-2 py-0.5 rounded text-[10px]">
                    {{ s.local_tracked_count }}
                  </span>
                  <span v-else class="font-bold text-slate-900">
                    {{ s.local_tracked_count }}
                  </span>
                </td>
                <td class="py-3 px-3 font-bold text-emerald-700">{{ s.benefit_amount_text }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>
  </div>
</template>
