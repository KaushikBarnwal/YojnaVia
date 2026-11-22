<script setup lang="ts">
import { useRouter } from 'vue-router';
import { 
  Mic, 
  MessageSquare, 
  Building2, 
  ArrowRight, 
  CheckCircle2, 
  Scale, 
  Clock, 
  Lock, 
  Smartphone, 
  Languages, 
  FileText
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
            <span>Official Maharashtra government rules • No paperwork maze • Maharashtra</span>
          </div>

          <h1 class="text-3xl sm:text-5xl lg:text-6xl font-black text-[#0B132B] tracking-tight leading-[1.1] font-heading">
            Find every government scheme in 
            <span class="bg-[#FDE047] text-[#0B132B] px-2 py-0.5 rounded-sm inline-block shadow-[2px_2px_0_0_#0B132B] mt-1 sm:mt-0">
              your own language.
            </span>
          </h1>

          <p class="text-base sm:text-lg text-slate-700 leading-relaxed font-medium max-w-2xl">
            Check which Maharashtra government schemes you qualify for, find missing documents, and track your application. No agents needed.
          </p>

          <div class="pt-2 flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
            <button
              @click="startDiscovery()"
              class="neo-btn bg-[#E11D48] hover:bg-[#BE123C] text-white px-7 py-3.5 text-sm sm:text-base font-extrabold tracking-wide flex items-center justify-center gap-2 shadow-[2.5px_2.5px_0_0_#0B132B] cursor-pointer"
            >
              <span>Find schemes for me</span>
              <ArrowRight class="w-4 h-4" />
            </button>

            <button
              @click="startDiscovery('voice')"
              class="neo-btn neo-btn-paper px-5 py-3.5 text-sm font-bold text-[#0B132B] flex items-center justify-center gap-2 cursor-pointer"
            >
              <Mic class="w-4 h-4 text-amber-600" />
              <span>Speak in Marathi or Hindi</span>
            </button>
          </div>

          <div class="text-xs text-slate-500 flex flex-wrap items-center gap-x-3 gap-y-1 font-semibold pt-1">
            <span>Free forever</span>
            <span>•</span>
            <span>No login needed to check</span>
            <span>•</span>
            <span>Based on official government rules</span>
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
                <span class="ml-2 font-bold text-[11px] text-slate-200">MahaDBT Eligibility Check</span>
              </div>
              <span class="text-[10px] bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded font-bold">
                Official rules checked
              </span>
            </div>

            <!-- Window Content -->
            <div class="p-5 space-y-4 text-xs">
              <!-- Citizen Query Card -->
              <div class="p-3 bg-[#F5F5F3] rounded-xl border-[1.5px] border-[#0B132B] shadow-[1.5px_1.5px_0_0_#0B132B]">
                <div class="text-[10px] uppercase font-bold text-slate-500">Your details:</div>
                <div class="font-bold text-[#0B132B] text-sm mt-0.5">
                  Age 20 • OBC Category • Sangli, MH
                </div>
                <div class="text-xs text-slate-600 mt-1 flex flex-wrap gap-x-2">
                  <span>Yearly family income: <strong>₹1,40,000/yr</strong></span>
                  <span>•</span>
                  <span>Course: <strong>B.Tech CAP Round</strong></span>
                </div>
              </div>

              <!-- Verdict Result Card -->
              <div class="p-4 bg-[#FEF3C7] rounded-xl border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#0B132B] space-y-2">
                <div class="flex items-center justify-between">
                  <span class="neo-stamp neo-stamp-emerald text-[9px]">Eligible</span>
                  <span class="font-mono text-[10px] font-bold text-slate-600">MH_DTE_EBC_2024</span>
                </div>
                <div class="font-extrabold text-[#0B132B] text-sm sm:text-base font-heading">
                  Rajarshi Chhatrapati Shahu Maharaj EBC Freeship
                </div>
                <div class="p-2 bg-white rounded-lg border border-[#0B132B]/30 font-bold text-emerald-900 text-xs">
                  You get: 50% tuition fee waived (₹42,500 a year) + hostel stipend
                </div>
                <div class="text-[11px] text-slate-700 leading-normal font-medium">
                  Official government order: Higher & Technical Education, No. 201806201732049608
                </div>
              </div>

              <!-- Quick Action Buttons Inside Mockup -->
              <div class="grid grid-cols-3 gap-2 pt-1">
                <button @click="startDiscovery()" class="neo-btn neo-btn-paper py-2 text-[11px] font-bold text-[#0B132B]">
                  Check documents
                </button>
                <button @click="startDiscovery()" class="neo-btn neo-btn-paper py-2 text-[11px] font-bold text-[#0B132B]">
                  Quick check ⚡
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
            Three ways to find schemes
          </div>
          <h2 class="text-2xl sm:text-4xl font-extrabold text-[#0B132B] tracking-tight font-heading">
            Pick the way that suits you.
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
                  Speak in Marathi or Hindi: <em>"मी सांगलीचा आहे, बी.टेक करतोय, उत्पन्न १ लाख आहे."</em> Sarvam AI Saaras v4 listens to your speech and types out your details.
                </p>
              </div>
            </div>
            <div class="pt-6 flex items-center justify-between text-xs font-bold text-[#0B132B]">
              <span class="inline-flex items-center gap-1 hover:underline">
                <span>Start speaking</span>
                <ArrowRight class="w-3.5 h-3.5" />
              </span>
              <span class="neo-stamp bg-white text-[9px]">Speech to text</span>
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
                <h3 class="text-lg font-extrabold text-[#0B132B] font-heading">Guided chat</h3>
                <p class="text-xs sm:text-sm text-slate-700 font-medium mt-1 leading-relaxed">
                  Answer 5 simple questions about your income, caste, district and course. Just tap your choice.
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
                <h3 class="text-lg font-extrabold text-[#0B132B] font-heading">Help desk at a CSC centre (Common Service Centre)</h3>
                <p class="text-xs sm:text-sm text-slate-700 font-medium mt-1 leading-relaxed">
                  Need help in person? Village computer operators (VLEs) and college clerks can use this desk to check applications, with your permission.
                </p>
              </div>
            </div>
            <div class="pt-6 flex items-center justify-between text-xs font-bold text-[#0B132B]">
              <span class="inline-flex items-center gap-1 hover:underline">
                <span>Open help desk</span>
                <ArrowRight class="w-3.5 h-3.5" />
              </span>
              <span class="neo-stamp neo-stamp-navy text-[9px]">CSC centre</span>
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
              Official rules, clearly shown
            </div>
            <h2 class="text-2xl sm:text-4xl font-extrabold text-[#0B132B] tracking-tight font-heading leading-tight">
              Not guesses,
              <span class="bg-[#FDE047] text-[#0B132B] px-1.5 py-0.5 rounded-sm inline-block shadow-[1.5px_1.5px_0_0_#0B132B]">
                official rules.
              </span>
            </h2>
            <p class="text-sm text-slate-700 leading-relaxed font-medium">
              Many websites give vague or wrong scheme lists, and applications get rejected at the clerk desk. YojnaVia checks every rule against official government orders.
            </p>
            <div class="pt-2">
              <button
                @click="startDiscovery()"
                class="neo-btn neo-btn-navy px-5 py-2.5 text-xs font-bold"
              >
                <span>Check your eligibility</span>
                <ArrowRight class="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          <div class="lg:col-span-7 space-y-3">
            <div class="neo-box p-4 bg-white flex items-start gap-4">
              <span class="neo-stamp neo-stamp-navy text-xs font-mono font-bold shrink-0 mt-0.5">01</span>
              <div>
                <h4 class="font-extrabold text-[#0B132B] text-sm font-heading">Official government order references</h4>
                <p class="text-xs text-slate-600 mt-0.5 font-medium">
                  Every rule shows the official government order number it comes from.
                </p>
              </div>
            </div>

            <div class="neo-box p-4 bg-white flex items-start gap-4">
              <span class="neo-stamp neo-stamp-navy text-xs font-mono font-bold shrink-0 mt-0.5">02</span>
              <div>
                <h4 class="font-extrabold text-[#0B132B] text-sm font-heading">Fixed rules, no guesswork</h4>
                <p class="text-xs text-slate-600 mt-0.5 font-medium">
                  No AI decides whether you get money. Simple checks confirm income limits, age limits and caste quotas.
                </p>
              </div>
            </div>

            <div class="neo-box p-4 bg-white flex items-start gap-4">
              <span class="neo-stamp neo-stamp-navy text-xs font-mono font-bold shrink-0 mt-0.5">03</span>
              <div>
                <h4 class="font-extrabold text-[#0B132B] text-sm font-heading">Document check before you apply</h4>
                <p class="text-xs text-slate-600 mt-0.5 font-medium">
                  We check that your certificates are in the right format and still valid before you submit on MahaDBT.
                </p>
              </div>
            </div>

            <div class="neo-box p-4 bg-white flex items-start gap-4">
              <span class="neo-stamp neo-stamp-navy text-xs font-mono font-bold shrink-0 mt-0.5">04</span>
              <div>
                <h4 class="font-extrabold text-[#0B132B] text-sm font-heading">Maharashtra Right to Services (RTS) Act 2015 deadlines</h4>
                <p class="text-xs text-slate-600 mt-0.5 font-medium">
                  See how many days each certificate usually takes: Tahsildar income, residence (domicile), and non-creamy layer. Appeal steps included.
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
            <span>See all schemes</span>
            <ArrowRight class="w-3.5 h-3.5" />
          </router-link>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="neo-box p-5 bg-[#FBFBFA] space-y-3">
            <span class="neo-stamp neo-stamp-navy text-[10px]">Higher education</span>
            <h3 class="font-extrabold text-[#0B132B] text-base font-heading">Higher Education</h3>
            <p class="text-xs text-slate-600 font-medium leading-relaxed">
              Rajarshi Shahu Maharaj tuition fee concession for Economically Backward Class (EBC) students, and Dr. Panjabrao Deshmukh hostel allowance for engineering, medical and polytechnic.
            </p>
          </div>

          <div class="neo-box p-5 bg-[#FBFBFA] space-y-3">
            <span class="neo-stamp neo-stamp-emerald text-[10px]">Social Justice</span>
            <h3 class="font-extrabold text-[#0B132B] text-base font-heading">Social Welfare & Tribal</h3>
            <p class="text-xs text-slate-600 font-medium leading-relaxed">
              Scholarships after Class 10 for SC, ST, VJNT and OBC students, fee waivers, Dr. Ambedkar Swadhar Scheme and Pandit Deendayal hostels.
            </p>
          </div>

          <div class="neo-box p-5 bg-[#FBFBFA] space-y-3">
            <span class="neo-stamp neo-stamp-amber text-[10px]">Revenue department</span>
            <h3 class="font-extrabold text-[#0B132B] text-base font-heading">Aaple Sarkar Certificates</h3>
            <p class="text-xs text-slate-600 font-medium leading-relaxed">
              Tahsildar income certificate, state residence (domicile) certificate, non-creamy layer (NCL) certificate, caste validity, and RTS deadline tracking.
            </p>
          </div>

          <div class="neo-box p-5 bg-[#FBFBFA] space-y-3">
            <span class="neo-stamp text-[10px] bg-purple-100 text-purple-900 border-[1.5px] border-[#0B132B]">Money sent to bank</span>
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
              Works in villages too
            </div>
            <h2 class="text-2xl sm:text-4xl font-extrabold text-[#0B132B] tracking-tight font-heading leading-tight">
              Slow network?
              <span class="block text-slate-800">YojnaVia keeps working.</span>
            </h2>
            <p class="text-sm text-slate-700 leading-relaxed font-medium">
              Made for remote villages, busy cyber cafes and weak mobile signal. It uses little data and prints handover slips for college clerks.
            </p>
          </div>

          <div class="lg:col-span-6">
            <div class="neo-box p-6 bg-white space-y-3">
              <div class="p-3 rounded-xl border-[1.5px] border-[#0B132B] bg-[#FBFBFA] flex items-center justify-between text-xs font-bold">
                <span class="flex items-center gap-2">
                  <FileText class="w-4 h-4 text-amber-600" />
                  <span>Printable checklist (PDF, works offline)</span>
                </span>
                <span class="neo-stamp neo-stamp-emerald text-[9px]">Ready to print</span>
              </div>

              <div class="p-3 rounded-xl border-[1.5px] border-[#0B132B] bg-[#FBFBFA] flex items-center justify-between text-xs font-bold">
                <span class="flex items-center gap-2">
                  <Smartphone class="w-4 h-4 text-emerald-600" />
                  <span>Safe on shared phones (no passwords saved)</span>
                </span>
                <span class="neo-stamp text-[9px] bg-slate-100">No personal data saved</span>
              </div>

              <div class="p-3 rounded-xl border-[1.5px] border-[#0B132B] bg-[#FBFBFA] flex items-center justify-between text-xs font-bold">
                <span class="flex items-center gap-2">
                  <Clock class="w-4 h-4 text-indigo-600" />
                  <span>Printed slips for your college scholarship clerk</span>
                </span>
                <span class="neo-stamp neo-stamp-navy text-[9px]">Required step</span>
              </div>

              <div class="p-3 bg-[#FEF3C7] rounded-xl border-[1.5px] border-[#0B132B] text-xs text-amber-950 font-bold flex items-center gap-2">
                <CheckCircle2 class="w-4 h-4 text-amber-700 shrink-0" />
                <span>Document checklists you can take to the revenue office, even offline.</span>
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
              Document check before you apply
            </span>
            <h2 class="text-2xl sm:text-4xl font-extrabold text-white tracking-tight font-heading leading-tight">
              Stop losing scholarships to paperwork mistakes.
            </h2>
            <p class="text-sm text-slate-300 leading-relaxed font-medium">
              Over 38% of MahaDBT applications are queried or rejected because of small certificate mistakes or missing seals. YojnaVia finds these before you submit.
            </p>

            <div class="space-y-2.5 text-xs text-slate-200 font-medium">
              <div class="flex items-center gap-2">
                <span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
                <span>15 days to fix and resubmit, with countdown reminders.</span>
              </div>
              <div class="flex items-center gap-2">
                <span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
                <span>Step-by-step help to appeal if an approval is delayed under the RTS Act.</span>
              </div>
            </div>

            <div class="pt-2">
              <button
                @click="startDiscovery()"
                class="neo-btn bg-[#F59E0B] hover:bg-[#D97706] text-[#0B132B] px-6 py-3 text-xs font-black shadow-[2.5px_2.5px_0_0_#FFFFFF] cursor-pointer"
              >
                <span>Run a free document check</span>
                <ArrowRight class="w-4 h-4" />
              </button>
            </div>
          </div>

          <!-- Right Breakdown Bar Mockup -->
          <div class="lg:col-span-6">
            <div class="bg-white text-[#0B132B] rounded-2xl border-[1.5px] border-[#0B132B] p-6 shadow-[4px_4px_0_0_#F59E0B] space-y-4">
              <div class="flex items-center justify-between pb-2 border-b-[1.5px] border-[#0B132B]/15">
                <span class="font-extrabold text-sm font-heading">Application document checklist</span>
                <span class="neo-stamp neo-stamp-emerald text-[9px]">92% Ready</span>
              </div>

              <div class="space-y-3 text-xs">
                <div>
                  <div class="flex items-center justify-between font-bold mb-1">
                    <span>Maharashtra residence (domicile) certificate (Aaple Sarkar)</span>
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
                    <span>Non-creamy layer certificate validity</span>
                    <span class="text-amber-700 font-mono">Expires March 31</span>
                  </div>
                  <div class="w-full h-2 rounded-full bg-slate-100 overflow-hidden border border-[#0B132B]/20">
                    <div class="h-full bg-amber-500 rounded-full w-3/4"></div>
                  </div>
                </div>
              </div>

              <div class="p-3 bg-[#FFFBEB] rounded-xl border-[1.5px] border-[#0B132B] text-xs text-amber-950 font-bold leading-relaxed">
                Tip: Submit your updated income certificate before the portal closes, so the college clerk has no questions.
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
            Clear rules. No hidden fine print.
          </h2>
          <p class="text-xs sm:text-sm text-slate-600 mt-2 font-medium">
            Built to protect students and families from fake agents, fake websites and illegal fee demands.
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
              Use it on a friend's phone or at a cyber cafe. We save no login details.
            </p>
          </div>

          <div class="neo-box p-6 bg-[#FBFBFA] space-y-3">
            <div class="w-10 h-10 rounded-xl bg-white border-[1.5px] border-[#0B132B] flex items-center justify-center text-slate-800 shadow-[1.5px_1.5px_0_0_#0B132B]">
              <Scale class="w-5 h-5 text-indigo-600" />
            </div>
            <h3 class="font-extrabold text-[#0B132B] text-base font-heading">Verifiable Citations</h3>
            <p class="text-xs text-slate-600 font-medium leading-relaxed">
              Every rule is linked to an official Maharashtra government order.
            </p>
          </div>

          <div class="neo-box p-6 bg-[#FBFBFA] space-y-3">
            <div class="w-10 h-10 rounded-xl bg-white border-[1.5px] border-[#0B132B] flex items-center justify-center text-slate-800 shadow-[1.5px_1.5px_0_0_#0B132B]">
              <Languages class="w-5 h-5 text-rose-600" />
            </div>
            <h3 class="font-extrabold text-[#0B132B] text-base font-heading">Easy to Read</h3>
            <p class="text-xs text-slate-600 font-medium leading-relaxed">
              Official government notices explained in simple Marathi, Hindi and English.
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
              Run an approved help desk for students and families.
            </h2>
            <p class="text-xs sm:text-sm text-slate-700 leading-relaxed font-medium">
              Village computer operators, student counsellors and NGOs can register people with their permission, check documents and track cases. Each centre's data stays private.
            </p>
          </div>

          <div class="shrink-0 flex flex-col sm:flex-row items-center gap-3 w-full lg:w-auto">
            <router-link
              to="/counselor"
              class="neo-btn neo-btn-navy w-full sm:w-auto px-6 py-3 text-xs sm:text-sm font-bold"
            >
              <span>Open help desk</span>
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
            Find the government help you are owed today.
          </h2>
          <p class="text-xs sm:text-sm text-amber-950 font-bold mt-1">
            Free • Takes 3 minutes • Based on official Maharashtra government rules
          </p>
        </div>

        <button
          @click="startDiscovery()"
          class="neo-btn bg-white hover:bg-slate-50 text-[#0B132B] px-8 py-3.5 text-sm font-extrabold shadow-[2.5px_2.5px_0_0_#0B132B] shrink-0 cursor-pointer"
        >
          <span>Find schemes for me</span>
          <ArrowRight class="w-4 h-4" />
        </button>
      </div>
    </section>

  </div>
</template>
