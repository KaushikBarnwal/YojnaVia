<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useStudentStore } from '../stores/studentStore';
import api from '../services/api';
import { 
  Bell, 
  MessageSquare, 
  Phone, 
  ShieldCheck, 
  CheckCircle2, 
  AlertTriangle, 
  Clock, 
  Send, 
  RefreshCw, 
  Sliders, 
  AlertCircle,
  Sparkles
} from '@lucide/vue';

const store = useStudentStore();

// Notification preferences state
const isLoading = ref(true);
const isSaving = ref(false);
const saveSuccess = ref(false);
const errorMessage = ref('');

interface Preferences {
  mobile_number: string;
  is_mobile_verified: boolean;
  whatsapp_enabled: boolean;
  whatsapp_opt_in_at: string | null;
  whatsapp_opt_out_at: string | null;
  sms_enabled: boolean;
  sms_opt_in_at: string | null;
  sms_opt_out_at: string | null;
  in_app_enabled: boolean;
  preferred_language: 'en' | 'mr' | 'hi';
  notify_deadlines: boolean;
  notify_missing_docs: boolean;
  notify_milestones: boolean;
  notify_inactivity: boolean;
  notify_grievances: boolean;
  notify_renewals: boolean;
  created_at?: string;
  updated_at?: string;
}

const prefs = ref<Preferences>({
  mobile_number: '',
  is_mobile_verified: false,
  whatsapp_enabled: false,
  whatsapp_opt_in_at: null,
  whatsapp_opt_out_at: null,
  sms_enabled: false,
  sms_opt_in_at: null,
  sms_opt_out_at: null,
  in_app_enabled: true,
  preferred_language: 'en',
  notify_deadlines: true,
  notify_missing_docs: true,
  notify_milestones: true,
  notify_inactivity: true,
  notify_grievances: true,
  notify_renewals: true,
});

const channelsAvailable = ref({
  whatsapp: { is_configured: false, provider_mode: 'SIMULATED' },
  sms: { is_configured: false, provider_mode: 'SIMULATED', dlt_entity_id: '110155234000001' },
  in_app: { is_configured: true, provider_mode: 'LIVE' },
});

// Mobile verification modal / state
const isVerifyModalOpen = ref(false);
const inputPhone = ref('');
const inputOtp = ref('');
const otpSent = ref(false);
const demoOtpCode = ref('');
const verifyError = ref('');
const isVerifying = ref(false);

// Delivery history state
interface NotificationLogItem {
  id: string;
  event_type: string;
  channel: string;
  idempotency_key: string;
  recipient: string;
  language: string;
  template_name: string;
  title: string;
  message_body: string;
  provider: string;
  provider_message_id: string;
  delivery_status: string;
  error_message: string;
  retry_count: number;
  sent_at: string | null;
  delivered_at: string | null;
  created_at: string;
  scheme_name?: string;
}

const historyLogs = ref<NotificationLogItem[]>([]);
const historyFilterChannel = ref('ALL');
const historyFilterStatus = ref('ALL');
const isHistoryLoading = ref(false);
const expandedLogId = ref<string | null>(null);

// Test Drive state
const testChannel = ref<'WHATSAPP' | 'SMS' | 'IN_APP'>('WHATSAPP');
const isTesting = ref(false);
const testResult = ref<any>(null);

// Admin Telemetry toggle
const showAdminTelemetry = ref(false);
const telemetryData = ref<any>(null);

