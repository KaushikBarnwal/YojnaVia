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
        <span>Public Legal Framework</span>
      </div>

      <h1 class="text-2xl sm:text-4xl font-black text-[#0B132B] font-heading tracking-tight">
        Terms of Service & Statutory Disclaimers
      </h1>

      <p class="text-xs sm:text-sm text-slate-600 font-medium leading-relaxed">
        Effective: Academic Year 2024–2025 • Governing the YojnaVia Public Welfare Navigation Engine
      </p>
    </div>

    <!-- Core Clauses -->
    <div class="space-y-6 text-xs sm:text-sm text-slate-700 font-medium leading-relaxed">

      <!-- Disclaimer 1 -->
      <div class="neo-box p-6 bg-white space-y-2.5">
        <h2 class="text-base sm:text-lg font-black text-[#0B132B] font-heading flex items-center gap-2">
          <AlertTriangle class="w-4 h-4 text-amber-600" />
          1. Statutory Eligibility Estimate (Never Guaranteed)
        </h2>
        <p>
          YojnaVia provides an <strong>informational statutory estimate</strong> derived deterministically from published Government Resolutions (GRs) of the Government of Maharashtra and central welfare guidelines.
        </p>
        <p class="bg-amber-50 p-3 rounded-xl border border-amber-300 text-amber-950 font-bold">
          Eligibility evaluations indicate that a citizen is "likely eligible" based on provided criteria. Final approval, sanction, and fund disbursement remain under the sole constitutional authority of the respective government department, desk officer, or scrutinizing committee.
        </p>
      </div>

      <!-- Disclaimer 2 -->
      <div class="neo-box p-6 bg-white space-y-2.5">
        <h2 class="text-base sm:text-lg font-black text-[#0B132B] font-heading flex items-center gap-2">
          <CheckCircle2 class="w-4 h-4 text-emerald-600" />
          2. Free Civic Service — No Middlemen / No Agent Fees
        </h2>
        <p>
          YojnaVia is dedicated to eliminating the exploitation of citizens by unauthorized middlemen. Using YojnaVia to discover schemes, generate document checklists, and inspect Government Resolutions is 100% free of charge.
        </p>
        <p>
          Official government fees for certificate issuance (such as Tahsildar stamp charges on Aaple Sarkar) are defined by the state government and must be paid only through official state gateways.
        </p>
      </div>

      <!-- Disclaimer 3 -->
      <div class="neo-box p-6 bg-white space-y-2.5">
        <h2 class="text-base sm:text-lg font-black text-[#0B132B] font-heading flex items-center gap-2">
          <Scale class="w-4 h-4 text-indigo-600" />
          3. Maharashtra Right to Services (RTS) Act 2015 SLA Guidelines
        </h2>
        <p>
          Service Level Agreements (SLAs) shown in the document dependency graph and application tracker reflect statutory timelines under the Maharashtra Right to Public Services Act 2015. While departments strive to meet these deadlines, processing times may vary during peak admission cycles.
        </p>
      </div>

      <!-- Disclaimer 4 -->
      <div class="neo-box p-6 bg-white space-y-2.5">
        <h2 class="text-base sm:text-lg font-black text-[#0B132B] font-heading flex items-center gap-2">
          <ShieldAlert class="w-4 h-4 text-blue-600" />
          4. Contact & Inquiries
        </h2>
        <p>
          For questions regarding the terms of service or institutional partnerships with Common Service Centers (CSCs), email us at:
        </p>
        <p class="font-bold text-[#0B132B]">
          Email: <a href="mailto:support@YojnaVia.in" class="text-amber-700 underline">support@YojnaVia.in</a>
        </p>
      </div>

    </div>
  </div>
</template>
