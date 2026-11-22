import { ref } from 'vue';

export type SpeechLang = 'en' | 'hi' | 'mr';

export const isSpeaking = ref(false);
export const speakingId = ref<string | null>(null);
export const speakingLang = ref<SpeechLang>('en');

let cachedVoices: SpeechSynthesisVoice[] = [];

function loadVoices(): SpeechSynthesisVoice[] {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
    return [];
  }
  const voices = window.speechSynthesis.getVoices();
  if (voices && voices.length > 0) {
    cachedVoices = voices;
  }
  return cachedVoices;
}

if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
  loadVoices();
  window.speechSynthesis.onvoiceschanged = () => {
    loadVoices();
  };
}

/**
 * Strips markdown symbols, asterisks, hash headers, urls, and brackets
 * so the synthetic voice sounds natural like a human reader.
 */
export function cleanTextForSpeech(text: string): string {
  if (!text) return '';
  return text
    .replace(/```[\s\S]*?```/g, '') // code blocks
    .replace(/`([^`]+)`/g, '$1') // inline code
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // links
    .replace(/[#*_~>]/g, ' ') // markdown formatting characters
    .replace(/[-•]\s+/g, ', ') // list bullets into breath pauses
    .replace(/₹\s*(\d+)/g, 'Rs $1') // currency reading
    .replace(/\s+/g, ' ')
    .trim();
}

/**
 * Finds the best matching voice for the target language.
 */
export function findVoiceForLanguage(lang: SpeechLang): { voice: SpeechSynthesisVoice | null; langCode: string } {
  const voices = loadVoices();

  if (lang === 'mr') {
    // 1. Native Marathi voice
    const mrVoice = voices.find(v => 
      v.lang.toLowerCase().startsWith('mr') || 
      v.name.toLowerCase().includes('marathi') ||
      v.name.toLowerCase().includes('मराठी')
    );
    if (mrVoice) {
      return { voice: mrVoice, langCode: mrVoice.lang || 'mr-IN' };
    }
    // 2. Fallback to Hindi Indian voice (shares Devanagari phonology, pronounces Marathi accurately)
    const hiVoice = voices.find(v => 
      v.lang.toLowerCase().startsWith('hi') || 
      v.name.toLowerCase().includes('hindi') || 
      v.name.toLowerCase().includes('हिन्दी')
    );
    if (hiVoice) {
      return { voice: hiVoice, langCode: hiVoice.lang || 'hi-IN' };
    }
    return { voice: null, langCode: 'mr-IN' };
  }

  if (lang === 'hi') {
    // 1. Native Hindi voice
    const hiVoice = voices.find(v => 
      v.lang.toLowerCase().startsWith('hi') || 
      v.name.toLowerCase().includes('hindi') || 
      v.name.toLowerCase().includes('हिन्दी') ||
      v.name.toLowerCase().includes('swara') ||
      v.name.toLowerCase().includes('madhur')
    );
    if (hiVoice) {
      return { voice: hiVoice, langCode: hiVoice.lang || 'hi-IN' };
    }
    // 2. Fallback to any Indian accent voice
    const inVoice = voices.find(v => v.lang.toLowerCase().includes('-in'));
    if (inVoice) {
      return { voice: inVoice, langCode: inVoice.lang };
    }
    return { voice: null, langCode: 'hi-IN' };
  }

  // English (default)
  // 1. Indian English voice (natural for Indian government terminology)
  const inEnVoice = voices.find(v => 
    v.lang.toLowerCase() === 'en-in' || 
    v.lang.toLowerCase() === 'en_in' ||
    v.name.toLowerCase().includes('india') ||
    v.name.toLowerCase().includes('heera') ||
    v.name.toLowerCase().includes('ravi')
  );
  if (inEnVoice) {
    return { voice: inEnVoice, langCode: inEnVoice.lang };
  }
  // 2. Generic English voice
  const genericEnVoice = voices.find(v => v.lang.toLowerCase().startsWith('en'));
  if (genericEnVoice) {
    return { voice: genericEnVoice, langCode: genericEnVoice.lang };
  }

  return { voice: null, langCode: 'en-IN' };
}

/**
 * Reads aloud text with the specified language voice.
 * If already speaking this item with this language, toggles off.
 */
export function speakText(
  rawText: string,
  lang: SpeechLang,
  id: string,
  callbacks?: { onEnd?: () => void; onError?: () => void }
): void {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
    alert('Speech synthesis is not supported in this browser.');
    return;
  }

  // If already speaking this item and language, clicking toggles off
  if (isSpeaking.value && speakingId.value === id && speakingLang.value === lang) {
    stopSpeaking();
    return;
  }

  stopSpeaking();

  const clean = cleanTextForSpeech(rawText);
  if (!clean) return;

  const utterance = new SpeechSynthesisUtterance(clean);
  const { voice, langCode } = findVoiceForLanguage(lang);

  if (voice) {
    utterance.voice = voice;
  }
  utterance.lang = langCode;
  utterance.rate = lang === 'en' ? 0.95 : 0.90; // Slightly slower for clear regional vernacular comprehension
  utterance.pitch = 1.0;

  isSpeaking.value = true;
  speakingId.value = id;
  speakingLang.value = lang;

  utterance.onend = () => {
    isSpeaking.value = false;
    speakingId.value = null;
    callbacks?.onEnd?.();
  };

  utterance.onerror = () => {
    isSpeaking.value = false;
    speakingId.value = null;
    callbacks?.onError?.();
  };

  window.speechSynthesis.speak(utterance);
}

export function stopSpeaking(): void {
  if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
  isSpeaking.value = false;
  speakingId.value = null;
}
