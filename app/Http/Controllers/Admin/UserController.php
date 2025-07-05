<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Models\User;
use App\Models\Organization;
use App\Models\OrganizationUsers;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\DB;
use Illuminate\Validation\Rule;
use Inertia\Inertia;

class UserController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        $OrganizationUsers = OrganizationUsers::with(['user', 'organization'])
            ->orderBy('created_at', 'desc')
            ->paginate(20);

        return Inertia::render('Admin/Users/Index', [
            'organization_users' => $OrganizationUsers
        ]);
    }

    /**
     * Show the form for creating a new resource.
     */
    public function create()
    {
        // Get all organizations for the dropdown
        $organizations = Organization::select('id', 'name', 'industry')
            ->orderBy('name')
            ->get();

        return Inertia::render('Admin/Users/Create', [
            'organizations' => $organizations
        ]);
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        // Validate the request
        $validated = $request->validate([
            'first_name' => ['required', 'string', 'max:255'],
            'last_name' => ['required', 'string', 'max:255'],
            'email' => ['required', 'string', 'email', 'max:255', 'unique:users'],
            'phone' => ['nullable', 'string', 'max:20'],
            'address' => ['nullable', 'string', 'max:500'],
            'password' => ['required', 'string', 'min:8', 'confirmed'],
            'is_admin' => ['boolean'],
            'organization_id' => [
                'nullable',
                'integer',
                'exists:organizations,id',
                // Organization is required unless user is admin
                Rule::requiredIf(function () use ($request) {
                    return !$request->boolean('is_admin');
                })
            ],
            'role' => [
                'required',
                'string',
                Rule::in(['employee', 'supervisor', 'manager', 'admin', 'contractor'])
            ]
        ]);

        try {
            DB::beginTransaction();

            // Create the user
            $user = User::create([
                'first_name' => $validated['first_name'],
                'last_name' => $validated['last_name'],
                'email' => $validated['email'],
                'phone' => $validated['phone'] ?? null,
                'address' => $validated['address'] ?? null,
                'password' => Hash::make($validated['password']),
                'email_verified_at' => now(), // Auto-verify for admin created users
            ]);

            // If user is not an admin, create organization relationship
            if (!$validated['is_admin']) {
                OrganizationUsers::create([
                    'user_id' => $user->id,
                    'organization_id' => $validated['organization_id'],
                    'role' => $validated['role'],
                    'is_active' => true,
                ]);
            } else {
                // For admin users, create a record without organization
                OrganizationUsers::create([
                    'user_id' => $user->id,
                    'organization_id' => null,
                    'role' => 'admin',
                    'is_active' => true,
                ]);
            }

            DB::commit();

            return redirect()
                ->route('admin.users.index')
                ->with('success', 'User created successfully!');

        } catch (\Exception $e) {
            DB::rollBack();
            
            // Log the actual error for debugging
            \Log::error('User creation failed: ' . $e->getMessage(), [
                'validated_data' => $validated,
                'stack_trace' => $e->getTraceAsString()
            ]);
            
            return back()
                ->withErrors(['error' => 'Failed to create user: ' . $e->getMessage()])
                ->withInput();
        }
    }

    /**
     * Display the specified resource.
     */
    public function show(User $user)
    {
        // $user->load(['OrganizationUsers']);
        
        return Inertia::render('Admin/Users/Show', [
            'user' => $user
        ]);
    }

    /**
     * Show the form for editing the specified resource.
     */
    public function edit(User $user)
    {
        $user->load(['OrganizationUsers.organization']);
        $organizations = Organization::select('id', 'name', 'industry')
            ->orderBy('name')
            ->get();

        return Inertia::render('Admin/Users/Edit', [
            'user' => $user,
            'organizations' => $organizations
        ]);
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, User $user)
    {
        // Validate the request
        $validated = $request->validate([
            'first_name' => ['required', 'string', 'max:255'],
            'last_name' => ['required', 'string', 'max:255'],
            'email' => [
                'required', 
                'string', 
                'email', 
                'max:255', 
                Rule::unique('users')->ignore($user->id)
            ],
            'phone' => ['nullable', 'string', 'max:20'],
            'address' => ['nullable', 'string', 'max:500'],
            'password' => ['nullable', 'string', 'min:8', 'confirmed'],
            'is_admin' => ['boolean'],
            'organization_id' => [
                'nullable',
                'integer',
                'exists:organizations,id',
                Rule::requiredIf(function () use ($request) {
                    return !$request->boolean('is_admin');
                })
            ],
            'role' => [
                'required',
                'string',
                Rule::in(['employee', 'supervisor', 'manager', 'admin', 'contractor'])
            ],
            'is_ministry' => ['boolean'],
            'is_active' => ['boolean']
        ]);

        try {
            DB::beginTransaction();

            // Update user basic information
            $updateData = [
                'first_name' => $validated['first_name'],
                'last_name' => $validated['last_name'],
                'email' => $validated['email'],
                'phone' => $validated['phone'] ?? null,
                'address' => $validated['address'] ?? null,
            ];

            // Only update password if provided
            if (!empty($validated['password'])) {
                $updateData['password'] = Hash::make($validated['password']);
            }

            $user->update($updateData);

            // Update or create organization relationship
            $orgUser = $user->OrganizationUserss()->first();

            if ($validated['is_admin']) {
                // For admin users
                if ($orgUser) {
                    $orgUser->update([
                        'organization_id' => null,
                        'role' => 'admin',
                        'is_active' => $validated['is_active'] ?? true,
                        'is_ministry' => false,
                    ]);
                } else {
                    OrganizationUsers::create([
                        'user_id' => $user->id,
                        'organization_id' => null,
                        'role' => 'admin',
                        'is_active' => $validated['is_active'] ?? true,
                        'is_ministry' => false,
                    ]);
                }
            } else {
                // For regular users
                if ($orgUser) {
                    $orgUser->update([
                        'organization_id' => $validated['organization_id'],
                        'role' => $validated['role'],
                        'is_active' => $validated['is_active'] ?? true,
                        'is_ministry' => $validated['is_ministry'] ?? false,
                    ]);
                } else {
                    OrganizationUsers::create([
                        'user_id' => $user->id,
                        'organization_id' => $validated['organization_id'],
                        'role' => $validated['role'],
                        'is_active' => $validated['is_active'] ?? true,
                        'is_ministry' => $validated['is_ministry'] ?? false,
                    ]);
                }
            }

            DB::commit();

            return redirect()
                ->route('admin.users.index')
                ->with('success', 'User updated successfully!');

        } catch (\Exception $e) {
            DB::rollBack();
            
            return back()
                ->withErrors(['error' => 'Failed to update user. Please try again.'])
                ->withInput();
        }
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(User $user)
    {
        try {
            DB::beginTransaction();

            // Soft delete or hard delete based on your needs
            // For this example, we'll use soft delete
            $user->OrganizationUserss()->delete();
            $user->delete();

            DB::commit();

            return redirect()
                ->route('admin.users.index')
                ->with('success', 'User deleted successfully!');

        } catch (\Exception $e) {
            DB::rollBack();
            
            return back()
                ->withErrors(['error' => 'Failed to delete user. Please try again.']);
        }
    }

    /**
     * Toggle user active status
     */
    public function toggleStatus(User $user)
    {
        try {
            $orgUser = $user->OrganizationUserss()->first();
            
            if ($orgUser) {
                $orgUser->update([
                    'is_active' => !$orgUser->is_active
                ]);

                $status = $orgUser->is_active ? 'activated' : 'deactivated';
                
                return back()->with('success', "User {$status} successfully!");
            }

            return back()->withErrors(['error' => 'User organization relationship not found.']);

        } catch (\Exception $e) {
            return back()->withErrors(['error' => 'Failed to update user status.']);
        }
    }

    /**
     * Bulk operations for users
     */
    public function bulkAction(Request $request)
    {
        $validated = $request->validate([
            'action' => ['required', 'string', Rule::in(['activate', 'deactivate', 'delete'])],
            'user_ids' => ['required', 'array'],
            'user_ids.*' => ['integer', 'exists:users,id']
        ]);

        try {
            DB::beginTransaction();

            $users = User::whereIn('id', $validated['user_ids'])->get();

            switch ($validated['action']) {
                case 'activate':
                    OrganizationUsers::whereIn('user_id', $validated['user_ids'])
                        ->update(['is_active' => true]);
                    $message = 'Users activated successfully!';
                    break;

                case 'deactivate':
                    OrganizationUsers::whereIn('user_id', $validated['user_ids'])
                        ->update(['is_active' => false]);
                    $message = 'Users deactivated successfully!';
                    break;

                case 'delete':
                    OrganizationUsers::whereIn('user_id', $validated['user_ids'])->delete();
                    User::whereIn('id', $validated['user_ids'])->delete();
                    $message = 'Users deleted successfully!';
                    break;
            }

            DB::commit();

            return back()->with('success', $message);

        } catch (\Exception $e) {
            DB::rollBack();
            
            return back()->withErrors(['error' => 'Failed to perform bulk action.']);
        }
    }

    /**
     * Search users with filters
     */
    public function search(Request $request)
    {
        $query = OrganizationUsers::with(['user', 'organization']);

        // Search by name or email
        if ($request->filled('search')) {
            $search = $request->input('search');
            $query->whereHas('user', function ($q) use ($search) {
                $q->where('first_name', 'like', "%{$search}%")
                  ->orWhere('last_name', 'like', "%{$search}%")
                  ->orWhere('email', 'like', "%{$search}%");
            });
        }

        // Filter by role
        if ($request->filled('role')) {
            $query->where('role', $request->input('role'));
        }

        // Filter by organization
        if ($request->filled('organization_id')) {
            $query->where('organization_id', $request->input('organization_id'));
        }

        // Filter by status
        if ($request->filled('status')) {
            $status = $request->input('status');
            if ($status === 'active') {
                $query->where('is_active', true)->whereNull('disabled_at');
            } elseif ($status === 'inactive') {
                $query->where('is_active', false);
            } elseif ($status === 'disabled') {
                $query->whereNotNull('disabled_at');
            }
        }

        // Filter by ministry status
        if ($request->filled('is_ministry')) {
            $query->where('is_ministry', $request->boolean('is_ministry'));
        }

        $OrganizationUserss = $query->orderBy('created_at', 'desc')->paginate(20);

        return Inertia::render('Admin/Users/Index', [
            'organization_users' => $OrganizationUserss,
            'filters' => $request->only(['search', 'role', 'organization_id', 'status', 'is_ministry'])
        ]);
    }
}