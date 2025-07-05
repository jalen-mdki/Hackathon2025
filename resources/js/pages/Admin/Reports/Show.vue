<script setup lang="ts">
import { Head, usePage, router } from '@inertiajs/vue3';
import { ref, computed } from 'vue';
import AppLayout from '@/layouts/AppLayout.vue';

interface Report {
  id: number;
  report_type: string;
  incident_type?: string;
  description: string;
  date_of_incident: string;
  location_lat?: number;
  location_long?: number;
  severity?: string;
  industry?: string;
  reporter_name?: string;
  reporter_contact?: string;
  status: string;
  assigned_to?: number;
  is_escalated: boolean;
  escalation_status: string;
  cause_of_death?: string;
  regulation_class_broken?: string;
  feedback_given: boolean;
  organization?: {
    id: number;
    name: string;
    industry: string;
    contact_person: string;
    contact_email: string;
  };
  reported_by_user?: {
    id: number;
    first_name: string;
    last_name: string;
    email: string;
  };
  assigned_to_user?: {
    id: number;
    first_name: string;
    last_name: string;
    email: string;
  };
  report_uploads?: {
    id: number;
    file_url: string;
    file_type: string;
    uploaded_by?: string;
    created_at: string;
  }[];
  report_escalations?: {
    id: number;
    escalation_reason: string;
    escalated_at: string;
    escalated_by_user: {
      id: number;
      first_name: string;
      last_name: string;
      email: string;
    };
  }[];
  created_at: string;
  updated_at: string;
}

const { props } = usePage();
const report = props.report as Report;

const activeTab = ref('Details');

// Image slideshow state
const currentImageIndex = ref(0);

const tabs = [
  { name: 'Details', icon: '📋', count: null },
  { name: 'Status & Timeline', icon: '📊', count: null },
  { name: 'Escalations', icon: '⚠️', count: report.report_escalations?.length || 0 },
  { name: 'Attachments', icon: '📎', count: report.report_uploads?.length || 0 },
  { name: 'Organization', icon: '🏢', count: null },
  { name: 'Location', icon: '📍', count: null },
];

// Utility functions
const getStatusColor = (status: string) => {
  const colors = {
    'Pending': 'from-yellow-500 to-orange-500',
    'In Progress': 'from-blue-500 to-cyan-500',
    'Completed': 'from-green-500 to-emerald-500',
    'Closed': 'from-gray-500 to-slate-500',
    'Under Review': 'from-purple-500 to-pink-500',
  };
  return colors[status] || 'from-gray-500 to-gray-600';
};

const getSeverityColor = (severity: string) => {
  const colors = {
    'Low': 'from-green-500 to-emerald-500',
    'Medium': 'from-yellow-500 to-orange-500',
    'High': 'from-orange-500 to-red-500',
    'Critical': 'from-red-500 to-rose-500',
  };
  return colors[severity] || 'from-gray-500 to-gray-600';
};

const getIndustryIcon = (industry: string) => {
  const icons = {
    'Technology': '💻',
    'Healthcare': '🏥',
    'Finance': '💰',
    'Manufacturing': '🏭',
    'Energy': '⚡',
    'Construction': '🏗️',
    'Mining': '⛏️',
    'Oil & Gas': '🛢️',
    'Chemical': '🧪',
    'Transportation': '🚛',
  };
  return icons[industry] || '🏢';
};

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const formatDateShort = (date: string) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

// Image handling
const getImageAttachments = computed(() => {
  if (!report.report_uploads) return [];
  return report.report_uploads.filter(upload => 
    upload.file_type && upload.file_type.startsWith('image/')
  );
});

const getDocumentAttachments = computed(() => {
  if (!report.report_uploads) return [];
  return report.report_uploads.filter(upload => 
    upload.file_type && !upload.file_type.startsWith('image/')
  );
});

// Image slideshow methods
const nextImage = () => {
  if (getImageAttachments.value.length > 0) {
    currentImageIndex.value = (currentImageIndex.value + 1) % getImageAttachments.value.length;
  }
};

