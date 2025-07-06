<template>
  <div class="incident-report-form" :class="{ 'dark': isDarkMode }">
    <div class="form-header">
      <div class="header-content">
        <h1>Submit Incident Report</h1>
        <p>Please fill out this form to report an incident. All fields marked with * are required.</p>
      </div>
      <button 
        type="button" 
        @click="toggleDarkMode" 
        class="theme-toggle"
        :title="isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'"
      >
        <span v-if="isDarkMode">☀️</span>
        <span v-else>🌙</span>
      </button>
    </div>

    <form @submit.prevent="submitReport" class="report-form">
      <!-- Basic Information -->
      <div class="form-section">
        <h2 class="section-title">Basic Information</h2>
        
        <div class="form-group">
          <label for="report_type">Report Type *</label>
          <select 
            id="report_type" 
            v-model="form.report_type" 
            :class="{ 'error': errors.report_type }"
            required
          >
            <option value="">Select Report Type</option>
            <option value="Accident">Accident</option>
            <option value="Near Miss">Near Miss</option>
            <option value="Hazard">Hazard</option>
            <option value="Environmental">Environmental</option>
            <option value="Security">Security</option>
            <option value="Other">Other</option>
          </select>
          <span v-if="errors.report_type" class="error-message">{{ errors.report_type }}</span>
        </div>

        <div class="form-group">
          <label for="incident_type">Incident Type</label>
          <input 
            type="text" 
            id="incident_type" 
            v-model="form.incident_type"
            placeholder="e.g., Slip and Fall, Equipment Failure"
            :class="{ 'error': errors.incident_type }"
          >
          <span v-if="errors.incident_type" class="error-message">{{ errors.incident_type }}</span>
        </div>

        <div class="form-group">
          <label for="description">Description *</label>
          <textarea 
            id="description" 
            v-model="form.description"
            placeholder="Please provide a detailed description of the incident"
            rows="4"
            :class="{ 'error': errors.description }"
            required
          ></textarea>
          <span v-if="errors.description" class="error-message">{{ errors.description }}</span>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="date_of_incident">Date of Incident *</label>
            <input 
              type="date" 
              id="date_of_incident" 
              v-model="form.date_of_incident"
              :class="{ 'error': errors.date_of_incident }"
              :max="today"
              required
            >
            <span v-if="errors.date_of_incident" class="error-message">{{ errors.date_of_incident }}</span>
          </div>

          <div class="form-group">
            <label for="severity">Severity Level</label>
            <select 
              id="severity" 
              v-model="form.severity"
              :class="{ 'error': errors.severity }"
            >
              <option value="">Select Severity</option>
              <option value="Low">Low</option>
              <option value="Medium">Medium</option>
              <option value="High">High</option>
              <option value="Critical">Critical</option>
            </select>
            <span v-if="errors.severity" class="error-message">{{ errors.severity }}</span>
          </div>
        </div>

        <div class="form-group">
          <label for="industry">Industry/Department</label>
          <input 
            type="text" 
            id="industry" 
            v-model="form.industry"
            placeholder="e.g., Manufacturing, Construction, Healthcare"
            :class="{ 'error': errors.industry }"
          >
          <span v-if="errors.industry" class="error-message">{{ errors.industry }}</span>
        </div>
      </div>

      <!-- Location Information -->
      <div class="form-section">
        <h2 class="section-title">Location Information</h2>
        
        <div class="form-row">
          <div class="form-group">
            <label for="location_lat">Latitude</label>
            <input 
              type="number" 
              id="location_lat" 
              v-model="form.location_lat"
              placeholder="e.g., 40.7128"
              step="0.0000001"
              min="-90"
              max="90"
              :class="{ 'error': errors.location_lat }"
            >
            <span v-if="errors.location_lat" class="error-message">{{ errors.location_lat }}</span>
          </div>

          <div class="form-group">
            <label for="location_long">Longitude</label>
            <input 
              type="number" 
              id="location_long" 
              v-model="form.location_long"
              placeholder="e.g., -74.0060"
              step="0.0000001"
              min="-180"
              max="180"
              :class="{ 'error': errors.location_long }"
            >
            <span v-if="errors.location_long" class="error-message">{{ errors.location_long }}</span>
          </div>
        </div>

        <div class="form-group">
          <button type="button" @click="getCurrentLocation" class="location-btn">
            📍 Get Current Location
          </button>
          <span v-if="locationStatus" class="location-status">{{ locationStatus }}</span>
        </div>
      </div>

      <!-- Reporter Information -->
      <div class="form-section">
        <h2 class="section-title">Reporter Information</h2>
        
        <div class="form-row">
          <div class="form-group">
            <label for="reporter_name">Reporter Name</label>
            <input 
              type="text" 
              id="reporter_name" 
              v-model="form.reporter_name"
              placeholder="Your full name"
              :class="{ 'error': errors.reporter_name }"
            >
            <span v-if="errors.reporter_name" class="error-message">{{ errors.reporter_name }}</span>
          </div>

          <div class="form-group">
            <label for="reporter_contact">Reporter Contact</label>
            <input 
              type="text" 
              id="reporter_contact" 
              v-model="form.reporter_contact"
              placeholder="Phone number or email"
              :class="{ 'error': errors.reporter_contact }"
            >
            <span v-if="errors.reporter_contact" class="error-message">{{ errors.reporter_contact }}</span>
          </div>
        </div>
      </div>

      <!-- Additional Information -->
      <div class="form-section">
        <h2 class="section-title">Additional Information</h2>
        
        <div class="form-group">
          <label for="cause_of_death">Cause of Death (if applicable)</label>
          <input 
            type="text" 
            id="cause_of_death" 
            v-model="form.cause_of_death"
            placeholder="Only fill if there was a fatality"
            :class="{ 'error': errors.cause_of_death }"
          >
          <span v-if="errors.cause_of_death" class="error-message">{{ errors.cause_of_death }}</span>
        </div>

        <div class="form-group">
          <label for="regulation_class_broken">Regulation/Policy Violated</label>
          <input 
            type="text" 
            id="regulation_class_broken" 
            v-model="form.regulation_class_broken"
            placeholder="e.g., OSHA 1926.95, Company Policy 123"
            :class="{ 'error': errors.regulation_class_broken }"
          >
          <span v-if="errors.regulation_class_broken" class="error-message">{{ errors.regulation_class_broken }}</span>
        </div>
      </div>

      <!-- File Uploads -->
      <div class="form-section">
        <h2 class="section-title">Supporting Documents</h2>
        
        <div class="form-group">
          <label for="files">Upload Files (Photos, Documents, etc.)</label>
          <input 
            type="file" 
            id="files" 
            @change="handleFileUpload"
            multiple
            accept="image/*,application/pdf,.doc,.docx,.txt"
            class="file-input"
          >
          <div class="file-info">
            <p>Accepted formats: Images, PDF, Word documents, Text files</p>
            <p>Maximum size: 10MB per file</p>
          </div>
          
          <div v-if="selectedFiles.length > 0" class="selected-files">
            <h4>Selected Files:</h4>
            <div v-for="(file, index) in selectedFiles" :key="index" class="file-item">
              <span>{{ file.name }}</span>
              <button type="button" @click="removeFile(index)" class="remove-file">×</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Submit Button -->
      <div class="form-actions">
        <button type="submit" :disabled="isSubmitting" class="submit-btn">
          <span v-if="isSubmitting">Submitting...</span>
          <span v-else>Submit Report</span>
        </button>
      </div>
    </form>

    <!-- Success Message -->
    <div v-if="submitSuccess" class="success-message">
      <h3>Report Submitted Successfully!</h3>
      <p>Thank you for your report. We will review it and take appropriate action.</p>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed } from 'vue'
