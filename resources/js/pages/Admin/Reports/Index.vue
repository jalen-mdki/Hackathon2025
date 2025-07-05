<script setup lang="ts">
import { Head, router, usePage } from '@inertiajs/vue3';
import { ref, computed, watch } from 'vue';
import AppLayout from '@/layouts/AppLayout.vue';

interface Report {
  id: number;
  report_type: string;
  incident_type?: string;
  description: string;
  date_of_incident: string;
  severity?: string;
  industry?: string;
  reporter_name?: string;
  reporter_contact?: string;
  status: string;
  is_escalated: boolean;
  escalation_status: string;
  cause_of_death?: string;
  regulation_class_broken?: string;
  feedback_given: boolean;
  organization?: {
    id: number;
    name: string;
  };
  reported_by_user?: {
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
  }[];
  created_at: string;
  updated_at: string;
}

const { props } = usePage();
const reports = props.reports as { data: Report[], links: any[], meta: any };

// Search and filter states
const searchTerm = ref('');
const selectedStatus = ref('');
const selectedSeverity = ref('');
const selectedReportType = ref('');
const selectedIndustry = ref('');
const isEscalated = ref('');
const dateFrom = ref('');
const dateTo = ref('');
const showFilters = ref(false);

// Image slideshow state
const currentImageIndex = ref<{ [key: number]: number }>({});

// Available filter options
const statusOptions = ['Pending', 'In Progress', 'Completed', 'Closed', 'Under Review'];
const severityOptions = ['Low', 'Medium', 'High', 'Critical'];
const reportTypeOptions = ['Accident', 'Near Miss', 'Incident', 'Hazard', 'Environmental', 'Security'];
const industryOptions = ['Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Energy', 'Construction', 'Mining', 'Oil & Gas', 'Chemical', 'Transportation'];
const escalationOptions = [
  { value: '', label: 'All Reports' },
  { value: 'true', label: 'Escalated' },
  { value: 'false', label: 'Not Escalated' }
];

// Image slideshow methods
const nextImage = (reportId: number, totalImages: number) => {
  if (!currentImageIndex.value[reportId]) {
    currentImageIndex.value[reportId] = 0;
  }
  currentImageIndex.value[reportId] = (currentImageIndex.value[reportId] + 1) % totalImages;
};

const prevImage = (reportId: number, totalImages: number) => {
  if (!currentImageIndex.value[reportId]) {
    currentImageIndex.value[reportId] = 0;
  }
  currentImageIndex.value[reportId] = currentImageIndex.value[reportId] === 0 
    ? totalImages - 1 
    : currentImageIndex.value[reportId] - 1;
};

const goToImage = (reportId: number, index: number) => {
  currentImageIndex.value[reportId] = index;
};

// Utility functions
const getStatusColor = (status: string) => {
  const colors = {
    'Pending': 'bg-yellow-500',
    'In Progress': 'bg-blue-500',
    'Completed': 'bg-green-500',
    'Closed': 'bg-gray-500',
    'Under Review': 'bg-purple-500',
  };
  return colors[status] || 'bg-gray-500';
};

const getSeverityColor = (severity: string) => {
  const colors = {
    'Low': 'bg-green-500',
    'Medium': 'bg-yellow-500',
    'High': 'bg-orange-500',
    'Critical': 'bg-red-500',
  };
  return colors[severity] || 'bg-gray-500';
};

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

const getImageAttachments = (uploads: any[]) => {
  if (!uploads) return [];
  return uploads.filter(upload => 
    upload.file_type && upload.file_type.startsWith('image/')
  );
};

// Search and filter functionality
const performSearch = () => {
  const params = new URLSearchParams();
  
  if (searchTerm.value) params.append('search', searchTerm.value);
  if (selectedStatus.value) params.append('status', selectedStatus.value);
  if (selectedSeverity.value) params.append('severity', selectedSeverity.value);
  if (selectedReportType.value) params.append('report_type', selectedReportType.value);
  if (selectedIndustry.value) params.append('industry', selectedIndustry.value);
  if (isEscalated.value) params.append('escalated', isEscalated.value);
  if (dateFrom.value) params.append('date_from', dateFrom.value);
  if (dateTo.value) params.append('date_to', dateTo.value);

  router.get(route('admin.reports.index'), Object.fromEntries(params), {
    preserveState: true,
    preserveScroll: true,
  });
};

const clearFilters = () => {
  searchTerm.value = '';
  selectedStatus.value = '';
  selectedSeverity.value = '';
  selectedReportType.value = '';
  selectedIndustry.value = '';
  isEscalated.value = '';
  dateFrom.value = '';
  dateTo.value = '';
  performSearch();
};

