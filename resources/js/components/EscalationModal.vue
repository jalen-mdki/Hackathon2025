<script setup lang="ts">
import { useForm } from '@inertiajs/vue3';
import { ref, computed, watch } from 'vue';
import Swal from 'sweetalert2';

interface Props {
  report: {
    id: number;
    report_type: string;
    status: string;
    severity?: string;
    is_escalated: boolean;
  };
  show: boolean;
}

interface Emits {
  (e: 'close'): void;
  (e: 'escalated'): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

// Step state
const currentStep = ref(1);
const totalSteps = 3;

// Form state
const form = useForm({
  escalation_priority: '',
  escalation_reason: '',
  notify_users: [] as number[],
});

// Users
const availableUsers = ref([
  { id: 1, name: 'Sarah Chen', role: 'Safety Manager', avatar: '👩‍💼', department: 'Health & Safety' },
  { id: 2, name: 'Mike Johnson', role: 'Department Head', avatar: '👨‍💼', department: 'Operations' },
  { id: 3, name: 'Lisa Rodriguez', role: 'Site Supervisor', avatar: '👩‍🔧', department: 'Engineering' },
]);

// Priority Options
const priorityOptions = [
  { 
    value: 'Critical', 
    label: 'Critical Emergency', 
    icon: '🚨', 
    color: 'from-red-500 to-red-600',
    description: 'Immediate response required - life safety concern',
    timeline: 'Response within 15 minutes'
  },
  { 
    value: 'High', 
    label: 'High Priority', 
    icon: '⚠️', 
    color: 'from-orange-500 to-orange-600',
    description: 'Urgent attention needed - significant risk',
    timeline: 'Response within 24 hours'
  },
  { 
    value: 'Medium', 
    label: 'Medium Priority', 
    icon: '⚡', 
    color: 'from-yellow-500 to-yellow-600',
    description: 'Important but not urgent - moderate risk',
    timeline: 'Response within 48 hours'
  },
];

// Reason Templates
const reasonTemplates = computed(() => {
  if (form.escalation_priority === 'Critical') {
    return [
      { text: 'Life-threatening situation identified', icon: '🆘' },
      { text: 'Immediate evacuation required', icon: '🚪' },
      { text: 'Critical equipment failure', icon: '⚙️' },
      { text: 'Environmental hazard detected', icon: '☢️' },
    ];
  } else if (form.escalation_priority === 'High') {
    return [
      { text: 'Safety risk requires urgent attention', icon: '⚠️' },
      { text: 'Equipment failure creating hazard', icon: '🔧' },
      { text: 'Potential compliance violation', icon: '📋' },
      { text: 'Injury or incident requiring investigation', icon: '🩹' },
    ];
  }
  return [
    { text: 'Safety concern requires review', icon: '🔍' },
    { text: 'Equipment maintenance needed', icon: '🛠️' },
    { text: 'Process improvement opportunity', icon: '📈' },
    { text: 'Documentation or training gap', icon: '📚' },
  ];
});

// Step titles and descriptions
const stepInfo = computed(() => {
  const steps = [
    { title: 'Set Priority Level', description: 'Determine the urgency and severity of this escalation' },
    { title: 'Provide Context', description: 'Explain the reason for escalation and expected outcomes' },
    { title: 'Notify Stakeholders', description: 'Select who needs to be informed about this escalation' },
  ];
  return steps[currentStep.value - 1];
});

// Logic
const canProceed = computed(() => {
  if (currentStep.value === 1) return form.escalation_priority !== '';
  if (currentStep.value === 2) return form.escalation_reason.trim().length > 10;
  return true;
});

const canSubmit = computed(() => {
  return (
    form.escalation_priority !== '' &&
    form.escalation_reason.trim().length > 10 &&
    form.notify_users.length > 0
  );
});

const selectedPriority = computed(() => {
  return priorityOptions.find(p => p.value === form.escalation_priority);
});

// Actions
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

const toggleUser = (id: number) => {
  const idx = form.notify_users.indexOf(id);
  if (idx === -1) {
    form.notify_users.push(id);
  } else {
    form.notify_users.splice(idx, 1);
  }
};

const selectReason = (reason: string) => {
  form.escalation_reason = reason;
  // Auto-advance after a brief delay for better UX
  setTimeout(() => nextStep(), 300);
};

const submitEscalation = () => {
  form.post(`/admin/reports/${props.report.id}/escalate`, {
    onSuccess: () => {
      // Show success alert
      Swal.fire({
        title: 'Escalation Submitted!',
        text: 'The report has been successfully escalated.',
        icon: 'success',
        confirmButtonText: 'OK',
        timer: 3000,
        timerProgressBar: true,
        didClose: () => {
          emit('escalated');
          closeModal();
          // Refresh the page
          window.location.reload();
        }
      });
    },
    onError: () => {
      Swal.fire({
        title: 'Error!',
        text: 'Failed to escalate the report. Please try again.',
        icon: 'error',
        confirmButtonText: 'OK'
      });
    },
  });
};

const closeModal = () => {
  form.reset();
  currentStep.value = 1;
  emit('close');
};

// Auto-select critical if severe
watch(() => props.show, (show) => {
  if (show && props.report.severity === 'Critical') {
    form.escalation_priority = 'Critical';
  }
});
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="duration-300 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div 
        v-if="props.show" 
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm px-4 overflow-y-auto"
        @click.self="closeModal"
      >
        <Transition
          enter-active-class="duration-300 ease-out"
          enter-from-class="opacity-0 scale-95 translate-y-4"
          enter-to-class="opacity-100 scale-100 translate-y-0"
          leave-active-class="duration-200 ease-in"
          leave-from-class="opacity-100 scale-100 translate-y-0"
          leave-to-class="opacity-0 scale-95 translate-y-4"
        >
          <div
            class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col"
          >
            <!-- Header with Progress -->
            <div class="relative bg-gradient-to-r from-slate-50 to-gray-50 px-8 py-6 border-b border-gray-100"></div>
            <!-- Header with Progress -->
            <div class="relative bg-gradient-to-r from-slate-50 to-gray-50 px-8 py-6 border-b border-gray-100">
              <div class="flex justify-between items-start mb-4">
                <div>
                  <h2 class="text-2xl font-bold text-gray-900 mb-1">
                    Escalate Report #{{ props.report.id }}
                  </h2>
                  <p class="text-gray-600 font-medium">{{ props.report.report_type }}</p>
                </div>
                <button
                  @click="closeModal"
                  class="text-gray-400 hover:text-gray-600 transition-colors p-2 rounded-full hover:bg-white/80"
                >
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <!-- Progress Bar -->
              <div class="flex items-center justify-between mb-2">
                <div class="flex space-x-2">
                  <div
                    v-for="step in totalSteps"
                    :key="step"
                    :class="[
                      'w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold transition-all duration-300',
                      step <= currentStep
                        ? 'bg-blue-600 text-white shadow-lg'
                        : 'bg-gray-200 text-gray-500'
                    ]"
                  >
                    {{ step }}
                  </div>
                </div>
                <div class="text-sm text-gray-500">
                  Step {{ currentStep }} of {{ totalSteps }}
                </div>
              </div>
              
              <!-- Step Info -->
              <div class="mt-4">
                <h3 class="font-semibold text-gray-900 text-lg">{{ stepInfo.title }}</h3>
                <p class="text-gray-600 text-sm mt-1">{{ stepInfo.description }}</p>
              </div>
            </div>

            <!-- Content -->
            <div class="p-8 min-h-[400px] overflow-y-auto">
              <!-- Step 1: Priority -->
              <Transition
                enter-active-class="duration-300 ease-out"
                enter-from-class="opacity-0 translate-x-4"
                enter-to-class="opacity-100 translate-x-0"
                leave-active-class="duration-200 ease-in"
                leave-from-class="opacity-100 translate-x-0"
                leave-to-class="opacity-0 -translate-x-4"
                mode="out-in"
              >
                <div v-if="currentStep === 1" class="space-y-4">
                  <div class="grid gap-4">
                    <div
                      v-for="option in priorityOptions"
                      :key="option.value"
                      @click="form.escalation_priority = option.value"
                      :class="[
                        'group relative p-6 border-2 rounded-xl cursor-pointer transition-all duration-300 hover:shadow-lg',
                        form.escalation_priority === option.value
                          ? 'border-blue-500 bg-blue-50 shadow-lg ring-2 ring-blue-200'
                          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                      ]"
                    >
                      <div class="flex items-start space-x-4">
                        <div :class="[
                          'w-12 h-12 rounded-xl flex items-center justify-center text-2xl bg-gradient-to-br shadow-md transition-transform group-hover:scale-105',
                          option.color
                        ]">
                          {{ option.icon }}
                        </div>
                        <div class="flex-1">
                          <h4 class="font-bold text-lg text-gray-900 mb-1">{{ option.label }}</h4>
                          <p class="text-gray-600 mb-2">{{ option.description }}</p>
                          <div class="flex items-center text-sm text-gray-500">
                            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            {{ option.timeline }}
                          </div>
                        </div>
                        <div v-if="form.escalation_priority === option.value" class="text-blue-600">
                          <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </Transition>

              <!-- Step 2: Reason -->
              <Transition
                enter-active-class="duration-300 ease-out"
                enter-from-class="opacity-0 translate-x-4"
                enter-to-class="opacity-100 translate-x-0"
                leave-active-class="duration-200 ease-in"
                leave-from-class="opacity-100 translate-x-0"
                leave-to-class="opacity-0 -translate-x-4"
                mode="out-in"
              >
                <div v-if="currentStep === 2" class="space-y-6">
                  <div v-if="selectedPriority" class="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-xl border border-blue-200">
                    <div class="flex items-center space-x-3">
                      <div :class="['w-8 h-8 rounded-lg flex items-center justify-center text-lg bg-gradient-to-br', selectedPriority.color]">
                        {{ selectedPriority.icon }}
                      </div>
                      <div>
                        <p class="font-semibold text-gray-900">{{ selectedPriority.label }}</p>
                        <p class="text-sm text-gray-600">{{ selectedPriority.timeline }}</p>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 class="font-semibold text-gray-900 mb-3">Quick Reason Templates</h4>
                    <div class="grid gap-3">
                      <div
                        v-for="template in reasonTemplates"
                        :key="template.text"
                        @click="selectReason(template.text)"
                        class="group flex items-center space-x-3 p-4 border border-gray-200 rounded-lg cursor-pointer hover:border-blue-300 hover:bg-blue-50 transition-all duration-200"
                      >
                        <span class="text-lg">{{ template.icon }}</span>
                        <span class="text-gray-700 group-hover:text-blue-700">{{ template.text }}</span>
                        <svg class="w-4 h-4 text-gray-400 group-hover:text-blue-600 ml-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                        </svg>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 class="font-semibold text-gray-900 mb-3">Or Provide Custom Reason</h4>
                    <textarea
                      v-model="form.escalation_reason"
                      class="w-full border border-gray-300 rounded-lg p-4 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 resize-none"
                      rows="4"
                      placeholder="Describe the situation requiring escalation, including any immediate actions needed and expected outcomes..."
                    ></textarea>
                    <div class="mt-2 text-sm text-gray-500">
                      {{ form.escalation_reason.trim().length }} / 500 characters
                    </div>
                  </div>
                </div>
              </Transition>

              <!-- Step 3: Notify Users -->
              <Transition
                enter-active-class="duration-300 ease-out"
                enter-from-class="opacity-0 translate-x-4"
                enter-to-class="opacity-100 translate-x-0"
                leave-active-class="duration-200 ease-in"
                leave-from-class="opacity-100 translate-x-0"
                leave-to-class="opacity-0 -translate-x-4"
                mode="out-in"
              >
                <div v-if="currentStep === 3" class="space-y-6">
                  <div class="bg-amber-50 border border-amber-200 rounded-xl p-4">
                    <div class="flex items-center space-x-2">
                      <svg class="w-5 h-5 text-amber-600" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <p class="text-amber-800 font-medium">
                        Selected stakeholders will be notified immediately via email and system notifications
                      </p>
                    </div>
                  </div>
                  
                  <div>
                    <h4 class="font-semibold text-gray-900 mb-4">Select Recipients</h4>
                    <div class="grid gap-3">
                      <div
                        v-for="user in availableUsers"
                        :key="user.id"
                        @click="toggleUser(user.id)"
                        :class="[
                          'group flex items-center space-x-4 p-4 border-2 rounded-xl cursor-pointer transition-all duration-300 hover:shadow-md',
                          form.notify_users.includes(user.id)
                            ? 'border-green-500 bg-green-50 shadow-lg ring-2 ring-green-200'
                            : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                        ]"
                      >
                        <div class="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-xl shadow-md">
                          {{ user.avatar }}
                        </div>
                        <div class="flex-1">
                          <h5 class="font-semibold text-gray-900">{{ user.name }}</h5>
                          <p class="text-gray-600 text-sm">{{ user.role }}</p>
                          <p class="text-gray-500 text-xs">{{ user.department }}</p>
                        </div>
                        <div v-if="form.notify_users.includes(user.id)" class="text-green-600">
                          <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        </div>
                      </div>
                    </div>
                    
                    <div class="mt-4 text-sm text-gray-600">
                      {{ form.notify_users.length }} recipient{{ form.notify_users.length !== 1 ? 's' : '' }} selected
                    </div>
                  </div>
                </div>
              </Transition>
            </div>

            <!-- Footer -->
            <div class="flex justify-between items-center p-6 border-t border-gray-100 bg-gray-50 sticky bottom-0">
              <button
                v-if="currentStep > 1"
                @click="prevStep"
                class="flex items-center space-x-2 px-6 py-3 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors duration-200 font-medium"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
                <span>Previous</span>
              </button>
              <div v-else></div>
              
              <button
                v-if="currentStep < totalSteps"
                @click="nextStep"
                :disabled="!canProceed"
                :class="[
                  'flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-200',
                  canProceed
                    ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg hover:shadow-xl'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                ]"
              >
                <span>Continue</span>
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>
              
              <button
                v-if="currentStep === totalSteps"
                @click="submitEscalation"
                :disabled="!canSubmit || form.processing"
                :class="[
                  'flex items-center space-x-2 px-8 py-3 rounded-lg font-bold transition-all duration-200',
                  canSubmit && !form.processing
                    ? 'bg-red-600 text-white hover:bg-red-700 shadow-lg hover:shadow-xl'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                ]"
              >
                <svg v-if="form.processing" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
                <span>{{ form.processing ? 'Processing...' : 'Submit Escalation' }}</span>
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
/* Enhanced scrollbar styling */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(45deg, #cbd5e1, #94a3b8);
  border-radius: 4px;
  transition: background 0.2s ease;
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(45deg, #94a3b8, #64748b);
}

/* Smooth focus transitions */
textarea:focus,
input:focus {
  outline: none;
  transform: translateY(-1px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

/* Hover effects for interactive elements */
.group:hover {
  transform: translateY(-2px);
}

/* Custom gradient backgrounds */
.bg-gradient-to-br {
  background-image: linear-gradient(to bottom right, var(--tw-gradient-stops));
}
</style>