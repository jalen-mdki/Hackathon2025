<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Models\Training;
use App\Models\UserTraining;
use Illuminate\Http\Request;
use Illuminate\Http\Response;
use Illuminate\Support\Facades\Validator;
use Illuminate\Support\Facades\DB;

class TrainingController extends Controller
{
    /**
     * Display a listing of the trainings.
     */
    public function index(Request $request)
    {
        $query = Training::query();

        // Search functionality
        if ($request->has('search') && !empty($request->search)) {
            $search = $request->search;
            $query->where(function ($q) use ($search) {
                $q->where('name', 'LIKE', "%{$search}%")
                  ->orWhere('description', 'LIKE', "%{$search}%")
                  ->orWhere('industry', 'LIKE', "%{$search}%");
            });
        }

        // Filter by industry
        if ($request->has('industry') && !empty($request->industry)) {
            $query->where('industry', $request->industry);
        }

        // Add enrollment counts
        $trainings = $query->withCount(['userTrainings as enrolled_count'])
                          ->orderBy('created_at', 'desc')
                          ->get();

        // Get statistics
        $stats = [
            'total_trainings' => Training::count(),
            'industries_covered' => Training::distinct('industry')->whereNotNull('industry')->count(),
            'active_programs' => Training::count(), // All trainings are considered active
            'total_enrollments' => UserTraining::count()
        ];

        // Get available industries for filter
        $industries = Training::distinct('industry')
                            ->whereNotNull('industry')
                            ->pluck('industry')
                            ->sort()
                            ->values();

        // Current filters
        $filters = [
            'search' => $request->search,
            'industry' => $request->industry,
        ];

        // Return JSON for API requests
        if ($request->expectsJson()) {
            return response()->json([
                'trainings' => $trainings,
                'stats' => $stats,
                'industries' => $industries,
                'filters' => $filters
            ]);
        }

        // Return Inertia response for web requests
        return inertia('Admin/Training/Index', [
            'trainings' => $trainings,
            'stats' => $stats,
            'industries' => $industries,
            'filters' => $filters
        ]);
    }

    /**
     * Show the form for creating a new training.
     */
    public function create()
    {
        $industries = [
            'Mining',
            'Construction', 
            'Manufacturing',
            'Healthcare',
            'Energy',
            'Transportation',
            'Agriculture',
            'Other'
        ];

        if (request()->expectsJson()) {
            return response()->json(['industries' => $industries]);
        }

        return view('trainings.create', compact('industries'));
    }

