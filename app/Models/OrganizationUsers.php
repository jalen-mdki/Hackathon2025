<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class OrganizationUsers extends Model
{
    /** @use HasFactory<\Database\Factories\OrganizationUsersFactory> */
    use HasFactory;

    protected $fillable = [
        'user_id',
        'organization_id',
        'role',
        'is_active'
    ];


    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public function organization()
    {
        return $this->belongsTo(Organization::class);
    }
}
