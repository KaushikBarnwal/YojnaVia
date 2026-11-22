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
        <div class="inline-flex items-center gap-2 mb-1.5">
          <span class="neo-stamp neo-stamp-navy text-[10px]">
            <Users class="w-3 h-3 text-amber-400" />
            Benefits for your whole household
          </span>
          <span class="text-xs text-slate-500 font-mono">All family members</span>
        </div>
        <h1 class="text-2xl sm:text-3xl font-extrabold text-[#0B132B] tracking-tight font-heading">
          Your family's benefits package
        </h1>
        <p class="text-xs sm:text-sm text-slate-600 mt-1 max-w-2xl font-medium">
          Schemes found for your whole family: college scholarships, help for small farmers, support for women and free family health cover.
        </p>
      </div>

      <div class="flex items-center gap-2 shrink-0">
        <button
          @click="printCounselorReport"
          class="neo-btn neo-btn-paper px-4 py-2 text-xs sm:text-sm font-bold text-[#0B132B]"
        >
          <Printer class="w-4 h-4 text-amber-600" />
          <span>Print summary for counsellor</span>
        </button>
      </div>
    </div>

    <!-- Family Selection Tabs -->
    <div class="neo-box p-2 flex flex-wrap gap-2 bg-white">
      <button
        @click="loadFamilyData('rohan_obc')"
        class="neo-btn px-3.5 py-1.5 text-xs font-bold"
        :class="activePersona === 'rohan_obc' ? 'neo-btn-navy' : 'neo-btn-paper text-slate-700'"
      >
        <span>Gaikwad family (OBC, small farmer)</span>
      </button>

      <button
        @click="loadFamilyData('sneha_ebc')"
        class="neo-btn px-3.5 py-1.5 text-xs font-bold"
        :class="activePersona === 'sneha_ebc' ? 'neo-btn-navy' : 'neo-btn-paper text-slate-700'"
      >
        <span>Kulkarni family (General / EWS)</span>
      </button>

      <button
        @click="loadFamilyData('vikas_sc')"
        class="neo-btn px-3.5 py-1.5 text-xs font-bold"
        :class="activePersona === 'vikas_sc' ? 'neo-btn-navy' : 'neo-btn-paper text-slate-700'"
      >
        <span>Kamble family (SC, polytechnic student)</span>
      </button>
    </div>

    <div v-if="familyData" class="space-y-6">
      <!-- Cumulative Family Value Card -->
      <div class="neo-box bg-[#0B132B] p-6 sm:p-8 text-white shadow-[4px_4px_0_0_#D97706]">
        <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div class="space-y-2">
            <div class="flex items-center gap-2">
              <span class="neo-stamp neo-stamp-emerald text-[9px]">
                Checked Maharashtra benefits
              </span>
              <span class="text-xs text-amber-300 font-mono font-bold">
                {{ familyData.district }} • {{ familyData.category }}
              </span>
            </div>
            <h2 class="text-2xl sm:text-3xl font-extrabold font-heading text-white">
              {{ familyData.family_name }} family package
            </h2>
            <p class="text-xs sm:text-sm text-slate-300 max-w-xl font-medium">
              Yearly household income: ₹{{ familyData.total_annual_income.toLocaleString('en-IN') }} (ration card: {{ familyData.ration_card }})
            </p>
          </div>

          <!-- Highlight Metric Boxes -->
          <div class="flex flex-wrap items-center gap-3">
            <div class="bg-white/10 p-4 rounded-xl border border-white/20 min-w-[160px]">
              <div class="text-xs text-emerald-300 font-bold">Total yearly cash and fee benefit</div>
              <div class="text-2xl sm:text-3xl font-extrabold text-white font-mono mt-1 font-heading">
                ₹{{ familyData.total_annual_household_benefit_inr.toLocaleString('en-IN') }}
              </div>
              <div class="text-[11px] text-slate-300 mt-0.5">Cash support and fee waivers</div>
            </div>

            <div class="bg-white/10 p-4 rounded-xl border border-white/20 min-w-[160px]">
              <div class="text-xs text-amber-300 font-bold">Free family health cover</div>
              <div class="text-2xl sm:text-3xl font-extrabold text-white font-mono mt-1 font-heading">
                ₹5,00,000
              </div>
              <div class="text-[11px] text-slate-300 mt-0.5">MJPJAY: free treatment at hospitals</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Household Members Grid -->
      <div class="space-y-4">
        <h3 class="text-base font-extrabold text-[#0B132B] flex items-center gap-2 font-heading">
          <Users class="w-4 h-4 text-amber-600" />
          <span>Benefits for each family member</span>
        </h3>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div 
            v-for="member in familyData.members" 
            :key="member.id"
            class="neo-box p-5 bg-white flex flex-col justify-between"
          >
            <div class="space-y-3">
              <!-- Member Header -->
              <div class="flex items-start justify-between gap-3">
                <div>
                  <div class="flex items-center gap-2">
                    <span class="text-sm font-extrabold text-[#0B132B]">{{ member.name }}</span>
                    <span class="neo-stamp bg-[#F5F5F3] text-slate-700 text-[9px]">
                      {{ member.relation }}
                    </span>
                  </div>
                  <p class="text-xs text-slate-600 mt-0.5 font-medium">{{ member.details }}</p>
                </div>
                <div class="text-right shrink-0">
                  <span class="neo-stamp neo-stamp-emerald text-xs font-mono font-bold">
                    +₹{{ member.subtotal_annual_benefit.toLocaleString('en-IN') }}/yr
                  </span>
                </div>
              </div>

              <!-- Matched Schemes for this Member -->
              <div class="space-y-2 pt-1">
                <div 
                  v-for="scheme in member.matched_schemes" 
                  :key="scheme.code"
                  class="p-3 rounded-xl border-[1.5px] border-[#0B132B] bg-[#FBFBFA] space-y-1 shadow-[1.5px_1.5px_0_0_#0B132B]"
                >
                  <div class="flex items-center justify-between gap-2 text-xs">
                    <span class="font-bold text-[#0B132B]">{{ scheme.name }}</span>
                    <span class="text-emerald-800 font-extrabold font-mono shrink-0">
                      ₹{{ scheme.annual_value.toLocaleString('en-IN') }}
                    </span>
                  </div>
                  <p class="text-[11px] text-slate-700 font-medium">{{ scheme.benefit_text }}</p>
                  <div class="text-[10px] text-slate-500 font-mono flex items-center justify-between pt-0.5 font-bold">
                    <span>{{ scheme.department }}</span>
                    <span>{{ scheme.statutory_gr }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Footer -->
            <div class="mt-4 pt-3 border-t-[1.5px] border-[#0B132B]/10 flex items-center justify-between text-xs text-slate-600 font-medium">
              <span>Status: <strong class="text-emerald-800 font-bold">Likely Eligible</strong></span>
              <span class="text-[11px] text-amber-700 font-bold">Matched by the eligibility check</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Shared Social Safety Net (Health & Housing) -->
      <div class="neo-box p-5 space-y-3 bg-white">
        <h3 class="text-sm sm:text-base font-extrabold text-[#0B132B] flex items-center gap-2 font-heading">
          <HeartHandshake class="w-4 h-4 text-emerald-700" />
          <span>Benefits shared by the whole family</span>
        </h3>

        <div 
          v-for="shared in familyData.shared_household_schemes" 
          :key="shared.code"
          class="p-4 rounded-xl border-[1.5px] border-[#0B132B] bg-[#ECFDF5] flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-[2px_2px_0_0_#0B132B]"
        >
          <div>
            <div class="flex items-center gap-2">
              <span class="neo-stamp neo-stamp-emerald text-[9px]">Open to every family</span>
              <span class="neo-stamp bg-emerald-200 text-emerald-950 text-[9px]">No income limit</span>
            </div>
            <h4 class="text-base font-extrabold text-emerald-950 mt-1 font-heading">{{ shared.name }}</h4>
            <p class="text-xs text-emerald-900 mt-0.5 font-medium">{{ shared.benefit_text }}</p>
            <p class="text-[11px] text-emerald-800 mt-1 font-mono font-bold">Official order: {{ shared.statutory_gr }}</p>
          </div>
          <div class="shrink-0 text-right">
            <span class="neo-stamp neo-stamp-navy text-xs">
              Covers all family members
            </span>
          </div>
        </div>
      </div>

      <!-- Counselor / CSC Worker Action Notes -->
      <div class="neo-box p-5 space-y-2 bg-[#FFFBEB]">
        <div class="flex items-center gap-2 text-xs font-extrabold uppercase tracking-wider text-[#0B132B] font-heading">
          <Building2 class="w-4 h-4 text-amber-700" />
          <span>Advice for counsellors and NGOs</span>
        </div>
        <ul class="text-xs text-amber-950 space-y-1.5 pl-4 list-disc font-medium">
          <li v-for="(note, idx) in familyData.counsellor_action_notes" :key="idx">
            {{ note }}
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>
