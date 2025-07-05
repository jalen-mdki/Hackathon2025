<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Models\Report;
use App\Models\Organization;
use App\Models\ReportUploads;
use App\Models\User;
use Illuminate\Http\Request;
use Inertia\Inertia;

class ReportController extends Controller
{
    public function index(Request $request)
    {
        $query = Report::with([
            'organization', 
            'reportedByUser', 
            'reportUploads', 
            'reportEscalations.escalatedByUser'
        ]);

        // Search functionality
        if ($request->filled('search')) {
            $searchTerm = $request->search;
            $query->where(function ($q) use ($searchTerm) {
                $q->where('report_type', 'like', "%{$searchTerm}%")
                  ->orWhere('description', 'like', "%{$searchTerm}%")
                  ->orWhere('incident_type', 'like', "%{$searchTerm}%")
                  ->orWhere('reporter_name', 'like', "%{$searchTerm}%")
                  ->orWhere('reporter_contact', 'like', "%{$searchTerm}%")
                  ->orWhereHas('organization', function ($orgQuery) use ($searchTerm) {
                      $orgQuery->where('name', 'like', "%{$searchTerm}%");
                  })
                  ->orWhereHas('reportedByUser', function ($userQuery) use ($searchTerm) {
                      $userQuery->where('first_name', 'like', "%{$searchTerm}%")
                               ->orWhere('last_name', 'like', "%{$searchTerm}%")
                               ->orWhere('email', 'like', "%{$searchTerm}%");
                  });
            });
        }

        // Status filter
        if ($request->filled('status')) {
            $query->where('status', $request->status);
        }

        // Severity filter
        if ($request->filled('severity')) {
            $query->where('severity', $request->severity);
        }

        // Report type filter
        if ($request->filled('report_type')) {
            $query->where('report_type', $request->report_type);
        }

        // Industry filter
        if ($request->filled('industry')) {
            $query->where('industry', $request->industry);
        }

        // Escalation filter
        if ($request->filled('escalated')) {
            $isEscalated = $request->escalated === 'true';
            $query->where('is_escalated', $isEscalated);
        }

        // Date range filters
        if ($request->filled('date_from')) {
            $query->whereDate('date_of_incident', '>=', $request->date_from);
        }

        if ($request->filled('date_to')) {
            $query->whereDate('date_of_incident', '<=', $request->date_to);
        }

        // Order by latest first
        $query->latest();

        $reports = $query->paginate(20)->withQueryString();

        return Inertia::render('Admin/Reports/Index', [
            'reports' => $reports,
            'filters' => [
                'search' => $request->search,
                'status' => $request->status,
                'severity' => $request->severity,
                'report_type' => $request->report_type,
                'industry' => $request->industry,
                'escalated' => $request->escalated,
                'date_from' => $request->date_from,
                'date_to' => $request->date_to,
            ],
        ]);
    }

    public function show(Report $report)
    {
        $report->load(['organization', 'reportedByUser', 'reportUploads', 'reportEscalations.escalatedByUser']);
        
        return Inertia::render('Admin/Reports/Show', [
            'report' => $report,
        ]);
    }

    public function create()
    {
        $organizations = Organization::select('id', 'name')->get();
        $users = User::select('id', 'first_name', 'last_name', 'email')->get();
        
        return Inertia::render('Admin/Reports/Create', [
            'organizations' => $organizations,
            'users' => $users,
        ]);
    }

    public function store(Request $request)
    {
        $validated = $request->validate([
            'organization_id' => 'required|exists:organizations,id',
            'report_type' => 'required|string|max:255',
            'incident_type' => 'nullable|string|max:255',
            'description' => 'required|string',
            'status' => 'required|string',
            'reported_by_user_id' => 'required|exists:users,id',
            'date_of_incident' => 'required|date',
            'severity' => 'nullable|string|in:Low,Medium,High,Critical',
            'industry' => 'nullable|string|max:255',
            'reporter_name' => 'nullable|string|max:255',
            'reporter_contact' => 'nullable|string|max:255',
            'location_lat' => 'nullable|numeric|between:-90,90',
            'location_long' => 'nullable|numeric|between:-180,180',
            'cause_of_death' => 'nullable|string|max:255',
            'regulation_class_broken' => 'nullable|string|max:255',
            'assigned_to' => 'nullable|exists:users,id',
            'attachments' => 'nullable|array',
            'attachments.*' => 'file|mimes:jpg,jpeg,png,gif,webp,bmp,tiff,mp4,webm,ogg,avi,mov,wmv,flv,mkv,pdf,doc,docx|max:102400', // 100MB max per file
        ]);

        // Remove attachments from validated data as we'll handle them separately
        $attachmentFiles = $validated['attachments'] ?? [];
        unset($validated['attachments']);

        $report = Report::create($validated);

         // Handle multiple file uploads to S3
        if (!empty($attachmentFiles)) {
            foreach ($attachmentFiles as $file) {
                // Generate unique filename to prevent conflicts
                $originalName = $file->getClientOriginalName();
                $extension = $file->getClientOriginalExtension();
                $filename = 'reports/' . $report->id . '/' . time() . '_' . uniqid() . '.' . $extension;
                
                try {
                    // Upload to S3
                    $path = $file->storeAs('', $filename, 's3');
                    $s3Url = \Storage::disk('s3')->url($path);
                    
                    ReportUploads::create([
                        'report_id' => $report->id,
                        'file_url' => $s3Url,
                        'file_type' => $file->getMimeType(),
                        'uploaded_by' => auth()->user()->first_name . ' ' . auth()->user()->last_name,
                        'original_filename' => $originalName,
                        's3_path' => $path, // Store S3 path for easier management
                    ]);
                } catch (\Exception $e) {
                    \Log::error('Failed to upload file to S3: ' . $e->getMessage(), [
                        'file' => $originalName,
                        'report_id' => $report->id
                    ]);
                    
                    // Continue with other files, but log the error
                    continue;
                }
            }
        }

        $successfulUploads = $report->reportUploads()->count();
        $message = $successfulUploads > 0 
            ? "Report created successfully with {$successfulUploads} attachment(s)."
            : "Report created successfully.";

        return redirect()->route('admin.reports.show', $report->id)
            ->with('success', $message);
    }

