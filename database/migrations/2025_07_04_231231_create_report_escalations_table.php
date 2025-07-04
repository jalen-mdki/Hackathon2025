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
        Schema::create('report_escalations', function (Blueprint $table) {
            $table->id();
            $table->foreignUuid('report_id')->constrained('reports')->cascadeOnDelete();
            $table->foreignId('escalated_by_user_id')->constrained('users')->cascadeOnDelete();
            $table->text('escalation_reason');
            $table->timestamp('escalated_at');
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('report_escalations');
    }
};
