<script setup lang="ts">
import { useRouter } from 'vue-router';
import { 
  Sparkles, 
  Mic, 
  MessageSquare, 
  Building2, 
  ArrowRight, 
  CheckCircle2, 
  ShieldCheck, 
  Scale, 
  FileCheck2, 
  Clock, 
  AlertTriangle, 
  Lock, 
  Smartphone, 
  BookOpen, 
  Languages, 
  FileText, 
  GraduationCap, 
  Users, 
  HelpCircle,
  ExternalLink
} from '@lucide/vue';

const router = useRouter();

function startDiscovery(mode?: string) {
  if (mode === 'voice') {
    router.push({ path: '/app', query: { voice: 'true' } });
  } else {
    router.push('/app');
  }
}
</script>

<template>
  <div class="min-h-screen bg-[#FBFBFA] text-[#0B132B]">

    <!-- HERO SECTION -->
    <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-10 sm:pt-16 pb-16 sm:pb-24">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-12 items-center">
        
        <!-- Left Hero Copy -->
        <div class="lg:col-span-7 space-y-6">
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full border-[1.5px] border-[#0B132B] bg-[#FFFBEB] text-[#0B132B] text-xs font-extrabold uppercase tracking-widest shadow-[1.5px_1.5px_0_0_#0B132B]">
            <span class="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></span>
            <span>100% Statutory GRs • Zero Bureaucracy • Maharashtra</span>
          </div>

          <h1 class="text-3xl sm:text-5xl lg:text-6xl font-black text-[#0B132B] tracking-tight leading-[1.1] font-heading">
            Discover every government scheme in 
            <span class="bg-[#FDE047] text-[#0B132B] px-2 py-0.5 rounded-sm inline-block shadow-[2px_2px_0_0_#0B132B] mt-1 sm:mt-0">
              your own language.
            </span>
          </h1>

          <p class="text-base sm:text-lg text-slate-700 leading-relaxed font-medium max-w-2xl">
            A direct statutory welfare engine for Maharashtra citizens and students to pre-audit welfare qualifications, find missing documents, and track sanctions without agents or confusion.
          </p>

          <div class="pt-2 flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
            <button
              @click="startDiscovery()"
              class="neo-btn bg-[#E11D48] hover:bg-[#BE123C] text-white px-7 py-3.5 text-sm sm:text-base font-extrabold tracking-wide flex items-center justify-center gap-2 shadow-[2.5px_2.5px_0_0_#0B132B] cursor-pointer"
            >
              <span>Start Scheme Discovery</span>
              <ArrowRight class="w-4 h-4" />
            </button>

            <button
              @click="startDiscovery('voice')"
              class="neo-btn neo-btn-paper px-5 py-3.5 text-sm font-bold text-[#0B132B] flex items-center justify-center gap-2 cursor-pointer"
            >
              <Mic class="w-4 h-4 text-amber-600" />
              <span>Speak in Marathi / Hindi</span>
            </button>
          </div>

          <div class="text-xs text-slate-500 flex flex-wrap items-center gap-x-3 gap-y-1 font-semibold pt-1">
            <span>Free forever</span>
            <span>•</span>
            <span>No login required to audit</span>
            <span>•</span>
            <span>Deterministic Government Resolution rules</span>
          </div>
        </div>

        <!-- Right Hero Mockup Window -->
        <div class="lg:col-span-5">
          <div class="neo-box bg-white overflow-hidden shadow-[4px_4px_0_0_#0B132B]">
            <!-- Window Top Bar -->
            <div class="bg-[#0B132B] text-white px-4 py-2.5 flex items-center justify-between text-xs font-mono">
              <div class="flex items-center gap-1.5">
                <span class="w-2.5 h-2.5 rounded-full bg-red-400"></span>
                <span class="w-2.5 h-2.5 rounded-full bg-amber-400"></span>
                <span class="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
                <span class="ml-2 font-bold text-[11px] text-slate-200">MahaDBT Eligibility Audit</span>
              </div>
              <span class="text-[10px] bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded font-bold">
                GR Certified
              </span>
            </div>

            <!-- Window Content -->
            <div class="p-5 space-y-4 text-xs">
              <!-- Citizen Query Card -->
              <div class="p-3 bg-[#F5F5F3] rounded-xl border-[1.5px] border-[#0B132B] shadow-[1.5px_1.5px_0_0_#0B132B]">
                <div class="text-[10px] uppercase font-bold text-slate-500">Citizen Profile Facts:</div>
                <div class="font-bold text-[#0B132B] text-sm mt-0.5">
                  Age 20 • OBC Category • Sangli, MH
                </div>
                <div class="text-xs text-slate-600 mt-1 flex flex-wrap gap-x-2">
                  <span>Family Income: <strong>₹1,40,000/yr</strong></span>
                  <span>•</span>
                  <span>Course: <strong>B.Tech CAP Round</strong></span>
                </div>
              </div>

              <!-- Verdict Result Card -->
              <div class="p-4 bg-[#FEF3C7] rounded-xl border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#0B132B] space-y-2">
                <div class="flex items-center justify-between">
                  <span class="neo-stamp neo-stamp-emerald text-[9px]">100% Eligible</span>
                  <span class="font-mono text-[10px] font-bold text-slate-600">MH_DTE_EBC_2024</span>
                </div>
                <div class="font-extrabold text-[#0B132B] text-sm sm:text-base font-heading">
                  Rajarshi Chhatrapati Shahu Maharaj EBC Freeship
                </div>
                <div class="p-2 bg-white rounded-lg border border-[#0B132B]/30 font-bold text-emerald-900 text-xs">
                  Direct Entitlement: 50% Tuition Fee Waiver (₹42,500/yr) + Hosteller Stipend
                </div>
                <div class="text-[11px] text-slate-700 leading-normal font-medium">
                  Statutory GR: Higher & Tech Ed. Resolution No. 201806201732049608
                </div>
              </div>

              <!-- Quick Action Buttons Inside Mockup -->
              <div class="grid grid-cols-3 gap-2 pt-1">
                <button @click="startDiscovery()" class="neo-btn neo-btn-paper py-2 text-[11px] font-bold text-[#0B132B]">
                  Check Docs
                </button>
                <button @click="startDiscovery()" class="neo-btn neo-btn-paper py-2 text-[11px] font-bold text-[#0B132B]">
                  Preflight ⚡
                </button>
                <button @click="startDiscovery()" class="neo-btn neo-btn-navy py-2 text-[11px] font-bold text-white">
                  Apply Now
                </button>
              </div>
            </div>
          </div>
        </div>

      </div>
    </section>

    <!-- SECTION 2: THREE WAYS TO USE -->
    <section class="border-t-[1.5px] border-[#0B132B] bg-white py-16 sm:py-20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="mb-10">
          <div class="text-xs font-extrabold uppercase tracking-widest text-slate-500 font-mono mb-1">
            Three Ways to Discover
          </div>
          <h2 class="text-2xl sm:text-4xl font-extrabold text-[#0B132B] tracking-tight font-heading">
            Ask the way that suits you.
          </h2>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <!-- Card 1: Voice (Yellow Tint) -->
          <div 
            @click="startDiscovery('voice')"
            class="neo-box-interactive p-6 bg-[#FEF3C7] flex flex-col justify-between"
          >
            <div class="space-y-4">
              <div class="w-10 h-10 rounded-xl bg-white border-[1.5px] border-[#0B132B] text-amber-700 flex items-center justify-center shadow-[1.5px_1.5px_0_0_#0B132B]">
                <Mic class="w-5 h-5" />
              </div>
              <div>
                <h3 class="text-lg font-extrabold text-[#0B132B] font-heading">Ask by voice</h3>
                <p class="text-xs sm:text-sm text-slate-800 font-medium mt-1 leading-relaxed">
                  Speak in Marathi or Hindi: <em>"मी सांगलीचा आहे, बी.टेक करतोय, उत्पन्न १ लाख आहे."</em> Sarvam AI Saaras v4 transcribes native speech into confirmed profile facts.
                </p>
              </div>
            </div>
            <div class="pt-6 flex items-center justify-between text-xs font-bold text-[#0B132B]">
              <span class="inline-flex items-center gap-1 hover:underline">
                <span>Start speaking</span>
                <ArrowRight class="w-3.5 h-3.5" />
              </span>
              <span class="neo-stamp bg-white text-[9px]">Sarvam STT</span>
            </div>
          </div>

          <!-- Card 2: Guided Chat -->
          <div 
            @click="startDiscovery()"
            class="neo-box-interactive p-6 bg-white flex flex-col justify-between"
          >
            <div class="space-y-4">
              <div class="w-10 h-10 rounded-xl bg-[#F5F5F3] border-[1.5px] border-[#0B132B] text-slate-800 flex items-center justify-center shadow-[1.5px_1.5px_0_0_#0B132B]">
                <MessageSquare class="w-5 h-5" />
              </div>
              <div>
                <h3 class="text-lg font-extrabold text-[#0B132B] font-heading">Interactive guided chat</h3>
                <p class="text-xs sm:text-sm text-slate-700 font-medium mt-1 leading-relaxed">
                  Answer 5 simple factual questions (income, caste, district, course) with quick-tap choice pills. Zero government bureaucracy or legal confusion.
                </p>
              </div>
            </div>
            <div class="pt-6 flex items-center justify-between text-xs font-bold text-[#0B132B]">
              <span class="inline-flex items-center gap-1 hover:underline">
                <span>Start chat</span>
                <ArrowRight class="w-3.5 h-3.5" />
              </span>
              <span class="neo-stamp bg-slate-100 text-[9px]">3 Minutes</span>
            </div>
          </div>

          <!-- Card 3: CSC Counselor -->
          <router-link
            to="/counselor"
            class="neo-box-interactive p-6 bg-white flex flex-col justify-between"
          >
            <div class="space-y-4">
              <div class="w-10 h-10 rounded-xl bg-[#F5F5F3] border-[1.5px] border-[#0B132B] text-slate-800 flex items-center justify-center shadow-[1.5px_1.5px_0_0_#0B132B]">
                <Building2 class="w-5 h-5 text-amber-600" />
              </div>
              <div>
                <h3 class="text-lg font-extrabold text-[#0B132B] font-heading">CSC Kendra assisted desk</h3>
                <p class="text-xs sm:text-sm text-slate-700 font-medium mt-1 leading-relaxed">
                  Need in-person support? Village-Level Entrepreneurs (VLEs) and college scholarship clerks use our assisted desk to run preflight audits with verified citizen consent.
                </p>
              </div>
            </div>
            <div class="pt-6 flex items-center justify-between text-xs font-bold text-[#0B132B]">
              <span class="inline-flex items-center gap-1 hover:underline">
                <span>Open Counselor Desk</span>
                <ArrowRight class="w-3.5 h-3.5" />
              </span>
              <span class="neo-stamp neo-stamp-navy text-[9px]">VLE Kendra</span>
            </div>
          </router-link>
        </div>
      </div>
    </section>

    <!-- SECTION 3: NOT GUESSES, STATUTORY CERTAINTY -->
    <section class="border-t-[1.5px] border-[#0B132B] bg-[#FBFBFA] py-16 sm:py-20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-12 items-start">
          
          <div class="lg:col-span-5 space-y-4">
            <div class="text-xs font-extrabold uppercase tracking-widest text-slate-500 font-mono">
              Legal Rigour & Transparency
            </div>
            <h2 class="text-2xl sm:text-4xl font-extrabold text-[#0B132B] tracking-tight font-heading leading-tight">
              Not guesses,
              <span class="bg-[#FDE047] text-[#0B132B] px-1.5 py-0.5 rounded-sm inline-block shadow-[1.5px_1.5px_0_0_#0B132B]">
                statutory certainty.
              </span>
            </h2>
            <p class="text-sm text-slate-700 leading-relaxed font-medium">
              Most portals give vague, AI-hallucinated scheme lists that get citizens rejected at the clerk desk. Yojnavia runs deterministic statutory code verified against official Government Gazette Resolutions.
            </p>
            <div class="pt-2">
              <button
                @click="startDiscovery()"
                class="neo-btn neo-btn-navy px-5 py-2.5 text-xs font-bold"
              >
                <span>Audit Your Eligibility</span>
                <ArrowRight class="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          <div class="lg:col-span-7 space-y-3">
            <div class="neo-box p-4 bg-white flex items-start gap-4">
              <span class="neo-stamp neo-stamp-navy text-xs font-mono font-bold shrink-0 mt-0.5">01</span>
              <div>
                <h4 class="font-extrabold text-[#0B132B] text-sm font-heading">Official GR Gazette Citations</h4>
                <p class="text-xs text-slate-600 mt-0.5 font-medium">
                  Every single eligibility rule links to the official government resolution number and department circular passage.
                </p>
              </div>
            </div>

            <div class="neo-box p-4 bg-white flex items-start gap-4">
              <span class="neo-stamp neo-stamp-navy text-xs font-mono font-bold shrink-0 mt-0.5">02</span>
              <div>
                <h4 class="font-extrabold text-[#0B132B] text-sm font-heading">Deterministic Logic, 0% Hallucination</h4>
                <p class="text-xs text-slate-600 mt-0.5 font-medium">
                  No LLM decides whether you get money. Pure mathematical boundary tests verify income limits, age cutoffs, and caste quotas.
                </p>
              </div>
            </div>

            <div class="neo-box p-4 bg-white flex items-start gap-4">
              <span class="neo-stamp neo-stamp-navy text-xs font-mono font-bold shrink-0 mt-0.5">03</span>
              <div>
                <h4 class="font-extrabold text-[#0B132B] text-sm font-heading">Preflight Scrutiny Audit</h4>
                <p class="text-xs text-slate-600 mt-0.5 font-medium">
                  We verify your certificate formats, issuing authority designations, and validity periods before you submit to MahaDBT.
                </p>
              </div>
            </div>

            <div class="neo-box p-4 bg-white flex items-start gap-4">
              <span class="neo-stamp neo-stamp-navy text-xs font-mono font-bold shrink-0 mt-0.5">04</span>
              <div>
                <h4 class="font-extrabold text-[#0B132B] text-sm font-heading">Maharashtra RTS Act 2015 Timelines</h4>
                <p class="text-xs text-slate-600 mt-0.5 font-medium">
                  Know exact statutory SLA days for Tahsildar income, domicile, and non-creamy layer certificates with appeal paths.
                </p>
              </div>
            </div>
          </div>

        </div>
      </div>
    </section>

    <!-- SECTION 4: COVERAGE ACROSS MAHARASHTRA -->
    <section class="border-t-[1.5px] border-[#0B132B] bg-white py-16 sm:py-20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-10">
          <div>
            <div class="text-xs font-extrabold uppercase tracking-widest text-slate-500 font-mono mb-1">
              Comprehensive Coverage
            </div>
            <h2 class="text-2xl sm:text-4xl font-extrabold text-[#0B132B] tracking-tight font-heading">
              All Major Maharashtra Portals in One Place.
            </h2>
          </div>
          <router-link
            to="/schemes"
            class="neo-btn neo-btn-paper px-4 py-2 text-xs font-bold text-[#0B132B] self-start sm:self-auto"
          >
            <span>Browse Full Scheme Catalog</span>
            <ArrowRight class="w-3.5 h-3.5" />
          </router-link>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="neo-box p-5 bg-[#FBFBFA] space-y-3">
            <span class="neo-stamp neo-stamp-navy text-[10px]">DTE & DHE</span>
            <h3 class="font-extrabold text-[#0B132B] text-base font-heading">Higher Education</h3>
            <p class="text-xs text-slate-600 font-medium leading-relaxed">
              Rajarshi Shahu Maharaj Tuition Fee (EBC), Dr. Panjabrao Deshmukh Hostel Allowance for Engineering, Medical, & Polytechnic.
            </p>
          </div>

          <div class="neo-box p-5 bg-[#FBFBFA] space-y-3">
            <span class="neo-stamp neo-stamp-emerald text-[10px]">Social Justice</span>
            <h3 class="font-extrabold text-[#0B132B] text-base font-heading">Social Welfare & Tribal</h3>
            <p class="text-xs text-slate-600 font-medium leading-relaxed">
              SC, ST, VJNT, OBC Post-Matric Scholarships, Freeships, Bharatratna Dr. Ambedkar Swadhar Scheme & Pandit Deendayal Hostels.
            </p>
          </div>

          <div class="neo-box p-5 bg-[#FBFBFA] space-y-3">
            <span class="neo-stamp neo-stamp-amber text-[10px]">Revenue Dept</span>
            <h3 class="font-extrabold text-[#0B132B] text-base font-heading">Aaple Sarkar Certificates</h3>
            <p class="text-xs text-slate-600 font-medium leading-relaxed">
              Tahsildar Income Certificates, State Domicile, Non-Creamy Layer (NCL), Caste Validity, and RTS legal SLA tracking.
            </p>
          </div>

          <div class="neo-box p-5 bg-[#FBFBFA] space-y-3">
            <span class="neo-stamp text-[10px] bg-purple-100 text-purple-900 border-[1.5px] border-[#0B132B]">Direct DBT</span>
            <h3 class="font-extrabold text-[#0B132B] text-base font-heading">Citizen & Farm Welfare</h3>
            <p class="text-xs text-slate-600 font-medium leading-relaxed">
              Mukhyamantri Majhi Ladki Bahin Yojana, PM-Kisan & Namo Shetkari Mahasanman Nidhi, Sanjay Gandhi Niradhar.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- SECTION 5: SOFT BLUE CONTRAST SECTION (LOW CONNECTIVITY / OFFLINE) -->
    <section class="border-t-[1.5px] border-[#0B132B] bg-[#EEF4F8] py-16 sm:py-20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
          
          <div class="lg:col-span-6 space-y-4">
            <div class="text-xs font-extrabold uppercase tracking-widest text-[#0B132B] font-mono">
              Rural & Kendra Ready
            </div>
            <h2 class="text-2xl sm:text-4xl font-extrabold text-[#0B132B] tracking-tight font-heading leading-tight">
              Slow network?
              <span class="block text-slate-800">Yojnavia keeps working.</span>
            </h2>
            <p class="text-sm text-slate-700 leading-relaxed font-medium">
              Designed specifically for remote talukas, crowded Cyber Cafes, and patchy 2G mobile coverage. Lightweight, low-bandwidth, and generates physical printable handover slips for college clerks.
            </p>
          </div>

          <div class="lg:col-span-6">
            <div class="neo-box p-6 bg-white space-y-3">
              <div class="p-3 rounded-xl border-[1.5px] border-[#0B132B] bg-[#FBFBFA] flex items-center justify-between text-xs font-bold">
                <span class="flex items-center gap-2">
                  <FileText class="w-4 h-4 text-amber-600" />
                  <span>Downloadable Offline PDF Checklist</span>
                </span>
                <span class="neo-stamp neo-stamp-emerald text-[9px]">Print-Ready</span>
              </div>

              <div class="p-3 rounded-xl border-[1.5px] border-[#0B132B] bg-[#FBFBFA] flex items-center justify-between text-xs font-bold">
                <span class="flex items-center gap-2">
                  <Smartphone class="w-4 h-4 text-emerald-600" />
                  <span>Safe on Shared Mobile Phones (No passwords stored)</span>
                </span>
                <span class="neo-stamp text-[9px] bg-slate-100">Zero PII</span>
              </div>

              <div class="p-3 rounded-xl border-[1.5px] border-[#0B132B] bg-[#FBFBFA] flex items-center justify-between text-xs font-bold">
                <span class="flex items-center gap-2">
                  <Clock class="w-4 h-4 text-indigo-600" />
                  <span>College Scholarship Clerk Physical Handover Slips</span>
                </span>
                <span class="neo-stamp neo-stamp-navy text-[9px]">Mandatory Step</span>
              </div>

              <div class="p-3 bg-[#FEF3C7] rounded-xl border-[1.5px] border-[#0B132B] text-xs text-amber-950 font-bold flex items-center gap-2">
                <CheckCircle2 class="w-4 h-4 text-amber-700 shrink-0" />
                <span>100% offline-friendly document checklists for revenue office visits.</span>
              </div>
            </div>
          </div>

        </div>
      </div>
    </section>

    <!-- SECTION 6: DARK SECTION (PREFLIGHT AUDIT & REJECTIONS) -->
    <section class="border-t-[1.5px] border-[#0B132B] bg-[#0B132B] text-white py-16 sm:py-24">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
          
          <div class="lg:col-span-6 space-y-5">
            <span class="neo-stamp neo-stamp-amber text-[10px]">
              Preflight Scrutiny Audit
            </span>
            <h2 class="text-2xl sm:text-4xl font-extrabold text-white tracking-tight font-heading leading-tight">
              Stop losing scholarships to clerical rejections.
            </h2>
            <p class="text-sm text-slate-300 leading-relaxed font-medium">
              Over 38% of MahaDBT applications get queried or rejected due to minor certificate mismatches or missing Tahsildar seals. Yojnavia detects defects before you submit.
            </p>

            <div class="space-y-2.5 text-xs text-slate-200 font-medium">
              <div class="flex items-center gap-2">
                <span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
                <span>15-day statutory resubmission clock with countdown alerts.</span>
              </div>
              <div class="flex items-center gap-2">
                <span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
                <span>Direct RTS Act First Appeal navigator for delayed government sanctions.</span>
              </div>
            </div>

            <div class="pt-2">
              <button
                @click="startDiscovery()"
                class="neo-btn bg-[#F59E0B] hover:bg-[#D97706] text-[#0B132B] px-6 py-3 text-xs font-black shadow-[2.5px_2.5px_0_0_#FFFFFF] cursor-pointer"
              >
                <span>Run Free Preflight Audit</span>
                <ArrowRight class="w-4 h-4" />
              </button>
            </div>
          </div>

          <!-- Right Breakdown Bar Mockup -->
          <div class="lg:col-span-6">
            <div class="bg-white text-[#0B132B] rounded-2xl border-[1.5px] border-[#0B132B] p-6 shadow-[4px_4px_0_0_#F59E0B] space-y-4">
              <div class="flex items-center justify-between pb-2 border-b-[1.5px] border-[#0B132B]/15">
                <span class="font-extrabold text-sm font-heading">Application Scrutiny Checklist</span>
                <span class="neo-stamp neo-stamp-emerald text-[9px]">92% Ready</span>
              </div>

              <div class="space-y-3 text-xs">
                <div>
                  <div class="flex items-center justify-between font-bold mb-1">
                    <span>Domicile Certificate (Aaple Sarkar)</span>
                    <span class="text-emerald-700">Valid</span>
                  </div>
                  <div class="w-full h-2 rounded-full bg-slate-100 overflow-hidden border border-[#0B132B]/20">
                    <div class="h-full bg-emerald-600 rounded-full w-full"></div>
                  </div>
                </div>

                <div>
                  <div class="flex items-center justify-between font-bold mb-1">
                    <span>Tahsildar Income Certificate (&lt; ₹8 Lakh)</span>
                    <span class="text-emerald-700">Valid</span>
                  </div>
                  <div class="w-full h-2 rounded-full bg-slate-100 overflow-hidden border border-[#0B132B]/20">
                    <div class="h-full bg-emerald-600 rounded-full w-full"></div>
                  </div>
                </div>

                <div>
                  <div class="flex items-center justify-between font-bold mb-1">
                    <span>Non-Creamy Layer Validity</span>
                    <span class="text-amber-700 font-mono">Expires March 31</span>
                  </div>
                  <div class="w-full h-2 rounded-full bg-slate-100 overflow-hidden border border-[#0B132B]/20">
                    <div class="h-full bg-amber-500 rounded-full w-3/4"></div>
                  </div>
                </div>
              </div>

              <div class="p-3 bg-[#FFFBEB] rounded-xl border-[1.5px] border-[#0B132B] text-xs text-amber-950 font-bold leading-relaxed">
                Advisory: Submit updated income certificate before portal cut-off date to avoid college clerk query.
              </div>
            </div>
          </div>

        </div>
      </div>
    </section>

    <!-- SECTION 7: CONSTITUTIONAL TRANSPARENCY -->
    <section class="border-t-[1.5px] border-[#0B132B] bg-white py-16 sm:py-20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center max-w-2xl mx-auto mb-12">
          <div class="text-xs font-extrabold uppercase tracking-widest text-slate-500 font-mono mb-1">
            Privacy & Trust
          </div>
          <h2 class="text-2xl sm:text-4xl font-extrabold text-[#0B132B] tracking-tight font-heading">
            Constitutional Transparency. Zero Hidden Fine Print.
          </h2>
          <p class="text-xs sm:text-sm text-slate-600 mt-2 font-medium">
            Built as a public utility to protect citizens from predatory touts, fake portals, and illegal fee solicitation.
          </p>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div class="neo-box p-6 bg-[#FBFBFA] space-y-3">
            <div class="w-10 h-10 rounded-xl bg-white border-[1.5px] border-[#0B132B] flex items-center justify-center text-slate-800 shadow-[1.5px_1.5px_0_0_#0B132B]">
              <Lock class="w-5 h-5 text-emerald-600" />
            </div>
            <h3 class="font-extrabold text-[#0B132B] text-base font-heading">Minimal Data</h3>
            <p class="text-xs text-slate-600 font-medium leading-relaxed">
              We never ask for your Aadhaar number, OTPs, portal passwords, or bank PINs. Ever.
            </p>
          </div>

          <div class="neo-box p-6 bg-[#FBFBFA] space-y-3">
            <div class="w-10 h-10 rounded-xl bg-white border-[1.5px] border-[#0B132B] flex items-center justify-center text-slate-800 shadow-[1.5px_1.5px_0_0_#0B132B]">
              <Smartphone class="w-5 h-5 text-amber-600" />
            </div>
            <h3 class="font-extrabold text-[#0B132B] text-base font-heading">Works on Shared Phones</h3>
            <p class="text-xs text-slate-600 font-medium leading-relaxed">
              Use it on a friend's phone or cyber cafe. Zero persistent personal credentials saved.
            </p>
          </div>

          <div class="neo-box p-6 bg-[#FBFBFA] space-y-3">
            <div class="w-10 h-10 rounded-xl bg-white border-[1.5px] border-[#0B132B] flex items-center justify-center text-slate-800 shadow-[1.5px_1.5px_0_0_#0B132B]">
              <Scale class="w-5 h-5 text-indigo-600" />
            </div>
            <h3 class="font-extrabold text-[#0B132B] text-base font-heading">Verifiable Citations</h3>
            <p class="text-xs text-slate-600 font-medium leading-relaxed">
              Every single qualification rule cites official Maharashtra Government Resolutions.
            </p>
          </div>

          <div class="neo-box p-6 bg-[#FBFBFA] space-y-3">
            <div class="w-10 h-10 rounded-xl bg-white border-[1.5px] border-[#0B132B] flex items-center justify-center text-slate-800 shadow-[1.5px_1.5px_0_0_#0B132B]">
              <Languages class="w-5 h-5 text-rose-600" />
            </div>
            <h3 class="font-extrabold text-[#0B132B] text-base font-heading">Easy to Read</h3>
            <p class="text-xs text-slate-600 font-medium leading-relaxed">
              Complex government circulars translated into plain conversational Marathi, Hindi, and English.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- SECTION 8: CSC OPERATOR & INSTITUTION PILOT -->
    <section class="border-t-[1.5px] border-[#0B132B] bg-[#FBFBFA] py-16 sm:py-20">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="neo-box p-8 sm:p-12 bg-white flex flex-col lg:flex-row items-center justify-between gap-8 shadow-[4px_4px_0_0_#0B132B]">
          <div class="space-y-3 max-w-2xl">
            <span class="neo-stamp neo-stamp-navy text-[10px]">
              For CSC Centers, Colleges & Panchayats
            </span>
            <h2 class="text-2xl sm:text-3xl font-extrabold text-[#0B132B] font-heading">
              Operate an authorized assisted welfare desk.
            </h2>
            <p class="text-xs sm:text-sm text-slate-700 leading-relaxed font-medium">
              VLE operators, student counselors, and NGOs can manage citizen intake with explicit digital consent, conduct preflight audits, and track cases without cross-center data leakage.
            </p>
          </div>

          <div class="shrink-0 flex flex-col sm:flex-row items-center gap-3 w-full lg:w-auto">
            <router-link
              to="/counselor"
              class="neo-btn neo-btn-navy w-full sm:w-auto px-6 py-3 text-xs sm:text-sm font-bold"
            >
              <span>Open Counselor Desk</span>
              <ArrowRight class="w-4 h-4" />
            </router-link>
          </div>
        </div>
      </div>
    </section>

    <!-- SECTION 9: YELLOW FULL-WIDTH BANNER CTA -->
    <section class="border-t-[1.5px] border-[#0B132B] bg-[#F59E0B] py-12 sm:py-16">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-6">
        <div>
          <h2 class="text-2xl sm:text-3xl font-black text-[#0B132B] tracking-tight font-heading">
            Discover your government entitlements today.
          </h2>
          <p class="text-xs sm:text-sm text-amber-950 font-bold mt-1">
            Free • Takes 3 minutes • 100% deterministic Maharashtra GR rules
          </p>
        </div>

        <button
          @click="startDiscovery()"
          class="neo-btn bg-white hover:bg-slate-50 text-[#0B132B] px-8 py-3.5 text-sm font-extrabold shadow-[2.5px_2.5px_0_0_#0B132B] shrink-0 cursor-pointer"
        >
          <span>Start Scheme Discovery</span>
          <ArrowRight class="w-4 h-4" />
        </button>
      </div>
    </section>

  </div>
</template>
