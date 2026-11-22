<script setup lang="ts">
import { onMounted } from 'vue';
import { useStudentStore } from '../stores/studentStore';
import PersonaBar from '../components/PersonaBar.vue';
import { 
  FileText, 
  Sparkles, 
  Clock, 
  ExternalLink, 
  FolderGit2
} from '@lucide/vue';

const store = useStudentStore();

onMounted(async () => {
  if (store.documentGraph.documents.length === 0) {
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
      <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-200 text-blue-800 text-xs font-bold uppercase tracking-wider mb-2">
        <FolderGit2 class="w-3.5 h-3.5 text-blue-600" />
        Step 4 of 5: Cross-Scheme Document Dependency Graph
      </div>
      <h1 class="text-2xl sm:text-3xl font-extrabold text-slate-900">
        The Single Document Multiplier Effect
      </h1>
      <p class="text-sm text-slate-600 mt-1 max-w-3xl">
        Stop obtaining documents repeatedly. This graph demonstrates how a single official civil document (like your Tahsildar Income Certificate) unlocks multiple scholarships simultaneously, while displaying issuing SLAs and prerequisite document chains.
      </p>
    </div>

    <!-- Top Highlight: The #1 Multiplier Document -->
    <div v-if="store.documentGraph.top_multiplier_document" class="mb-8 p-6 rounded-2xl bg-gradient-to-r from-emerald-900 via-teal-900 to-slate-900 text-white shadow-xl border border-emerald-700/40">
      <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
        <div class="space-y-2">
          <div class="flex items-center gap-2">
            <span class="p-1 rounded-md bg-emerald-400 text-emerald-950">
              <Sparkles class="w-4 h-4" />
            </span>
            <span class="text-xs font-bold uppercase tracking-wider text-emerald-300">
              Highest Leverage Certificate in Maharashtra
            </span>
            <span class="text-[10px] bg-white/20 px-2 py-0.5 rounded-full font-mono text-white">
              Unlocks {{ store.documentGraph.top_multiplier_document.schemes_count }} Schemes at Once
            </span>
          </div>

          <h2 class="text-xl sm:text-2xl font-black text-white">
            {{ store.documentGraph.top_multiplier_document.name }}
          </h2>

          <p class="text-sm text-emerald-100">
            Marathi Name: <span class="font-medium text-white">{{ store.documentGraph.top_multiplier_document.name_marathi }}</span>
          </p>

          <p class="text-sm text-slate-300 leading-relaxed max-w-2xl">
            Obtaining this single document unlocks an estimated <strong class="text-emerald-300 font-bold font-mono">₹{{ store.documentGraph.top_multiplier_document.total_financial_value_unlocked.toLocaleString('en-IN') }}/year</strong> across EBC Tuition, OBC Freeship, and Dr. Panjabrao Deshmukh Hostel Assistance!
          </p>

          <!-- Prerequisite Chain Pill -->
          <div v-if="store.documentGraph.top_multiplier_document.prerequisites.length > 0" class="pt-2">
            <div class="text-xs text-emerald-200 bg-emerald-950/60 border border-emerald-500/30 p-2.5 rounded-lg flex items-start gap-2">
              <span class="font-bold">Prerequisites Needed First:</span>
              <span>{{ store.documentGraph.top_multiplier_document.prerequisites.join(' • ') }}</span>
            </div>
          </div>
        </div>

        <div class="shrink-0 text-right space-y-2 w-full lg:w-auto">
          <div class="bg-white/10 backdrop-blur-xs p-4 rounded-xl border border-white/20">
            <div class="text-xs text-emerald-200">Aaple Sarkar SLA</div>
            <div class="text-2xl font-black text-white">{{ store.documentGraph.top_multiplier_document.estimated_sla_days }} Days</div>
            <div class="text-[11px] text-slate-300 mt-1 font-mono">aaplesarkar.mahaonline.gov.in</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Complete Cross-Scheme Documents Grid -->
    <div class="space-y-4">
      <h2 class="text-lg font-bold text-slate-900 flex items-center gap-2">
        <FileText class="w-5 h-5 text-indigo-600" />
        All Maharashtra Higher Education Documents (Ranked by Multiplier Power)
      </h2>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div 
          v-for="doc in store.documentGraph.documents" 
          :key="doc.code"
          class="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs hover:shadow-md transition-all flex flex-col justify-between"
        >
          <div class="space-y-3">
            <div class="flex items-start justify-between gap-3">
              <div>
                <span class="text-xs font-mono bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-medium">
                  {{ doc.code }}
                </span>
                <h3 class="font-bold text-base text-slate-900 mt-1">{{ doc.name }}</h3>
                <p v-if="doc.name_marathi" class="text-xs text-slate-500 font-medium">{{ doc.name_marathi }}</p>
              </div>

              <div class="text-right shrink-0">
                <span class="text-xs font-bold px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 flex items-center gap-1">
                  <Clock class="w-3 h-3 text-emerald-600" />
                  {{ doc.estimated_sla_days }}d SLA
                </span>
              </div>
            </div>

            <!-- Multiplier Metrics -->
            <div class="flex items-center gap-4 text-xs bg-slate-50 p-2.5 rounded-xl border border-slate-100">
              <div>
                <span class="text-slate-500">Unlocks:</span>
                <span class="font-bold text-indigo-700 ml-1">{{ doc.schemes_count }} Schemes</span>
              </div>
              <div class="border-l border-slate-200 pl-4">
                <span class="text-slate-500">Total Unlocked Value:</span>
                <span class="font-bold text-emerald-700 font-mono ml-1">₹{{ doc.total_financial_value_unlocked.toLocaleString('en-IN') }}/yr</span>
              </div>
            </div>

            <!-- Unlocked Schemes Tags -->
            <div v-if="doc.unlocks_schemes.length > 0" class="space-y-1">
              <div class="text-[11px] font-bold text-slate-600 uppercase tracking-wider">Unlocks for:</div>
              <div class="flex flex-wrap gap-1.5">
                <span 
                  v-for="s in doc.unlocks_schemes" 
                  :key="s.scheme_code"
                  class="text-[11px] px-2 py-0.5 rounded-md bg-indigo-50 border border-indigo-200 text-indigo-900 font-medium"
                >
                  {{ s.scheme_name.split('(')[0].trim() }}
                </span>
              </div>
            </div>

            <!-- Prerequisites Chain -->
            <div v-if="doc.prerequisites.length > 0" class="pt-1">
              <div class="text-[11px] text-slate-500">
                <strong class="text-slate-700">Pre-requisite Civil Docs:</strong> {{ doc.prerequisites.join(', ') }}
              </div>
            </div>
          </div>

          <!-- Bottom Procurement Portal Link -->
          <div class="pt-4 mt-4 border-t border-slate-100 flex items-center justify-between text-xs">
            <span class="text-slate-500 font-medium">Authority: {{ doc.issuing_authority }}</span>
            <a 
              :href="formatUrl(doc.procurement_portal)" 
              target="_blank" 
              rel="noopener noreferrer"
              class="font-semibold text-indigo-600 hover:text-indigo-800 flex items-center gap-1"
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
