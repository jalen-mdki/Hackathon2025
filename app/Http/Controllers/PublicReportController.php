<?php

namespace App\Http\Controllers;

use App\Models\Report;
use App\Models\ReportUpload;
use App\Http\Requests\StoreReportRequest;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\Validator;
use Inertia\Inertia;

class PublicReportController extends Controller
{
    public function index()
    {
        return Inertia::render('Public/Reports/Create');
    }

    public function store(StoreReportRequest $request)
    {

        try {
            // Create the report
            $report = Report::create([
                'report_type' => $request->report_type,
                'incident_type' => $request->incident_type,
                'description' => $request->description,
                'date_of_incident' => $request->date_of_incident,
                'location_lat' => $request->location_lat,
                'location_long' => $request->location_long,
                'severity' => $request->severity,
                'industry' => $request->industry,
                'reporter_name' => $request->reporter_name,
                'reporter_contact' => $request->reporter_contact,
                'cause_of_death' => $request->cause_of_death,
                'regulation_class_broken' => $request->regulation_class_broken,
                'status' => 'Pending',
                'is_escalated' => false,
                'escalation_status' => 'Not Required',
                'feedback_given' => false,
            ]);

            // Handle file uploads
            // if ($request->hasFile('files')) {
            //     foreach ($request->file('files') as $file) {
            //         $this->handleFileUpload($file, $report->id);
            //     }
            // }

            return redirect()->back()->with('success', 'Report submitted successfully!');

        } catch (\Exception $e) {
            return redirect()->back()
                ->withErrors(['error' => 'An error occurred while submitting the report. Please try again.'])
                ->withInput();
        }
    }

    private function handleFileUpload($file, $reportId)
    {
        try {
            // Generate unique filename with proper sanitization
            $originalName = pathinfo($file->getClientOriginalName(), PATHINFO_FILENAME);
            $extension = $file->getClientOriginalExtension();
            $sanitizedName = preg_replace('/[^A-Za-z0-9\-_]/', '_', $originalName);
            $filename = date('Y/m/d') . '/' . $sanitizedName . '_' . time() . '_' . uniqid() . '.' . $extension;
            
            // Store file directly to S3
            $s3Path = $file->storeAs(
                'incident-reports',
                $filename,
                's3'
            );
            
            // Get the full S3 URL
            $fileUrl = Storage::disk('s3')->url($s3Path);
            
            // Create database record
            ReportUpload::create([
                'report_id' => $reportId,
                'file_url' => $fileUrl,
                'file_type' => $file->getClientMimeType(),
                'uploaded_by' => request()->ip(), // Use IP as identifier for anonymous uploads
                's3_path' => $s3Path,
            ]);

            \Log::info('File uploaded successfully to S3', [
                'filename' => $filename,
                's3_path' => $s3Path,
                'report_id' => $reportId
            ]);

        } catch (\Exception $e) {
            \Log::error('S3 file upload failed', [
                'error' => $e->getMessage(),
                'report_id' => $reportId,
                'file_name' => $file->getClientOriginalName()
            ]);
            throw new \Exception('Failed to upload file to cloud storage: ' . $e->getMessage());
        }
    }

    public function show(Report $report)
    {
        $report->load('uploads');
        return Inertia::render('Reports/Show', [
            'report' => $report
        ]);
    }

    public function list()
    {
        $reports = Report::with('uploads')
            ->orderBy('created_at', 'desc')
            ->paginate(20);

        return Inertia::render('Reports/Index', [
            'reports' => $reports
        ]);
    }

    public function update(Request $request, Report $report)
    {
        $validator = Validator::make($request->all(), [
            'status' => 'required|string|in:Pending,In Progress,Resolved,Closed',
            'assigned_to' => 'nullable|exists:users,id',
            'is_escalated' => 'boolean',
            'escalation_status' => 'string|in:Not Required,Required,Escalated,Resolved',
            'feedback_given' => 'boolean',
        ]);

        if ($validator->fails()) {
            return redirect()->back()->withErrors($validator);
        }

        $report->update($request->only([
            'status',
            'assigned_to',
            'is_escalated',
            'escalation_status',
            'feedback_given'
        ]));

        return redirect()->back()->with('success', 'Report updated successfully!');
    }

    public function destroy(Report $report)
    {
        try {
            // Delete associated files from S3
            foreach ($report->uploads as $upload) {
                if ($upload->s3_path && Storage::disk('s3')->exists($upload->s3_path)) {
                    Storage::disk('s3')->delete($upload->s3_path);
                    \Log::info('File deleted from S3', ['s3_path' => $upload->s3_path]);
                }
            }

            $report->delete();

            return redirect()->route('reports.index')->with('success', 'Report and associated files deleted successfully!');
            
        } catch (\Exception $e) {
            \Log::error('Failed to delete report or files', [
                'report_id' => $report->id,
                'error' => $e->getMessage()
            ]);
            
            return redirect()->route('reports.index')
                ->withErrors(['error' => 'Failed to delete report. Some files may still exist in storage.']);
        }
    }
}