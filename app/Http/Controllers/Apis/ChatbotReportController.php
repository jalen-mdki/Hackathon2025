<?php

namespace App\Http\Controllers\Apis;

use App\Models\Report;
use App\Models\ReportUploads;
use Illuminate\Http\Request;
use App\Http\Controllers\Controller;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\Validator;
use Illuminate\Support\Str;

class ChatbotReportController extends Controller
{
    /**
     * Submit a new report from the chatbot
     * 
     * @param Request $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function submitReport(Request $request)
    {
        try {
            // Validate the incoming request
            $validator = Validator::make($request->all(), [
                'report_type' => 'required|string|max:255',
                'description' => 'required|string',
                'date_of_incident' => 'required|date',
                'reporter_name' => 'required|string|max:255',
                'reporter_contact' => 'required|string|max:255',
                'severity' => 'nullable|string|in:low,medium,high,critical',
                'incident_type' => 'nullable|string|max:255',
                'location_lat' => 'nullable|numeric|between:-90,90',
                'location_long' => 'nullable|numeric|between:-180,180',
                'industry' => 'nullable|string|max:255',
                'regulation_class_broken' => 'nullable|string|max:255',
                'ai_analysis' => 'nullable|string',
                'whatsapp_report_id' => 'nullable|string|max:255',
                'source' => 'nullable|string|max:255',
                'media_files' => 'nullable|array',
                'media_files.*.url' => 'required_with:media_files|url',
                'media_files.*.type' => 'required_with:media_files|string',
                'media_files.*.filename' => 'nullable|string'
            ]);

            if ($validator->fails()) {
                return response()->json([
                    'success' => false,
                    'message' => 'Validation failed',
                    'errors' => $validator->errors()
                ], 422);
            }

            // Use NLP analysis to enhance report data
            $enhancedData = $this->enhanceReportWithNLP($request->all());

            // Create the report
            $report = Report::create([
                'report_type' => $enhancedData['report_type'],
                'incident_type' => $enhancedData['incident_type'],
                'description' => $enhancedData['description'],
                'date_of_incident' => $enhancedData['date_of_incident'],
                'location_lat' => $enhancedData['location_lat'],
                'location_long' => $enhancedData['location_long'],
                'severity' => $enhancedData['severity'],
                'industry' => $enhancedData['industry'] ?? 'General',
                'reporter_name' => $enhancedData['reporter_name'],
                'reporter_contact' => $enhancedData['reporter_contact'],
                'status' => 'Pending',
                'regulation_class_broken' => $enhancedData['regulation_class_broken'],
                'metadata' => json_encode([
                    'ai_analysis' => $enhancedData['ai_analysis'] ?? null,
                    'whatsapp_report_id' => $enhancedData['whatsapp_report_id'] ?? null,
                    'source' => $enhancedData['source'] ?? 'whatsapp_chatbot',
                    'enhanced_by_nlp' => true,
                    'original_data' => $request->only(['description', 'severity', 'incident_type'])
                ])
            ]);

            // Handle media files if provided
            $uploadedFiles = [];
            if ($request->has('media_files') && is_array($request->media_files)) {
                $uploadedFiles = $this->processMediaFiles($report->id, $request->media_files);
            }

            // Log successful creation
            Log::info('Chatbot report created successfully', [
                'report_id' => $report->id,
                'reporter_contact' => $report->reporter_contact,
                'severity' => $report->severity,
                'media_files_count' => count($uploadedFiles)
            ]);

            // Return success response
            return response()->json([
                'success' => true,
                'message' => 'Report submitted successfully',
                'data' => [
                    'id' => $report->id,
                    'report_type' => $report->report_type,
                    'incident_type' => $report->incident_type,
                    'severity' => $report->severity,
                    'status' => $report->status,
                    'created_at' => $report->created_at->toISOString(),
                    'media_files_uploaded' => count($uploadedFiles),
                    'enhanced_fields' => [
                        'auto_detected_incident_type' => $enhancedData['auto_detected_incident_type'] ?? false,
                        'auto_detected_severity' => $enhancedData['auto_detected_severity'] ?? false,
                        'auto_detected_location' => $enhancedData['auto_detected_location'] ?? false,
                        'extracted_entities' => $enhancedData['extracted_entities'] ?? []
                    ]
                ]
            ], 201);

        } catch (\Exception $e) {
            Log::error('Failed to create chatbot report', [
                'error' => $e->getMessage(),
                'request_data' => $request->all()
            ]);

            return response()->json([
                'success' => false,
                'message' => 'Failed to create report',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Submit media files from chatbot (for real-time uploads)
     * 
     * @param Request $request
     * @return \Illuminate\Http\JsonResponse
     */
    public function submitMediaFiles(Request $request)
    {
        try {
            $validator = Validator::make($request->all(), [
                'report_id' => 'required|integer|exists:reports,id',
                'files' => 'required|array|min:1',
                'files.*' => 'required|file|mimes:jpeg,png,jpg,gif,mp4,avi,mov,wmv|max:20480', // 20MB max
                'uploaded_by' => 'nullable|string|max:255'
            ]);

            if ($validator->fails()) {
                return response()->json([
                    'success' => false,
                    'message' => 'Validation failed',
                    'errors' => $validator->errors()
                ], 422);
            }

            $report = Report::findOrFail($request->report_id);
            $uploadedFiles = [];
            $errors = [];

            foreach ($request->file('files') as $index => $file) {
                try {
                    $originalName = $file->getClientOriginalName();
                    $filename = Str::uuid() . '.' . $file->getClientOriginalExtension();
                    
                    // Upload to S3
                    $path = $file->storeAs('hsse-reports/' . date('Y/m/d'), $filename, 's3');
                    $s3Url = Storage::disk('s3')->url($path);

                    // Create upload record
                    $uploadRecord = ReportUploads::create([
                        'report_id' => $report->id,
                        'file_url' => $s3Url,
                        'file_type' => $file->getMimeType(),
                        'uploaded_by' => $request->uploaded_by ?? 'WhatsApp Bot',
                        's3_path' => $path,
                        'original_filename' => $originalName,
                        'file_size' => $file->getSize()
                    ]);

                    $uploadedFiles[] = [
                        'id' => $uploadRecord->id,
                        'file_url' => $s3Url,
                        'file_type' => $uploadRecord->file_type,
                        's3_path' => $path,
                        'original_filename' => $originalName,
                        'file_size' => $file->getSize()
                    ];

                } catch (\Exception $e) {
                    Log::error('Failed to upload file to S3: ' . $e->getMessage(), [
                        'file' => $originalName,
                        'report_id' => $report->id,
                        'index' => $index
                    ]);
                    
                    $errors[] = [
                        'file' => $originalName,
                        'error' => 'Upload failed: ' . $e->getMessage()
                    ];
                }
            }

            return response()->json([
                'success' => true,
                'message' => 'Media files processed',
                'data' => [
                    'uploaded_files' => $uploadedFiles,
                    'total_uploaded' => count($uploadedFiles),
                    'errors' => $errors,
                    'report_id' => $report->id
                ]
            ], 201);

        } catch (\Exception $e) {
            Log::error('Failed to process media files', [
                'error' => $e->getMessage(),
                'request_data' => $request->except('files')
            ]);

            return response()->json([
                'success' => false,
                'message' => 'Failed to process media files',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Get report status for chatbot updates
     * 
     * @param int $id
     * @return \Illuminate\Http\JsonResponse
     */
    public function getReportStatus($id)
    {
        try {
            $report = Report::with(['uploads', 'assignedTo'])->findOrFail($id);

            return response()->json([
                'success' => true,
                'data' => [
                    'id' => $report->id,
                    'status' => $report->status,
                    'severity' => $report->severity,
                    'assigned_to' => $report->assignedTo ? $report->assignedTo->first_name . ' ' . $report->assignedTo->last_name : null,
                    'is_escalated' => $report->is_escalated,
                    'escalation_status' => $report->escalation_status,
                    'feedback_given' => $report->feedback_given,
                    'created_at' => $report->created_at->toISOString(),
                    'updated_at' => $report->updated_at->toISOString(),
                    'media_files_count' => $report->uploads->count()
                ]
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Report not found',
                'error' => $e->getMessage()
            ], 404);
        }
    }

    /**
     * Enhance report data using NLP analysis
     * 
     * @param array $data
     * @return array
     */
    private function enhanceReportWithNLP($data)
    {
        $enhanced = $data;
        $description = strtolower($data['description'] ?? '');
        
        // Auto-detect incident type if not provided or enhance existing
        if (empty($data['incident_type']) || $data['incident_type'] === 'other') {
            $enhanced['incident_type'] = $this->detectIncidentType($description);
            $enhanced['auto_detected_incident_type'] = true;
        }

        // Auto-detect or enhance severity
        if (empty($data['severity']) || $data['severity'] === 'medium') {
            $detectedSeverity = $this->detectSeverity($description);
            if ($detectedSeverity !== 'medium') {
                $enhanced['severity'] = $detectedSeverity;
                $enhanced['auto_detected_severity'] = true;
            }
        }

        // Extract location information
        $locationInfo = $this->extractLocationInfo($description);
        if ($locationInfo) {
            $enhanced = array_merge($enhanced, $locationInfo);
            $enhanced['auto_detected_location'] = true;
        }

        // Extract entities (equipment, people, etc.)
        $enhanced['extracted_entities'] = $this->extractEntities($description);

        // Detect regulation violations
        if (empty($data['regulation_class_broken'])) {
            $enhanced['regulation_class_broken'] = $this->detectRegulationViolation($description);
        }

        return $enhanced;
    }

    /**
     * Detect incident type from description
     * 
     * @param string $description
     * @return string
     */
    private function detectIncidentType($description)
    {
        $patterns = [
            'fire' => ['fire', 'flame', 'burning', 'smoke', 'ignition', 'combustion'],
            'injury' => ['injury', 'hurt', 'injured', 'wound', 'cut', 'bruise', 'broken', 'sprain', 'burn'],
            'chemical_spill' => ['spill', 'chemical', 'leak', 'toxic', 'hazardous', 'contamination'],
            'equipment_failure' => ['equipment', 'machine', 'failure', 'malfunction', 'breakdown', 'fault'],
            'fall' => ['fall', 'fell', 'slip', 'trip', 'dropped', 'height'],
            'electrical' => ['electrical', 'shock', 'electrocution', 'power', 'wire', 'circuit'],
            'near_miss' => ['near miss', 'almost', 'nearly', 'could have', 'close call'],
            'environmental' => ['pollution', 'waste', 'emission', 'environmental', 'discharge']
        ];

        foreach ($patterns as $type => $keywords) {
            foreach ($keywords as $keyword) {
                if (strpos($description, $keyword) !== false) {
                    return $type;
                }
            }
        }

        return 'other';
    }

    /**
     * Detect severity from description
     * 
     * @param string $description
     * @return string
     */
    private function detectSeverity($description)
    {
        $criticalKeywords = ['death', 'fatality', 'critical', 'severe', 'major', 'serious', 'emergency'];
        $highKeywords = ['injury', 'hospital', 'ambulance', 'medical', 'damage', 'evacuation'];
        $lowKeywords = ['minor', 'small', 'little', 'scratch', 'near miss'];

        foreach ($criticalKeywords as $keyword) {
            if (strpos($description, $keyword) !== false) {
                return 'critical';
            }
        }

        foreach ($highKeywords as $keyword) {
            if (strpos($description, $keyword) !== false) {
                return 'high';
            }
        }

        foreach ($lowKeywords as $keyword) {
            if (strpos($description, $keyword) !== false) {
                return 'low';
            }
        }

        return 'medium';
    }

    /**
     * Extract location information from description
     * 
     * @param string $description
     * @return array|null
     */
    private function extractLocationInfo($description)
    {
        // Common Guyana locations and facilities
        $locations = [
            'sbm' => ['name' => 'SBM Offshore', 'lat' => 6.8013, 'lng' => -58.1551],
            'exxonmobil' => ['name' => 'ExxonMobil', 'lat' => 6.8013, 'lng' => -58.1551],
            'georgetown' => ['name' => 'Georgetown', 'lat' => 6.8013, 'lng' => -58.1551],
            'berbice' => ['name' => 'New Amsterdam, Berbice', 'lat' => 6.2484, 'lng' => -57.5084],
            'essequibo' => ['name' => 'Essequibo', 'lat' => 6.5933, 'lng' => -58.4467],
            'linden' => ['name' => 'Linden', 'lat' => 6.0063, 'lng' => -58.3106],
            'platform' => ['name' => 'Offshore Platform', 'lat' => 6.5000, 'lng' => -57.0000],
            'fpso' => ['name' => 'FPSO Vessel', 'lat' => 6.5000, 'lng' => -57.0000],
            'warehouse' => ['name' => 'Warehouse Facility', 'lat' => null, 'lng' => null],
            'office' => ['name' => 'Office Building', 'lat' => null, 'lng' => null]
        ];

        foreach ($locations as $key => $location) {
            if (strpos($description, $key) !== false) {
                $result = [];
                if ($location['lat'] && $location['lng']) {
                    $result['location_lat'] = $location['lat'];
                    $result['location_long'] = $location['lng'];
                }
                return $result;
            }
        }

        return null;
    }

    /**
     * Extract entities from description
     * 
     * @param string $description
     * @return array
     */
    private function extractEntities($description)
    {
        $entities = [
            'equipment' => [],
            'personnel' => [],
            'substances' => []
        ];

        // Equipment patterns
        $equipment = ['crane', 'forklift', 'pump', 'compressor', 'generator', 'drill', 'vessel', 'tank'];
        foreach ($equipment as $item) {
            if (strpos($description, $item) !== false) {
                $entities['equipment'][] = $item;
            }
        }

        // Substance patterns
        $substances = ['oil', 'gas', 'chemical', 'fuel', 'diesel', 'hydraulic fluid'];
        foreach ($substances as $substance) {
            if (strpos($description, $substance) !== false) {
                $entities['substances'][] = $substance;
            }
        }

        return array_filter($entities);
    }

    /**
     * Detect regulation violation
     * 
     * @param string $description
     * @return string|null
     */
    private function detectRegulationViolation($description)
    {
        $violations = [
            'PPE Violation' => ['no helmet', 'no gloves', 'no safety', 'not wearing'],
            'Fire Safety Violation' => ['fire exit blocked', 'no extinguisher', 'smoking'],
            'Chemical Safety Violation' => ['improper storage', 'no ventilation', 'mixed chemicals'],
            'Electrical Safety Violation' => ['exposed wire', 'wet electrical', 'no lockout'],
            'Fall Protection Violation' => ['no harness', 'unsecured ladder', 'no guardrail']
        ];

        foreach ($violations as $violation => $keywords) {
            foreach ($keywords as $keyword) {
                if (strpos($description, $keyword) !== false) {
                    return $violation;
                }
            }
        }

        return null;
    }

    /**
     * Process media files from URLs (for chatbot integration)
     * 
     * @param int $reportId
     * @param array $mediaFiles
     * @return array
     */
    private function processMediaFiles($reportId, $mediaFiles)
    {
        $uploadedFiles = [];

        foreach ($mediaFiles as $mediaFile) {
            try {
                $uploadRecord = ReportUploads::create([
                    'report_id' => $reportId,
                    'file_url' => $mediaFile['url'],
                    'file_type' => $mediaFile['type'],
                    'uploaded_by' => 'WhatsApp Bot',
                    's3_path' => $mediaFile['s3_path'] ?? null,
                    'original_filename' => $mediaFile['filename'] ?? 'whatsapp_media'
                ]);

                $uploadedFiles[] = $uploadRecord;

            } catch (\Exception $e) {
                Log::error('Failed to create upload record', [
                    'report_id' => $reportId,
                    'media_file' => $mediaFile,
                    'error' => $e->getMessage()
                ]);
            }
        }

        return $uploadedFiles;
    }

    /**
     * Send webhook notification to chatbot
     * 
     * @param Report $report
     * @param string $eventType
     * @return void
     */
    private function sendWebhookNotification($report, $eventType)
    {
        try {
            $webhookUrl = config('services.chatbot.webhook_url');
            
            if (!$webhookUrl) {
                return;
            }

            $payload = [
                'event_type' => $eventType,
                'report_id' => $report->id,
                'status' => $report->status,
                'phone_number' => $report->reporter_contact,
                'severity' => $report->severity,
                'assigned_to_name' => $report->assignedTo ? 
                    $report->assignedTo->first_name . ' ' . $report->assignedTo->last_name : null,
                'timestamp' => now()->toISOString()
            ];

            // Send webhook (you can queue this for better performance)
            Http::timeout(10)->post($webhookUrl, $payload);

        } catch (\Exception $e) {
            Log::error('Failed to send webhook notification', [
                'report_id' => $report->id,
                'event_type' => $eventType,
                'error' => $e->getMessage()
            ]);
        }
    }
}