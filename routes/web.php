<?php

use Illuminate\Support\Facades\Route;
use Inertia\Inertia;
use App\Http\Controllers\Admin\OrganizationController;
use App\Http\Controllers\Admin\ReportController;
use App\Http\Controllers\Admin\UserController;
use App\Http\Controllers\Admin\TrainingController;

Route::get('/', function () {
    return Inertia::render('Welcome');
})->name('home');

Route::get('dashboard', function () {
    return Inertia::render('Dashboard');
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
