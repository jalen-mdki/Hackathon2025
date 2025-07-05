<?php

use Illuminate\Support\Facades\Route;
use Inertia\Inertia;
use App\Http\Controllers\Admin\OrganizationController;

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
});

// Non-admin (general) organization routes placeholder for future expansion
// Route::middleware(['auth', 'verified'])->group(function () {
//     Route::get('organizations', [OrganizationController::class, 'publicIndex'])->name('organizations.public.index');
//     Route::get('organizations/{organization}', [OrganizationController::class, 'show'])->name('organizations.show');
// });

require __DIR__.'/settings.php';
require __DIR__.'/auth.php';
