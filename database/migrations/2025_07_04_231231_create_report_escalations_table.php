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
        // Update report_escalations table
        Schema::table('report_escalations', function (Blueprint $table) {
            $table->string('escalation_priority')->default('Medium')->after('escalation_reason');
            $table->boolean('immediate_action_required')->default(false)->after('escalation_priority');
            $table->string('estimated_resolution_time')->nullable()->after('immediate_action_required');
            $table->text('additional_notes')->nullable()->after('estimated_resolution_time');
            $table->timestamp('resolved_at')->nullable()->after('escalated_at');
            $table->foreignId('resolved_by_user_id')->nullable()->constrained('users')->nullOnDelete()->after('resolved_at');
            $table->text('resolution_notes')->nullable()->after('resolved_by_user_id');
            $table->string('resolved_by_action')->nullable()->after('resolution_notes');
        });

        // Create escalation_notifications table
        Schema::create('escalation_notifications', function (Blueprint $table) {
            $table->id();
            $table->foreignId('escalation_id')->constrained('report_escalations')->cascadeOnDelete();
            $table->foreignId('user_id')->constrained('users')->cascadeOnDelete();
            $table->string('notification_type')->default('email'); // email, sms, push
            $table->enum('status', ['pending', 'sent', 'failed', 'read'])->default('pending');
            $table->timestamp('sent_at')->nullable();
            $table->timestamp('read_at')->nullable();
            $table->json('metadata')->nullable(); // Store additional notification data
            $table->timestamps();

            $table->index(['escalation_id', 'user_id']);
            $table->index(['status', 'created_at']);
        });

        // Create escalation_assignments table (for assigning escalations to specific users/teams)
        Schema::create('escalation_assignments', function (Blueprint $table) {
            $table->id();
            $table->foreignId('escalation_id')->constrained('report_escalations')->cascadeOnDelete();
            $table->foreignId('assigned_to_user_id')->constrained('users')->cascadeOnDelete();
            $table->foreignId('assigned_by_user_id')->constrained('users')->cascadeOnDelete();
            $table->enum('status', ['assigned', 'in_progress', 'completed', 'reassigned'])->default('assigned');
            $table->text('assignment_notes')->nullable();
            $table->timestamp('assigned_at');
            $table->timestamp('started_at')->nullable();
            $table->timestamp('completed_at')->nullable();
            $table->timestamps();

            $table->index(['escalation_id', 'status']);
            $table->index(['assigned_to_user_id', 'status']);
        });

        // Create escalation_updates table (for tracking updates/comments on escalations)
        Schema::create('escalation_updates', function (Blueprint $table) {
            $table->id();
            $table->foreignId('escalation_id')->constrained('report_escalations')->cascadeOnDelete();
            $table->foreignId('user_id')->constrained('users')->cascadeOnDelete();
            $table->enum('update_type', ['comment', 'status_change', 'priority_change', 'assignment', 'resolution']);
            $table->text('update_content');
            $table->json('previous_values')->nullable(); // Store previous values for changes
            $table->json('new_values')->nullable(); // Store new values for changes
            $table->boolean('is_internal')->default(false); // Internal notes vs public updates
            $table->timestamps();

            $table->index(['escalation_id', 'created_at']);
            $table->index(['user_id', 'created_at']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('escalation_updates');
        Schema::dropIfExists('escalation_assignments');
        Schema::dropIfExists('escalation_notifications');
        
        Schema::table('report_escalations', function (Blueprint $table) {
            $table->dropColumn([
                'escalation_priority',
                'immediate_action_required',
                'estimated_resolution_time',
                'additional_notes',
                'resolved_at',
                'resolved_by_user_id',
                'resolution_notes',
                'resolved_by_action'
            ]);
        });
    }
};