    public function edit(Report $report)
    {
        $report->load(['organization', 'reportedByUser', 'reportUploads']);
        $organizations = Organization::select('id', 'name')->get();
        $users = User::select('id', 'first_name', 'last_name', 'email')->get();
        
        return Inertia::render('Admin/Reports/Edit', [
            'report' => $report,
            'organizations' => $organizations,
            'users' => $users,
        ]);
    }

    public function update(Request $request, Report $report)
    {
        $validated = $request->validate([
            'organization_id' => 'required|exists:organizations,id',
            'report_type' => 'required|string|max:255',
            'incident_type' => 'nullable|string|max:255',
            'description' => 'required|string',
            'status' => 'required|string',
            'reported_by_user_id' => 'required|exists:users,id',
            'date_of_incident' => 'required|date',
            'severity' => 'nullable|string|in:Low,Medium,High,Critical',
            'industry' => 'nullable|string|max:255',
            'reporter_name' => 'nullable|string|max:255',
            'reporter_contact' => 'nullable|string|max:255',
            'location_lat' => 'nullable|numeric|between:-90,90',
            'location_long' => 'nullable|numeric|between:-180,180',
            'cause_of_death' => 'nullable|string|max:255',
            'regulation_class_broken' => 'nullable|string|max:255',
            'is_escalated' => 'nullable|boolean',
            'escalation_status' => 'nullable|string|max:255',
            'feedback_given' => 'nullable|boolean',
            'attachments' => 'nullable|array',
            'attachments.*' => 'file|mimes:jpg,jpeg,png,gif,webp,bmp,tiff,mp4,webm,ogg,avi,mov,wmv,flv,mkv,pdf,doc,docx|max:102400',
        ]);

        $report->update($validated);

        // Handle new file uploads
        if ($request->hasFile('attachments')) {
            foreach ($request->file('attachments') as $file) {
                $path = $file->store('report-attachments', 'public');
                
                $report->reportUploads()->create([
                    'file_url' => asset('storage/' . $path),
                    'file_type' => $file->getMimeType(),
                    'uploaded_by' => auth()->user()->first_name . ' ' . auth()->user()->last_name,
                ]);
            }
        }

        return redirect()->route('admin.reports.show', $report->id)
            ->with('success', 'Report updated successfully.');
    }

    public function destroy(Report $report)
    {
        // Delete associated files from storage
        foreach ($report->reportUploads as $upload) {
            $filePath = str_replace(asset('storage/'), '', $upload->file_url);
            \Storage::disk('public')->delete($filePath);
        }

        $report->delete();

        return redirect()->route('admin.reports.index')
            ->with('success', 'Report deleted successfully.');
    }

    public function escalate(Request $request, Report $report)
    {
        $validated = $request->validate([
            'escalation_priority' => 'required|string|in:Critical,High,Medium',
            'escalation_reason' => 'required|string|min:10',
            'notify_users' => 'required|array|min:1',
            'notify_users.*' => 'exists:users,id',
        ]);

        $report->update([
            'is_escalated' => true,
            'escalation_status' => 'Escalated',
        ]);

        $escalation = $report->reportEscalations()->create([
            'escalated_by_user_id' => auth()->id(),
            'escalation_reason' => $validated['escalation_reason'],
            'escalation_priority' => $validated['escalation_priority'],
            'escalated_at' => now(),
        ]);

        // Create notifications for each user
        foreach ($validated['notify_users'] as $userId) {
            $escalation->notifications()->create([
                'user_id' => $userId,
                'notification_type' => 'email', // or determine type dynamically
                'status' => 'pending',
                'metadata' => json_encode([
                    'initiated_by' => auth()->user()->name,
                    'report_id' => $report->id,
                    'priority' => $validated['escalation_priority'],
                ]),
            ]);
        }

        return redirect()->back()->with('success', 'Report escalated successfully.');
    }


    /**
     * Remove file attachment
     */
    public function removeAttachment(Request $request, Report $report, $attachmentId)
    {
        $attachment = $report->reportUploads()->findOrFail($attachmentId);
        
        // Delete file from storage
        $filePath = str_replace(asset('storage/'), '', $attachment->file_url);
        \Storage::disk('public')->delete($filePath);
        
        // Delete database record
        $attachment->delete();

        return redirect()->back()->with('success', 'Attachment removed successfully.');
    }
}