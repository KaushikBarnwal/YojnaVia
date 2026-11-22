import { createRouter, createWebHistory } from 'vue-router';
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

const routes = [
  { path: '/', name: 'Intake', component: IntakeView },
  { path: '/review', name: 'ProfileReview', component: ProfileReviewView },
  { path: '/schemes', name: 'Schemes', component: SchemesDashboardView },
  { path: '/schemes/:code', name: 'SchemeDetail', component: SchemeDetailView },
  { path: '/family', name: 'FamilyBenefits', component: FamilyBenefitsView },
  { path: '/what-if', name: 'WhatIfSimulator', component: WhatIfSimulatorView },
  { path: '/gr-interpreter', name: 'GrInterpreter', component: GrInterpreterView },
  { path: '/community-gap', name: 'CommunityGap', component: CommunityGapView },
  { path: '/documents', name: 'DocumentGraph', component: DocumentGraphView },
  { path: '/tracker', name: 'Tracker', component: TrackerView },
  { path: '/notifications', name: 'NotificationPreferences', component: NotificationPreferencesView },
  { path: '/counselor', name: 'CounselorDashboard', component: CounselorDashboardView },
  { path: '/admin-portal', name: 'AdminPortal', component: AdminPortalView },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