// 6 Canonical Events definitions for interactive preview
const canonicalEvents = computed(() => [
  {
    key: 'DEADLINE_APPROACHING',
    field: 'notify_deadlines' as keyof Preferences,
    title: {
      en: 'Application deadline is near',
      mr: 'अर्ज अंतिम मुदत सूचना',
      hi: 'आवेदन अंतिम तिथि अलर्ट'
    },
    trigger: 'Sent 7 days, 2 days, and on the deadline day.',
    preview: {
      en: `Namaste ${store.profile?.name || 'Citizen'}, this is an important reminder from YojnaVia. The deadline to apply for 'Post Matric Scholarship' on MahaDBT is 31 December 2026 (2 days left). Please submit all required documents before the portal closes.`,
      mr: `नमस्ते ${store.profile?.name || 'विद्यार्थी'}, योजनाव्हायाकडून महत्त्वाची सूचना. 'पोस्ट मॅट्रिक शिष्यवृत्ती' या योजनेसाठी MahaDBT संकेतस्थळावर अर्ज करण्याची अंतिम मुदत 31 डिसेंबर 2026 आहे (फक्त 2 दिवस शिल्लक). कृपया मुदतीपूर्वी आपले कागदपत्र सादर करा.`,
      hi: `नमस्ते ${store.profile?.name || 'नागरिक'}, योजनावाया की ओर से महत्वपूर्ण सूचना। 'पोस्ट मैट्रिक छात्रवृत्ति' के लिए MahaDBT पोर्टल पर आवेदन की अंतिम तिथि 31 दिसंबर 2026 है (केवल 2 दिन शेष)। कृपया पोर्टल बंद होने से पहले अपने दस्तावेज़ जमा करें।`
    }
  },
  {
    key: 'MISSING_DOCUMENT_REMINDER',
    field: 'notify_missing_docs' as keyof Preferences,
    title: {
      en: 'Reminder: a required document is missing',
      mr: 'प्रलंबित कागदपत्र स्मरणपत्र',
      hi: 'लंबित आवश्यक दस्तावेज़ अनुस्मारक'
    },
    trigger: 'Weekly reminder until you get the required documents (Tahsildar income, caste validity).',
    preview: {
      en: `Namaste ${store.profile?.name || 'Citizen'}, your application for 'Rajarshi Shahu Maharaj Tuition Scheme' is waiting for: 'Tahsildar Income Certificate'. You can apply online on the Aaple Sarkar website (usually takes 15 days). Once you have it, your application can move forward.`,
      mr: `नमस्ते ${store.profile?.name || 'विद्यार्थी'}, आपल्या 'राजर्षी शाहू महाराज शिक्षण शुल्क योजना' अर्जासाठी 'तहसीलदार उत्पन्न दाखला' अद्याप प्रलंबित आहे. आपण 'आपले सरकार' पोर्टलवरून १५ दिवसांच्या विहित मुदतीत अर्ज करू शकता.`,
      hi: `नमस्ते ${store.profile?.name || 'नागरिक'}, आपके 'राजर्षि शाहू महाराज शिक्षण शुल्क योजना' आवेदन के लिए 'तहसीलदार आय प्रमाण पत्र' अभी लंबित है। आप 'आपले सरकार' पोर्टल के माध्यम से 15-दिवसीय विधिक समय-सीमा में आवेदन कर सकते हैं।`
    }
  },
  {
    key: 'MILESTONE_UPDATED',
    field: 'notify_milestones' as keyof Preferences,
    title: {
      en: 'Your application moved to a new step',
      mr: 'अर्ज टप्पा बदल सूचना',
      hi: 'आवेदन चरण अद्यतन सूचना'
    },
    trigger: 'Sent each time your application moves to a new step (for example: documents ready, applied, approved).',
    preview: {
      en: `Namaste ${store.profile?.name || 'Citizen'}, your application for 'Post Matric Scholarship' has moved to: Applied / College check. Next step: give a printed receipt and attested document copies to your college scholarship clerk.`,
      mr: `नमस्ते ${store.profile?.name || 'विद्यार्थी'}, आपल्या 'पोस्ट मॅट्रिक शिष्यवृत्ती' अर्जाचा टप्पा पुढे सरकला आहे: अर्ज सादर केला / महाविद्यालयीन पडताळणी. पुढील कृती: महाविद्यालयातील शिष्यवृत्ती लिपिकाकडे स्वाक्षरी प्रत व कागदपत्रे जमा करा.`,
      hi: `नमस्ते ${store.profile?.name || 'नागरिक'}, आपके 'पोस्ट मैट्रिक छात्रवृत्ति' आवेदन की स्थिति आगे बढ़ी है: आवेदन जमा / कॉलेज स्तर पर जांच। अगला कदम: कॉलेज छात्रवृत्ति लिपिक के पास हस्ताक्षरित प्रति व दस्तावेज जमा करें।`
    }
  },
  {
    key: 'STATUS_INACTIVITY',
    field: 'notify_inactivity' as keyof Preferences,
    title: {
      en: 'No status change for 14 days',
      mr: '१४ दिवसांची अक्रियाशीलता सूचना',
      hi: '14 दिनों से कोई स्थिति परिवर्तन नहीं'
    },
    trigger: 'Sent when your application status has not changed for 14 days, so you can follow up.',
    preview: {
      en: `Namaste ${store.profile?.name || 'Citizen'}, your application for 'EBC Fee Concession' has been 'Under Review' for over 14 days. Please check with your college scholarship clerk, or log in to the portal to see any questions.`,
      mr: `नमस्ते ${store.profile?.name || 'विद्यार्थी'}, आपल्या 'ईबीसी शुल्क सवलत' अर्जाची स्थिती 'तपासणी सुरू' अशी १४ दिवसांपासून कायम आहे. कृपया महाविद्यालयातील लिपिकाकडे चौकशी करा अथवा पोर्टलवर लॉगिन करून पडताळणी शेरा तपासा.`,
      hi: `नमस्ते ${store.profile?.name || 'नागरिक'}, आपके 'ईबीसी शुल्क छूट' आवेदन की स्थिति 'समीक्षाधीन' पिछले 14 दिनों से अपरिवर्तित है। कृपया अपने कॉलेज लिपिक से संपर्क करें या पोर्टल पर लॉगिन करके जांच टिप्पणी देखें।`
    }
  },
  {
    key: 'GRIEVANCE_RESUBMISSION',
    field: 'notify_grievances' as keyof Preferences,
    title: {
      en: '15 days left to fix your application',
      mr: '१५-दिवसीय पडताळणी दुरुस्ती मुदत',
      hi: '15-दिवसीय आपत्ति सुधार समय-सीमा'
    },
    trigger: 'Countdown reminders (day 10, 5, 2 and 1) to upload corrected documents before MahaDBT rejects the application automatically.',
    preview: {
      en: `Namaste ${store.profile?.name || 'Citizen'}, an official objection was raised on your 'Post Matric Scholarship' application. You have 5 days left to upload the corrected document, by 28 November 2026. Do not let it lapse!`,
      mr: `नमस्ते ${store.profile?.name || 'विद्यार्थी'}, आपल्या 'पोस्ट मॅट्रिक शिष्यवृत्ती' अर्जावर छाननी अधिकाऱ्याने आक्षेप नोंदवला आहे. अर्ज रद्द होण्यापासून वाचवण्यासाठी दुरुस्त कागदपत्र अपलोड करण्यास फक्त ५ दिवस शिल्लक आहेत (अंतिम मुदत: 28 नोव्हेंबर 2026).`,
      hi: `नमस्ते ${store.profile?.name || 'नागरिक'}, आपके 'पोस्ट मैट्रिक छात्रवृत्ति' आवेदन पर जांच अधिकारी द्वारा आपत्ति दर्ज की गई है। आवेदन स्वतः निरस्त होने से बचाने हेतु संशोधित दस्तावेज़ अपलोड करने के लिए केवल 5 दिन शेष हैं (अंतिम तिथि: 28 नवंबर 2026)।`
    }
  },
  {
    key: 'ANNUAL_RENEWAL',
    field: 'notify_renewals' as keyof Preferences,
    title: {
      en: 'Yearly renewal: certificate expires 31 March',
      mr: 'वार्षिक नूतनीकरण व ३१ मार्च दाखला मुदत',
      hi: 'वार्षिक नवीनीकरण एवं 31 मार्च प्रमाण पत्र समाप्ति'
    },
    trigger: 'Sent in February and March, before your Tahsildar income certificate expires on 31 March.',
    preview: {
      en: `Namaste ${store.profile?.name || 'Citizen'}, your Tahsildar Income Certificate expires on 31 March. Apply now for the new 2026-27 certificate on Aaple Sarkar, so your scholarship continues without a break.`,
      mr: `नमस्ते ${store.profile?.name || 'विद्यार्थी'}, शासकीय आर्थिक वर्ष नियमांनुसार आपला तहसीलदार उत्पन्न दाखला ३१ मार्च रोजी संपत आहे. नवीन शैक्षणिक वर्ष २०२६-२७ च्या शिष्यवृत्तीसाठी आताच 'आपले सरकार' वर नवीन दाखल्यासाठी अर्ज करा.`,
      hi: `नमस्ते ${store.profile?.name || 'नागरिक'}, सरकारी वित्तीय वर्ष नियमों के अनुसार आपका तहसीलदार आय प्रमाण पत्र 31 मार्च को समाप्त हो रहा है। नए शैक्षणिक सत्र 2026-27 की छात्रवृत्ति हेतु अभी 'आपले सरकार' पर नए प्रमाण पत्र के लिए आवेदन करें।`
    }
  }
]);

// Fetch Preferences
async function fetchPreferences() {
  isLoading.value = true;
  errorMessage.value = '';
  try {
    const res = await api.get(`/notifications/preferences/?session_token=${store.sessionToken}`);
    prefs.value = { ...prefs.value, ...res.data.preferences };
    if (res.data.channels_available) {
      channelsAvailable.value = res.data.channels_available;
    }
    inputPhone.value = prefs.value.mobile_number || '';
  } catch (err: any) {
    errorMessage.value = err?.response?.data?.error || 'Something went wrong. Please try again in a few minutes.';
  } finally {
    isLoading.value = false;
  }
}