import { router } from '@inertiajs/vue3'

export default {
  name: 'IncidentReportForm',
  setup() {
    const form = reactive({
      report_type: '',
      incident_type: '',
      description: '',
      date_of_incident: '',
      location_lat: null,
      location_long: null,
      severity: '',
      industry: '',
      reporter_name: '',
      reporter_contact: '',
      cause_of_death: '',
      regulation_class_broken: ''
    })

    const errors = ref({})
    const isSubmitting = ref(false)
    const submitSuccess = ref(false)
    const selectedFiles = ref([])
    const locationStatus = ref('')
    const isDarkMode = ref(false)

    // Initialize dark mode from localStorage or system preference
    const initializeDarkMode = () => {
      const savedTheme = localStorage.getItem('theme')
      if (savedTheme) {
        isDarkMode.value = savedTheme === 'dark'
      } else {
        // Check system preference
        isDarkMode.value = window.matchMedia('(prefers-color-scheme: dark)').matches
      }
    }

    const toggleDarkMode = () => {
      isDarkMode.value = !isDarkMode.value
      localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light')
    }

    // Initialize on component mount
    initializeDarkMode()

    const today = computed(() => {
      return new Date().toISOString().split('T')[0]
    })

    const getCurrentLocation = () => {
      if (!navigator.geolocation) {
        locationStatus.value = 'Geolocation is not supported by this browser.'
        return
      }

      locationStatus.value = 'Getting location...'
      navigator.geolocation.getCurrentPosition(
        (position) => {
          form.location_lat = position.coords.latitude
          form.location_long = position.coords.longitude
          locationStatus.value = 'Location captured successfully!'
          setTimeout(() => {
            locationStatus.value = ''
          }, 3000)
        },
        (error) => {
          locationStatus.value = 'Error getting location: ' + error.message
          setTimeout(() => {
            locationStatus.value = ''
          }, 5000)
        }
      )
    }

    const handleFileUpload = (event) => {
      const files = Array.from(event.target.files)
      
      // Validate file sizes
      const maxSize = 10 * 1024 * 1024 // 10MB
      const validFiles = files.filter(file => {
        if (file.size > maxSize) {
          alert(`File ${file.name} is too large. Maximum size is 10MB.`)
          return false
        }
        return true
      })

      selectedFiles.value = [...selectedFiles.value, ...validFiles]
    }

    const removeFile = (index) => {
      selectedFiles.value.splice(index, 1)
    }

    const submitReport = async () => {
      if (isSubmitting.value) return

      isSubmitting.value = true
      errors.value = {}

      try {
        const formData = new FormData()
        
        // Add form fields
        Object.keys(form).forEach(key => {
          if (form[key] !== null && form[key] !== '') {
            formData.append(key, form[key])
          }
        })

        // Add files
        selectedFiles.value.forEach((file, index) => {
          formData.append(`files[${index}]`, file)
        })

        // Submit using Inertia
        await router.post('/public-reports', formData, {
          forceFormData: true,
          onSuccess: () => {
            submitSuccess.value = true
            // Reset form
            Object.keys(form).forEach(key => {
              form[key] = ''
            })
            selectedFiles.value = []
            
            // Scroll to top
            window.scrollTo({ top: 0, behavior: 'smooth' })
          },
          onError: (serverErrors) => {
            errors.value = serverErrors
          }
        })
      } catch (error) {
        console.error('Error submitting report:', error)
        alert('An error occurred while submitting the report. Please try again.')
      } finally {
        isSubmitting.value = false
      }
    }

    return {
      form,
      errors,
      isSubmitting,
      submitSuccess,
      selectedFiles,
      locationStatus,
      isDarkMode,
      today,
      getCurrentLocation,
      handleFileUpload,
      removeFile,
      submitReport,
      toggleDarkMode
    }
  }
}
</script>

