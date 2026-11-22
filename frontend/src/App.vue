<script setup lang="ts">
import { onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useStudentStore } from './stores/studentStore';
import Navbar from './components/Navbar.vue';
import CookieConsent from './components/CookieConsent.vue';
import ToastNotification from './components/ToastNotification.vue';
import { t } from './utils/i18n';
import { 
  Sparkles, 
  UserCheck, 
  Award, 
  FileText, 
  CheckCircle2, 
  ShieldCheck,
  Users,
  Mail
} from '@lucide/vue';

const route = useRoute();
const store = useStudentStore();

onMounted(async () => {
  await store.initSession();
});
</script>

<template>
  <div class="min-h-screen bg-[#FBFBFA] flex flex-col font-sans selection:bg-[#D97706] selection:text-white overflow-x-hidden">
    <!-- Global Toast Notifications -->
    <ToastNotification />

    <!-- Main Top Navbar -->
    <Navbar />

    <!-- Main View Content -->
    <main class="flex-1" :class="route.path === '/' ? 'pb-0' : 'pb-16 md:pb-0 xl:pl-64'">
      <router-view />
    </main>

    <!-- Sovereign Cookie / Storage Consent Banner -->
    <CookieConsent />

    <!-- Mobile Bottom Navigation Bar (Visible only inside /app routes on < md screens) -->
    <nav v-if="route.path !== '/'" class="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-[#FBFBFA]/95 backdrop-blur-md border-t-[1.5px] border-[#0B132B] px-2 py-1.5 flex items-center justify-around shadow-lg">
      <router-link
        to="/app"
        class="flex flex-col items-center py-1 px-2.5 rounded-xl text-[10px] font-bold transition-all"
        :class="route.path === '/app' ? 'text-[#D97706] font-black' : 'text-slate-600 hover:text-slate-900'"
      >
        <Sparkles class="w-4 h-4 mb-0.5" />
        <span>{{ t('nav_discovery', store.locale) }}</span>
      </router-link>

      <router-link
        to="/review"
        class="flex flex-col items-center py-1 px-2.5 rounded-xl text-[10px] font-bold transition-all relative"
        :class="route.path === '/review' ? 'text-[#D97706] font-black' : 'text-slate-600 hover:text-slate-900'"
      >
        <UserCheck class="w-4 h-4 mb-0.5" />
        <span>{{ t('nav_profile', store.locale) }}</span>
        <span v-if="store.profile && !store.profile.is_confirmed" class="w-1.5 h-1.5 rounded-full bg-amber-500 absolute top-1 right-2 animate-pulse"></span>
      </router-link>

      <router-link
        to="/schemes"
        class="flex flex-col items-center py-1 px-2 rounded-xl text-[10px] font-bold transition-all relative"
        :class="route.path === '/schemes' ? 'text-[#D97706] font-black' : 'text-slate-600 hover:text-slate-900'"
      >
        <Award class="w-4 h-4 mb-0.5" />
        <span>{{ t('nav_schemes', store.locale) }}</span>
        <span v-if="store.evaluationSummary?.likely_eligible" class="text-[9px] px-1 bg-[#059669] text-white font-black rounded-full absolute -top-0.5 right-1">
          {{ store.evaluationSummary.likely_eligible }}
        </span>
      </router-link>

      <router-link
        to="/family"
        class="flex flex-col items-center py-1 px-2 rounded-xl text-[10px] font-bold transition-all"
        :class="route.path === '/family' ? 'text-[#D97706] font-black' : 'text-slate-600 hover:text-slate-900'"
      >
        <Users class="w-4 h-4 mb-0.5" />
        <span>Family</span>
      </router-link>

      <router-link
        to="/documents"
        class="flex flex-col items-center py-1 px-2.5 rounded-xl text-[10px] font-bold transition-all"
        :class="route.path === '/documents' ? 'text-[#D97706] font-black' : 'text-slate-600 hover:text-slate-900'"
      >
        <FileText class="w-4 h-4 mb-0.5" />
        <span>{{ t('nav_documents', store.locale) }}</span>
      </router-link>

      <router-link
        to="/tracker"
        class="flex flex-col items-center py-1 px-2.5 rounded-xl text-[10px] font-bold transition-all relative"
        :class="route.path === '/tracker' ? 'text-[#D97706] font-black' : 'text-slate-600 hover:text-slate-900'"
      >
        <CheckCircle2 class="w-4 h-4 mb-0.5" />
        <span>{{ t('nav_tracker', store.locale) }}</span>
        <span v-if="store.trackedApplications.length > 0" class="text-[9px] px-1 bg-[#0B132B] text-white font-black rounded-full absolute -top-0.5 right-1">
          {{ store.trackedApplications.length }}
        </span>
      </router-link>
    </nav>

    <!-- Civic Tech Footer -->
    <footer class="bg-white border-t-[1.5px] border-[#0B132B] mt-12 py-8" :class="route.path === '/' ? '' : 'xl:pl-64'">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-4">
        <div class="flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-slate-600 font-medium pb-4 border-b border-slate-100">
          <div class="flex items-center gap-2 flex-wrap">
            <span class="font-black text-[#0B132B] tracking-tight text-sm">YojnaVia</span>
            <span>•</span>
            <span class="font-bold text-slate-800">{{ t('brand_subtitle', store.locale) }}</span>
            <span>•</span>
            <span class="neo-stamp neo-stamp-emerald">
              <ShieldCheck class="w-3.5 h-3.5 text-emerald-600" />
              Zero-PII Sovereign Advisory
            </span>
          </div>

          <!-- Clickable Email & Helpdesk -->
          <div class="flex items-center gap-3 text-xs">
            <a
              href="mailto:support@YojnaVia.in"
              class="inline-flex items-center gap-1.5 font-bold text-[#0B132B] hover:text-[#D97706] transition-colors"
              title="Official Civic Tech Helpdesk"
            >
              <Mail class="w-3.5 h-3.5 text-[#D97706]" />
              <span>support@YojnaVia.in</span>
            </a>
          </div>
        </div>

        <div class="flex flex-col sm:flex-row items-center justify-between gap-3 text-[11px] text-slate-500 font-medium">
          <div class="flex items-center gap-3 flex-wrap">
            <router-link to="/privacy" class="hover:text-amber-800 transition-colors font-semibold">Privacy Policy</router-link>
            <span>•</span>
            <router-link to="/terms" class="hover:text-amber-800 transition-colors font-semibold">Terms & Disclaimers</router-link>
            <span>•</span>
            <router-link to="/schemes" class="hover:text-amber-800 transition-colors font-semibold">Schemes Catalog</router-link>
            <span>•</span>
            <router-link to="/counselor" class="hover:text-amber-800 transition-colors font-semibold">CSC Portal</router-link>
          </div>

          <div class="flex items-center gap-2 text-slate-500">
            <span>Derived from official Maharashtra GRs • Maharashtra Public Services (RTS) Act 2015</span>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>
