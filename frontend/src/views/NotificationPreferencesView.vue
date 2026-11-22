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
      en: 'Application Deadline Approaching',
      mr: 'अर्ज अंतिम मुदत सूचना',
      hi: 'आवेदन अंतिम तिथि अलर्ट'
    },
    trigger: 'Sent 7 days, 2 days, and on deadline day from verified scheme record.',
    preview: {
      en: `Namaste ${store.profile?.name || 'Citizen'}, this is an important reminder from YOJNAVIA. The official application deadline for 'Post Matric Scholarship' on the MahaDBT portal is on 31 December 2026 (2 days remaining). Please ensure all mandatory documents are submitted before portal cutoff.`,
      mr: `नमस्ते ${store.profile?.name || 'विद्यार्थी'}, योजनाव्हायाकडून महत्त्वाची सूचना. 'पोस्ट मॅट्रिक शिष्यवृत्ती' या योजनेसाठी MahaDBT संकेतस्थळावर अर्ज करण्याची अंतिम मुदत 31 डिसेंबर 2026 आहे (फक्त 2 दिवस शिल्लक). कृपया मुदतीपूर्वी आपले कागदपत्र सादर करा.`,
      hi: `नमस्ते ${store.profile?.name || 'नागरिक'}, योजनावाया की ओर से महत्वपूर्ण सूचना। 'पोस्ट मैट्रिक छात्रवृत्ति' के लिए MahaDBT पोर्टल पर आवेदन की अंतिम तिथि 31 दिसंबर 2026 है (केवल 2 दिन शेष)। कृपया पोर्टल बंद होने से पहले अपने दस्तावेज़ जमा करें।`
    }
  },
  {
    key: 'MISSING_DOCUMENT_REMINDER',
    field: 'notify_missing_docs' as keyof Preferences,
    title: {
      en: 'Pending Mandatory Document Reminder',
      mr: 'प्रलंबित कागदपत्र स्मरणपत्र',
      hi: 'लंबित आवश्यक दस्तावेज़ अनुस्मारक'
    },
    trigger: 'Weekly reminder while mandatory civil documents (Tahsildar Income, Caste Validity) remain unprocured.',
    preview: {
      en: `Namaste ${store.profile?.name || 'Citizen'}, your application for 'Rajarshi Shahu Maharaj Tuition Scheme' is currently waiting for: 'Tahsildar Income Certificate'. You can apply online via Aaple Sarkar portal (15-day statutory SLA). Obtaining this unlocks your application progress.`,
      mr: `नमस्ते ${store.profile?.name || 'विद्यार्थी'}, आपल्या 'राजर्षी शाहू महाराज शिक्षण शुल्क योजना' अर्जासाठी 'तहसीलदार उत्पन्न दाखला' अद्याप प्रलंबित आहे. आपण 'आपले सरकार' पोर्टलवरून १५ दिवसांच्या विहित मुदतीत अर्ज करू शकता.`,
      hi: `नमस्ते ${store.profile?.name || 'नागरिक'}, आपके 'राजर्षि शाहू महाराज शिक्षण शुल्क योजना' आवेदन के लिए 'तहसीलदार आय प्रमाण पत्र' अभी लंबित है। आप 'आपले सरकार' पोर्टल के माध्यम से 15-दिवसीय विधिक समय-सीमा में आवेदन कर सकते हैं।`
    }
  },
  {
    key: 'MILESTONE_UPDATED',
    field: 'notify_milestones' as keyof Preferences,
    title: {
      en: 'Application Milestone Updated',
      mr: 'अर्ज टप्पा बदल सूचना',
      hi: 'आवेदन चरण अद्यतन सूचना'
    },
    trigger: 'Sent whenever application transitions stages (e.g. Discovered -> Documents Ready -> Applied -> Sanctioned).',
    preview: {
      en: `Namaste ${store.profile?.name || 'Citizen'}, your application milestone for 'Post Matric Scholarship' has progressed to: Applied / College Scrutiny. Next step: Submit printed acknowledgment copy along with attested document copies to College Scholarship Clerk.`,
      mr: `नमस्ते ${store.profile?.name || 'विद्यार्थी'}, आपल्या 'पोस्ट मॅट्रिक शिष्यवृत्ती' अर्जाचा टप्पा पुढे सरकला आहे: अर्ज सादर केला / महाविद्यालयीन पडताळणी. पुढील कृती: महाविद्यालयातील शिष्यवृत्ती लिपिकाकडे स्वाक्षरी प्रत व कागदपत्रे जमा करा.`,
      hi: `नमस्ते ${store.profile?.name || 'नागरिक'}, आपके 'पोस्ट मैट्रिक छात्रवृत्ति' आवेदन की स्थिति आगे बढ़ी है: आवेदन जमा / कॉलेज स्तर पर जांच। अगला कदम: कॉलेज छात्रवृत्ति लिपिक के पास हस्ताक्षरित प्रति व दस्तावेज जमा करें।`
    }
  },
  {
    key: 'STATUS_INACTIVITY',
    field: 'notify_inactivity' as keyof Preferences,
    title: {
      en: 'Status Inactivity (>14 Days)',
      mr: '१४ दिवसांची अक्रियाशीलता सूचना',
      hi: '14 दिनों से कोई स्थिति परिवर्तन नहीं'
    },
    trigger: 'Sent when self-reported application status has not changed for 14 days, prompting follow-up.',
    preview: {
      en: `Namaste ${store.profile?.name || 'Citizen'}, your application for 'EBC Fee Concession' has been in 'Under Review' status for over 14 days. We recommend checking with your College Scholarship Clerk or logging into the portal to check scrutiny queries.`,
      mr: `नमस्ते ${store.profile?.name || 'विद्यार्थी'}, आपल्या 'ईबीसी शुल्क सवलत' अर्जाची स्थिती 'तपासणी सुरू' अशी १४ दिवसांपासून कायम आहे. कृपया महाविद्यालयातील लिपिकाकडे चौकशी करा अथवा पोर्टलवर लॉगिन करून पडताळणी शेरा तपासा.`,
      hi: `नमस्ते ${store.profile?.name || 'नागरिक'}, आपके 'ईबीसी शुल्क छूट' आवेदन की स्थिति 'समीक्षाधीन' पिछले 14 दिनों से अपरिवर्तित है। कृपया अपने कॉलेज लिपिक से संपर्क करें या पोर्टल पर लॉगिन करके जांच टिप्पणी देखें।`
    }
  },
  {
    key: 'GRIEVANCE_RESUBMISSION',
    field: 'notify_grievances' as keyof Preferences,
    title: {
      en: '15-Day Scrutiny Resubmission Clock',
      mr: '१५-दिवसीय पडताळणी दुरुस्ती मुदत',
      hi: '15-दिवसीय आपत्ति सुधार समय-सीमा'
    },
    trigger: 'Countdown reminders (Day 10, 5, 2, 1) to upload corrected documents before MahaDBT scrutiny auto-rejection.',
    preview: {
      en: `Namaste ${store.profile?.name || 'Citizen'}, an official scrutiny objection was raised on your 'Post Matric Scholarship' application. You have 5 days remaining to upload the corrected document before 28 November 2026. Do not let your application lapse!`,
      mr: `नमस्ते ${store.profile?.name || 'विद्यार्थी'}, आपल्या 'पोस्ट मॅट्रिक शिष्यवृत्ती' अर्जावर छाननी अधिकाऱ्याने आक्षेप नोंदवला आहे. अर्ज रद्द होण्यापासून वाचवण्यासाठी दुरुस्त कागदपत्र अपलोड करण्यास फक्त ५ दिवस शिल्लक आहेत (अंतिम मुदत: 28 नोव्हेंबर 2026).`,
      hi: `नमस्ते ${store.profile?.name || 'नागरिक'}, आपके 'पोस्ट मैट्रिक छात्रवृत्ति' आवेदन पर जांच अधिकारी द्वारा आपत्ति दर्ज की गई है। आवेदन स्वतः निरस्त होने से बचाने हेतु संशोधित दस्तावेज़ अपलोड करने के लिए केवल 5 दिन शेष हैं (अंतिम तिथि: 28 नवंबर 2026)।`
    }
  },
  {
    key: 'ANNUAL_RENEWAL',
    field: 'notify_renewals' as keyof Preferences,
    title: {
      en: 'Annual Academic & March 31 Renewal',
      mr: 'वार्षिक नूतनीकरण व ३१ मार्च दाखला मुदत',
      hi: 'वार्षिक नवीनीकरण एवं 31 मार्च प्रमाण पत्र समाप्ति'
    },
    trigger: 'Sent in February & March before statutory 31 March Tahsildar income certificate expiry and July MahaDBT cycle.',
    preview: {
      en: `Namaste ${store.profile?.name || 'Citizen'}, your Tahsildar Income Certificate expires on 31 March as per statutory financial year rules. Apply for the new 2026-27 certificate now on Aaple Sarkar to ensure continuous scholarship eligibility without delay.`,
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
    errorMessage.value = err?.response?.data?.error || 'Failed to load notification preferences.';
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
    errorMessage.value = err?.response?.data?.error || 'Failed to update preferences.';
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
    verifyError.value = err?.response?.data?.mobile_number?.[0] || err?.response?.data?.error || 'Failed to send OTP.';
  } finally {
    isVerifying.value = false;
  }
}

