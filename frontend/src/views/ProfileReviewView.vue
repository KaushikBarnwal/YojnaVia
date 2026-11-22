<script setup lang="ts">
import { ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useStudentStore } from '../stores/studentStore';
import PersonaBar from '../components/PersonaBar.vue';
import { 
  UserCheck, 
  ArrowRight, 
  Save, 
  CheckCircle2
} from '@lucide/vue';

const store = useStudentStore();
const router = useRouter();

// Editable form state copy synchronized with store profile
const form = ref({
  name: store.profile?.name || 'Student',
  age: store.profile?.age || 20,
  gender: store.profile?.gender || 'MALE',
  district: store.profile?.district || 'Pune',
  is_maharashtra_domicile: store.profile?.is_maharashtra_domicile ?? true,
  caste_category: store.profile?.caste_category || 'OBC',
  caste_name: store.profile?.caste_name || '',
  annual_family_income: store.profile?.annual_family_income || 110000,
  current_course_level: store.profile?.current_course_level || 'PROFESSIONAL_DEGREE',
  course_name: store.profile?.course_name || 'B.Tech Engineering',
  admission_quota: store.profile?.admission_quota || 'CAP_ROUND',
  previous_year_percentage: store.profile?.previous_year_percentage || 75.0,
  accommodation_type: store.profile?.accommodation_type || 'PRIVATE_RENTAL_PG',
  parent_is_farmer: store.profile?.parent_is_farmer ?? false,
  parent_land_acres: store.profile?.parent_land_acres || 0,
});

watch(
  () => store.profile,
  (newProfile) => {
    if (newProfile) {
      form.value = {
        name: newProfile.name || 'Student',
        age: newProfile.age || 20,
        gender: newProfile.gender || 'MALE',
        district: newProfile.district || 'Pune',
        is_maharashtra_domicile: newProfile.is_maharashtra_domicile ?? true,
        caste_category: newProfile.caste_category || 'OBC',
        caste_name: newProfile.caste_name || '',
        annual_family_income: newProfile.annual_family_income || 110000,
        current_course_level: newProfile.current_course_level || 'PROFESSIONAL_DEGREE',
        course_name: newProfile.course_name || 'B.Tech Engineering',
        admission_quota: newProfile.admission_quota || 'CAP_ROUND',
        previous_year_percentage: newProfile.previous_year_percentage || 75.0,
        accommodation_type: newProfile.accommodation_type || 'PRIVATE_RENTAL_PG',
        parent_is_farmer: newProfile.parent_is_farmer ?? false,
        parent_land_acres: newProfile.parent_land_acres || 0,
      };
    }
  },
  { immediate: true }
);

async function saveAndEvaluate() {
  await store.updateProfile(form.value);
  router.push('/schemes');
}
</script>

