<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;
use App\Models\Organization;
use App\Models\User;
use App\Models\Training;

class StagingSeeder extends Seeder
{
    public function run(): void
    {
        // Create Admin
        $admin = User::create([
            'first_name' => 'Fiducia',
            'last_name' => 'Inc',
            'email' => 'admin@fiducia.gy',
            'password' => bcrypt('password'),
            'is_admin' => true
        ]);


        // Create Organizations
        $org1 = Organization::create([
            'name' => 'Guyana Mining Ltd',
            'industry' => 'Mining',
            'contact_person' => 'John Doe',
            'contact_email' => 'john@gml.com',
        ]);

        $org2 = Organization::create([
            'name' => 'Safe Builders Inc',
            'industry' => 'Construction',
            'contact_person' => 'Jane Smith',
            'contact_email' => 'jane@safebuilders.com',
        ]);

        // Create Users with first_name and last_name fields
        $user1 = User::create([
            'first_name' => 'Supervisor',
            'last_name' => 'Alpha',
            'email' => 'alpha@gml.com',
            'password' => bcrypt('password'),
        ]);
        DB::table('organization_users')->insert([
            'user_id' => $user1->id,
            'organization_id' => $org1->id,
            'role' => 'org_supervisor',
            'is_active' => true,
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        $user2 = User::create([
            'first_name' => 'Worker',
            'last_name' => 'Beta',
            'email' => 'beta@gml.com',
            'password' => bcrypt('password'),
        ]);
        DB::table('organization_users')->insert([
            'user_id' => $user2->id,
            'organization_id' => $org1->id,
            'role' => 'org_employee',
            'is_active' => true,
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        $user3 = User::create([
            'first_name' => 'Supervisor',
            'last_name' => 'Gamma',
            'email' => 'gamma@safebuilders.com',
            'password' => bcrypt('password'),
        ]);
        DB::table('organization_users')->insert([
            'user_id' => $user3->id,
            'organization_id' => $org2->id,
            'role' => 'org_supervisor',
            'is_active' => true,
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        // Create Trainings
        $training1 = Training::create([
            'name' => 'Fire Safety Training',
            'description' => 'Learn fire prevention and emergency procedures.',
            'industry' => 'All',
        ]);

        $training2 = Training::create([
            'name' => 'PPE Usage Training',
            'description' => 'Proper use of personal protective equipment.',
            'industry' => 'Construction',
        ]);

        // Assign Trainings to Users
        DB::table('user_trainings')->insert([
            [
                'user_id' => $user1->id,
                'organization_id' => $org1->id,
                'training_id' => $training1->id,
                'status' => 'Completed',
                'completed_at' => now(),
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'user_id' => $user2->id,
                'organization_id' => $org1->id,
                'training_id' => $training2->id,
                'status' => 'In Progress',
                'completed_at' => null,
                'created_at' => now(),
                'updated_at' => now(),
            ],
        ]);

        // Create Emergency Response Plans
        DB::table('emergency_response_plans')->insert([
            [
                'organization_id' => $org1->id,
                'plan_name' => 'Mining Fire Response Plan',
                'document_url' => 'https://example.com/fire_plan.pdf',
                'last_reviewed_at' => now()->subMonths(2),
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'organization_id' => $org2->id,
                'plan_name' => 'Construction Evacuation Plan',
                'document_url' => 'https://example.com/evac_plan.pdf',
                'last_reviewed_at' => now()->subMonths(1),
                'created_at' => now(),
                'updated_at' => now(),
            ],
        ]);

        // Create Hazards
        DB::table('hazards')->insert([
            [
                'organization_id' => $org1->id,
                'description' => 'Unsecured electrical wiring near excavation site.',
                'risk_level' => 'High',
                'mitigation_plan' => 'Install proper casing and signage.',
                'status' => 'Open',
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'organization_id' => $org2->id,
                'description' => 'Wet surfaces causing slip hazards.',
                'risk_level' => 'Medium',
                'mitigation_plan' => 'Regular cleaning and slip-resistant mats.',
                'status' => 'In Progress',
                'created_at' => now(),
                'updated_at' => now(),
            ],
        ]);
    }
}