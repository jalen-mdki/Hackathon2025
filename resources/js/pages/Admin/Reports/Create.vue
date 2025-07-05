<script setup lang="ts">
import { Head, useForm, usePage } from '@inertiajs/vue3';
import { ref, computed } from 'vue';
import AppLayout from '@/layouts/AppLayout.vue';

interface Organization {
  id: number;
  name: string;
  industry: string;
}

interface User {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
}

const { props } = usePage();
const organizations = props.organizations as Organization[];
const users = props.users as User[];

// Form state
const form = useForm({
  organization_id: '',
  report_type: '',
  incident_type: '',
  description: '',
  date_of_incident: '',
  location_lat: '',
  location_long: '',
  severity: '',
  industry: '',
  reporter_name: '',
  reporter_contact: '',
  status: 'Pending',
  reported_by_user_id: '',
  assigned_to: '',
  cause_of_death: '',
  regulation_class_broken: '',
  attachments: [] as File[],
});

// UI state
const currentStep = ref(1);
const totalSteps = 4;
const showLocationFields = ref(false);
const dragOver = ref(false);

// Form options
const reportTypes = [
  'Accident',
  'Near Miss',
  'Incident',
  'Hazard Identification',
  'Environmental Issue',
  'Security Breach',
  'Equipment Failure',
  'Safety Violation',
  'Chemical Spill',
  'Fire/Explosion',
  'Injury',
  'Property Damage'
];

const incidentTypes = [
  'Slip/Trip/Fall',
  'Cut/Laceration',
  'Burn',
  'Chemical Exposure',
  'Electrical Shock',
  'Equipment Malfunction',
  'Vehicle Accident',
  'Fire',
  'Explosion',
  'Structural Collapse',
  'Environmental Release',
  'Security Incident',
  'Other'
];

const severityLevels = [
  { value: 'Low', label: 'Low - Minor impact', color: 'from-green-500 to-emerald-500' },
  { value: 'Medium', label: 'Medium - Moderate impact', color: 'from-yellow-500 to-orange-500' },
  { value: 'High', label: 'High - Significant impact', color: 'from-orange-500 to-red-500' },
  { value: 'Critical', label: 'Critical - Severe impact', color: 'from-red-500 to-rose-500' }
];

const statusOptions = [
  'Pending',
  'In Progress',
  'Under Review',
  'Completed',
  'Closed'
];

const industries = [
  'Technology',
  'Healthcare',
  'Finance',
  'Manufacturing',
  'Energy',
  'Construction',
  'Mining',
  'Oil & Gas',
  'Chemical',
  'Transportation',
  'Agriculture',
  'Education',
  'Government',
  'Other'
];

// Computed properties
const progress = computed(() => (currentStep.value / totalSteps) * 100);
const canProceed = computed(() => {
  switch (currentStep.value) {
    case 1:
      return form.organization_id && form.report_type && form.description && form.date_of_incident;
    case 2:
      return form.reported_by_user_id;
    case 3:
      return true; // Optional fields
    case 4:
      return true; // Review step
    default:
      return false;
  }
});

const selectedOrganization = computed(() => 
  organizations.find(org => org.id === parseInt(form.organization_id))
);

