<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { ShieldCheck, ArrowRight, X } from '@lucide/vue';

const isVisible = ref(false);

onMounted(() => {
  const consent = localStorage.getItem('YojnaVia_cookie_consent');
  if (!consent) {
    // Show banner after short delay
    setTimeout(() => {
      isVisible.value = true;
    }, 1000);
  }
});

function acceptConsent() {
  localStorage.setItem('YojnaVia_cookie_consent', 'accepted');
  isVisible.value = false;
}
</script>

<template>
  <transition
    enter-active-class="transition duration-300 ease-out"
    enter-from-class="transform translate-y-6 opacity-0"
    enter-to-class="transform translate-y-0 opacity-100"
    leave-active-class="transition duration-200 ease-in"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0 translate-y-4"
  >
    <div
      v-if="isVisible"
      class="fixed bottom-4 left-4 right-4 sm:left-auto sm:right-6 sm:max-w-md z-[90] p-4 rounded-2xl bg-white border-[1.5px] border-[#0B132B] shadow-[4px_4px_0_0_#0B132B]"
    >
      <div class="flex items-start justify-between gap-3 mb-2">
        <div class="flex items-center gap-2">
          <div class="w-6 h-6 rounded-lg bg-emerald-100 border border-emerald-600 flex items-center justify-center text-emerald-800">
            <ShieldCheck class="w-3.5 h-3.5" />
          </div>
          <span class="text-xs font-black text-[#0B132B] uppercase tracking-wider">
            Privacy notice
          </span>
        </div>
        <button
          @click="acceptConsent"
          class="text-slate-400 hover:text-slate-700 cursor-pointer p-0.5"
          aria-label="Dismiss banner"
        >
          <X class="w-3.5 h-3.5" />
        </button>
      </div>

      <p class="text-xs text-slate-600 font-medium leading-relaxed mb-3">
        YojnaVia saves small bits of data only on your device, to remember your search. We do not use ad cookies, third-party trackers or biometric data.
      </p>

      <div class="flex items-center justify-between gap-2 pt-1 border-t border-slate-100">
        <router-link
          to="/privacy"
          class="text-[11px] font-bold text-amber-700 hover:underline inline-flex items-center gap-1"
        >
          <span>Read our privacy policy</span>
          <ArrowRight class="w-2.5 h-2.5" />
        </router-link>

        <button
          @click="acceptConsent"
          class="neo-btn neo-btn-navy py-1.5 px-3 text-xs font-bold"
        >
          <span>Accept & Continue</span>
        </button>
      </div>
    </div>
  </transition>
</template>
