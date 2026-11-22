export interface StudentProfile {
  id?: string;
  session_token?: string;
  name: string;
  age: number | null;
  gender: 'MALE' | 'FEMALE' | 'OTHER';
  state: string;
  district: string;
  is_maharashtra_domicile: boolean;
  caste_category: 'OPEN' | 'OBC' | 'SC' | 'ST' | 'VJNT' | 'SBC' | 'EWS';
  caste_name?: string;
  annual_family_income: number;
  current_course_level: '11TH_12TH' | 'DIPLOMA' | 'UNDERGRADUATE' | 'PROFESSIONAL_DEGREE' | 'POSTGRADUATE';
  course_name?: string;
  admission_quota: 'CAP_ROUND' | 'INSTITUTE_QUOTA' | 'DIRECT_SECOND_YEAR';
  previous_year_percentage?: number | null;
  accommodation_type: 'DAY_SCHOLAR' | 'GOVT_HOSTEL' | 'PRIVATE_RENTAL_PG';
  parent_is_farmer: boolean;
  parent_land_acres: number;
  has_disability?: boolean;
  disability_percentage?: number;
  has_aadhaar_seeded_bank: boolean;
  is_confirmed: boolean;
  field_confidence_scores?: Record<string, number>;
}

export interface CriterionAudit {
  field?: string;
  label?: string;
  reason: string;
  citation?: string;
}

export interface RequiredDocument {
  code: string;
  name: string;
  name_marathi: string;
  issuing_authority: string;
  procurement_portal: string;
  estimated_sla_days: number;
  is_mandatory: boolean;
  purpose: string;
}

export interface EvaluatedScheme {
  scheme_id: string;
  code: string;
  version: string;
  effective_academic_year: string;
  name: string;
  name_marathi: string;
  department: string;
  statutory_gr: string;
  benefit_type: string;
  benefit_amount_text: string;
  estimated_annual_value: number;
  brief_description: string;
  official_portal_url: string;
  official_source_url?: string;
  portal_name: string;
  last_verified_on?: string;
  application_deadline?: string | null;
  application_steps?: string[];
  verification_status?: string;
  is_sample?: boolean;
  contact_helpline?: string;
  statutory_fee_text?: string;
  status: 'LIKELY_ELIGIBLE' | 'NEAR_ELIGIBLE' | 'NEEDS_CONFIRMATION' | 'INELIGIBLE';
  passed_criteria: CriterionAudit[];
  near_eligible_criteria: CriterionAudit[];
  failed_criteria: CriterionAudit[];
  missing_criteria: CriterionAudit[];
  near_eligible_guidance?: string;
  required_documents: RequiredDocument[];
}

export interface EvaluationSummary {
  total: number;
  likely_eligible: number;
  near_eligible: number;
  needs_confirmation: number;
  ineligible: number;
}

export interface StackingBundle {
  recommended_bundle: EvaluatedScheme[];
  total_package_value: number;
  conflicting_schemes: Array<{
    scheme_code: string;
    scheme_name: string;
    reason: string;
  }>;
  guidance: string;
}

export interface DocumentNode {
  code: string;
  name: string;
  name_marathi: string;
  issuing_authority: string;
  procurement_portal: string;
  estimated_sla_days: number;
  validity_duration: string;
  prerequisites: string[];
  how_to_obtain: string[];
  schemes_count: number;
  total_financial_value_unlocked: number;
  unlocks_schemes: Array<{
    scheme_code: string;
    scheme_name: string;
    benefit_type: string;
    estimated_value: number;
    is_mandatory: boolean;
    purpose: string;
  }>;
}

export type ApplicationStatus = 
  | 'NOT_STARTED' 
  | 'DOCUMENTS_PENDING' 
  | 'DOCUMENTS_READY' 
  | 'APPLIED' 
  | 'UNDER_REVIEW' 
  | 'APPROVED' 
  | 'REJECTED';

export interface ApplicationRecord {
  id: string;
  scheme: string;
  scheme_code: string;
  scheme_name: string;
  scheme_benefit: string;
  portal_name: string;
  official_portal_url: string;
  status: ApplicationStatus;
  stage: 'DISCOVERED' | 'DOCUMENTS_PREPARATION' | 'ONLINE_REGISTRATION' | 'COLLEGE_SCRUTINY' | 'DEPT_APPROVAL' | 'DISBURSED';
  completed_documents: string[];
  application_reference_number: string;
  applied_date?: string | null;
  submission_mode?: string;
  is_user_reported?: boolean;
  needs_re_evaluation?: boolean;
  re_evaluation_reason?: string;
  re_evaluation_notified_at?: string | null;
  next_immediate_action: string;
  next_action_deadline?: string;
  notes?: string;
  updated_at: string;
}

export interface SchemeRuleVersion {
  id: string;
  version: string;
  changed_by: string;
  changed_at: string;
  change_type: string;
  change_summary: string;
  affected_applications_count: number;
  rules?: any;
}

export interface AdminUser {
  username: string;
  name: string;
  role: 'SCHEME_OFFICER' | 'SUPERADMIN';
  department: string;
  token?: string;
}

export interface PersonaInfo {
  key: string;
  name: string;
  tag: string;
  details: string;
}

// Phase 3 Conversational Intake Types
export interface IntakeField {
  value: any;
  status: 'known' | 'unknown';
  confidence: number | null;
  user_confirmed: boolean;
  source: string | null;
}

export interface StructuredAnalysis {
  understanding?: string;
  key_statutory_finding?: string;
  simple_explanation?: string;
  steps?: string[];
  final_recommendation?: string;
  next_action?: string;
  engine_used?: string;
}

export interface IntakeState {
  fields: Record<string, IntakeField>;
  known_count: number;
  total_count: number;
  structured_analysis?: StructuredAnalysis;
}

export interface NextQuestion {
  field: string;
  text: string;
  suggested_answers: string[];
}

export interface IntakeChatResponse {
  reply: string;
  session_token: string;
  state: IntakeState;
  next_question: NextQuestion | null;
  eligibility: {
    summary: EvaluationSummary;
    results: EvaluatedScheme[];
    stacking_bundle: StackingBundle;
  } | null;
  error: {
    code: string;
    message: string;
    retry_after?: number | null;
  } | null;
}
