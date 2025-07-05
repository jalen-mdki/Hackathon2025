<?php

use Illuminate\Support\Facades\Route;
use Inertia\Inertia;
use App\Http\Controllers\Admin\OrganizationController;
use App\Http\Controllers\Admin\ReportController;
use App\Http\Controllers\Admin\UserController;
use App\Http\Controllers\Admin\TrainingController;
use App\Models\UserTraining;
use App\Models\Report;
use App\Models\Hazards;

Route::get('/', function () {
    return Inertia::render('Welcome');
})->name('home');

Route::get('dashboard', function () {
    // Existing queries...
    $reportStatusCounts = Report::select('status', DB::raw('count(*) as total'))
        ->groupBy('status')
        ->pluck('total', 'status');

    $trainingStatusCounts = UserTraining::select('status', DB::raw('count(*) as total'))
        ->groupBy('status')
        ->pluck('total', 'status');

    $hazardRiskCounts = Hazards::select('risk_level', DB::raw('count(*) as total'))
        ->groupBy('risk_level')
        ->pluck('total', 'risk_level');

    $reportsByMonth = Report::select(DB::raw("DATE_FORMAT(created_at, '%Y-%m') as month"), DB::raw('count(*) as total'))
        ->where('created_at', '>=', now()->subMonths(12))
        ->groupBy('month')
        ->orderBy('month')
        ->pluck('total', 'month');

    $reportTypeCounts = Report::select('report_type', DB::raw('count(*) as total'))
        ->groupBy('report_type')
        ->pluck('total', 'report_type');

    $incidentTypeCounts = Report::select('incident_type', DB::raw('count(*) as total'))
        ->whereNotNull('incident_type')
        ->groupBy('incident_type')
        ->pluck('total', 'incident_type');

    $severityCounts = Report::select('severity', DB::raw('count(*) as total'))
        ->whereNotNull('severity')
        ->groupBy('severity')
        ->pluck('total', 'severity');
    
    // Add this query to get reports with location data
    $mapReports = Report::select([
            'id',
            'location_lat as lat',
            'location_long as lng',
            'severity',
            'report_type as type',
            'status',
            'description'
        ])
        ->whereNotNull('location_lat')
        ->whereNotNull('location_long')
        ->get();

    return Inertia::render('Dashboard', [
        'reportStatusData' => [
            'labels' => $reportStatusCounts->keys(),
            'datasets' => [[
                'label' => 'Reports by Status',
                'data' => $reportStatusCounts->values(),
            ]]
        ],
        'trainingStatusData' => [
            'labels' => $trainingStatusCounts->keys(),
            'datasets' => [[
                'label' => 'Trainings by Status',
                'data' => $trainingStatusCounts->values(),
            ]]
        ],
        'hazardsByRiskData' => [
            'labels' => $hazardRiskCounts->keys(),
            'datasets' => [[
                'label' => 'Hazards by Risk Level',
                'data' => $hazardRiskCounts->values(),
            ]]
        ],
        'reportsByMonthData' => [
            'labels' => $reportsByMonth->keys(),
            'datasets' => [[
                'label' => 'Reports by Month',
                'data' => $reportsByMonth->values(),
            ]]
        ],
        'reportTypeData' => [
            'labels' => $reportTypeCounts->keys(),
            'datasets' => [[
                'label' => 'Reports by Type',
                'data' => $reportTypeCounts->values(),
            ]]
        ],
        'incidentTypeData' => [
            'labels' => $incidentTypeCounts->keys(),
            'datasets' => [[
                'label' => 'Incidents by Type', 
                'data' => $incidentTypeCounts->values(),
            ]]
        ],
        'severityBreakdownData' => [
            'labels' => $severityCounts->keys(),
            'datasets' => [[
                'label' => 'Incidents by Severity',
                'data' => $severityCounts->values(),
            ]]
        ],
        // Add the map reports data
        'mapReportsData' => $mapReports
    ]);
})->middleware(['auth', 'verified'])->name('dashboard');

// Admin Organization Routes
Route::middleware(['auth', 'verified', 'can:admin-access'])->prefix('admin')->name('admin.')->group(function () {
    Route::get('organizations', [OrganizationController::class, 'index'])->name('organizations.index');
    Route::get('organizations/create', [OrganizationController::class, 'create'])->name('organizations.create');
    Route::post('organizations', [OrganizationController::class, 'store'])->name('organizations.store');
    Route::get('organizations/{organization}/edit', [OrganizationController::class, 'edit'])->name('organizations.edit');
    Route::put('organizations/{organization}', [OrganizationController::class, 'update'])->name('organizations.update');
    Route::get('organizations/{organization}', [OrganizationController::class, 'show'])->name('organizations.show');

    Route::prefix('reports')->name('reports.')->group(function () {
        Route::get('/', [ReportController::class, 'index'])->name('index');
        Route::get('/create', [ReportController::class, 'create'])->name('create');
        Route::post('/', [ReportController::class, 'store'])->name('store');
        Route::get('/{report}', [ReportController::class, 'show'])->name('show');
        Route::get('/{report}/edit', [ReportController::class, 'edit'])->name('edit');
        Route::put('/{report}', [ReportController::class, 'update'])->name('update');
        Route::delete('/{report}', [ReportController::class, 'destroy'])->name('destroy');

        Route::post('/{report}/escalate', [ReportController::class, 'escalate'])->name('reports.escalate');
        Route::post('/{report}/resolve-escalation', [ReportController::class, 'resolveEscalation'])->name('reports.resolve-escalation');
    
    });

    Route::get('escalations', [EscalationController::class, 'index'])->name('escalations.index');
    Route::get('escalations/{escalation}', [EscalationController::class, 'show'])->name('escalations.show');
    Route::post('escalations/{escalation}/assign', [EscalationController::class, 'assign'])->name('escalations.assign');
    Route::post('escalations/{escalation}/update', [EscalationController::class, 'addUpdate'])->name('escalations.update');
    Route::resource('users', UserController::class);

    Route::resource('trainings', TrainingController::class);
    
    // Additional Training Routes
    Route::get('trainings/{training}/enrollments', [TrainingController::class, 'enrollments'])
        ->name('trainings.enrollments');
    
    Route::post('trainings/bulk-action', [TrainingController::class, 'bulkAction'])
        ->name('trainings.bulk-action');
    
    Route::get('trainings-statistics', [TrainingController::class, 'statistics'])
        ->name('trainings.statistics');
});

// Non-admin (general) organization routes placeholder for future expansion
// Route::middleware(['auth', 'verified'])->group(function () {
//     Route::get('organizations', [OrganizationController::class, 'publicIndex'])->name('organizations.public.index');
//     Route::get('organizations/{organization}', [OrganizationController::class, 'show'])->name('organizations.show');
// });

require __DIR__.'/settings.php';
require __DIR__.'/auth.php';
