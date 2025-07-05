<script setup lang="ts">
import { Head, usePage } from '@inertiajs/vue3';
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import AppLayout from '@/layouts/AppLayout.vue';
import { Chart, registerables } from 'chart.js';

// Register Chart.js components
Chart.register(...registerables);

const { props } = usePage();
const organization = props.organization;
const reports = props.reports;
const employees = props.employees;
const hazards = props.hazards;
const emergencyResponsePlans = props.emergencyResponsePlans;
const userTrainings = props.userTrainings;

const activeTab = ref('Analytics');

const currentImageIndex = ref<{ [key: number]: number }>({});

// Add this method to handle image navigation
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


const tabs = [
  { name: 'Analytics', icon: '📊', count: null },
  { name: 'Reports', icon: '📋', count: reports?.length || 0 },
  { name: 'Employees', icon: '👥', count: employees?.length || 0 },
  { name: 'Hazards', icon: '⚠️', count: hazards?.length || 0 },
  { name: 'Emergency Response Plans', icon: '🚨', count: emergencyResponsePlans?.length || 0 },
  { name: 'User Training', icon: '🎓', count: userTrainings?.length || 0 },
];

const getIndustryColor = (industry: string) => {
  const colors = {
    'Technology': 'from-blue-500 to-cyan-500',
    'Healthcare': 'from-green-500 to-emerald-500',
    'Finance': 'from-yellow-500 to-orange-500',
    'Manufacturing': 'from-purple-500 to-pink-500',
    'Energy': 'from-red-500 to-rose-500',
    'Construction': 'from-gray-500 to-slate-500',
    'Mining': 'from-amber-500 to-yellow-600',
    'Oil & Gas': 'from-indigo-500 to-purple-600',
    'Chemical': 'from-teal-500 to-green-600',
    'Transportation': 'from-orange-500 to-red-500',
  };
  return colors[industry] || 'from-gray-500 to-gray-600';
};

// Add this function to your script setup section

const getStatusColor = (status: string) => {
  const statusColors = {
    // Report statuses
    'completed': 'bg-green-500',
    'pending': 'bg-yellow-500', 
    'in_progress': 'bg-blue-500',
    
    // Risk levels for hazards
    'High': 'bg-red-500',
    'Medium': 'bg-yellow-500',
    'Low': 'bg-green-500',
    
    // Training statuses  
    'active': 'bg-green-500',
    'inactive': 'bg-gray-500',
    
    // Default fallback
    'default': 'bg-gray-500'
  };
  
  return statusColors[status] || statusColors['default'];
};

// Get industry icon
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

// Analytics data computed
const analyticsData = computed(() => ({
  totalReports: reports?.length || 0,
  totalEmployees: employees?.length || 0,
  totalHazards: hazards?.length || 0,
  totalTrainings: userTrainings?.length || 0,
  completedTrainings: userTrainings?.filter(t => t.status === 'completed').length || 0,
  highRiskHazards: hazards?.filter(h => h.risk_level === 'High').length || 0,
  mediumRiskHazards: hazards?.filter(h => h.risk_level === 'Medium').length || 0,
  lowRiskHazards: hazards?.filter(h => h.risk_level === 'Low').length || 0,
  reportStatuses: {
    completed: reports?.filter(r => r.status === 'completed').length || 0,
    pending: reports?.filter(r => r.status === 'pending').length || 0,
    in_progress: reports?.filter(r => r.status === 'in_progress').length || 0,
  },
  trainingStatuses: {
    completed: userTrainings?.filter(t => t.status === 'completed').length || 0,
    pending: userTrainings?.filter(t => t.status === 'pending').length || 0,
    in_progress: userTrainings?.filter(t => t.status === 'in_progress').length || 0,
  }
}));

// Chart references
const hazardRiskChartRef = ref<HTMLCanvasElement | null>(null);
const reportStatusChartRef = ref<HTMLCanvasElement | null>(null);
const trainingStatusChartRef = ref<HTMLCanvasElement | null>(null);
const monthlyTrendsChartRef = ref<HTMLCanvasElement | null>(null);

onMounted(() => {
  // Initialize charts when component is mounted
  if (activeTab.value === 'Analytics') {
    setTimeout(() => {
      initHazardRiskChart();
      initReportStatusChart();
      initTrainingStatusChart();
      initMonthlyTrendsChart();
    }, 100);
  }
});

