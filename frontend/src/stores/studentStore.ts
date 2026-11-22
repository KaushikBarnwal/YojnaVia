import { defineStore } from 'pinia';
import api, { intakeApi } from '../services/api';
import type {
  StudentProfile,
  EvaluatedScheme,
  EvaluationSummary,
  StackingBundle,
  DocumentNode,
  ApplicationRecord,
  ApplicationStatus,
  PersonaInfo,
  IntakeState,
  NextQuestion,
  AdminUser
} from '../types';

export const useStudentStore = defineStore('student', {
  state: () => ({
    sessionToken: localStorage.getItem('YojnaVia_session_token') || ('YojnaVia-' + Math.random().toString(36).substring(2, 10)),
    profile: null as StudentProfile | null,
    evaluationSummary: null as EvaluationSummary | null,
    evaluatedSchemes: [] as EvaluatedScheme[],
    stackingBundle: null as StackingBundle | null,
    documentGraph: {
      documents: [] as DocumentNode[],
      top_multiplier_document: null as DocumentNode | null,
      total_schemes_analyzed: 0
    },
    trackedApplications: [] as ApplicationRecord[],
    personas: [] as PersonaInfo[],
    activePersonaKey: '',
    isLoading: false,
    errorMessage: '',
    intakeState: null as IntakeState | null,
    nextQuestion: null as NextQuestion | null,
    intakeError: null as { code: string; message: string; retry_after?: number | null } | null,
    chatMessages: [
      {
        sender: 'assistant',
        text: 'Namaste! I am YojnaVia. Tell me about your situation, education, family income and district in Maharashtra (e.g. "I am 21, from Pune, studying MCA, family income around ₹2 lakh"), or choose a demo persona above to discover what benefits you qualify for.',
        structuredAnalysis: {
          understanding: 'Ready to evaluate Maharashtra welfare entitlements for your household.',
          key_statutory_finding: '100% deterministic rule matching against authentic Maharashtra Government Resolutions (GRs).',
          simple_explanation: 'Speak or type your current course, district, category and annual household income to discover all eligible scholarships and tuition fee waivers.',
          steps: [
            '1. State your current education level & district in Maharashtra',
            '2. Provide annual family income range and social category',
            '3. Review preflight document checklist & RTS Act processing SLAs'
          ],
          final_recommendation: 'Awaiting your criteria to calculate likely eligible welfare schemes.',
          next_action: 'Tap the mic or enter your details below.',
          engine_used: 'Groq Llama-3.3 (Primary) · Gemini Flash (Fallback)'
        }
      }
    ] as Array<{
      sender: 'user' | 'assistant';
      text: string;
      isSensitiveRefusal?: boolean;
      error?: string;
      structuredAnalysis?: any;
    }>,
    adminUser: (localStorage.getItem('YojnaVia_admin_user') ? JSON.parse(localStorage.getItem('YojnaVia_admin_user')!) : null) as AdminUser | null,
    adminToken: localStorage.getItem('YojnaVia_admin_token') || '',
    adminSchemes: [] as any[],
    locale: (localStorage.getItem('YojnaVia_locale') || 'en') as 'en' | 'mr' | 'hi'
  }),

  getters: {
    reEvaluationAlerts(state) {
      return state.trackedApplications.filter(a => a.needs_re_evaluation);
    }
  },

  actions: {
    setLocale(lang: 'en' | 'mr' | 'hi') {
      this.locale = lang;
      localStorage.setItem('YojnaVia_locale', lang);
    },

    async initSession() {
      if (!this.sessionToken) {
        this.sessionToken = 'YojnaVia-' + Math.random().toString(36).substring(2, 10);
        localStorage.setItem('YojnaVia_session_token', this.sessionToken);
      }
      await this.fetchPersonas();
      await this.fetchProfile();
      await this.fetchIntakeState();
      await this.fetchDocumentGraph();
      await this.fetchTracker();
    },

    async fetchIntakeState() {
      try {
        const res = await intakeApi.getState(this.sessionToken);
        this.intakeState = res.data.state;
        this.nextQuestion = res.data.next_question;
      } catch (err: any) {
        // Conversation session may not be started yet; ignore 404
      }
    },

    async fetchPersonas() {
      try {
        const res = await api.get('/profiles/personas/');
        this.personas = res.data.personas || [];
      } catch (err: any) {
        console.error('Failed to load personas:', err);
      }
    },

    async fetchProfile() {
      try {
        this.isLoading = true;
        const res = await api.get(`/profiles/me/?session_token=${this.sessionToken}`);
        this.profile = res.data.profile;
        if (res.data.session_token) {
          this.sessionToken = res.data.session_token;
          localStorage.setItem('YojnaVia_session_token', this.sessionToken);
        }
      } catch (err: any) {
        this.errorMessage = 'Failed to load student profile';
      } finally {
        this.isLoading = false;
      }
    },

    async loadPersona(key: string) {
      try {
        this.isLoading = true;
        this.activePersonaKey = key;
        const res = await api.post('/profiles/load_persona/', {
          persona_key: key,
          session_token: this.sessionToken
        });
        this.profile = res.data.profile;
        this.chatMessages.push({
          sender: 'assistant',
          text: `Loaded demo persona: ${this.profile?.name}. Profile attributes and verified data are now synchronized.`
        });
        await this.fetchIntakeState();
        await this.evaluateEligibility();
      } catch (err: any) {
        this.errorMessage = 'Failed to load persona';
      } finally {
        this.isLoading = false;
      }
    },

    async updateProfile(updatedData: Partial<StudentProfile>) {
      try {
        this.isLoading = true;
        const res = await api.put('/profiles/me/', {
          ...updatedData,
          session_token: this.sessionToken,
          is_confirmed: true
        });
        this.profile = res.data.profile;
        await this.fetchIntakeState();
        await this.evaluateEligibility();
      } catch (err: any) {
        this.errorMessage = 'Failed to update profile';
      } finally {
        this.isLoading = false;
      }
    },

    async sendIntakeMessage(message: string) {
      if (!message.trim()) return;
      if (!this.sessionToken) {
        this.sessionToken = 'YojnaVia-' + Math.random().toString(36).substring(2, 10);
        localStorage.setItem('YojnaVia_session_token', this.sessionToken);
      }
      this.chatMessages.push({ sender: 'user', text: message });
      this.isLoading = true;
      this.intakeError = null;
      try {
        const res = await intakeApi.chat(message, this.sessionToken);
        const data = res.data;

        const replyText = typeof data.reply === 'string' ? data.reply : 'I have recorded your details.';
        this.chatMessages.push({
          sender: 'assistant',
          text: replyText,
          isSensitiveRefusal: replyText.includes("don't share Aadhaar") || replyText.includes("Please don't share") || replyText.includes("Never enter your Aadhaar"),
          error: data.error?.message,
          structuredAnalysis: data.state?.structured_analysis
        });

        this.intakeState = data.state;
        this.nextQuestion = data.next_question;
        this.intakeError = data.error;

        // If deterministic eligibility result was calculated
        if (data.eligibility) {
          this.evaluationSummary = data.eligibility.summary;
          this.evaluatedSchemes = data.eligibility.results;
          this.stackingBundle = data.eligibility.stacking_bundle;
          await this.fetchTracker();
        }

        // Refresh underlying student profile
        await this.fetchProfile();
      } catch (err: any) {
        console.error('Intake chat error:', err);
        const serverError = err.response?.data?.error?.message;
        const msg = serverError || 'I encountered an issue connecting to the intake assistant. Please try typing again or edit your profile fields directly.';
        this.chatMessages.push({
          sender: 'assistant',
          text: msg
        });
      } finally {
        this.isLoading = false;
      }
    },

    async correctIntakeField(field: string, value: any) {
      try {
        this.isLoading = true;
        const res = await intakeApi.correct(this.sessionToken, field, value);
        this.intakeState = res.data.state;
        this.nextQuestion = res.data.next_question;
        this.chatMessages.push({
          sender: 'assistant',
          text: `I have updated your confirmed ${field.replace('_', ' ')} to "${value}".`
        });
        await this.fetchProfile();
        if (!this.nextQuestion) {
          await this.evaluateEligibility();
        }
      } catch (err: any) {
        this.errorMessage = err.response?.data?.error?.message || 'Failed to update field';
      } finally {
        this.isLoading = false;
      }
    },

    async restartIntake() {
      try {
        this.isLoading = true;
        const res = await intakeApi.restart(this.sessionToken);
        this.intakeState = res.data.state;
        this.nextQuestion = res.data.next_question;
        this.intakeError = null;
        this.chatMessages = [
          {
            sender: 'assistant',
            text: 'Session restarted. Tell me about your studies, family background, and living arrangement in Maharashtra.'
          }
        ];
        await this.fetchProfile();
      } catch (err: any) {
        this.errorMessage = 'Failed to restart intake';
      } finally {
        this.isLoading = false;
      }
    },

    async evaluateEligibility() {
      try {
        this.isLoading = true;
        const res = await api.post('/eligibility/evaluate/', {
          session_token: this.sessionToken
        });
        this.evaluationSummary = res.data.summary;
        this.evaluatedSchemes = res.data.results;
        this.stackingBundle = res.data.stacking_bundle;
        await this.fetchTracker();
      } catch (err: any) {
        this.errorMessage = 'Eligibility evaluation failed';
      } finally {
        this.isLoading = false;
      }
    },

    async fetchDocumentGraph() {
      try {
        const res = await api.get('/documents/dependency_graph/');
        this.documentGraph = res.data;
      } catch (err: any) {
        console.error('Failed to load document graph:', err);
      }
    },

    async fetchTracker() {
      try {
        const res = await api.get(`/tracker/?session_token=${this.sessionToken}`);
        this.trackedApplications = res.data.applications || [];
      } catch (err: any) {
        console.error('Failed to load tracked applications:', err);
      }
    },

    async saveSchemeToTracker(schemeCode: string, initialStatus: ApplicationStatus = 'NOT_STARTED') {
      try {
        const res = await api.post('/tracker/update/', {
          session_token: this.sessionToken,
          scheme_code: schemeCode,
          status: initialStatus
        });
        await this.fetchTracker();
        return res.data;
      } catch (err: any) {
        this.errorMessage = 'Failed to save scheme to application tracker';
      }
    },

    async updateTrackerStage(schemeCode: string, stage: string, completedDocs: string[] = [], refNo: string = '', notes: string = '') {
      return this.updateTrackerRecord({
        scheme_code: schemeCode,
        stage,
        completed_documents: completedDocs,
        application_reference_number: refNo,
        notes
      });
    },

    async updateTrackerRecord(payload: {
      scheme_code: string;
      status?: ApplicationStatus;
      stage?: string;
      application_reference_number?: string;
      applied_date?: string;
      submission_mode?: string;
      notes?: string;
      completed_documents?: string[];
    }) {
      try {
        const res = await api.post('/tracker/update/', {
          session_token: this.sessionToken,
          ...payload
        });
        await this.fetchTracker();
        return res.data;
      } catch (err: any) {
        this.errorMessage = 'Failed to update application tracker record';
      }
    },

    async acknowledgeReEvaluation(schemeCode?: string) {
      try {
        await api.post('/tracker/acknowledge_re_evaluation/', {
          session_token: this.sessionToken,
          scheme_code: schemeCode
        });
        await this.fetchTracker();
      } catch (err: any) {
        console.error('Failed to acknowledge re-evaluation:', err);
      }
    },

    // Administrative Actions (Phase 5)
    async adminLogin(username?: string, password?: string, demoRole?: string) {
      try {
        this.isLoading = true;
        const res = await api.post('/admin/auth/login/', {
          username,
          password,
          demo_role: demoRole
        });
        this.adminToken = res.data.token;
        this.adminUser = res.data.user;
        localStorage.setItem('YojnaVia_admin_token', this.adminToken);
        localStorage.setItem('YojnaVia_admin_user', JSON.stringify(this.adminUser));
        await this.fetchAdminSchemes();
        return res.data;
      } catch (err: any) {
        this.errorMessage = err.response?.data?.error || 'Administrative login failed';
        throw err;
      } finally {
        this.isLoading = false;
      }
    },

    adminLogout() {
      this.adminToken = '';
      this.adminUser = null;
      localStorage.removeItem('YojnaVia_admin_token');
      localStorage.removeItem('YojnaVia_admin_user');
      this.adminSchemes = [];
    },

    getAdminHeaders() {
      const headers: Record<string, string> = {};
      if (this.adminToken) {
        headers['Authorization'] = `Bearer ${this.adminToken}`;
      }
      if (this.adminUser?.role) {
        headers['X-Admin-Role'] = this.adminUser.role;
      }
      return headers;
    },

    async fetchAdminSchemes(filters: { status?: string; verification?: string; search?: string } = {}) {
      try {
        this.isLoading = true;
        const params = new URLSearchParams();
        if (filters.status) params.append('status', filters.status);
        if (filters.verification) params.append('verification', filters.verification);
        if (filters.search) params.append('search', filters.search);

        const res = await api.get(`/admin/schemes/?${params.toString()}`, {
          headers: this.getAdminHeaders()
        });
        this.adminSchemes = res.data.schemes || [];
        return res.data;
      } catch (err: any) {
        console.error('Failed to load admin schemes:', err);
      } finally {
        this.isLoading = false;
      }
    },

    async createAdminScheme(schemePayload: any) {
      try {
        this.isLoading = true;
        const res = await api.post('/admin/schemes/', schemePayload, {
          headers: this.getAdminHeaders()
        });
        await this.fetchAdminSchemes();
        await this.evaluateEligibility();
        return res.data;
      } catch (err: any) {
        const errorMsg = err.response?.data?.error || 'Failed to create scheme';
        throw new Error(typeof errorMsg === 'object' ? JSON.stringify(errorMsg) : errorMsg);
      } finally {
        this.isLoading = false;
      }
    },

    async updateAdminScheme(code: string, schemePayload: any) {
      try {
        this.isLoading = true;
        const res = await api.put(`/admin/schemes/${code}/`, schemePayload, {
          headers: this.getAdminHeaders()
        });
        await this.fetchAdminSchemes();
        await this.evaluateEligibility();
        return res.data;
      } catch (err: any) {
        const errorMsg = err.response?.data?.error || 'Failed to update scheme';
        throw new Error(typeof errorMsg === 'object' ? JSON.stringify(errorMsg) : errorMsg);
      } finally {
        this.isLoading = false;
      }
    },

    async updateAdminSchemeRules(code: string, rules: any, changeSummary: string) {
      try {
        this.isLoading = true;
        const res = await api.post(`/admin/schemes/${code}/rules/`, {
          rules,
          change_summary: changeSummary
        }, {
          headers: this.getAdminHeaders()
        });
        await this.fetchAdminSchemes();
        await this.fetchTracker();
        return res.data;
      } catch (err: any) {
        const errorMsg = err.response?.data?.error || 'Failed to update rules';
        throw new Error(typeof errorMsg === 'object' ? JSON.stringify(errorMsg) : errorMsg);
      } finally {
        this.isLoading = false;
      }
    },

    async toggleAdminSchemeStatus(code: string) {
      try {
        const res = await api.post(`/admin/schemes/${code}/deactivate/`, {}, {
          headers: this.getAdminHeaders()
        });
        await this.fetchAdminSchemes();
        return res.data;
      } catch (err: any) {
        console.error('Failed to toggle scheme status:', err);
      }
    },

    async fetchSchemeHistory(code: string) {
      try {
        const res = await api.get(`/admin/schemes/${code}/history/`, {
          headers: this.getAdminHeaders()
        });
        return res.data.history || [];
      } catch (err: any) {
        console.error('Failed to fetch scheme history:', err);
        return [];
      }
    },

    async reRunSchemeMatching(code: string) {
      try {
        this.isLoading = true;
        const res = await api.post(`/admin/schemes/${code}/re_evaluate_matching/`, {}, {
          headers: this.getAdminHeaders()
        });
        return res.data;
      } catch (err: any) {
        console.error('Failed to re-run matching:', err);
        throw err;
      } finally {
        this.isLoading = false;
      }
    }
  }
});
