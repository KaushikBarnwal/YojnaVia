<script setup lang="ts">
import { ShieldCheck, Lock, CheckCircle2, ArrowLeft } from '@lucide/vue';
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
      <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-100 text-emerald-900 border border-emerald-600 text-xs font-black uppercase tracking-wider">
        <ShieldCheck class="w-4 h-4 text-emerald-700" />
        <span>Sovereign Citizen Privacy Architecture</span>
      </div>

      <h1 class="text-2xl sm:text-4xl font-black text-[#0B132B] font-heading tracking-tight">
        Citizen Privacy & Zero-Aadhaar Sovereign Policy
      </h1>

      <p class="text-xs sm:text-sm text-slate-600 font-medium leading-relaxed">
        Last Updated: November 2024 • Enforced under Maharashtra Public Services (Right to Services) Framework
      </p>
    </div>

    <!-- Core Clauses -->
    <div class="space-y-6 text-xs sm:text-sm text-slate-700 font-medium leading-relaxed">

      <!-- Clause 1 -->
      <div class="neo-box p-6 bg-white space-y-2.5">
        <h2 class="text-base sm:text-lg font-black text-[#0B132B] font-heading flex items-center gap-2">
          <Lock class="w-4 h-4 text-emerald-600" />
          1. Zero-Aadhaar Sovereign Data Guarantee
        </h2>
        <p>
          YOJNAVIA has a strict, programmatic <strong>Zero-Sensitive Identifier Policy</strong>. The application will never ask for, collect, store, or transmit your 12-digit Aadhaar number, PAN card number, bank passwords, or biometric credentials.
        </p>
        <p>
          Official government submission on MahaDBT or Aaple Sarkar will require your official authentication through their official portals; however, on YOJNAVIA, all scheme matching operates purely on coarsened criteria (e.g. annual family income bracket, educational level, and district).
        </p>
      </div>

      <!-- Clause 2 -->
      <div class="neo-box p-6 bg-white space-y-2.5">
        <h2 class="text-base sm:text-lg font-black text-[#0B132B] font-heading flex items-center gap-2">
          <CheckCircle2 class="w-4 h-4 text-amber-600" />
          2. Ephemeral & Local Browser Session Tokens
        </h2>
        <p>
          Your discovery session is identified by a client-side pseudonymous token stored only within your browser’s local storage. This enables you to navigate between eligibility criteria, document dependency graphs, and what-if simulators without registering a phone number or creating a password.
        </p>
        <p>
          You may reset or wipe your session at any time by clicking the "Reset" button in the navigation bar.
        </p>
      </div>

      <!-- Clause 3 -->
      <div class="neo-box p-6 bg-white space-y-2.5">
        <h2 class="text-base sm:text-lg font-black text-[#0B132B] font-heading flex items-center gap-2">
          <CheckCircle2 class="w-4 h-4 text-indigo-600" />
          3. Zero Advertising & Third-Party Trackers
        </h2>
        <p>
          YOJNAVIA does not sell, lease, or broker citizen demographic data to financial institutions, private loan providers, or advertising networks. We use zero third-party commercial analytics scripts.
        </p>
      </div>

      <!-- Clause 4 -->
      <div class="neo-box p-6 bg-white space-y-2.5">
        <h2 class="text-base sm:text-lg font-black text-[#0B132B] font-heading flex items-center gap-2">
          <CheckCircle2 class="w-4 h-4 text-blue-600" />
          4. Contact & Sovereign Data Officer
        </h2>
        <p>
          If you have questions regarding data retention or statutory compliance under the Maharashtra Right to Services Act 2015, please contact our civil tech team at:
        </p>
        <p class="font-bold text-[#0B132B]">
          Email: <a href="mailto:privacy@yojnavia.in" class="text-amber-700 underline">privacy@yojnavia.in</a>
        </p>
      </div>

    </div>
  </div>
</template>