const initHazardRiskChart = () => {
  if (!hazardRiskChartRef.value) return;
  
  const ctx = hazardRiskChartRef.value.getContext('2d');
  if (!ctx) return;

  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['High Risk', 'Medium Risk', 'Low Risk'],
      datasets: [{
        data: [
          analyticsData.value.highRiskHazards,
          analyticsData.value.mediumRiskHazards,
          analyticsData.value.lowRiskHazards
        ],
        backgroundColor: [
          'rgba(239, 68, 68, 0.8)',    // red-500
          'rgba(234, 179, 8, 0.8)',    // yellow-500
          'rgba(34, 197, 94, 0.8)'     // green-500
        ],
        borderColor: [
          'rgba(239, 68, 68, 1)',
          'rgba(234, 179, 8, 1)',
          'rgba(34, 197, 94, 1)'
        ],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: 'right',
          labels: {
            color: '#E2E8F0', // slate-200
            font: {
              size: 12
            }
          }
        },
        title: {
          display: true,
          text: 'Hazard Risk Distribution',
          color: '#F8FAFC', // slate-50
          font: {
            size: 16
          }
        }
      },
      cutout: '70%'
    }
  });
};

const initReportStatusChart = () => {
  if (!reportStatusChartRef.value) return;
  
  const ctx = reportStatusChartRef.value.getContext('2d');
  if (!ctx) return;

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Completed', 'Pending', 'In Progress'],
      datasets: [{
        label: 'Reports',
        data: [
          analyticsData.value.reportStatuses.completed,
          analyticsData.value.reportStatuses.pending,
          analyticsData.value.reportStatuses.in_progress
        ],
        backgroundColor: [
          'rgba(34, 197, 94, 0.8)',   // green-500
          'rgba(234, 179, 8, 0.8)',   // yellow-500
          'rgba(59, 130, 246, 0.8)'    // blue-500
        ],
        borderColor: [
          'rgba(34, 197, 94, 1)',
          'rgba(234, 179, 8, 1)',
          'rgba(59, 130, 246, 1)'
        ],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            color: '#E2E8F0' // slate-200
          },
          grid: {
            color: 'rgba(226, 232, 240, 0.1)'
          }
        },
        x: {
          ticks: {
            color: '#E2E8F0' // slate-200
          },
          grid: {
            color: 'rgba(226, 232, 240, 0.1)'
          }
        }
      },
      plugins: {
        legend: {
          display: false
        },
        title: {
          display: true,
          text: 'Report Status Overview',
          color: '#F8FAFC', // slate-50
          font: {
            size: 16
          }
        }
      }
    }
  });
};

const initTrainingStatusChart = () => {
  if (!trainingStatusChartRef.value) return;
  
  const ctx = trainingStatusChartRef.value.getContext('2d');
  if (!ctx) return;

  new Chart(ctx, {
    type: 'pie',
    data: {
      labels: ['Completed', 'Pending', 'In Progress'],
      datasets: [{
        data: [
          analyticsData.value.trainingStatuses.completed,
          analyticsData.value.trainingStatuses.pending,
          analyticsData.value.trainingStatuses.in_progress
        ],
        backgroundColor: [
          'rgba(34, 197, 94, 0.8)',   // green-500
          'rgba(234, 179, 8, 0.8)',   // yellow-500
          'rgba(59, 130, 246, 0.8)'   // blue-500
        ],
        borderColor: [
          'rgba(34, 197, 94, 1)',
          'rgba(234, 179, 8, 1)',
          'rgba(59, 130, 246, 1)'
        ],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: 'right',
          labels: {
            color: '#E2E8F0', // slate-200
            font: {
              size: 12
            }
          }
        },
        title: {
          display: true,
          text: 'Training Completion',
          color: '#F8FAFC', // slate-50
          font: {
            size: 16
          }
        }
      }
    }
  });
};

