<template>
  <Head title="AI Scraper Data" />
  <AppLayout :breadcrumbs="breadcrumbs">
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
            Proactive
            <span class="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              Monitoring
            </span>
          </h1>
          <p class="text-xl text-slate-300 max-w-2xl mx-auto leading-relaxed">
            Monitor and analyze data from various sources
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
              v-model="form.search"
              type="text"
              placeholder="Search in title or content..."
              class="w-full pl-10 pr-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all duration-200 backdrop-blur-sm"
            />
          </div>

          <!-- Category Filter -->
          <div class="relative">
            <select
              v-model="form.category"
              class="appearance-none bg-white/10 border border-white/20 rounded-xl px-4 py-3 pr-10 text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all duration-200 backdrop-blur-sm min-w-[200px]"
            >
              <option value="" class="bg-slate-800 text-white">All Categories</option>
              <option value="news" class="bg-slate-800 text-white">News</option>
              <option value="social" class="bg-slate-800 text-white">Social</option>
            </select>
            <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
              <svg class="h-5 w-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>

          <!-- Source Filter -->
          <div class="relative flex-1 max-w-md">
            <input
              v-model="form.source"
              type="text"
              placeholder="Filter by source..."
              class="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all duration-200 backdrop-blur-sm"
            />
          </div>

          <!-- Filter Button -->
          <button 
            @click="filter"
            class="px-6 py-3 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-medium rounded-xl hover:from-blue-600 hover:to-cyan-600 transition-all duration-300 transform hover:scale-105 hover:shadow-lg"
          >
            Apply Filters
          </button>
        </div>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="px-6 -mt-6 relative z-10">
      <div class="max-w-7xl mx-auto">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div class="bg-gradient-to-br from-blue-500/20 to-cyan-500/20 backdrop-blur-lg rounded-2xl p-6 border border-blue-500/30">
            <div class="flex items-center">
              <div class="p-3 bg-blue-500/20 rounded-xl">
                <svg class="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-2xl font-bold text-white">{{ scrapers.length }}</p>
                <p class="text-sm text-slate-400">Total Items</p>
              </div>
            </div>
          </div>

          <div class="bg-gradient-to-br from-green-500/20 to-emerald-500/20 backdrop-blur-lg rounded-2xl p-6 border border-green-500/30">
            <div class="flex items-center">
              <div class="p-3 bg-green-500/20 rounded-xl">
                <svg class="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-2xl font-bold text-white">{{ newsCount }}</p>
                <p class="text-sm text-slate-400">News Items</p>
              </div>
            </div>
          </div>

          <div class="bg-gradient-to-br from-purple-500/20 to-pink-500/20 backdrop-blur-lg rounded-2xl p-6 border border-purple-500/30">
            <div class="flex items-center">
              <div class="p-3 bg-purple-500/20 rounded-xl">
                <svg class="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-2xl font-bold text-white">{{ socialCount }}</p>
                <p class="text-sm text-slate-400">Social Items</p>
              </div>
            </div>
          </div>

          <div class="bg-gradient-to-br from-amber-500/20 to-yellow-500/20 backdrop-blur-lg rounded-2xl p-6 border border-amber-500/30">
            <div class="flex items-center">
              <div class="p-3 bg-amber-500/20 rounded-xl">
                <svg class="w-6 h-6 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div class="ml-4">
                <p class="text-2xl font-bold text-white">{{ latestItemDate }}</p>
                <p class="text-sm text-slate-400">Last Updated</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Data Display -->
        <div
          class="transition-all duration-500 ease-out space-y-4"
          :class="isLoaded ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'"
        >
          <div
            v-for="(item, index) in scrapers"
            :key="item.id"
            :style="{ animationDelay: `${index * 50}ms` }"
            class="group relative overflow-hidden rounded-2xl transition-all duration-500 hover:scale-[1.01] hover:shadow-xl animate-fade-in-up bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-lg border border-slate-700/50 p-6"
          >
            <!-- Gradient overlay based on category -->
            <div 
              :class="`absolute inset-0 bg-gradient-to-br ${item.category === 'news' ? 'from-blue-500/10 to-cyan-500/10' : 'from-green-500/10 to-emerald-500/10'} opacity-0 group-hover:opacity-20 transition-opacity duration-500`"
            ></div>
            
            <div class="flex items-start justify-between gap-6">
              <!-- Category Icon -->
              <div class="relative flex-shrink-0">
                <div 
                  :class="`inline-flex items-center justify-center w-14 h-14 rounded-xl ${item.category === 'news' ? 'bg-gradient-to-br from-blue-500 to-cyan-500' : 'bg-gradient-to-br from-green-500 to-emerald-500'} text-xl shadow-lg`"
                >
                  {{ item.category === 'news' ? '📰' : '💬' }}
                </div>
              </div>

              <!-- Content -->
              <div class="flex-1 min-w-0">
                <div class="flex items-start justify-between mb-3">
                  <h3 class="text-lg font-bold text-white group-hover:text-blue-300 transition-colors duration-300 line-clamp-1">
                    {{ item.title }}
                  </h3>
                  <div 
                    :class="`px-3 py-1 rounded-full text-xs font-medium ${item.category === 'news' ? 'bg-gradient-to-r from-blue-500 to-cyan-500' : 'bg-gradient-to-r from-green-500 to-emerald-500'} text-white shadow-lg`"
                  >
                    {{ item.source }}
                  </div>
                </div>

                <div class="space-y-2 mb-4">
                  <div class="flex items-center text-slate-300">
                    <svg class="w-4 h-4 mr-2 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span class="text-sm">{{ formatDate(item.published_at) }}</span>
                  </div>
                  <div class="flex items-center text-slate-300">
                    <svg class="w-4 h-4 mr-2 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                    </svg>
                    <span class="text-sm truncate">{{ item.url }}</span>
                  </div>
                </div>

                <p v-if="item.content" class="mt-1 text-sm text-slate-400 line-clamp-2">
                  {{ item.content }}
                </p>
              </div>

              <!-- View Button -->
              <div class="flex-shrink-0">
                <a 
                  :href="item.url" 
                  target="_blank"
                  class="group/btn relative inline-flex items-center justify-center px-4 py-2 bg-gradient-to-r from-slate-700 to-slate-800 hover:from-slate-600 hover:to-slate-700 text-white font-medium rounded-xl transition-all duration-300 transform hover:scale-105 hover:shadow-lg overflow-hidden"
                >
                  <div class="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover/btn:translate-x-full transition-transform duration-1000"></div>
                  <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                  View
                </a>
              </div>
            </div>
          </div>

          <!-- Empty State -->
          <div
            v-if="scrapers.length === 0"
            class="text-center py-16"
          >
            <div class="mx-auto w-24 h-24 bg-gradient-to-br from-slate-700 to-slate-800 rounded-full flex items-center justify-center mb-6">
              <svg class="w-12 h-12 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <h3 class="text-xl font-semibold text-slate-300 mb-2">No data found</h3>
            <p class="text-slate-500">Try adjusting your search criteria or filters</p>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { Head, Link, usePage, useForm } from '@inertiajs/vue3';
