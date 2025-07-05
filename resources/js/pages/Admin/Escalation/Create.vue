<script setup lang="ts">
import { useForm } from '@inertiajs/vue3';
import { ref, computed } from 'vue';

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

// Form state
const form = useForm({
  escalation_reason: '',
  escalation_priority: 'High',
  notify_users: [] as number[],
  immediate_action_required: false,
  estimated_resolution_time: '',
  additional_notes: '',
});

// Available users for notification (in real app, this would come from props)
const availableUsers = ref([
  { id: 1, name: 'Safety Manager', email: 'safety@company.com', role: 'Safety Manager' },
  { id: 2, name: 'Department Head', email: 'dept@company.com', role: 'Department Head' },
  { id: 3, name: 'Site Supervisor', email: 'supervisor@company.com', role: 'Site Supervisor' },
  { id: 4, name: 'HR Manager', email: 'hr@company.com', role: 'HR Manager' },
  { id: 5, name: 'Compliance Officer', email: 'compliance@company.com', role: 'Compliance Officer' },
]);

// Escalation priority options
const priorityOptions = [
  { value: 'Critical', label: 'Critical - Immediate action required', color: 'from-red-500 to-red-600', icon: '🚨' },
  { value: 'High', label: 'High - Action required within 24 hours', color: 'from-orange-500 to-orange-600', icon: '⚠️' },
  { value: 'Medium', label: 'Medium - Action required within 48 hours', color: 'from-yellow-500 to-yellow-600', icon: '⚡' },
  { value: 'Low', label: 'Low - Action required within 1 week', color: 'from-blue-500 to-blue-600', icon: '📋' },
];

// Predefined escalation reasons
const commonReasons = [
  'Safety risk requires immediate attention',
  'Potential regulatory violation',
  'Severity higher than initially assessed',
  'Multiple incidents of similar nature',
  'Equipment failure creating ongoing hazard',
  'Environmental impact concerns',
  'Legal liability exposure',
  'Stakeholder concerns raised',
  'Investigation requires specialized expertise',
  'Management decision required',
];

// Resolution time options
const resolutionTimeOptions = [
  'Immediate (0-4 hours)',
  'Same day (4-24 hours)',
  '2-3 days',
  '1 week',
  '2 weeks',
  '1 month',
  'To be determined',
];

// Computed properties
const selectedPriority = computed(() => 
  priorityOptions.find(p => p.value === form.escalation_priority)
);

const canSubmit = computed(() => 
  form.escalation_reason.trim().length > 10 && form.escalation_priority
);

// Methods
const selectReason = (reason: string) => {
  form.escalation_reason = reason;
};

const toggleUser = (userId: number) => {
  const index = form.notify_users.indexOf(userId);
  if (index > -1) {
    form.notify_users.splice(index, 1);
  } else {
    form.notify_users.push(userId);
  }
};

const submitEscalation = () => {
  form.post(`/admin/reports/${props.report.id}/escalate`, {
    onSuccess: () => {
      emit('escalated');
      closeModal();
    },
    onError: (errors) => {
      console.error('Escalation failed:', errors);
    }
  });
};

const closeModal = () => {
  form.reset();
  emit('close');
};

// Auto-select critical priority for certain conditions
const autoSelectPriority = () => {
  if (props.report.severity === 'Critical' || 
      props.report.report_type.includes('Death') || 
      props.report.report_type.includes('Explosion') ||
      props.report.report_type.includes('Fire')) {
    form.escalation_priority = 'Critical';
    form.immediate_action_required = true;
  }
};

// Initialize form when modal opens
const initializeForm = () => {
  if (props.show && !props.report.is_escalated) {
    autoSelectPriority();
  }
};

// Watch for modal opening
import { watch } from 'vue';
watch(() => props.show, (newValue) => {
  if (newValue) {
    initializeForm();
  }
});
</script>