const prevImage = () => {
  if (getImageAttachments.value.length > 0) {
    currentImageIndex.value = currentImageIndex.value === 0 
      ? getImageAttachments.value.length - 1 
      : currentImageIndex.value - 1;
  }
};

const goToImage = (index: number) => {
  currentImageIndex.value = index;
};

// Analytics data
const analyticsData = computed(() => ({
  totalAttachments: report.report_uploads?.length || 0,
  imageAttachments: getImageAttachments.value.length,
  documentAttachments: getDocumentAttachments.value.length,
  totalEscalations: report.report_escalations?.length || 0,
  daysOpen: Math.floor((new Date().getTime() - new Date(report.created_at).getTime()) / (1000 * 3600 * 24)),
  daysFromIncident: Math.floor((new Date().getTime() - new Date(report.date_of_incident).getTime()) / (1000 * 3600 * 24)),
}));

// Actions
const editReport = () => {
  router.visit(`/admin/reports/${report.id}/edit`);
};

const escalateReport = () => {
  // This would open a modal or redirect to escalation form
  console.log('Escalate report');
};

const downloadAttachment = (attachment: any) => {
  window.open(attachment.file_url, '_blank');
};
</script>

<template>
  <Head :title="`Report #${report.id} - ${report.report_type}`" />

  <AppLayout :breadcrumbs="[
    { title: 'Dashboard', href: '/dashboard' }, 
    { title: 'Reports', href: '/admin/reports' }, 
    { title: `Report #${report.id}`, href: '#' }
  ]">
    <!-- Hero Header -->
    <div class="relative overflow-hidden bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">
      <!-- Animated background elements -->
      <div class="absolute inset-0 overflow-hidden">
        <div class="absolute -top-40 -right-32 w-80 h-80 rounded-full bg-blue-500/10 blur-3xl animate-pulse"></div>
        <div class="absolute -bottom-40 -left-32 w-80 h-80 rounded-full bg-indigo-500/10 blur-3xl animate-pulse delay-1000"></div>
      </div>
      
      <div class="relative px-6 py-12">
        <!-- Report Header -->
        <div class="flex flex-col lg:flex-row items-start lg:items-center gap-6 mb-8">
          <!-- Report Icon -->
          <div class="relative">
            <div :class="`inline-flex items-center justify-center w-24 h-24 rounded-3xl bg-gradient-to-br ${getStatusColor(report.status)} text-4xl shadow-2xl`">
              🚨
            </div>
            <!-- Escalation indicator -->
            <div v-if="report.is_escalated" class="absolute -top-2 -right-2 w-8 h-8 bg-red-500 rounded-full border-4 border-white shadow-lg animate-pulse flex items-center justify-center">
              <div class="w-3 h-3 bg-white rounded-full"></div>
            </div>
          </div>

          <!-- Report Info -->
          <div class="flex-1">
            <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
              <div>
                <h1 class="text-4xl md:text-5xl font-bold text-white mb-2 tracking-tight">
                  Report #{{ report.id }}
                </h1>
                <p class="text-xl text-blue-100 mb-4">{{ report.report_type }}</p>
                <div class="flex flex-wrap items-center gap-4 text-blue-100">
                  <span :class="`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium bg-gradient-to-r ${getStatusColor(report.status)} text-white shadow-lg`">
                    {{ report.status }}
                  </span>
                  <span v-if="report.severity" :class="`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium bg-gradient-to-r ${getSeverityColor(report.severity)} text-white shadow-lg`">
                    {{ report.severity }} Severity
                  </span>
                  <span v-if="report.is_escalated" class="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium bg-gradient-to-r from-red-500 to-rose-500 text-white shadow-lg">
                    ⚠️ Escalated
                  </span>
                  <div class="flex items-center">
                    <svg class="w-5 h-5 mr-2 text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <span>{{ formatDateShort(report.date_of_incident) }}</span>
                  </div>
                </div>
              </div>
              
              <!-- Action Buttons -->
              <div class="flex items-center gap-4">
                <button
                  @click="editReport"
                  class="inline-flex items-center px-6 py-3 bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white font-semibold rounded-xl shadow-lg transform hover:scale-105 transition-all duration-300"
                >
                  <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                  Edit Report
                </button>
                
                <button
                  v-if="!report.is_escalated"
                  @click="escalateReport"
                  class="inline-flex items-center px-6 py-3 bg-gradient-to-r from-red-500 to-rose-500 hover:from-red-600 hover:to-rose-600 text-white font-semibold rounded-xl shadow-lg transform hover:scale-105 transition-all duration-300"
                >
                  <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.966-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                  Escalate
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Tab Navigation -->
        <div class="bg-white/10 backdrop-blur-lg rounded-2xl p-2 border border-white/20">
          <div class="flex flex-wrap gap-2">
            <button
              v-for="tab in tabs"
              :key="tab.name"
              @click="activeTab = tab.name"
              :class="[
                'flex items-center gap-2 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-300 transform hover:scale-105',
                activeTab === tab.name
                  ? 'bg-blue-500 text-white shadow-lg scale-105'
                  : 'text-white/80 hover:text-white hover:bg-white/10'
              ]"
            >
              <span class="text-lg">{{ tab.icon }}</span>
              <span class="hidden sm:inline">{{ tab.name }}</span>
              <span v-if="tab.count !== null" :class="[
                'inline-flex items-center justify-center px-2 py-1 text-xs rounded-full',
                activeTab === tab.name ? 'bg-white/20' : 'bg-blue-500/20'
              ]">
                {{ tab.count }}
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="px-6 -mt-8 relative z-10">
      <!-- Details Tab -->
      <div v-if="activeTab === 'Details'" class="space-y-8">
        <!-- Key Metrics Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
          <div class="bg-gradient-to-br from-blue-500/20 to-cyan-500/20 backdrop-blur-lg rounded-2xl p-6 border border-blue-500/30 transform hover:scale-105 transition-all duration-300">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-3xl font-bold text-white">{{ analyticsData.daysOpen }}</p>
                <p class="text-sm text-blue-200">Days Open</p>
              </div>
              <div class="p-3 bg-blue-500/20 rounded-xl">
                <svg class="w-8 h-8 text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
            </div>
          </div>

          <div class="bg-gradient-to-br from-green-500/20 to-emerald-500/20 backdrop-blur-lg rounded-2xl p-6 border border-green-500/30 transform hover:scale-105 transition-all duration-300">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-3xl font-bold text-white">{{ analyticsData.totalAttachments }}</p>
                <p class="text-sm text-green-200">Total Attachments</p>
              </div>
              <div class="p-3 bg-green-500/20 rounded-xl">
                <svg class="w-8 h-8 text-green-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                </svg>
              </div>
            </div>
          </div>

          <div class="bg-gradient-to-br from-red-500/20 to-rose-500/20 backdrop-blur-lg rounded-2xl p-6 border border-red-500/30 transform hover:scale-105 transition-all duration-300">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-3xl font-bold text-white">{{ analyticsData.totalEscalations }}</p>
                <p class="text-sm text-red-200">Escalations</p>
              </div>
              <div class="p-3 bg-red-500/20 rounded-xl">
                <svg class="w-8 h-8 text-red-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.966-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
            </div>
          </div>

          <div class="bg-gradient-to-br from-purple-500/20 to-pink-500/20 backdrop-blur-lg rounded-2xl p-6 border border-purple-500/30 transform hover:scale-105 transition-all duration-300">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-3xl font-bold text-white">{{ analyticsData.daysFromIncident }}</p>
                <p class="text-sm text-purple-200">Days Since Incident</p>
              </div>
              <div class="p-3 bg-purple-500/20 rounded-xl">
                <svg class="w-8 h-8 text-purple-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        <!-- Report Details -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <!-- Basic Information -->
          <div class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-lg rounded-2xl p-8 border border-slate-700/50">
            <h3 class="text-2xl font-bold text-white mb-6 flex items-center">
              <span class="text-3xl mr-3">📋</span>
              Basic Information
            </h3>
            <div class="space-y-4">
              <div class="flex justify-between items-start">
                <span class="text-slate-300">Report Type:</span>
                <span class="font-semibold text-white text-right">{{ report.report_type }}</span>
              </div>
              <div v-if="report.incident_type" class="flex justify-between items-start">
                <span class="text-slate-300">Incident Type:</span>
                <span class="font-semibold text-white text-right">{{ report.incident_type }}</span>
              </div>
              <div class="flex justify-between items-start">
                <span class="text-slate-300">Severity:</span>
                <span v-if="report.severity" :class="`font-semibold px-3 py-1 rounded-full text-xs bg-gradient-to-r ${getSeverityColor(report.severity)} text-white`">
                  {{ report.severity }}
                </span>
                <span v-else class="text-slate-400">Not specified</span>
              </div>
              <div class="flex justify-between items-start">
                <span class="text-slate-300">Industry:</span>
                <span class="font-semibold text-white text-right">{{ report.industry || 'Not specified' }}</span>
              </div>
              <div class="flex justify-between items-start">
                <span class="text-slate-300">Date of Incident:</span>
                <span class="font-semibold text-white text-right">{{ formatDateShort(report.date_of_incident) }}</span>
              </div>
              <div class="flex justify-between items-start">
                <span class="text-slate-300">Report Created:</span>
                <span class="font-semibold text-white text-right">{{ formatDateShort(report.created_at) }}</span>
              </div>
              <div class="flex justify-between items-start">
                <span class="text-slate-300">Last Updated:</span>
                <span class="font-semibold text-white text-right">{{ formatDateShort(report.updated_at) }}</span>
              </div>
            </div>
          </div>

          <!-- Reporter Information -->
          <div class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-lg rounded-2xl p-8 border border-slate-700/50">
            <h3 class="text-2xl font-bold text-white mb-6 flex items-center">
              <span class="text-3xl mr-3">👤</span>
              Reporter Information
            </h3>
            <div class="space-y-4">
              <div v-if="report.reported_by_user" class="flex justify-between items-start">
                <span class="text-slate-300">System User:</span>
                <div class="text-right">
                  <div class="font-semibold text-white">{{ report.reported_by_user.first_name }} {{ report.reported_by_user.last_name }}</div>
                  <div class="text-sm text-slate-400">{{ report.reported_by_user.email }}</div>
                </div>
              </div>
              <div v-if="report.reporter_name" class="flex justify-between items-start">
                <span class="text-slate-300">Reporter Name:</span>
                <span class="font-semibold text-white text-right">{{ report.reporter_name }}</span>
              </div>
              <div v-if="report.reporter_contact" class="flex justify-between items-start">
                <span class="text-slate-300">Contact Info:</span>
                <span class="font-semibold text-white text-right">{{ report.reporter_contact }}</span>
              </div>
              <div v-if="report.assigned_to_user" class="flex justify-between items-start">
                <span class="text-slate-300">Assigned To:</span>
                <div class="text-right">
                  <div class="font-semibold text-white">{{ report.assigned_to_user.first_name }} {{ report.assigned_to_user.last_name }}</div>
                  <div class="text-sm text-slate-400">{{ report.assigned_to_user.email }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Description -->
        <div class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-lg rounded-2xl p-8 border border-slate-700/50">
          <h3 class="text-2xl font-bold text-white mb-6 flex items-center">
            <span class="text-3xl mr-3">📝</span>
            Description
          </h3>
          <p class="text-slate-300 leading-relaxed">{{ report.description }}</p>
        </div>

        <!-- Additional Information -->
        <div v-if="report.cause_of_death || report.regulation_class_broken" class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-lg rounded-2xl p-8 border border-slate-700/50">
          <h3 class="text-2xl font-bold text-white mb-6 flex items-center">
            <span class="text-3xl mr-3">⚖️</span>
            Additional Information
          </h3>
          <div class="space-y-4">
            <div v-if="report.cause_of_death" class="flex justify-between items-start">
              <span class="text-slate-300">Cause of Death:</span>
              <span class="font-semibold text-white text-right">{{ report.cause_of_death }}</span>
            </div>
            <div v-if="report.regulation_class_broken" class="flex justify-between items-start">
              <span class="text-slate-300">Regulation Class Broken:</span>
              <span class="font-semibold text-white text-right">{{ report.regulation_class_broken }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Status & Timeline Tab -->
      <div v-if="activeTab === 'Status & Timeline'" class="space-y-8">
        <!-- Current Status -->
        <div class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-lg rounded-2xl p-8 border border-slate-700/50">
          <h3 class="text-2xl font-bold text-white mb-6 flex items-center">
            <span class="text-3xl mr-3">📊</span>
            Current Status
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="text-center p-6 bg-slate-700/30 rounded-xl">
              <div :class="`w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br ${getStatusColor(report.status)} flex items-center justify-center text-2xl`">
                📋
              </div>
              <h4 class="text-lg font-semibold text-white mb-2">Report Status</h4>
              <p class="text-slate-300">{{ report.status }}</p>
            </div>
            <div class="text-center p-6 bg-slate-700/30 rounded-xl">
              <div :class="`w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br ${report.is_escalated ? 'from-red-500 to-rose-500' : 'from-green-500 to-emerald-500'} flex items-center justify-center text-2xl`">
                {{ report.is_escalated ? '⚠️' : '✅' }}
              </div>
              <h4 class="text-lg font-semibold text-white mb-2">Escalation Status</h4>
              <p class="text-slate-300">{{ report.escalation_status }}</p>
            </div>
            <div class="text-center p-6 bg-slate-700/30 rounded-xl">
              <div :class="`w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br ${report.feedback_given ? 'from-green-500 to-emerald-500' : 'from-yellow-500 to-orange-500'} flex items-center justify-center text-2xl`">
                {{ report.feedback_given ? '💬' : '⏳' }}
              </div>
              <h4 class="text-lg font-semibold text-white mb-2">Feedback Status</h4>
              <p class="text-slate-300">{{ report.feedback_given ? 'Feedback Given' : 'Pending Feedback' }}</p>
            </div>
          </div>
        </div>

        <!-- Timeline -->
        <div class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-lg rounded-2xl p-8 border border-slate-700/50">
          <h3 class="text-2xl font-bold text-white mb-6 flex items-center">
            <span class="text-3xl mr-3">⏱️</span>
            Timeline
          </h3>
          <div class="space-y-6">
            <!-- Incident Date -->
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 bg-gradient-to-br from-red-500 to-rose-500 rounded-full flex items-center justify-center flex-shrink-0">
                <span class="text-white text-xl">🚨</span>
              </div>
              <div class="flex-1">
                <h4 class="text-lg font-semibold text-white">Incident Occurred</h4>
                <p class="text-slate-300 text-sm">{{ formatDate(report.date_of_incident) }}</p>
              </div>
            </div>

            <!-- Report Created -->
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-full flex items-center justify-center flex-shrink-0">
                <span class="text-white text-xl">📝</span>
              </div>
              <div class="flex-1">
                <h4 class="text-lg font-semibold text-white">Report Created</h4>
                <p class="text-slate-300 text-sm">{{ formatDate(report.created_at) }}</p>
                <p v-if="report.reported_by_user" class="text-slate-400 text-xs">
                  by {{ report.reported_by_user.first_name }} {{ report.reported_by_user.last_name }}
                </p>
              </div>
            </div>

            <!-- Escalations -->
            <div v-for="escalation in report.report_escalations" :key="escalation.id" class="flex items-start space-x-4">
              <div class="w-12 h-12 bg-gradient-to-br from-red-500 to-rose-500 rounded-full flex items-center justify-center flex-shrink-0">
                <span class="text-white text-xl">⚠️</span>
              </div>
              <div class="flex-1">
                <h4 class="text-lg font-semibold text-white">Report Escalated</h4>
                <p class="text-slate-300 text-sm">{{ formatDate(escalation.escalated_at) }}</p>
                <p class="text-slate-400 text-xs">
                  by {{ escalation.escalated_by_user.first_name }} {{ escalation.escalated_by_user.last_name }}
                </p>
                <p class="text-slate-300 text-sm mt-2 bg-red-500/10 p-2 rounded border border-red-500/20">
                  {{ escalation.escalation_reason }}
                </p>
              </div>
            </div>

            <!-- Last Updated -->
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-500 rounded-full flex items-center justify-center flex-shrink-0">
                <span class="text-white text-xl">🔄</span>
              </div>
              <div class="flex-1">
                <h4 class="text-lg font-semibold text-white">Last Updated</h4>
                <p class="text-slate-300 text-sm">{{ formatDate(report.updated_at) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Escalations Tab -->
      <div v-if="activeTab === 'Escalations'" class="space-y-8">
        <div v-if="report.report_escalations && report.report_escalations.length > 0">
          <div v-for="(escalation, index) in report.report_escalations" :key="escalation.id" 
               class="bg-gradient-to-br from-red-500/10 to-rose-500/10 backdrop-blur-lg rounded-2xl p-8 border border-red-500/30 mb-6">
            <div class="flex items-start justify-between mb-6">
              <div class="flex items-center">
                <div class="w-12 h-12 bg-gradient-to-br from-red-500 to-rose-500 rounded-full flex items-center justify-center mr-4">
                  <span class="text-white text-xl">⚠️</span>
                </div>
                <div>
                  <h3 class="text-xl font-bold text-white">Escalation #{{ index + 1 }}</h3>
                  <p class="text-red-200">{{ formatDate(escalation.escalated_at) }}</p>
                </div>
              </div>
              <span class="px-3 py-1 bg-red-500 text-white text-sm rounded-full">Critical</span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <h4 class="text-lg font-semibold text-red-300 mb-2">Escalated By</h4>
                <div class="bg-red-500/5 p-4 rounded-lg border border-red-500/20">
                  <p class="text-white font-medium">
                    {{ escalation.escalated_by_user.first_name }} {{ escalation.escalated_by_user.last_name }}
                  </p>
                  <p class="text-red-200 text-sm">{{ escalation.escalated_by_user.email }}</p>
                </div>
              </div>
              <div>
                <h4 class="text-lg font-semibold text-red-300 mb-2">Escalation Date</h4>
                <div class="bg-red-500/5 p-4 rounded-lg border border-red-500/20">
                  <p class="text-white font-medium">{{ formatDate(escalation.escalated_at) }}</p>
                  <p class="text-red-200 text-sm">
                    {{ Math.floor((new Date().getTime() - new Date(escalation.escalated_at).getTime()) / (1000 * 3600 * 24)) }} days ago
                  </p>
                </div>
              </div>
            </div>

            <div>
              <h4 class="text-lg font-semibold text-red-300 mb-2">Escalation Reason</h4>
              <div class="bg-red-500/5 p-4 rounded-lg border border-red-500/20">
                <p class="text-white leading-relaxed">{{ escalation.escalation_reason }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- No Escalations -->
        <div v-else class="text-center py-16">
          <div class="mx-auto w-24 h-24 bg-gradient-to-br from-slate-700 to-slate-800 rounded-full flex items-center justify-center mb-6">
            <span class="text-4xl">✅</span>
          </div>
          <h3 class="text-xl font-semibold text-slate-300 mb-2">No Escalations</h3>
          <p class="text-slate-500 mb-6">This report has not been escalated.</p>
          <button
            @click="escalateReport"
            class="inline-flex items-center px-6 py-3 bg-red-500 hover:bg-red-600 text-white font-medium rounded-lg transition-colors"
          >
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.966-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            Escalate Report
          </button>
        </div>
      </div>

      <!-- Attachments Tab -->
      <div v-if="activeTab === 'Attachments'" class="space-y-8">
        <!-- Image Gallery -->
        <div v-if="getImageAttachments.length > 0" class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-lg rounded-2xl p-8 border border-slate-700/50">
          <h3 class="text-2xl font-bold text-white mb-6 flex items-center">
            <span class="text-3xl mr-3">🖼️</span>
            Images ({{ getImageAttachments.length }})
          </h3>
          
          <!-- Main Image Display -->
          <div class="relative mb-6">
            <div class="relative h-96 bg-slate-700 rounded-xl overflow-hidden">
              <img 
                :src="getImageAttachments[currentImageIndex]?.file_url"
                :alt="`Report attachment ${currentImageIndex + 1}`"
                class="w-full h-full object-contain"
              />
              
              <!-- Navigation arrows -->
              <template v-if="getImageAttachments.length > 1">
                <button 
                  @click="prevImage"
                  class="absolute left-4 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white rounded-full p-3 transition-all duration-200"
                >
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
                
                <button 
                  @click="nextImage"
                  class="absolute right-4 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white rounded-full p-3 transition-all duration-200"
                >
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </button>
                
                <!-- Image counter -->
                <div class="absolute top-4 right-4 bg-black/50 text-white px-3 py-1 rounded">
                  {{ currentImageIndex + 1 }} / {{ getImageAttachments.length }}
                </div>
              </template>
            </div>
            
            <!-- Download button -->
            <button
              @click="downloadAttachment(getImageAttachments[currentImageIndex])"
              class="absolute bottom-4 left-4 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors flex items-center"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Download
            </button>
          </div>
          
          <!-- Thumbnail Navigation -->
          <div v-if="getImageAttachments.length > 1" class="flex space-x-2 overflow-x-auto pb-2">
            <button
              v-for="(image, index) in getImageAttachments"
              :key="index"
              @click="goToImage(index)"
              :class="[
                'flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden border-2 transition-all duration-200',
                currentImageIndex === index 
                  ? 'border-blue-500 scale-105' 
                  : 'border-slate-600 hover:border-blue-400'
              ]"
            >
              <img 
                :src="image.file_url"
                :alt="`Thumbnail ${index + 1}`"
                class="w-full h-full object-cover"
              />
            </button>
          </div>
        </div>

        <!-- Document Attachments -->
        <div v-if="getDocumentAttachments.length > 0" class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-lg rounded-2xl p-8 border border-slate-700/50">
          <h3 class="text-2xl font-bold text-white mb-6 flex items-center">
            <span class="text-3xl mr-3">📄</span>
            Documents ({{ getDocumentAttachments.length }})
          </h3>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              v-for="document in getDocumentAttachments"
              :key="document.id"
              class="flex items-center p-4 bg-slate-700/30 rounded-lg border border-slate-600 hover:border-blue-500/50 transition-all duration-300"
            >
              <div class="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center mr-4">
                <svg class="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div class="flex-1">
                <p class="text-white font-medium">Document {{ document.id }}</p>
                <p class="text-slate-400 text-sm">{{ document.file_type }}</p>
                <p v-if="document.uploaded_by" class="text-slate-400 text-xs">by {{ document.uploaded_by }}</p>
              </div>
              <button
                @click="downloadAttachment(document)"
                class="p-2 text-blue-400 hover:text-blue-300 transition-colors"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- No Attachments -->
        <div v-if="!report.report_uploads || report.report_uploads.length === 0" class="text-center py-16">
          <div class="mx-auto w-24 h-24 bg-gradient-to-br from-slate-700 to-slate-800 rounded-full flex items-center justify-center mb-6">
            <span class="text-4xl">📎</span>
          </div>
          <h3 class="text-xl font-semibold text-slate-300 mb-2">No Attachments</h3>
          <p class="text-slate-500">No files have been attached to this report.</p>
        </div>
      </div>

      <!-- Organization Tab -->
      <div v-if="activeTab === 'Organization'" class="space-y-8">
        <div v-if="report.organization" class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-lg rounded-2xl p-8 border border-slate-700/50">
          <div class="flex items-center mb-8">
            <div class="w-16 h-16 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-2xl flex items-center justify-center text-2xl mr-6">
              {{ getIndustryIcon(report.organization.industry) }}
            </div>
            <div>
              <h3 class="text-2xl font-bold text-white">{{ report.organization.name }}</h3>
              <p class="text-blue-200">{{ report.organization.industry }}</p>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 class="text-lg font-semibold text-blue-300 mb-4">Contact Information</h4>
              <div class="space-y-3">
                <div class="flex justify-between">
                  <span class="text-slate-300">Contact Person:</span>
                  <span class="text-white font-medium">{{ report.organization.contact_person }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-slate-300">Email:</span>
                  <span class="text-white font-medium">{{ report.organization.contact_email }}</span>
                </div>
              </div>
            </div>
            <div>
              <h4 class="text-lg font-semibold text-green-300 mb-4">Actions</h4>
              <div class="space-y-3">
                <a
                  :href="`/admin/organizations/${report.organization.id}`"
                  class="inline-flex items-center px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
                >
                  <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                  View Organization
                </a>
              </div>
            </div>
          </div>
        </div>

        <!-- No Organization -->
        <div v-else class="text-center py-16">
          <div class="mx-auto w-24 h-24 bg-gradient-to-br from-slate-700 to-slate-800 rounded-full flex items-center justify-center mb-6">
            <span class="text-4xl">🏢</span>
          </div>
          <h3 class="text-xl font-semibold text-slate-300 mb-2">No Organization</h3>
          <p class="text-slate-500">This report is not associated with any organization.</p>
        </div>
      </div>

      <!-- Location Tab -->
      <div v-if="activeTab === 'Location'" class="space-y-8">
        <div v-if="report.location_lat && report.location_long" class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-lg rounded-2xl p-8 border border-slate-700/50">
          <h3 class="text-2xl font-bold text-white mb-6 flex items-center">
            <span class="text-3xl mr-3">📍</span>
            Incident Location
          </h3>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <h4 class="text-lg font-semibold text-green-300 mb-4">Coordinates</h4>
              <div class="space-y-3">
                <div class="flex justify-between">
                  <span class="text-slate-300">Latitude:</span>
                  <span class="text-white font-medium">{{ report.location_lat }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-slate-300">Longitude:</span>
                  <span class="text-white font-medium">{{ report.location_long }}</span>
                </div>
              </div>
            </div>
            <div>
              <h4 class="text-lg font-semibold text-blue-300 mb-4">Actions</h4>
              <div class="space-y-3">
                <a
                  :href="`https://www.google.com/maps?q=${report.location_lat},${report.location_long}`"
                  target="_blank"
                  class="inline-flex items-center px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors"
                >
                  <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                  View on Google Maps
                </a>
              </div>
            </div>
          </div>

          <!-- Simple Map Placeholder -->
          <div class="h-64 bg-slate-700 rounded-xl flex items-center justify-center">
            <div class="text-center">
              <svg class="w-16 h-16 text-slate-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <p class="text-slate-300">Map integration can be added here</p>
              <p class="text-slate-400 text-sm">{{ report.location_lat }}, {{ report.location_long }}</p>
            </div>
          </div>
        </div>

        <!-- No Location -->
        <div v-else class="text-center py-16">
          <div class="mx-auto w-24 h-24 bg-gradient-to-br from-slate-700 to-slate-800 rounded-full flex items-center justify-center mb-6">
            <span class="text-4xl">📍</span>
          </div>
          <h3 class="text-xl font-semibold text-slate-300 mb-2">No Location Data</h3>
          <p class="text-slate-500">Location coordinates were not provided for this incident.</p>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in-up {
  animation: fade-in-up 0.6s ease-out forwards;
}

.line-clamp-2 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}
</style>