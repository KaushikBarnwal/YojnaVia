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
      <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-200 text-indigo-700 text-xs font-bold uppercase tracking-wider mb-2">
        <UserCheck class="w-3.5 h-3.5 text-indigo-600" />
        Step 2 of 5: Human-In-The-Loop Verification
      </div>
      <h1 class="text-2xl sm:text-3xl font-extrabold text-slate-900">
        Review & Confirm Student Profile Attributes
      </h1>
      <p class="text-sm text-slate-600 mt-1">
        Prevent costly mistakes: Tap or edit any variable before running the deterministic eligibility evaluator.
      </p>
    </div>

    <!-- Edit Form Card -->
    <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 sm:p-8">
      <form @submit.prevent="saveAndEvaluate" class="space-y-6">
        
        <!-- Section 1: Demographics -->
        <div>
          <h2 class="text-sm font-bold uppercase tracking-wider text-slate-500 mb-4 pb-2 border-b border-slate-100 flex items-center gap-2">
            1. Demographics & Maharashtra Domicile
          </h2>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Student Name / Tag</label>
              <input v-model="form.name" type="text" class="w-full text-sm px-3.5 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-indigo-500" />
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Age</label>
              <input v-model.number="form.age" type="number" class="w-full text-sm px-3.5 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-indigo-500" />
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Gender</label>
              <select v-model="form.gender" class="w-full text-sm px-3.5 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-indigo-500 bg-white">
                <option value="MALE">Male</option>
                <option value="FEMALE">Female</option>
                <option value="OTHER">Other</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">District (Maharashtra)</label>
              <input v-model="form.district" type="text" class="w-full text-sm px-3.5 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-indigo-500" />
            </div>

            <div class="sm:col-span-2 flex items-center pt-5">
              <label class="flex items-center gap-2 cursor-pointer text-sm font-semibold text-slate-800">
                <input v-model="form.is_maharashtra_domicile" type="checkbox" class="w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500" />
                Holds Maharashtra State Domicile Certificate (Eligible for State Scholarships)
              </label>
            </div>
          </div>
        </div>

        <!-- Section 2: Social Category & Economic Status -->
        <div>
          <h2 class="text-sm font-bold uppercase tracking-wider text-slate-500 mb-4 pb-2 border-b border-slate-100 flex items-center gap-2">
            2. Social Category & Family Income
          </h2>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Caste / Social Category</label>
              <select v-model="form.caste_category" class="w-full text-sm px-3.5 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-indigo-500 bg-white">
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
              <label class="block text-xs font-semibold text-slate-700 mb-1">Caste Name (Optional)</label>
              <input v-model="form.caste_name" type="text" placeholder="e.g. Kunbi, Maratha, Mahar" class="w-full text-sm px-3.5 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-indigo-500" />
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">
                Annual Family Income (₹)
                <span class="text-slate-400 font-normal">Per Tahsildar Certificate</span>
              </label>
              <input v-model.number="form.annual_family_income" type="number" step="1000" class="w-full text-sm px-3.5 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-indigo-500 font-mono font-bold text-emerald-800" />
            </div>
          </div>
        </div>

        <!-- Section 3: Course & Admission Quota -->
        <div>
          <h2 class="text-sm font-bold uppercase tracking-wider text-slate-500 mb-4 pb-2 border-b border-slate-100 flex items-center gap-2">
            3. Education & Centralized Admission
          </h2>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Course Level</label>
              <select v-model="form.current_course_level" class="w-full text-sm px-3.5 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-indigo-500 bg-white">
                <option value="11TH_12TH">11th / 12th / Junior College</option>
                <option value="DIPLOMA">Polytechnic / Diploma</option>
                <option value="UNDERGRADUATE">Undergraduate (BA / B.Sc / B.Com)</option>
                <option value="PROFESSIONAL_DEGREE">Professional Degree (Engineering / Pharmacy / Medical)</option>
                <option value="POSTGRADUATE">Postgraduate Degree</option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Course Name</label>
              <input v-model="form.course_name" type="text" class="w-full text-sm px-3.5 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-indigo-500" />
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Admission Quota Type</label>
              <select v-model="form.admission_quota" class="w-full text-sm px-3.5 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-indigo-500 bg-white">
                <option value="CAP_ROUND">Centralized Admission Process (CAP Merit Round)</option>
                <option value="DIRECT_SECOND_YEAR">Direct Second Year (DSE via CAP)</option>
                <option value="INSTITUTE_QUOTA">Institute / Management Quota</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Section 4: Accommodation & Background -->
        <div>
          <h2 class="text-sm font-bold uppercase tracking-wider text-slate-500 mb-4 pb-2 border-b border-slate-100 flex items-center gap-2">
            4. Living Accommodation & Farmer Landholding (Hostel Allowance)
          </h2>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-700 mb-1">Accommodation Type</label>
              <select v-model="form.accommodation_type" class="w-full text-sm px-3.5 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-indigo-500 bg-white">
                <option value="PRIVATE_RENTAL_PG">Private Rented Room / PG / Non-Govt Hostel</option>
                <option value="DAY_SCHOLAR">Day Scholar (Living at home with parents)</option>
                <option value="GOVT_HOSTEL">Government / University Hostel</option>
              </select>
            </div>

            <div class="flex items-center pt-5">
              <label class="flex items-center gap-2 cursor-pointer text-sm font-semibold text-slate-800">
                <input v-model="form.parent_is_farmer" type="checkbox" class="w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500" />
                Parents are Registered Farmers (Holds 7/12 land extract)
              </label>
            </div>

            <div v-if="form.parent_is_farmer">
              <label class="block text-xs font-semibold text-slate-700 mb-1">Agricultural Land Holding (Acres)</label>
              <input v-model.number="form.parent_land_acres" type="number" step="0.1" class="w-full text-sm px-3.5 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-indigo-500" />
            </div>
          </div>
        </div>

        <!-- Save & Submit Button -->
        <div class="pt-6 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div class="flex items-center gap-2 text-xs text-slate-500">
            <CheckCircle2 class="w-4 h-4 text-emerald-600" />
            Clicking confirm will run the pure Python deterministic rule engine.
          </div>

          <button
            type="submit"
            class="w-full sm:w-auto px-8 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl shadow-md shadow-indigo-100 flex items-center justify-center gap-2 transition-all"
          >
            <Save class="w-4 h-4" />
            <span>Confirm Profile & Evaluate Schemes</span>
            <ArrowRight class="w-4 h-4" />
          </button>
        </div>

      </form>
    </div>
  </div>
</template>
