<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class UserTraining extends Model
{
    use HasFactory;

    /**
     * The table associated with the model.
     *
     * @var string
     */
    protected $table = 'user_trainings';

    /**
     * The attributes that are mass assignable.
     *
     * @var array<int, string>
     */
    protected $fillable = [
        'user_id',
        'organization_id',
        'training_id',
        'status',
        'completed_at',
    ];

    /**
     * The attributes that should be cast.
     *
     * @var array<string, string>
     */
    protected $casts = [
        'completed_at' => 'datetime',
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    /**
     * The possible status values for training enrollment.
     *
     * @var array<string>
     */
    const STATUSES = [
        'Pending',
        'In Progress',
        'Completed',
        'Failed',
        'Cancelled'
    ];

    /**
     * Get the user that owns the training enrollment.
     *
     * @return BelongsTo
     */
    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    /**
     * Get the organization associated with this training enrollment.
     *
     * @return BelongsTo
     */
    public function organization(): BelongsTo
    {
        return $this->belongsTo(Organization::class);
    }

    /**
     * Get the training associated with this enrollment.
     *
     * @return BelongsTo
     */
    public function training(): BelongsTo
    {
        return $this->belongsTo(Training::class);
    }

    /**
     * Scope to filter by status.
     *
     * @param \Illuminate\Database\Eloquent\Builder $query
     * @param string $status
     * @return \Illuminate\Database\Eloquent\Builder
     */
    public function scopeByStatus($query, $status)
    {
        return $query->where('status', $status);
    }

    /**
     * Scope to filter completed enrollments.
     *
     * @param \Illuminate\Database\Eloquent\Builder $query
     * @return \Illuminate\Database\Eloquent\Builder
     */
    public function scopeCompleted($query)
    {
        return $query->where('status', 'Completed');
    }

    /**
     * Scope to filter pending enrollments.
     *
     * @param \Illuminate\Database\Eloquent\Builder $query
     * @return \Illuminate\Database\Eloquent\Builder
     */
    public function scopePending($query)
    {
        return $query->where('status', 'Pending');
    }

    /**
     * Scope to filter in-progress enrollments.
     *
     * @param \Illuminate\Database\Eloquent\Builder $query
     * @return \Illuminate\Database\Eloquent\Builder
     */
    public function scopeInProgress($query)
    {
        return $query->where('status', 'In Progress');
    }

    /**
     * Scope to filter by organization.
     *
     * @param \Illuminate\Database\Eloquent\Builder $query
     * @param int $organizationId
     * @return \Illuminate\Database\Eloquent\Builder
     */
    public function scopeByOrganization($query, $organizationId)
    {
        return $query->where('organization_id', $organizationId);
    }

    /**
     * Scope to filter by training.
     *
     * @param \Illuminate\Database\Eloquent\Builder $query
     * @param int $trainingId
     * @return \Illuminate\Database\Eloquent\Builder
     */
    public function scopeByTraining($query, $trainingId)
    {
        return $query->where('training_id', $trainingId);
    }

    /**
     * Mark the training as completed.
     *
     * @return bool
     */
    public function markAsCompleted(): bool
    {
        return $this->update([
            'status' => 'Completed',
            'completed_at' => now(),
        ]);
    }

    /**
     * Mark the training as in progress.
     *
     * @return bool
     */
    public function markAsInProgress(): bool
    {
        return $this->update([
            'status' => 'In Progress',
            'completed_at' => null,
        ]);
    }

    /**
     * Mark the training as failed.
     *
     * @return bool
     */
    public function markAsFailed(): bool
    {
        return $this->update([
            'status' => 'Failed',
            'completed_at' => null,
        ]);
    }

    /**
     * Check if the training is completed.
     *
     * @return bool
     */
    public function isCompleted(): bool
    {
        return $this->status === 'Completed';
    }

    /**
     * Check if the training is pending.
     *
     * @return bool
     */
    public function isPending(): bool
    {
        return $this->status === 'Pending';
    }

    /**
     * Check if the training is in progress.
     *
     * @return bool
     */
    public function isInProgress(): bool
    {
        return $this->status === 'In Progress';
    }

    /**
     * Get the progress percentage (you can customize this based on your needs).
     *
     * @return int
     */
    public function getProgressPercentageAttribute(): int
    {
        switch ($this->status) {
            case 'Pending':
                return 0;
            case 'In Progress':
                return 50; // You can make this more sophisticated
            case 'Completed':
                return 100;
            case 'Failed':
            case 'Cancelled':
                return 0;
            default:
                return 0;
        }
    }

    /**
     * Get the status color for UI display.
     *
     * @return string
     */
    public function getStatusColorAttribute(): string
    {
        switch ($this->status) {
            case 'Pending':
                return 'yellow';
            case 'In Progress':
                return 'blue';
            case 'Completed':
                return 'green';
            case 'Failed':
                return 'red';
            case 'Cancelled':
                return 'gray';
            default:
                return 'gray';
        }
    }

    /**
     * Get formatted completion date.
     *
     * @return string|null
     */
    public function getFormattedCompletedAtAttribute(): ?string
    {
        return $this->completed_at?->format('M d, Y');
    }

    /**
     * Boot method to add model event listeners.
     */
    protected static function boot()
    {
        parent::boot();

        // Automatically set completed_at when status changes to completed
        static::updating(function ($userTraining) {
            if ($userTraining->isDirty('status')) {
                if ($userTraining->status === 'Completed' && $userTraining->getOriginal('status') !== 'Completed') {
                    $userTraining->completed_at = now();
                } elseif ($userTraining->status !== 'Completed') {
                    $userTraining->completed_at = null;
                }
            }
        });
    }
}