// Save Preferences
async function savePreferences() {
  isSaving.value = true;
  saveSuccess.value = false;
  errorMessage.value = '';
  try {
    const res = await api.put('/notifications/preferences/', {
      session_token: store.sessionToken,
      preferences: prefs.value
    });
    prefs.value = { ...prefs.value, ...res.data.preferences };
    saveSuccess.value = true;
    setTimeout(() => {
      saveSuccess.value = false;
    }, 3500);
  } catch (err: any) {
    errorMessage.value = err?.response?.data?.error || 'Something went wrong. Please try again in a few minutes.';
  } finally {
    isSaving.value = false;
  }
}

// Fetch History
async function fetchHistory() {
  isHistoryLoading.value = true;
  try {
    let url = `/notifications/history/?session_token=${store.sessionToken}`;
    if (historyFilterChannel.value !== 'ALL') {
      url += `&channel=${historyFilterChannel.value}`;
    }
    if (historyFilterStatus.value !== 'ALL') {
      url += `&status=${historyFilterStatus.value}`;
    }
    const res = await api.get(url);
    historyLogs.value = res.data.notifications || [];
  } catch (err) {
    console.error('Failed to load history:', err);
  } finally {
    isHistoryLoading.value = false;
  }
}

// Verify Mobile Flow
function openVerifyModal() {
  inputPhone.value = prefs.value.mobile_number || '';
  inputOtp.value = '';
  otpSent.value = false;
  demoOtpCode.value = '';
  verifyError.value = '';
  isVerifyModalOpen.value = true;
}

async function handleSendOtp() {
  if (!inputPhone.value.trim()) {
    verifyError.value = 'Please enter a valid 10-digit mobile number.';
    return;
  }
  isVerifying.value = true;
  verifyError.value = '';
  try {
    const res = await api.post('/notifications/verify_mobile/', {
      session_token: store.sessionToken,
      action: 'send_otp',
      mobile_number: inputPhone.value.trim()
    });
    otpSent.value = true;
    demoOtpCode.value = res.data.demo_code || '123456';
    prefs.value.mobile_number = res.data.mobile_number || inputPhone.value.trim();
  } catch (err: any) {
    verifyError.value = err?.response?.data?.mobile_number?.[0] || err?.response?.data?.error || 'Something went wrong. Please try again in a few minutes.';
  } finally {
    isVerifying.value = false;
  }
}

async function handleVerifyOtp() {
  if (!inputOtp.value.trim()) {
    verifyError.value = 'Please enter the 6-digit code we sent you.';
    return;
  }
  isVerifying.value = true;
  verifyError.value = '';
  try {
    const res = await api.post('/notifications/verify_mobile/', {
      session_token: store.sessionToken,
      action: 'verify_otp',
      code: inputOtp.value.trim()
    });
    prefs.value.is_mobile_verified = true;
    prefs.value.mobile_number = res.data.mobile_number || inputPhone.value.trim();
    isVerifyModalOpen.value = false;
    await savePreferences();
  } catch (err: any) {
    verifyError.value = err?.response?.data?.error || 'The code is wrong. Please check it and try again.';
  } finally {
    isVerifying.value = false;
  }
}

// Toggle Channel Consent with Instant Save
async function handleChannelToggle(channel: 'whatsapp' | 'sms' | 'in_app') {
  if (channel === 'whatsapp') {
    if (!prefs.value.is_mobile_verified && !prefs.value.whatsapp_enabled) {
      openVerifyModal();
      return;
    }
    prefs.value.whatsapp_enabled = !prefs.value.whatsapp_enabled;
  } else if (channel === 'sms') {
    if (!prefs.value.is_mobile_verified && !prefs.value.sms_enabled) {
      openVerifyModal();
      return;
    }
    prefs.value.sms_enabled = !prefs.value.sms_enabled;
  } else if (channel === 'in_app') {
    prefs.value.in_app_enabled = !prefs.value.in_app_enabled;
  }
  await savePreferences();
}

// Send Test Reminder
async function handleSendTest() {
  isTesting.value = true;
  testResult.value = null;
  try {
    const res = await api.post('/notifications/trigger_test/', {
      session_token: store.sessionToken,
      channel: testChannel.value
    });
    testResult.value = res.data;
    await fetchHistory();
  } catch (err: any) {
    testResult.value = { success: false, message: err?.response?.data?.error || 'Something went wrong. Please try again in a few minutes.' };
  } finally {
    isTesting.value = false;
  }
}

// Admin Telemetry
async function loadAdminTelemetry() {
  try {
    const res = await api.get('/notifications/admin/delivery_console/');
    telemetryData.value = res.data;
  } catch (err) {
    console.error('Failed to load telemetry:', err);
  }
}

function toggleTelemetry() {
  showAdminTelemetry.value = !showAdminTelemetry.value;
  if (showAdminTelemetry.value && !telemetryData.value) {
    loadAdminTelemetry();
  }
}

function formatDate(isoStr?: string | null) {
  if (!isoStr) return 'Not saved';
  try {
    const d = new Date(isoStr);
    return d.toLocaleString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return isoStr;
  }
}

function getStatusBadgeClass(status: string) {
  switch (status) {
    case 'DELIVERED':
    case 'READ':
      return 'bg-emerald-100 text-emerald-800 border-emerald-300';
    case 'SENT':
      return 'bg-blue-100 text-blue-800 border-blue-300';
    case 'SIMULATED':
      return 'bg-indigo-100 text-indigo-800 border-indigo-300';
    case 'OPTED_OUT':
      return 'bg-amber-100 text-amber-800 border-amber-300';
    case 'FAILED':
      return 'bg-rose-100 text-rose-800 border-rose-300';
    default:
      return 'bg-slate-100 text-slate-800 border-slate-300';
  }
}

onMounted(async () => {
  await fetchPreferences();
  await fetchHistory();
});
</script>

