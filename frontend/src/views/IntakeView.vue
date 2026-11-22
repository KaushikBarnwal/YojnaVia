<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useStudentStore } from '../stores/studentStore';
import PersonaBar from '../components/PersonaBar.vue';
import { intakeApi } from '../services/api';
import { t } from '../utils/i18n';
import { speakText, stopSpeaking, isSpeaking, speakingId, speakingLang } from '../utils/speech';
import { showToast } from '../utils/toast';
import { 
  Send, 
  Sparkles, 
  Bot, 
  User, 
  ArrowRight, 
  ShieldCheck, 
  Cpu, 
  AlertCircle,
  RotateCcw,
  Edit3,
  X,
  Award,
  CheckCircle2,
  Mic,
  Square,
  Volume2,
  Radio,
  RefreshCw
} from '@lucide/vue';

const store = useStudentStore();
const router = useRouter();
const route = useRoute();
const inputMessage = ref('');
const chatInputEl = ref<HTMLInputElement | null>(null);

onMounted(() => {
  if (route.query.voice === 'true') {
    startRecording();
  }
});

// Edit field modal state
const isEditModalOpen = ref(false);
const editingFieldKey = ref('age');
const editingFieldValue = ref<any>('');

// Voice Intake State (Speech-to-Text directly into message box)
const isRecording = ref(false);
const recordingDuration = ref(0);
const mediaRecorder = ref<MediaRecorder | null>(null);
const speechRecognition = ref<any>(null);
const audioChunks = ref<Blob[]>([]);
const timerInterval = ref<any>(null);
const isTranscribing = ref(false);
const voiceError = ref('');
const selectedVoiceLang = ref<'unknown' | 'mr-IN' | 'hi-IN'>('unknown');
const voiceTranscript = ref('');
const detectedLanguage = ref('mr-IN');

// Audio Speech Synthesis (Listen in Hindi, English, Marathi)
function listenMessage(text: string, lang: 'en' | 'hi' | 'mr', msgIndex: number) {
  speakText(text, lang, `intake-msg-${msgIndex}`);
}

const formattedDuration = computed(() => {
  const m = Math.floor(recordingDuration.value / 60);
  const s = recordingDuration.value % 60;
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
});

async function startRecording() {
  voiceError.value = '';
  audioChunks.value = [];
  recordingDuration.value = 0;

  // 1. Try Browser Web Speech API for instantaneous transcription directly into input
  const SpeechRec = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
  if (SpeechRec) {
    try {
      const recognition = new SpeechRec();
      recognition.continuous = true;
      recognition.interimResults = true;
      if (selectedVoiceLang.value === 'mr-IN') {
        recognition.lang = 'mr-IN';
      } else if (selectedVoiceLang.value === 'hi-IN') {
        recognition.lang = 'hi-IN';
      } else {
        recognition.lang = 'en-IN';
      }

      const initialText = inputMessage.value ? inputMessage.value.trim() + ' ' : '';

      recognition.onresult = (e: any) => {
        let finalStr = '';
        let interimStr = '';
        for (let i = e.resultIndex; i < e.results.length; i++) {
          if (e.results[i].isFinal) {
            finalStr += e.results[i][0].transcript;
          } else {
            interimStr += e.results[i][0].transcript;
          }
        }
        inputMessage.value = (initialText + finalStr + (interimStr ? ' ' + interimStr : '')).trim();
      };

      recognition.onerror = (err: any) => {
        console.warn('SpeechRecognition error:', err);
      };

      recognition.onend = () => {
        isRecording.value = false;
        clearInterval(timerInterval.value);
      };

      recognition.start();
      speechRecognition.value = recognition;
      isRecording.value = true;
      timerInterval.value = setInterval(() => {
        recordingDuration.value++;
        if (recordingDuration.value >= 60) {
          stopRecording();
        }
      }, 1000);
      return;
    } catch (err) {
      console.warn('Web Speech API could not start, falling back to MediaRecorder:', err);
    }
  }

  // 2. Fallback to MediaRecorder & backend Whisper transcription
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream);
    mediaRecorder.value = recorder;

    recorder.ondataavailable = (e) => {
      if (e.data && e.data.size > 0) {
        audioChunks.value.push(e.data);
      }
    };

    recorder.onstop = async () => {
      clearInterval(timerInterval.value);
      stream.getTracks().forEach((track) => track.stop());
      if (audioChunks.value.length > 0) {
        const mime = recorder.mimeType || 'audio/webm';
        const audioBlob = new Blob(audioChunks.value, { type: mime });
        await processAudioUpload(audioBlob);
      }
    };

    recorder.start(250);
    isRecording.value = true;
    timerInterval.value = setInterval(() => {
      recordingDuration.value++;
      if (recordingDuration.value >= 60) {
        stopRecording();
      }
    }, 1000);
  } catch (err: any) {
    voiceError.value = 'Microphone access denied or audio device not found. You can test using the 1-Click Demo Voice below.';
  }
}