    /**
     * Store a newly created training in storage.
     */
    public function store(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'name' => 'required|string|max:255|unique:trainings,name',
            'description' => 'nullable|string',
            'industry' => 'nullable|string|max:255',
        ]);

        if ($validator->fails()) {
            if ($request->expectsJson()) {
                return response()->json([
                    'success' => false,
                    'message' => 'Validation failed',
                    'errors' => $validator->errors()
                ], 422);
            }

            return back()->withErrors($validator)->withInput();
        }

        try {
            $training = Training::create([
                'name' => $request->name,
                'description' => $request->description,
                'industry' => $request->industry,
            ]);

            if ($request->expectsJson()) {
                return response()->json([
                    'success' => true,
                    'message' => 'Training created successfully',
                    'training' => $training
                ], 201);
            }

            return redirect()->route('trainings.index')
                           ->with('success', 'Training created successfully');

        } catch (\Exception $e) {
            if ($request->expectsJson()) {
                return response()->json([
                    'success' => false,
                    'message' => 'Failed to create training',
                    'error' => $e->getMessage()
                ], 500);
            }

            return back()->with('error', 'Failed to create training')
                        ->withInput();
        }
    }

    /**
     * Display the specified training.
     */
    public function show(Training $training)
    {
        // Load related data
        $training->load(['userTrainings.user', 'userTrainings.organization']);
        
        // Get enrollment statistics
        $enrollmentStats = [
            'total_enrolled' => $training->userTrainings->count(),
            'completed' => $training->userTrainings->where('status', 'Completed')->count(),
            'pending' => $training->userTrainings->where('status', 'Pending')->count(),
            'in_progress' => $training->userTrainings->where('status', 'In Progress')->count(),
        ];

        // Get enrollments by organization
        $organizationStats = $training->userTrainings()
                                    ->with('organization')
                                    ->select('organization_id', DB::raw('count(*) as count'))
                                    ->groupBy('organization_id')
                                    ->get()
                                    ->map(function ($item) {
                                        return [
                                            'organization' => $item->organization->name ?? 'Unknown',
                                            'count' => $item->count
                                        ];
                                    });

        if (request()->expectsJson()) {
            return response()->json([
                'training' => $training,
                'enrollment_stats' => $enrollmentStats,
                'organization_stats' => $organizationStats
            ]);
        }

        return view('trainings.show', compact('training', 'enrollmentStats', 'organizationStats'));
    }

    /**
     * Show the form for editing the specified training.
     */
    public function edit(Training $training)
    {
        $industries = [
            'Mining',
            'Construction', 
            'Manufacturing',
            'Healthcare',
            'Energy',
            'Transportation',
            'Agriculture',
            'Other'
        ];

        if (request()->expectsJson()) {
            return response()->json([
                'training' => $training,
                'industries' => $industries
            ]);
        }

        return view('trainings.edit', compact('training', 'industries'));
    }

    /**
     * Update the specified training in storage.
     */
    public function update(Request $request, Training $training)
    {
        $validator = Validator::make($request->all(), [
            'name' => 'required|string|max:255|unique:trainings,name,' . $training->id,
            'description' => 'nullable|string',
            'industry' => 'nullable|string|max:255',
        ]);

        if ($validator->fails()) {
            if ($request->expectsJson()) {
                return response()->json([
                    'success' => false,
                    'message' => 'Validation failed',
                    'errors' => $validator->errors()
                ], 422);
            }

            return back()->withErrors($validator)->withInput();
        }

        try {
            $training->update([
                'name' => $request->name,
                'description' => $request->description,
                'industry' => $request->industry,
            ]);

            if ($request->expectsJson()) {
                return response()->json([
                    'success' => true,
                    'message' => 'Training updated successfully',
                    'training' => $training
                ]);
            }

            return redirect()->route('trainings.index')
                           ->with('success', 'Training updated successfully');

        } catch (\Exception $e) {
            if ($request->expectsJson()) {
                return response()->json([
                    'success' => false,
                    'message' => 'Failed to update training',
                    'error' => $e->getMessage()
                ], 500);
            }

            return back()->with('error', 'Failed to update training')
                        ->withInput();
        }
    }

    /**
     * Remove the specified training from storage.
     */
    public function destroy(Training $training)
    {
        try {
            // Check if training has enrollments
            $enrollmentCount = $training->userTrainings()->count();
            
            if ($enrollmentCount > 0) {
                if (request()->expectsJson()) {
                    return response()->json([
                        'success' => false,
                        'message' => "Cannot delete training. It has {$enrollmentCount} enrollments."
                    ], 422);
                }

                return back()->with('error', "Cannot delete training. It has {$enrollmentCount} enrollments.");
            }

            $training->delete();

            if (request()->expectsJson()) {
                return response()->json([
                    'success' => true,
                    'message' => 'Training deleted successfully'
                ]);
            }

            return redirect()->route('trainings.index')
                           ->with('success', 'Training deleted successfully');

        } catch (\Exception $e) {
            if (request()->expectsJson()) {
                return response()->json([
                    'success' => false,
                    'message' => 'Failed to delete training',
                    'error' => $e->getMessage()
                ], 500);
            }

            return back()->with('error', 'Failed to delete training');
        }
    }

    /**
     * Get enrollment details for a specific training
     */
    public function enrollments(Training $training)
    {
        $enrollments = $training->userTrainings()
                               ->with(['user', 'organization'])
                               ->orderBy('created_at', 'desc')
                               ->get();

        if (request()->expectsJson()) {
            return response()->json([
                'training' => $training,
                'enrollments' => $enrollments
            ]);
        }

        return view('trainings.enrollments', compact('training', 'enrollments'));
    }

    /**
     * Bulk operations for trainings
     */
    public function bulkAction(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'action' => 'required|string|in:delete,update_industry',
            'training_ids' => 'required|array',
            'training_ids.*' => 'exists:trainings,id',
            'industry' => 'required_if:action,update_industry|string|max:255'
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'message' => 'Validation failed',
                'errors' => $validator->errors()
            ], 422);
        }

        try {
            $trainings = Training::whereIn('id', $request->training_ids);

            switch ($request->action) {
                case 'delete':
                    // Check for enrollments before deleting
                    $enrollmentCount = UserTraining::whereIn('training_id', $request->training_ids)->count();
                    
                    if ($enrollmentCount > 0) {
                        return response()->json([
                            'success' => false,
                            'message' => "Cannot delete trainings. They have {$enrollmentCount} total enrollments."
                        ], 422);
                    }

                    $deleted = $trainings->delete();
                    
                    return response()->json([
                        'success' => true,
                        'message' => "{$deleted} trainings deleted successfully"
                    ]);

                case 'update_industry':
                    $updated = $trainings->update(['industry' => $request->industry]);
                    
                    return response()->json([
                        'success' => true,
                        'message' => "{$updated} trainings updated successfully"
                    ]);

                default:
                    return response()->json([
                        'success' => false,
                        'message' => 'Invalid action'
                    ], 422);
            }

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'Bulk operation failed',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Get training statistics
     */
    public function statistics()
    {
        $stats = [
            'total_trainings' => Training::count(),
            'industries_covered' => Training::distinct('industry')->whereNotNull('industry')->count(),
            'total_enrollments' => UserTraining::count(),
            'completed_trainings' => UserTraining::where('status', 'Completed')->count(),
            'pending_trainings' => UserTraining::where('status', 'Pending')->count(),
            'in_progress_trainings' => UserTraining::where('status', 'In Progress')->count(),
        ];

        // Training by industry
        $trainingsByIndustry = Training::select('industry', DB::raw('count(*) as count'))
                                     ->whereNotNull('industry')
                                     ->groupBy('industry')
                                     ->orderBy('count', 'desc')
                                     ->get();

        // Enrollment trends (last 6 months)
        $enrollmentTrends = UserTraining::select(
                                DB::raw('DATE_FORMAT(created_at, "%Y-%m") as month'),
                                DB::raw('count(*) as count')
                            )
                            ->where('created_at', '>=', now()->subMonths(6))
                            ->groupBy('month')
                            ->orderBy('month')
                            ->get();

        return response()->json([
            'stats' => $stats,
            'trainings_by_industry' => $trainingsByIndustry,
            'enrollment_trends' => $enrollmentTrends
        ]);
    }
}