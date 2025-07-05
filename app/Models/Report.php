<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Report extends Model
{
    use HasFactory;

    protected $fillable = [
        'report_type',
        'incident_type',
        'description',
        'date_of_incident',
        'location_lat',
        'location_long',
        'severity',
        'industry',
        'reporter_name',
        'reporter_contact',
        'status',
        'assigned_to',
        'organization_id',
        'reported_by_user_id',
        'is_escalated',
        'escalation_status',
        'cause_of_death',
        'regulation_class_broken',
        'feedback_given',
    ];

    protected $casts = [
        'date_of_incident' => 'date',
        'location_lat' => 'decimal:7',
        'location_long' => 'decimal:7',
        'is_escalated' => 'boolean',
        'feedback_given' => 'boolean',
    ];

    /**
     * Get the organization that owns the report
     */
    public function organization(): BelongsTo
    {
        return $this->belongsTo(Organization::class);
    }

    /**
     * Get the user who reported this incident
     */
    public function reportedByUser(): BelongsTo
    {
        return $this->belongsTo(User::class, 'reported_by_user_id');
    }

    /**
     * Get the user assigned to this report
     */
    public function assignedToUser(): BelongsTo
    {
        return $this->belongsTo(User::class, 'assigned_to');
    }

    /**
     * Get all uploads for this report
     */
    public function reportUploads(): HasMany
    {
        return $this->hasMany(ReportUploads::class);
    }

    /**
     * Get all escalations for this report
     */
    public function reportEscalations(): HasMany
    {
        return $this->hasMany(ReportEscalation::class);
    }

    /**
     * Scope to filter by status
     */
    public function scopeStatus($query, $status)
    {
        return $query->where('status', $status);
    }

    /**
     * Scope to filter by severity
     */
    public function scopeSeverity($query, $severity)
    {
        return $query->where('severity', $severity);
    }

    /**
     * Scope to filter escalated reports
     */
    public function scopeEscalated($query, $escalated = true)
    {
        return $query->where('is_escalated', $escalated);
    }

    /**
     * Get the status color for display
     */
    public function getStatusColorAttribute()
    {
        $colors = [
            'Pending' => 'yellow',
            'In Progress' => 'blue',
            'Completed' => 'green',
            'Closed' => 'gray',
            'Under Review' => 'purple',
        ];

        return $colors[$this->status] ?? 'gray';
    }

    /**
     * Get the severity color for display
     */
    public function getSeverityColorAttribute()
    {
        $colors = [
            'Low' => 'green',
            'Medium' => 'yellow',
            'High' => 'orange',
            'Critical' => 'red',
        ];

        return $colors[$this->severity] ?? 'gray';
    }
}