// File handling
const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files) {
    const newFiles = Array.from(target.files);
    
    // Validate file types and sizes
    const validFiles = newFiles.filter(file => {
      const validTypes = [
        // Image types
        'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp', 'image/bmp', 'image/tiff',
        // Video types
        'video/mp4', 'video/webm', 'video/ogg', 'video/avi', 'video/mov', 'video/wmv', 'video/flv', 'video/mkv',
        // Document types
        'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      ];
      const isValidType = validTypes.includes(file.type);
      const maxSize = file.type.startsWith('video/') ? 100 * 1024 * 1024 : 10 * 1024 * 1024; // 100MB for videos, 10MB for others
      const isValidSize = file.size <= maxSize;
      
      if (!isValidType) {
        alert(`File "${file.name}" has an invalid type. Please upload images, videos, PDF, or Word documents.`);
        return false;
      }
      
      if (!isValidSize) {
        const maxSizeText = file.type.startsWith('video/') ? '100MB' : '10MB';
        alert(`File "${file.name}" is too large. Maximum file size is ${maxSizeText}.`);
        return false;
      }
      
      return true;
    });
    
    // Check for duplicates
    const uniqueFiles = validFiles.filter(newFile => {
      return !form.attachments.some(existingFile => 
        existingFile.name === newFile.name && existingFile.size === newFile.size
      );
    });
    
    if (uniqueFiles.length !== newFiles.length) {
      const duplicateCount = newFiles.length - uniqueFiles.length;
      alert(`${duplicateCount} duplicate file(s) were skipped.`);
    }
    
    form.attachments = [...form.attachments, ...uniqueFiles];
    
    // Reset the input value to allow selecting the same file again if needed
    target.value = '';
  }
};

const handleFileDrop = (event: DragEvent) => {
  dragOver.value = false;
  if (event.dataTransfer?.files) {
    const newFiles = Array.from(event.dataTransfer.files);
    
    // Validate file types and sizes
    const validFiles = newFiles.filter(file => {
      const validTypes = [
        // Image types
        'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp', 'image/bmp', 'image/tiff',
        // Video types
        'video/mp4', 'video/webm', 'video/ogg', 'video/avi', 'video/mov', 'video/wmv', 'video/flv', 'video/mkv',
        // Document types
        'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      ];
      const isValidType = validTypes.includes(file.type);
      const maxSize = file.type.startsWith('video/') ? 100 * 1024 * 1024 : 10 * 1024 * 1024; // 100MB for videos, 10MB for others
      const isValidSize = file.size <= maxSize;
      
      if (!isValidType) {
        alert(`File "${file.name}" has an invalid type. Please upload images, videos, PDF, or Word documents.`);
        return false;
      }
      
      if (!isValidSize) {
        const maxSizeText = file.type.startsWith('video/') ? '100MB' : '10MB';
        alert(`File "${file.name}" is too large. Maximum file size is ${maxSizeText}.`);
        return false;
      }
      
      return true;
    });
    
    // Check for duplicates
    const uniqueFiles = validFiles.filter(newFile => {
      return !form.attachments.some(existingFile => 
        existingFile.name === newFile.name && existingFile.size === newFile.size
      );
    });
    
    if (uniqueFiles.length !== newFiles.length) {
      const duplicateCount = newFiles.length - uniqueFiles.length;
      alert(`${duplicateCount} duplicate file(s) were skipped.`);
    }
    
    form.attachments = [...form.attachments, ...uniqueFiles];
  }
};

// Get file type icon
const getFileIcon = (file: File) => {
  if (file.type.startsWith('image/')) {
    return '🖼️';
  } else if (file.type.startsWith('video/')) {
    return '🎥';
  } else if (file.type.includes('pdf')) {
    return '📄';
  } else if (file.type.includes('word') || file.type.includes('document')) {
    return '📝';
  }
  return '📎';
};

// Get file type label
const getFileTypeLabel = (file: File) => {
  if (file.type.startsWith('image/')) {
    return 'Image';
  } else if (file.type.startsWith('video/')) {
    return 'Video';
  } else if (file.type.includes('pdf')) {
    return 'PDF';
  } else if (file.type.includes('word') || file.type.includes('document')) {
    return 'Document';
  }
  return 'File';
};

const removeFile = (index: number) => {
  form.attachments.splice(index, 1);
};

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// Navigation
const nextStep = () => {
  if (currentStep.value < totalSteps && canProceed.value) {
    currentStep.value++;
  }
};

const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--;
  }
};

const goToStep = (step: number) => {
  currentStep.value = step;
};

