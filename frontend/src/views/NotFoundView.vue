<script setup lang="ts">
import { ArrowLeft, Sparkles, Scale, AlertTriangle } from '@lucide/vue';
</script>

<template>
  <div class="min-h-[75vh] flex items-center justify-center px-4 py-16">
    <div class="max-w-xl w-full neo-box p-8 sm:p-12 text-center bg-white shadow-[5px_5px_0_0_#0B132B]">
      <!-- 404 Stamp -->
      <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full border-[1.5px] border-[#0B132B] bg-rose-50 text-rose-800 text-xs font-black uppercase tracking-wider mb-4 shadow-[1.5px_1.5px_0_0_#0B132B]">
        <AlertTriangle class="w-3.5 h-3.5" />
        <span>Statutory Code 404 • Not Found</span>
      </div>

      <h1 class="text-4xl sm:text-6xl font-black text-[#0B132B] font-heading tracking-tight leading-none mb-3">
        404
      </h1>

      <h2 class="text-lg sm:text-xl font-extrabold text-[#0B132B] mb-2 font-heading">
        Gazette Page or Scheme Not Found
      </h2>

      <p class="text-xs sm:text-sm text-slate-600 font-medium leading-relaxed max-w-md mx-auto mb-8">
        The link you followed does not correspond to an active statutory route in the Maharashtra public services catalog. It may have been updated or relocated.
      </p>

      <!-- Quick Action Buttons -->
      <div class="flex flex-col sm:flex-row items-center justify-center gap-3">
        <router-link
          to="/app"
          class="neo-btn neo-btn-saffron w-full sm:w-auto px-5 py-2.5 text-xs font-bold"
        >
          <Sparkles class="w-4 h-4" />
          <span>Launch AI Scheme Intake</span>
        </router-link>

        <router-link
          to="/schemes"
          class="neo-btn neo-btn-paper w-full sm:w-auto px-5 py-2.5 text-xs font-bold text-[#0B132B]"
        >
          <Scale class="w-4 h-4 text-amber-600" />
          <span>View All 15 Schemes</span>
        </router-link>

        <router-link
          to="/"
          class="neo-btn neo-btn-navy w-full sm:w-auto px-5 py-2.5 text-xs font-bold"
        >
          <ArrowLeft class="w-4 h-4" />
          <span>Return Home</span>
        </router-link>
      </div>

      <!-- Assistance note with clickable email -->
      <div class="mt-8 pt-6 border-t border-[#0B132B]/10 text-xs text-slate-500 font-medium">
        Need assistance or found a broken government gazette citation?
        <br />
        Contact the civil tech helpdesk at
        <a href="mailto:support@yojnavia.in" class="font-bold text-amber-700 hover:underline">
          support@yojnavia.in
        </a>
      </div>
    </div>
  </div>
</template>