const initMonthlyTrendsChart = () => {
  if (!monthlyTrendsChartRef.value) return;
  
  const ctx = monthlyTrendsChartRef.value.getContext('2d');
  if (!ctx) return;

  // Sample data - replace with your actual monthly data
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const reportsData = [5, 8, 7, 10, 12, 15, 18, 16, 14, 12, 9, 6];
  const hazardsData = [2, 3, 5, 4, 6, 8, 7, 5, 4, 3, 2, 1];

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: months,
      datasets: [
        {
          label: 'Safety Reports',
          data: reportsData,
          borderColor: 'rgba(59, 130, 246, 0.8)', // blue-500
          backgroundColor: 'rgba(59, 130, 246, 0.2)',
          tension: 0.3,
          fill: true
        },
        {
          label: 'Hazards Reported',
          data: hazardsData,
          borderColor: 'rgba(239, 68, 68, 0.8)', // red-500
          backgroundColor: 'rgba(239, 68, 68, 0.2)',
          tension: 0.3,
          fill: true
        }
      ]
    },
    options: {
      responsive: true,
      interaction: {
        mode: 'index',
        intersect: false,
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            color: '#E2E8F0' // slate-200
          },
          grid: {
            color: 'rgba(226, 232, 240, 0.1)'
          }
        },
        x: {
          ticks: {
            color: '#E2E8F0' // slate-200
          },
          grid: {
            color: 'rgba(226, 232, 240, 0.1)'
          }
        }
      },
      plugins: {
        legend: {
          position: 'top',
          labels: {
            color: '#E2E8F0' // slate-200
          }
        },
        title: {
          display: true,
          text: 'Monthly Trends',
          color: '#F8FAFC', // slate-50
          font: {
            size: 16
          }
        }
      }
    }
  });
};

// Watch for tab changes to initialize charts when Analytics tab is selected
watch(activeTab, (newTab) => {
  if (newTab === 'Analytics') {
    nextTick(() => {
      initHazardRiskChart();
      initReportStatusChart();
      initTrainingStatusChart();
      initMonthlyTrendsChart();
    });
  }
});
</script>

