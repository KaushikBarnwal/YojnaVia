import { createRouter, createWebHistory } from 'vue-router';
import LandingView from '../views/LandingView.vue';
import IntakeView from '../views/IntakeView.vue';
import ProfileReviewView from '../views/ProfileReviewView.vue';
import SchemesDashboardView from '../views/SchemesDashboardView.vue';
import SchemeDetailView from '../views/SchemeDetailView.vue';
import DocumentGraphView from '../views/DocumentGraphView.vue';
import FamilyBenefitsView from '../views/FamilyBenefitsView.vue';
import WhatIfSimulatorView from '../views/WhatIfSimulatorView.vue';
import GrInterpreterView from '../views/GrInterpreterView.vue';
import CommunityGapView from '../views/CommunityGapView.vue';
import TrackerView from '../views/TrackerView.vue';
import NotificationPreferencesView from '../views/NotificationPreferencesView.vue';
import CounselorDashboardView from '../views/CounselorDashboardView.vue';
import AdminPortalView from '../views/AdminPortalView.vue';
import PrivacyView from '../views/PrivacyView.vue';
import TermsView from '../views/TermsView.vue';
import NotFoundView from '../views/NotFoundView.vue';

const routes = [
  { 
    path: '/', 
    name: 'Landing', 
    component: LandingView,
    meta: {
      title: 'YOJNAVIA — Claim What’s Yours | Maharashtra Benefits Navigator',
      description: 'Discover every government scheme and scholarship in plain Marathi, Hindi, and English. 100% deterministic rules, zero-Aadhaar policy, and RTS Act 2015 tracking.'
    }
  },
  { 
    path: '/app', 
    name: 'AppIntake', 
    component: IntakeView,
    meta: {
      title: 'AI Conversational Intake & Discovery — YOJNAVIA',
      description: 'Speak or type your age, course, and income in Marathi, Hindi, or English to unlock likely eligible Maharashtra welfare entitlements.'
    }
  },
  { path: '/app/intake', redirect: '/app' },
  { path: '/intake', redirect: '/app' },
  { 
    path: '/review', 
    name: 'ProfileReview', 
    component: ProfileReviewView,
    meta: {
      title: 'Profile Verification & Statutory Audit — YOJNAVIA',
      description: 'Review and confirm your verified demographic criteria against Maharashtra welfare resolutions.'
    }
  },
  { 
    path: '/schemes', 
    name: 'Schemes', 
    component: SchemesDashboardView,
    meta: {
      title: 'Recommended Schemes & Scholarships Catalog — YOJNAVIA',
      description: 'Explore 15 pre-qualified Maharashtra Higher Education and Social Justice schemes matched deterministically with GR citations.'
    }
  },
  { 
    path: '/schemes/:code', 
    name: 'SchemeDetail', 
    component: SchemeDetailView,
    meta: {
      title: 'Scheme Specifications & Applying Guide — YOJNAVIA',
      description: 'Step-by-step applying instructions, issuing authorities, and required document checklists.'
    }
  },
  { 
    path: '/family', 
    name: 'FamilyBenefits', 
    component: FamilyBenefitsView,
    meta: {
      title: 'Family Stacking & Household Welfare — YOJNAVIA',
      description: 'Combine and maximize household benefits across students, parents, and siblings without illegal stacking conflicts.'
    }
  },
  { 
    path: '/what-if', 
    name: 'WhatIfSimulator', 
    component: WhatIfSimulatorView,
    meta: {
      title: 'What-If Entitlement Simulator — YOJNAVIA',
      description: 'Simulate how income certificate changes or hosteller status unlocks new higher education fee waivers.'
    }
  },
  { 
    path: '/gr-interpreter', 
    name: 'GrInterpreter', 
    component: GrInterpreterView,
    meta: {
      title: 'Government Resolution (GR) Interpreter — YOJNAVIA',
      description: 'Decode complex Maharashtra government resolutions and gazette circulars into plain language and structured rules.'
    }
  },
  { 
    path: '/community-gap', 
    name: 'CommunityGap', 
    component: CommunityGapView,
    meta: {
      title: 'Community Insights & Grievance Intelligence — YOJNAVIA',
      description: 'Track rejection hotspots and RTI/RTS Act 2015 resolution metrics across Maharashtra districts.'
    }
  },
  { 
    path: '/documents', 
    name: 'DocumentGraph', 
    component: DocumentGraphView,
    meta: {
      title: 'Cross-Scheme Document Dependency Graph — YOJNAVIA',
      description: 'Visual prerequisite tree mapping Domicile, Tahsildar Income, Caste Validity, and Non-Creamy Layer certificates.'
    }
  },
  { 
    path: '/tracker', 
    name: 'Tracker', 
    component: TrackerView,
    meta: {
      title: 'Application Lifecycle & RTS SLA Tracker — YOJNAVIA',
      description: 'Track saved applications from preparation through scrutiny to final disbursement with 30-day statutory SLAs.'
    }
  },
  { 
    path: '/notifications', 
    name: 'NotificationPreferences', 
    component: NotificationPreferencesView,
    meta: {
      title: 'Deadline Reminders & SMS/WhatsApp Alerts — YOJNAVIA',
      description: 'Configure automated SMS and WhatsApp reminders for scholarship filing deadlines.'
    }
  },
  { 
    path: '/counselor', 
    name: 'CounselorDashboard', 
    component: CounselorDashboardView,
    meta: {
      title: 'Aaple Sarkar Seva Kendra (ASSK) Counselor Desk — YOJNAVIA',
      description: 'Co-pilot for VLEs and CSC operators to serve 50+ walk-in citizens daily with zero data leakage.'
    }
  },
  { 
    path: '/admin-portal', 
    name: 'AdminPortal', 
    component: AdminPortalView,
    meta: {
      title: 'Scheme Rules & Gazette Admin Portal — YOJNAVIA',
      description: 'Edit scheme rules and criteria versions as policies change and trigger student re-evaluations.'
    }
  },
  { 
    path: '/privacy', 
    name: 'Privacy', 
    component: PrivacyView,
    meta: {
      title: 'Citizen Privacy & Zero-Aadhaar Policy — YOJNAVIA',
      description: 'Read YOJNAVIA’s sovereign zero-Aadhaar guarantee and client-side data privacy policy.'
    }
  },
  { 
    path: '/terms', 
    name: 'Terms', 
    component: TermsView,
    meta: {
      title: 'Terms of Service & Statutory Disclaimers — YOJNAVIA',
      description: 'Statutory disclaimers, RTS Act 2015 framework, and informational eligibility guidelines.'
    }
  },
  { 
    path: '/:pathMatch(.*)*', 
    name: 'NotFound', 
    component: NotFoundView,
    meta: {
      title: '404 Page Not Found — YOJNAVIA',
      description: 'The requested statutory page or scheme link was not found on YOJNAVIA.'
    }
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    }
    return { top: 0 };
  }
});

// Dynamic Title & Meta Description Synchronization
router.afterEach((to) => {
  const title = (to.meta?.title as string) || 'YOJNAVIA — Maharashtra Benefits Navigator';
  document.title = title;

  const desc = to.meta?.description as string;
  if (desc) {
    let metaDesc = document.querySelector('meta[name="description"]');
    if (!metaDesc) {
      metaDesc = document.createElement('meta');
      metaDesc.setAttribute('name', 'description');
      document.head.appendChild(metaDesc);
    }
    metaDesc.setAttribute('content', desc);
  }

  // Analytics event dispatch
  if (typeof window !== 'undefined' && (window as any).yojnaviaAnalytics) {
    (window as any).yojnaviaAnalytics.trackEvent('page_view', { path: to.path, title });
  }
});

export default router;
