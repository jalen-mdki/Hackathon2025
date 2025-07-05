<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class ReportEscalation extends Model
{
    use HasFactory;

    protected $fillable = [
        'report_id',
        'escalated_by_user_id',
        'escalation_reason',
        'escalation_priority',
        'immediate_action_required',
        'estimated_resolution_time',
        'additional_notes',
        'escalated_at',
        'resolved_at',
        'resolved_by_user_id',
        'resolution_notes',
        'resolved_by_action',
    ];

    protected $casts = [
        'escalated_at' => 'datetime',
        'resolved_at' => 'datetime',
        'immediate_action_required' => 'boolean',
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

    /**
     * Get the user who resolved the escalation
     */
    public function resolvedByUser(): BelongsTo
    {
        return $this->belongsTo(User::class, 'resolved_by_user_id');
    }

    /**
     * Get all notifications for this escalation
     */
    public function notifications(): HasMany
    {
        return $this->hasMany(EscalationNotification::class);
    }

    /**
     * Check if escalation is resolved
     */
    public function isResolved(): bool
    {
        return !is_null($this->resolved_at);
    }

    /**
     * Get escalation priority color
     */
    public function getPriorityColorAttribute(): string
    {
        $colors = [
            'Critical' => 'from-red-500 to-red-600',
            'High' => 'from-orange-500 to-orange-600',
            'Medium' => 'from-yellow-500 to-yellow-600',
            'Low' => 'from-blue-500 to-blue-600',
        ];

        return $colors[$this->escalation_priority] ?? 'from-gray-500 to-gray-600';
    }

    /**
     * Get escalation priority icon
     */
    public function getPriorityIconAttribute(): string
    {
        $icons = [
            'Critical' => '🚨',
            'High' => '⚠️',
            'Medium' => '⚡',
            'Low' => '📋',
        ];

        return $icons[$this->escalation_priority] ?? '📋';
    }

    /**
     * Get time since escalation
     */
    public function getTimeSinceEscalationAttribute(): string
    {
        $diff = now()->diff($this->escalated_at);
        
        if ($diff->days > 0) {
            return $diff->days . ' day' . ($diff->days > 1 ? 's' : '') . ' ago';
        } elseif ($diff->h > 0) {
            return $diff->h . ' hour' . ($diff->h > 1 ? 's' : '') . ' ago';
        } else {
            return $diff->i . ' minute' . ($diff->i > 1 ? 's' : '') . ' ago';
        }
    }

    /**
     * Get resolution time if resolved
     */
    public function getResolutionTimeAttribute(): ?string
    {
        if (!$this->isResolved()) {
            return null;
        }

        $diff = $this->resolved_at->diff($this->escalated_at);
        
        if ($diff->days > 0) {
            return $diff->days . ' day' . ($diff->days > 1 ? 's' : '');
        } elseif ($diff->h > 0) {
            return $diff->h . ' hour' . ($diff->h > 1 ? 's' : '');
        } else {
            return $diff->i . ' minute' . ($diff->i > 1 ? 's' : '');
        }
    }
}