// Location handling
const getCurrentLocation = () => {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        form.location_lat = position.coords.latitude.toString();
        form.location_long = position.coords.longitude.toString();
        showLocationFields.value = true;
      },
      (error) => {
        console.error('Error getting location:', error);
        alert('Unable to get current location. Please enter coordinates manually.');
        showLocationFields.value = true;
      }
    );
  } else {
    alert('Geolocation is not supported by this browser.');
    showLocationFields.value = true;
  }
};

// Form submission
const submit = () => {
  // Create FormData to handle file uploads properly
  const formData = new FormData();
  
  // Add all form fields
  Object.keys(form.data()).forEach(key => {
    if (key === 'attachments') {
      // Handle multiple file uploads
      form.attachments.forEach((file, index) => {
        formData.append(`attachments[${index}]`, file);
      });
    } else if (form[key] !== null && form[key] !== '') {
      formData.append(key, form[key]);
    }
  });

  // Submit using Inertia with FormData
  form.post('/admin/reports', {
    data: formData,
    forceFormData: true,
    onSuccess: () => {
      // Handle success - redirect or show success message
      console.log('Report submitted successfully');
    },
    onError: (errors) => {
      console.error('Form errors:', errors);
      // Handle errors - could scroll to first error, show notifications, etc.
    },
    onFinish: () => {
      // Always runs after success or error
      console.log('Form submission finished');
    }
  });
};
</script>

