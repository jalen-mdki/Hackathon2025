<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('reports', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->string('report_type');
            $table->string('incident_type')->nullable();
            $table->text('description');
            $table->date('date_of_incident');
            $table->decimal('location_lat', 10, 7);
            $table->decimal('location_long', 10, 7);
            $table->string('severity');
            $table->string('industry');
            $table->string('reporter_name')->nullable();
            $table->string('reporter_contact')->nullable();
            $table->string('status')->default('Pending');
            $table->foreignId('assigned_to')->nullable()->constrained('users')->nullOnDelete();
            $table->foreignId('organization_id')->nullable()->constrained('organizations')->nullOnDelete();
            $table->foreignId('reported_by_user_id')->nullable()->constrained('users')->nullOnDelete();
            $table->boolean('is_escalated')->default(false);
            $table->string('escalation_status')->default('Not Required');
            $table->string('cause_of_death')->nullable();
            $table->string('regulation_class_broken')->nullable();
            $table->boolean('feedback_given')->default(false);
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('reports');
    }
};
