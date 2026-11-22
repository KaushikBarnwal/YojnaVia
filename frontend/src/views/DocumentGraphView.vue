<script setup lang="ts">
import { onMounted } from 'vue';
import { useStudentStore } from '../stores/studentStore';
import PersonaBar from '../components/PersonaBar.vue';
import { 
  FileText, 
  Clock, 
  ExternalLink, 
  FolderGit2
} from '@lucide/vue';

const store = useStudentStore();

onMounted(async () => {
  if (!store.documentGraph?.documents || store.documentGraph.documents.length === 0) {
    await store.fetchDocumentGraph();
  }
});

function formatUrl(url: string) {
  if (!url) return '#';
  return url.startsWith('http') ? url : 'https://' + url;
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <PersonaBar />

    <!-- Page Header -->
    <div class="mb-8">
      <div class="inline-flex items-center gap-2 mb-1.5">
        <span class="neo-stamp neo-stamp-navy text-[10px]">
          <FolderGit2 class="w-3 h-3 text-amber-400" />
          How your certificates connect
        </span>
        <span class="text-xs text-slate-500 font-mono">Step 4 of 5</span>
      </div>
      <h1 class="text-2xl sm:text-3xl font-extrabold text-[#0B132B] tracking-tight font-heading">
        One Certificate, Many Scholarships
      </h1>
      <p class="text-xs sm:text-sm text-slate-600 mt-1 max-w-3xl font-medium">
        Don't get the same certificate again and again. One official certificate, like your Tahsildar Income Certificate, can help you apply for several scholarships at once. This page shows which certificates help the most, how long each one takes, and which ones you need first.
      </p>
    </div>

    <!-- Top Highlight: The #1 Multiplier Document -->
    <div v-if="store.documentGraph.top_multiplier_document" class="mb-8 neo-box !bg-[#0B132B] p-6 text-white shadow-[4px_4px_0_0_#D97706]">
      <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
        <div class="space-y-2">
          <div class="flex items-center gap-2 flex-wrap">
            <span class="neo-stamp neo-stamp-emerald text-[9px]">
              Most helpful certificate in Maharashtra
            </span>
            <span class="neo-stamp text-[9px] bg-white/20 text-white font-mono">
              Helps with {{ store.documentGraph.top_multiplier_document.schemes_count }} scholarships
            </span>
          </div>

          <h2 class="text-xl sm:text-2xl font-extrabold text-white font-heading">
            {{ store.documentGraph.top_multiplier_document.name }}
          </h2>

          <p class="text-xs sm:text-sm text-slate-200 font-indic">
            Name in Marathi: <span class="font-bold text-amber-300">{{ store.documentGraph.top_multiplier_document.name_marathi }}</span>
          </p>

          <p class="text-xs sm:text-sm text-slate-200 leading-relaxed max-w-2xl font-medium">
            Obtaining this single document unlocks an estimated <strong class="text-emerald-300 font-mono font-bold">₹{{ store.documentGraph.top_multiplier_document.total_financial_value_unlocked.toLocaleString('en-IN') }}/year</strong> across EBC Tuition, OBC Freeship, and Dr. Panjabrao Deshmukh Hostel Assistance!
          </p>

          <!-- Prerequisite Chain Pill -->
          <div v-if="store.documentGraph.top_multiplier_document.prerequisites.length > 0" class="pt-2">
            <div class="text-xs text-amber-200 bg-[#1E293B] border border-[#0B132B] p-2.5 rounded-xl flex items-start gap-2 font-medium">
              <span class="font-bold text-amber-400">Get these documents first:</span>
              <span>{{ store.documentGraph.top_multiplier_document.prerequisites.join(' • ') }}</span>
            </div>
          </div>
        </div>

        <div class="shrink-0 text-right space-y-2 w-full lg:w-auto">
          <div class="bg-white/10 p-4 rounded-xl border border-white/20">
            <div class="text-xs text-amber-300 font-bold">Time to get it at Aaple Sarkar</div>
            <div class="text-2xl font-extrabold text-white font-mono font-heading">{{ store.documentGraph.top_multiplier_document.estimated_sla_days }} days</div>
            <div class="text-[11px] text-slate-300 mt-1 font-mono">aaplesarkar.mahaonline.gov.in</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Complete Cross-Scheme Documents Grid -->
    <div class="space-y-4">
      <h2 class="text-base sm:text-lg font-extrabold text-[#0B132B] flex items-center gap-2 font-heading">
        <FileText class="w-4 h-4 text-amber-600" />
        All certificates, most helpful first
      </h2>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div 
          v-for="doc in store.documentGraph.documents" 
          :key="doc.code"
          class="neo-box p-5 bg-white flex flex-col justify-between"
        >
          <div class="space-y-3">
            <div class="flex items-start justify-between gap-3">
              <div>
                <span class="neo-stamp neo-stamp-navy font-mono text-xs">
                  {{ doc.code }}
                </span>
                <h3 class="font-extrabold text-base text-[#0B132B] mt-1 font-heading">{{ doc.name }}</h3>
                <p v-if="doc.name_marathi" class="text-xs text-slate-700 font-medium font-indic">{{ doc.name_marathi }}</p>
              </div>

              <div class="text-right shrink-0">
                <span class="neo-stamp neo-stamp-emerald text-xs">
                  <Clock class="w-3 h-3 text-emerald-700" />
                  About {{ doc.estimated_sla_days }} days
                </span>
              </div>
            </div>

            <!-- Multiplier Metrics -->
            <div class="flex items-center gap-4 text-xs bg-[#FBFBFA] p-2.5 rounded-xl border-[1.5px] border-[#0B132B]/15 font-medium">
              <div>
                <span class="text-slate-700">Helps with:</span>
                <span class="font-bold text-amber-800 ml-1">{{ doc.schemes_count }} scholarships</span>
              </div>
              <div class="border-l border-[#0B132B]/15 pl-4">
                <span class="text-slate-700">Possible yearly benefit:</span>
                <span class="font-bold text-emerald-800 font-mono ml-1">₹{{ doc.total_financial_value_unlocked.toLocaleString('en-IN') }}/yr</span>
              </div>
            </div>

            <!-- Unlocked Schemes Tags -->
            <div v-if="doc.unlocks_schemes.length > 0" class="space-y-1">
              <div class="text-xs font-bold text-[#0B132B]">Scholarships it helps with:</div>
              <div class="flex flex-wrap gap-1.5">
                <span 
                  v-for="s in doc.unlocks_schemes" 
                  :key="s.scheme_code"
                  class="text-xs font-bold px-2 py-0.5 rounded-md bg-[#F5F5F3] border border-[#0B132B]/20 text-[#0B132B]"
                >
                  {{ s.scheme_name.split('(')[0].trim() }}
                </span>
              </div>
            </div>

            <!-- Prerequisites Chain -->
            <div v-if="doc.prerequisites.length > 0" class="pt-1">
              <div class="text-xs text-slate-700 font-medium">
                <strong class="text-[#0B132B]">You need these first:</strong> {{ doc.prerequisites.join(', ') }}
              </div>
            </div>
          </div>

          <!-- Bottom Procurement Portal Link -->
          <div class="pt-3 mt-4 border-t-[1.5px] border-[#0B132B]/10 flex items-center justify-between text-xs font-medium">
            <span class="text-slate-600">Issued by: {{ doc.issuing_authority }}</span>
            <a 
              :href="formatUrl(doc.procurement_portal)" 
              target="_blank" 
              rel="noopener noreferrer"
              class="font-bold text-amber-700 hover:text-black flex items-center gap-1"
            >
              <span>{{ doc.procurement_portal }}</span>
              <ExternalLink class="w-3 h-3" />
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
