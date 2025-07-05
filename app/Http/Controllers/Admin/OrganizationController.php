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