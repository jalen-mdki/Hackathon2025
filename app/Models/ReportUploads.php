<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class ReportUploads extends Model
{
    /** @use HasFactory<\Database\Factories\ReportUploadsFactory> */
    use HasFactory;

    protected $fillable = [
        'report_id',
        'file_url',
        'file_type',
        'uploaded_by',
    ];

    public function report()
    {
        return $this->belongsTo(Report::class);
    }
}
