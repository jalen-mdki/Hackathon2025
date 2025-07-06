<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class StoreReportRequest extends FormRequest
{
    /**
     * Determine if the user is authorized to make this request.
     */
    public function authorize(): bool
    {
        return true; // Public form, no authorization needed
    }

    /**
     * Get the validation rules that apply to the request.
     *
     * @return array<string, \Illuminate\Contracts\Validation\ValidationRule|array<mixed>|string>
     */
    public function rules(): array
    {
        return [
            'report_type' => 'required|string|max:255|in:Accident,Near Miss,Hazard,Environmental,Security,Other',
            'incident_type' => 'nullable|string|max:255',
            'description' => 'required|string|min:10|max:5000',
            'date_of_incident' => 'required|date|before_or_equal:today|after:1900-01-01',
            'location_lat' => 'nullable|numeric|between:-90,90',
            'location_long' => 'nullable|numeric|between:-180,180',
            'severity' => 'nullable|string|in:Low,Medium,High,Critical',
            'industry' => 'nullable|string|max:255',
            'reporter_name' => 'nullable|string|max:255|regex:/^[a-zA-Z\s]+$/',
            'reporter_contact' => 'nullable|string|max:255',
            'cause_of_death' => 'nullable|string|max:500',
            'regulation_class_broken' => 'nullable|string|max:500',
            'files' => 'nullable|array|max:10',
            'files.*' => 'file|max:10240|mimes:jpeg,jpg,png,gif,pdf,doc,docx,txt,csv,xlsx'
        ];
    }

    /**
     * Get custom error messages for validator errors.
     *
     * @return array<string, string>
     */
    public function messages(): array
    {
        return [
            'report_type.required' => 'Please select a report type.',
            'report_type.in' => 'Please select a valid report type.',
            'description.required' => 'Please provide a description of the incident.',
            'description.min' => 'Description must be at least 10 characters long.',
            'description.max' => 'Description cannot exceed 5000 characters.',
            'date_of_incident.required' => 'Please provide the date when the incident occurred.',
            'date_of_incident.before_or_equal' => 'Incident date cannot be in the future.',
            'date_of_incident.after' => 'Please provide a valid incident date.',
            'location_lat.between' => 'Latitude must be between -90 and 90 degrees.',
            'location_long.between' => 'Longitude must be between -180 and 180 degrees.',
            'severity.in' => 'Please select a valid severity level.',
            'reporter_name.regex' => 'Reporter name should only contain letters and spaces.',
            'cause_of_death.max' => 'Cause of death description cannot exceed 500 characters.',
            'regulation_class_broken.max' => 'Regulation description cannot exceed 500 characters.',
            'files.max' => 'You can upload a maximum of 10 files.',
            'files.*.max' => 'Each file must be smaller than 10MB.',
            'files.*.mimes' => 'Only image files, PDFs, Word documents, text files, and spreadsheets are allowed.',
        ];
    }

    /**
     * Get custom attributes for validator errors.
     *
     * @return array<string, string>
     */
    public function attributes(): array
    {
        return [
            'report_type' => 'report type',
            'incident_type' => 'incident type',
            'date_of_incident' => 'incident date',
            'location_lat' => 'latitude',
            'location_long' => 'longitude',
            'reporter_name' => 'reporter name',
            'reporter_contact' => 'reporter contact',
            'cause_of_death' => 'cause of death',
            'regulation_class_broken' => 'regulation violated',
        ];
    }

    /**
     * Prepare the data for validation.
     */
    protected function prepareForValidation(): void
    {
        // Clean and format data before validation
        if ($this->has('reporter_name')) {
            $this->merge([
                'reporter_name' => trim($this->reporter_name)
            ]);
        }

        if ($this->has('reporter_contact')) {
            $this->merge([
                'reporter_contact' => trim($this->reporter_contact)
            ]);
        }

        if ($this->has('description')) {
            $this->merge([
                'description' => trim($this->description)
            ]);
        }

        // Convert empty strings to null for nullable fields
        $nullableFields = [
            'incident_type', 'location_lat', 'location_long', 'severity', 
            'industry', 'reporter_name', 'reporter_contact', 'cause_of_death', 
            'regulation_class_broken'
        ];

        foreach ($nullableFields as $field) {
            if ($this->has($field) && $this->$field === '') {
                $this->merge([$field => null]);
            }
        }
    }
}