function stopRecording() {
  if (speechRecognition.value) {
    try {
      speechRecognition.value.stop();
    } catch (e) {}
    speechRecognition.value = null;
    isRecording.value = false;
    clearInterval(timerInterval.value);
    nextTick(() => {
      if (chatInputEl.value) chatInputEl.value.focus();
    });
    showToast('Speech recorded in message box! Press Enter or Send.', 'success');
    return;
  }
  if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
    mediaRecorder.value.stop();
    isRecording.value = false;
  }
}

function cancelRecording() {
  if (speechRecognition.value) {
    try {
      speechRecognition.value.abort();
    } catch (e) {}
    speechRecognition.value = null;
    isRecording.value = false;
    clearInterval(timerInterval.value);
  }
  if (mediaRecorder.value && mediaRecorder.value.state !== 'inactive') {
    clearInterval(timerInterval.value);
    mediaRecorder.value.stop();
    isRecording.value = false;
    audioChunks.value = [];
  }
}

async function processAudioUpload(audioSource: Blob | 'marathi' | 'hindi') {
  isTranscribing.value = true;
  voiceError.value = '';
  try {
    const formData = new FormData();
    formData.append('session_token', store.sessionToken);
    formData.append('language_code', selectedVoiceLang.value);

    if (typeof audioSource === 'string') {
      formData.append('is_demo', 'true');
      formData.append('demo_scenario', audioSource);
    } else {
      const ext = audioSource.type.includes('wav') ? 'wav' : 'webm';
      formData.append('audio', audioSource, `citizen_voice.${ext}`);
    }

    const res = await intakeApi.voiceIntake(formData);
    if (res.data.is_sensitive_refusal) {
      voiceError.value = res.data.reply;
      return;
    }

    const transcript = (res.data.transcript || '').trim();
    if (transcript) {
      if (inputMessage.value.trim()) {
        inputMessage.value = `${inputMessage.value.trim()} ${transcript}`;
      } else {
        inputMessage.value = transcript;
      }
      voiceTranscript.value = transcript;
      detectedLanguage.value = res.data.detected_language || 'mr-IN';
      nextTick(() => {
        if (chatInputEl.value) {
          chatInputEl.value.focus();
        }
      });
      showToast('Voice transcribed into message box! Press Enter or Send to submit.', 'success');
    } else {
      voiceError.value = 'No speech was detected. Please try speaking again.';
    }
  } catch (err: any) {
    voiceError.value =
      err?.response?.data?.error?.message ||
      err?.response?.data?.error ||
      'Transcription failed. Please try speaking again.';
  } finally {
    isTranscribing.value = false;
  }
}



const samplePrompts = [
  "I am 21, from Sangli, Maharashtra, studying B.Tech Mechanical Engineering, and my family's annual income is around ₹1.2 Lakhs.",
  "I am an OBC student from Nashik in MCA. Our annual household income is ₹2.1 Lakhs, staying in a rented hostel.",
  "I am an SC student from Solapur doing Civil Diploma. Family income is ₹65,000 per year.",
  "I am an Open category girl student from Pune studying B.Pharm. Family income is ₹3.5 Lakhs, admitted via CAP round."
];

const fieldLabels: Record<string, string> = {
  age: "Age",
  state: "State",
  district: "District",
  occupation: "Occupation",
  education_level: "Education Level",
  income_band: "Annual Household Income Band",
  social_category: "Social Category (Volunteered)",
  disability_status: "Disability Status (Volunteered)",
  family_members: "Family Members"
};

const incomeBandOptions = [
  { value: "below_1_lakh", label: "Below ₹1 Lakh" },
  { value: "1_to_2_5_lakh", label: "₹1 – 2.5 Lakh" },
  { value: "2_5_to_5_lakh", label: "₹2.5 – 5 Lakh" },
  { value: "5_to_8_lakh", label: "₹5 – 8 Lakh" },
  { value: "above_8_lakh", label: "Above ₹8 Lakh" },
];

const educationOptions = [
  { value: "undergraduate", label: "Undergraduate (B.Tech / B.Sc / BA / B.Com)" },
  { value: "postgraduate", label: "Postgraduate (MCA / M.Tech / MBA / M.Sc)" },
  { value: "diploma", label: "Polytechnic Diploma" },
  { value: "12th_pass", label: "12th Pass / Junior College" },
  { value: "10th_pass", label: "10th Pass" },
  { value: "doctorate", label: "Doctorate (Ph.D)" },
  { value: "other", label: "Other" }
];

const socialCategoryOptions = [
  { value: "general", label: "General / Open" },
  { value: "obc", label: "Other Backward Class (OBC)" },
  { value: "sc", label: "Scheduled Caste (SC)" },
  { value: "st", label: "Scheduled Tribe (ST)" },
  { value: "ews", label: "Economically Weaker Section (EWS)" },
  { value: "vjnt", label: "VJNT (Vimukta Jati & Nomadic Tribes)" },
  { value: "sbc", label: "Special Backward Class (SBC)" },
  { value: "prefer_not_to_say", label: "Prefer Not to Say" }
];

const progressPercentage = computed(() => {
  const total = store.intakeState?.total_count || 1;
  const known = store.intakeState?.known_count || 0;
  return Math.min(100, Math.round((known / total) * 100));
});

