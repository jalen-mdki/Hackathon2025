<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Models\User;
use App\Models\OrganizationUsers;
use Illuminate\Http\Request;
use Inertia\Inertia;

class UserController extends Controller
{
    public function index()
    {
        $users = OrganizationUsers::with(['user', 'organization'])->withCount(['organization'])->paginate(25);

        return Inertia::render('Admin/Users/Index', [
            'organization_users' => $users,
        ]);
    }

    public function create()
    {
        // Return Inertia form to create a new user
    }

    public function store(Request $request)
    {
        // Validate and store new user
    }

    public function edit(User $user)
    {
        $user->load('organization');

        return Inertia::render('Admin/Users/Edit', [
            'user' => $user,
        ]);
    }

    public function update(Request $request, User $user)
    {
        // Validate and update user
    }

    public function destroy(User $user)
    {
        $user->delete();

        return redirect()->route('admin.users.index')->with('success', 'User deleted successfully.');
    }
}
