<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Organization extends Model
{
    /** @use HasFactory<\Database\Factories\OrganizationFactory> */
    use HasFactory;

    public function reports()
    {
        return $this->hasMany(Report::class);
    }

    public function employees()
    {
        return $this->belongsToMany(User::class, 'organization_users');
    }

    public function hazards()
    {
        return $this->hasMany(Hazards::class);
    }

    public function emergencyResponsePlans()
    {
        return $this->hasMany(EmergencyResponsePlans::class);
    }

    public function userTrainings()
    {
        return $this->hasMany(UserTraining::class);
    }

}
