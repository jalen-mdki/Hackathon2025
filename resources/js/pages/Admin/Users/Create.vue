<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useForm } from '@inertiajs/vue3';
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
  },
  {
    title: 'Add User',
    href: '/admin/users/create',
  }
];

interface Organization {
  id: number;
  name: string;
  industry?: string;
}

const props = defineProps<{
  organizations: Organization[];
}>();

// Form state
const form = useForm({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  address: '',
  password: '',
  password_confirmation: '',
  is_admin: false,
  organization_id: null as number | null,
  role: 'employee',
});

// Reactive state
const showPassword = ref(false);
const showPasswordConfirmation = ref(false);

// Computed properties
const isFormValid = computed(() => {
  return form.first_name && 
         form.last_name && 
         form.email && 
         form.password && 
         form.password_confirmation &&
         form.password === form.password_confirmation &&
         (form.is_admin || form.organization_id);
});

const availableRoles = computed(() => [
  { value: 'employee', label: 'Employee' },
  { value: 'supervisor', label: 'Supervisor' },
  { value: 'manager', label: 'Manager' },
  { value: 'admin', label: 'Admin' },
  { value: 'contractor', label: 'Contractor' }
]);

// Watch for admin status changes
watch(() => form.is_admin, (newValue) => {
  if (newValue) {
    form.organization_id = null;
    form.role = 'admin';
  } else {
    form.role = 'employee';
  }
});

// Methods
const submit = () => {
  form.post('/admin/users', {
    onSuccess: () => {
      // Handle success (will be redirected by controller)
    },
    onError: (errors) => {
      console.log('Validation errors:', errors);
    }
  });
};

const generatePassword = () => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
  let password = '';
  for (let i = 0; i < 12; i++) {
    password += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  form.password = password;
  form.password_confirmation = password;
};
</script>

