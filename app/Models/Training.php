<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;

class Training extends Model
{
    /** @use HasFactory<\Database\Factories\TrainingFactory> */
    use HasFactory;

    /**
     * The attributes that are mass assignable.
     *
     * @var array<int, string>
     */
    protected $fillable = [
        'name',
        'description',
        'industry',
    ];

    /**
     * The attributes that should be cast.
     *
     * @var array<string, string>
     */
    protected $casts = [
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    /**
     * Get all user training enrollments for this training.
     * This is the relationship the controller is looking for.
     *
     * @return HasMany
     */
    public function userTrainings(): HasMany
    {
        return $this->hasMany(UserTraining::class);
    }

    /**
     * Get all users enrolled in this training.
     * This provides a direct relationship to users through the pivot table.
     *
     * @return BelongsToMany
     */
    public function users(): BelongsToMany
    {
        return $this->belongsToMany(User::class, 'user_trainings')
                    ->withPivot(['status', 'completed_at', 'organization_id'])
                    ->withTimestamps();
    }

    /**
     * Get all organizations that have users enrolled in this training.
     *
     * @return BelongsToMany
     */
    public function organizations(): BelongsToMany
    {
        return $this->belongsToMany(Organization::class, 'user_trainings')
                    ->withPivot(['user_id', 'status', 'completed_at'])
                    ->withTimestamps()
                    ->distinct();
    }

    /**
     * Get completed enrollments for this training.
     *
     * @return HasMany
     */
    public function completedEnrollments(): HasMany
    {
        return $this->userTrainings()->where('status', 'Completed');
    }

    /**
     * Get pending enrollments for this training.
     *
     * @return HasMany
     */
    public function pendingEnrollments(): HasMany
    {
        return $this->userTrainings()->where('status', 'Pending');
    }

    /**
     * Get in-progress enrollments for this training.
     *
     * @return HasMany
     */
    public function inProgressEnrollments(): HasMany
    {
        return $this->userTrainings()->where('status', 'In Progress');
    }

    /**
     * Scope to filter trainings by industry.
     *
     * @param \Illuminate\Database\Eloquent\Builder $query
     * @param string $industry
     * @return \Illuminate\Database\Eloquent\Builder
     */
    public function scopeByIndustry($query, $industry)
    {
        return $query->where('industry', $industry);
    }

    /**
     * Scope to search trainings by name or description.
     *
     * @param \Illuminate\Database\Eloquent\Builder $query
     * @param string $search
     * @return \Illuminate\Database\Eloquent\Builder
     */
    public function scopeSearch($query, $search)
    {
        return $query->where(function ($q) use ($search) {
            $q->where('name', 'LIKE', "%{$search}%")
              ->orWhere('description', 'LIKE', "%{$search}%")
              ->orWhere('industry', 'LIKE', "%{$search}%");
        });
    }

    /**
     * Get the total number of enrolled users.
     *
     * @return int
     */
    public function getEnrolledCountAttribute(): int
    {
        return $this->userTrainings()->count();
    }

    /**
     * Get the completion rate for this training.
     *
     * @return float
     */
    public function getCompletionRateAttribute(): float
    {
        $total = $this->userTrainings()->count();
        
        if ($total === 0) {
            return 0;
        }

        $completed = $this->completedEnrollments()->count();
        
        return round(($completed / $total) * 100, 2);
    }

    /**
     * Check if a user is enrolled in this training.
     *
     * @param User $user
     * @return bool
     */
    public function hasUserEnrolled(User $user): bool
    {
        return $this->users()->where('user_id', $user->id)->exists();
    }

    /**
     * Enroll a user in this training.
     *
     * @param User $user
     * @param Organization $organization
     * @param string $status
     * @return UserTraining
     */
    public function enrollUser(User $user, Organization $organization, string $status = 'Pending'): UserTraining
    {
        return $this->userTrainings()->create([
            'user_id' => $user->id,
            'organization_id' => $organization->id,
            'status' => $status,
        ]);
    }

    /**
     * Unenroll a user from this training.
     *
     * @param User $user
     * @return bool
     */
    public function unenrollUser(User $user): bool
    {
        return $this->userTrainings()
                    ->where('user_id', $user->id)
                    ->delete() > 0;
    }

    /**
     * Get enrollment statistics for this training.
     *
     * @return array
     */
    public function getEnrollmentStats(): array
    {
        return [
            'total' => $this->userTrainings()->count(),
            'completed' => $this->completedEnrollments()->count(),
            'pending' => $this->pendingEnrollments()->count(),
            'in_progress' => $this->inProgressEnrollments()->count(),
            'completion_rate' => $this->completion_rate,
        ];
    }

    /**
     * Get organizations with enrollment counts for this training.
     *
     * @return \Illuminate\Support\Collection
     */
    public function getOrganizationStats()
    {
        return $this->userTrainings()
                    ->with('organization')
                    ->selectRaw('organization_id, COUNT(*) as enrollment_count')
                    ->groupBy('organization_id')
                    ->get()
                    ->map(function ($item) {
                        return [
                            'organization_id' => $item->organization_id,
                            'organization_name' => $item->organization->name ?? 'Unknown',
                            'enrollment_count' => $item->enrollment_count,
                        ];
                    });
    }
}