// Active filters count
const activeFiltersCount = computed(() => {
  let count = 0;
  if (searchTerm.value) count++;
  if (selectedStatus.value) count++;
  if (selectedSeverity.value) count++;
  if (selectedReportType.value) count++;
  if (selectedIndustry.value) count++;
  if (isEscalated.value) count++;
  if (dateFrom.value) count++;
  if (dateTo.value) count++;
  return count;
});

// Watch for search term changes
watch(searchTerm, () => {
  if (searchTerm.value.length > 2 || searchTerm.value.length === 0) {
    performSearch();
  }
});
</script>

<template>
  <Head title="Safety Reports" />

  <AppLayout :breadcrumbs="[{ title: 'Dashboard', href: '/dashboard' }, { title: 'Safety Reports', href: '#' }]">
    <!-- Header -->
    <div class="relative overflow-hidden bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">
      <!-- Background Elements -->
      <div class="absolute inset-0 overflow-hidden">
        <div class="absolute -top-40 -right-32 w-80 h-80 rounded-full bg-blue-500/10 blur-3xl animate-pulse"></div>
        <div class="absolute -bottom-40 -left-32 w-80 h-80 rounded-full bg-indigo-500/10 blur-3xl animate-pulse delay-1000"></div>
      </div>
      
      <div class="relative px-6 py-12">
        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
          <div>
            <h1 class="text-4xl md:text-5xl font-bold text-white mb-4 tracking-tight">
              🚨 Safety Reports
            </h1>
            <p class="text-xl text-blue-100">
              Monitor and manage safety incidents across all organizations
            </p>
          </div>
          
          <div class="flex items-center gap-4">
            <a
              href="/admin/reports/create"
              class="inline-flex items-center px-6 py-3 bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white font-semibold rounded-xl shadow-lg transform hover:scale-105 transition-all duration-300"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              New Report
            </a>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="px-6 -mt-8 relative z-10">
      <!-- Search and Filters -->
      <div class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-lg rounded-2xl p-6 border border-slate-700/50 mb-8">
        <!-- Search Bar -->
        <div class="flex flex-col lg:flex-row gap-4 mb-6">
          <div class="flex-1 relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg class="h-5 w-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              v-model="searchTerm"
              type="text"
              placeholder="Search reports by type, description, reporter name..."
              class="block w-full pl-10 pr-4 py-3 border border-slate-600 rounded-xl bg-slate-700/50 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <button
            @click="showFilters = !showFilters"
            :class="[
              'inline-flex items-center px-6 py-3 rounded-xl font-medium transition-all duration-300',
              showFilters 
                ? 'bg-blue-500 text-white' 
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            ]"
          >
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.707A1 1 0 013 7V4z" />
            </svg>
            Filters
            <span v-if="activeFiltersCount > 0" class="ml-2 px-2 py-1 bg-red-500 text-white text-xs rounded-full">
              {{ activeFiltersCount }}
            </span>
          </button>
        </div>

        <!-- Filter Panel -->
        <div v-if="showFilters" class="border-t border-slate-600 pt-6">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <!-- Status Filter -->
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">Status</label>
              <select
                v-model="selectedStatus"
                class="block w-full px-3 py-2 border border-slate-600 rounded-lg bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Statuses</option>
                <option v-for="status in statusOptions" :key="status" :value="status">
                  {{ status }}
                </option>
              </select>
            </div>

            <!-- Severity Filter -->
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">Severity</label>
              <select
                v-model="selectedSeverity"
                class="block w-full px-3 py-2 border border-slate-600 rounded-lg bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Severities</option>
                <option v-for="severity in severityOptions" :key="severity" :value="severity">
                  {{ severity }}
                </option>
              </select>
            </div>

            <!-- Report Type Filter -->
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">Report Type</label>
              <select
                v-model="selectedReportType"
                class="block w-full px-3 py-2 border border-slate-600 rounded-lg bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Types</option>
                <option v-for="type in reportTypeOptions" :key="type" :value="type">
                  {{ type }}
                </option>
              </select>
            </div>

            <!-- Industry Filter -->
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">Industry</label>
              <select
                v-model="selectedIndustry"
                class="block w-full px-3 py-2 border border-slate-600 rounded-lg bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Industries</option>
                <option v-for="industry in industryOptions" :key="industry" :value="industry">
                  {{ industry }}
                </option>
              </select>
            </div>

            <!-- Escalation Filter -->
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">Escalation</label>
              <select
                v-model="isEscalated"
                class="block w-full px-3 py-2 border border-slate-600 rounded-lg bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option v-for="option in escalationOptions" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </div>

            <!-- Date From -->
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">Date From</label>
              <input
                v-model="dateFrom"
                type="date"
                class="block w-full px-3 py-2 border border-slate-600 rounded-lg bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <!-- Date To -->
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">Date To</label>
              <input
                v-model="dateTo"
                type="date"
                class="block w-full px-3 py-2 border border-slate-600 rounded-lg bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <!-- Filter Actions -->
          <div class="flex items-center justify-between">
            <button
              @click="clearFilters"
              class="text-slate-400 hover:text-white transition-colors"
            >
              Clear all filters
            </button>
            
            <button
              @click="performSearch"
              class="px-6 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
            >
              Apply Filters
            </button>
          </div>
        </div>
      </div>

      <!-- Reports Grid -->
      <div v-if="reports.data && reports.data.length > 0" class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 mb-8">
        <div
          v-for="(report, index) in reports.data"
          :key="report.id"
          :style="{ animationDelay: `${index * 100}ms` }"
          class="group bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-lg rounded-2xl overflow-hidden border border-slate-700/50 hover:border-blue-500/50 transition-all duration-300 animate-fade-in-up transform hover:scale-105"
        >
          <!-- Image Slideshow Section -->
          <div v-if="getImageAttachments(report.report_uploads).length > 0" class="relative h-48 bg-slate-700">
            <img 
              :src="getImageAttachments(report.report_uploads)[currentImageIndex[report.id] || 0]?.file_url || getImageAttachments(report.report_uploads)[0]?.file_url"
              :alt="`Report ${report.id} attachment`"
              class="w-full h-full object-cover"
            />
            
            <!-- Navigation arrows (only show if more than 1 image) -->
            <template v-if="getImageAttachments(report.report_uploads).length > 1">
              <button 
                @click="prevImage(report.id, getImageAttachments(report.report_uploads).length)"
                class="absolute left-2 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white rounded-full p-2 transition-all duration-200 opacity-0 group-hover:opacity-100"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              
              <button 
                @click="nextImage(report.id, getImageAttachments(report.report_uploads).length)"
                class="absolute right-2 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white rounded-full p-2 transition-all duration-200 opacity-0 group-hover:opacity-100"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>
              
              <!-- Image indicator dots -->
              <div class="absolute bottom-2 left-1/2 -translate-x-1/2 flex space-x-1">
                <button
                  v-for="(attachment, imgIndex) in getImageAttachments(report.report_uploads)"
                  :key="imgIndex"
                  @click="goToImage(report.id, imgIndex)"
                  :class="[
                    'w-2 h-2 rounded-full transition-all duration-200',
                    (currentImageIndex[report.id] || 0) === imgIndex 
                      ? 'bg-white' 
                      : 'bg-white/50 hover:bg-white/70'
                  ]"
                />
              </div>
              
              <!-- Image counter -->
              <div class="absolute top-2 right-2 bg-black/50 text-white text-xs px-2 py-1 rounded">
                {{ (currentImageIndex[report.id] || 0) + 1 }} / {{ getImageAttachments(report.report_uploads).length }}
              </div>
            </template>
          </div>
          
          <!-- Card Content -->
          <div class="p-6">
            <!-- Header with Status and Severity -->
            <div class="flex items-start justify-between mb-4">
              <div class="flex items-center space-x-2">
                <span :class="`px-2 py-1 rounded text-xs font-medium ${getStatusColor(report.status)} text-white`">
                  {{ report.status }}
                </span>
                <span v-if="report.severity" :class="`px-2 py-1 rounded text-xs font-medium ${getSeverityColor(report.severity)} text-white`">
                  {{ report.severity }}
                </span>
                <span v-if="report.is_escalated" class="px-2 py-1 rounded text-xs font-medium bg-red-500 text-white">
                  ⚠️ Escalated
                </span>
              </div>
            </div>
            
            <!-- Report Details -->
            <h3 class="text-lg font-bold text-white mb-2">{{ report.report_type }}</h3>
            <p v-if="report.incident_type" class="text-sm text-blue-300 mb-2">{{ report.incident_type }}</p>
            <p class="text-slate-300 text-sm mb-4 line-clamp-2">{{ report.description }}</p>
            
            <!-- Meta Information -->
            <div class="space-y-2 text-xs text-slate-400">
              <div class="flex items-center justify-between">
                <span>📅 Incident Date:</span>
                <span class="text-white">{{ formatDate(report.date_of_incident) }}</span>
              </div>
              
              <div v-if="report.organization" class="flex items-center justify-between">
                <span>🏢 Organization:</span>
                <span class="text-white">{{ report.organization.name }}</span>
              </div>
              
              <div v-if="report.reported_by_user" class="flex items-center justify-between">
                <span>👤 Reported by:</span>
                <span class="text-white">{{ report.reported_by_user.first_name }} {{ report.reported_by_user.last_name }}</span>
              </div>
              
              <div v-if="report.reporter_name" class="flex items-center justify-between">
                <span>📞 Reporter:</span>
                <span class="text-white">{{ report.reporter_name }}</span>
              </div>
              
              <div v-if="getImageAttachments(report.report_uploads).length > 0" class="flex items-center justify-between">
                <span>📎 Images:</span>
                <span class="text-white">{{ getImageAttachments(report.report_uploads).length }}</span>
              </div>
            </div>
            
            <!-- Escalation Section -->
            <div v-if="report.is_escalated && report.report_escalations && report.report_escalations.length > 0" class="mt-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
              <div class="flex items-center mb-2">
                <svg class="w-4 h-4 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.966-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
                <h4 class="text-sm font-semibold text-red-300">⚠️ Escalation Alert</h4>
              </div>
              
              <!-- Latest Escalation Details -->
              <div class="space-y-1 text-xs">
                <div class="flex items-start justify-between">
                  <span class="text-red-200">Escalated on:</span>
                  <span class="text-white font-medium">{{ formatDate(report.report_escalations[report.report_escalations.length - 1].escalated_at) }}</span>
                </div>
                
                <div v-if="report.report_escalations[report.report_escalations.length - 1].escalated_by_user" class="flex items-start justify-between">
                  <span class="text-red-200">Escalated by:</span>
                  <span class="text-white font-medium">
                    {{ report.report_escalations[report.report_escalations.length - 1].escalated_by_user.first_name }} 
                    {{ report.report_escalations[report.report_escalations.length - 1].escalated_by_user.last_name }}
                  </span>
                </div>
                
                <div class="mt-2">
                  <span class="text-red-200">Reason:</span>
                  <p class="text-white text-xs mt-1 line-clamp-2 bg-red-500/5 p-2 rounded border border-red-500/20">
                    {{ report.report_escalations[report.report_escalations.length - 1].escalation_reason }}
                  </p>
                </div>
                
                <!-- Multiple Escalations Indicator -->
                <div v-if="report.report_escalations.length > 1" class="mt-2 text-center">
                  <span class="text-red-300 text-xs bg-red-500/20 px-2 py-1 rounded">
                    {{ report.report_escalations.length }} escalation{{ report.report_escalations.length > 1 ? 's' : '' }} total
                  </span>
                </div>
              </div>
            </div>
            
            <!-- Actions -->
            <div class="flex items-center justify-between mt-6 pt-4 border-t border-slate-600">
              <a
                :href="`/admin/reports/${report.id}`"
                class="text-blue-400 hover:text-blue-300 text-sm font-medium transition-colors"
              >
                View Details →
              </a>
              
              <div class="flex items-center space-x-2">
                <a
                  :href="`/admin/reports/${report.id}/edit`"
                  class="p-2 text-slate-400 hover:text-white transition-colors"
                  title="Edit Report"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-16">
        <div class="mx-auto w-24 h-24 bg-gradient-to-br from-slate-700 to-slate-800 rounded-full flex items-center justify-center mb-6">
          <span class="text-4xl">📋</span>
        </div>
        <h3 class="text-xl font-semibold text-slate-300 mb-2">No reports found</h3>
        <p class="text-slate-500 mb-6">No safety reports match your current filters.</p>
        <a
          href="/admin/reports/create"
          class="inline-flex items-center px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white font-medium rounded-lg transition-colors"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Create First Report
        </a>
      </div>

      <!-- Pagination -->
      <div v-if="reports.links && reports.links.length > 3" class="flex justify-center">
        <nav class="flex items-center space-x-2">
          <template v-for="link in reports.links" :key="link.label">
            <button
              v-if="link.url"
              @click="router.get(link.url)"
              v-html="link.label"
              :class="[
                'px-4 py-2 text-sm font-medium rounded-lg transition-colors',
                link.active
                  ? 'bg-blue-500 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              ]"
            />
            <span
              v-else
              v-html="link.label"
              class="px-4 py-2 text-sm font-medium text-slate-500"
            />
          </template>
        </nav>
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