<template>
  <Head title="Create New Report" />

  <AppLayout :breadcrumbs="[
    { title: 'Dashboard', href: '/dashboard' }, 
    { title: 'Reports', href: '/admin/reports' }, 
    { title: 'Create New Report', href: '#' }
  ]">
    <!-- Hero Header -->
    <div class="relative overflow-hidden bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">
      <div class="absolute inset-0 overflow-hidden">
        <div class="absolute -top-40 -right-32 w-80 h-80 rounded-full bg-blue-500/10 blur-3xl animate-pulse"></div>
        <div class="absolute -bottom-40 -left-32 w-80 h-80 rounded-full bg-indigo-500/10 blur-3xl animate-pulse delay-1000"></div>
      </div>
      
      <div class="relative px-6 py-12">
        <div class="text-center">
          <h1 class="text-4xl md:text-5xl font-bold text-white mb-4 tracking-tight">
            🚨 Submit New Safety Report
          </h1>
          <p class="text-xl text-blue-100 mb-8">
            Report incidents, hazards, and safety concerns
          </p>
          
          <!-- Progress Bar -->
          <div class="max-w-md mx-auto">
            <div class="flex items-center justify-between mb-4">
              <div 
                v-for="step in totalSteps" 
                :key="step"
                :class="[
                  'w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold transition-all duration-300',
                  step <= currentStep 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-white/20 text-white/60'
                ]"
              >
                {{ step }}
              </div>
            </div>
            <div class="w-full bg-white/20 rounded-full h-2 mb-4">
              <div 
                class="bg-gradient-to-r from-blue-500 to-cyan-500 h-2 rounded-full transition-all duration-300"
                :style="{ width: `${progress}%` }"
              ></div>
            </div>
            <div class="flex justify-between text-sm text-blue-200">
              <span>Basic Info</span>
              <span>Reporter</span>
              <span>Details</span>
              <span>Review</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Form Content -->
    <div class="px-6 -mt-8 relative z-10">
      <div class="max-w-4xl mx-auto">
        <form @submit.prevent="submit" class="space-y-8">
          
          <!-- Step 1: Basic Information -->
          <div v-if="currentStep === 1" class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-lg rounded-2xl p-8 border border-slate-700/50">
            <h2 class="text-2xl font-bold text-white mb-6 flex items-center">
              <span class="text-3xl mr-3">📋</span>
              Basic Information
            </h2>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Organization -->
              <div>
                <label class="block text-sm font-medium text-slate-300 mb-2">
                  Organization <span class="text-red-400">*</span>
                </label>
                <select 
                  v-model="form.organization_id"
                  class="block w-full px-3 py-3 border border-slate-600 rounded-lg bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                >
                  <option value="">Select Organization</option>
                  <option v-for="org in organizations" :key="org.id" :value="org.id">
                    {{ org.name }} ({{ org.industry }})
                  </option>
                </select>
                <div v-if="form.errors.organization_id" class="text-red-400 text-sm mt-1">
                  {{ form.errors.organization_id }}
                </div>
              </div>

              <!-- Report Type -->
              <div>
                <label class="block text-sm font-medium text-slate-300 mb-2">
                  Report Type <span class="text-red-400">*</span>
                </label>
                <select 
                  v-model="form.report_type"
                  class="block w-full px-3 py-3 border border-slate-600 rounded-lg bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                >
                  <option value="">Select Report Type</option>
                  <option v-for="type in reportTypes" :key="type" :value="type">
                    {{ type }}
                  </option>
                </select>
                <div v-if="form.errors.report_type" class="text-red-400 text-sm mt-1">
                  {{ form.errors.report_type }}
                </div>
              </div>

              <!-- Incident Type -->
              <div>
                <label class="block text-sm font-medium text-slate-300 mb-2">
                  Incident Type
                </label>
                <select 
                  v-model="form.incident_type"
                  class="block w-full px-3 py-3 border border-slate-600 rounded-lg bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Select Incident Type</option>
                  <option v-for="type in incidentTypes" :key="type" :value="type">
                    {{ type }}
                  </option>
                </select>
              </div>

              <!-- Date of Incident -->
              <div>
                <label class="block text-sm font-medium text-slate-300 mb-2">
                  Date of Incident <span class="text-red-400">*</span>
                </label>
                <input 
                  v-model="form.date_of_incident"
                  type="date"
                  class="block w-full px-3 py-3 border border-slate-600 rounded-lg bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
                <div v-if="form.errors.date_of_incident" class="text-red-400 text-sm mt-1">
                  {{ form.errors.date_of_incident }}
                </div>
              </div>

              <!-- Severity -->
              <div>
                <label class="block text-sm font-medium text-slate-300 mb-2">
                  Severity Level
                </label>
                <div class="grid grid-cols-2 gap-2">
                  <button
                    v-for="severity in severityLevels"
                    :key="severity.value"
                    type="button"
                    @click="form.severity = severity.value"
                    :class="[
                      'p-3 rounded-lg border-2 transition-all duration-300 text-sm font-medium',
                      form.severity === severity.value
                        ? `border-white bg-gradient-to-r ${severity.color} text-white`
                        : 'border-slate-600 bg-slate-700/50 text-slate-300 hover:border-slate-500'
                    ]"
                  >
                    {{ severity.label }}
                  </button>
                </div>
              </div>

              <!-- Industry -->
              <div>
                <label class="block text-sm font-medium text-slate-300 mb-2">
                  Industry
                </label>
                <select 
                  v-model="form.industry"
                  class="block w-full px-3 py-3 border border-slate-600 rounded-lg bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Select Industry</option>
                  <option v-for="industry in industries" :key="industry" :value="industry">
                    {{ industry }}
                  </option>
                </select>
              </div>
            </div>

            <!-- Description -->
            <div class="mt-6">
              <label class="block text-sm font-medium text-slate-300 mb-2">
                Description <span class="text-red-400">*</span>
              </label>
              <textarea 
                v-model="form.description"
                rows="6"
                class="block w-full px-3 py-3 border border-slate-600 rounded-lg bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Provide a detailed description of the incident, including what happened, when, where, and any contributing factors..."
                required
              ></textarea>
              <div v-if="form.errors.description" class="text-red-400 text-sm mt-1">
                {{ form.errors.description }}
              </div>
            </div>
          </div>

          <!-- Step 2: Reporter Information -->
          <div v-if="currentStep === 2" class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-lg rounded-2xl p-8 border border-slate-700/50">
            <h2 class="text-2xl font-bold text-white mb-6 flex items-center">
              <span class="text-3xl mr-3">👤</span>
              Reporter Information
            </h2>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Reported by User -->
              <div>
                <label class="block text-sm font-medium text-slate-300 mb-2">
                  System User <span class="text-red-400">*</span>
                </label>
                <select 
                  v-model="form.reported_by_user_id"
                  class="block w-full px-3 py-3 border border-slate-600 rounded-lg bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                >
                  <option value="">Select User</option>
                  <option v-for="user in users" :key="user.id" :value="user.id">
                    {{ user.first_name }} {{ user.last_name }} ({{ user.email }})
                  </option>
                </select>
                <div v-if="form.errors.reported_by_user_id" class="text-red-400 text-sm mt-1">
                  {{ form.errors.reported_by_user_id }}
                </div>
              </div>

              <!-- Assigned To -->
              <div>
                <label class="block text-sm font-medium text-slate-300 mb-2">
                  Assign To
                </label>
                <select 
                  v-model="form.assigned_to"
                  class="block w-full px-3 py-3 border border-slate-600 rounded-lg bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Assign to User (Optional)</option>
                  <option v-for="user in users" :key="user.id" :value="user.id">
                    {{ user.first_name }} {{ user.last_name }} ({{ user.email }})
                  </option>
                </select>
              </div>

              <!-- Reporter Name -->
              <div>
                <label class="block text-sm font-medium text-slate-300 mb-2">
                  Reporter Name
                </label>
                <input 
                  v-model="form.reporter_name"
                  type="text"
                  class="block w-full px-3 py-3 border border-slate-600 rounded-lg bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Name of person reporting (if different)"
                />
              </div>

              <!-- Reporter Contact -->
              <div>
                <label class="block text-sm font-medium text-slate-300 mb-2">
                  Reporter Contact
                </label>
                <input 
                  v-model="form.reporter_contact"
                  type="text"
                  class="block w-full px-3 py-3 border border-slate-600 rounded-lg bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Phone number or email"
                />
              </div>

              <!-- Status -->
              <div>
                <label class="block text-sm font-medium text-slate-300 mb-2">
                  Initial Status
                </label>
                <select 
                  v-model="form.status"
                  class="block w-full px-3 py-3 border border-slate-600 rounded-lg bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option v-for="status in statusOptions" :key="status" :value="status">
                    {{ status }}
                  </option>
                </select>
              </div>
            </div>
          </div>

          <!-- Step 3: Additional Details -->
          <div v-if="currentStep === 3" class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-lg rounded-2xl p-8 border border-slate-700/50">
            <h2 class="text-2xl font-bold text-white mb-6 flex items-center">
              <span class="text-3xl mr-3">📍</span>
              Additional Details
            </h2>

            <!-- Location Section -->
            <div class="mb-8">
              <h3 class="text-lg font-semibold text-white mb-4">Location Information</h3>
              <div class="flex items-center space-x-4 mb-4">
                <button
                  type="button"
                  @click="getCurrentLocation"
                  class="inline-flex items-center px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors"
                >
                  <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  </svg>
                  Get Current Location
                </button>
                <button
                  type="button"
                  @click="showLocationFields = !showLocationFields"
                  class="inline-flex items-center px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
                >
                  <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  Enter Manually
                </button>
              </div>

              <div v-if="showLocationFields" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-slate-300 mb-2">Latitude</label>
                  <input 
                    v-model="form.location_lat"
                    type="number"
                    step="any"
                    class="block w-full px-3 py-3 border border-slate-600 rounded-lg bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., 40.7128"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-slate-300 mb-2">Longitude</label>
                  <input 
                    v-model="form.location_long"
                    type="number"
                    step="any"
                    class="block w-full px-3 py-3 border border-slate-600 rounded-lg bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., -74.0060"
                  />
                </div>
              </div>
            </div>

            <!-- Additional Fields -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="block text-sm font-medium text-slate-300 mb-2">
                  Cause of Death (if applicable)
                </label>
                <input 
                  v-model="form.cause_of_death"
                  type="text"
                  class="block w-full px-3 py-3 border border-slate-600 rounded-lg bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Describe cause of death"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-slate-300 mb-2">
                  Regulation Class Broken
                </label>
                <input 
                  v-model="form.regulation_class_broken"
                  type="text"
                  class="block w-full px-3 py-3 border border-slate-600 rounded-lg bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., OSHA 1926.95"
                />
              </div>
            </div>

            <!-- File Upload Section -->
            <div class="mt-8">
              <h3 class="text-lg font-semibold text-white mb-4">Attachments</h3>
              
              <!-- Drag and Drop Zone -->
              <div 
                @drop.prevent="handleFileDrop"
                @dragover.prevent="dragOver = true"
                @dragleave.prevent="dragOver = false"
                :class="[
                  'border-2 border-dashed rounded-lg p-8 text-center transition-all duration-300',
                  dragOver 
                    ? 'border-blue-500 bg-blue-500/10' 
                    : 'border-slate-600 bg-slate-700/30'
                ]"
              >
                <svg class="w-12 h-12 text-slate-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p class="text-slate-300 mb-2">Drag and drop files here, or</p>
                <label class="inline-flex items-center px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg cursor-pointer transition-colors">
                  <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  Browse Files
                  <input 
                    type="file" 
                    multiple 
                    name="attachments[]"
                    @change="handleFileSelect"
                    class="hidden"
                    accept="image/*,video/*,.pdf,.doc,.docx"
                  />
                </label>
                <p class="text-slate-400 text-sm mt-2">Supported: Images, Videos, PDF, DOC, DOCX (Max 10MB for images/docs, 100MB for videos)</p>
              </div>

              <!-- File List -->
              <div v-if="form.attachments.length > 0" class="mt-4 space-y-2">
                <div 
                  v-for="(file, index) in form.attachments" 
                  :key="index"
                  class="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg border border-slate-600"
                >
                  <div class="flex items-center">
                    <div class="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center mr-3">
                      <span class="text-xl">{{ getFileIcon(file) }}</span>
                    </div>
                    <div>
                      <p class="text-white font-medium">{{ file.name }}</p>
                      <div class="flex items-center space-x-2 text-slate-400 text-sm">
                        <span>{{ getFileTypeLabel(file) }}</span>
                        <span>•</span>
                        <span>{{ formatFileSize(file.size) }}</span>
                      </div>
                    </div>
                  </div>
                  <button
                    type="button"
                    @click="removeFile(index)"
                    class="p-2 text-red-400 hover:text-red-300 transition-colors"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
                
                <!-- File Summary -->
                <div class="mt-4 p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                  <div class="flex items-center justify-between text-sm">
                    <span class="text-blue-300">Total Files: {{ form.attachments.length }}</span>
                    <span class="text-blue-300">
                      Total Size: {{ formatFileSize(form.attachments.reduce((total, file) => total + file.size, 0)) }}
                    </span>
                  </div>
                  <div class="mt-2 flex flex-wrap gap-2">
                    <span v-if="form.attachments.filter(f => f.type.startsWith('image/')).length > 0" class="px-2 py-1 bg-green-500/20 text-green-300 rounded text-xs">
                      {{ form.attachments.filter(f => f.type.startsWith('image/')).length }} Image(s)
                    </span>
                    <span v-if="form.attachments.filter(f => f.type.startsWith('video/')).length > 0" class="px-2 py-1 bg-purple-500/20 text-purple-300 rounded text-xs">
                      {{ form.attachments.filter(f => f.type.startsWith('video/')).length }} Video(s)
                    </span>
                    <span v-if="form.attachments.filter(f => f.type.includes('pdf')).length > 0" class="px-2 py-1 bg-red-500/20 text-red-300 rounded text-xs">
                      {{ form.attachments.filter(f => f.type.includes('pdf')).length }} PDF(s)
                    </span>
                    <span v-if="form.attachments.filter(f => f.type.includes('word') || f.type.includes('document')).length > 0" class="px-2 py-1 bg-blue-500/20 text-blue-300 rounded text-xs">
                      {{ form.attachments.filter(f => f.type.includes('word') || f.type.includes('document')).length }} Document(s)
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Step 4: Review -->
          <div v-if="currentStep === 4" class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-lg rounded-2xl p-8 border border-slate-700/50">
            <h2 class="text-2xl font-bold text-white mb-6 flex items-center">
              <span class="text-3xl mr-3">👁️</span>
              Review & Submit
            </h2>

            <div class="space-y-6">
              <!-- Basic Information Summary -->
              <div class="bg-slate-700/30 rounded-lg p-6">
                <h3 class="text-lg font-semibold text-white mb-4">Basic Information</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div><span class="text-slate-300">Organization:</span> <span class="text-white font-medium">{{ selectedOrganization?.name }}</span></div>
                  <div><span class="text-slate-300">Report Type:</span> <span class="text-white font-medium">{{ form.report_type }}</span></div>
                  <div v-if="form.incident_type"><span class="text-slate-300">Incident Type:</span> <span class="text-white font-medium">{{ form.incident_type }}</span></div>
                  <div><span class="text-slate-300">Date of Incident:</span> <span class="text-white font-medium">{{ form.date_of_incident }}</span></div>
                  <div v-if="form.severity"><span class="text-slate-300">Severity:</span> <span class="text-white font-medium">{{ form.severity }}</span></div>
                  <div v-if="form.industry"><span class="text-slate-300">Industry:</span> <span class="text-white font-medium">{{ form.industry }}</span></div>
                </div>
                <div class="mt-4">
                  <span class="text-slate-300">Description:</span>
                  <p class="text-white mt-2 p-3 bg-slate-800/50 rounded border border-slate-600">{{ form.description }}</p>
                </div>
              </div>

              <!-- Reporter Information Summary -->
              <div class="bg-slate-700/30 rounded-lg p-6">
                <h3 class="text-lg font-semibold text-white mb-4">Reporter Information</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div><span class="text-slate-300">System User ID:</span> <span class="text-white font-medium">{{ form.reported_by_user_id }}</span></div>
                  <div><span class="text-slate-300">Status:</span> <span class="text-white font-medium">{{ form.status }}</span></div>
                  <div v-if="form.reporter_name"><span class="text-slate-300">Reporter Name:</span> <span class="text-white font-medium">{{ form.reporter_name }}</span></div>
                  <div v-if="form.reporter_contact"><span class="text-slate-300">Reporter Contact:</span> <span class="text-white font-medium">{{ form.reporter_contact }}</span></div>
                  <div v-if="form.assigned_to"><span class="text-slate-300">Assigned To:</span> <span class="text-white font-medium">{{ form.assigned_to }}</span></div>
                </div>
              </div>

              <!-- Additional Details Summary -->
              <div v-if="form.location_lat || form.location_long || form.cause_of_death || form.regulation_class_broken" class="bg-slate-700/30 rounded-lg p-6">
                <h3 class="text-lg font-semibold text-white mb-4">Additional Details</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div v-if="form.location_lat && form.location_long">
                    <span class="text-slate-300">Location:</span> 
                    <span class="text-white font-medium">{{ form.location_lat }}, {{ form.location_long }}</span>
                  </div>
                  <div v-if="form.cause_of_death"><span class="text-slate-300">Cause of Death:</span> <span class="text-white font-medium">{{ form.cause_of_death }}</span></div>
                  <div v-if="form.regulation_class_broken"><span class="text-slate-300">Regulation Broken:</span> <span class="text-white font-medium">{{ form.regulation_class_broken }}</span></div>
                </div>
              </div>

              <!-- Attachments Summary -->
              <div v-if="form.attachments.length > 0" class="bg-slate-700/30 rounded-lg p-6">
                <h3 class="text-lg font-semibold text-white mb-4">Attachments ({{ form.attachments.length }})</h3>
                <div class="space-y-2">
                  <div 
                    v-for="(file, index) in form.attachments" 
                    :key="index"
                    class="flex items-center justify-between p-2 bg-slate-800/50 rounded border border-slate-600"
                  >
                    <div class="flex items-center">
                      <svg class="w-4 h-4 text-blue-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                      </svg>
                      <span class="text-white text-sm">{{ file.name }}</span>
                    </div>
                    <span class="text-slate-400 text-xs">{{ formatFileSize(file.size) }}</span>
                  </div>
                </div>
              </div>

              <!-- Submission Notice -->
              <div class="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
                <div class="flex items-start">
                  <svg class="w-5 h-5 text-blue-400 mr-3 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div>
                    <h4 class="text-blue-300 font-medium">Review Before Submitting</h4>
                    <p class="text-blue-200 text-sm mt-1">
                      Please review all information carefully. Once submitted, this report will be processed and relevant personnel will be notified.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Navigation Buttons -->
          <div class="flex items-center justify-between bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-lg rounded-2xl p-6 border border-slate-700/50">
            <button
              v-if="currentStep > 1"
              type="button"
              @click="prevStep"
              class="inline-flex items-center px-6 py-3 bg-slate-600 hover:bg-slate-500 text-white font-medium rounded-lg transition-colors"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
              Previous
            </button>
            <div v-else></div>

            <div class="text-center">
              <p class="text-slate-400 text-sm">Step {{ currentStep }} of {{ totalSteps }}</p>
            </div>

            <div>
              <button
                v-if="currentStep < totalSteps"
                type="button"
                @click="nextStep"
                :disabled="!canProceed"
                :class="[
                  'inline-flex items-center px-6 py-3 font-medium rounded-lg transition-colors',
                  canProceed
                    ? 'bg-blue-500 hover:bg-blue-600 text-white'
                    : 'bg-slate-600 text-slate-400 cursor-not-allowed'
                ]"
              >
                Next
                <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>
              
              <button
                v-else
                type="submit"
                :disabled="form.processing"
                :class="[
                  'inline-flex items-center px-8 py-3 font-semibold rounded-lg transition-colors',
                  form.processing
                    ? 'bg-slate-600 text-slate-400 cursor-not-allowed'
                    : 'bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white transform hover:scale-105'
                ]"
              >
                <svg v-if="form.processing" class="w-4 h-4 mr-2 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <svg v-else class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {{ form.processing ? 'Submitting...' : 'Submit Report' }}
              </button>
            </div>
          </div>

          <!-- Step Navigation (Clickable) -->
          <div class="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-lg rounded-2xl p-6 border border-slate-700/50">
            <div class="flex justify-center space-x-4">
              <button
                v-for="step in totalSteps"
                :key="step"
                type="button"
                @click="goToStep(step)"
                :class="[
                  'px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300',
                  step === currentStep
                    ? 'bg-blue-500 text-white'
                    : step < currentStep
                    ? 'bg-green-500/20 text-green-300 hover:bg-green-500/30'
                    : 'bg-slate-700 text-slate-400 hover:bg-slate-600'
                ]"
              >
                <div class="flex items-center">
                  <span class="w-6 h-6 rounded-full bg-current opacity-20 flex items-center justify-center mr-2">
                    {{ step }}
                  </span>
                  <span v-if="step === 1">Basic Info</span>
                  <span v-else-if="step === 2">Reporter</span>
                  <span v-else-if="step === 3">Details</span>
                  <span v-else>Review</span>
                </div>
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* Custom scrollbar for file list */
.space-y-2::-webkit-scrollbar {
  width: 6px;
}

.space-y-2::-webkit-scrollbar-track {
  background: rgba(71, 85, 105, 0.3);
  border-radius: 3px;
}

.space-y-2::-webkit-scrollbar-thumb {
  background: rgba(59, 130, 246, 0.5);
  border-radius: 3px;
}

.space-y-2::-webkit-scrollbar-thumb:hover {
  background: rgba(59, 130, 246, 0.7);
}
</style>