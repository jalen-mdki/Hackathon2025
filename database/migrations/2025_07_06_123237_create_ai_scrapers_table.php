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
        Schema::create('ai_scrapers', function (Blueprint $table) {
            $table->id();
            $table->text('source');
            $table->text('category');
            $table->text('title');
            $table->text('content')->nullable();
            $table->text('url');
            $table->timestamp('published_at');
            $table->timestamp('scraped_at');
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('ai_scrapers');
    }
};
