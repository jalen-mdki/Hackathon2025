<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Support\Facades\Storage;

class ReportUploads extends Model
{
    use HasFactory;

    protected $fillable = [
        'report_id',
        'file_url',
        'file_type',
        'uploaded_by',
        'original_filename',
        's3_path',
    ];

    /**
     * Get the report that owns the upload
     */
    public function report(): BelongsTo
    {
        return $this->belongsTo(Report::class);
    }

    /**
     * Get the file size from S3 if file exists
     */
    public function getFileSizeAttribute()
    {
        try {
            if ($this->s3_path && Storage::disk('s3')->exists($this->s3_path)) {
                return Storage::disk('s3')->size($this->s3_path);
            }
        } catch (\Exception $e) {
            \Log::warning('Could not get file size from S3', [
                's3_path' => $this->s3_path,
                'error' => $e->getMessage()
            ]);
        }
        
        return 0;
    }

    /**
     * Get human readable file size
     */
    public function getFormattedFileSizeAttribute()
    {
        $bytes = $this->file_size;
        
        if ($bytes === 0) return '0 Bytes';
        
        $k = 1024;
        $sizes = ['Bytes', 'KB', 'MB', 'GB'];
        $i = floor(log($bytes) / log($k));
        
        return round($bytes / pow($k, $i), 2) . ' ' . $sizes[$i];
    }

    /**
     * Check if file is an image
     */
    public function getIsImageAttribute()
    {
        return str_starts_with($this->file_type, 'image/');
    }

    /**
     * Get file extension
     */
    public function getFileExtensionAttribute()
    {
        return pathinfo($this->original_filename ?? $this->file_url, PATHINFO_EXTENSION);
    }

    /**
     * Generate a signed URL for temporary access (useful for private S3 buckets)
     */
    public function getSignedUrlAttribute()
    {
        try {
            if ($this->s3_path) {
                // Generate a signed URL that expires in 1 hour
                return Storage::disk('s3')->temporaryUrl($this->s3_path, now()->addHour());
            }
        } catch (\Exception $e) {
            \Log::warning('Could not generate signed URL for S3 file', [
                's3_path' => $this->s3_path,
                'error' => $e->getMessage()
            ]);
        }
        
        return $this->file_url;
    }

    /**
     * Check if file exists in S3
     */
    public function existsInS3()
    {
        try {
            return $this->s3_path && Storage::disk('s3')->exists($this->s3_path);
        } catch (\Exception $e) {
            return false;
        }
    }

    /**
     * Get the download URL (uses signed URL for private buckets, direct URL for public)
     */
    public function getDownloadUrlAttribute()
    {
        // If using private S3 bucket, use signed URL
        if (config('filesystems.disks.s3.visibility') === 'private') {
            return $this->signed_url;
        }
        
        // If using public S3 bucket, use direct URL
        return $this->file_url;
    }
}