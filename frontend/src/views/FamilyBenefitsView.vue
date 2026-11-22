<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../services/api';
import PersonaBar from '../components/PersonaBar.vue';
import { 
  Users, 
  HeartHandshake, 
  Printer, 
  Building2
} from '@lucide/vue';

const activePersona = ref('rohan_obc');
const familyData = ref<any>(null);
const isLoading = ref(false);

async function loadFamilyData(personaKey: string) {
  isLoading.value = true;
  activePersona.value = personaKey;
  try {
    const res = await api.get(`/eligibility/family/?persona=${personaKey}`);
    familyData.value = res.data;
  } catch (err) {
    console.error('Failed to load family data:', err);
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  loadFamilyData('rohan_obc');
});

function printCounselorReport() {
  window.print();
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
    <PersonaBar />

    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700 text-xs font-bold uppercase tracking-wider mb-2">
          <Users class="w-3.5 h-3.5 text-indigo-600" />
          Household-Level Benefits Discovery
        </div>
        <h1 class="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Family Entitlement Package
        </h1>
        <p class="text-sm text-slate-600 mt-1 max-w-2xl">
          Schemes matched across your entire household—combining higher education scholarships, small farmer support, women's welfare, and universal family health insurance.
        </p>
      </div>

      <div class="flex items-center gap-2 shrink-0">
        <button
          @click="printCounselorReport"
          class="px-4 py-2 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 rounded-xl text-xs sm:text-sm font-semibold transition-colors flex items-center gap-1.5 shadow-xs"
        >
          <Printer class="w-4 h-4 text-indigo-600" />
          <span>Print / Export Counselor Summary</span>
        </button>
      </div>
    </div>

    <!-- Family Selection Tabs -->
    <div class="bg-white rounded-2xl border border-slate-200 p-2 flex flex-wrap gap-2 shadow-xs">
      <button
        @click="loadFamilyData('rohan_obc')"
        class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5"
        :class="activePersona === 'rohan_obc' ? 'bg-indigo-600 text-white shadow-xs' : 'text-slate-600 hover:bg-slate-100'"
      >
        <span>Gaikwad Family (OBC Small Farmer)</span>
      </button>

      <button
        @click="loadFamilyData('sneha_ebc')"
        class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5"
        :class="activePersona === 'sneha_ebc' ? 'bg-indigo-600 text-white shadow-xs' : 'text-slate-600 hover:bg-slate-100'"
      >
        <span>Kulkarni Family (Open / EWS)</span>
      </button>

      <button
        @click="loadFamilyData('vikas_sc')"
        class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5"
        :class="activePersona === 'vikas_sc' ? 'bg-indigo-600 text-white shadow-xs' : 'text-slate-600 hover:bg-slate-100'"
      >
        <span>Kamble Family (SC Polytechnic)</span>
      </button>
    </div>

    <div v-if="familyData" class="space-y-6">
      <!-- Cumulative Family Value Card -->
      <div class="rounded-3xl bg-gradient-to-r from-indigo-900 via-slate-900 to-emerald-950 p-6 sm:p-8 text-white shadow-lg border border-indigo-800/40">
        <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div class="space-y-2">
            <div class="flex items-center gap-2">
              <span class="text-xs font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-emerald-400 text-emerald-950">
                Verified Maharashtra Entitlements
              </span>
              <span class="text-xs text-indigo-200">
                {{ familyData.district }} • {{ familyData.category }}
              </span>
            </div>
            <h2 class="text-2xl sm:text-3xl font-black">
              {{ familyData.family_name }} Household Package
            </h2>
            <p class="text-xs sm:text-sm text-slate-300 max-w-xl">
              Annual household income: ₹{{ familyData.total_annual_income.toLocaleString('en-IN') }}/yr (Ration Card: {{ familyData.ration_card }})
            </p>
          </div>

          <!-- Highlight Metric Boxes -->
          <div class="flex flex-wrap items-center gap-3">
            <div class="bg-white/10 backdrop-blur-xs p-4 rounded-2xl border border-white/20 min-w-[160px]">
              <div class="text-xs text-emerald-300 font-semibold">Total Annual Direct Benefit</div>
              <div class="text-2xl sm:text-3xl font-black text-white font-mono mt-1">
                ₹{{ familyData.total_annual_household_benefit_inr.toLocaleString('en-IN') }}
              </div>
              <div class="text-[11px] text-slate-300 mt-0.5">Direct Cash & Tuition Waivers</div>
            </div>

            <div class="bg-white/10 backdrop-blur-xs p-4 rounded-2xl border border-white/20 min-w-[160px]">
              <div class="text-xs text-indigo-300 font-semibold">Universal Family Health Cover</div>
              <div class="text-2xl sm:text-3xl font-black text-white font-mono mt-1">
                ₹5,00,000
              </div>
              <div class="text-[11px] text-slate-300 mt-0.5">MJPJAY Cashless Hospitalization</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Household Members Grid -->
      <div class="space-y-4">
        <h3 class="text-base font-bold text-slate-900 flex items-center gap-2">
          <Users class="w-4 h-4 text-indigo-600" />
          <span>Individual Member Entitlement Breakdown</span>
        </h3>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div 
            v-for="member in familyData.members" 
            :key="member.id"
            class="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs hover:shadow-md transition-shadow flex flex-col justify-between"
          >
            <div class="space-y-3">
              <!-- Member Header -->
              <div class="flex items-start justify-between gap-3">
                <div>
                  <div class="flex items-center gap-2">
                    <span class="text-sm font-extrabold text-slate-900">{{ member.name }}</span>
                    <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
                      {{ member.relation }}
                    </span>
                  </div>
                  <p class="text-xs text-slate-500 mt-0.5">{{ member.details }}</p>
                </div>
                <div class="text-right shrink-0">
                  <span class="text-xs font-mono font-bold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-200">
                    +₹{{ member.subtotal_annual_benefit.toLocaleString('en-IN') }}/yr
                  </span>
                </div>
              </div>

              <!-- Matched Schemes for this Member -->
              <div class="space-y-2 pt-1">
                <div 
                  v-for="scheme in member.matched_schemes" 
                  :key="scheme.code"
                  class="p-3 rounded-xl bg-slate-50 border border-slate-200/80 space-y-1"
                >
                  <div class="flex items-center justify-between gap-2 text-xs">
                    <span class="font-bold text-slate-900">{{ scheme.name }}</span>
                    <span class="text-emerald-700 font-bold font-mono shrink-0">
                      ₹{{ scheme.annual_value.toLocaleString('en-IN') }}
                    </span>
                  </div>
                  <p class="text-[11px] text-slate-600">{{ scheme.benefit_text }}</p>
                  <div class="text-[10px] text-slate-400 font-mono flex items-center justify-between pt-0.5">
                    <span>{{ scheme.department }}</span>
                    <span>{{ scheme.statutory_gr }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Footer -->
            <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
              <span>Status: <strong class="text-emerald-700 font-semibold">Likely Eligible</strong></span>
              <span class="text-[11px] text-indigo-600 font-semibold">100% Rule Engine Matched</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Shared Social Safety Net (Health & Housing) -->
      <div class="bg-white rounded-2xl border border-slate-200 p-5 space-y-3 shadow-xs">
        <h3 class="text-sm sm:text-base font-bold text-slate-900 flex items-center gap-2">
          <HeartHandshake class="w-4 h-4 text-emerald-600" />
          <span>Shared Family Social Safety Nets (Universal Maharashtra Cover)</span>
        </h3>

        <div 
          v-for="shared in familyData.shared_household_schemes" 
          :key="shared.code"
          class="p-4 rounded-xl bg-emerald-50/70 border border-emerald-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
        >
          <div>
            <div class="flex items-center gap-2">
              <span class="text-xs font-bold text-emerald-800 uppercase tracking-wider">Universal Family Protection</span>
              <span class="text-[10px] bg-emerald-200 text-emerald-900 px-2 py-0.5 rounded-full font-semibold">Zero Income Cap</span>
            </div>
            <h4 class="text-base font-bold text-emerald-950 mt-1">{{ shared.name }}</h4>
            <p class="text-xs text-emerald-800 mt-0.5">{{ shared.benefit_text }}</p>
            <p class="text-[11px] text-emerald-700 mt-1 font-mono">Authority: {{ shared.statutory_gr }}</p>
          </div>
          <div class="shrink-0 text-right">
            <span class="text-xs font-bold px-3 py-1.5 rounded-xl bg-emerald-600 text-white shadow-xs inline-block">
              All Family Members Covered
            </span>
          </div>
        </div>
      </div>

      <!-- Counselor / CSC Worker Action Notes -->
      <div class="bg-slate-50 rounded-2xl border border-slate-200 p-5 space-y-2">
        <div class="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-700">
          <Building2 class="w-4 h-4 text-indigo-600" />
          <span>NGO / CSC Counselor Guidance Plan</span>
        </div>
        <ul class="text-xs text-slate-600 space-y-1.5 pl-4 list-disc">
          <li v-for="(note, idx) in familyData.counsellor_action_notes" :key="idx">
            {{ note }}
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>