<template>
  <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
    
    <!-- HEADER & REGULATORY BADGES -->
    <div class="bg-[#0B132B] text-white rounded-xl p-6 sm:p-8 border-[1.5px] border-[#0B132B] shadow-[3.5px_3.5px_0_0_#D97706] relative overflow-hidden">
      <div class="relative z-10 space-y-4">
        <div class="flex flex-wrap items-center gap-2">
          <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-sm text-xs font-black bg-[#059669]/20 text-[#34D399] border border-[#059669]">
            <ShieldCheck class="w-3.5 h-3.5" />
            Only sent with your permission
          </span>
          <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-sm text-xs font-black bg-[#2563EB]/20 text-[#60A5FA] border border-[#2563EB]">
            <CheckCircle2 class="w-3.5 h-3.5" />
            Registered for SMS (DLT ID: 110155234000001)
          </span>
          <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-sm text-xs font-black bg-[#D97706]/20 text-[#FBBF24] border border-[#D97706]">
            <MessageSquare class="w-3.5 h-3.5" />
            WhatsApp Business service
          </span>
        </div>

        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 class="text-2xl sm:text-3xl font-black tracking-tight text-white flex items-center gap-2.5">
              <Bell class="w-8 h-8 text-[#F59E0B]" />
              WhatsApp & SMS <span class="bg-[#FDE047] text-[#0B132B] px-2 py-0.5 ml-1">deadline reminders</span>
            </h1>
            <p class="text-slate-300 text-sm sm:text-base max-w-3xl mt-1.5">
              Never miss a scholarship deadline, a missing document, the 15-day fix window, or the yearly 31 March certificate renewal.
            </p>
          </div>

          <!-- Quick Test Trigger & Admin Console Toggle -->
          <div class="flex items-center gap-2 shrink-0">
            <button
              @click="toggleTelemetry()"
              class="px-3.5 py-2 rounded-lg text-xs font-bold bg-[#1C2541] hover:bg-[#253256] text-white border border-white/20 transition-all flex items-center gap-1.5 cursor-pointer shadow-[1.5px_1.5px_0_0_#000]"
            >
              <Sliders class="w-3.5 h-3.5" />
              <span>Admin status</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ADMIN TELEMETRY DRAWER (IF TOGGLED) -->
    <div v-if="showAdminTelemetry" class="p-6 bg-[#0B132B] text-slate-100 rounded-xl border-[1.5px] border-[#0B132B] shadow-[2.5px_2.5px_0_0_#0B132B] space-y-4">
      <div class="flex items-center justify-between border-b border-slate-700 pb-3">
        <div class="flex items-center gap-2">
          <Sliders class="w-5 h-5 text-[#34D399]" />
          <h3 class="font-black text-sm sm:text-base text-white">Live status of reminder services</h3>
        </div>
        <button @click="showAdminTelemetry = false" class="text-xs text-slate-400 hover:text-white cursor-pointer font-bold">Close ✕</button>
      </div>

      <div v-if="telemetryData" class="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
        <div class="p-4 bg-[#1C2541] rounded-lg border border-slate-700 space-y-2">
          <div class="text-[#FBBF24] font-black uppercase tracking-wider text-[10px]">WhatsApp (Meta) service</div>
          <div class="text-sm font-bold text-[#34D399]">Mode: {{ telemetryData.gateways?.whatsapp?.mode }}</div>
          <div class="text-slate-300">Phone number ID: <code class="text-emerald-300">{{ telemetryData.gateways?.whatsapp?.phone_number_id }}</code></div>
          <div class="text-slate-400 text-[11px]">Security check on incoming messages is on.</div>
        </div>

        <div class="p-4 bg-[#1C2541] rounded-lg border border-slate-700 space-y-2">
          <div class="text-[#60A5FA] font-black uppercase tracking-wider text-[10px]">SMS service (India DLT registered)</div>
          <div class="text-sm font-bold text-[#60A5FA]">Mode: {{ telemetryData.gateways?.sms?.mode }}</div>
          <div class="text-slate-300">Registered ID: <code class="text-blue-300">{{ telemetryData.gateways?.sms?.dlt_entity_id }}</code></div>
          <div class="text-slate-400 text-[11px]">Paid SMS sending stays blocked until registration is complete.</div>
        </div>

        <div class="p-4 bg-[#1C2541] rounded-lg border border-slate-700 space-y-2">
          <div class="text-slate-400 font-black uppercase tracking-wider text-[10px]">Overall summary</div>
          <div class="text-sm font-bold text-white">Total messages: {{ telemetryData.summary?.total_notifications }}</div>
          <div class="flex flex-wrap gap-1 mt-1">
            <span v-for="(count, stat) in telemetryData.summary?.by_status" :key="stat" class="px-1.5 py-0.5 rounded bg-slate-800 text-[10px] text-slate-200 border border-slate-700">
              {{ stat }}: {{ count }}
            </span>
          </div>
        </div>
      </div>
      <div v-else class="text-center py-4 text-xs text-slate-400">Loading status...</div>
    </div>

    <!-- ERROR & SUCCESS ALERTS -->
    <div v-if="saveSuccess" class="p-4 rounded-xl bg-[#ECFDF5] border-[1.5px] border-[#065F46] text-[#064E3B] text-xs sm:text-sm font-black flex items-center gap-2 shadow-[2px_2px_0_0_#065F46]">
      <CheckCircle2 class="w-4 h-4 text-[#059669] shrink-0" />
      <span>Your reminder settings are saved.</span>
    </div>

    <div v-if="errorMessage" class="p-4 rounded-xl bg-[#FEF2F2] border-[1.5px] border-[#DC2626] text-[#991B1B] text-xs sm:text-sm font-black flex items-center gap-2 shadow-[2px_2px_0_0_#DC2626]">
      <AlertCircle class="w-4 h-4 text-[#DC2626] shrink-0" />
      <span>{{ errorMessage }}</span>
    </div>

    <!-- STEP 1: MOBILE NUMBER & OTP VERIFICATION CARD -->
    <div class="bg-[#FBFBFA] rounded-xl p-6 sm:p-8 border-[1.5px] border-[#0B132B] shadow-[2.5px_2.5px_0_0_#0B132B] space-y-6">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b-[1.5px] border-[#0B132B] pb-5">
        <div>
          <div class="text-xs font-black uppercase tracking-wider text-[#D97706]">Step 1: Your mobile number</div>
          <h2 class="text-xl font-black text-[#0B132B] flex items-center gap-2 mt-0.5">
            <Phone class="w-5 h-5 text-[#0B132B]" />
            Your mobile number and permission
          </h2>
          <p class="text-xs sm:text-sm text-[#475569] mt-1 font-medium">
            To stop spam, we must confirm the phone number is yours before we send reminders.
          </p>
        </div>

        <button
          @click="openVerifyModal()"
          class="px-4 py-2 rounded-lg text-xs font-black transition-all flex items-center gap-1.5 shrink-0 self-start sm:self-auto cursor-pointer border-[1.5px]"
          :class="prefs.is_mobile_verified ? 'bg-white hover:bg-slate-100 text-[#0B132B] border-[#0B132B] shadow-[2px_2px_0_0_#0B132B]' : 'bg-[#D97706] hover:bg-[#B45309] text-white border-[#0B132B] shadow-[2px_2px_0_0_#0B132B]'"
        >
          <Phone class="w-3.5 h-3.5" />
          <span>{{ prefs.is_mobile_verified ? 'Change Mobile Number' : 'Verify my mobile number' }}</span>
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Number Status -->
        <div class="p-4 rounded-xl bg-white border-[1.5px] border-[#0B132B] shadow-[1.5px_1.5px_0_0_#0B132B] flex items-center justify-between">
          <div>
            <div class="text-[11px] font-black text-[#64748B] uppercase tracking-wider">Your mobile number</div>
            <div class="text-base font-black text-[#0B132B] mt-0.5 font-mono">
              {{ prefs.mobile_number || 'No number added' }}
            </div>
          </div>
          <div>
            <span v-if="prefs.is_mobile_verified" class="inline-flex items-center gap-1 px-2.5 py-1 rounded-sm text-xs font-black bg-[#D1FAE5] text-[#065F46] border border-[#065F46]">
              <CheckCircle2 class="w-3 h-3 text-[#059669]" />
              Verified
            </span>
            <span v-else class="inline-flex items-center gap-1 px-2.5 py-1 rounded-sm text-xs font-black bg-[#FEF3C7] text-[#92400E] border border-[#D97706]">
              <AlertTriangle class="w-3 h-3 text-[#D97706]" />
              Not verified
            </span>
          </div>
        </div>

        <!-- WhatsApp Consent Timestamp -->
        <div class="p-4 rounded-xl bg-white border-[1.5px] border-[#0B132B] shadow-[1.5px_1.5px_0_0_#0B132B]">
          <div class="text-[11px] font-black text-[#64748B] uppercase tracking-wider">WhatsApp permission</div>
          <div class="text-xs font-black text-[#0B132B] mt-1 flex items-center gap-1.5">
            <span class="w-2.5 h-2.5 rounded-full border border-[#0B132B]" :class="prefs.whatsapp_enabled ? 'bg-[#059669]' : 'bg-slate-300'"></span>
            <span>{{ prefs.whatsapp_enabled ? 'Permission on' : 'Permission off' }}</span>
          </div>
          <div class="text-[11px] text-[#64748B] mt-1 font-medium">
            {{ prefs.whatsapp_enabled ? 'Since: ' + formatDate(prefs.whatsapp_opt_in_at) : (prefs.whatsapp_opt_out_at ? 'Turned off on ' + formatDate(prefs.whatsapp_opt_out_at) : 'No permission given yet') }}
          </div>
        </div>

        <!-- SMS Consent Timestamp -->
        <div class="p-4 rounded-xl bg-white border-[1.5px] border-[#0B132B] shadow-[1.5px_1.5px_0_0_#0B132B]">
          <div class="text-[11px] font-black text-[#64748B] uppercase tracking-wider">SMS permission</div>
          <div class="text-xs font-black text-[#0B132B] mt-1 flex items-center gap-1.5">
            <span class="w-2.5 h-2.5 rounded-full border border-[#0B132B]" :class="prefs.sms_enabled ? 'bg-[#2563EB]' : 'bg-slate-300'"></span>
            <span>{{ prefs.sms_enabled ? 'Permission on' : 'Permission off' }}</span>
          </div>
          <div class="text-[11px] text-[#64748B] mt-1 font-medium">
            {{ prefs.sms_enabled ? 'Since: ' + formatDate(prefs.sms_opt_in_at) : (prefs.sms_opt_out_at ? 'Turned off on ' + formatDate(prefs.sms_opt_out_at) : 'No permission given yet') }}
          </div>
        </div>
      </div>
    </div>

    <!-- STEP 2: CHANNELS & LANGUAGE SELECTION -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      <!-- WHATSAPP CARD -->
      <div class="bg-white rounded-xl p-6 border-[1.5px] border-[#0B132B] shadow-[2.5px_2.5px_0_0_#0B132B] flex flex-col justify-between space-y-4 relative overflow-hidden">
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <div class="p-2.5 bg-[#ECFDF5] text-[#065F46] rounded-lg border border-[#065F46]">
              <MessageSquare class="w-6 h-6" />
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input 
                type="checkbox" 
                :checked="prefs.whatsapp_enabled"
                @change="handleChannelToggle('whatsapp')"
                :disabled="!prefs.is_mobile_verified && !prefs.whatsapp_enabled"
                class="sr-only peer"
              >
              <div class="w-11 h-6 bg-slate-500 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-[#0B132B] after:border after:rounded-full after:h-5 after:width-5 after:transition-all peer-checked:bg-[#059669] border border-[#0B132B]"></div>
            </label>
          </div>

          <div>
            <h3 class="font-black text-[#0B132B] text-base flex items-center gap-1.5">
              WhatsApp reminders
              <span class="text-[10px] px-2 py-0.5 rounded-sm font-black border border-[#0B132B]" :class="channelsAvailable.whatsapp.is_configured ? 'bg-[#D1FAE5] text-[#065F46]' : 'bg-[#E0E7FF] text-[#3730A3]'">
                {{ channelsAvailable.whatsapp.provider_mode }}
              </span>
            </h3>
            <p class="text-xs text-[#475569] mt-1 font-medium leading-relaxed">
              Sends reminders to your WhatsApp for close deadlines, missing documents and office remarks.
            </p>
          </div>
        </div>

        <div class="pt-3 border-t-[1.5px] border-[#0B132B] text-[11px] text-[#64748B] space-y-1 font-medium">
          <div class="flex items-center justify-between">
            <span>Service provider:</span>
            <strong class="text-[#0B132B]">Meta Cloud API</strong>
          </div>
          <div class="flex items-center justify-between">
            <span>Stop anytime:</span>
            <strong class="text-[#059669]">You can turn it off anytime</strong>
          </div>
        </div>
      </div>

      <!-- SMS GATEWAY CARD -->
      <div class="bg-white rounded-xl p-6 border-[1.5px] border-[#0B132B] shadow-[2.5px_2.5px_0_0_#0B132B] flex flex-col justify-between space-y-4 relative overflow-hidden">
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <div class="p-2.5 bg-[#EFF6FF] text-[#1E40AF] rounded-lg border border-[#1E40AF]">
              <Phone class="w-6 h-6" />
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input 
                type="checkbox" 
                :checked="prefs.sms_enabled"
                @change="handleChannelToggle('sms')"
                :disabled="!prefs.is_mobile_verified && !prefs.sms_enabled"
                class="sr-only peer"
              >
              <div class="w-11 h-6 bg-slate-500 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-[#0B132B] after:border after:rounded-full after:h-5 after:width-5 after:transition-all peer-checked:bg-[#2563EB] border border-[#0B132B]"></div>
            </label>
          </div>

          <div>
            <h3 class="font-black text-[#0B132B] text-base flex items-center gap-1.5">
              SMS reminders
              <span class="text-[10px] px-2 py-0.5 rounded-sm font-black border border-[#0B132B]" :class="channelsAvailable.sms.is_configured ? 'bg-[#DBEAFE] text-[#1E40AF]' : 'bg-slate-100 text-slate-800'">
                {{ channelsAvailable.sms.provider_mode }}
              </span>
            </h3>
            <p class="text-xs text-[#475569] mt-1 font-medium leading-relaxed">
              Text message reminders for villages with weak internet. Works without mobile data.
            </p>
          </div>
        </div>

        <div class="pt-3 border-t-[1.5px] border-[#0B132B] text-[11px] text-[#64748B] space-y-1 font-medium">
          <div class="flex items-center justify-between">
            <span>Sender ID:</span>
            <strong class="text-[#0B132B]">YOJNAV (DLT Approved)</strong>
          </div>
          <div class="flex items-center justify-between">
            <span>Status:</span>
            <strong class="text-[#2563EB]">{{ channelsAvailable.sms.is_configured ? 'SMS service active' : 'Test mode, no real SMS sent' }}</strong>
          </div>
        </div>
      </div>

      <!-- IN-APP CONSOLE & LANGUAGE -->
      <div class="bg-white rounded-xl p-6 border-[1.5px] border-[#0B132B] shadow-[2.5px_2.5px_0_0_#0B132B] flex flex-col justify-between space-y-4">
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <div class="p-2.5 bg-[#FAF5FF] text-[#6B21A8] rounded-lg border border-[#6B21A8]">
              <Bell class="w-6 h-6" />
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input 
                type="checkbox" 
                :checked="prefs.in_app_enabled"
                @change="handleChannelToggle('in_app')"
                class="sr-only peer"
              >
              <div class="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-[#0B132B] after:border after:rounded-full after:h-5 after:width-5 after:transition-all peer-checked:bg-[#7C3AED] border border-[#0B132B]"></div>
            </label>
          </div>

          <div>
            <h3 class="font-black text-[#0B132B] text-base">Alerts on this website</h3>
            <p class="text-xs text-[#475569] mt-1 font-medium leading-relaxed">
              Alerts shown on this website when you log in or check your applications.
            </p>
          </div>
        </div>

        <!-- Language Selector -->
        <div class="pt-3 border-t-[1.5px] border-[#0B132B] space-y-1.5">
          <label class="text-[11px] font-black text-[#0B132B] uppercase tracking-wider">Language for reminders</label>
          <div class="grid grid-cols-3 gap-1.5 bg-[#F1F5F9] p-1 rounded-lg border border-[#0B132B]">
            <button
              @click="prefs.preferred_language = 'en'; savePreferences();"
              class="py-1 text-xs font-bold rounded-sm transition-all cursor-pointer"
              :class="prefs.preferred_language === 'en' ? 'bg-[#0B132B] text-white shadow-[1px_1px_0_0_#000]' : 'text-[#475569] hover:text-[#0B132B]'"
            >
              English
            </button>
            <button
              @click="prefs.preferred_language = 'mr'; savePreferences();"
              class="py-1 text-xs font-bold rounded-sm transition-all cursor-pointer"
              :class="prefs.preferred_language === 'mr' ? 'bg-[#0B132B] text-white shadow-[1px_1px_0_0_#000]' : 'text-[#475569] hover:text-[#0B132B]'"
            >
              मराठी
            </button>
            <button
              @click="prefs.preferred_language = 'hi'; savePreferences();"
              class="py-1 text-xs font-bold rounded-sm transition-all cursor-pointer"
              :class="prefs.preferred_language === 'hi' ? 'bg-[#0B132B] text-white shadow-[1px_1px_0_0_#000]' : 'text-[#475569] hover:text-[#0B132B]'"
            >
              हिंदी
            </button>
          </div>
        </div>
      </div>

    </div>

    <!-- 1-CLICK CITIZEN TEST DRIVE SECTION -->
    <div class="bg-[#FEF3C7]/40 rounded-xl p-6 sm:p-8 border-[1.5px] border-[#0B132B] shadow-[2.5px_2.5px_0_0_#0B132B] space-y-4">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span class="inline-flex items-center gap-1 text-[11px] font-black uppercase tracking-wider text-[#92400E]">
            <Sparkles class="w-3.5 h-3.5" />
            Try it out
          </span>
          <h2 class="text-xl font-black text-[#0B132B] mt-0.5">
            Send a test reminder
          </h2>
          <p class="text-xs sm:text-sm text-[#475569] mt-0.5 font-medium">
            Send a sample reminder now, in your chosen language ({{ prefs.preferred_language.toUpperCase() }}).
          </p>
        </div>

        <div class="flex items-center gap-2">
          <select 
            v-model="testChannel" 
            class="px-3 py-2 bg-white rounded-lg text-xs font-black border-[1.5px] border-[#0B132B] text-[#0B132B] shadow-[2px_2px_0_0_#0B132B] focus:outline-hidden"
          >
            <option value="WHATSAPP">WhatsApp 🟢</option>
            <option value="SMS">SMS 📱</option>
            <option value="IN_APP">Alert on this website 🔔</option>
          </select>

          <button
            @click="handleSendTest()"
            :disabled="isTesting"
            class="px-4 py-2 bg-[#D97706] hover:bg-[#B45309] text-white rounded-lg text-xs font-black transition-all shadow-[2px_2px_0_0_#0B132B] border-[1.5px] border-[#0B132B] flex items-center gap-1.5 disabled:opacity-50 cursor-pointer"
          >
            <Send class="w-3.5 h-3.5" />
            <span>{{ isTesting ? 'Sending...' : 'Send Test Reminder 🔔' }}</span>
          </button>
        </div>
      </div>

      <!-- Test Result Alert -->
      <div v-if="testResult" class="p-4 rounded-xl text-xs font-medium space-y-1 border-[1.5px] shadow-[2px_2px_0_0_#0B132B]" :class="testResult.success ? 'bg-[#ECFDF5] text-[#064E3B] border-[#065F46]' : 'bg-[#FEF2F2] text-[#991B1B] border-[#DC2626]'">
        <div class="font-black flex items-center gap-1.5">
          <CheckCircle2 v-if="testResult.success" class="w-4 h-4 text-[#059669]" />
          <AlertCircle v-else class="w-4 h-4 text-[#DC2626]" />
          <span>{{ testResult.message }}</span>
        </div>
        <div v-if="testResult.notification" class="text-[11px] text-[#065F46] bg-white p-2.5 rounded-lg border border-[#065F46] mt-2 font-mono">
          <div>Provider: <strong>{{ testResult.notification.provider }}</strong></div>
          <div>Status: <strong>{{ testResult.notification.delivery_status }}</strong> (Message ID: {{ testResult.notification.provider_message_id }})</div>
          <div class="mt-1 pt-1 border-t border-[#065F46]/30 font-sans text-[#0B132B]">
            "{{ testResult.notification.message_body }}"
          </div>
        </div>
      </div>
    </div>

    <!-- STEP 3: THE 6 CANONICAL NOTIFICATION EVENTS WITH INTERACTIVE PREVIEWS -->
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <div>
          <div class="text-xs font-black uppercase tracking-wider text-[#D97706]">Step 3: Choose your alerts</div>
          <h2 class="text-xl font-black text-[#0B132B] mt-0.5">
            The 6 types of reminders
          </h2>
          <p class="text-xs sm:text-sm text-[#475569] mt-0.5 font-medium">
            Reminders are based on official scheme dates. Choose the ones you want:
          </p>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div 
          v-for="evt in canonicalEvents" 
          :key="evt.key" 
          class="bg-[#FBFBFA] rounded-xl p-5 border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#0B132B] flex flex-col justify-between space-y-3"
        >
          <div class="space-y-2">
            <div class="flex items-start justify-between gap-2">
              <h4 class="font-black text-sm text-[#0B132B]">
                {{ evt.title[prefs.preferred_language] }}
              </h4>
              <label class="relative inline-flex items-center cursor-pointer shrink-0">
                <input 
                  type="checkbox" 
                  v-model="prefs[evt.field]"
                  @change="savePreferences()"
                  class="sr-only peer"
                >
                <div class="w-9 h-5 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-[#0B132B] after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-[#059669] border border-[#0B132B]"></div>
              </label>
            </div>

            <p class="text-[11px] text-[#475569]">
              <strong class="text-[#0B132B]">Trigger:</strong> {{ evt.trigger }}
            </p>

            <!-- Trilingual WhatsApp Chat Bubble Preview -->
            <div class="bg-[#ECFDF5] border-[1.5px] border-[#059669] p-3 rounded-lg text-[11px] text-[#064E3B] leading-relaxed shadow-[1px_1px_0_0_#059669] relative">
              <div class="flex items-center justify-between text-[10px] text-[#065F46] font-black mb-1 pb-1 border-b border-[#059669]/30">
                <span>YojnaVia alert ({{ prefs.preferred_language.toUpperCase() }})</span>
                <span class="flex items-center gap-0.5 text-[#059669]">
                  <CheckCircle2 class="w-2.5 h-2.5" />
                  Official
                </span>
              </div>
              <p>{{ evt.preview[prefs.preferred_language] }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- STEP 4: NOTIFICATION DELIVERY HISTORY & TELEMETRY TABLE -->
    <div class="bg-[#FBFBFA] rounded-xl p-6 sm:p-8 border-[1.5px] border-[#0B132B] shadow-[2.5px_2.5px_0_0_#0B132B] space-y-6">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b-[1.5px] border-[#0B132B] pb-5">
        <div>
          <div class="text-xs font-black uppercase tracking-wider text-[#D97706]">Message history</div>
          <h2 class="text-xl font-black text-[#0B132B] flex items-center gap-2 mt-0.5">
            <Clock class="w-5 h-5 text-[#0B132B]" />
            Reminders sent to you
          </h2>
          <p class="text-xs sm:text-sm text-[#475569] mt-1 font-medium">
            A record of reminders sent, test messages, and reminders stopped because you opted out.
          </p>
        </div>

        <!-- Filter Controls -->
        <div class="flex flex-wrap items-center gap-2">
          <select 
            v-model="historyFilterChannel" 
            @change="fetchHistory()"
            class="px-2.5 py-1.5 bg-white rounded-lg text-xs font-black border-[1.5px] border-[#0B132B] text-[#0B132B] shadow-[1.5px_1.5px_0_0_#0B132B] focus:outline-hidden"
          >
            <option value="ALL">All types</option>
            <option value="WHATSAPP">WhatsApp</option>
            <option value="SMS">SMS</option>
            <option value="IN_APP">On this website</option>
          </select>

          <select 
            v-model="historyFilterStatus" 
            @change="fetchHistory()"
            class="px-2.5 py-1.5 bg-white rounded-lg text-xs font-black border-[1.5px] border-[#0B132B] text-[#0B132B] shadow-[1.5px_1.5px_0_0_#0B132B] focus:outline-hidden"
          >
            <option value="ALL">All results</option>
            <option value="SIMULATED">Test</option>
            <option value="DELIVERED">Delivered</option>
            <option value="SENT">Sent</option>
            <option value="OPTED_OUT">Stopped</option>
            <option value="FAILED">Failed</option>
          </select>

          <button
            @click="fetchHistory()"
            :disabled="isHistoryLoading"
            class="p-2 rounded-lg bg-white hover:bg-slate-100 text-[#0B132B] border-[1.5px] border-[#0B132B] shadow-[1.5px_1.5px_0_0_#0B132B] transition-colors cursor-pointer"
            title="Refresh list"
          >
            <RefreshCw class="w-3.5 h-3.5" :class="{ 'animate-spin': isHistoryLoading }" />
          </button>
        </div>
      </div>

      <!-- History Table -->
      <div v-if="historyLogs.length === 0" class="text-center py-12 text-[#64748B] space-y-2">
        <Bell class="w-10 h-10 mx-auto text-[#CBD5E1]" />
        <div class="text-sm font-black text-[#0B132B]">No notifications sent yet</div>
        <p class="text-xs text-[#64748B] max-w-sm mx-auto font-medium">
          Click "Send Test Reminder 🔔" above to try a sample reminder.
        </p>
      </div>

      <div v-else class="overflow-x-auto border-[1.5px] border-[#0B132B] rounded-lg">
        <table class="w-full text-left text-xs bg-white">
          <thead>
            <tr class="border-b-[1.5px] border-[#0B132B] bg-[#F1F5F9] text-[#0B132B] uppercase text-[10px] font-black">
              <th class="py-2.5 px-3">Channel</th>
              <th class="py-2.5 px-3">Reminder type</th>
              <th class="py-2.5 px-3">Sent to</th>
              <th class="py-2.5 px-3">Language</th>
              <th class="py-2.5 px-3">Status</th>
              <th class="py-2.5 px-3">Reference no.</th>
              <th class="py-2.5 px-3">Sent on</th>
              <th class="py-2.5 px-3 text-right">Details</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-[#E2E8F0] font-medium text-[#334155]">
            <template v-for="log in historyLogs" :key="log.id">
              <tr class="hover:bg-[#F8FAFC] transition-colors">
                <td class="py-3 px-3">
                  <span class="inline-flex items-center gap-1 font-bold text-[#0B132B]">
                    <span v-if="log.channel === 'WHATSAPP'">🟢 WA</span>
                    <span v-else-if="log.channel === 'SMS'">📱 SMS</span>
                    <span v-else>🔔 InApp</span>
                  </span>
                </td>
                <td class="py-3 px-3 font-black text-[#0B132B]">
                  {{ log.event_type }}
                </td>
                <td class="py-3 px-3 font-mono text-[#64748B] text-[11px]">
                  {{ log.recipient }}
                </td>
                <td class="py-3 px-3">
                  <span class="px-1.5 py-0.5 rounded-sm bg-[#F1F5F9] text-[10px] font-black uppercase text-[#0B132B] border border-[#CBD5E1]">
                    {{ log.language }}
                  </span>
                </td>
                <td class="py-3 px-3">
                  <span 
                    class="px-2 py-0.5 rounded-sm text-[10px] font-black border border-[#0B132B]"
                    :class="getStatusBadgeClass(log.delivery_status)"
                  >
                    {{ log.delivery_status }}
                  </span>
                </td>
                <td class="py-3 px-3 font-mono text-[#64748B] text-[10px]">
                  {{ log.provider_message_id || '—' }}
                </td>
                <td class="py-3 px-3 text-[#64748B] whitespace-nowrap font-mono text-[11px]">
                  {{ formatDate(log.sent_at || log.created_at) }}
                </td>
                <td class="py-3 px-3 text-right">
                  <button
                    @click="expandedLogId = expandedLogId === log.id ? null : log.id"
                    class="text-[#D97706] hover:text-[#B45309] font-black cursor-pointer"
                  >
                    {{ expandedLogId === log.id ? 'Hide' : 'View' }}
                  </button>
                </td>
              </tr>

              <!-- Expanded Log Message View -->
              <tr v-if="expandedLogId === log.id" class="bg-[#FFFBEB]">
                <td colspan="8" class="p-4 space-y-2 text-xs border-y border-[#FCD34D]">
                  <div class="font-black text-[#78350F] flex items-center justify-between">
                    <span>Title: {{ log.title }}</span>
                    <span class="text-[10px] text-[#64748B] font-mono">Reference: {{ log.idempotency_key }}</span>
                  </div>
                  <div class="p-3 bg-white rounded-lg border border-[#FCD34D] text-[#0B132B] font-sans leading-relaxed">
                    {{ log.message_body }}
                  </div>
                  <div v-if="log.error_message" class="text-[#DC2626] font-black text-[11px]">
                    Problem: {{ log.error_message }}
                  </div>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>

    <!-- MOBILE NUMBER VERIFICATION MODAL -->
    <div v-if="isVerifyModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#0B132B]/70 backdrop-blur-xs">
      <div class="bg-[#FBFBFA] rounded-xl max-w-md w-full p-6 sm:p-8 shadow-[4px_4px_0_0_#0B132B] border-[2px] border-[#0B132B] space-y-6">
        <div class="flex items-center justify-between border-b-[1.5px] border-[#0B132B] pb-3">
          <h3 class="font-black text-[#0B132B] text-lg flex items-center gap-2">
            <Phone class="w-5 h-5 text-[#0B132B]" />
            Confirm your mobile number
          </h3>
          <button @click="isVerifyModalOpen = false" class="text-[#64748B] hover:text-[#0B132B] font-bold text-sm cursor-pointer">✕</button>
        </div>

        <div v-if="verifyError" class="p-3 rounded-lg bg-[#FEF2F2] border border-[#DC2626] text-[#991B1B] text-xs font-black">
          {{ verifyError }}
        </div>

        <!-- Phone input step -->
        <div v-if="!otpSent" class="space-y-4">
          <p class="text-xs text-[#475569] font-medium leading-relaxed">
            Enter your 10-digit mobile number to get WhatsApp and SMS reminders.
          </p>

          <div class="space-y-1">
            <label class="text-[11px] font-black text-[#0B132B] uppercase tracking-wider">Mobile Number</label>
            <div class="flex items-center">
              <span class="px-3 py-2.5 bg-[#F1F5F9] border-[1.5px] border-r-0 border-[#0B132B] rounded-l-lg text-xs font-black text-[#0B132B]">+91</span>
              <input 
                type="text" 
                v-model="inputPhone"
                placeholder="9876543210"
                class="w-full px-3 py-2.5 bg-white border-[1.5px] border-[#0B132B] rounded-r-lg text-xs font-bold text-[#0B132B] focus:outline-hidden"
              >
            </div>
          </div>

          <button
            @click="handleSendOtp()"
            :disabled="isVerifying"
            class="w-full py-2.5 bg-[#D97706] hover:bg-[#B45309] text-white rounded-lg text-xs font-black transition-all border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#0B132B] disabled:opacity-50 cursor-pointer"
          >
            {{ isVerifying ? 'Sending Code...' : 'Send code' }}
          </button>
        </div>

        <!-- OTP verification step -->
        <div v-else class="space-y-4">
          <p class="text-xs text-[#475569] font-medium">
            We sent a 6-digit code to <strong>+91 {{ inputPhone }}</strong>.
          </p>

          <div v-if="demoOtpCode" class="p-3 bg-[#FEF3C7] border border-[#D97706] rounded-lg text-xs text-[#92400E]">
            <strong>Test code:</strong> Enter code <code class="font-black text-[#0B132B] bg-white px-1.5 py-0.5 rounded border border-[#0B132B]">{{ demoOtpCode }}</code> (or <code>123456</code>).
          </div>

          <div class="space-y-1">
            <label class="text-[11px] font-black text-[#0B132B] uppercase tracking-wider">6-Digit Code</label>
            <input 
              type="text" 
              v-model="inputOtp"
              placeholder="123456"
              maxlength="6"
              class="w-full px-3 py-2.5 bg-white border-[1.5px] border-[#0B132B] rounded-lg text-center text-lg font-mono font-black tracking-widest text-[#0B132B] focus:outline-hidden shadow-[2px_2px_0_0_#0B132B]"
            >
          </div>

          <div class="flex items-center gap-2">
            <button
              @click="otpSent = false"
              class="w-1/2 py-2.5 bg-white hover:bg-slate-100 text-[#0B132B] rounded-lg text-xs font-black transition-all border-[1.5px] border-[#0B132B] shadow-[1.5px_1.5px_0_0_#0B132B] cursor-pointer"
            >
              Back
            </button>
            <button
              @click="handleVerifyOtp()"
              :disabled="isVerifying"
              class="w-1/2 py-2.5 bg-[#059669] hover:bg-[#047857] text-white rounded-lg text-xs font-black transition-all border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#0B132B] disabled:opacity-50 cursor-pointer"
            >
              {{ isVerifying ? 'Verifying...' : 'Confirm' }}
            </button>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>
