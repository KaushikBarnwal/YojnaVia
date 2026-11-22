<script setup lang="ts">
import { ref } from 'vue';
import { useStudentStore } from '../stores/studentStore';
import { Users, Check, ChevronDown, ChevronUp } from '@lucide/vue';

const store = useStudentStore();
const isExpanded = ref(false);
</script>

<template>
  <div class="bg-slate-900 text-white rounded-2xl p-2.5 sm:px-4 shadow-sm border border-slate-800 mb-6 transition-all">
    <!-- Compact Single-Line Header (Default) -->
    <div class="flex flex-wrap items-center justify-between gap-2">
      <div class="flex items-center gap-2">
        <Users class="w-4 h-4 text-indigo-400 shrink-0" />
        <span class="text-xs font-bold text-slate-200 uppercase tracking-wider">Demo Scenarios:</span>
      </div>

      <!-- Compact 4 Pills -->
      <div class="flex flex-wrap items-center gap-1.5 flex-1 max-w-3xl">
        <button
          v-for="p in store.personas"
          :key="p.key"
          @click="store.loadPersona(p.key)"
          class="px-3 py-1 rounded-xl text-xs font-semibold transition-all flex items-center gap-1.5 border"
          :class="store.activePersonaKey === p.key
            ? 'bg-indigo-600 text-white border-indigo-400 shadow-sm ring-1 ring-indigo-400'
            : 'bg-slate-800/80 hover:bg-slate-700 text-slate-300 border-slate-700/60'"
        >
          <span>{{ p.name.split(' (')[0] }}</span>
          <span class="text-[10px] opacity-75 hidden sm:inline">({{ p.name.includes('OBC') ? 'OBC' : (p.name.includes('EBC') ? 'Open/EBC' : (p.name.includes('SC') ? 'SC' : 'Borderline')) }})</span>
          <Check v-if="store.activePersonaKey === p.key" class="w-3 h-3 text-emerald-400" />
        </button>
      </div>

      <!-- Quick Expand Details Toggle -->
      <button 
        @click="isExpanded = !isExpanded"
        class="text-[11px] text-slate-400 hover:text-slate-200 flex items-center gap-1 transition-colors px-2 py-0.5 rounded-lg hover:bg-slate-800"
      >
        <span>{{ isExpanded ? 'Hide Info' : 'Details' }}</span>
        <ChevronUp v-if="isExpanded" class="w-3 h-3" />
        <ChevronDown v-else class="w-3 h-3" />
      </button>
    </div>

    <!-- Collapsible Detailed Description Cards -->
    <div v-if="isExpanded" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5 mt-3 pt-3 border-t border-slate-800 animate-in fade-in">
      <div
        v-for="p in store.personas"
        :key="'desc-' + p.key"
        @click="store.loadPersona(p.key)"
        class="cursor-pointer p-2.5 rounded-xl border transition-all"
        :class="store.activePersonaKey === p.key
          ? 'bg-indigo-950/60 border-indigo-500'
          : 'bg-slate-800/40 border-slate-700/40 hover:bg-slate-800/80'"
      >
        <div class="font-bold text-xs text-white mb-0.5">{{ p.name }}</div>
        <div class="text-[10px] text-amber-300 font-medium mb-1">{{ p.tag }}</div>
        <p class="text-[11px] text-slate-400 leading-snug line-clamp-2">{{ p.details }}</p>
      </div>
    </div>
  </div>
</template>
