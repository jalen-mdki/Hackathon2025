<script setup lang="ts">
import { ref, computed } from 'vue';
import { Head } from '@inertiajs/vue3';
import AppLayout from '@/layouts/AppLayout.vue';
import { type BreadcrumbItem } from '@/types';

const breadcrumbs: BreadcrumbItem[] = [
  {
    title: 'Dashboard',
    href: '/dashboard',
  },
  {
    title: 'Users',
    href: '/admin/users',
  }
];

interface Organization {
  id: number;
  name: string;
}

interface User {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone: string | null;
}

interface OrganizationUser {
  id: number;
  role: string;
  is_active: boolean;
  is_ministry: boolean;
  disabled_at: string | null;
  created_at: string;
  updated_at: string;
  organization?: Organization;
  user: User;
}

const props = defineProps<{
  organization_users: {
    data: OrganizationUser[];
    links: any[];
    meta: any;
  }
}>();

// Reactive state
const searchQuery = ref('');
const selectedRole = ref('all');
const selectedStatus = ref('all');
const selectedOrganization = ref('all');
const viewMode = ref('list'); // 'grid' or 'list'

// Computed properties
const users = computed(() => {
  let filteredUsers = props.organization_users.data;

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filteredUsers = filteredUsers.filter(orgUser => 
      orgUser.user.first_name.toLowerCase().includes(query) ||
      orgUser.user.last_name.toLowerCase().includes(query) ||
      orgUser.user.email.toLowerCase().includes(query) ||
      (orgUser.user.phone && orgUser.user.phone.toLowerCase().includes(query)) ||
      (orgUser.organization?.name && orgUser.organization.name.toLowerCase().includes(query))
    );
  }

  // Apply role filter
  if (selectedRole.value !== 'all') {
    filteredUsers = filteredUsers.filter(orgUser => orgUser.role === selectedRole.value);
  }

  // Apply status filter
  if (selectedStatus.value !== 'all') {
    filteredUsers = filteredUsers.filter(orgUser => {
      const status = getStatusText(orgUser).toLowerCase();
      return status === selectedStatus.value;
    });
  }

  // Apply organization filter
  if (selectedOrganization.value !== 'all') {
    filteredUsers = filteredUsers.filter(orgUser => 
      orgUser.organization?.name === selectedOrganization.value
    );
  }

  return filteredUsers;
});

const uniqueRoles = computed(() => {
  const roles = new Set(props.organization_users.data.map(orgUser => orgUser.role));
  return Array.from(roles);
});

const uniqueOrganizations = computed(() => {
  const orgs = new Set(
    props.organization_users.data
      .map(orgUser => orgUser.organization?.name)
      .filter(Boolean)
  );
  return Array.from(orgs);
});

const totalUsers = computed(() => props.organization_users.data.length);
const activeUsers = computed(() => 
  props.organization_users.data.filter(orgUser => orgUser.is_active && !orgUser.disabled_at).length
);
const filteredResults = computed(() => users.value.length);

const hasActiveFilters = computed(() => {
  return searchQuery.value || 
         selectedRole.value !== 'all' || 
         selectedStatus.value !== 'all' || 
         selectedOrganization.value !== 'all';
});

