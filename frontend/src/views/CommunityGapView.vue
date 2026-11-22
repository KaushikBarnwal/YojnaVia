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
    errorMessage.value = 'Something went wrong. Please try again in a few minutes.';
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
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b-[1.5px] border-[#0B132B]">
      <div>
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-sm bg-[#FEF3C7] border border-[#D97706] text-[#92400E] text-xs font-black uppercase tracking-wider mb-2 shadow-[1px_1px_0_0_#92400E]">
          <Users class="w-3.5 h-3.5 text-[#D97706]" />
          Support for community groups and NGOs
        </div>
        <h1 class="text-2xl sm:text-4xl font-black text-[#0B132B] tracking-tight">
          Community Benefits <span class="bg-[#FDE047] px-1.5 py-0.5 border-b-[2px] border-[#0B132B]">Gap Report</span>
        </h1>
        <p class="text-sm text-[#475569] mt-2 max-w-3xl leading-relaxed">
          Anonymous, combined information to help social workers, CSC counselors and NGOs find where students get stuck: documents, steps and confusing instructions.
        </p>
      </div>

      <!-- District Selector -->
      <div class="flex items-center gap-2 shrink-0 bg-[#FBFBFA] p-2 rounded-lg border-[1.5px] border-[#0B132B] shadow-[2.5px_2.5px_0_0_#0B132B]">
        <MapPin class="w-4 h-4 text-[#0B132B] ml-2" />
        <label class="text-xs font-black text-[#0B132B] uppercase tracking-wider">District:</label>
        <select 
          v-model="selectedDistrict" 
          @change="fetchReport"
          class="px-3 py-1.5 text-xs font-bold text-[#0B132B] bg-white border border-[#0B132B] rounded-sm focus:ring-2 focus:ring-[#D97706] focus:outline-hidden"
        >
          <option v-for="d in districts" :key="d" :value="d">{{ d === 'All' ? 'All of Maharashtra (combined)' : d }}</option>
        </select>
      </div>
    </div>

    <!-- PRIVACY SAFEGUARD NOTICE: K-ANONYMITY BANNER -->
    <div class="p-4 rounded-xl bg-[#ECFDF5] border-[1.5px] border-[#065F46] text-[#064E3B] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-[2.5px_2.5px_0_0_#065F46]">
      <div class="flex items-start gap-3">
        <div class="p-2 bg-[#D1FAE5] rounded-lg text-[#065F46] border border-[#065F46] shrink-0 mt-0.5">
          <ShieldCheck class="w-5 h-5" />
        </div>
        <div>
          <div class="font-black text-[#064E3B] text-sm flex items-center gap-2">
            <span>Privacy protected: results are combined so no one can be identified (groups of at least 5)</span>
            <span class="text-[10px] bg-[#A7F3D0] text-[#065F46] px-2 py-0.5 rounded-sm font-black border border-[#065F46]">No personal details</span>
          </div>
          <p class="text-xs text-[#065F46] mt-0.5">
            Any group with fewer than 5 people is hidden so no one can be identified. Student names, Aadhaar numbers and individual records are never stored or shown.
          </p>
        </div>
      </div>
      <div class="inline-flex items-center gap-1.5 text-xs font-black text-[#064E3B] bg-white px-3 py-1.5 rounded-sm border border-[#065F46] shrink-0 shadow-[1px_1px_0_0_#065F46]">
        <Lock class="w-3.5 h-3.5 text-[#059669]" />
        <span>Privacy protection on</span>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="py-20 text-center space-y-3">
      <Loader2 class="w-10 h-10 animate-spin text-[#0B132B] mx-auto" />
      <p class="text-sm font-bold text-[#0B132B]">Gathering community information...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="errorMessage" class="p-6 bg-[#FEF2F2] border-[1.5px] border-[#DC2626] rounded-xl text-[#991B1B] text-center shadow-[2.5px_2.5px_0_0_#DC2626]">
      <p class="font-bold">{{ errorMessage }}</p>
      <button @click="fetchReport" class="mt-3 px-4 py-2 bg-[#DC2626] text-white rounded-lg text-xs font-bold border border-[#7F1D1D] shadow-[1.5px_1.5px_0_0_#7F1D1D] cursor-pointer">Try again</button>
    </div>

    <!-- Main Content -->
    <div v-else-if="reportData" class="space-y-8">

      <!-- 1. Top 4 Metric Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        <div class="bg-[#FBFBFA] p-5 rounded-xl border-[1.5px] border-[#0B132B] shadow-[2.5px_2.5px_0_0_#0B132B] space-y-1">
          <div class="flex items-center justify-between text-[#64748B]">
            <span class="text-xs font-black uppercase tracking-wider text-[#0B132B]">Top Barrier Document</span>
            <FileText class="w-4 h-4 text-[#DC2626]" />
          </div>
          <div class="text-lg font-black text-[#0B132B] truncate">Tahsildar Income Certificate</div>
          <p class="text-xs text-[#DC2626] font-bold">82% of applicants face delays</p>
        </div>

        <div class="bg-[#FBFBFA] p-5 rounded-xl border-[1.5px] border-[#0B132B] shadow-[2.5px_2.5px_0_0_#0B132B] space-y-1">
          <div class="flex items-center justify-between text-[#64748B]">
            <span class="text-xs font-black uppercase tracking-wider text-[#0B132B]">Highest Drop-off Phase</span>
            <TrendingDown class="w-4 h-4 text-[#D97706]" />
          </div>
          <div class="text-lg font-black text-[#0B132B] truncate">Collecting official documents</div>
          <p class="text-xs text-[#D97706] font-bold">38% give up before applying</p>
        </div>

        <div class="bg-[#FBFBFA] p-5 rounded-xl border-[1.5px] border-[#0B132B] shadow-[2.5px_2.5px_0_0_#0B132B] space-y-1">
          <div class="flex items-center justify-between text-[#64748B]">
            <span class="text-xs font-black uppercase tracking-wider text-[#0B132B]">Most Demanded Scheme</span>
            <Search class="w-4 h-4 text-[#059669]" />
          </div>
          <div class="text-lg font-black text-[#0B132B] truncate">Ladki Bahin Yojana</div>
          <p class="text-xs text-[#059669] font-bold">Demand score: 96 out of 100</p>
        </div>

        <div class="bg-[#FBFBFA] p-5 rounded-xl border-[1.5px] border-[#0B132B] shadow-[2.5px_2.5px_0_0_#0B132B] space-y-1">
          <div class="flex items-center justify-between text-[#64748B]">
            <span class="text-xs font-black uppercase tracking-wider text-[#0B132B]">Overall Abandonment Rate</span>
            <AlertTriangle class="w-4 h-4 text-[#7C3AED]" />
          </div>
          <div class="text-lg font-black text-[#0B132B]">{{ reportData.summary_metrics.average_abandonment_rate_pct }}%</div>
          <p class="text-xs text-[#7C3AED] font-bold">Across college scholarship schemes</p>
        </div>

      </div>

      <!-- 2. Preparation Abandonment Funnel (Where Users Leave) -->
      <div class="bg-[#FBFBFA] p-6 rounded-xl border-[1.5px] border-[#0B132B] shadow-[2.5px_2.5px_0_0_#0B132B] space-y-6">
        <div>
          <h2 class="text-lg font-black text-[#0B132B] flex items-center gap-2">
            <TrendingDown class="w-5 h-5 text-[#D97706]" />
            Where students stop while preparing applications
          </h2>
          <p class="text-xs text-[#64748B] mt-0.5 font-medium">
            Shows the exact step where students get stuck or stop preparing their application.
          </p>
        </div>

        <div class="space-y-4">
          <div 
            v-for="stage in reportData.preparation_abandonment_funnel" 
            :key="stage.stage_id"
            class="space-y-1.5"
          >
            <div class="flex items-center justify-between text-xs font-bold">
              <span class="text-[#0B132B]">{{ stage.stage_name }}</span>
              <div class="flex items-center gap-3">
                <span v-if="stage.drop_off_pct > 0" class="text-[#DC2626] font-black">
                  -{{ stage.drop_off_pct }}% gave up here
                </span>
                <span class="text-[#0B132B] bg-[#F1F5F9] px-2.5 py-0.5 rounded-sm border border-[#0B132B] font-mono font-bold">
                  {{ stage.retention_pct }}% still going
                </span>
              </div>
            </div>

            <!-- Progress bar with ink border -->
            <div class="w-full bg-[#E2E8F0] h-3.5 rounded-none border border-[#0B132B] overflow-hidden flex">
              <div 
                class="h-full transition-all duration-500"
                :class="stage.retention_pct > 60 ? 'bg-[#059669]' : (stage.retention_pct > 35 ? 'bg-[#D97706]' : 'bg-[#DC2626]')"
                :style="{ width: `${stage.retention_pct}%` }"
              ></div>
            </div>

            <p class="text-[11px] text-[#475569] flex items-center gap-1.5">
              <AlertTriangle v-if="stage.drop_off_pct > 10" class="w-3 h-3 text-[#D97706] shrink-0" />
              <span>{{ stage.drop_off_reason }}</span>
            </p>
          </div>
        </div>
      </div>

      <!-- 3. Document Barrier Leaderboard (Which Documents Block Access) -->
      <div class="bg-[#FBFBFA] p-6 rounded-xl border-[1.5px] border-[#0B132B] shadow-[2.5px_2.5px_0_0_#0B132B] space-y-6">
        <div>
          <h2 class="text-lg font-black text-[#0B132B] flex items-center gap-2">
            <FileText class="w-5 h-5 text-[#DC2626]" />
            Documents that hold students back
          </h2>
          <p class="text-xs text-[#64748B] mt-0.5 font-medium">
            Ranked by how much they slow students down. Compares the official time limit with how long it really takes.
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div 
            v-for="doc in reportData.common_document_barriers" 
            :key="doc.document_code"
            class="p-4 rounded-xl border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#0B132B] bg-white space-y-3"
          >
            <div class="flex items-start justify-between gap-2">
              <div>
                <h3 class="font-black text-[#0B132B] text-sm">{{ doc.document_name }}</h3>
                <span class="text-[11px] text-[#64748B] block mt-0.5 font-mono">{{ doc.issuing_authority }}</span>
              </div>
              <span class="px-2.5 py-1 rounded-sm text-xs font-black shrink-0 border border-[#0B132B]"
                :class="doc.friction_score_pct >= 75 ? 'bg-[#FEE2E2] text-[#991B1B]' : (doc.friction_score_pct >= 60 ? 'bg-[#FEF3C7] text-[#92400E]' : 'bg-[#E0F2FE] text-[#075985]')"
              >
                {{ doc.friction_score_pct }}% slows people down
              </span>
            </div>

            <!-- SLA comparison -->
            <div class="grid grid-cols-2 gap-2 text-xs py-2 px-3 rounded-lg bg-[#F8FAFC] border border-[#CBD5E1]">
              <div>
                <span class="text-[#64748B] block text-[10px] font-bold uppercase">Official time limit:</span>
                <span class="font-black text-[#0B132B]">{{ doc.statutory_sla_days }} days</span>
              </div>
              <div>
                <span class="text-[#64748B] block text-[10px] font-bold uppercase">Real wait time:</span>
                <span class="font-black text-[#DC2626]">{{ doc.avg_delay_days }} days (+{{ doc.avg_delay_days - doc.statutory_sla_days }} days over)</span>
              </div>
            </div>

            <p class="text-xs text-[#334155] leading-relaxed">
              <strong class="font-bold text-[#0B132B]">Main problem:</strong> {{ doc.primary_barrier_reason }}
            </p>

            <div class="p-2.5 rounded-lg bg-[#FEF3C7]/60 border border-[#F59E0B] text-[11px] text-[#78350F]">
              <strong class="font-bold text-[#92400E]">Advice for counselors:</strong> {{ doc.ngo_intervention_guidance }}
            </div>
          </div>
        </div>
      </div>

      <!-- 4. Confusion Hotspots & Frequently Misunderstood Instructions -->
      <div class="bg-[#FBFBFA] p-6 rounded-xl border-[1.5px] border-[#0B132B] shadow-[2.5px_2.5px_0_0_#0B132B] space-y-6">
        <div>
          <h2 class="text-lg font-black text-[#0B132B] flex items-center gap-2">
            <HelpCircle class="w-5 h-5 text-[#D97706]" />
            Official instructions that confuse students again and again
          </h2>
          <p class="text-xs text-[#64748B] mt-0.5 font-medium">
            Shows unclear rules in government notices that often lead to rejected or delayed applications.
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div 
            v-for="(hotspot, idx) in reportData.confusion_hotspots" 
            :key="idx"
            class="p-5 rounded-xl border-[1.5px] border-[#0B132B] bg-[#FFFBEB] shadow-[2px_2px_0_0_#0B132B] space-y-3"
          >
            <div class="flex items-start justify-between gap-2">
              <div>
                <span class="text-[10px] font-mono font-bold text-[#92400E] bg-[#FEF3C7] px-2 py-0.5 rounded-sm border border-[#D97706]">
                  {{ hotspot.scheme }}
                </span>
                <h3 class="font-black text-[#0B132B] text-sm mt-1.5">{{ hotspot.title }}</h3>
              </div>
              <span class="text-xs font-black text-[#92400E] bg-white px-2.5 py-1 rounded-sm border border-[#0B132B] shrink-0 shadow-[1px_1px_0_0_#0B132B]">
                {{ hotspot.confusion_rate_pct }}% find it confusing
              </span>
            </div>

            <p class="text-xs text-[#334155] leading-relaxed">
              {{ hotspot.issue_summary }}
            </p>

            <div class="pt-2 border-t border-[#FCD34D] text-xs font-medium text-[#78350F] flex items-start gap-1.5">
              <CheckCircle2 class="w-4 h-4 text-[#059669] shrink-0 mt-0.5" />
              <span><strong class="font-bold text-[#0B132B]">What to do:</strong> {{ hotspot.ngo_action }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 5. Frequently Searched & Tracked Schemes (Demand Index) -->
      <div class="bg-[#FBFBFA] p-6 rounded-xl border-[1.5px] border-[#0B132B] shadow-[2.5px_2.5px_0_0_#0B132B] space-y-6">
        <div>
          <h2 class="text-lg font-black text-[#0B132B] flex items-center gap-2">
            <Search class="w-5 h-5 text-[#0B132B]" />
            Which schemes people are looking for
          </h2>
          <p class="text-xs text-[#64748B] mt-0.5 font-medium">
            Ranking of popular welfare and scholarship schemes across Maharashtra.
          </p>
        </div>

        <div class="overflow-x-auto border-[1.5px] border-[#0B132B] rounded-lg">
          <table class="w-full text-left text-xs bg-white">
            <thead>
              <tr class="border-b-[1.5px] border-[#0B132B] bg-[#F1F5F9] text-[#0B132B] font-black uppercase tracking-wider text-[10px]">
                <th class="py-3 px-3">Scheme and department</th>
                <th class="py-3 px-3">Who it is for</th>
                <th class="py-3 px-3">Popularity</th>
                <th class="py-3 px-3">Students tracked locally</th>
                <th class="py-3 px-3">Benefit</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[#E2E8F0] text-[#334155]">
              <tr v-for="s in reportData.frequently_searched_schemes" :key="s.code" class="hover:bg-[#F8FAFC] transition-colors">
                <td class="py-3 px-3">
                  <div class="font-black text-[#0B132B]">{{ s.name }}</div>
                  <div class="text-[11px] text-[#64748B] font-mono">{{ s.department }}</div>
                </td>
                <td class="py-3 px-3 font-bold text-[#0B132B]">{{ s.target_category }}</td>
                <td class="py-3 px-3">
                  <div class="flex items-center gap-2">
                    <span class="font-black font-mono text-[#0B132B]">{{ s.interest_index }}/100</span>
                    <div class="w-16 bg-[#E2E8F0] h-2.5 rounded-none border border-[#0B132B] overflow-hidden">
                      <div class="bg-[#059669] h-full" :style="{ width: `${s.interest_index}%` }"></div>
                    </div>
                  </div>
                </td>
                <td class="py-3 px-3 font-mono">
                  <span v-if="s.is_suppressed" class="text-[#64748B] bg-[#F1F5F9] px-2 py-0.5 rounded-sm border border-[#CBD5E1] text-[10px] font-bold">
                    {{ s.local_tracked_count }}
                  </span>
                  <span v-else class="font-black text-[#0B132B]">
                    {{ s.local_tracked_count }}
                  </span>
                </td>
                <td class="py-3 px-3 font-black text-[#059669]">{{ s.benefit_amount_text }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>
  </div>
</template>
