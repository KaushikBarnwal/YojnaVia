<script setup lang="ts">
import { ref } from 'vue';
import { useStudentStore } from '../stores/studentStore';
import { Users, Check, ChevronDown, ChevronUp } from '@lucide/vue';

const store = useStudentStore();
const isExpanded = ref(false);
</script>

<template>
  <div class="bg-[#0B132B] text-white rounded-2xl p-2.5 sm:px-4 border-[1.5px] border-[#0B132B] shadow-[2.5px_2.5px_0_0_#D97706] mb-6 transition-all">
    <!-- Compact Single-Line Header (Default) -->
    <div class="flex flex-wrap items-center justify-between gap-2">
      <div class="flex items-center gap-2">
        <div class="w-6 h-6 rounded-lg bg-[#D97706]/20 border border-[#D97706]/40 flex items-center justify-center text-[#F59E0B]">
          <Users class="w-3.5 h-3.5" />
        </div>
        <span class="text-xs font-black text-slate-100 uppercase tracking-wider">Verified Personas:</span>
      </div>

      <!-- Compact 4 Pills -->
      <div class="flex flex-wrap items-center gap-1.5 flex-1 max-w-3xl">
        <button
          v-for="p in store.personas"
          :key="p.key"
          @click="store.loadPersona(p.key)"
          class="px-3 py-1 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 border-[1.5px] cursor-pointer"
          :class="store.activePersonaKey === p.key
            ? 'bg-[#D97706] text-white border-white shadow-[1.5px_1.5px_0_0_#060A14]'
            : 'bg-[#1C2541] hover:bg-[#253256] text-slate-200 border-[#3A506B]/50'"
        >
          <span>{{ p.name.split(' (')[0] }}</span>
          <span class="text-[10px] opacity-80 hidden sm:inline">({{ p.name.includes('OBC') ? 'OBC' : (p.name.includes('EBC') ? 'Open/EBC' : (p.name.includes('SC') ? 'SC' : 'Borderline')) }})</span>
          <Check v-if="store.activePersonaKey === p.key" class="w-3.5 h-3.5 text-white" />
        </button>
      </div>

      <!-- Quick Expand Details Toggle -->
      <button 
        @click="isExpanded = !isExpanded"
        class="text-[11px] text-amber-300 hover:text-white flex items-center gap-1 transition-colors px-2.5 py-1 rounded-lg hover:bg-[#1C2541] cursor-pointer font-bold"
      >
        <span>{{ isExpanded ? 'Hide Details' : 'View Scenarios' }}</span>
        <ChevronUp v-if="isExpanded" class="w-3 h-3" />
        <ChevronDown v-else class="w-3 h-3" />
      </button>
    </div>

    <!-- Collapsible Detailed Description Cards -->
    <div v-if="isExpanded" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5 mt-3 pt-3 border-t border-[#1C2541] animate-in fade-in">
      <div
        v-for="p in store.personas"
        :key="'desc-' + p.key"
        @click="store.loadPersona(p.key)"
        class="cursor-pointer p-3 rounded-xl border-[1.5px] transition-all"
        :class="store.activePersonaKey === p.key
          ? 'bg-[#1C2541] border-[#F59E0B] shadow-[2px_2px_0_0_#F59E0B]'
          : 'bg-[#0F172A] border-[#1E293B] hover:border-[#3A506B]'"
      >
        <div class="font-bold text-xs text-white mb-0.5">{{ p.name }}</div>
        <div class="text-[10px] text-amber-400 font-extrabold mb-1 uppercase tracking-wide">{{ p.tag }}</div>
        <p class="text-[11px] text-slate-300 leading-snug line-clamp-2">{{ p.details }}</p>
      </div>
    </div>
  </div>
</template>