const isEligibilityReady = computed(() => {
  return store.nextQuestion === null && (store.evaluatedSchemes.length > 0 || store.evaluationSummary !== null);
});

async function handleSendMessage() {
  if (!inputMessage.value.trim() || store.isLoading) return;
  const msg = inputMessage.value;
  inputMessage.value = '';
  await store.sendIntakeMessage(msg);
}

function handleUsePrompt(prompt: string) {
  inputMessage.value = prompt;
}

function handleSendChip(chipText: string) {
  store.sendIntakeMessage(chipText);
}

function openEditModal(fieldKey: string) {
  editingFieldKey.value = fieldKey;
  const currentVal = store.intakeState?.fields?.[fieldKey]?.value;
  editingFieldValue.value = currentVal !== null && currentVal !== undefined ? currentVal : '';
  isEditModalOpen.value = true;
}

watch(editingFieldKey, (newKey) => {
  const currentVal = store.intakeState?.fields?.[newKey]?.value;
  editingFieldValue.value = currentVal !== null && currentVal !== undefined ? currentVal : '';
});

async function handleSaveCorrection() {
  if (editingFieldValue.value === '' || editingFieldValue.value === null) return;
  let val = editingFieldValue.value;
  if (editingFieldKey.value === 'age') {
    val = parseInt(val, 10);
  } else if (editingFieldKey.value === 'disability_status') {
    val = val === 'true' || val === true;
  }
  await store.correctIntakeField(editingFieldKey.value, val);
  isEditModalOpen.value = false;
}

async function handleRestart() {
  if (confirm("Restart conversational discovery? All conversation turns will be reset.")) {
    await store.restartIntake();
  }
}

function proceedToSchemes() {
  router.push('/schemes');
}

