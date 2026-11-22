<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, computed } from 'vue';
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
  Building2,
  RotateCcw,
  User,
  ArrowRight
} from '@lucide/vue';

const route = useRoute();
const store = useStudentStore();
const isMobileMenuOpen = ref(false);

// All app destinations — single source of truth
const APP_NAV: { to: string; labelKey: Parameters<typeof t>[0]; icon: typeof Sparkles }[] = [
  { to: '/app',           labelKey: 'nav_discovery',    icon: Sparkles },
  { to: '/review',        labelKey: 'nav_profile',      icon: UserCheck },
  { to: '/schemes',       labelKey: 'nav_schemes',      icon: Award },
  { to: '/family',        labelKey: 'nav_family',       icon: Users },
  { to: '/what-if',       labelKey: 'nav_what_if',      icon: Sliders },
  { to: '/gr-interpreter',labelKey: 'nav_gr_decoder',   icon: BookOpen },
  { to: '/community-gap', labelKey: 'nav_insights',     icon: BarChart3 },
  { to: '/documents',     labelKey: 'nav_documents',    icon: FileText },
  { to: '/tracker',       labelKey: 'nav_tracker',      icon: CheckCircle2 },
  { to: '/notifications', labelKey: 'nav_notifications',icon: Bell },
  { to: '/counselor',     labelKey: 'nav_counselor',    icon: Building2 },
  { to: '/admin-portal',  labelKey: 'nav_admin',        icon: Settings },
];

const isLanding = computed(() => route.path === '/');

function sidebarItemClass(to: string): string {
  return route.path === to
    ? 'bg-[#0B132B] text-white shadow-[2px_2px_0_0_#D97706] border-[#0B132B]'
    : 'text-slate-700 hover:text-[#0B132B] hover:bg-slate-100 border-transparent';
}

function drawerItemClass(to: string): string {
  return route.path === to
    ? 'bg-[#0B132B] text-white shadow-[1.5px_1.5px_0_0_#D97706]'
    : 'bg-white text-slate-700 shadow-[1px_1px_0_0_#0B132B]';
}

watch(() => route.path, () => {
  isMobileMenuOpen.value = false;
});

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') isMobileMenuOpen.value = false;
}
onMounted(() => window.addEventListener('keydown', onKeydown));
onUnmounted(() => window.removeEventListener('keydown', onKeydown));

async function handleRestart() {
  if (confirm("Reset current citizen discovery session?")) {
    await store.restartIntake();
  }
}
</script>