<template>
  <Head :title="organization.name" />

  <AppLayout :breadcrumbs="[{ title: 'Dashboard', href: '/dashboard' }, { title: 'Organizations', href: '/admin/organizations' }, { title: organization.name, href: '#' }]">
    <!-- Hero Header -->
    <div class="relative overflow-hidden bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">
      <!-- Animated background elements -->
      <div class="absolute inset-0 overflow-hidden">
        <div class="absolute -top-40 -right-32 w-80 h-80 rounded-full bg-blue-500/10 blur-3xl animate-pulse"></div>
        <div class="absolute -bottom-40 -left-32 w-80 h-80 rounded-full bg-indigo-500/10 blur-3xl animate-pulse delay-1000"></div>
      </div>
      
      <div class="relative px-6 py-12">
        <!-- Organization Header -->
        <div class="flex flex-col lg:flex-row items-start lg:items-center gap-6 mb-8">
          <!-- Organization Icon -->
          <div class="relative">
            <div :class="`inline-flex items-center justify-center w-24 h-24 rounded-3xl bg-gradient-to-br ${getIndustryColor(organization.industry)} text-4xl shadow-2xl`">
              {{ getIndustryIcon(organization.industry) }}
            </div>
            <!-- Status indicator -->
            <div class="absolute -top-2 -right-2 w-8 h-8 bg-green-500 rounded-full border-4 border-white shadow-lg animate-pulse flex items-center justify-center">
              <div class="w-3 h-3 bg-white rounded-full"></div>
            </div>
          </div>

          <!-- Organization Info -->
          <div class="flex-1">
            <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
              <div>
                <h1 class="text-4xl md:text-5xl font-bold text-white mb-2 tracking-tight">
                  {{ organization.name }}
                </h1>
                <div class="flex flex-wrap items-center gap-4 text-blue-100">
                  <span :class="`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium bg-gradient-to-r ${getIndustryColor(organization.industry)} text-white shadow-lg`">
                    {{ organization.industry }}
                  </span>
                  <div class="flex items-center">
                    <svg class="w-5 h-5 mr-2 text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    <span>{{ organization.contact_person }}</span>
                  </div>
                  <div class="flex items-center">
                    <svg class="w-5 h-5 mr-2 text-green-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    <span>{{ organization.contact_email }}</span>
                  </div>
                </div>
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
      <!-- Analytics Tab -->
      <div v-if="activeTab === 'Analytics'" class="space-y-8">
        <!-- Key Metrics Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
          <div class="bg-gradient-to-br from-blue-500/20 to-cyan-500/20 backdrop-blur-lg rounded-2xl p-6 border border-blue-500/30 transform hover:scale-105 transition-all duration-300">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-3xl font-bold text-white">{{ analyticsData.totalEmployees }}</p>
                <p class="text-sm text-blue-200">Total Employees</p>
              </div>
              <div class="p-3 bg-blue-500/20 rounded-xl">
                <svg class="w-8 h-8 text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
            </div>
          </div>

          <div class="bg-gradient-to-br from-green-500/20 to-emerald-500/20 backdrop-blur-lg rounded-2xl p-6 border border-green-500/30 transform hover:scale-105 transition-all duration-300">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-3xl font-bold text-white">{{ analyticsData.totalReports }}</p>
                <p class="text-sm text-green-200">Safety Reports</p>
              </div>
              <div class="p-3 bg-green-500/20 rounded-xl">
                <svg class="w-8 h-8 text-green-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>
          </div>
          <div class="bg-gradient-to-br from-red-500/20 to-rose-500/20 backdrop-blur-lg rounded-2xl p-6 border border-red-500/30 transform hover:scale-105 transition-all duration-300">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-3xl font-bold text-white">{{ analyticsData.highRiskHazards }}</p>
                <p class="text-sm text-red-200">High Risk Hazards</p>
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
                <p class="text-3xl font-bold text-white">{{ Math.round((analyticsData.completedTrainings / analyticsData.totalTrainings) * 100) || 0 }}%</p>
                <p class="text-sm text-purple-200">Training Completion</p>
              </div>
              <div class="p-3 bg-purple-500/20 rounded-xl">
                <svg class="w-8 h-8 text-purple-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
            </div>
          </div>
        </div>
        
          
        </div>
        <!-- Charts Section -->
        <div v-if="activeTab === 'Analytics'" class="grid grid-cols-2 lg:grid-cols-2 gap-6 pt-10">
        <!-- Charts -->
        <div class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-lg rounded-2xl p-6 border border-slate-700/50">
            <canvas ref="hazardRiskChartRef" height="300"></canvas>
        </div>
        <div class="pt-20 bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-lg rounded-2xl p-6 border border-slate-700/50">
            <canvas ref="monthlyTrendsChartRef" height="300"></canvas>
        </div>
        <div class="pt-20 bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-lg rounded-2xl p-6 border border-slate-700/50">
            <canvas ref="reportStatusChartRef" height="300"></canvas>
        </div>
        

        <!-- Quick Overview -->
        <div class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-lg rounded-2xl p-8 border border-slate-700/50">
          <h3 class="text-2xl font-bold text-white mb-6 flex items-center">
            <span class="text-3xl mr-3">📈</span>
            Quick Overview
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h4 class="text-lg font-semibold text-blue-300 mb-4">Safety Metrics</h4>
              <ul class="space-y-3">
                <li class="flex items-center justify-between text-slate-300">
                  <span>Total Safety Reports</span>
                  <span class="font-semibold text-white">{{ analyticsData.totalReports }}</span>
                </li>
                <li class="flex items-center justify-between text-slate-300">
                  <span>Active Hazards</span>
                  <span class="font-semibold text-white">{{ analyticsData.totalHazards }}</span>
                </li>
                <li class="flex items-center justify-between text-slate-300">
                  <span>Emergency Response Plans</span>
                  <span class="font-semibold text-white">{{ emergencyResponsePlans?.length || 0 }}</span>
                </li>
              </ul>
            </div>
            <div>
              <h4 class="text-lg font-semibold text-green-300 mb-4">Training Progress</h4>
              <ul class="space-y-3">
                <li class="flex items-center justify-between text-slate-300">
                  <span>Total Training Sessions</span>
                  <span class="font-semibold text-white">{{ analyticsData.totalTrainings }}</span>
                </li>
                <li class="flex items-center justify-between text-slate-300">
                  <span>Completed Sessions</span>
                  <span class="font-semibold text-white">{{ analyticsData.completedTrainings }}</span>
                </li>
                <li class="flex items-center justify-between text-slate-300">
                  <span>Completion Rate</span>
                  <span class="font-semibold text-white">{{ Math.round((analyticsData.completedTrainings / analyticsData.totalTrainings) * 100) || 0 }}%</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'Reports'" class="space-y-6">
        <div v-if="reports && reports.length > 0" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            <div
            v-for="(report, index) in reports"
            :key="report.id"
            :style="{ animationDelay: `${index * 100}ms` }"
            class="group bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-lg rounded-2xl overflow-hidden border border-slate-700/50 hover:border-blue-500/50 transition-all duration-300 animate-fade-in-up transform hover:scale-105"
            >
            <!-- Image Slideshow Section -->
            <div v-if="report.report_uploads && report.report_uploads.length > 0" class="relative h-48 bg-slate-700">
                <img 
                :src="report.report_uploads[currentImageIndex[report.id] || 0]?.url || report.report_uploads[0]?.file_url"
                :alt="`Report ${report.id} attachment`"
                class="w-full h-full object-cover"
                />
                
                <!-- Navigation arrows (only show if more than 1 image) -->
                <template v-if="report.report_uploads.length > 1">
                <button 
                    @click="prevImage(report.id, report.report_uploads.length)"
                    class="absolute left-2 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white rounded-full p-2 transition-all duration-200 opacity-0 group-hover:opacity-100"
                >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                    </svg>
                </button>
                
                <button 
                    @click="nextImage(report.id, report.report_uploads.length)"
                    class="absolute right-2 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white rounded-full p-2 transition-all duration-200 opacity-0 group-hover:opacity-100"
                >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                    </svg>
                </button>
                
                <!-- Image indicator dots -->
                <div class="absolute bottom-2 left-1/2 -translate-x-1/2 flex space-x-1">
                    <button
                    v-for="(attachment, imgIndex) in report.report_uploads"
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
                    {{ (currentImageIndex[report.id] || 0) + 1 }} / {{ report.report_uploads.length }}
                </div>
                </template>
            </div>
            
            <!-- Card Content -->
            <div class="p-6">
                <div class="flex items-start justify-between mb-4">
                <div class="p-3 bg-blue-500/20 rounded-xl">
                    <svg class="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                </div>
                <div :class="`w-3 h-3 rounded-full ${getStatusColor(report.status)}`"></div>
                </div>
                
                <h3 class="text-lg font-bold text-white mb-2">{{ report.report_type }}</h3>
                <p class="text-slate-300 text-sm mb-4 line-clamp-2">{{ report.description }}</p>
                
                <!-- Attachment count indicator -->
                <div v-if="report.report_uploads && report.report_uploads.length > 0" class="flex items-center mb-3 text-slate-400 text-xs">
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                </svg>
                {{ report.report_uploads.length }} attachment{{ report.report_uploads.length > 1 ? 's' : '' }}
                </div>
                
                <div class="flex items-center justify-between">
                <span :class="`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(report.status)} text-white`">
                    {{ report.status }}
                </span>
                </div>
            </div>
            </div>
        </div>
        
        <div v-else class="text-center py-16">
            <div class="mx-auto w-24 h-24 bg-gradient-to-br from-slate-700 to-slate-800 rounded-full flex items-center justify-center mb-6">
            <span class="text-4xl">📋</span>
            </div>
            <h3 class="text-xl font-semibold text-slate-300 mb-2">No reports found</h3>
            <p class="text-slate-500">No safety reports have been submitted yet.</p>
        </div>
        </div>

      <!-- Employees Tab -->
      <div v-if="activeTab === 'Employees'" class="space-y-6">
        <div v-if="employees && employees.length > 0" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          <div
            v-for="(employee, index) in employees"
            :key="employee.id"
            :style="{ animationDelay: `${index * 100}ms` }"
            class="group bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-lg rounded-2xl p-6 border border-slate-700/50 hover:border-green-500/50 transition-all duration-300 animate-fade-in-up transform hover:scale-105"
          >
            <div class="flex items-center mb-4">
              <div class="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-500 rounded-full flex items-center justify-center text-white font-bold text-lg mr-4">
                {{ employee.first_name.charAt(0) }}{{ employee.last_name.charAt(0) }}
              </div>
              <div class="flex-1">
                <h3 class="text-lg font-bold text-white">{{ employee.first_name }} {{ employee.last_name }}</h3>
                <p class="text-slate-300 text-sm">{{ employee.email }}</p>
              </div>
            </div>
            <div class="flex items-center justify-between">
              <span class="px-3 py-1 rounded-full text-xs font-medium bg-green-500/20 text-green-300 border border-green-500/30">
                Active
              </span>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-16">
          <div class="mx-auto w-24 h-24 bg-gradient-to-br from-slate-700 to-slate-800 rounded-full flex items-center justify-center mb-6">
            <span class="text-4xl">👥</span>
          </div>
          <h3 class="text-xl font-semibold text-slate-300 mb-2">No employees found</h3>
          <p class="text-slate-500">No employees have been added to this organization yet.</p>
        </div>
      </div>

      <!-- Hazards Tab -->
      <div v-if="activeTab === 'Hazards'" class="space-y-6">
        <div v-if="hazards && hazards.length > 0" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          <div
            v-for="(hazard, index) in hazards"
            :key="hazard.id"
            :style="{ animationDelay: `${index * 100}ms` }"
            class="group bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-lg rounded-2xl p-6 border border-slate-700/50 hover:border-red-500/50 transition-all duration-300 animate-fade-in-up transform hover:scale-105"
          >
            <div class="flex items-start justify-between mb-4">
              <div class="p-3 bg-red-500/20 rounded-xl">
                <svg class="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.966-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <div :class="`w-3 h-3 rounded-full ${getStatusColor(hazard.risk_level)}`"></div>
            </div>
            <h3 class="text-lg font-bold text-white mb-2 line-clamp-2">{{ hazard.description }}</h3>
            <div class="flex items-center justify-between">
              <span :class="`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(hazard.risk_level)} text-white`">
                {{ hazard.risk_level }} Risk
              </span>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-16">
          <div class="mx-auto w-24 h-24 bg-gradient-to-br from-slate-700 to-slate-800 rounded-full flex items-center justify-center mb-6">
            <span class="text-4xl">⚠️</span>
          </div>
          <h3 class="text-xl font-semibold text-slate-300 mb-2">No hazards reported</h3>
          <p class="text-slate-500">No hazards have been identified for this organization yet.</p>
        </div>
      </div>

      <!-- Emergency Response Plans Tab -->
      <div v-if="activeTab === 'Emergency Response Plans'" class="space-y-6">
        <div v-if="emergencyResponsePlans && emergencyResponsePlans.length > 0" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          <div
            v-for="(plan, index) in emergencyResponsePlans"
            :key="plan.id"
            :style="{ animationDelay: `${index * 100}ms` }"
            class="group bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-lg rounded-2xl p-6 border border-slate-700/50 hover:border-yellow-500/50 transition-all duration-300 animate-fade-in-up transform hover:scale-105"
          >
            <div class="flex items-start justify-between mb-4">
              <div class="p-3 bg-yellow-500/20 rounded-xl">
                <svg class="w-6 h-6 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.966-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
            </div>
            <h3 class="text-lg font-bold text-white mb-4">{{ plan.plan_name }}</h3>
            <a 
              :href="plan.document_url" 
              target="_blank" 
              class="inline-flex items-center px-4 py-2 bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white font-medium rounded-lg transition-all duration-300 transform hover:scale-105"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
              View Document
            </a>
          </div>
        </div>
        <div v-else class="text-center py-16">
          <div class="mx-auto w-24 h-24 bg-gradient-to-br from-slate-700 to-slate-800 rounded-full flex items-center justify-center mb-6">
            <span class="text-4xl">🚨</span>
          </div>
          <h3 class="text-xl font-semibold text-slate-300 mb-2">No emergency response plans</h3>
          <p class="text-slate-500">No emergency response plans have been uploaded yet.</p>
        </div>
      </div>

      <!-- User Training Tab -->
      <div v-if="activeTab === 'User Training'" class="space-y-6">
        <div v-if="userTrainings && userTrainings.length > 0" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          <div
            v-for="(training, index) in userTrainings"
            :key="training.id"
            :style="{ animationDelay: `${index * 100}ms` }"
            class="group bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-lg rounded-2xl p-6 border border-slate-700/50 hover:border-purple-500/50 transition-all duration-300 animate-fade-in-up transform hover:scale-105"
          >
            <div class="flex items-start justify-between mb-4">
              <div class="p-3 bg-purple-500/20 rounded-xl">
                <svg class="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <div :class="`w-3 h-3 rounded-full ${getStatusColor(training.status)}`"></div>
            </div>
            <h3 class="text-lg font-bold text-white mb-2">{{ training.training.name }}</h3>
            <div class="flex items-center justify-between">
              <span :class="`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(training.status)} text-white`">
                {{ training.status }}
              </span>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-16">
          <div class="mx-auto w-24 h-24 bg-gradient-to-br from-slate-700 to-slate-800 rounded-full flex items-center justify-center mb-6">
            <span class="text-4xl">🎓</span>
          </div>
          <h3 class="text-xl font-semibold text-slate-300 mb-2">No training sessions</h3>
          <p class="text-slate-500">No training sessions have been assigned yet.</p>
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

.line-clamp-1 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 1;
}

.line-clamp-2 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}
</style>