import { createRouter, createWebHistory } from 'vue-router';
import IntakeView from '../views/IntakeView.vue';
import ProfileReviewView from '../views/ProfileReviewView.vue';
import SchemesDashboardView from '../views/SchemesDashboardView.vue';
import SchemeDetailView from '../views/SchemeDetailView.vue';
import DocumentGraphView from '../views/DocumentGraphView.vue';
import FamilyBenefitsView from '../views/FamilyBenefitsView.vue';
import TrackerView from '../views/TrackerView.vue';
import AdminPortalView from '../views/AdminPortalView.vue';

const routes = [
  { path: '/', name: 'Intake', component: IntakeView },
  { path: '/review', name: 'ProfileReview', component: ProfileReviewView },
  { path: '/schemes', name: 'Schemes', component: SchemesDashboardView },
  { path: '/schemes/:code', name: 'SchemeDetail', component: SchemeDetailView },
  { path: '/family', name: 'FamilyBenefits', component: FamilyBenefitsView },
  { path: '/documents', name: 'DocumentGraph', component: DocumentGraphView },
  { path: '/tracker', name: 'Tracker', component: TrackerView },
  { path: '/admin-portal', name: 'AdminPortal', component: AdminPortalView },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
