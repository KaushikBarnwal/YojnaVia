<script setup lang="ts">
import { toasts, removeToast } from '../utils/toast';
import { CheckCircle2, AlertCircle, Info, X } from '@lucide/vue';
</script>

<template>
  <div class="fixed top-20 right-4 sm:right-6 z-[100] flex flex-col gap-2 pointer-events-none max-w-sm w-full">
    <transition-group
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="transform translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-4"
      enter-to-class="transform translate-y-0 opacity-100 sm:translate-x-0"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="pointer-events-auto p-3.5 rounded-xl border-[1.5px] border-[#0B132B] shadow-[3px_3px_0_0_#0B132B] flex items-center justify-between gap-3 text-xs font-bold"
        :class="{
          'bg-[#ECFDF5] text-emerald-950': toast.type === 'success',
          'bg-[#FFF1F2] text-rose-950': toast.type === 'error',
          'bg-[#EFF6FF] text-blue-950': toast.type === 'info',
        }"
      >
        <div class="flex items-center gap-2 min-w-0">
          <CheckCircle2 v-if="toast.type === 'success'" class="w-4 h-4 text-emerald-700 shrink-0" />
          <AlertCircle v-else-if="toast.type === 'error'" class="w-4 h-4 text-rose-700 shrink-0" />
          <Info v-else class="w-4 h-4 text-blue-700 shrink-0" />
          <span class="truncate">{{ toast.message }}</span>
        </div>
        <button
          @click="removeToast(toast.id)"
          class="p-1 hover:opacity-75 rounded transition-opacity cursor-pointer shrink-0"
          aria-label="Close"
        >
          <X class="w-3.5 h-3.5" />
        </button>
      </div>
    </transition-group>
  </div>
</template>