<template>
  <!-- ═══════════════════════════════════════════════════════════════════
       1. LANDING PAGE NAVBAR (route.path === '/')
       Matches Photo 3: Clean top navbar with logo, links, language switch,
       and bold red/saffron CTA button. NO sidebar on landing page!
       ═══════════════════════════════════════════════════════════════════ -->
  <header
    v-if="isLanding"
    class="bg-[#FBFBFA]/95 backdrop-blur-md border-b-[1.5px] border-[#0B132B] sticky top-0 z-50 h-16"
  >
    <div class="max-w-7xl mx-auto h-full px-4 sm:px-6 lg:px-8 flex items-center justify-between gap-4">
      <!-- Brand lockup -->
      <router-link to="/" class="flex items-center gap-2.5 group shrink-0 cursor-pointer">
        <img
          src="/favicon.svg"
          alt="YojnaVia"
          class="w-9 h-9 rounded-xl shadow-[1.5px_1.5px_0_0_#D97706] group-hover:scale-105 transition-transform duration-200 select-none"
          draggable="false"
        />
        <div class="flex items-center gap-2">
          <span class="text-lg font-black tracking-tight text-[#0B132B] leading-none">YOJNAVIA</span>
          <span class="px-1.5 py-0.5 rounded bg-[#F59E0B] text-[#0B132B] text-[10px] font-black uppercase tracking-wider border border-[#0B132B] shadow-[1px_1px_0_0_#0B132B]">
            AI
          </span>
        </div>
      </router-link>

      <!-- Center Nav Links (Photo 3: "How it works", "Parents & teachers", "Content & AI") -->
      <nav class="hidden md:flex items-center gap-6 text-sm font-bold text-slate-800">
        <router-link to="/app" class="hover:text-[#D97706] transition-colors">How it works</router-link>
        <router-link to="/schemes" class="hover:text-[#D97706] transition-colors">Schemes Catalog</router-link>
        <router-link to="/what-if" class="hover:text-[#D97706] transition-colors">What-If Simulator</router-link>
        <router-link to="/gr-interpreter" class="hover:text-[#D97706] transition-colors">GR Decoder</router-link>
        <router-link to="/counselor" class="hover:text-[#D97706] transition-colors">CSC Kendra</router-link>
      </nav>

      <!-- Right Controls: Language Switcher & Bold Red/Saffron CTA Button (Photo 3) -->
      <div class="flex items-center gap-3">
        <!-- Language selector pill -->
        <div class="flex items-center bg-white rounded-lg p-0.5 border-[1.5px] border-[#0B132B] shadow-[1.5px_1.5px_0_0_#0B132B] text-xs font-black">
          <button
            @click="store.setLocale('hi')"
            class="px-2 py-1 rounded transition-all cursor-pointer"
            :class="store.locale === 'hi' ? 'bg-[#0B132B] text-white' : 'text-slate-700 hover:text-slate-900'"
          >
            हिंदी
          </button>
          <button
            @click="store.setLocale('en')"
            class="px-2 py-1 rounded transition-all cursor-pointer"
            :class="store.locale === 'en' ? 'bg-[#0B132B] text-white' : 'text-slate-700 hover:text-slate-900'"
          >
            English
          </button>
          <button
            @click="store.setLocale('mr')"
            class="px-2 py-1 rounded transition-all cursor-pointer"
            :class="store.locale === 'mr' ? 'bg-[#0B132B] text-white' : 'text-slate-700 hover:text-slate-900'"
          >
            मराठी
          </button>
        </div>

        <!-- Prominent Red/Saffron Button (Photo 3 "Open dashboard") -->
        <router-link
          to="/app"
          class="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs sm:text-sm font-black bg-[#DC2626] hover:bg-[#B91C1C] text-white border-[1.5px] border-[#0B132B] shadow-[2.5px_2.5px_0_0_#0B132B] transition-transform active:translate-x-0.5 active:translate-y-0.5 cursor-pointer"
        >
          <span>Open dashboard</span>
          <ArrowRight class="w-3.5 h-3.5" />
        </router-link>

        <!-- Mobile Menu Toggle Button -->
        <button
          @click="isMobileMenuOpen = !isMobileMenuOpen"
          class="md:hidden p-2 rounded-xl text-slate-800 bg-white border-[1.5px] border-[#0B132B] shadow-[1.5px_1.5px_0_0_#0B132B] cursor-pointer"
          aria-label="Toggle navigation"
        >
          <X v-if="isMobileMenuOpen" class="w-5 h-5" />
          <Menu v-else class="w-5 h-5" />
        </button>
      </div>
    </div>

    <!-- Mobile Drawer for Landing Page -->
    <div
      v-if="isMobileMenuOpen"
      class="md:hidden bg-[#FBFBFA] border-b-[1.5px] border-[#0B132B] px-4 pt-3 pb-5 shadow-xl space-y-2 animate-in slide-in-from-top duration-200"
    >
      <router-link
        v-for="item in APP_NAV"
        :key="item.to"
        :to="item.to"
        class="flex items-center gap-2.5 p-2.5 rounded-xl border-[1.5px] border-[#0B132B] text-xs font-bold transition-all"
        :class="drawerItemClass(item.to)"
      >
        <component :is="item.icon" class="w-4 h-4 text-[#D97706]" />
        <span>{{ t(item.labelKey, store.locale) }}</span>
      </router-link>
    </div>
  </header>

  <!-- ═══════════════════════════════════════════════════════════════════
       2. APP ROUTES (!isLanding)
       Matches Photo 2 & Photo 4:
       - Full-Height Sidebar from top:0 to bottom:0 unbroken!
       - Logo at the top of the sidebar.
       - Nav items below logo.
       - User profile, language toggle, and policy seal at bottom.
       - App Header sits to the right of the sidebar (xl:pl-64).
       ═══════════════════════════════════════════════════════════════════ -->
  <template v-else>
    <!-- Full-Height Sidebar (Desktop xl+) -->
    <aside
      class="hidden xl:flex flex-col fixed left-0 top-0 bottom-0 h-screen w-64 z-50 bg-[#FBFBFA] border-r-[1.5px] border-[#0B132B]"
      aria-label="App Navigation Sidebar"
    >
      <!-- Top Logo Lockup inside Sidebar (Photo 2 & Photo 4) -->
      <div class="px-5 py-4 border-b-[1.5px] border-[#0B132B]/10 shrink-0">
        <router-link to="/" class="flex items-center gap-2.5 group cursor-pointer">
          <img
            src="/favicon.svg"
            alt="YojnaVia"
            class="w-9 h-9 rounded-xl shadow-[1.5px_1.5px_0_0_#D97706] group-hover:scale-105 transition-transform duration-200 select-none shrink-0"
            draggable="false"
          />
          <div class="flex items-center gap-2">
            <span class="text-[17px] font-black tracking-tight text-[#0B132B] leading-none">YOJNAVIA</span>
            <span class="px-1.5 py-0.5 rounded bg-[#F59E0B] text-[#0B132B] text-[10px] font-black uppercase tracking-wider border border-[#0B132B] shadow-[1px_1px_0_0_#0B132B]">
              AI
            </span>
          </div>
        </router-link>
      </div>

      <!-- Navigation Links List (Photo 2 & Photo 4: Home, Learn, Tutor...) -->
      <nav class="flex-1 overflow-y-auto px-3 py-3 space-y-1">
        <router-link
          v-for="item in APP_NAV"
          :key="item.to"
          :to="item.to"
          class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-[13px] font-bold transition-all border-[1.5px] relative cursor-pointer"
          :class="sidebarItemClass(item.to)"
        >
          <component :is="item.icon" class="w-4 h-4 shrink-0" :class="route.path === item.to ? 'text-white' : 'text-slate-600'" />
          <span class="flex-1 truncate">{{ t(item.labelKey, store.locale) }}</span>

          <!-- Badges -->
          <span
            v-if="item.to === '/review' && store.profile && !store.profile.is_confirmed"
            class="w-2 h-2 rounded-full bg-amber-500 animate-pulse shrink-0"
          ></span>
          <span
            v-if="item.to === '/schemes' && store.evaluationSummary?.likely_eligible"
            class="text-[10px] px-1.5 py-0.2 rounded-full font-black shrink-0"
            :class="route.path === '/schemes' ? 'bg-white/20 text-white' : 'bg-emerald-100 text-emerald-800 border border-emerald-300'"
          >
            {{ store.evaluationSummary.likely_eligible }}
          </span>
          <span
            v-if="item.to === '/tracker' && store.trackedApplications.length > 0"
            class="text-[10px] px-1.5 py-0.2 rounded-full font-black shrink-0"
            :class="route.path === '/tracker' ? 'bg-white/20 text-white' : 'bg-indigo-100 text-indigo-900 border border-indigo-300'"
          >
            {{ store.trackedApplications.length }}
          </span>
        </router-link>
      </nav>

      <!-- Sidebar Footer (Photo 2 & Photo 4: Kaushik @user, [हिंदी | English], logout) -->
      <div class="p-3.5 border-t-[1.5px] border-[#0B132B]/10 bg-white/60 space-y-2.5 shrink-0">
        <!-- Citizen User Info -->
        <div class="flex items-center justify-between px-1">
          <div class="min-w-0">
            <div class="text-xs font-black text-[#0B132B] truncate flex items-center gap-1.5">
              <User class="w-3.5 h-3.5 text-[#D97706] shrink-0" />
              <span>{{ store.profile?.name || 'Citizen User' }}</span>
            </div>
            <div class="text-[10px] text-slate-500 font-medium pl-5 truncate">
              @{{ store.profile?.district || 'Maharashtra' }} · Student
            </div>
          </div>
          <button
            @click="handleRestart"
            title="Reset Session"
            class="p-1 text-slate-400 hover:text-slate-800 hover:bg-slate-100 rounded-md transition-colors cursor-pointer"
          >
            <RotateCcw class="w-3.5 h-3.5" />
          </button>
        </div>

        <!-- Language Switcher in Sidebar (Photo 4) -->
        <div class="flex items-center bg-white rounded-lg p-0.5 border-[1.5px] border-[#0B132B] shadow-[1px_1px_0_0_#0B132B] text-[11px] font-black w-full justify-between">
          <button
            @click="store.setLocale('hi')"
            class="flex-1 py-0.5 text-center rounded transition-all cursor-pointer"
            :class="store.locale === 'hi' ? 'bg-[#0B132B] text-white' : 'text-slate-700 hover:text-slate-900'"
          >
            हिंदी
          </button>
          <button
            @click="store.setLocale('en')"
            class="flex-1 py-0.5 text-center rounded transition-all cursor-pointer"
            :class="store.locale === 'en' ? 'bg-[#0B132B] text-white' : 'text-slate-700 hover:text-slate-900'"
          >
            English
          </button>
          <button
            @click="store.setLocale('mr')"
            class="flex-1 py-0.5 text-center rounded transition-all cursor-pointer"
            :class="store.locale === 'mr' ? 'bg-[#0B132B] text-white' : 'text-slate-700 hover:text-slate-900'"
          >
            मराठी
          </button>
        </div>

        <!-- RTS Act Seal -->
        <div class="flex items-center gap-1.5 text-[9px] text-emerald-800 font-bold px-1">
          <ShieldCheck class="w-3 h-3 text-emerald-600 shrink-0" />
          <span>Zero-Aadhaar · RTS Act 2015</span>
        </div>
      </div>
    </aside>

    <!-- App Top Bar (Sits to the right of the sidebar on desktop; full width on mobile) -->
    <header class="xl:pl-64 bg-[#FBFBFA]/95 backdrop-blur-md border-b-[1.5px] border-[#0B132B] sticky top-0 z-40 h-14">
      <div class="h-full px-4 sm:px-6 flex items-center justify-between gap-4">
        <!-- Mobile brand (visible only below xl) -->
        <div class="flex items-center gap-2 xl:hidden">
          <router-link to="/" class="flex items-center gap-2 group cursor-pointer">
            <img src="/favicon.svg" alt="YojnaVia" class="w-8 h-8 rounded-lg shadow-[1.5px_1.5px_0_0_#D97706]" />
            <span class="text-base font-black tracking-tight text-[#0B132B]">YOJNAVIA</span>
          </router-link>
        </div>

        <!-- Desktop left indicator -->
        <div class="hidden xl:flex items-center gap-2 text-xs font-bold text-slate-700">
          <span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md bg-[#FFFBEB] text-[#92400E] border-[1.5px] border-[#0B132B] shadow-[1px_1px_0_0_#0B132B] text-[10px] font-black uppercase tracking-wider">
            <Sparkles class="w-3 h-3 text-[#D97706] fill-current" />
            <span>Sovereign Welfare Intelligence</span>
          </span>
          <span class="text-slate-400">•</span>
          <span>100% Deterministic Maharashtra Rules</span>
        </div>

        <!-- Right Quick Links: CSC Desk & Admin -->
        <div class="flex items-center gap-2.5 ml-auto">
          <!-- CSC Desk shortcut pill -->
          <router-link
            to="/counselor"
            class="flex items-center gap-1.5 px-2.5 py-1 rounded-xl text-xs font-bold border-[1.5px] transition-all cursor-pointer"
            :class="route.path === '/counselor'
              ? 'bg-[#D97706] text-white border-[#0B132B] shadow-[1.5px_1.5px_0_0_#0B132B]'
              : 'bg-[#FFFBEB] hover:bg-[#FEF3C7] text-[#92400E] border-[#0B132B] shadow-[1.5px_1.5px_0_0_#0B132B]'"
          >
            <Building2 class="w-3.5 h-3.5" :class="route.path === '/counselor' ? 'text-white' : 'text-[#D97706]'" />
            <span class="hidden sm:inline">CSC Desk</span>
          </router-link>

          <!-- Admin Portal shortcut pill -->
          <router-link
            to="/admin-portal"
            class="flex items-center gap-1 px-2.5 py-1 rounded-xl text-xs font-bold border-[1.5px] border-[#0B132B] transition-all cursor-pointer"
            :class="route.path === '/admin-portal'
              ? 'bg-[#0B132B] text-white shadow-[1.5px_1.5px_0_0_#D97706]'
              : 'bg-white hover:bg-slate-100 text-slate-700 shadow-[1.5px_1.5px_0_0_#0B132B]'"
          >
            <Settings class="w-3 h-3" />
            <span class="hidden sm:inline">Admin</span>
          </router-link>

          <!-- Mobile Hamburger Toggle Button (< xl) -->
          <button
            @click="isMobileMenuOpen = !isMobileMenuOpen"
            class="xl:hidden p-1.5 rounded-xl text-slate-800 bg-white border-[1.5px] border-[#0B132B] shadow-[1.5px_1.5px_0_0_#0B132B] cursor-pointer"
            aria-label="Toggle navigation menu"
          >
            <X v-if="isMobileMenuOpen" class="w-5 h-5" />
            <Menu v-else class="w-5 h-5" />
          </button>
        </div>
      </div>

      <!-- Mobile / Tablet Drawer (< xl) -->
      <div
        v-if="isMobileMenuOpen"
        class="xl:hidden bg-[#FBFBFA] border-b-[1.5px] border-[#0B132B] px-4 pt-3 pb-5 shadow-xl space-y-3"
      >
        <div class="text-[10px] font-black text-slate-500 uppercase tracking-widest px-1">
          Sovereign Benefits Navigation
        </div>
        <div class="grid grid-cols-2 gap-1.5 text-xs font-bold">
          <router-link
            v-for="item in APP_NAV"
            :key="item.to"
            :to="item.to"
            class="flex items-center gap-2 p-2.5 rounded-lg border-[1.5px] border-[#0B132B] transition-all relative cursor-pointer"
            :class="drawerItemClass(item.to)"
          >
            <component :is="item.icon" class="w-3.5 h-3.5 shrink-0 text-[#D97706]" />
            <span class="truncate">{{ t(item.labelKey, store.locale) }}</span>
            <span v-if="item.to === '/schemes' && store.evaluationSummary?.likely_eligible" class="text-[9px] px-1.5 rounded-full bg-emerald-100 text-emerald-800 font-black border border-emerald-300 ml-auto">
              {{ store.evaluationSummary.likely_eligible }}
            </span>
          </router-link>
        </div>
      </div>
    </header>
  </template>
</template>