<template>
  <!-- Modal Overlay -->
  <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <!-- Background overlay -->
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="closeModal"></div>

      <!-- Modal panel -->
      <div class="inline-block align-bottom bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full border border-slate-700">
        <!-- Header -->
        <div class="bg-gradient-to-r from-red-500 to-rose-500 px-6 py-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <div class="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center mr-3">
                <span class="text-xl">🚨</span>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-white">Escalate Report</h3>
                <p class="text-red-100 text-sm">Report #{{ report.id }} - {{ report.report_type }}</p>
              </div>
            </div>
            <button @click="closeModal" class="text-white hover:text-red-200 transition-colors">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Content -->
        <div class="px-6 py-6 max-h-[70vh] overflow-y-auto">
          <form @submit.prevent="submitEscalation" class="space-y-6">
            
            <!-- Escalation Priority -->
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-3">
                Escalation Priority <span class="text-red-400">*</span>
              </label>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                <button
                  v-for="priority in priorityOptions"
                  :key="priority.value"
                  type="button"
                  @click="form.escalation_priority = priority.value"
                  :class="[
                    'p-4 rounded-lg border-2 transition-all duration-300 text-left',
                    form.escalation_priority === priority.value
                      ? `border-white bg-gradient-to-r ${priority.color} text-white transform scale-105`
                      : 'border-slate-600 bg-slate-700/50 text-slate-300 hover:border-slate-500'
                  ]"
                >
                  <div class="flex items-center mb-2">
                    <span class="text-xl mr-2">{{ priority.icon }}</span>
                    <span class="font-semibold">{{ priority.value }}</span>
                  </div>
                  <p class="text-sm opacity-90">{{ priority.label.split(' - ')[1] }}</p>
                </button>
              </div>
              <div v-if="form.errors.escalation_priority" class="text-red-400 text-sm mt-1">
                {{ form.errors.escalation_priority }}
              </div>
            </div>

            <!-- Immediate Action Required -->
            <div class="flex items-center">
              <input
                v-model="form.immediate_action_required"
                type="checkbox"
                id="immediate_action"
                class="w-4 h-4 text-red-600 bg-slate-700 border-slate-600 rounded focus:ring-red-500 focus:ring-2"
              />
              <label for="immediate_action" class="ml-2 text-sm font-medium text-slate-300">
                Immediate action required (stops all related operations)
              </label>
            </div>

            <!-- Common Reasons -->
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-3">
                Common Escalation Reasons
              </label>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-2 mb-4">
                <button
                  v-for="reason in commonReasons"
                  :key="reason"
                  type="button"
                  @click="selectReason(reason)"
                  class="p-3 text-left text-sm bg-slate-700/50 hover:bg-slate-600/50 border border-slate-600 rounded-lg transition-colors text-slate-300 hover:text-white"
                >
                  {{ reason }}
                </button>
              </div>
            </div>

            <!-- Escalation Reason -->
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">
                Detailed Escalation Reason <span class="text-red-400">*</span>
              </label>
              <textarea
                v-model="form.escalation_reason"
                rows="6"
                class="block w-full px-3 py-3 border border-slate-600 rounded-lg bg-slate-700 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                placeholder="Provide a detailed explanation of why this report needs to be escalated. Include specific risks, timeline concerns, or regulatory requirements..."
                required
              ></textarea>
              <div class="flex justify-between mt-1">
                <div v-if="form.errors.escalation_reason" class="text-red-400 text-sm">
                  {{ form.errors.escalation_reason }}
                </div>
                <div class="text-slate-400 text-sm">
                  {{ form.escalation_reason.length }} characters (minimum 10)
                </div>
              </div>
            </div>

            <!-- Estimated Resolution Time -->
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">
                Estimated Resolution Time
              </label>
              <select
                v-model="form.estimated_resolution_time"
                class="block w-full px-3 py-3 border border-slate-600 rounded-lg bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
              >
                <option value="">Select estimated resolution time</option>
                <option v-for="time in resolutionTimeOptions" :key="time" :value="time">
                  {{ time }}
                </option>
              </select>
            </div>

            <!-- Notify Users -->
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-3">
                Notify Key Personnel
              </label>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div
                  v-for="user in availableUsers"
                  :key="user.id"
                  @click="toggleUser(user.id)"
                  :class="[
                    'p-3 rounded-lg border cursor-pointer transition-all duration-300',
                    form.notify_users.includes(user.id)
                      ? 'border-red-500 bg-red-500/20 text-white'
                      : 'border-slate-600 bg-slate-700/50 text-slate-300 hover:border-slate-500'
                  ]"
                >
                  <div class="flex items-center">
                    <div :class="[
                      'w-4 h-4 rounded border-2 mr-3 flex items-center justify-center',
                      form.notify_users.includes(user.id) ? 'border-red-500 bg-red-500' : 'border-slate-400'
                    ]">
                      <svg v-if="form.notify_users.includes(user.id)" class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                      </svg>
                    </div>
                    <div>
                      <p class="font-medium">{{ user.name }}</p>
                      <p class="text-xs opacity-75">{{ user.role }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Additional Notes -->
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">
                Additional Notes
              </label>
              <textarea
                v-model="form.additional_notes"
                rows="3"
                class="block w-full px-3 py-3 border border-slate-600 rounded-lg bg-slate-700 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                placeholder="Any additional information, context, or special instructions for the escalation team..."
              ></textarea>
            </div>

            <!-- Summary -->
            <div v-if="selectedPriority" class="bg-slate-700/30 rounded-lg p-4 border border-slate-600">
              <h4 class="font-semibold text-white mb-2 flex items-center">
                <span class="text-xl mr-2">{{ selectedPriority.icon }}</span>
                Escalation Summary
              </h4>
              <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                  <span class="text-slate-300">Priority:</span>
                  <span class="text-white font-medium">{{ form.escalation_priority }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-slate-300">Immediate Action:</span>
                  <span class="text-white font-medium">{{ form.immediate_action_required ? 'Yes' : 'No' }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-slate-300">Personnel to Notify:</span>
                  <span class="text-white font-medium">{{ form.notify_users.length }} person(s)</span>
                </div>
                <div v-if="form.estimated_resolution_time" class="flex justify-between">
                  <span class="text-slate-300">Est. Resolution:</span>
                  <span class="text-white font-medium">{{ form.estimated_resolution_time }}</span>
                </div>
              </div>
            </div>
          </form>
        </div>

        <!-- Footer -->
        <div class="bg-slate-800/50 px-6 py-4 border-t border-slate-700">
          <div class="flex items-center justify-between">
            <div class="text-sm text-slate-400">
              <span class="flex items-center">
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Escalation will notify selected personnel immediately
              </span>
            </div>
            <div class="flex space-x-3">
              <button
                type="button"
                @click="closeModal"
                class="px-4 py-2 text-sm font-medium text-slate-300 bg-slate-700 border border-slate-600 rounded-lg hover:bg-slate-600 transition-colors"
              >
                Cancel
              </button>
              <button
                @click="submitEscalation"
                :disabled="!canSubmit || form.processing"
                :class="[
                  'px-6 py-2 text-sm font-medium rounded-lg transition-colors flex items-center',
                  canSubmit && !form.processing
                    ? 'bg-gradient-to-r from-red-500 to-rose-500 hover:from-red-600 hover:to-rose-600 text-white'
                    : 'bg-slate-600 text-slate-400 cursor-not-allowed'
                ]"
              >
                <svg v-if="form.processing" class="w-4 h-4 mr-2 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <svg v-else class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.966-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
                {{ form.processing ? 'Escalating...' : 'Escalate Report' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
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
</style>