<style scoped>
/* Light Theme (Default) */
.incident-report-form {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background: #f8f9fa;
  min-height: 100vh;
  transition: background-color 0.3s ease;
}

.form-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 40px;
  border-radius: 10px;
  text-align: center;
  margin-bottom: 30px;
  position: relative;
}

.header-content h1 {
  font-size: 2.5rem;
  margin-bottom: 10px;
  font-weight: 700;
}

.header-content p {
  font-size: 1.1rem;
  opacity: 0.9;
}

.theme-toggle {
  position: absolute;
  top: 20px;
  right: 20px;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  font-size: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.theme-toggle:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.report-form {
  background: white;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.form-section {
  margin-bottom: 40px;
}

.section-title {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #3498db;
  transition: color 0.3s ease;
}

.form-group {
  margin-bottom: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  color: #555;
  transition: color 0.3s ease;
}

input, select, textarea {
  width: 100%;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 5px;
  font-size: 16px;
  transition: all 0.3s ease;
  background: white;
  color: #333;
}

input:focus, select:focus, textarea:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

input.error, select.error, textarea.error {
  border-color: #e74c3c;
}

.error-message {
  color: #e74c3c;
  font-size: 14px;
  margin-top: 5px;
  display: block;
}

.location-btn {
  background: #27ae60;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s ease;
}

.location-btn:hover {
  background: #219a52;
  transform: translateY(-1px);
}

.location-status {
  margin-left: 10px;
  font-style: italic;
  color: #666;
  transition: color 0.3s ease;
}

.file-input {
  border: 2px dashed #ddd;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
}

.file-input:hover {
  border-color: #3498db;
  background: #f8f9fa;
}

.file-info {
  margin-top: 10px;
  font-size: 14px;
  color: #666;
  transition: color 0.3s ease;
}

.selected-files {
  margin-top: 15px;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 5px;
  margin-bottom: 5px;
  transition: background-color 0.3s ease;
}

.remove-file {
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 50%;
  width: 25px;
  height: 25px;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.remove-file:hover {
  background: #c0392b;
  transform: scale(1.1);
}

.form-actions {
  text-align: center;
  margin-top: 30px;
}

.submit-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 15px 40px;
  border: none;
  border-radius: 25px;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.success-message {
  background: #d4edda;
  color: #155724;
  padding: 20px;
  border-radius: 5px;
  margin-top: 20px;
  text-align: center;
  transition: all 0.3s ease;
}

.success-message h3 {
  margin-bottom: 10px;
}

/* Dark Theme */
.incident-report-form.dark {
  background: #1a1a1a;
  color: #e1e1e1;
}

.incident-report-form.dark .form-header {
  background: linear-gradient(135deg, #4a4a8a 0%, #2d1b69 100%);
}

.incident-report-form.dark .report-form {
  background: #2d2d2d;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}

.incident-report-form.dark .section-title {
  color: #e1e1e1;
  border-bottom-color: #4a90e2;
}

.incident-report-form.dark label {
  color: #b3b3b3;
}

.incident-report-form.dark input,
.incident-report-form.dark select,
.incident-report-form.dark textarea {
  background: #3a3a3a;
  border-color: #555;
  color: #e1e1e1;
}

.incident-report-form.dark input::placeholder,
.incident-report-form.dark textarea::placeholder {
  color: #888;
}

.incident-report-form.dark input:focus,
.incident-report-form.dark select:focus,
.incident-report-form.dark textarea:focus {
  border-color: #4a90e2;
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.2);
}

.incident-report-form.dark input.error,
.incident-report-form.dark select.error,
.incident-report-form.dark textarea.error {
  border-color: #ff6b6b;
}

.incident-report-form.dark .error-message {
  color: #ff6b6b;
}

.incident-report-form.dark .location-btn {
  background: #2ecc71;
}

.incident-report-form.dark .location-btn:hover {
  background: #27ae60;
}

.incident-report-form.dark .location-status {
  color: #b3b3b3;
}

.incident-report-form.dark .file-input {
  background: #3a3a3a;
  border-color: #555;
  color: #e1e1e1;
}

.incident-report-form.dark .file-input:hover {
  border-color: #4a90e2;
  background: #404040;
}

.incident-report-form.dark .file-info {
  color: #b3b3b3;
}

.incident-report-form.dark .file-item {
  background: #404040;
  color: #e1e1e1;
}

.incident-report-form.dark .remove-file {
  background: #ff6b6b;
}

.incident-report-form.dark .remove-file:hover {
  background: #ff5252;
}

.incident-report-form.dark .submit-btn {
  background: linear-gradient(135deg, #4a4a8a 0%, #2d1b69 100%);
}

.incident-report-form.dark .submit-btn:hover:not(:disabled) {
  box-shadow: 0 8px 20px rgba(74, 74, 138, 0.4);
}

.incident-report-form.dark .success-message {
  background: #1e3a1e;
  color: #4caf50;
}

/* Custom scrollbar for dark mode */
.incident-report-form.dark ::-webkit-scrollbar {
  width: 8px;
}

.incident-report-form.dark ::-webkit-scrollbar-track {
  background: #2d2d2d;
}

.incident-report-form.dark ::-webkit-scrollbar-thumb {
  background: #555;
  border-radius: 4px;
}

.incident-report-form.dark ::-webkit-scrollbar-thumb:hover {
  background: #666;
}

/* Animations for theme transition */
@media (prefers-reduced-motion: no-preference) {
  .incident-report-form * {
    transition-duration: 0.3s;
    transition-timing-function: ease;
  }
}

/* Responsive adjustments for dark mode */
@media (max-width: 768px) {
  .theme-toggle {
    top: 15px;
    right: 15px;
    width: 40px;
    height: 40px;
    font-size: 1.2rem;
  }
  
  .incident-report-form.dark .form-header {
    padding: 30px 20px;
  }
  
  .incident-report-form.dark .report-form {
    padding: 30px 20px;
  }
}
</style>