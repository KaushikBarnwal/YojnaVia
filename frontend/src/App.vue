<script setup lang="ts">
import { onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useStudentStore } from './stores/studentStore';
import Navbar from './components/Navbar.vue';
import { t } from './utils/i18n';
import { 
  Sparkles, 
  UserCheck, 
  Award, 
  FileText, 
  CheckCircle2, 
  ShieldCheck,
  Users
} from '@lucide/vue';

const route = useRoute();
const store = useStudentStore();

onMounted(async () => {
  await store.initSession();
});
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex flex-col font-sans selection:bg-indigo-500 selection:text-white">
    <!-- Main Top Navbar -->
    <Navbar />

    <!-- Main View Content -->
    <main class="flex-1 pb-16 md:pb-0">
      <router-view />
    </main>

    <!-- Mobile Bottom Navigation Bar (Visible only on < md screens) -->
    <nav class="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-md border-t border-slate-200 px-2 py-1.5 flex items-center justify-around shadow-lg">
      <router-link
        to="/"
        class="flex flex-col items-center py-1 px-2.5 rounded-xl text-[10px] font-bold transition-colors"
        :class="route.path === '/' ? 'text-indigo-600 bg-indigo-50/80' : 'text-slate-500 hover:text-slate-800'"
      >
        <Sparkles class="w-4 h-4 mb-0.5" />
        <span>{{ t('nav_discovery', store.locale) }}</span>
      </router-link>

      <router-link
        to="/review"
        class="flex flex-col items-center py-1 px-2.5 rounded-xl text-[10px] font-bold transition-colors relative"
        :class="route.path === '/review' ? 'text-indigo-600 bg-indigo-50/80' : 'text-slate-500 hover:text-slate-800'"
      >
        <UserCheck class="w-4 h-4 mb-0.5" />
        <span>{{ t('nav_profile', store.locale) }}</span>
        <span v-if="store.profile && !store.profile.is_confirmed" class="w-1.5 h-1.5 rounded-full bg-amber-500 absolute top-1 right-2 animate-pulse"></span>
      </router-link>

      <router-link
        to="/schemes"
        class="flex flex-col items-center py-1 px-2 rounded-xl text-[10px] font-bold transition-colors relative"
        :class="route.path === '/schemes' ? 'text-indigo-600 bg-indigo-50/80' : 'text-slate-500 hover:text-slate-800'"
      >
        <Award class="w-4 h-4 mb-0.5" />
        <span>{{ t('nav_schemes', store.locale) }}</span>
        <span v-if="store.evaluationSummary?.likely_eligible" class="text-[9px] px-1 bg-emerald-500 text-white font-black rounded-full absolute -top-0.5 right-1">
          {{ store.evaluationSummary.likely_eligible }}
        </span>
      </router-link>

      <router-link
        to="/family"
        class="flex flex-col items-center py-1 px-2 rounded-xl text-[10px] font-bold transition-colors"
        :class="route.path === '/family' ? 'text-indigo-600 bg-indigo-50/80' : 'text-slate-500 hover:text-slate-800'"
      >
        <Users class="w-4 h-4 mb-0.5" />
        <span>Family</span>
      </router-link>

      <router-link
        to="/documents"
        class="flex flex-col items-center py-1 px-2.5 rounded-xl text-[10px] font-bold transition-colors"
        :class="route.path === '/documents' ? 'text-indigo-600 bg-indigo-50/80' : 'text-slate-500 hover:text-slate-800'"
      >
        <FileText class="w-4 h-4 mb-0.5" />
        <span>{{ t('nav_documents', store.locale) }}</span>
      </router-link>

      <router-link
        to="/tracker"
        class="flex flex-col items-center py-1 px-2.5 rounded-xl text-[10px] font-bold transition-colors relative"
        :class="route.path === '/tracker' ? 'text-indigo-600 bg-indigo-50/80' : 'text-slate-500 hover:text-slate-800'"
      >
        <CheckCircle2 class="w-4 h-4 mb-0.5" />
        <span>{{ t('nav_tracker', store.locale) }}</span>
        <span v-if="store.trackedApplications.length > 0" class="text-[9px] px-1 bg-indigo-600 text-white font-black rounded-full absolute -top-0.5 right-1">
          {{ store.trackedApplications.length }}
        </span>
      </router-link>
    </nav>

    <!-- Civic Tech Footer -->
    <footer class="bg-white border-t border-slate-200 mt-12 py-8">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
        <div class="flex items-center gap-2">
          <span class="font-bold text-slate-800">YOJNAVIA</span>
          <span>•</span>
          <span>{{ t('brand_subtitle', store.locale) }}</span>
          <span>•</span>
          <span class="inline-flex items-center gap-1 text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200 font-medium">
            <ShieldCheck class="w-3 h-3 text-emerald-600" />
            Zero-PII Advisory Assistant
          </span>
        </div>

        <div class="flex items-center gap-4">
          <span>Official GR citations from MahaDBT & Aaple Sarkar</span>
          <span>•</span>
          <span>Built for Maharashtra Higher Education</span>
        </div>
      </div>
    </footer>
  </div>
</template>
