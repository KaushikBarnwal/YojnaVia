<script setup lang="ts">
import { Scale, AlertTriangle, CheckCircle2, ArrowLeft, ShieldAlert } from '@lucide/vue';
</script>

<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
    <!-- Back to Discovery -->
    <div>
      <router-link
        to="/app"
        class="neo-btn neo-btn-paper px-3 py-1.5 text-xs font-bold text-[#0B132B]"
      >
        <ArrowLeft class="w-3.5 h-3.5" />
        <span>Back to Application</span>
      </router-link>
    </div>

    <!-- Header Banner -->
    <div class="neo-box p-6 sm:p-8 bg-white space-y-3">
      <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-100 text-amber-900 border border-amber-600 text-xs font-black uppercase tracking-wider">
        <Scale class="w-4 h-4 text-amber-700" />
        <span>Official legal terms</span>
      </div>

      <h1 class="text-2xl sm:text-4xl font-black text-[#0B132B] font-heading tracking-tight">
        Terms of use and important disclaimers
      </h1>

      <p class="text-xs sm:text-sm text-slate-600 font-medium leading-relaxed">
        Effective: Academic Year 2024–2025 • The rules for using YojnaVia
      </p>
    </div>

    <!-- Core Clauses -->
    <div class="space-y-6 text-xs sm:text-sm text-slate-700 font-medium leading-relaxed">

      <!-- Disclaimer 1 -->
      <div class="neo-box p-6 bg-white space-y-2.5">
        <h2 class="text-base sm:text-lg font-black text-[#0B132B] font-heading flex items-center gap-2">
          <AlertTriangle class="w-4 h-4 text-amber-600" />
          1. Eligibility is an estimate, never a promise
        </h2>
        <p class="font-bold text-[#0B132B]">In short: this is an estimate only. The government makes the final decision.</p>
        <p>
          YojnaVia gives an <strong>information-only estimate</strong>, based on published Government of Maharashtra orders (GRs) and central welfare rules.
        </p>
        <p class="bg-amber-50 p-3 rounded-xl border border-amber-300 text-amber-950 font-bold">
          "Likely eligible" means you appear to qualify based on the details you gave. Only the government department, desk officer or scrutiny committee can approve, sanction and send money.
        </p>
      </div>

      <!-- Disclaimer 2 -->
      <div class="neo-box p-6 bg-white space-y-2.5">
        <h2 class="text-base sm:text-lg font-black text-[#0B132B] font-heading flex items-center gap-2">
          <CheckCircle2 class="w-4 h-4 text-emerald-600" />
          2. Free to use: no agents, no middlemen fees
        </h2>
        <p class="font-bold text-[#0B132B]">In short: using YojnaVia is free. Pay official fees only on government websites.</p>
        <p>
          YojnaVia works to stop unauthorised middlemen from exploiting citizens. Using YojnaVia to find schemes, make document checklists and read government orders is completely free.
        </p>
        <p>
          Official fees for certificates (such as Tahsildar stamp charges on Aaple Sarkar) are set by the state government. Pay them only through official state payment systems.
        </p>
      </div>

      <!-- Disclaimer 3 -->
      <div class="neo-box p-6 bg-white space-y-2.5">
        <h2 class="text-base sm:text-lg font-black text-[#0B132B] font-heading flex items-center gap-2">
          <Scale class="w-4 h-4 text-indigo-600" />
          3. Maharashtra Right to Services (RTS) Act 2015: processing times
        </h2>
        <p class="font-bold text-[#0B132B]">In short: processing times are guides, and they can change during busy periods.</p>
        <p>
          The processing times shown in the document guide and application tracker follow the Maharashtra Right to Public Services Act 2015. Departments try to meet them, but times may vary in busy admission periods.
        </p>
      </div>

      <!-- Disclaimer 4 -->
      <div class="neo-box p-6 bg-white space-y-2.5">
        <h2 class="text-base sm:text-lg font-black text-[#0B132B] font-heading flex items-center gap-2">
          <ShieldAlert class="w-4 h-4 text-blue-600" />
          4. Contact us
        </h2>
        <p class="font-bold text-[#0B132B]">In short: email us with questions about these terms.</p>
        <p>
          For questions about these terms, or about partnering with Common Service Centres (CSCs), email us at:
        </p>
        <p class="font-bold text-[#0B132B]">
          Email: <a href="mailto:barnwalkaushik@gmail.com" class="text-amber-700 underline">barnwalkaushik@gmail.com</a>
        </p>
      </div>

    </div>
  </div>
</template>
