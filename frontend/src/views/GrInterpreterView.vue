<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../services/api';
import PersonaBar from '../components/PersonaBar.vue';
import { 
  FileText, 
  Sparkles, 
  CheckCircle2, 
  Clock, 
  HelpCircle, 
  ShieldCheck, 
  BookOpen, 
  Loader2,
  Copy,
  Check,
  Layers
} from '@lucide/vue';

const sampleGrs = ref<any[]>([]);
const selectedSampleId = ref('ebc_cap_merit_2018');
const inputText = ref('');
const isLoading = ref(false);
const isSamplesLoading = ref(true);
const interpretedData = ref<any>(null);
const errorMessage = ref<string | null>(null);
const highlightedQuote = ref<string | null>(null);
const isCopied = ref(false);

async function loadSampleGrs() {
  isSamplesLoading.value = true;
  try {
    const res = await api.get('/assistant/gr_samples/');
    sampleGrs.value = res.data.samples || [];
    if (sampleGrs.value.length > 0) {
      selectSample(sampleGrs.value[0]);
    }
  } catch (err) {
    console.error('Failed to load GR samples:', err);
  } finally {
    isSamplesLoading.value = false;
  }
}

function selectSample(sample: any) {
  selectedSampleId.value = sample.id;
  inputText.value = sample.excerpt_text;
  highlightedQuote.value = null;
  handleInterpret();
}

async function handleInterpret() {
  if (!inputText.value.trim()) return;
  isLoading.value = true;
  errorMessage.value = null;
  try {
    const res = await api.post('/assistant/interpret_gr/', {
      source_text: inputText.value,
      preferred_language: 'en'
    });
    interpretedData.value = res.data;
  } catch (err: any) {
    console.error('Interpretation failed:', err);
    errorMessage.value = err.response?.data?.error || 'Could not explain this text. Please try again.';
  } finally {
    isLoading.value = false;
  }
}

function highlightInSource(quote: string) {
  highlightedQuote.value = quote;
  // Scroll to source container smoothly
  const el = document.getElementById('source-text-container');
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
}

function copyBlueprint() {
  if (!interpretedData.value) return;
  const text = JSON.stringify(interpretedData.value, null, 2);
  navigator.clipboard.writeText(text);
  isCopied.value = true;
  setTimeout(() => isCopied.value = false, 2000);
}