// Helper functions
const formatRole = (role: string) => {
  return role.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

const getStatusColor = (orgUser: OrganizationUser) => {
  if (orgUser.disabled_at) return 'bg-red-500';
  if (!orgUser.is_active) return 'bg-yellow-500';
  return 'bg-green-500';
};

const getStatusText = (orgUser: OrganizationUser) => {
  if (orgUser.disabled_at) return 'Disabled';
  if (!orgUser.is_active) return 'Inactive';
  return 'Active';
};

const getInitials = (firstName: string, lastName: string) => {
  return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
};

const getRoleBadgeColor = (role: string) => {
  const colors = {
    'admin': 'bg-red-500',
    'supervisor': 'bg-blue-500', 
    'manager': 'bg-purple-500',
    'employee': 'bg-gray-500',
    'contractor': 'bg-orange-500'
  };
  return colors[role.toLowerCase()] || 'bg-gray-500';
};

const clearFilters = () => {
  searchQuery.value = '';
  selectedRole.value = 'all';
  selectedStatus.value = 'all';
  selectedOrganization.value = 'all';
};
</script>

<template>
  <Head title="Users" />
  <AppLayout :breadcrumbs="breadcrumbs">
    <!-- Hero Section with Gradient Background -->
    <div class="relative overflow-hidden">
      <!-- Gradient Background -->
      <div class="absolute inset-0 bg-gradient-to-br from-blue-900 via-blue-800 to-purple-900"></div>
      
      <!-- Content -->
      <div class="relative px-6 py-16 sm:py-20">
        <div class="text-center">
          <h1 class="text-4xl sm:text-5xl font-bold text-white mb-4">
            User <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-300 to-purple-300">Management</span>
          </h1>
          <p class="text-xl text-blue-100 mb-8 max-w-3xl mx-auto">
            Comprehensive user account management across all your partner organizations
          </p>
          
          <!-- Search and Controls -->
          <div class="flex flex-col sm:flex-row gap-4 justify-center items-center max-w-4xl mx-auto">
            <!-- Search Input -->
            <div class="relative flex-1 w-full max-w-md">
              <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <svg class="h-5 w-5 text-blue-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search users..."
                class="block w-full pl-12 pr-4 py-3 border-0 rounded-full bg-white/10 backdrop-blur-sm text-white placeholder-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-300 focus:bg-white/20 transition-all"
              />
            </div>
            
            <!-- Filter Dropdown -->
            <div class="flex gap-2">
              <select
                v-model="selectedRole"
                class="px-4 py-3 border-0 rounded-full bg-white/10 backdrop-blur-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-300 focus:bg-white/20 transition-all"
              >
                <option value="all" class="text-gray-800">All Roles</option>
                <option v-for="role in uniqueRoles" :key="role" :value="role" class="text-gray-800">
                  {{ formatRole(role) }}
                </option>
              </select>
              
              <!-- View Toggle -->
              <div class="flex rounded-full bg-white/10 backdrop-blur-sm p-1">
                <button
                  @click="viewMode = 'grid'"
                  :class="[
                    'px-4 py-2 rounded-full text-sm font-medium transition-all flex items-center gap-2',
                    viewMode === 'grid' ? 'bg-blue-500 text-white' : 'text-blue-200 hover:text-white'
                  ]"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                  </svg>
                  Grid
                </button>
                <button
                  @click="viewMode = 'list'"
                  :class="[
                    'px-4 py-2 rounded-full text-sm font-medium transition-all flex items-center gap-2',
                    viewMode === 'list' ? 'bg-blue-500 text-white' : 'text-blue-200 hover:text-white'
                  ]"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                  </svg>
                  List
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="px-6 -mt-8 relative z-10">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto">
        <!-- Total Users -->
        <div class="bg-gray-800 rounded-2xl p-6 border border-gray-700">
          <div class="flex items-center">
            <div class="p-3 rounded-lg bg-blue-500/20">
              <svg class="w-8 h-8 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-2xl font-bold text-white">{{ totalUsers }}</p>
              <p class="text-sm text-gray-400">Total Users</p>
            </div>
          </div>
        </div>

        <!-- Active Users -->
        <div class="bg-gray-800 rounded-2xl p-6 border border-gray-700">
          <div class="flex items-center">
            <div class="p-3 rounded-lg bg-green-500/20">
              <div class="w-3 h-3 bg-green-500 rounded-full"></div>
            </div>
            <div class="ml-4">
              <p class="text-2xl font-bold text-white">{{ activeUsers }}</p>
              <p class="text-sm text-gray-400">Active Users</p>
            </div>
          </div>
        </div>

        <!-- Filtered Results -->
        <div class="bg-gray-800 rounded-2xl p-6 border border-gray-700">
          <div class="flex items-center">
            <div class="p-3 rounded-lg bg-purple-500/20">
              <svg class="w-8 h-8 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-2xl font-bold text-white">{{ filteredResults }}</p>
              <p class="text-sm text-gray-400">Filtered Results</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Users Table -->
    <div class="px-6 py-8">
      <div class="max-w-7xl mx-auto">
        <!-- Table Controls -->
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div class="flex items-center gap-4">
            <h2 class="text-xl font-semibold text-white">Users</h2>
            <div v-if="hasActiveFilters" class="flex items-center gap-2">
              <span class="text-sm text-gray-400">{{ filteredResults }} of {{ totalUsers }} users</span>
              <button
                @click="clearFilters"
                class="text-sm text-blue-400 hover:text-blue-300 transition-colors"
              >
                Clear filters
              </button>
            </div>
          </div>
          
          <button 
                  @click="$inertia.visit('/admin/users/create')"
                  class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
                >
                  <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  Add User
                </button>
        </div>

        <!-- List View -->
        <div v-if="viewMode === 'list'" class="bg-gray-800 rounded-2xl border border-gray-700 overflow-hidden">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-700">
              <thead class="bg-gray-900/50">
                <tr>
                  <th class="px-6 py-4 text-left text-xs font-semibold text-gray-300 uppercase tracking-wider">
                    User
                  </th>
                  <th class="px-6 py-4 text-left text-xs font-semibold text-gray-300 uppercase tracking-wider">
                    Contact
                  </th>
                  <th class="px-6 py-4 text-left text-xs font-semibold text-gray-300 uppercase tracking-wider">
                    Role
                  </th>
                  <th class="px-6 py-4 text-left text-xs font-semibold text-gray-300 uppercase tracking-wider">
                    Organization
                  </th>
                  <th class="px-6 py-4 text-left text-xs font-semibold text-gray-300 uppercase tracking-wider">
                    Status
                  </th>
                  <th class="px-6 py-4 text-right text-xs font-semibold text-gray-300 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody class="bg-gray-800 divide-y divide-gray-700">
                <tr
                  v-for="orgUser in users"
                  :key="orgUser.id"
                  class="hover:bg-gray-700/50 transition-colors duration-150"
                >
                  <!-- User Info -->
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div class="flex-shrink-0 h-12 w-12">
                        <div class="h-12 w-12 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-sm font-semibold">
                          {{ getInitials(orgUser.user.first_name, orgUser.user.last_name) }}
                        </div>
                      </div>
                      <div class="ml-4">
                        <div class="text-sm font-semibold text-white">
                          {{ orgUser.user.first_name }} {{ orgUser.user.last_name }}
                        </div>
                        <div class="text-xs text-gray-400">
                          ID: {{ orgUser.user.id }}
                        </div>
                      </div>
                    </div>
                  </td>

                  <!-- Contact Info -->
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-white">{{ orgUser.user.email }}</div>
                    <div class="text-xs text-gray-400">
                      {{ orgUser.user.phone || 'No phone number' }}
                    </div>
                  </td>

                  <!-- Role -->
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex flex-col gap-1">
                      <span :class="[
                        'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium text-white',
                        getRoleBadgeColor(orgUser.role)
                      ]">
                        {{ formatRole(orgUser.role) }}
                      </span>
                      <span v-if="orgUser.is_ministry" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-500 text-white">
                        Ministry
                      </span>
                    </div>
                  </td>

                  <!-- Organization -->
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-white">
                      {{ orgUser.organization?.name || 'Unassigned' }}
                    </div>
                  </td>

                  <!-- Status -->
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div :class="['w-2 h-2 rounded-full mr-2', getStatusColor(orgUser)]"></div>
                      <span class="text-sm text-white">{{ getStatusText(orgUser) }}</span>
                    </div>
                  </td>

                  <!-- Actions -->
                  <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div class="flex items-center justify-end space-x-2">
                      <button
                        @click="$inertia.visit(`/admin/users/${orgUser.user.id}/edit`)"
                        class="inline-flex items-center px-3 py-1.5 bg-blue-600 text-white rounded-lg text-xs font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
                      >
                        <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                        Edit
                      </button>
                      <button
                        @click="$inertia.visit(`/admin/users/${orgUser.user.id}`)"
                        class="inline-flex items-center px-3 py-1.5 bg-gray-600 text-white rounded-lg text-xs font-medium hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors"
                      >
                        <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                        View Details
                      </button>
                    </div>
                  </td>
                </tr>

                <!-- Empty State -->
                <tr v-if="users.length === 0">
                  <td colspan="6" class="px-6 py-12 text-center">
                    <div class="flex flex-col items-center">
                      <svg class="w-12 h-12 text-gray-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                      </svg>
                      <h3 class="text-lg font-medium text-white mb-2">
                        {{ hasActiveFilters ? 'No matching users found' : 'No users found' }}
                      </h3>
                      <p class="text-sm text-gray-400 mb-4">
                        {{ hasActiveFilters ? 'Try adjusting your search or filters to find what you\'re looking for.' : 'Get started by adding your first user to the system.' }}
                      </p>
                      <div class="flex space-x-3">
                        <button
                          v-if="hasActiveFilters"
                          @click="clearFilters"
                          class="inline-flex items-center px-4 py-2 border border-gray-600 rounded-lg text-sm font-medium text-gray-300 bg-gray-800 hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
                        >
                          Clear filters
                        </button>
                        <button class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors">
                          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                          </svg>
                          Add User
                        </button>
                      </div>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Grid View -->
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="orgUser in users"
            :key="orgUser.id"
            class="bg-gray-800 rounded-2xl border border-gray-700 p-6 hover:border-gray-600 transition-all duration-200"
          >
            <!-- User Header -->
            <div class="flex items-center mb-4">
              <div class="h-16 w-16 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-lg font-semibold">
                {{ getInitials(orgUser.user.first_name, orgUser.user.last_name) }}
              </div>
              <div class="ml-4 flex-1">
                <div class="flex items-center justify-between">
                  <h3 class="text-lg font-semibold text-white">
                    {{ orgUser.user.first_name }} {{ orgUser.user.last_name }}
                  </h3>
                  <div :class="['w-3 h-3 rounded-full', getStatusColor(orgUser)]"></div>
                </div>
                <p class="text-sm text-gray-400">ID: {{ orgUser.user.id }}</p>
              </div>
            </div>

            <!-- Contact Info -->
            <div class="space-y-2 mb-4">
              <div class="flex items-center text-sm">
                <svg class="w-4 h-4 text-gray-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                </svg>
                <span class="text-white">{{ orgUser.user.email }}</span>
              </div>
              <div v-if="orgUser.user.phone" class="flex items-center text-sm">
                <svg class="w-4 h-4 text-gray-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
                <span class="text-white">{{ orgUser.user.phone }}</span>
              </div>
            </div>

            <!-- Role and Organization -->
            <div class="space-y-3 mb-4">
              <div class="flex flex-wrap gap-2">
                <span :class="[
                  'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium text-white',
                  getRoleBadgeColor(orgUser.role)
                ]">
                  {{ formatRole(orgUser.role) }}
                </span>
                <span v-if="orgUser.is_ministry" class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-500 text-white">
                  Ministry
                </span>
              </div>
              <div class="text-sm text-gray-400">
                <span class="font-medium">Organization:</span> 
                <span class="text-white">{{ orgUser.organization?.name || 'Unassigned' }}</span>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex space-x-3">
              <button
                @click="$inertia.visit(`/admin/users/${orgUser.user.id}/edit`)"
                class="flex-1 inline-flex items-center justify-center px-3 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
              >
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                Edit
              </button>
              <button
                @click="$inertia.visit(`/admin/users/${orgUser.user.id}`)"
                class="flex-1 inline-flex items-center justify-center px-3 py-2 bg-gray-600 text-white rounded-lg text-sm font-medium hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors"
              >
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                View
              </button>
            </div>
          </div>

          <!-- Empty State for Grid -->
          <div v-if="users.length === 0" class="col-span-full">
            <div class="text-center py-12">
              <svg class="w-12 h-12 text-gray-500 mb-4 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              <h3 class="text-lg font-medium text-white mb-2">
                {{ hasActiveFilters ? 'No matching users found' : 'No users found' }}
              </h3>
              <p class="text-sm text-gray-400 mb-4">
                {{ hasActiveFilters ? 'Try adjusting your search or filters to find what you\'re looking for.' : 'Get started by adding your first user to the system.' }}
              </p>
              <div class="flex justify-center space-x-3">
                <button
                  v-if="hasActiveFilters"
                  @click="clearFilters"
                  class="inline-flex items-center px-4 py-2 border border-gray-600 rounded-lg text-sm font-medium text-gray-300 bg-gray-800 hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
                >
                  Clear filters
                </button>
                <button class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors">
                  <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  Add User
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
/* Custom scrollbar for table */
.overflow-x-auto::-webkit-scrollbar {
  height: 6px;
}

.overflow-x-auto::-webkit-scrollbar-track {
  background: #374151;
  border-radius: 3px;
}

.overflow-x-auto::-webkit-scrollbar-thumb {
  background: #6b7280;
  border-radius: 3px;
}

.overflow-x-auto::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

/* Smooth gradient animation */
@keyframes gradient-shift {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

.bg-gradient-to-br {
  background-size: 400% 400%;
  animation: gradient-shift 15s ease infinite;
}
</style>