async function handleVerifyOtp() {
  if (!inputOtp.value.trim()) {
    verifyError.value = 'Please enter the 6-digit OTP code.';
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
    verifyError.value = err?.response?.data?.error || 'Invalid OTP code.';
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
    testResult.value = { success: false, message: err?.response?.data?.error || 'Failed to dispatch test reminder.' };
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
  if (!isoStr) return 'Not recorded';
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
    <div class="bg-gradient-to-r from-emerald-900 via-teal-900 to-indigo-950 text-white rounded-3xl p-6 sm:p-8 shadow-xl relative overflow-hidden">
      <div class="absolute -right-12 -top-12 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>
      <div class="relative z-10 space-y-4">
        <div class="flex flex-wrap items-center gap-2">
          <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-400/30">
            <ShieldCheck class="w-3.5 h-3.5" />
            Consent-Driven (Zero Unsolicited Messages)
          </span>
          <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-blue-500/20 text-blue-300 border border-blue-400/30">
            <CheckCircle2 class="w-3.5 h-3.5" />
            TRAI DLT Compliant (PE ID: 110155234000001)
          </span>
          <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-purple-500/20 text-purple-300 border border-purple-400/30">
            <MessageSquare class="w-3.5 h-3.5" />
            Meta WhatsApp Cloud API v20.0
          </span>
        </div>

        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 class="text-2xl sm:text-3xl font-black tracking-tight text-white flex items-center gap-2.5">
              <Bell class="w-8 h-8 text-emerald-400" />
              WhatsApp & SMS Deadline Notification System
            </h1>
            <p class="text-slate-300 text-sm sm:text-base max-w-3xl mt-1.5">
              Never miss a scholarship deadline, missing document SLA, 15-day scrutiny resubmission clock, or annual March 31 income certificate renewal.
            </p>
          </div>

          <!-- Quick Test Trigger & Admin Console Toggle -->
          <div class="flex items-center gap-2 shrink-0">
            <button
              @click="toggleTelemetry()"
              class="px-3.5 py-2 rounded-xl text-xs font-bold bg-white/10 hover:bg-white/20 text-white border border-white/20 transition-all flex items-center gap-1.5"
            >
              <Sliders class="w-3.5 h-3.5" />
              <span>Admin Telemetry</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ADMIN TELEMETRY DRAWER (IF TOGGLED) -->
    <div v-if="showAdminTelemetry" class="p-6 bg-slate-900 text-slate-100 rounded-3xl border border-slate-800 shadow-xl space-y-4">
      <div class="flex items-center justify-between border-b border-slate-800 pb-3">
        <div class="flex items-center gap-2">
          <Sliders class="w-5 h-5 text-emerald-400" />
          <h3 class="font-bold text-sm sm:text-base text-white">Live Notification Gateway Telemetry & Health</h3>
        </div>
        <button @click="showAdminTelemetry = false" class="text-xs text-slate-400 hover:text-white">Close ✕</button>
      </div>

      <div v-if="telemetryData" class="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
        <div class="p-4 bg-slate-800/60 rounded-2xl border border-slate-700 space-y-2">
          <div class="text-slate-400 font-bold uppercase tracking-wider text-[10px]">Meta WhatsApp Gateway</div>
          <div class="text-sm font-bold text-emerald-400">Mode: {{ telemetryData.gateways?.whatsapp?.mode }}</div>
          <div class="text-slate-300">Phone ID: <code class="text-emerald-300">{{ telemetryData.gateways?.whatsapp?.phone_number_id }}</code></div>
          <div class="text-slate-400 text-[11px]">HMAC-SHA256 signature verification active on inbound webhooks.</div>
        </div>

        <div class="p-4 bg-slate-800/60 rounded-2xl border border-slate-700 space-y-2">
          <div class="text-slate-400 font-bold uppercase tracking-wider text-[10px]">Indian SMS DLT Gateway</div>
          <div class="text-sm font-bold text-blue-400">Mode: {{ telemetryData.gateways?.sms?.mode }}</div>
          <div class="text-slate-300">Entity ID: <code class="text-blue-300">{{ telemetryData.gateways?.sms?.dlt_entity_id }}</code></div>
          <div class="text-slate-400 text-[11px]">Commercial delivery blocked without registered DLT credentials.</div>
        </div>

        <div class="p-4 bg-slate-800/60 rounded-2xl border border-slate-700 space-y-2">
          <div class="text-slate-400 font-bold uppercase tracking-wider text-[10px]">Overall Telemetry Metrics</div>
          <div class="text-sm font-bold text-white">Total Messages: {{ telemetryData.summary?.total_notifications }}</div>
          <div class="flex flex-wrap gap-1 mt-1">
            <span v-for="(count, stat) in telemetryData.summary?.by_status" :key="stat" class="px-1.5 py-0.5 rounded bg-slate-700 text-[10px] text-slate-200">
              {{ stat }}: {{ count }}
            </span>
          </div>
        </div>
      </div>
      <div v-else class="text-center py-4 text-xs text-slate-400">Loading gateway telemetry...</div>
    </div>

    <!-- ERROR & SUCCESS ALERTS -->
    <div v-if="saveSuccess" class="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs sm:text-sm font-bold flex items-center gap-2">
      <CheckCircle2 class="w-4 h-4 text-emerald-600 shrink-0" />
      <span>Notification preferences updated and saved securely!</span>
    </div>

    <div v-if="errorMessage" class="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-900 text-xs sm:text-sm font-bold flex items-center gap-2">
      <AlertCircle class="w-4 h-4 text-rose-600 shrink-0" />
      <span>{{ errorMessage }}</span>
    </div>

    <!-- STEP 1: MOBILE NUMBER & OTP VERIFICATION CARD -->
    <div class="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-6">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-5">
        <div>
          <div class="text-xs font-bold uppercase tracking-wider text-indigo-600">Step 1: Contact Identity</div>
          <h2 class="text-xl font-bold text-slate-900 flex items-center gap-2 mt-0.5">
            <Phone class="w-5 h-5 text-indigo-600" />
            Citizen Mobile Number & Verified Consent
          </h2>
          <p class="text-xs sm:text-sm text-slate-500 mt-1">
            Under TRAI and Meta WhatsApp anti-spam policies, explicit phone ownership verification is required before sending deadline reminders.
          </p>
        </div>

        <button
          @click="openVerifyModal()"
          class="px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 shadow-xs shrink-0 self-start sm:self-auto"
          :class="prefs.is_mobile_verified ? 'bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-300' : 'bg-emerald-600 hover:bg-emerald-700 text-white'"
        >
          <Phone class="w-3.5 h-3.5" />
          <span>{{ prefs.is_mobile_verified ? 'Change Mobile Number' : 'Verify Mobile Number Now' }}</span>
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Number Status -->
        <div class="p-4 rounded-2xl bg-slate-50 border border-slate-200 flex items-center justify-between">
          <div>
            <div class="text-[11px] font-bold text-slate-500 uppercase">Registered Mobile</div>
            <div class="text-base font-extrabold text-slate-900 mt-0.5">
              {{ prefs.mobile_number || 'No number added' }}
            </div>
          </div>
          <div>
            <span v-if="prefs.is_mobile_verified" class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
              <CheckCircle2 class="w-3 h-3 text-emerald-600" />
              Verified
            </span>
            <span v-else class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-800 border border-amber-300">
              <AlertTriangle class="w-3 h-3 text-amber-600" />
              Unverified
            </span>
          </div>
        </div>

        <!-- WhatsApp Consent Timestamp -->
        <div class="p-4 rounded-2xl bg-slate-50 border border-slate-200">
          <div class="text-[11px] font-bold text-slate-500 uppercase">WhatsApp Opt-in Audit</div>
          <div class="text-xs font-bold text-slate-800 mt-1 flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full" :class="prefs.whatsapp_enabled ? 'bg-emerald-500' : 'bg-slate-400'"></span>
            <span>{{ prefs.whatsapp_enabled ? 'Opted In' : 'Opted Out / Inactive' }}</span>
          </div>
          <div class="text-[11px] text-slate-500 mt-1">
            {{ prefs.whatsapp_enabled ? 'Since: ' + formatDate(prefs.whatsapp_opt_in_at) : (prefs.whatsapp_opt_out_at ? 'Opted out: ' + formatDate(prefs.whatsapp_opt_out_at) : 'No opt-in record') }}
          </div>
        </div>

        <!-- SMS Consent Timestamp -->
        <div class="p-4 rounded-2xl bg-slate-50 border border-slate-200">
          <div class="text-[11px] font-bold text-slate-500 uppercase">SMS Opt-in Audit</div>
          <div class="text-xs font-bold text-slate-800 mt-1 flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full" :class="prefs.sms_enabled ? 'bg-blue-500' : 'bg-slate-400'"></span>
            <span>{{ prefs.sms_enabled ? 'Opted In' : 'Opted Out / Inactive' }}</span>
          </div>
          <div class="text-[11px] text-slate-500 mt-1">
            {{ prefs.sms_enabled ? 'Since: ' + formatDate(prefs.sms_opt_in_at) : (prefs.sms_opt_out_at ? 'Opted out: ' + formatDate(prefs.sms_opt_out_at) : 'No opt-in record') }}
          </div>
        </div>
      </div>
    </div>

    <!-- STEP 2: CHANNELS & LANGUAGE SELECTION -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      <!-- WHATSAPP CARD -->
      <div class="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm flex flex-col justify-between space-y-4 relative overflow-hidden">
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <div class="p-2.5 bg-emerald-50 text-emerald-700 rounded-2xl">
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
              <div class="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:width-5 after:transition-all peer-checked:bg-emerald-600"></div>
            </label>
          </div>

          <div>
            <h3 class="font-bold text-slate-900 text-base flex items-center gap-1.5">
              WhatsApp Notifications
              <span class="text-[10px] px-2 py-0.5 rounded-full font-extrabold" :class="channelsAvailable.whatsapp.is_configured ? 'bg-emerald-100 text-emerald-800' : 'bg-indigo-100 text-indigo-800'">
                {{ channelsAvailable.whatsapp.provider_mode }}
              </span>
            </h3>
            <p class="text-xs text-slate-500 mt-1">
              Delivers rich alerts directly into your WhatsApp inbox for imminent deadlines, document SLAs, and scrutiny remarks.
            </p>
          </div>
        </div>

        <div class="pt-3 border-t border-slate-100 text-[11px] text-slate-500 space-y-1">
          <div class="flex items-center justify-between">
            <span>Provider:</span>
            <strong class="text-slate-700">Meta Cloud API</strong>
          </div>
          <div class="flex items-center justify-between">
            <span>Anti-Spam Policy:</span>
            <strong class="text-emerald-700">Instant Opt-Out Respected</strong>
          </div>
        </div>
      </div>

      <!-- SMS GATEWAY CARD -->
      <div class="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm flex flex-col justify-between space-y-4 relative overflow-hidden">
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <div class="p-2.5 bg-blue-50 text-blue-700 rounded-2xl">
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
              <div class="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:width-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div>
            <h3 class="font-bold text-slate-900 text-base flex items-center gap-1.5">
              SMS Gateway Reminders
              <span class="text-[10px] px-2 py-0.5 rounded-full font-extrabold" :class="channelsAvailable.sms.is_configured ? 'bg-blue-100 text-blue-800' : 'bg-slate-100 text-slate-800'">
                {{ channelsAvailable.sms.provider_mode }}
              </span>
            </h3>
            <p class="text-xs text-slate-500 mt-1">
              TRAI TCCCPR (2018) compliant text alerts for citizens in low-bandwidth rural talukas without active data connections.
            </p>
          </div>
        </div>

        <div class="pt-3 border-t border-slate-100 text-[11px] text-slate-500 space-y-1">
          <div class="flex items-center justify-between">
            <span>TRAI Header / ID:</span>
            <strong class="text-slate-700">YOJNAV (DLT Approved)</strong>
          </div>
          <div class="flex items-center justify-between">
            <span>Status:</span>
            <strong class="text-blue-700">{{ channelsAvailable.sms.is_configured ? 'Commercial Gateway Active' : 'Simulated Gateway Active' }}</strong>
          </div>
        </div>
      </div>

      <!-- IN-APP CONSOLE & LANGUAGE -->
      <div class="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm flex flex-col justify-between space-y-4">
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <div class="p-2.5 bg-purple-50 text-purple-700 rounded-2xl">
              <Bell class="w-6 h-6" />
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input 
                type="checkbox" 
                :checked="prefs.in_app_enabled"
                @change="handleChannelToggle('in_app')"
                class="sr-only peer"
              >
              <div class="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:width-5 after:transition-all peer-checked:bg-purple-600"></div>
            </label>
          </div>

          <div>
            <h3 class="font-bold text-slate-900 text-base">In-App Notification Console</h3>
            <p class="text-xs text-slate-500 mt-1">
              Active alerts inside the web portal whenever you log in or check saved scholarship applications.
            </p>
          </div>
        </div>

        <!-- Language Selector -->
        <div class="pt-3 border-t border-slate-100 space-y-1.5">
          <label class="text-[11px] font-bold text-slate-500 uppercase">Notification Language Preference</label>
          <div class="grid grid-cols-3 gap-1.5 bg-slate-100 p-1 rounded-xl">
            <button
              @click="prefs.preferred_language = 'en'; savePreferences();"
              class="py-1 text-xs font-bold rounded-lg transition-all"
              :class="prefs.preferred_language === 'en' ? 'bg-white text-indigo-700 shadow-xs' : 'text-slate-600 hover:text-slate-900'"
            >
              English
            </button>
            <button
              @click="prefs.preferred_language = 'mr'; savePreferences();"
              class="py-1 text-xs font-bold rounded-lg transition-all"
              :class="prefs.preferred_language === 'mr' ? 'bg-white text-indigo-700 shadow-xs' : 'text-slate-600 hover:text-slate-900'"
            >
              मराठी
            </button>
            <button
              @click="prefs.preferred_language = 'hi'; savePreferences();"
              class="py-1 text-xs font-bold rounded-lg transition-all"
              :class="prefs.preferred_language === 'hi' ? 'bg-white text-indigo-700 shadow-xs' : 'text-slate-600 hover:text-slate-900'"
            >
              हिंदी
            </button>
          </div>
        </div>
      </div>

    </div>

    <!-- 1-CLICK CITIZEN TEST DRIVE SECTION -->
    <div class="bg-gradient-to-r from-indigo-50 via-slate-50 to-emerald-50 rounded-3xl p-6 sm:p-8 border border-indigo-200 shadow-sm space-y-4">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span class="inline-flex items-center gap-1 text-[11px] font-bold uppercase tracking-wider text-indigo-700">
            <Sparkles class="w-3.5 h-3.5" />
            Interactive Demonstration
          </span>
          <h2 class="text-xl font-bold text-slate-900 mt-0.5">
            1-Click Citizen Test Drive
          </h2>
          <p class="text-xs sm:text-sm text-slate-600 mt-0.5">
            Test the transmission pipeline right now. Dispatches a verified sample alert in your preferred language ({{ prefs.preferred_language.toUpperCase() }}).
          </p>
        </div>

        <div class="flex items-center gap-2">
          <select 
            v-model="testChannel" 
            class="px-3 py-2 bg-white rounded-xl text-xs font-bold border border-slate-300 text-slate-700 shadow-xs focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="WHATSAPP">WhatsApp 🟢</option>
            <option value="SMS">SMS Gateway 📱</option>
            <option value="IN_APP">In-App Alert 🔔</option>
          </select>

          <button
            @click="handleSendTest()"
            :disabled="isTesting"
            class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition-all shadow-xs flex items-center gap-1.5 disabled:opacity-50"
          >
            <Send class="w-3.5 h-3.5" />
            <span>{{ isTesting ? 'Transmitting...' : 'Send Test Reminder 🔔' }}</span>
          </button>
        </div>
      </div>

      <!-- Test Result Alert -->
      <div v-if="testResult" class="p-4 rounded-2xl text-xs font-medium space-y-1" :class="testResult.success ? 'bg-emerald-100 text-emerald-950 border border-emerald-300' : 'bg-rose-100 text-rose-950 border border-rose-300'">
        <div class="font-bold flex items-center gap-1.5">
          <CheckCircle2 v-if="testResult.success" class="w-4 h-4 text-emerald-700" />
          <AlertCircle v-else class="w-4 h-4 text-rose-700" />
          <span>{{ testResult.message }}</span>
        </div>
        <div v-if="testResult.notification" class="text-[11px] text-emerald-800 bg-white/70 p-2.5 rounded-xl border border-emerald-200 mt-2 font-mono">
          <div>Provider: <strong>{{ testResult.notification.provider }}</strong></div>
          <div>Status: <strong>{{ testResult.notification.delivery_status }}</strong> (Message ID: {{ testResult.notification.provider_message_id }})</div>
          <div class="mt-1 pt-1 border-t border-emerald-200 font-sans text-slate-800">
            "{{ testResult.notification.message_body }}"
          </div>
        </div>
      </div>
    </div>

    <!-- STEP 3: THE 6 CANONICAL NOTIFICATION EVENTS WITH INTERACTIVE PREVIEWS -->
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <div>
          <div class="text-xs font-bold uppercase tracking-wider text-indigo-600">Step 3: Alert Customization</div>
          <h2 class="text-xl font-bold text-slate-900 mt-0.5">
            The 6 Canonical Deadline & Milestone Event Types
          </h2>
          <p class="text-xs sm:text-sm text-slate-500 mt-0.5">
            All reminders are grounded strictly in verified scheme records and statutory dates. Customize which alerts you wish to receive:
          </p>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div 
          v-for="evt in canonicalEvents" 
          :key="evt.key" 
          class="bg-white rounded-3xl p-5 border border-slate-200 shadow-sm flex flex-col justify-between space-y-3"
        >
          <div class="space-y-2">
            <div class="flex items-start justify-between gap-2">
              <h4 class="font-bold text-sm text-slate-900">
                {{ evt.title[prefs.preferred_language] }}
              </h4>
              <label class="relative inline-flex items-center cursor-pointer shrink-0">
                <input 
                  type="checkbox" 
                  v-model="prefs[evt.field]"
                  @change="savePreferences()"
                  class="sr-only peer"
                >
                <div class="w-9 h-5 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-emerald-600"></div>
              </label>
            </div>

            <p class="text-[11px] text-slate-500">
              <strong class="text-indigo-700">Trigger:</strong> {{ evt.trigger }}
            </p>

            <!-- Trilingual WhatsApp Chat Bubble Preview -->
            <div class="bg-[#e7fedb] border border-[#c4e6b5] p-3 rounded-2xl text-[11px] text-slate-800 leading-relaxed shadow-2xs relative">
              <div class="flex items-center justify-between text-[10px] text-emerald-800 font-bold mb-1 pb-1 border-b border-emerald-200/50">
                <span>YOJNAVIA Verified Alert ({{ prefs.preferred_language.toUpperCase() }})</span>
                <span class="flex items-center gap-0.5 text-emerald-700">
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
    <div class="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-6">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-5">
        <div>
          <div class="text-xs font-bold uppercase tracking-wider text-indigo-600">Telemetry & Audit Log</div>
          <h2 class="text-xl font-bold text-slate-900 flex items-center gap-2 mt-0.5">
            <Clock class="w-5 h-5 text-indigo-600" />
            Notification Delivery History
          </h2>
          <p class="text-xs sm:text-sm text-slate-500 mt-1">
            Immutable log of all reminders dispatched, simulated, or suppressed due to opt-out policies.
          </p>
        </div>

        <!-- Filter Controls -->
        <div class="flex flex-wrap items-center gap-2">
          <select 
            v-model="historyFilterChannel" 
            @change="fetchHistory()"
            class="px-2.5 py-1.5 bg-slate-50 rounded-xl text-xs font-bold border border-slate-200 text-slate-700 focus:outline-none"
          >
            <option value="ALL">All Channels</option>
            <option value="WHATSAPP">WhatsApp</option>
            <option value="SMS">SMS Gateway</option>
            <option value="IN_APP">In-App</option>
          </select>

          <select 
            v-model="historyFilterStatus" 
            @change="fetchHistory()"
            class="px-2.5 py-1.5 bg-slate-50 rounded-xl text-xs font-bold border border-slate-200 text-slate-700 focus:outline-none"
          >
            <option value="ALL">All Statuses</option>
            <option value="SIMULATED">Simulated</option>
            <option value="DELIVERED">Delivered</option>
            <option value="SENT">Sent</option>
            <option value="OPTED_OUT">Opted Out</option>
            <option value="FAILED">Failed</option>
          </select>

          <button
            @click="fetchHistory()"
            :disabled="isHistoryLoading"
            class="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 transition-colors"
            title="Refresh logs"
          >
            <RefreshCw class="w-3.5 h-3.5" :class="{ 'animate-spin': isHistoryLoading }" />
          </button>
        </div>
      </div>

      <!-- History Table -->
      <div v-if="historyLogs.length === 0" class="text-center py-12 text-slate-400 space-y-2">
        <Bell class="w-10 h-10 mx-auto text-slate-300" />
        <div class="text-sm font-bold text-slate-600">No notifications sent yet</div>
        <p class="text-xs text-slate-400 max-w-sm mx-auto">
          Click "Send Test Reminder 🔔" above or run the background scanner to trigger scheduled reminders.
        </p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full text-left text-xs border-collapse">
          <thead>
            <tr class="border-b border-slate-200 text-slate-400 uppercase text-[10px] font-bold">
              <th class="py-2.5 px-3">Channel</th>
              <th class="py-2.5 px-3">Event Type</th>
              <th class="py-2.5 px-3">Recipient</th>
              <th class="py-2.5 px-3">Lang</th>
              <th class="py-2.5 px-3">Status</th>
              <th class="py-2.5 px-3">Provider ID</th>
              <th class="py-2.5 px-3">Sent Time</th>
              <th class="py-2.5 px-3 text-right">Details</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 font-medium">
            <template v-for="log in historyLogs" :key="log.id">
              <tr class="hover:bg-slate-50/80 transition-colors">
                <td class="py-3 px-3">
                  <span class="inline-flex items-center gap-1 font-bold text-slate-800">
                    <span v-if="log.channel === 'WHATSAPP'">🟢 WA</span>
                    <span v-else-if="log.channel === 'SMS'">📱 SMS</span>
                    <span v-else>🔔 InApp</span>
                  </span>
                </td>
                <td class="py-3 px-3 font-bold text-slate-900">
                  {{ log.event_type }}
                </td>
                <td class="py-3 px-3 font-mono text-slate-600 text-[11px]">
                  {{ log.recipient }}
                </td>
                <td class="py-3 px-3">
                  <span class="px-1.5 py-0.5 rounded bg-slate-100 text-[10px] font-bold uppercase text-slate-700">
                    {{ log.language }}
                  </span>
                </td>
                <td class="py-3 px-3">
                  <span 
                    class="px-2 py-0.5 rounded-full text-[10px] font-extrabold border"
                    :class="getStatusBadgeClass(log.delivery_status)"
                  >
                    {{ log.delivery_status }}
                  </span>
                </td>
                <td class="py-3 px-3 font-mono text-slate-500 text-[10px]">
                  {{ log.provider_message_id || '—' }}
                </td>
                <td class="py-3 px-3 text-slate-500 whitespace-nowrap">
                  {{ formatDate(log.sent_at || log.created_at) }}
                </td>
                <td class="py-3 px-3 text-right">
                  <button
                    @click="expandedLogId = expandedLogId === log.id ? null : log.id"
                    class="text-indigo-600 hover:text-indigo-800 font-bold"
                  >
                    {{ expandedLogId === log.id ? 'Hide' : 'View' }}
                  </button>
                </td>
              </tr>

              <!-- Expanded Log Message View -->
              <tr v-if="expandedLogId === log.id" class="bg-indigo-50/40">
                <td colspan="8" class="p-4 space-y-2 text-xs">
                  <div class="font-bold text-indigo-950 flex items-center justify-between">
                    <span>Message Subject: {{ log.title }}</span>
                    <span class="text-[10px] text-slate-500 font-mono">Idempotency Key: {{ log.idempotency_key }}</span>
                  </div>
                  <div class="p-3 bg-white rounded-xl border border-indigo-100 text-slate-800 font-sans leading-relaxed">
                    {{ log.message_body }}
                  </div>
                  <div v-if="log.error_message" class="text-rose-700 font-bold text-[11px]">
                    Error: {{ log.error_message }}
                  </div>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>

    <!-- MOBILE NUMBER VERIFICATION MODAL -->
    <div v-if="isVerifyModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
      <div class="bg-white rounded-3xl max-w-md w-full p-6 sm:p-8 shadow-2xl border border-slate-200 space-y-6">
        <div class="flex items-center justify-between border-b border-slate-100 pb-3">
          <h3 class="font-extrabold text-slate-900 text-lg flex items-center gap-2">
            <Phone class="w-5 h-5 text-emerald-600" />
            Verify Citizen Mobile Number
          </h3>
          <button @click="isVerifyModalOpen = false" class="text-slate-400 hover:text-slate-600 text-sm">✕</button>
        </div>

        <div v-if="verifyError" class="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-bold">
          {{ verifyError }}
        </div>

        <!-- Phone input step -->
        <div v-if="!otpSent" class="space-y-4">
          <p class="text-xs text-slate-500">
            Enter your 10-digit Indian mobile number to enable WhatsApp and SMS deadline alerts.
          </p>

          <div class="space-y-1">
            <label class="text-[11px] font-bold text-slate-700 uppercase">Mobile Number</label>
            <div class="flex items-center">
              <span class="px-3 py-2.5 bg-slate-100 border border-r-0 border-slate-300 rounded-l-xl text-xs font-bold text-slate-600">+91</span>
              <input 
                type="text" 
                v-model="inputPhone"
                placeholder="9876543210"
                class="w-full px-3 py-2.5 bg-white border border-slate-300 rounded-r-xl text-xs font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
            </div>
          </div>

          <button
            @click="handleSendOtp()"
            :disabled="isVerifying"
            class="w-full py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold transition-all shadow-xs disabled:opacity-50"
          >
            {{ isVerifying ? 'Sending Code...' : 'Send Verification OTP' }}
          </button>
        </div>

        <!-- OTP verification step -->
        <div v-else class="space-y-4">
          <p class="text-xs text-slate-500">
            A 6-digit verification code has been sent to <strong>+91 {{ inputPhone }}</strong>.
          </p>

          <div v-if="demoOtpCode" class="p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-900">
            <strong>Demo Mode OTP:</strong> Use code <code class="font-extrabold text-indigo-700 bg-white px-1.5 py-0.5 rounded border border-amber-300">{{ demoOtpCode }}</code> (or standard code <code>123456</code>).
          </div>

          <div class="space-y-1">
            <label class="text-[11px] font-bold text-slate-700 uppercase">6-Digit Code</label>
            <input 
              type="text" 
              v-model="inputOtp"
              placeholder="123456"
              maxlength="6"
              class="w-full px-3 py-2.5 bg-white border border-slate-300 rounded-xl text-center text-lg font-mono font-bold tracking-widest text-slate-900 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            >
          </div>

          <div class="flex items-center gap-2">
            <button
              @click="otpSent = false"
              class="w-1/2 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold transition-all"
            >
              Back
            </button>
            <button
              @click="handleVerifyOtp()"
              :disabled="isVerifying"
              class="w-1/2 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold transition-all shadow-xs disabled:opacity-50"
            >
              {{ isVerifying ? 'Verifying...' : 'Confirm & Activate' }}
            </button>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>
