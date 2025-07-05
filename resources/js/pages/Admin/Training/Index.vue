<script setup lang="ts">
import { Head, router } from '@inertiajs/vue3';
import { ref, computed, onMounted } from 'vue';
import AppLayout from '@/layouts/AppLayout.vue';
import { type BreadcrumbItem } from '@/types';

// Props from controller
interface Props {
  trainings: Array<any>;
  stats: {
    total_trainings: number;
    industries_covered: number;
    active_programs: number;
    total_enrollments: number;
  };
  industries: Array<string>;
  filters?: {
    search?: string;
    industry?: string;
  };
}

const breadcrumbs: BreadcrumbItem[] = [
  {
    title: 'Dashboard',
    href: '/dashboard',
  },
  {
    title: 'Training',
    href: '/admin/trainings',
  },
];

const props = defineProps<Props>();

// Reactive data for UI state - no need for filters from props since we handle client-side
const searchQuery = ref('');
const selectedIndustry = ref('');
const viewMode = ref('grid');
const isLoaded = ref(false);

// Computed properties
const filteredTrainings = computed(() => {
  let filtered = props.trainings;

  // Client-side filtering for immediate feedback
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(training => 
      training.name.toLowerCase().includes(query) ||
      (training.description && training.description.toLowerCase().includes(query)) ||
      (training.industry && training.industry.toLowerCase().includes(query))
    );
  }

  if (selectedIndustry.value) {
    filtered = filtered.filter(training => training.industry === selectedIndustry.value);
  }

  return filtered;
});

// Methods - No need for API calls since data comes from Inertia props

const editTraining = (training: any) => {
  router.visit(`/trainings/${training.id}/edit`);
};

const viewDetails = (training: any) => {
  router.visit(`/trainings/${training.id}`);
};