function formatFieldValue(key: string, value: any): string {
  if (value === null || value === undefined || value === '') return 'Not provided';
  if (key === 'income_band') {
    const found = incomeBandOptions.find(o => o.value === value);
    return found ? found.label : String(value);
  }
  if (key === 'education_level') {
    const found = educationOptions.find(o => o.value === value);
    return found ? found.label : String(value);
  }
  if (key === 'social_category') {
    const found = socialCategoryOptions.find(o => o.value === value);
    return found ? found.label : String(value);
  }
  if (typeof value === 'boolean') {
    return value ? 'Yes' : 'No';
  }
  if (key === 'family_members' && Array.isArray(value)) {
    return `${value.length} member(s)`;
  }
  return String(value);
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <!-- Demo Persona Bar -->
    <PersonaBar />

    <!-- Hero Header -->
    <div class="text-center max-w-3xl mx-auto mb-6">
      <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-md bg-[#FFFBEB] text-[#92400E] border-[1.5px] border-[#0B132B] shadow-[1.5px_1.5px_0_0_#0B132B] text-[11px] font-black uppercase tracking-wider mb-2.5">
        <Sparkles class="w-3.5 h-3.5 text-[#D97706] fill-current" />
        <span>Sovereign Welfare Intelligence • 100% Deterministic Rules</span>
      </div>
      <h1 class="text-2xl sm:text-4xl font-black text-[#0B132B] tracking-tight">
        Discover Government Schemes & Scholarships
      </h1>
      <p class="text-slate-700 text-xs sm:text-sm mt-1.5 font-medium max-w-xl mx-auto">
        पात्रतेपासून थेट लाभापर्यंत — Speak or type your details in Marathi, Hindi, or English to unlock verified Maharashtra welfare entitlements.
      </p>
    </div>

    <!-- Intake Progress Indicator Bar -->
    <div class="bg-white rounded-2xl border-[1.5px] border-[#0B132B] shadow-[2.5px_2.5px_0_0_#0B132B] p-4 mb-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-xl bg-[#0B132B] text-white flex items-center justify-center font-black text-xs shrink-0 shadow-[1px_1px_0_0_#D97706]">
          {{ progressPercentage }}%
        </div>
        <div>
          <div class="text-xs font-bold text-slate-900">
            Profile Completion: <span class="text-[#D97706] font-black">{{ store.intakeState?.known_count || 0 }}</span> of <span class="text-slate-700">{{ store.intakeState?.total_count || 1 }}</span> statutory criteria
          </div>
          <div class="w-36 sm:w-48 bg-slate-200 rounded-full h-2 overflow-hidden mt-1 border border-slate-300">
            <div 
              class="bg-[#D97706] h-2 rounded-full transition-all duration-500"
              :style="{ width: `${progressPercentage}%` }"
            ></div>
          </div>
        </div>
      </div>
      
      <div class="flex items-center gap-2 self-end sm:self-auto">
        <span 
          class="text-xs font-black px-3 py-1 rounded-full border-[1.5px] border-[#0B132B] inline-flex items-center gap-1.5 shadow-[1px_1px_0_0_#0B132B]"
          :class="isEligibilityReady ? 'bg-[#ECFDF5] text-[#065F46]' : 'bg-[#FFFBEB] text-[#92400E]'"
        >
          <span class="w-2 h-2 rounded-full" :class="isEligibilityReady ? 'bg-[#059669]' : 'bg-[#D97706] animate-ping'"></span>
          {{ isEligibilityReady ? 'Ready for Matching' : 'Gathering Criteria' }}
        </span>
        <button
          @click="handleRestart"
          title="Reset conversation"
          class="neo-btn neo-btn-paper text-xs px-2.5 py-1 text-slate-700 hover:text-red-700"
        >
          <RotateCcw class="w-3 h-3" />
          <span>Reset</span>
        </button>
      </div>
    </div>

    <!-- Eligibility Ready Notification Bar -->
    <div 
      v-if="isEligibilityReady"
      class="mb-5 bg-[#0B132B] border-[1.5px] border-[#0B132B] rounded-2xl px-5 py-4 text-white shadow-[3px_3px_0_0_#D97706] flex flex-col sm:flex-row items-center justify-between gap-3 animate-in fade-in"
    >
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-[#D97706] text-white flex items-center justify-center shrink-0 border border-white/20 shadow-[1px_1px_0_0_#060A14]">
          <Award class="w-5 h-5" />
        </div>
        <div>
          <div class="text-sm sm:text-base font-black">
            Matching Complete! {{ store.evaluationSummary?.likely_eligible || 0 }} eligible scholarships found
          </div>
          <div class="text-xs text-amber-200/90 font-medium">
            Verified against authentic Maharashtra Government Resolutions (GRs)
          </div>
        </div>
      </div>
      <button
        @click="proceedToSchemes"
        class="neo-btn neo-btn-saffron px-4 py-2 text-xs sm:text-sm shadow-[2px_2px_0_0_#FFFFFF] shrink-0"
      >
        <span>View Matched Schemes</span>
        <ArrowRight class="w-4 h-4" />
      </button>
    </div>

    <!-- Main Grid: Conversational Chat Interface (7 cols) & Extracted Profile (5 cols) -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
      
      <!-- Conversational Chat Interface -->
      <div class="lg:col-span-7 bg-white rounded-2xl border-[1.5px] border-[#0B132B] shadow-[3px_3px_0_0_#0B132B] flex flex-col h-[540px] sm:h-[650px] overflow-hidden">
        
        <!-- Chat Header -->
        <div class="px-4 py-3 bg-[#0B132B] text-white border-b-[1.5px] border-[#0B132B] flex items-center justify-between">
          <div class="flex items-center gap-2.5">
            <div class="w-8 h-8 rounded-xl bg-[#D97706] text-white border border-white/20 flex items-center justify-center shadow-[1px_1px_0_0_#060A14]">
              <Bot class="w-4 h-4" />
            </div>
            <div>
              <div class="text-sm font-black tracking-tight text-white">YojnaVia Sovereign Navigator</div>
              <div class="text-[11px] text-amber-300 flex items-center gap-1 font-bold">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                Official Maharashtra Scheme Guide
              </div>
            </div>
          </div>
          <div class="flex items-center gap-2">
          </div>
        </div>

        <!-- Chat Messages Area -->
        <div class="flex-1 p-4 overflow-y-auto space-y-3.5 bg-[#FBFBFA]">
          <div 
            v-for="(msg, index) in store.chatMessages" 
            :key="index"
            class="flex items-start gap-3"
            :class="msg.sender === 'user' ? 'flex-row-reverse' : ''"
          >
            <div 
              class="w-8 h-8 rounded-xl flex items-center justify-center shrink-0 text-white text-xs font-bold border-[1.5px] border-[#0B132B]"
              :class="msg.sender === 'user' ? 'bg-[#0B132B] shadow-[1px_1px_0_0_#D97706]' : (msg.isSensitiveRefusal ? 'bg-amber-600 shadow-[1px_1px_0_0_#0B132B]' : 'bg-[#D97706] shadow-[1px_1px_0_0_#0B132B]')"
            >
              <User v-if="msg.sender === 'user'" class="w-4 h-4" />
              <ShieldCheck v-else-if="msg.isSensitiveRefusal" class="w-4 h-4" />
              <Bot v-else class="w-4 h-4" />
            </div>

            <div 
              class="max-w-[85%] rounded-2xl p-3.5 text-sm"
              :class="msg.sender === 'user' 
                ? 'bg-[#0B132B] text-white rounded-tr-xs border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#D97706]' 
                : (msg.isSensitiveRefusal 
                    ? 'bg-amber-50 text-amber-950 border-[1.5px] border-amber-600 rounded-tl-xs shadow-[2px_2px_0_0_#0B132B]'
                    : 'bg-white text-slate-900 rounded-tl-xs border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#0B132B]')"
            >
              <p class="leading-relaxed whitespace-pre-line font-medium">{{ msg.text }}</p>

              <!-- Listen in English, Hindi, Marathi Controls -->
              <div 
                class="mt-2.5 pt-2 border-t flex flex-wrap items-center justify-between gap-1.5 text-[11px]"
                :class="msg.sender === 'user' ? 'border-white/10 text-slate-300' : 'border-slate-100 text-slate-600'"
              >
                <div class="flex items-center gap-1">
                  <Volume2 class="w-3.5 h-3.5" :class="isSpeaking && speakingId === 'intake-msg-' + index ? 'text-[#D97706] animate-pulse' : (msg.sender === 'user' ? 'text-amber-400' : 'text-slate-500')" />
                  <button
                    @click="listenMessage(msg.text, 'en', index)"
                    class="px-2 py-0.5 rounded text-[10px] font-black border transition-all cursor-pointer"
                    :class="isSpeaking && speakingId === 'intake-msg-' + index && speakingLang === 'en'
                      ? 'bg-[#D97706] text-white border-[#D97706] shadow-xs'
                      : (msg.sender === 'user' ? 'bg-white/10 hover:bg-white/20 text-white border-white/20' : 'bg-slate-100 hover:bg-slate-200 text-slate-800 border-slate-300')"
                  >
                    English
                  </button>
                  <button
                    @click="listenMessage(msg.text, 'hi', index)"
                    class="px-2 py-0.5 rounded text-[10px] font-black border transition-all cursor-pointer"
                    :class="isSpeaking && speakingId === 'intake-msg-' + index && speakingLang === 'hi'
                      ? 'bg-[#D97706] text-white border-[#D97706] shadow-xs'
                      : (msg.sender === 'user' ? 'bg-white/10 hover:bg-white/20 text-white border-white/20' : 'bg-slate-100 hover:bg-slate-200 text-slate-800 border-slate-300')"
                  >
                    हिंदी
                  </button>
                  <button
                    @click="listenMessage(msg.text, 'mr', index)"
                    class="px-2 py-0.5 rounded text-[10px] font-black border transition-all cursor-pointer"
                    :class="isSpeaking && speakingId === 'intake-msg-' + index && speakingLang === 'mr'
                      ? 'bg-[#D97706] text-white border-[#D97706] shadow-xs'
                      : (msg.sender === 'user' ? 'bg-white/10 hover:bg-white/20 text-white border-white/20' : 'bg-slate-100 hover:bg-slate-200 text-slate-800 border-slate-300')"
                  >
                    मराठी
                  </button>
                  <button
                    v-if="isSpeaking && speakingId === 'intake-msg-' + index"
                    @click="stopSpeaking"
                    class="ml-1 px-1.5 py-0.5 rounded text-[10px] font-black bg-red-600 text-white border border-red-700 hover:bg-red-700 cursor-pointer"
                    title="Stop speaking"
                  >
                    ⏹️
                  </button>
                </div>
              </div>

              <!-- Optional Error Banner if extraction failed or timed out -->
              <div v-if="msg.error" class="mt-2 text-xs text-amber-800 bg-amber-50 border-[1.5px] border-amber-300 rounded-lg p-2 flex items-center gap-1.5 font-bold">
                <AlertCircle class="w-3.5 h-3.5 text-amber-600 shrink-0" />
                <span>{{ msg.error }}</span>
              </div>
            </div>
          </div>

          <!-- Typing Indicator -->
          <div v-if="store.isLoading" class="flex items-center gap-2 text-slate-600 text-xs italic pl-11 py-1 font-semibold">
            <span class="w-2 h-2 rounded-full bg-[#D97706] animate-ping"></span>
            <span>Evaluating your facts against Maharashtra statutory rules...</span>
          </div>
        </div>

        <!-- Suggested Answers Chips (Dynamic from Next Question) -->
        <div 
          v-if="store.nextQuestion && store.nextQuestion.suggested_answers && store.nextQuestion.suggested_answers.length > 0"
          class="px-4 py-2.5 bg-[#FFFBEB] border-t-[1.5px] border-[#0B132B]"
        >
          <div class="text-[11px] font-black text-[#92400E] mb-1.5 flex items-center gap-1 uppercase tracking-wide">
            <Sparkles class="w-3 h-3 text-[#D97706]" />
            Suggested Quick Answers:
          </div>
          <div class="flex flex-wrap gap-1.5">
            <button
              v-for="(chip, chipIdx) in store.nextQuestion.suggested_answers"
              :key="chipIdx"
              @click="handleSendChip(chip)"
              class="neo-btn neo-btn-paper text-xs px-3 py-1 font-bold text-slate-800 hover:text-white hover:bg-[#0B132B]"
            >
              {{ chip }}
            </button>
          </div>
        </div>

        <!-- Starter Prompt Suggestions (When chat just started) -->
        <div 
          v-else-if="store.chatMessages.length <= 2"
          class="px-4 py-2 bg-slate-50 border-t-[1.5px] border-[#0B132B]/20 overflow-x-auto whitespace-nowrap scrollbar-none flex gap-2"
        >
          <button
            v-for="(sp, idx) in samplePrompts"
            :key="idx"
            @click="handleUsePrompt(sp)"
            class="neo-btn neo-btn-paper text-[11px] px-3 py-1 font-bold text-slate-700 hover:border-[#0B132B] shrink-0"
          >
            "{{ sp.substring(0, 36) }}..."
          </button>
        </div>

        <!-- Voice Mode & Quick Speech Demo Strip -->
        <div class="px-4 py-2 bg-[#F8FAFC] border-t-[1.5px] border-[#0B132B] flex flex-wrap items-center justify-between gap-2 text-xs">
          <div class="flex items-center gap-1.5">
            <span class="text-[11px] font-black text-[#0B132B] flex items-center gap-1">
              <Volume2 class="w-3.5 h-3.5 text-[#059669]" />
              <span>Voice:</span>
            </span>
            <div class="inline-flex rounded-lg bg-white p-0.5 border-[1.5px] border-[#0B132B] shadow-[1px_1px_0_0_#0B132B] text-[10px] font-black">
              <button 
                type="button"
                @click="selectedVoiceLang = 'unknown'" 
                class="px-2 py-0.5 rounded transition-all cursor-pointer"
                :class="selectedVoiceLang === 'unknown' ? 'bg-[#0B132B] text-white' : 'text-slate-600 hover:text-slate-900'"
              >
                Auto
              </button>
              <button 
                type="button"
                @click="selectedVoiceLang = 'mr-IN'" 
                class="px-2 py-0.5 rounded transition-all cursor-pointer"
                :class="selectedVoiceLang === 'mr-IN' ? 'bg-[#0B132B] text-white' : 'text-slate-600 hover:text-slate-900'"
              >
                मराठी
              </button>
              <button 
                type="button"
                @click="selectedVoiceLang = 'hi-IN'" 
                class="px-2 py-0.5 rounded transition-all cursor-pointer"
                :class="selectedVoiceLang === 'hi-IN' ? 'bg-[#0B132B] text-white' : 'text-slate-600 hover:text-slate-900'"
              >
                हिंदी
              </button>
            </div>
          </div>

          <!-- 1-Click Demo Voice Buttons -->
          <div class="flex items-center gap-1.5">
            <button
              type="button"
              @click="processAudioUpload('marathi')"
              :disabled="isTranscribing || isRecording"
              title="Test Marathi speech input with Pune, age 24, income 2 lakh"
              class="neo-btn neo-btn-paper px-2.5 py-1 text-[10px] font-black text-emerald-900 hover:bg-emerald-50"
            >
              <Radio class="w-2.5 h-2.5 text-emerald-600" />
              <span>🎙️ Marathi Voice</span>
            </button>

            <button
              type="button"
              @click="processAudioUpload('hindi')"
              :disabled="isTranscribing || isRecording"
              title="Test Hindi speech input"
              class="neo-btn neo-btn-paper px-2.5 py-1 text-[10px] font-black text-amber-900 hover:bg-amber-50"
            >
              <Radio class="w-2.5 h-2.5 text-amber-600" />
              <span>🎙️ Hindi Voice</span>
            </button>
          </div>
        </div>

        <!-- Voice Error Alert -->
        <div v-if="voiceError" class="mx-3 my-2 p-2.5 bg-rose-50 border-[1.5px] border-rose-600 rounded-xl text-xs text-rose-900 flex items-center justify-between gap-2 shadow-[1px_1px_0_0_#0B132B]">
          <div class="flex items-center gap-1.5 font-bold">
            <AlertCircle class="w-4 h-4 text-rose-600 shrink-0" />
            <span>{{ voiceError }}</span>
          </div>
          <button @click="voiceError = ''" class="text-rose-600 hover:text-rose-900 text-xs font-black">✕</button>
        </div>

        <!-- ACTIVE RECORDING BAR -->
        <div v-if="isRecording" class="p-2.5 bg-red-50 border-t-[1.5px] border-[#0B132B] flex items-center justify-between gap-3 animate-in fade-in">
          <div class="flex items-center gap-3">
            <div class="relative flex items-center justify-center">
              <span class="w-3.5 h-3.5 rounded-full bg-red-600 animate-ping absolute"></span>
              <span class="w-3 h-3 rounded-full bg-red-600 relative"></span>
            </div>
            <div>
              <div class="text-xs font-bold text-red-950 flex items-center gap-2">
                <span>Listening... (Speak your details)</span>
                <span class="font-mono bg-red-100 text-red-800 px-2 py-0.5 rounded text-[11px] font-extrabold border border-red-300">{{ formattedDuration }}</span>
              </div>
              <div class="text-[10px] text-red-700">Speech is transcribed directly into the message box below.</div>
            </div>
          </div>

          <div class="flex items-center gap-2 shrink-0">
            <button
              type="button"
              @click="cancelRecording()"
              class="neo-btn neo-btn-paper px-3 py-1.5 text-xs font-bold"
            >
              Cancel
            </button>
            <button
              type="button"
              @click="stopRecording()"
              class="neo-btn bg-red-600 hover:bg-red-700 text-white px-4 py-1.5 text-xs font-bold flex items-center gap-1.5"
            >
              <Square class="w-3.5 h-3.5 fill-current" />
              <span>Done Speaking</span>
            </button>
          </div>
        </div>

        <!-- TRANSCRIBING LOADER BAR -->
        <div v-if="isTranscribing" class="p-2.5 bg-amber-50 border-t-[1.5px] border-[#0B132B] flex items-center justify-center gap-2 text-xs font-bold text-amber-950 animate-in fade-in">
          <RefreshCw class="w-4 h-4 text-[#D97706] animate-spin" />
          <span>Transcribing your speech into the message box...</span>
        </div>

        <!-- Normal Chat Input Form ALWAYS VISIBLE -->
        <form @submit.prevent="handleSendMessage" class="p-3 bg-white border-t-[1.5px] border-[#0B132B] flex items-center gap-2">
          <input
            ref="chatInputEl"
            v-model="inputMessage"
            data-chat-input
            type="text"
            placeholder="Speak with the mic or type your course, location, category, income..."
            class="flex-1 text-xs sm:text-sm px-4 py-2.5 rounded-xl border-[1.5px] border-[#0B132B] bg-[#FBFBFA] focus:outline-hidden focus:ring-2 focus:ring-amber-500/20 font-medium"
          />

          <!-- Microphone Recording Button (Toggles Start / Stop) -->
          <button
            type="button"
            @click="isRecording ? stopRecording() : startRecording()"
            :title="isRecording ? 'Stop Recording' : t('voice_start_record', store.locale)"
            :class="isRecording ? 'bg-red-600 text-white animate-pulse' : 'neo-btn-paper text-[#059669]'"
            class="neo-btn p-2.5 shrink-0"
          >
            <Mic v-if="!isRecording" class="w-4 h-4" />
            <Square v-else class="w-4 h-4 fill-current" />
          </button>

          <button
            type="submit"
            :disabled="!inputMessage.trim() || store.isLoading"
            class="neo-btn neo-btn-navy px-4 py-2.5 text-xs sm:text-sm text-white shrink-0 disabled:opacity-50"
          >
            <span>Send</span>
            <Send class="w-4 h-4" />
          </button>
        </form>
      </div>

      <!-- Real-Time Extracted Profile State & Action Card (5 cols) -->
      <div class="lg:col-span-5 space-y-4">
        <div class="bg-white rounded-2xl border-[1.5px] border-[#0B132B] shadow-[3px_3px_0_0_#0B132B] p-5">
          <div class="flex items-center justify-between pb-3 border-b-[1.5px] border-[#0B132B]/10">
            <div>
              <h2 class="text-sm sm:text-base font-black text-[#0B132B]">Live Verified Profile</h2>
              <p class="text-xs text-slate-500 font-medium">Synchronized with statutory rules</p>
            </div>
            <span 
              class="neo-stamp text-[10px]"
              :class="isEligibilityReady ? 'neo-stamp-emerald' : 'neo-stamp-amber'"
            >
              <CheckCircle2 v-if="isEligibilityReady" class="w-3.5 h-3.5 text-emerald-600" />
              <Cpu v-else class="w-3.5 h-3.5 text-[#D97706]" />
              {{ store.intakeState?.known_count || 0 }} Confirmed
            </span>
          </div>

          <!-- Structured Fields List -->
          <div class="divide-y divide-slate-100 text-sm mt-2 max-h-[460px] overflow-y-auto pr-1">
            <div 
              v-for="(label, key) in fieldLabels" 
              :key="key"
              class="py-2.5 flex items-start justify-between gap-2 border-[1.5px] border-[#0B132B]/15 bg-[#FBFBFA] rounded-xl p-2.5 my-1.5 hover:border-[#0B132B] transition-colors"
            >
              <div class="flex-1 min-w-0">
                <div class="text-[11px] text-slate-500 font-bold uppercase tracking-wide">{{ label }}</div>
                <div class="font-black text-slate-900 text-xs sm:text-sm flex items-center gap-1.5 mt-0.5">
                  <span class="truncate">{{ formatFieldValue(key, store.intakeState?.fields?.[key]?.value) }}</span>
                  
                  <!-- Clean Status Badges -->
                  <span 
                    v-if="store.intakeState?.fields?.[key]?.status === 'known'" 
                    class="neo-stamp neo-stamp-emerald text-[9px] px-1 py-0.2"
                  >
                    Verified
                  </span>
                  <span 
                    v-else
                    class="text-[11px] text-slate-400 font-normal italic"
                  >
                    Pending
                  </span>
                </div>
              </div>

              <!-- Inline Edit Button -->
              <button
                @click="openEditModal(key)"
                class="p-1.5 text-slate-600 hover:text-[#0B132B] hover:bg-white rounded-lg border border-slate-200 transition-colors mt-0.5 shadow-2xs"
                title="Edit this statutory detail"
              >
                <Edit3 class="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          <!-- Action Buttons Area -->
          <div class="mt-4 pt-4 border-t-[1.5px] border-[#0B132B]/10 space-y-2">
            <button
              @click="proceedToSchemes"
              class="neo-btn neo-btn-saffron w-full py-3 text-sm font-black flex items-center justify-center gap-2"
            >
              <span>Explore Matched Entitlements</span>
              <ArrowRight class="w-4 h-4" />
            </button>
            <p class="text-[11px] text-center text-slate-500 font-medium">
              100% deterministic evaluation based on Maharashtra Government Resolutions.
            </p>
          </div>
        </div>

        <!-- Privacy & Safety Note -->
        <div class="p-3.5 rounded-xl bg-[#FFFBEB] border-[1.5px] border-[#0B132B] shadow-[2px_2px_0_0_#0B132B] text-xs text-amber-950 flex items-start gap-2.5">
          <ShieldCheck class="w-5 h-5 text-[#D97706] shrink-0 mt-0.5" />
          <div class="space-y-0.5">
            <div class="font-black uppercase tracking-wider text-[11px]">Zero-Aadhaar Sovereign Policy</div>
            <p class="text-amber-900 leading-normal font-medium text-[11px]">
              YojnaVia never requests or records 12-digit Aadhaar numbers, OTPs, or bank passwords. All official filings occur on the official MahaDBT portal.
            </p>
          </div>
        </div>

      </div>

    </div>

    <!-- Edit / Correction Modal -->
    <div 
      v-if="isEditModalOpen"
      class="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4 animate-in fade-in"
    >
      <div class="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-slate-200">
        <div class="flex items-center justify-between pb-3 border-b border-slate-100">
          <div class="flex items-center gap-2 font-bold text-slate-900 text-base">
            <Edit3 class="w-4 h-4 text-indigo-600" />
            Edit / Correct Parameter
          </div>
          <button 
            @click="isEditModalOpen = false"
            class="text-slate-400 hover:text-slate-600 p-1 rounded-lg"
          >
            <X class="w-4 h-4" />
          </button>
        </div>

        <form @submit.prevent="handleSaveCorrection" class="space-y-4 mt-4">
          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">
              Field to Update:
            </label>
            <select 
              v-model="editingFieldKey"
              class="w-full text-sm border border-slate-300 rounded-xl px-3 py-2 bg-slate-50 text-slate-800 font-medium"
            >
              <option v-for="(lbl, k) in fieldLabels" :key="k" :value="k">
                {{ lbl }}
              </option>
            </select>
          </div>

          <!-- Dynamic Input Based on Field Type -->
          <div>
            <label class="block text-xs font-semibold text-slate-700 mb-1">
              Corrected Value:
            </label>

            <!-- Age Input -->
            <input 
              v-if="editingFieldKey === 'age'"
              v-model.number="editingFieldValue"
              type="number"
              min="0"
              max="120"
              placeholder="e.g. 21"
              class="w-full text-sm border border-slate-300 rounded-xl px-3.5 py-2 focus:ring-2 focus:ring-indigo-500"
              required
            />

            <!-- Income Band Input -->
            <select 
              v-else-if="editingFieldKey === 'income_band'"
              v-model="editingFieldValue"
              class="w-full text-sm border border-slate-300 rounded-xl px-3.5 py-2 focus:ring-2 focus:ring-indigo-500"
              required
            >
              <option value="" disabled>Select Annual Income Band</option>
              <option v-for="opt in incomeBandOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>

            <!-- Education Level Input -->
            <select 
              v-else-if="editingFieldKey === 'education_level'"
              v-model="editingFieldValue"
              class="w-full text-sm border border-slate-300 rounded-xl px-3.5 py-2 focus:ring-2 focus:ring-indigo-500"
              required
            >
              <option value="" disabled>Select Education Level</option>
              <option v-for="opt in educationOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>

            <!-- Social Category Input -->
            <select 
              v-else-if="editingFieldKey === 'social_category'"
              v-model="editingFieldValue"
              class="w-full text-sm border border-slate-300 rounded-xl px-3.5 py-2 focus:ring-2 focus:ring-indigo-500"
              required
            >
              <option value="" disabled>Select Social Category</option>
              <option v-for="opt in socialCategoryOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>

            <!-- Disability Status Input -->
            <select 
              v-else-if="editingFieldKey === 'disability_status'"
              v-model="editingFieldValue"
              class="w-full text-sm border border-slate-300 rounded-xl px-3.5 py-2 focus:ring-2 focus:ring-indigo-500"
              required
            >
              <option :value="false">No (False)</option>
              <option :value="true">Yes (True)</option>
            </select>

            <!-- Default String Input (State, District, Occupation) -->
            <input 
              v-else
              v-model="editingFieldValue"
              type="text"
              placeholder="Enter value..."
              class="w-full text-sm border border-slate-300 rounded-xl px-3.5 py-2 focus:ring-2 focus:ring-indigo-500"
              required
            />
          </div>

          <div class="text-[11px] text-slate-500 bg-slate-50 p-2.5 rounded-lg border border-slate-200">
            <strong>Note:</strong> User-confirmed values have 100% confidence and will never be overwritten by AI extraction.
          </div>

          <div class="flex items-center justify-end gap-2 pt-2">
            <button
              type="button"
              @click="isEditModalOpen = false"
              class="px-4 py-2 border border-slate-300 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="store.isLoading"
              class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold shadow-xs transition-colors"
            >
              Save & Confirm
            </button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>
