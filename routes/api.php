<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Apis\ChatbotReportController;

Route::get('/user', function (Request $request) {
    return $request->user();
})->middleware('auth:sanctum');


Route::prefix('chatbot')->group(function () {
    // dd('Test');
    
    // Submit incident report from chatbot
    Route::post('/reports', [ChatbotReportController::class, 'submitReport']);
    
    // Submit media files for a report (real-time upload)
    Route::post('/reports/{reportId}/media', [ChatbotReportController::class, 'submitMediaFiles']);
    
    // Get report status for updates
    Route::get('/reports/{id}/status', [ChatbotReportController::class, 'getReportStatus']);
    
    // Webhook endpoints for sending updates back to chatbot
    Route::post('/webhook/status-update', [ChatbotReportController::class, 'receiveStatusUpdate']);
    
});