onMounted(async () => {
  await loadSampleGrs();
});
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
    <PersonaBar />

    <!-- Page Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b-[1.5px] border-[#0B132B]/15">
      <div>
        <div class="inline-flex items-center gap-2 mb-1.5">
          <span class="neo-stamp neo-stamp-navy text-[10px]">
            <BookOpen class="w-3 h-3 text-amber-400" />
            Official order explainer
          </span>
          <span class="text-xs text-slate-500 font-mono">Explains official orders</span>
        </div>
        <h1 class="text-2xl sm:text-3xl font-extrabold text-[#0B132B] tracking-tight font-heading">
          Government order explainer 📜
        </h1>
        <p class="text-xs sm:text-sm text-slate-600 mt-1 max-w-3xl font-medium">
          Paste a Maharashtra Government Resolution (GR) or notice. YojnaVia explains who qualifies, what documents you need and what to do next. Every point links to the exact sentence it came from.
        </p>
      </div>

      <!-- Evidence Certification Badge -->
      <div class="flex items-center gap-2 shrink-0">
        <span class="neo-stamp neo-stamp-emerald text-xs">
          <ShieldCheck class="w-4 h-4 text-emerald-700" />
          Checked against the original text
        </span>
      </div>
    </div>

    <!-- 1-Click Sample GR Templates Bar -->
    <div class="space-y-2">
      <div class="flex items-center justify-between text-xs font-bold text-[#0B132B]">
        <span>Try a sample government order (one click):</span>
        <span class="text-slate-500 font-mono text-[11px]">Official notices</span>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
        <button
          v-for="sample in sampleGrs"
          :key="sample.id"
          @click="selectSample(sample)"
          class="neo-box-interactive p-3 text-left flex flex-col justify-between gap-2"
          :class="selectedSampleId === sample.id 
            ? '!bg-[#FEF3C7] !shadow-[3px_3px_0_0_#0B132B] ring-2 ring-amber-600' 
            : 'bg-white'"
        >
          <div>
            <div class="text-[10px] font-mono font-bold text-amber-800 uppercase tracking-wider">{{ sample.gr_number }}</div>
            <div class="text-xs font-extrabold text-[#0B132B] mt-0.5 line-clamp-1 font-heading">{{ sample.title }}</div>
          </div>
          <div class="text-[10px] text-slate-600 flex items-center justify-between font-medium">
            <span>{{ sample.date }}</span>
            <span class="font-bold text-amber-700">Explain this →</span>
          </div>
        </button>
      </div>
    </div>

    <!-- Custom Textarea & Action Bar -->
    <div class="neo-box bg-white p-5 space-y-3">
      <div class="flex items-center justify-between">
        <label class="text-xs font-bold text-[#0B132B] flex items-center gap-1.5">
          <FileText class="w-4 h-4 text-amber-600" />
          <span>Paste the official text (Marathi or English):</span>
        </label>
        <span class="text-[11px] text-slate-500 font-medium">Paste the official sentences</span>
      </div>

      <textarea
        v-model="inputText"
        rows="6"
        placeholder="Paste a paragraph from an official government order, scheme notice or circular..."
        class="neo-input w-full p-4 text-xs font-mono leading-relaxed"
      ></textarea>

      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2">
        <div class="text-[11px] text-slate-600 font-medium flex items-center gap-1.5">
          <ShieldCheck class="w-3.5 h-3.5 text-emerald-700" />
          <span>Every point includes the exact quote from the original text.</span>
        </div>

        <button
          @click="handleInterpret"
          :disabled="isLoading || !inputText.trim()"
          class="neo-btn neo-btn-saffron px-5 py-2.5 text-xs font-bold disabled:opacity-50"
        >
          <Loader2 v-if="isLoading" class="w-4 h-4 animate-spin" />
          <Sparkles v-else class="w-4 h-4" />
          <span>Explain this order</span>
        </button>
      </div>
    </div>

    <!-- DUAL WORKSPACE: SOURCE TEXT vs CITIZEN ACTION BLUEPRINT -->
    <div v-if="interpretedData" class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      
      <!-- LEFT COLUMN: VERBATIM SOURCE TEXT (40% width) -->
      <div class="lg:col-span-5 bg-slate-900 text-slate-100 rounded-3xl p-6 shadow-md border border-slate-800 space-y-4 sticky top-20">
        <div class="flex items-center justify-between pb-3 border-b border-slate-800">
          <div>
            <div class="flex items-center gap-2">
              <span class="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
              <span class="text-xs font-extrabold uppercase tracking-wider text-slate-300">Official original text</span>
            </div>
            <div class="text-[11px] text-slate-400 mt-0.5">Word-for-word from the department</div>
          </div>
          <span class="text-[10px] font-mono bg-slate-800 text-slate-300 px-2 py-0.5 rounded">
            Original text
          </span>
        </div>

        <div class="space-y-1 text-xs text-slate-300">
          <div class="text-[11px] text-slate-400 font-bold uppercase tracking-wider">Order number:</div>
          <div class="font-mono text-emerald-300 font-bold">{{ interpretedData.gr_reference_number }}</div>
          <div class="text-[11px] text-slate-400 font-medium">{{ interpretedData.issuing_department }}</div>
        </div>

        <!-- Highlightable source viewport -->
        <div id="source-text-container" class="max-h-[500px] overflow-y-auto p-4 rounded-2xl bg-slate-950/80 border border-slate-800 font-mono text-[11px] leading-relaxed space-y-2 select-text">
          <div 
            v-for="(line, idx) in (interpretedData.source_text_verbatim || inputText).split('\n')" 
            :key="idx"
            class="transition-colors duration-300 p-0.5 rounded"
            :class="highlightedQuote && line.toLowerCase().includes(highlightedQuote.toLowerCase().slice(0, 20)) ? 'bg-amber-500/30 text-amber-200 font-bold border-l-2 border-amber-400 pl-1.5' : 'text-slate-300'"
          >
            <span class="text-slate-600 select-none mr-2 font-mono text-[10px]">{{ Number(idx) + 1 }}</span>
            <span>{{ line }}</span>
          </div>
        </div>

        <div class="p-3 rounded-2xl bg-slate-800/80 border border-slate-700/60 text-[11px] text-slate-400">
          <strong>How to use this:</strong> Click <span class="text-amber-300 font-bold">"View source"</span> on the right to find and highlight the exact sentence here.
        </div>
      </div>

      <!-- RIGHT COLUMN: CITIZEN ACTION BLUEPRINT (60% width) -->
      <div class="lg:col-span-7 space-y-5">
        
        <!-- Top Status Banner -->
        <div class="p-4 rounded-2xl bg-indigo-50 border border-indigo-200 text-indigo-950 flex items-center justify-between gap-3 shadow-xs">
          <div class="flex items-center gap-2.5">
            <Sparkles class="w-5 h-5 text-indigo-600 shrink-0" />
            <div>
              <span class="text-xs font-bold text-indigo-900 block">AI explanation (for information only)</span>
              <span class="text-[11px] text-indigo-700">{{ interpretedData.interpreted_by }}</span>
            </div>
          </div>
          <button 
            @click="copyBlueprint" 
            class="px-3 py-1.5 bg-white text-indigo-700 border border-indigo-300 rounded-xl text-xs font-bold flex items-center gap-1 hover:bg-indigo-50 shadow-xs"
          >
            <Check v-if="isCopied" class="w-3.5 h-3.5 text-emerald-600" />
            <Copy v-else class="w-3.5 h-3.5 text-indigo-600" />
            <span>{{ isCopied ? 'Copied!' : 'Copy summary' }}</span>
          </button>
        </div>

        <!-- 1. Plain Language Explanation Card -->
        <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-3">
          <div class="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-500">
            <BookOpen class="w-4 h-4 text-indigo-600" />
            <span>What this order means in plain words:</span>
          </div>
          <p class="text-sm text-slate-800 font-medium leading-relaxed bg-slate-50 p-4 rounded-2xl border border-slate-100">
            {{ interpretedData.plain_language_summary }}
          </p>
        </div>

        <!-- 2. Extracted Eligibility Conditions with Source Quotes -->
        <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
          <h2 class="text-sm font-bold text-slate-900 flex items-center justify-between">
            <span class="flex items-center gap-2">
              <CheckCircle2 class="w-4 h-4 text-emerald-600" />
              Who qualifies
            </span>
            <span class="text-[11px] font-mono text-slate-400">{{ interpretedData.eligibility_conditions?.length || 0 }} points</span>
          </h2>

          <div class="space-y-3">
            <div 
              v-for="(cond, idx) in interpretedData.eligibility_conditions" 
              :key="idx"
              class="p-4 rounded-2xl border border-slate-200 hover:border-slate-300 transition-all space-y-2 bg-slate-50/40"
            >
              <div class="flex items-start justify-between gap-2">
                <span class="text-xs font-bold text-slate-900">{{ cond.condition }}</span>
                <span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold uppercase shrink-0"
                  :class="cond.impact === 'Mandatory' ? 'bg-indigo-100 text-indigo-800' : (cond.impact === 'Exclusion' ? 'bg-rose-100 text-rose-800' : 'bg-emerald-100 text-emerald-800')"
                >
                  {{ cond.impact }}
                </span>
              </div>

              <!-- Verbatim Source Evidence Citation -->
              <div class="pt-2 border-t border-slate-200/60 flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-[11px]">
                <div class="text-slate-600 italic truncate max-w-md">
                  "{{ cond.source_quote }}"
                </div>
                <button
                  @click="highlightInSource(cond.source_quote)"
                  class="text-indigo-600 hover:text-indigo-800 font-bold shrink-0 flex items-center gap-1 text-[10px]"
                >
                  <span>View source 🔍</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 3. Required Documents Checklist -->
        <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
          <h2 class="text-sm font-bold text-slate-900 flex items-center justify-between">
            <span class="flex items-center gap-2">
              <FileText class="w-4 h-4 text-indigo-600" />
              Documents you need
            </span>
            <span class="text-[11px] font-mono text-slate-400">{{ interpretedData.required_documents?.length || 0 }} documents</span>
          </h2>

          <div class="space-y-3">
            <div 
              v-for="(doc, idx) in interpretedData.required_documents" 
              :key="idx"
              class="p-4 rounded-2xl border border-slate-200 space-y-2 bg-slate-50/40"
            >
              <div class="flex items-start justify-between gap-2">
                <div>
                  <div class="font-bold text-slate-900 text-xs">{{ doc.document_name }}</div>
                  <div class="text-[11px] text-slate-500 mt-0.5">Issued by: {{ doc.issuing_authority }}</div>
                </div>
                <button
                  @click="highlightInSource(doc.source_quote)"
                  class="text-indigo-600 hover:text-indigo-800 font-bold shrink-0 text-[10px]"
                >
                  View Quote 🔍
                </button>
              </div>

              <div class="text-[11px] text-slate-500 italic bg-white p-2 rounded-xl border border-slate-100">
                Source: "{{ doc.source_quote }}"
              </div>
            </div>
          </div>
        </div>

        <!-- 4. Deadlines & Timelines -->
        <div v-if="interpretedData.deadlines_and_timelines?.length" class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-3">
          <h2 class="text-sm font-bold text-slate-900 flex items-center gap-2">
            <Clock class="w-4 h-4 text-amber-600" />
            Deadlines
          </h2>

          <div class="space-y-2">
            <div 
              v-for="(d, idx) in interpretedData.deadlines_and_timelines" 
              :key="idx"
              class="p-3.5 rounded-2xl bg-amber-50/60 border border-amber-200 flex items-start justify-between gap-2 text-xs"
            >
              <div>
                <strong class="font-bold text-amber-950 block">{{ d.label }}</strong>
                <span class="text-amber-900">{{ d.timeframe }}</span>
              </div>
              <button
                @click="highlightInSource(d.source_quote)"
                class="text-amber-800 hover:text-amber-950 font-bold shrink-0 text-[10px]"
              >
                Quote 🔍
              </button>
            </div>
          </div>
        </div>

        <!-- 5. Step-by-Step Action Plan -->
        <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
          <h2 class="text-sm font-bold text-slate-900 flex items-center gap-2">
            <Layers class="w-4 h-4 text-indigo-600" />
            What to do, step by step
          </h2>

          <div class="space-y-3">
            <div 
              v-for="step in interpretedData.action_steps" 
              :key="step.step_number"
              class="flex items-start gap-3 p-3.5 rounded-2xl border border-slate-100 bg-slate-50/50"
            >
              <div class="w-6 h-6 rounded-full bg-indigo-600 text-white flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">
                {{ step.step_number }}
              </div>
              <div class="space-y-0.5">
                <div class="text-xs font-bold text-slate-900">{{ step.title }}</div>
                <div class="text-xs text-slate-600">{{ step.action_details }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 6. Clarification Questions -->
        <div v-if="interpretedData.clarification_questions_for_citizen?.length" class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-3">
          <h2 class="text-sm font-bold text-slate-900 flex items-center gap-2">
            <HelpCircle class="w-4 h-4 text-purple-600" />
            Questions to check before you apply
          </h2>

          <ul class="space-y-2 text-xs text-slate-700">
            <li 
              v-for="(q, idx) in interpretedData.clarification_questions_for_citizen" 
              :key="idx"
              class="flex items-start gap-2 bg-purple-50/50 p-2.5 rounded-xl border border-purple-100"
            >
              <span class="text-purple-600 font-bold">•</span>
              <span>{{ q }}</span>
            </li>
          </ul>
        </div>

      </div>

    </div>

  </div>
</template>
