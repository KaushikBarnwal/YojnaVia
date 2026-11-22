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
        <span>Your privacy, explained</span>
      </div>

      <h1 class="text-2xl sm:text-4xl font-black text-[#0B132B] font-heading tracking-tight">
        Privacy policy: no Aadhaar needed
      </h1>

      <p class="text-xs sm:text-sm text-slate-600 font-medium leading-relaxed">
        Last updated: November 2024 • Enforced under the Maharashtra Right to Services (RTS) framework
      </p>
    </div>

    <!-- Core Clauses -->
    <div class="space-y-6 text-xs sm:text-sm text-slate-700 font-medium leading-relaxed">

      <!-- Clause 1 -->
      <div class="neo-box p-6 bg-white space-y-2.5">
        <h2 class="text-base sm:text-lg font-black text-[#0B132B] font-heading flex items-center gap-2">
          <Lock class="w-4 h-4 text-emerald-600" />
          1. We never ask for your Aadhaar
        </h2>
        <p class="font-bold text-[#0B132B]">In short: we never ask for Aadhaar, PAN, bank passwords or biometric details.</p>
        <p>
          YojnaVia has a firm rule: <strong>we never ask for sensitive identity numbers</strong>. We will never ask for, store or send your 12-digit Aadhaar number, PAN card number, bank passwords or biometric details.
        </p>
        <p>
          On MahaDBT or Aaple Sarkar, the official websites will ask you to verify yourself. On YojnaVia, we only match schemes using broad details, such as yearly family income range, education level and district.
        </p>
      </div>

      <!-- Clause 2 -->
      <div class="neo-box p-6 bg-white space-y-2.5">
        <h2 class="text-base sm:text-lg font-black text-[#0B132B] font-heading flex items-center gap-2">
          <CheckCircle2 class="w-4 h-4 text-amber-600" />
          2. Your session is saved only in your browser
        </h2>
        <p class="font-bold text-[#0B132B]">In short: your session stays on this device, and you can clear it anytime.</p>
        <p>
          Your search session is kept only in your browser’s storage, under a random code rather than your name. This lets you move between pages without a phone number or password.
        </p>
        <p>
          You can clear your session at any time by clicking the "Reset" button in the menu bar at the top.
        </p>
      </div>

      <!-- Clause 3 -->
      <div class="neo-box p-6 bg-white space-y-2.5">
        <h2 class="text-base sm:text-lg font-black text-[#0B132B] font-heading flex items-center gap-2">
          <CheckCircle2 class="w-4 h-4 text-indigo-600" />
          3. No ads and no outside tracking
        </h2>
        <p class="font-bold text-[#0B132B]">In short: we do not sell your data or show you ads.</p>
        <p>
          YojnaVia does not sell or share your personal details with banks, loan companies or advertisers. We do not use outside tracking tools for marketing.
        </p>
      </div>

      <!-- Clause 4 -->
      <div class="neo-box p-6 bg-white space-y-2.5">
        <h2 class="text-base sm:text-lg font-black text-[#0B132B] font-heading flex items-center gap-2">
          <CheckCircle2 class="w-4 h-4 text-blue-600" />
          4. How to contact us about your data
        </h2>
        <p class="font-bold text-[#0B132B]">In short: email us if you have questions about your data.</p>
        <p>
          If you have questions about how long we keep your data, or about the Maharashtra Right to Services Act 2015, email our team:
        </p>
        <p class="font-bold text-[#0B132B]">
          Email: <a href="mailto:barnwalkaushik@gmail.com" class="text-amber-700 underline">barnwalkaushik@gmail.com</a>
        </p>
      </div>

    </div>
  </div>
</template>
