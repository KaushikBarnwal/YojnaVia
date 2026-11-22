<script setup lang="ts">
import { ref, watch } from 'vue';
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
  Users, 
  Settings, 
  BookOpen, 
  BarChart3,
  Menu,
  X,
  ShieldCheck,
  Bell,
  Building2
} from '@lucide/vue';

const route = useRoute();
const store = useStudentStore();
const isMobileMenuOpen = ref(false);

watch(() => route.path, () => {
  isMobileMenuOpen.value = false;
});
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
        <nav class="hidden xl:flex items-center gap-1">
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
            <span>{{ t('nav_family', store.locale) }}</span>
          </router-link>

          <router-link
            to="/what-if"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-colors"
            :class="route.path === '/what-if' ? 'bg-indigo-50 text-indigo-700' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'"
          >
            <Sliders class="w-3.5 h-3.5" />
            <span>{{ t('nav_what_if', store.locale) }}</span>
          </router-link>

          <router-link
            to="/gr-interpreter"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-colors"
            :class="route.path === '/gr-interpreter' ? 'bg-indigo-50 text-indigo-700' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'"
          >
            <BookOpen class="w-3.5 h-3.5" />
            <span>{{ t('nav_gr_decoder', store.locale) }}</span>
          </router-link>

          <router-link
            to="/community-gap"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-colors"
            :class="route.path === '/community-gap' ? 'bg-indigo-50 text-indigo-700' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'"
          >
            <BarChart3 class="w-3.5 h-3.5" />
            <span>{{ t('nav_insights', store.locale) }}</span>
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

          <router-link
            to="/notifications"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-colors"
            :class="route.path === '/notifications' ? 'bg-indigo-50 text-indigo-700' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'"
          >
            <Bell class="w-3.5 h-3.5" />
            <span>{{ t('nav_notifications', store.locale) }}</span>
          </router-link>
        </nav>

        <!-- Right Controls: Language, Admin & Mobile Hamburger -->
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

          <!-- CSC Counselor Desk Link -->
          <router-link
            to="/counselor"
            class="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-xl text-xs font-bold transition-all border"
            :class="route.path === '/counselor' 
              ? 'bg-amber-600 text-white border-amber-600 shadow-xs' 
              : 'bg-amber-50 hover:bg-amber-100 text-amber-900 border-amber-200'"
          >
            <Building2 class="w-3.5 h-3.5" :class="route.path === '/counselor' ? 'text-white' : 'text-amber-700'" />
            <span>CSC Desk</span>
          </router-link>

          <!-- Admin Portal Link -->
          <router-link
            to="/admin-portal"
            class="hidden sm:flex items-center gap-1 px-2.5 py-1 rounded-xl text-xs font-bold transition-all border"
            :class="route.path === '/admin-portal' 
              ? 'bg-indigo-600 text-white border-indigo-600 shadow-xs' 
              : 'bg-slate-50 hover:bg-slate-100 text-slate-700 border-slate-200'"
          >
            <Settings class="w-3 h-3" />
            <span>Admin</span>
          </router-link>

          <!-- Mobile / Tablet Hamburger Toggle Button -->
          <button
            @click="isMobileMenuOpen = !isMobileMenuOpen"
            class="xl:hidden p-1.5 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 border border-slate-200 transition-colors"
            aria-label="Toggle navigation menu"
          >
            <X v-if="isMobileMenuOpen" class="w-5 h-5 text-slate-800" />
            <Menu v-else class="w-5 h-5 text-slate-800" />
          </button>
        </div>

      </div>
    </div>

    <!-- Mobile Slide-Down Menu Drawer -->
    <div 
      v-if="isMobileMenuOpen" 
      class="xl:hidden bg-white border-b border-slate-200 px-4 pt-3 pb-6 shadow-xl space-y-3 animate-in slide-in-from-top-2 duration-200"
    >
      <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider px-2">
        Main Navigation & Citizen Tools
      </div>

      <div class="grid grid-cols-2 gap-2 text-xs font-bold">
        <router-link
          to="/"
          class="flex items-center gap-2 p-2.5 rounded-xl border transition-colors"
          :class="route.path === '/' ? 'bg-indigo-50 text-indigo-700 border-indigo-200' : 'bg-slate-50 text-slate-700 border-slate-200'"
        >
          <Sparkles class="w-4 h-4 text-indigo-600" />
          <span>{{ t('nav_discovery', store.locale) }}</span>
        </router-link>

        <router-link
          to="/review"
          class="flex items-center gap-2 p-2.5 rounded-xl border transition-colors"
          :class="route.path === '/review' ? 'bg-indigo-50 text-indigo-700 border-indigo-200' : 'bg-slate-50 text-slate-700 border-slate-200'"
        >
          <UserCheck class="w-4 h-4 text-indigo-600" />
          <span>{{ t('nav_profile', store.locale) }}</span>
        </router-link>

        <router-link
          to="/schemes"
          class="flex items-center gap-2 p-2.5 rounded-xl border transition-colors"
          :class="route.path === '/schemes' ? 'bg-indigo-50 text-indigo-700 border-indigo-200' : 'bg-slate-50 text-slate-700 border-slate-200'"
        >
          <Award class="w-4 h-4 text-indigo-600" />
          <span>{{ t('nav_schemes', store.locale) }}</span>
        </router-link>

        <router-link
          to="/tracker"
          class="flex items-center gap-2 p-2.5 rounded-xl border transition-colors"
          :class="route.path === '/tracker' ? 'bg-indigo-50 text-indigo-700 border-indigo-200' : 'bg-slate-50 text-slate-700 border-slate-200'"
        >
          <CheckCircle2 class="w-4 h-4 text-indigo-600" />
          <span>{{ t('nav_tracker', store.locale) }}</span>
        </router-link>

        <router-link
          to="/notifications"
          class="flex items-center gap-2 p-2.5 rounded-xl border transition-colors"
          :class="route.path === '/notifications' ? 'bg-indigo-50 text-indigo-700 border-indigo-200' : 'bg-slate-50 text-slate-700 border-slate-200'"
        >
          <Bell class="w-4 h-4 text-indigo-600" />
          <span>{{ t('nav_notifications', store.locale) }}</span>
        </router-link>

        <router-link
          to="/family"
          class="flex items-center gap-2 p-2.5 rounded-xl border transition-colors"
          :class="route.path === '/family' ? 'bg-indigo-50 text-indigo-700 border-indigo-200' : 'bg-slate-50 text-slate-700 border-slate-200'"
        >
          <Users class="w-4 h-4 text-indigo-600" />
          <span>{{ t('nav_family', store.locale) }}</span>
        </router-link>

        <router-link
          to="/what-if"
          class="flex items-center gap-2 p-2.5 rounded-xl border transition-colors"
          :class="route.path === '/what-if' ? 'bg-indigo-50 text-indigo-700 border-indigo-200' : 'bg-slate-50 text-slate-700 border-slate-200'"
        >
          <Sliders class="w-4 h-4 text-indigo-600" />
          <span>{{ t('nav_what_if', store.locale) }}</span>
        </router-link>

        <router-link
          to="/gr-interpreter"
          class="flex items-center gap-2 p-2.5 rounded-xl border transition-colors"
          :class="route.path === '/gr-interpreter' ? 'bg-indigo-50 text-indigo-700 border-indigo-200' : 'bg-slate-50 text-slate-700 border-slate-200'"
        >
          <BookOpen class="w-4 h-4 text-indigo-600" />
          <span>{{ t('nav_gr_decoder', store.locale) }}</span>
        </router-link>

        <router-link
          to="/community-gap"
          class="flex items-center gap-2 p-2.5 rounded-xl border transition-colors"
          :class="route.path === '/community-gap' ? 'bg-indigo-50 text-indigo-700 border-indigo-200' : 'bg-slate-50 text-slate-700 border-slate-200'"
        >
          <BarChart3 class="w-4 h-4 text-indigo-600" />
          <span>{{ t('nav_insights', store.locale) }}</span>
        </router-link>

        <router-link
          to="/documents"
          class="flex items-center gap-2 p-2.5 rounded-xl border transition-colors"
          :class="route.path === '/documents' ? 'bg-indigo-50 text-indigo-700 border-indigo-200' : 'bg-slate-50 text-slate-700 border-slate-200'"
        >
          <FileText class="w-4 h-4 text-indigo-600" />
          <span>{{ t('nav_documents', store.locale) }}</span>
        </router-link>

        <router-link
          to="/counselor"
          class="flex items-center gap-2 p-2.5 rounded-xl border transition-colors"
          :class="route.path === '/counselor' ? 'bg-amber-600 text-white border-amber-600' : 'bg-amber-50 text-amber-900 border-amber-200'"
        >
          <Building2 class="w-4 h-4" :class="route.path === '/counselor' ? 'text-white' : 'text-amber-700'" />
          <span>{{ t('nav_counselor', store.locale) }}</span>
        </router-link>

        <router-link
          to="/admin-portal"
          class="flex items-center gap-2 p-2.5 rounded-xl border transition-colors"
          :class="route.path === '/admin-portal' ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-slate-50 text-slate-700 border-slate-200'"
        >
          <Settings class="w-4 h-4" />
          <span>{{ t('nav_admin', store.locale) }}</span>
        </router-link>
      </div>

      <div class="pt-2 flex items-center justify-between text-[11px] text-slate-500 px-1 border-t border-slate-100">
        <span class="flex items-center gap-1 text-emerald-700 font-semibold">
          <ShieldCheck class="w-3.5 h-3.5 text-emerald-600" />
          Zero-Aadhaar Advisory Platform
        </span>
        <span>Maharashtra Higher Education</span>
      </div>
    </div>
  </header>
</template>