import { ref, computed, onMounted } from 'vue';
import AppLayout from '@/layouts/AppLayout.vue';
import { type BreadcrumbItem } from '@/types';

const { props } = usePage();
const scrapers = props.scrapers;
const filters = props.filters || {};

const breadcrumbs: BreadcrumbItem[] = [
  {
    title: 'Dashboard',
    href: '/dashboard',
  },
  {
    title: 'AI Scraper',
    href: '/ai-scrapers',
  },
];

const isLoaded = ref(false);

// Form handling with Inertia
const form = useForm({
  category: filters.category || '',
  source: filters.source || '',
  search: filters.search || ''
});

// Computed properties
const newsCount = computed(() => {
  return scrapers.filter(item => item.category === 'news').length;
});

const socialCount = computed(() => {
  return scrapers.filter(item => item.category === 'social').length;
});

const latestItemDate = computed(() => {
  if (scrapers.length === 0) return 'N/A';
  const dates = scrapers.map(item => new Date(item.published_at));
  const latest = new Date(Math.max(...dates));
  return latest.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
});

// Format date for display
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// Filter function
const filter = () => {
  form.get(route('ai-scrapers.index'), {
    preserveState: true,
    replace: true
  });
};

// Animation trigger
onMounted(() => {
  setTimeout(() => {
    isLoaded.value = true;
  }, 100);
});
</script>

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
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>