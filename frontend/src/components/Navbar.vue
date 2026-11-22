<script setup lang="ts">
import { useRoute } from 'vue-router';
import { useStudentStore } from '../stores/studentStore';
import { t } from '../utils/i18n';
import { 
  Sparkles, 
  UserCheck, 
  Award, 
  FileText, 
  CheckCircle2, 
  Sliders,
  Users
} from '@lucide/vue';

const route = useRoute();
const store = useStudentStore();
</script>

<template>
  <header class="bg-white/95 backdrop-blur-md border-b border-slate-200 sticky top-0 z-40 shadow-xs">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16 gap-4">
        
        <!-- Brand -->
        <router-link to="/" class="flex items-center gap-2.5 group shrink-0">
          <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-blue-500 flex items-center justify-center text-white shadow-sm group-hover:scale-105 transition-transform">
            <Sparkles class="w-4 h-4" />
          </div>
          <div class="flex items-center gap-2">
            <span class="text-lg font-black tracking-tight text-slate-900">YOJNAVIA</span>
            <span class="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
              Maharashtra
            </span>
          </div>
        </router-link>

        <!-- Main Navigation Links (Clean & Human) -->
        <nav class="hidden md:flex items-center gap-1">
          <router-link
            to="/"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-colors"
            :class="route.path === '/' ? 'bg-indigo-50 text-indigo-700' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'"
          >
            <Sparkles class="w-3.5 h-3.5" />
            <span>{{ t('nav_discovery', store.locale) }}</span>
          </router-link>

          <router-link
            to="/review"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-colors relative"
            :class="route.path === '/review' ? 'bg-indigo-50 text-indigo-700' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'"
          >
            <UserCheck class="w-3.5 h-3.5" />
            <span>{{ t('nav_profile', store.locale) }}</span>
            <span v-if="store.profile && !store.profile.is_confirmed" class="w-1.5 h-1.5 rounded-full bg-amber-500 absolute top-1.5 right-1.5 animate-pulse"></span>
          </router-link>

          <router-link
            to="/schemes"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-colors"
            :class="route.path === '/schemes' ? 'bg-indigo-50 text-indigo-700' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'"
          >
            <Award class="w-3.5 h-3.5" />
            <span>{{ t('nav_schemes', store.locale) }}</span>
            <span v-if="store.evaluationSummary?.likely_eligible" class="text-[10px] px-1.5 py-0.2 rounded-full bg-emerald-100 text-emerald-800 font-extrabold">
              {{ store.evaluationSummary.likely_eligible }}
            </span>
          </router-link>

          <router-link
            to="/family"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-colors"
            :class="route.path === '/family' ? 'bg-indigo-50 text-indigo-700' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'"
          >
            <Users class="w-3.5 h-3.5" />
            <span>Family Benefits</span>
          </router-link>

          <router-link
            to="/documents"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-colors"
            :class="route.path === '/documents' ? 'bg-indigo-50 text-indigo-700' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'"
          >
            <FileText class="w-3.5 h-3.5" />
            <span>{{ t('nav_documents', store.locale) }}</span>
          </router-link>

          <router-link
            to="/tracker"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-colors"
            :class="route.path === '/tracker' ? 'bg-indigo-50 text-indigo-700' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'"
          >
            <CheckCircle2 class="w-3.5 h-3.5" />
            <span>{{ t('nav_tracker', store.locale) }}</span>
            <span v-if="store.trackedApplications.length > 0" class="text-[10px] px-1.5 py-0.2 rounded-full bg-indigo-100 text-indigo-800 font-extrabold">
              {{ store.trackedApplications.length }}
            </span>
          </router-link>
        </nav>

        <!-- Right Controls: Language & Admin -->
        <div class="flex items-center gap-2">
          <!-- 3-Language Selector -->
          <div class="flex items-center bg-slate-100 rounded-xl p-0.5 border border-slate-200 text-xs font-bold">
            <button
              @click="store.setLocale('en')"
              class="px-2 py-0.5 rounded-lg transition-all"
              :class="store.locale === 'en' ? 'bg-white text-indigo-700 shadow-xs' : 'text-slate-500 hover:text-slate-800'"
            >
              EN
            </button>
            <button
              @click="store.setLocale('mr')"
              class="px-2 py-0.5 rounded-lg transition-all"
              :class="store.locale === 'mr' ? 'bg-white text-indigo-700 shadow-xs' : 'text-slate-500 hover:text-slate-800'"
            >
              मराठी
            </button>
            <button
              @click="store.setLocale('hi')"
              class="px-2 py-0.5 rounded-lg transition-all"
              :class="store.locale === 'hi' ? 'bg-white text-indigo-700 shadow-xs' : 'text-slate-500 hover:text-slate-800'"
            >
              हिंदी
            </button>
          </div>

          <!-- Admin Portal Link -->
          <router-link
            to="/admin-portal"
            class="flex items-center gap-1 px-2.5 py-1 rounded-xl text-xs font-bold transition-all border"
            :class="route.path === '/admin-portal' 
              ? 'bg-indigo-600 text-white border-indigo-600 shadow-xs' 
              : 'bg-slate-50 hover:bg-slate-100 text-slate-700 border-slate-200'"
          >
            <Sliders class="w-3 h-3" />
            <span class="hidden sm:inline">Admin</span>
          </router-link>
        </div>

      </div>
    </div>
  </header>
</template>
