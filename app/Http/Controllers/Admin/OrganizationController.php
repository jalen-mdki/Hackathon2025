<?php

namespace App\Http\Controllers\Admin;

use App\Models\Organization;
use Illuminate\Http\Request;
use App\Http\Controllers\Controller;

class OrganizationController extends Controller
{
    // Display list of organizations for admin
    public function index()
    {
        $organizations = Organization::paginate(15);
        return inertia('Admin/Organizations/Index', [
            'organizations' => $organizations
        ]);
    }

    // Show create form
    public function create()
    {
        return inertia('Admin/Organizations/Create');
    }

    // Store new organization
    public function store(Request $request)
    {
        $validated = $request->validate([
            'name' => 'required|string|max:255',
            'industry' => 'required|string|max:255',
            'contact_person' => 'required|string|max:255',
            'contact_email' => 'required|email|max:255',
        ]);

        Organization::create($validated);

        return redirect()->route('admin.organizations.index')->with('success', 'Organization created successfully.');
    }

    public function show(Organization $organization)
    {
        $organization->load([
            'reports.reportUploads', // include report uploads for images
            'employees',
            'hazards',
            'emergencyResponsePlans',
            'userTrainings',
        ]);

        return inertia('Admin/Organizations/Show', [
            'organization' => $organization,
            'reports' => $organization->reports->map(function ($report) {
                return [
                    'id' => $report->id,
                    'report_type' => $report->report_type,
                    'description' => $report->description,
                    'status' => $report->status,
                    'date_of_incident' => $report->date_of_incident,
                    'report_uploads' => $report->reportUploads->map(function ($upload) {
                        return [
                            'id' => $upload->id,
                            'file_url' => $upload->file_url,
                            'file_type' => $upload->file_type,
                        ];
                    }),
                ];
            }),
            'employees' => $organization->employees,
            'hazards' => $organization->hazards,
            'emergencyResponsePlans' => $organization->emergencyResponsePlans,
            'userTrainings' => $organization->userTrainings,
        ]);
    }



    // Show edit form
    public function edit(Organization $organization)
    {
        return inertia('Admin/Organizations/Edit', [
            'organization' => $organization
        ]);
    }

    // Update organization
    public function update(Request $request, Organization $organization)
    {
        $validated = $request->validate([
            'name' => 'required|string|max:255',
            'industry' => 'required|string|max:255',
            'contact_person' => 'required|string|max:255',
            'contact_email' => 'required|email|max:255',
        ]);

        $organization->update($validated);

        return redirect()->route('admin.organizations.index')->with('success', 'Organization updated successfully.');
    }
}