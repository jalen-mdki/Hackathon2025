<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class ReportEscalation extends Model
{
    use HasFactory;

    protected $fillable = [
        'report_id',
        'escalated_by_user_id',
        'escalation_reason',
        'escalated_at',
    ];

    protected $casts = [
        'escalated_at' => 'datetime',
    ];

    /**
     * Get the report that was escalated
     */
    public function report(): BelongsTo
    {
        return $this->belongsTo(Report::class);
    }

    /**
     * Get the user who escalated the report
     */
    public function escalatedByUser(): BelongsTo
    {
        return $this->belongsTo(User::class, 'escalated_by_user_id');
    }
}