<template>
  <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <PersonaBar />

    <!-- Page Title -->
    <div class="mb-6">
      <div class="inline-flex items-center gap-2 mb-1.5">
        <span class="neo-stamp neo-stamp-navy text-[10px]">
          <UserCheck class="w-3 h-3 text-amber-400" />
          Check your details
        </span>
        <span class="text-xs text-slate-500 font-mono">Stage 2 of 5</span>
      </div>
      <h1 class="text-2xl sm:text-3xl font-extrabold text-[#0B132B] tracking-tight font-heading">
        Review and confirm your details
      </h1>
      <p class="text-xs sm:text-sm text-slate-600 mt-1 font-medium">
        Check these carefully. Change anything that is wrong before we check your eligibility.
      </p>
    </div>

    <!-- Edit Form Card -->
    <div class="neo-box bg-white p-6 sm:p-8 shadow-[3px_3px_0_0_#0B132B]">
      <form @submit.prevent="saveAndEvaluate" class="space-y-6">
        
        <!-- Section 1: Demographics -->
        <div>
          <h2 class="text-xs font-extrabold uppercase tracking-widest text-[#0B132B] mb-4 pb-2 border-b-[1.5px] border-[#0B132B]/15 flex items-center gap-2 font-heading">
            1. About you and Maharashtra residence (domicile)
          </h2>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label class="block text-xs font-bold text-[#0B132B] mb-1">Your name</label>
              <input v-model="form.name" type="text" class="neo-input w-full text-xs sm:text-sm px-3.5 py-2.5" />
            </div>

            <div>
              <label class="block text-xs font-bold text-[#0B132B] mb-1">Age</label>
              <input v-model.number="form.age" type="number" class="neo-input w-full text-xs sm:text-sm px-3.5 py-2.5 font-mono" />
            </div>

            <div>
              <label class="block text-xs font-bold text-[#0B132B] mb-1">Gender</label>
              <select v-model="form.gender" class="neo-input w-full text-xs sm:text-sm px-3.5 py-2.5 bg-white font-medium">
                <option value="MALE">Male</option>
                <option value="FEMALE">Female</option>
                <option value="OTHER">Other</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-bold text-[#0B132B] mb-1">District in Maharashtra</label>
              <input v-model="form.district" type="text" class="neo-input w-full text-xs sm:text-sm px-3.5 py-2.5" />
            </div>

            <div class="sm:col-span-2 flex items-center pt-5">
              <label class="flex items-center gap-2.5 cursor-pointer text-xs sm:text-sm font-bold text-[#0B132B]">
                <input v-model="form.is_maharashtra_domicile" type="checkbox" class="w-4 h-4 rounded border-[#0B132B] text-amber-600 focus:ring-amber-500" />
                <span>I have a Maharashtra residence (domicile) certificate (needed for state scholarships)</span>
              </label>
            </div>
          </div>
        </div>

        <!-- Section 2: Social Category & Economic Status -->
        <div>
          <h2 class="text-xs font-extrabold uppercase tracking-widest text-[#0B132B] mb-4 pb-2 border-b-[1.5px] border-[#0B132B]/15 flex items-center gap-2 font-heading">
            2. Social Category & Family Income
          </h2>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label class="block text-xs font-bold text-[#0B132B] mb-1">Caste category</label>
              <select v-model="form.caste_category" class="neo-input w-full text-xs sm:text-sm px-3.5 py-2.5 bg-white font-bold">
                <option value="OPEN">Open / General</option>
                <option value="OBC">Other Backward Class (OBC)</option>
                <option value="SC">Scheduled Caste (SC) / Navboudha</option>
                <option value="ST">Scheduled Tribe (ST)</option>
                <option value="VJNT">Vimukta Jati & Nomadic Tribes (VJNT)</option>
                <option value="SBC">Special Backward Class (SBC)</option>
                <option value="EWS">Economically Weaker Section (EWS)</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-bold text-[#0B132B] mb-1">Caste name (optional)</label>
              <input v-model="form.caste_name" type="text" placeholder="e.g. Kunbi, Maratha, Mahar" class="neo-input w-full text-xs sm:text-sm px-3.5 py-2.5" />
            </div>

            <div>
              <label class="block text-xs font-bold text-[#0B132B] mb-1">
                Yearly family income (₹)
                <span class="text-slate-500 font-normal">As shown on your Tahsildar certificate</span>
              </label>
              <input v-model.number="form.annual_family_income" type="number" step="1000" class="neo-input w-full text-xs sm:text-sm px-3.5 py-2.5 font-mono font-bold text-emerald-900" />
            </div>
          </div>
        </div>

        <!-- Section 3: Course & Admission Quota -->
        <div>
          <h2 class="text-xs font-extrabold uppercase tracking-widest text-[#0B132B] mb-4 pb-2 border-b-[1.5px] border-[#0B132B]/15 flex items-center gap-2 font-heading">
            3. Your course and admission
          </h2>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label class="block text-xs font-bold text-[#0B132B] mb-1">Course level</label>
              <select v-model="form.current_course_level" class="neo-input w-full text-xs sm:text-sm px-3.5 py-2.5 bg-white font-medium">
                <option value="11TH_12TH">11th / 12th / Junior College</option>
                <option value="DIPLOMA">Polytechnic / Diploma</option>
                <option value="UNDERGRADUATE">Undergraduate (BA / B.Sc / B.Com)</option>
                <option value="PROFESSIONAL_DEGREE">Professional Degree (Engineering / Pharmacy / Medical)</option>
                <option value="POSTGRADUATE">Postgraduate Degree</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-bold text-[#0B132B] mb-1">Course name</label>
              <input v-model="form.course_name" type="text" class="neo-input w-full text-xs sm:text-sm px-3.5 py-2.5" />
            </div>

            <div>
              <label class="block text-xs font-bold text-[#0B132B] mb-1">Type of admission</label>
              <select v-model="form.admission_quota" class="neo-input w-full text-xs sm:text-sm px-3.5 py-2.5 bg-white font-medium">
                <option value="CAP_ROUND">Centralised admission (CAP merit round)</option>
                <option value="DIRECT_SECOND_YEAR">Direct second year (through CAP)</option>
                <option value="INSTITUTE_QUOTA">College / management quota</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Section 4: Accommodation & Background -->
        <div>
          <h2 class="text-xs font-extrabold uppercase tracking-widest text-[#0B132B] mb-4 pb-2 border-b-[1.5px] border-[#0B132B]/15 flex items-center gap-2 font-heading">
            4. Where you live and family farm land (for hostel allowance)
          </h2>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label class="block text-xs font-bold text-[#0B132B] mb-1">Where you live</label>
              <select v-model="form.accommodation_type" class="neo-input w-full text-xs sm:text-sm px-3.5 py-2.5 bg-white font-medium">
                <option value="PRIVATE_RENTAL_PG">Private Rented Room / PG / Non-Govt Hostel</option>
                <option value="DAY_SCHOLAR">Day Scholar (Living at home with parents)</option>
                <option value="GOVT_HOSTEL">Government / University Hostel</option>
              </select>
            </div>

            <div class="flex items-center pt-5">
              <label class="flex items-center gap-2.5 cursor-pointer text-xs sm:text-sm font-bold text-[#0B132B]">
                <input v-model="form.parent_is_farmer" type="checkbox" class="w-4 h-4 rounded border-[#0B132B] text-amber-600 focus:ring-amber-500" />
                <span>My parents are registered farmers (they hold a 7/12 land record)</span>
              </label>
            </div>

            <div v-if="form.parent_is_farmer">
              <label class="block text-xs font-bold text-[#0B132B] mb-1">Farm land owned (acres)</label>
              <input v-model.number="form.parent_land_acres" type="number" step="0.1" class="neo-input w-full text-xs sm:text-sm px-3.5 py-2.5 font-mono" />
            </div>
          </div>
        </div>

        <!-- Save & Submit Button -->
        <div class="pt-6 border-t-[1.5px] border-[#0B132B]/15 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div class="flex items-center gap-2 text-xs text-slate-600 font-medium">
            <CheckCircle2 class="w-4 h-4 text-emerald-700" />
            When you confirm, we check which schemes you qualify for.
          </div>

          <button
            type="submit"
            class="neo-btn neo-btn-saffron w-full sm:w-auto px-8 py-3 text-sm font-bold"
          >
            <Save class="w-4 h-4" />
            <span>Confirm and check schemes</span>
            <ArrowRight class="w-4 h-4" />
          </button>
        </div>

      </form>
    </div>
  </div>
</template>