<template>
  <Head title="Add User" />
  <AppLayout :breadcrumbs="breadcrumbs">
    <!-- Hero Section -->
    <div class="relative overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-br from-blue-900 via-blue-800 to-purple-900"></div>
      <div class="relative px-6 py-16">
        <div class="text-center">
          <h1 class="text-4xl font-bold text-white mb-4">
            Add New <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-300 to-purple-300">User</span>
          </h1>
          <p class="text-xl text-blue-100 max-w-2xl mx-auto">
            Create a new user account and assign them to an organization
          </p>
        </div>
      </div>
    </div>

    <!-- Form Section -->
    <div class="px-6 py-8 -mt-8 relative z-10">
      <div class="max-w-4xl mx-auto p-10">
        <form @submit.prevent="submit" class="bg-gray-800 rounded-2xl border border-gray-700 overflow-hidden">
          <div class="p-8">
            <!-- Personal Information Section -->
            <div class="mb-8">
              <h2 class="text-xl font-semibold text-white mb-6 flex items-center">
                <svg class="w-6 h-6 mr-3 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                Personal Information
              </h2>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- First Name -->
                <div>
                  <label for="first_name" class="block text-sm font-medium text-gray-300 mb-2">
                    First Name <span class="text-red-400">*</span>
                  </label>
                  <input
                    id="first_name"
                    v-model="form.first_name"
                    type="text"
                    required
                    class="block w-full px-4 py-3 border border-gray-600 rounded-lg bg-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                    placeholder="Enter first name"
                  />
                  <div v-if="form.errors.first_name" class="mt-1 text-sm text-red-400">
                    {{ form.errors.first_name }}
                  </div>
                </div>

                <!-- Last Name -->
                <div>
                  <label for="last_name" class="block text-sm font-medium text-gray-300 mb-2">
                    Last Name <span class="text-red-400">*</span>
                  </label>
                  <input
                    id="last_name"
                    v-model="form.last_name"
                    type="text"
                    required
                    class="block w-full px-4 py-3 border border-gray-600 rounded-lg bg-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                    placeholder="Enter last name"
                  />
                  <div v-if="form.errors.last_name" class="mt-1 text-sm text-red-400">
                    {{ form.errors.last_name }}
                  </div>
                </div>

                <!-- Email -->
                <div>
                  <label for="email" class="block text-sm font-medium text-gray-300 mb-2">
                    Email Address <span class="text-red-400">*</span>
                  </label>
                  <input
                    id="email"
                    v-model="form.email"
                    type="email"
                    required
                    class="block w-full px-4 py-3 border border-gray-600 rounded-lg bg-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                    placeholder="Enter email address"
                  />
                  <div v-if="form.errors.email" class="mt-1 text-sm text-red-400">
                    {{ form.errors.email }}
                  </div>
                </div>

                <!-- Phone -->
                <div>
                  <label for="phone" class="block text-sm font-medium text-gray-300 mb-2">
                    Phone Number
                  </label>
                  <input
                    id="phone"
                    v-model="form.phone"
                    type="tel"
                    class="block w-full px-4 py-3 border border-gray-600 rounded-lg bg-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                    placeholder="Enter phone number"
                  />
                  <div v-if="form.errors.phone" class="mt-1 text-sm text-red-400">
                    {{ form.errors.phone }}
                  </div>
                </div>

                <!-- Address -->
                <div class="md:col-span-2">
                  <label for="address" class="block text-sm font-medium text-gray-300 mb-2">
                    Address
                  </label>
                  <textarea
                    id="address"
                    v-model="form.address"
                    rows="3"
                    class="block w-full px-4 py-3 border border-gray-600 rounded-lg bg-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                    placeholder="Enter full address"
                  ></textarea>
                  <div v-if="form.errors.address" class="mt-1 text-sm text-red-400">
                    {{ form.errors.address }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Account Security Section -->
            <div class="mb-8">
              <h2 class="text-xl font-semibold text-white mb-6 flex items-center">
                <svg class="w-6 h-6 mr-3 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
                Account Security
              </h2>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Password -->
                <div>
                  <label for="password" class="block text-sm font-medium text-gray-300 mb-2">
                    Password <span class="text-red-400">*</span>
                  </label>
                  <div class="relative">
                    <input
                      id="password"
                      v-model="form.password"
                      :type="showPassword ? 'text' : 'password'"
                      required
                      class="block w-full px-4 py-3 pr-12 border border-gray-600 rounded-lg bg-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                      placeholder="Enter password"
                    />
                    <button
                      type="button"
                      @click="showPassword = !showPassword"
                      class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-300"
                    >
                      <svg v-if="showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                      </svg>
                      <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </button>
                  </div>
                  <button
                    type="button"
                    @click="generatePassword"
                    class="mt-2 text-sm text-blue-400 hover:text-blue-300 transition-colors"
                  >
                    Generate secure password
                  </button>
                  <div v-if="form.errors.password" class="mt-1 text-sm text-red-400">
                    {{ form.errors.password }}
                  </div>
                </div>

                <!-- Confirm Password -->
                <div>
                  <label for="password_confirmation" class="block text-sm font-medium text-gray-300 mb-2">
                    Confirm Password <span class="text-red-400">*</span>
                  </label>
                  <div class="relative">
                    <input
                      id="password_confirmation"
                      v-model="form.password_confirmation"
                      :type="showPasswordConfirmation ? 'text' : 'password'"
                      required
                      class="block w-full px-4 py-3 pr-12 border border-gray-600 rounded-lg bg-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                      placeholder="Confirm password"
                    />
                    <button
                      type="button"
                      @click="showPasswordConfirmation = !showPasswordConfirmation"
                      class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-300"
                    >
                      <svg v-if="showPasswordConfirmation" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                      </svg>
                      <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </button>
                  </div>
                  <div v-if="form.password && form.password_confirmation && form.password !== form.password_confirmation" class="mt-1 text-sm text-red-400">
                    Passwords do not match
                  </div>
                </div>
              </div>
            </div>

            <!-- Role & Organization Section -->
            <div class="mb-8">
              <h2 class="text-xl font-semibold text-white mb-6 flex items-center">
                <svg class="w-6 h-6 mr-3 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
                Role & Organization
              </h2>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Admin Toggle -->
                <div class="md:col-span-2">
                  <div class="flex items-center p-4 bg-gray-700 rounded-lg border border-gray-600">
                    <input
                      id="is_admin"
                      v-model="form.is_admin"
                      type="checkbox"
                      class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label for="is_admin" class="ml-3 text-sm font-medium text-white">
                      System Administrator
                    </label>
                    <div class="ml-2">
                      <svg class="w-4 h-4 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                  </div>
                  <p class="mt-2 text-sm text-gray-400">
                    Administrators have full system access and don't need to be assigned to an organization.
                  </p>
                </div>

                <!-- Organization (only if not admin) -->
                <div v-if="!form.is_admin">
                  <label for="organization_id" class="block text-sm font-medium text-gray-300 mb-2">
                    Organization <span class="text-red-400">*</span>
                  </label>
                  <select
                    id="organization_id"
                    v-model="form.organization_id"
                    required
                    class="block w-full px-4 py-3 border border-gray-600 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                  >
                    <option value="" disabled>Select an organization</option>
                    <option v-for="org in organizations" :key="org.id" :value="org.id">
                      {{ org.name }}
                    </option>
                  </select>
                  <div v-if="form.errors.organization_id" class="mt-1 text-sm text-red-400">
                    {{ form.errors.organization_id }}
                  </div>
                </div>

                <!-- Role -->
                <div>
                  <label for="role" class="block text-sm font-medium text-gray-300 mb-2">
                    Role <span class="text-red-400">*</span>
                  </label>
                  <select
                    id="role"
                    v-model="form.role"
                    :disabled="form.is_admin"
                    required
                    class="block w-full px-4 py-3 border border-gray-600 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <option v-for="role in availableRoles" :key="role.value" :value="role.value">
                      {{ role.label }}
                    </option>
                  </select>
                  <div v-if="form.errors.role" class="mt-1 text-sm text-red-400">
                    {{ form.errors.role }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Form Actions -->
          <div class="px-8 py-6 bg-gray-900/50 border-t border-gray-700">
            <div class="flex items-center justify-between">
              <button
                type="button"
                @click="$inertia.visit('/admin/users')"
                class="inline-flex items-center px-6 py-3 border border-gray-600 rounded-lg text-sm font-medium text-gray-300 bg-gray-800 hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors"
              >
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
                Cancel
              </button>
              
              <button
                type="submit"
                :disabled="!isFormValid || form.processing"
                class="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg v-if="form.processing" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <svg v-else class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                {{ form.processing ? 'Creating User...' : 'Create User' }}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
/* Custom scrollbar */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #374151;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #6b7280;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

/* Form animations */
.form-section {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>