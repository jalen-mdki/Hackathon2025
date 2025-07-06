<?php

namespace App\Http\Controllers\Admin;

use App\Models\AiScraper;
use Illuminate\Http\Request;
use Inertia\Inertia;
use App\Http\Controllers\Controller;

class AiScraperController extends Controller
{
    /**
     * Display the AI scrapers index view with initial data
     *
     * @return \Inertia\Response
     */
    public function index()
    {
        $scrapers = AiScraper::orderBy('published_at', 'desc')->get();
        
        return Inertia::render('Admin/AiScrapers/Index', [
            'scrapers' => $scrapers,
            'filters' => [
                'category' => request('category', ''),
                'source' => request('source', ''),
                'search' => request('search', ''),
            ]
        ]);
    }

    /**
     * Filter scraper data
     *
     * @param  \Illuminate\Http\Request  $request
     * @return \Inertia\Response
     */
    public function filter(Request $request)
    {
        $validated = $request->validate([
            'category' => 'sometimes|string|in:news,social',
            'source' => 'sometimes|string',
            'search' => 'sometimes|string'
        ]);

        $query = AiScraper::query();

        if ($request->has('category')) {
            $query->where('category', $validated['category']);
        }

        if ($request->has('source')) {
            $query->where('source', 'like', '%'.$validated['source'].'%');
        }

        if ($request->has('search')) {
            $query->where(function($q) use ($validated) {
                $q->where('title', 'like', '%'.$validated['search'].'%')
                  ->orWhere('content', 'like', '%'.$validated['search'].'%');
            });
        }

        $scrapers = $query->orderBy('published_at', 'desc')->get();

        return Inertia::render('AiScrapers/Index', [
            'scrapers' => $scrapers,
            'filters' => $validated
        ]);
    }
}