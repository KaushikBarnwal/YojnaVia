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
  <header class="bg-[#FBFBFA]/95 backdrop-blur-md border-b-[1.5px] border-[#0B132B] sticky top-0 z-40">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16 gap-4">
        
        <!-- Brand -->
        <router-link to="/" class="flex items-center gap-2.5 group shrink-0">
          <div class="w-9 h-9 rounded-xl bg-[#0B132B] border-[1.5px] border-[#0B132B] shadow-[1.5px_1.5px_0_0_#D97706] flex items-center justify-center text-[#F59E0B] group-hover:scale-105 transition-transform">
            <Sparkles class="w-4 h-4 fill-current" />
          </div>
          <div class="flex items-center gap-2">
            <span class="text-lg font-black tracking-tight text-[#0B132B]">YOJNAVIA</span>
            <span class="text-[10px] font-extrabold uppercase tracking-widest px-2 py-0.5 rounded-md bg-[#FFFBEB] text-[#92400E] border-[1.5px] border-[#0B132B] shadow-[1px_1px_0_0_#0B132B]">
              Maharashtra
            </span>
          </div>
        </router-link>

        <!-- Main Navigation Links (Clean & Human) -->
        <nav class="hidden xl:flex items-center gap-1">
          <router-link
            to="/"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all border-[1.5px]"
            :class="route.path === '/' ? 'bg-[#0B132B] text-white border-[#0B132B] shadow-[1.5px_1.5px_0_0_#D97706]' : 'text-slate-700 hover:text-slate-900 hover:bg-slate-100 border-transparent'"
          >
            <Sparkles class="w-3.5 h-3.5" />
            <span>{{ t('nav_discovery', store.locale) }}</span>
          </router-link>

          <router-link
            to="/review"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all border-[1.5px] relative"
            :class="route.path === '/review' ? 'bg-[#0B132B] text-white border-[#0B132B] shadow-[1.5px_1.5px_0_0_#D97706]' : 'text-slate-700 hover:text-slate-900 hover:bg-slate-100 border-transparent'"
          >
            <UserCheck class="w-3.5 h-3.5" />
            <span>{{ t('nav_profile', store.locale) }}</span>
            <span v-if="store.profile && !store.profile.is_confirmed" class="w-1.5 h-1.5 rounded-full bg-amber-500 absolute top-1.5 right-1.5 animate-pulse"></span>
          </router-link>

          <router-link
            to="/schemes"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all border-[1.5px]"
            :class="route.path === '/schemes' ? 'bg-[#0B132B] text-white border-[#0B132B] shadow-[1.5px_1.5px_0_0_#D97706]' : 'text-slate-700 hover:text-slate-900 hover:bg-slate-100 border-transparent'"
          >
            <Award class="w-3.5 h-3.5" />
            <span>{{ t('nav_schemes', store.locale) }}</span>
            <span v-if="store.evaluationSummary?.likely_eligible" class="text-[10px] px-1.5 py-0.2 rounded-full bg-emerald-100 text-emerald-800 font-black border border-emerald-300">
              {{ store.evaluationSummary.likely_eligible }}
            </span>
          </router-link>

          <router-link
            to="/family"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all border-[1.5px]"
            :class="route.path === '/family' ? 'bg-[#0B132B] text-white border-[#0B132B] shadow-[1.5px_1.5px_0_0_#D97706]' : 'text-slate-700 hover:text-slate-900 hover:bg-slate-100 border-transparent'"
          >
            <Users class="w-3.5 h-3.5" />
            <span>{{ t('nav_family', store.locale) }}</span>
          </router-link>

          <router-link
            to="/what-if"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all border-[1.5px]"
            :class="route.path === '/what-if' ? 'bg-[#0B132B] text-white border-[#0B132B] shadow-[1.5px_1.5px_0_0_#D97706]' : 'text-slate-700 hover:text-slate-900 hover:bg-slate-100 border-transparent'"
          >
            <Sliders class="w-3.5 h-3.5" />
            <span>{{ t('nav_what_if', store.locale) }}</span>
          </router-link>

          <router-link
            to="/gr-interpreter"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all border-[1.5px]"
            :class="route.path === '/gr-interpreter' ? 'bg-[#0B132B] text-white border-[#0B132B] shadow-[1.5px_1.5px_0_0_#D97706]' : 'text-slate-700 hover:text-slate-900 hover:bg-slate-100 border-transparent'"
          >
            <BookOpen class="w-3.5 h-3.5" />
            <span>{{ t('nav_gr_decoder', store.locale) }}</span>
          </router-link>

          <router-link
            to="/community-gap"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all border-[1.5px]"
            :class="route.path === '/community-gap' ? 'bg-[#0B132B] text-white border-[#0B132B] shadow-[1.5px_1.5px_0_0_#D97706]' : 'text-slate-700 hover:text-slate-900 hover:bg-slate-100 border-transparent'"
          >
            <BarChart3 class="w-3.5 h-3.5" />
            <span>{{ t('nav_insights', store.locale) }}</span>
          </router-link>

          <router-link
            to="/documents"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all border-[1.5px]"
            :class="route.path === '/documents' ? 'bg-[#0B132B] text-white border-[#0B132B] shadow-[1.5px_1.5px_0_0_#D97706]' : 'text-slate-700 hover:text-slate-900 hover:bg-slate-100 border-transparent'"
          >
            <FileText class="w-3.5 h-3.5" />
            <span>{{ t('nav_documents', store.locale) }}</span>
          </router-link>

          <router-link
            to="/tracker"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all border-[1.5px]"
            :class="route.path === '/tracker' ? 'bg-[#0B132B] text-white border-[#0B132B] shadow-[1.5px_1.5px_0_0_#D97706]' : 'text-slate-700 hover:text-slate-900 hover:bg-slate-100 border-transparent'"
          >
            <CheckCircle2 class="w-3.5 h-3.5" />
            <span>{{ t('nav_tracker', store.locale) }}</span>
            <span v-if="store.trackedApplications.length > 0" class="text-[10px] px-1.5 py-0.2 rounded-full bg-indigo-100 text-indigo-900 font-black border border-indigo-300">
              {{ store.trackedApplications.length }}
            </span>
          </router-link>

          <router-link
            to="/notifications"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all border-[1.5px]"
            :class="route.path === '/notifications' ? 'bg-[#0B132B] text-white border-[#0B132B] shadow-[1.5px_1.5px_0_0_#D97706]' : 'text-slate-700 hover:text-slate-900 hover:bg-slate-100 border-transparent'"
          >
            <Bell class="w-3.5 h-3.5" />
            <span>{{ t('nav_notifications', store.locale) }}</span>
          </router-link>
        </nav>

        <!-- Right Controls: Language, Admin & Mobile Hamburger -->
        <div class="flex items-center gap-2">
          <!-- 3-Language Selector -->
          <div class="flex items-center bg-white rounded-xl p-0.5 border-[1.5px] border-[#0B132B] shadow-[1.5px_1.5px_0_0_#0B132B] text-xs font-black">
            <button
              @click="store.setLocale('en')"
              class="px-2 py-0.5 rounded-lg transition-all cursor-pointer"
              :class="store.locale === 'en' ? 'bg-[#0B132B] text-white' : 'text-slate-600 hover:text-slate-900'"
            >
              EN
            </button>
            <button
              @click="store.setLocale('mr')"
              class="px-2 py-0.5 rounded-lg transition-all cursor-pointer"
              :class="store.locale === 'mr' ? 'bg-[#0B132B] text-white' : 'text-slate-600 hover:text-slate-900'"
            >
              मराठी
            </button>
            <button
              @click="store.setLocale('hi')"
              class="px-2 py-0.5 rounded-lg transition-all cursor-pointer"
              :class="store.locale === 'hi' ? 'bg-[#0B132B] text-white' : 'text-slate-600 hover:text-slate-900'"
            >
              हिंदी
            </button>
          </div>

          <!-- CSC Counselor Desk Link -->
          <router-link
            to="/counselor"
            class="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-xl text-xs font-bold transition-all border-[1.5px]"
            :class="route.path === '/counselor' 
              ? 'bg-[#D97706] text-white border-[#0B132B] shadow-[1.5px_1.5px_0_0_#0B132B]' 
              : 'bg-[#FFFBEB] hover:bg-[#FEF3C7] text-[#92400E] border-[#0B132B] shadow-[1.5px_1.5px_0_0_#0B132B]'"
          >
            <Building2 class="w-3.5 h-3.5" :class="route.path === '/counselor' ? 'text-white' : 'text-[#D97706]'" />
            <span>CSC Desk</span>
          </router-link>

          <!-- Admin Portal Link -->
          <router-link
            to="/admin-portal"
            class="hidden sm:flex items-center gap-1 px-2.5 py-1 rounded-xl text-xs font-bold transition-all border-[1.5px] border-[#0B132B]"
            :class="route.path === '/admin-portal' 
              ? 'bg-[#0B132B] text-white shadow-[1.5px_1.5px_0_0_#D97706]' 
              : 'bg-white hover:bg-slate-100 text-slate-800 shadow-[1.5px_1.5px_0_0_#0B132B]'"
          >
            <Settings class="w-3 h-3" />
            <span>Admin</span>
          </router-link>

          <!-- Mobile / Tablet Hamburger Toggle Button -->
          <button
            @click="isMobileMenuOpen = !isMobileMenuOpen"
            class="xl:hidden p-1.5 rounded-xl text-slate-700 hover:text-slate-900 bg-white border-[1.5px] border-[#0B132B] shadow-[1.5px_1.5px_0_0_#0B132B] transition-colors"
            aria-label="Toggle navigation menu"
          >
            <X v-if="isMobileMenuOpen" class="w-5 h-5 text-slate-900" />
            <Menu v-else class="w-5 h-5 text-slate-900" />
          </button>
        </div>

      </div>
    </div>

    <!-- Mobile Slide-Down Menu Drawer -->
    <div 
      v-if="isMobileMenuOpen" 
      class="xl:hidden bg-[#FBFBFA] border-b-[1.5px] border-[#0B132B] px-4 pt-3 pb-6 shadow-xl space-y-3 animate-in slide-in-from-top-2 duration-200"
    >
      <div class="text-[10px] font-black text-slate-500 uppercase tracking-widest px-2">
        Sovereign Benefits Navigation
      </div>

      <div class="grid grid-cols-2 gap-2 text-xs font-bold">
        <router-link
          to="/"
          class="flex items-center gap-2 p-2.5 rounded-xl border-[1.5px] border-[#0B132B] transition-all"
          :class="route.path === '/' ? 'bg-[#0B132B] text-white shadow-[1.5px_1.5px_0_0_#D97706]' : 'bg-white text-slate-800 shadow-[1px_1px_0_0_#0B132B]'"
        >
          <Sparkles class="w-4 h-4 text-[#D97706]" />
          <span>{{ t('nav_discovery', store.locale) }}</span>
        </router-link>

        <router-link
          to="/review"
          class="flex items-center gap-2 p-2.5 rounded-xl border-[1.5px] border-[#0B132B] transition-all"
          :class="route.path === '/review' ? 'bg-[#0B132B] text-white shadow-[1.5px_1.5px_0_0_#D97706]' : 'bg-white text-slate-800 shadow-[1px_1px_0_0_#0B132B]'"
        >
          <UserCheck class="w-4 h-4 text-[#D97706]" />
          <span>{{ t('nav_profile', store.locale) }}</span>
        </router-link>

        <router-link
          to="/schemes"
          class="flex items-center gap-2 p-2.5 rounded-xl border-[1.5px] border-[#0B132B] transition-all"
          :class="route.path === '/schemes' ? 'bg-[#0B132B] text-white shadow-[1.5px_1.5px_0_0_#D97706]' : 'bg-white text-slate-800 shadow-[1px_1px_0_0_#0B132B]'"
        >
          <Award class="w-4 h-4 text-[#D97706]" />
          <span>{{ t('nav_schemes', store.locale) }}</span>
        </router-link>

        <router-link
          to="/tracker"
          class="flex items-center gap-2 p-2.5 rounded-xl border-[1.5px] border-[#0B132B] transition-all"
          :class="route.path === '/tracker' ? 'bg-[#0B132B] text-white shadow-[1.5px_1.5px_0_0_#D97706]' : 'bg-white text-slate-800 shadow-[1px_1px_0_0_#0B132B]'"
        >
          <CheckCircle2 class="w-4 h-4 text-[#D97706]" />
          <span>{{ t('nav_tracker', store.locale) }}</span>
        </router-link>

        <router-link
          to="/notifications"
          class="flex items-center gap-2 p-2.5 rounded-xl border-[1.5px] border-[#0B132B] transition-all"
          :class="route.path === '/notifications' ? 'bg-[#0B132B] text-white shadow-[1.5px_1.5px_0_0_#D97706]' : 'bg-white text-slate-800 shadow-[1px_1px_0_0_#0B132B]'"
        >
          <Bell class="w-4 h-4 text-[#D97706]" />
          <span>{{ t('nav_notifications', store.locale) }}</span>
        </router-link>

        <router-link
          to="/family"
          class="flex items-center gap-2 p-2.5 rounded-xl border-[1.5px] border-[#0B132B] transition-all"
          :class="route.path === '/family' ? 'bg-[#0B132B] text-white shadow-[1.5px_1.5px_0_0_#D97706]' : 'bg-white text-slate-800 shadow-[1px_1px_0_0_#0B132B]'"
        >
          <Users class="w-4 h-4 text-[#D97706]" />
          <span>{{ t('nav_family', store.locale) }}</span>
        </router-link>

        <router-link
          to="/what-if"
          class="flex items-center gap-2 p-2.5 rounded-xl border-[1.5px] border-[#0B132B] transition-all"
          :class="route.path === '/what-if' ? 'bg-[#0B132B] text-white shadow-[1.5px_1.5px_0_0_#D97706]' : 'bg-white text-slate-800 shadow-[1px_1px_0_0_#0B132B]'"
        >
          <Sliders class="w-4 h-4 text-[#D97706]" />
          <span>{{ t('nav_what_if', store.locale) }}</span>
        </router-link>

        <router-link
          to="/gr-interpreter"
          class="flex items-center gap-2 p-2.5 rounded-xl border-[1.5px] border-[#0B132B] transition-all"
          :class="route.path === '/gr-interpreter' ? 'bg-[#0B132B] text-white shadow-[1.5px_1.5px_0_0_#D97706]' : 'bg-white text-slate-800 shadow-[1px_1px_0_0_#0B132B]'"
        >
          <BookOpen class="w-4 h-4 text-[#D97706]" />
          <span>{{ t('nav_gr_decoder', store.locale) }}</span>
        </router-link>

        <router-link
          to="/community-gap"
          class="flex items-center gap-2 p-2.5 rounded-xl border-[1.5px] border-[#0B132B] transition-all"
          :class="route.path === '/community-gap' ? 'bg-[#0B132B] text-white shadow-[1.5px_1.5px_0_0_#D97706]' : 'bg-white text-slate-800 shadow-[1px_1px_0_0_#0B132B]'"
        >
          <BarChart3 class="w-4 h-4 text-[#D97706]" />
          <span>{{ t('nav_insights', store.locale) }}</span>
        </router-link>

        <router-link
          to="/documents"
          class="flex items-center gap-2 p-2.5 rounded-xl border-[1.5px] border-[#0B132B] transition-all"
          :class="route.path === '/documents' ? 'bg-[#0B132B] text-white shadow-[1.5px_1.5px_0_0_#D97706]' : 'bg-white text-slate-800 shadow-[1px_1px_0_0_#0B132B]'"
        >
          <FileText class="w-4 h-4 text-[#D97706]" />
          <span>{{ t('nav_documents', store.locale) }}</span>
        </router-link>

        <router-link
          to="/counselor"
          class="flex items-center gap-2 p-2.5 rounded-xl border-[1.5px] border-[#0B132B] transition-all"
          :class="route.path === '/counselor' ? 'bg-[#D97706] text-white shadow-[1.5px_1.5px_0_0_#0B132B]' : 'bg-[#FFFBEB] text-[#92400E] shadow-[1px_1px_0_0_#0B132B]'"
        >
          <Building2 class="w-4 h-4" :class="route.path === '/counselor' ? 'text-white' : 'text-[#D97706]'" />
          <span>{{ t('nav_counselor', store.locale) }}</span>
        </router-link>

        <router-link
          to="/admin-portal"
          class="flex items-center gap-2 p-2.5 rounded-xl border-[1.5px] border-[#0B132B] transition-all"
          :class="route.path === '/admin-portal' ? 'bg-[#0B132B] text-white shadow-[1.5px_1.5px_0_0_#D97706]' : 'bg-white text-slate-800 shadow-[1px_1px_0_0_#0B132B]'"
        >
          <Settings class="w-4 h-4" />
          <span>{{ t('nav_admin', store.locale) }}</span>
        </router-link>
      </div>

      <div class="pt-2 flex items-center justify-between text-[11px] text-slate-600 px-1 border-t-[1.5px] border-[#0B132B]/10 font-bold">
        <span class="flex items-center gap-1 text-emerald-800">
          <ShieldCheck class="w-3.5 h-3.5 text-emerald-600" />
          Zero-Aadhaar Sovereign Policy
        </span>
        <span>Maharashtra Higher Education</span>
      </div>
    </div>
  </header>
</template>