const formatDate = (dateString: string) => {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

// Handle search input - pure client-side filtering
const handleSearchInput = () => {
  // No debouncing needed since it's just filtering the existing data
};

// Handle industry change - pure client-side filtering
const handleIndustryChange = () => {
  // No API call needed since it's just filtering the existing data
};

// Get industry color
const getIndustryColor = (industry: string) => {
  const colors = {
    'Mining': 'from-amber-500 to-yellow-600',
    'Construction': 'from-gray-500 to-slate-500',
    'Manufacturing': 'from-purple-500 to-pink-500',
    'Healthcare': 'from-green-500 to-emerald-500',
    'Energy': 'from-red-500 to-rose-500',
    'Transportation': 'from-orange-500 to-red-500',
    'Agriculture': 'from-green-600 to-lime-500',
    'Technology': 'from-blue-500 to-cyan-500',
    'Oil & Gas': 'from-indigo-500 to-purple-600',
    'Chemical': 'from-teal-500 to-green-600',
  };
  return colors[industry] || 'from-gray-500 to-gray-600';
};

// Get industry icon
const getIndustryIcon = (industry: string) => {
  const icons = {
    'Mining': '⛏️',
    'Construction': '🏗️',
    'Manufacturing': '🏭',
    'Healthcare': '🏥',
    'Energy': '⚡',
    'Transportation': '🚛',
    'Agriculture': '🌾',
    'Technology': '💻',
    'Oil & Gas': '🛢️',
    'Chemical': '🧪',
  };
  return icons[industry] || '📚';
};

// Animation trigger
onMounted(() => {
  setTimeout(() => {
    isLoaded.value = true;
  }, 100);
});
</script>

<template>
  <Head title="Training" />

  <AppLayout :breadcrumbs="[{ title: 'Dashboard', href: '/dashboard' }, { title: 'Training', href: '#' }]">
    <!-- Hero Header with Gradient Background -->
    <div class="relative overflow-hidden bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900 px-6 pt-8 pb-12">
      <!-- Animated background elements -->
      <div class="absolute inset-0 overflow-hidden">
        <div class="absolute -top-40 -right-32 w-80 h-80 rounded-full bg-blue-500/10 blur-3xl animate-pulse"></div>
        <div class="absolute -bottom-40 -left-32 w-80 h-80 rounded-full bg-indigo-500/10 blur-3xl animate-pulse delay-1000"></div>
      </div>
      
      <div class="relative max-w-7xl mx-auto">
        <div class="text-center mb-8">
          <h1 class="text-4xl md:text-5xl font-bold text-white mb-4 tracking-tight">
            Training
            <span class="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              Management
            </span>
          </h1>
          <p class="text-xl text-slate-300 max-w-2xl mx-auto leading-relaxed">
            Comprehensive training program tracking and management across all industries
          </p>
        </div>

        <!-- Search and Filter Bar -->
        <div class="flex flex-col lg:flex-row gap-4 items-center justify-between bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
          <!-- Search Input -->
          <div class="relative flex-1 max-w-md w-full">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg class="h-5 w-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search trainings..."
              class="w-full pl-10 pr-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all duration-200 backdrop-blur-sm"
            />
          </div>

          <!-- Industry Filter -->
          <div class="relative">
            <select
              v-model="selectedIndustry"
              class="appearance-none bg-white/10 border border-white/20 rounded-xl px-4 py-3 pr-10 text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all duration-200 backdrop-blur-sm min-w-[200px]"
            >
              <option value="" class="bg-slate-800 text-white">All Industries</option>
              <option
                v-for="industry in industries"
                :key="industry"
                :value="industry"
                class="bg-slate-800 text-white"
              >
                {{ industry }}
              </option>
            </select>
            <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
              <svg class="h-5 w-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>

          <!-- View Toggle -->
          <div class="flex bg-white/10 rounded-xl p-1 backdrop-blur-sm border border-white/20">
            <button
              @click="viewMode = 'grid'"
              :class="[
                'px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200',
                viewMode === 'grid'
                  ? 'bg-blue-500 text-white shadow-lg'
                  : 'text-slate-300 hover:text-white hover:bg-white/10'
              ]"
            >
              Grid
            </button>
            <button
              @click="viewMode = 'list'"
              :class="[
                'px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200',
                viewMode === 'list'
                  ? 'bg-blue-500 text-white shadow-lg'
                  : 'text-slate-300 hover:text-white hover:bg-white/10'
              ]"
            >
              List
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content with Theme-Aware Background -->
    <div class="bg-gray-50 dark:bg-gray-900 min-h-screen px-6 -mt-6 relative z-10">
      <div class="max-w-7xl mx-auto pt-6">
        <!-- Stats Cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div class="bg-gradient-to-br from-blue-500/20 to-cyan-500/20 backdrop-blur-lg rounded-2xl p-6 border border-blue-500/30 bg-white/80 dark:bg-gray-800/80">
            <div class="flex items-center">
              <div class="p-3 bg-blue-500/20 rounded-xl">
                <svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ stats.total_trainings || 0 }}</p>
                <p class="text-sm text-gray-600 dark:text-gray-400">Total Trainings</p>
              </div>
            </div>
          </div>

          <div class="bg-gradient-to-br from-green-500/20 to-emerald-500/20 backdrop-blur-lg rounded-2xl p-6 border border-green-500/30 bg-white/80 dark:bg-gray-800/80">
            <div class="flex items-center">
              <div class="p-3 bg-green-500/20 rounded-xl">
                <svg class="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ stats.industries_covered || 0 }}</p>
                <p class="text-sm text-gray-600 dark:text-gray-400">Industries Covered</p>
              </div>
            </div>
          </div>

          <div class="bg-gradient-to-br from-purple-500/20 to-pink-500/20 backdrop-blur-lg rounded-2xl p-6 border border-purple-500/30 bg-white/80 dark:bg-gray-800/80">
            <div class="flex items-center">
              <div class="p-3 bg-purple-500/20 rounded-xl">
                <svg class="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ stats.active_programs || 0 }}</p>
                <p class="text-sm text-gray-600 dark:text-gray-400">Active Programs</p>
              </div>
            </div>
          </div>

          <div class="bg-gradient-to-br from-orange-500/20 to-red-500/20 backdrop-blur-lg rounded-2xl p-6 border border-orange-500/30 bg-white/80 dark:bg-gray-800/80">
            <div class="flex items-center">
              <div class="p-3 bg-orange-500/20 rounded-xl">
                <svg class="w-6 h-6 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 715 0z" />
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ stats.total_enrollments || 0 }}</p>
                <p class="text-sm text-gray-600 dark:text-gray-400">Total Enrollments</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Trainings Display -->
        <div
          :class="[
            'transition-all duration-500 ease-out',
            isLoaded ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4',
            viewMode === 'grid'
              ? 'grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6'
              : 'space-y-4'
          ]"
        >
          <div
            v-for="(training, index) in filteredTrainings"
            :key="training.id"
            :style="{ animationDelay: `${index * 100}ms` }"
            :class="[
              'group relative overflow-hidden rounded-2xl transition-all duration-500 hover:scale-[1.02] hover:shadow-2xl animate-fade-in-up bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700',
              viewMode === 'grid'
                ? 'p-6'
                : 'p-6 flex items-center gap-6'
            ]"
          >
            <!-- Gradient overlay -->
            <div :class="`absolute inset-0 bg-gradient-to-br ${getIndustryColor(training.industry || 'General')} opacity-0 group-hover:opacity-10 transition-opacity duration-500`"></div>
            
            <!-- Industry Icon -->
            <div class="relative">
              <div :class="`inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br ${getIndustryColor(training.industry || 'General')} text-2xl shadow-lg`">
                {{ getIndustryIcon(training.industry || 'General') }}
              </div>
              <!-- Status indicator -->
              <div class="absolute -top-1 -right-1 w-5 h-5 bg-green-500 rounded-full border-2 border-white dark:border-gray-800 shadow-lg animate-pulse"></div>
            </div>

            <!-- Content -->
            <div :class="viewMode === 'grid' ? 'mt-4' : 'flex-1'">
              <div class="flex items-start justify-between mb-3">
                <h3 class="text-xl font-bold text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors duration-300 line-clamp-1">
                  {{ training.name }}
                </h3>
                <div :class="`px-3 py-1 rounded-full text-xs font-medium bg-gradient-to-r ${getIndustryColor(training.industry || 'General')} text-white shadow-lg`">
                  {{ training.industry || 'General' }}
                </div>
              </div>

              <div class="space-y-2 mb-6">
                <div class="flex items-center text-gray-600 dark:text-gray-400">
                  <svg class="w-4 h-4 mr-2 text-blue-500 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <span class="text-sm">{{ formatDate(training.created_at) }}</span>
                </div>
                <div class="flex items-center text-gray-600 dark:text-gray-400">
                  <svg class="w-4 h-4 mr-2 text-green-500 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 715 0z" />
                  </svg>
                  <span class="text-sm">{{ training.enrolled_count || 0 }} enrolled</span>
                </div>
              </div>

              <div class="mb-6">
                <p class="text-gray-600 dark:text-gray-400 text-sm line-clamp-2">
                  {{ training.description || 'No description available' }}
                </p>
              </div>

              <!-- Action Buttons -->
              <div :class="viewMode === 'grid' ? 'space-y-3' : 'flex gap-3'">
                <button
                  @click="editTraining(training)"
                  class="group/btn relative inline-flex items-center justify-center px-6 py-3 bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white font-medium rounded-xl transition-all duration-300 transform hover:scale-105 hover:shadow-lg overflow-hidden"
                >
                  <!-- Button shine effect -->
                  <div class="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover/btn:translate-x-full transition-transform duration-1000"></div>
                  <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                  Edit Training
                </button>
                
                <button
                  @click="viewDetails(training)"
                  class="group/btn relative inline-flex items-center justify-center px-6 py-3 bg-gradient-to-r from-gray-600 to-gray-700 hover:from-gray-500 hover:to-gray-600 dark:from-gray-700 dark:to-gray-800 dark:hover:from-gray-600 dark:hover:to-gray-700 text-white font-medium rounded-xl transition-all duration-300 transform hover:scale-105 hover:shadow-lg overflow-hidden"
                >
                  <div class="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover/btn:translate-x-full transition-transform duration-1000"></div>
                  <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m5.231 13.481L15 17.25m-4.5-15H5.625c-.621 0-1.125.504-1.125 1.125v16.5c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Zm3.75 11.625a2.625 2.625 0 1 1-5.25 0 2.625 2.625 0 0 1 5.25 0Z" />
                  </svg>
                  View Details
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div
          v-if="filteredTrainings.length === 0"
          class="text-center py-16"
        >
          <div class="mx-auto w-24 h-24 bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-800 rounded-full flex items-center justify-center mb-6">
            <svg class="w-12 h-12 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <h3 class="text-xl font-semibold text-gray-700 dark:text-gray-300 mb-2">No trainings found</h3>
          <p class="text-gray-500 dark:text-gray-400">Try adjusting your search criteria or filters</p>
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