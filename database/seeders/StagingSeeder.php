<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;
use App\Models\Organization;
use App\Models\User;
use App\Models\Training;
use App\Models\Report;

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

        // Create Reports with Media
        $report1 = Report::create([
            'organization_id' => $org1->id,
            'report_type' => 'Safety Inspection',
            'description' => 'Routine inspection conducted on excavation site.',
            'status' => 'Completed',
            'reported_by_user_id' => $user2->id,
            'date_of_incident' => now()
        ]);

        $report2 = Report::create([
            'organization_id' => $org2->id,
            'report_type' => 'Incident Report',
            'description' => 'Minor injury reported on scaffolding site.',
            'status' => 'Pending',
            'reported_by_user_id' => $user3->id,
            'date_of_incident' => now()
        ]);

        // Attach sample media to reports (using Spatie Media Library)
        // Attach random images to reports via report_uploads
        DB::table('report_uploads')->insert([
            [
                'report_id' => $report1->id,
                'file_url' => 'https://via.placeholder.com/600x400.png?text=Inspection+Photo+1',
                'file_type' => 'image/png',
                'uploaded_by' => $user2->email,
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'report_id' => $report1->id,
                'file_url' => 'https://via.placeholder.com/600x400.png?text=Inspection+Photo+2',
                'file_type' => 'image/png',
                'uploaded_by' => $user2->email,
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'report_id' => $report2->id,
                'file_url' => 'https://via.placeholder.com/600x400.png?text=Incident+Photo+1',
                'file_type' => 'image/png',
                'uploaded_by' => $user3->email,
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'report_id' => $report2->id,
                'file_url' => 'https://via.placeholder.com/600x400.png?text=Incident+Photo+2',
                'file_type' => 'image/png',
                'uploaded_by' => $user3->email,
                'created_at' => now(),
                'updated_at' => now(),
            ],
        ]);

        $data = [
            [
                'source' => 'Stabroek News',
                'category' => 'news',
                'title' => 'Man dies after SUV collides with truck on Mahaica new road',
                'content' => 'A man died following a collision last night on the Mahaica new road near Sugar Bar on the East Coast of Demerara. 2 h ago',
                'url' => 'https://www.stabroeknews.com/2025/07/06/news/guyana/man-dies-after-suv-collides-with-truck-on-mahaica-new-road/',
                'published_at' => '2025-07-06 08:47:07',
                'scraped_at' => '2025-07-06 08:47:13',
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'source' => 'Stabroek News',
                'category' => 'news',
                'title' => 'Separation of gas-to-energy contractors will have no impact on Exim Bank loan – Jagdeo',
                'content' => 'There will be no impact on the loan from the Export-Import Bank of the United States to the Government of Guyana following the separation of gas-to-energy joint venture contractors, Lindsayca and CH4, Vice President Bharrat Jagdeo has stated. 2 h ago',
                'url' => 'https://www.stabroeknews.com/2025/07/06/news/guyana/separation-of-gas-to-energy-contractors-will-have-no-impact-on-exim-bank-loan-jagdeo/',
                'published_at' => '2025-07-06 08:47:13',
                'scraped_at' => '2025-07-06 08:47:16',
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'source' => 'Stabroek News',
                'category' => 'news',
                'title' => 'Charity gets reconstructed police station, boat house',
                'content' => 'The residents of Charity and the wider Pomeroon River communities now have renewed hope in public safety and security, following the commissioning of the newly reconstructed Charity Police Station and a boat house yesterday.  2 h ago',
                'url' => 'https://www.stabroeknews.com/2025/07/06/news/guyana/charity-gets-reconstructed-police-station-boat-house/',
                'published_at' => '2025-07-06 08:47:16',
                'scraped_at' => '2025-07-06 08:47:19',
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'source' => 'Stabroek News',
                'category' => 'news',
                'title' => 'Rotaract Club of Georgetown turns 40',
                'content' => null,
                'url' => 'https://www.stabroeknews.com/2025/07/06/sunday/rotaract-club-of-georgetown-turns-40/',
                'published_at' => '2025-07-06 08:47:19',
                'scraped_at' => '2025-07-06 08:47:21',
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'source' => 'Stabroek News',
                'category' => 'news',
                'title' => 'Gaico building marina and conference centre on Demerara River',
                'content' => 'Gaico Construction Inc on Wednesday announced that it is building a marina and a conference centre on the Demerara River. July 4, 2025',
                'url' => 'https://www.stabroeknews.com/2025/07/04/business/gaico-building-marina-and-conference-centre-on-demerara-river/',
                'published_at' => '2025-07-04 04:00:00',
                'scraped_at' => '2025-07-06 08:47:23',
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'source' => 'Stabroek News',
                'category' => 'news',
                'title' => 'Death toll from Texas floods reaches at least 43; dozens still missing',
                'content' => '(Reuters) – At least 43 people, including 15 children, have been confirmed dead following flash floods in central Texas, authorities said yesterday as rescuers continued a frantic search for campers, vacationers and residents who were still missing. 2 h ago',
                'url' => 'https://www.stabroeknews.com/2025/07/06/news/world/death-toll-from-texas-floods-reaches-at-least-43-dozens-still-missing/',
                'published_at' => '2025-07-06 08:47:23',
                'scraped_at' => '2025-07-06 08:47:25',
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'source' => 'Nitter Search',
                'category' => 'social',
                'title' => '#HelipadCenter 🇬🇾
🇪🇸🔐 Charla de seguridad antes de iniciar labores
🦺 La vida y el bienestar del equipo, primero
#Conmarca #SeguridadEnObra #Guyana #SafetyFirst

🇬🇧🔐 Safety briefing before starting the day
🦺 Life and well-being always come first
 #JobsiteSafety #SafetyCulture',
                'content' => '#HelipadCenter 🇬🇾
🇪🇸🔐 Charla de seguridad antes de iniciar labores
🦺 La vida y el bienestar del equipo, primero
#Conmarca #SeguridadEnObra #Guyana #SafetyFirst

🇬🇧🔐 Safety briefing before starting the day
🦺 Life and well-being always come first
 #JobsiteSafety #SafetyCulture',
                'url' => 'https://nitter.net/ConmarcaING/status/1941191986473730187#m',
                'published_at' => '2001-07-04 04:00:00',
                'scraped_at' => '2025-07-06 08:47:38',
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'source' => 'Nitter Search',
                'category' => 'social',
                'title' => 'That\'s impressive! @DerekHayes112, sounds like Guyana\'s on the right track with these changes. Big wins for safety!',
                'content' => 'That\'s impressive! @DerekHayes112, sounds like Guyana\'s on the right track with these changes. Big wins for safety!',
                'url' => 'https://nitter.net/AranYildir14436/status/1940088988460884259#m',
                'published_at' => '2001-07-01 04:00:00',
                'scraped_at' => '2025-07-06 08:47:40',
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'source' => 'Nitter Search',
                'category' => 'social',
                'title' => 'French Guyana can give him a better launch pad, as they did to Russia at times.

Close to the Equator.

Patrolling sharks ensure the safety.',
                'content' => 'French Guyana can give him a better launch pad, as they did to Russia at times.

Close to the Equator.

Patrolling sharks ensure the safety.',
                'url' => 'https://nitter.net/BreizhLondon/status/1939961701534724248#m',
                'published_at' => '2001-07-01 04:00:00',
                'scraped_at' => '2025-07-06 08:47:42',
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'source' => 'Nitter Search',
                'category' => 'social',
                'title' => 'A new community-based business offering safety and emergency response training has launched in Guyana.

Read the details: newsroom.gy/2025/06/30/new-g…',
                'content' => 'A new community-based business offering safety and emergency response training has launched in Guyana.

Read the details: newsroom.gy/2025/06/30/new-g…',
                'url' => 'https://nitter.net/newsroomgy/status/1939842659427758572#m',
                'published_at' => '2001-07-01 04:00:00',
                'scraped_at' => '2025-07-06 08:47:43',
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'source' => 'Nitter Search',
                'category' => 'social',
                'title' => '**"Power Plays & Global Standoffs: Today\'s High-Stakes Battles"**  

✅ GOP bill may block state AI laws—sparking backlash over privacy & safety  
✅ Venezuela threatens Guyana\'s oil region, testing U.S. influence  
✅ Trump\'s rare earths deal with China, but trade tension',
                'content' => '**"Power Plays & Global Standoffs: Today\'s High-Stakes Battles"**  

✅ GOP bill may block state AI laws—sparking backlash over privacy & safety  
✅ Venezuela threatens Guyana\'s oil region, testing U.S. influence  
✅ Trump\'s rare earths deal with China, but trade tension',
                'url' => 'https://nitter.net/Deep_AI_Tracker/status/1938592803958956362#m',
                'published_at' => '2001-06-27 04:00:00',
                'scraped_at' => '2025-07-06 08:47:45',
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'source' => 'Nitter Search',
                'category' => 'social',
                'title' => '🚨 A survivor should never have to go viral to be protected. That is a systemic failure.

Survivors deserve safety the first time they speak — not after public outrage.

📢 Read our full statement:
lifeinleggings.org/2025/06/2…

#JusticeForJoanna #EndGBV #Guyana #LifeInLeggings',
                'content' => '🚨 A survivor should never have to go viral to be protected. That is a systemic failure.

Survivors deserve safety the first time they speak — not after public outrage.

📢 Read our full statement:
lifeinleggings.org/2025/06/2…

#JusticeForJoanna #EndGBV #Guyana #LifeInLeggings',
                'url' => 'https://nitter.net/TheOfficialLIL/status/1937201362153918586#m',
                'published_at' => '2001-06-23 04:00:00',
                'scraped_at' => '2025-07-06 08:47:47',
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'source' => 'Nitter Search',
                'category' => 'social',
                'title' => 'With over 2,000 new hotel rooms expected in Guyana by the end of 2025, the Caribbean Public Health Agency (CARPHA) recently delivered advanced food safety training to dozens of participants. Learn more: brnw.ch/21wTC07

#Hospitality #Foodservice #FoodSafetyTraining',
                'content' => 'With over 2,000 new hotel rooms expected in Guyana by the end of 2025, the Caribbean Public Health Agency (CARPHA) recently delivered advanced food safety training to dozens of participants. Learn more: brnw.ch/21wTC07

#Hospitality #Foodservice #FoodSafetyTraining',
                'url' => 'https://nitter.net/FoodSafetyMag/status/1937141140572057949#m',
                'published_at' => '2001-06-23 04:00:00',
                'scraped_at' => '2025-07-06 08:47:49',
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'source' => 'Nitter Search',
                'category' => 'social',
                'title' => 'Viewer discretion is advised. 

Always obey traffic signs — they are there to save lives, not slow you down. Your safety and that of others depends on it.

Video credit: Captured on CCTV || shared by Pixels Guyana Inc.',
                'content' => 'Viewer discretion is advised. 

Always obey traffic signs — they are there to save lives, not slow you down. Your safety and that of others depends on it.

Video credit: Captured on CCTV || shared by Pixels Guyana Inc.',
                'url' => 'https://nitter.net/AskRtsa/status/1937093538992304310#m',
                'published_at' => '2001-06-23 04:00:00',
                'scraped_at' => '2025-07-06 08:47:51',
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'source' => 'Nitter Search',
                'category' => 'social',
                'title' => 'Safety rankings (2025 Global Peace Index, lower is safer): Malaysia (13), Qatar (27), Kuwait (31), Bahrain (37), Brunei (40), Indonesia (43), Oman (52), Senegal (62), Albania (67), Guyana (72), Suriname (75), Benin (78), Lesotho (79), Kosovo (82), Morocco (85), Kazakhstan (92), Maldives (94), Jordan (98), Tunisia (101), Comoros (102), Uzbekistan (104), Saudi Arabia (105), Mauritania (109), Sierra Leone (110), Azerbaijan (113), Tajikistan (116), Kyrgyzstan (118), Bangladesh (121), Turkmenistan (123), Algeria (124), Uganda (127), Djibouti (132), Iran (135), Turkey (136), Mozambique (138), Lebanon (140), Cameroon (142), Niger (144), Guinea (146), Nigeria (149), Pakistan (151), Iraq (152), Chad (155), Mali (156), Palestine (157), Afghanistan (158), Yemen (159), Syria (160), Somalia (161). Women\'s rights (same as men, per 2025 Gender Gap Report, score ≥ 0.9): No for all listed countries. grok.com',
                'content' => 'Safety rankings (2025 Global Peace Index, lower is safer): Malaysia (13), Qatar (27), Kuwait (31), Bahrain (37), Brunei (40), Indonesia (43), Oman (52), Senegal (62), Albania (67), Guyana (72), Suriname (75), Benin (78), Lesotho (79), Kosovo (82), Morocco (85), Kazakhstan (92), Maldives (94), Jordan (98), Tunisia (101), Comoros (102), Uzbekistan (104), Saudi Arabia (105), Mauritania (109), Sierra Leone (110), Azerbaijan (113), Tajikistan (116), Kyrgyzstan (118), Bangladesh (121), Turkmenistan (123), Algeria (124), Uganda (127), Djibouti (132), Iran (135), Turkey (136), Mozambique (138), Lebanon (140), Cameroon (142), Niger (144), Guinea (146), Nigeria (149), Pakistan (151), Iraq (152), Chad (155), Mali (156), Palestine (157), Afghanistan (158), Yemen (159), Syria (160), Somalia (161). Women\'s rights (same as men, per 2025 Gender Gap Report, score ≥ 0.9): No for all listed countries. grok.com',
                'url' => 'https://nitter.net/grok/status/1936746203951292703#m',
                'published_at' => '2001-06-22 04:00:00',
                'scraped_at' => '2025-07-06 08:47:53',
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'source' => 'Nitter Search',
                'category' => 'social',
                'title' => 'Guyana Police and Prison officials begin training in non-lethal taser use, enhancing public safety and readiness for the upcoming elections with modern policing methods.   inewsguyana.com/cops-prison-…',
                'content' => 'Guyana Police and Prison officials begin training in non-lethal taser use, enhancing public safety and readiness for the upcoming elections with modern policing methods.   inewsguyana.com/cops-prison-…',
                'url' => 'https://nitter.net/crypt0Vanguard_/status/1936385700414595484#m',
                'published_at' => '2001-06-21 04:00:00',
                'scraped_at' => '2025-07-06 08:47:55',
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'source' => 'Nitter Search',
                'category' => 'social',
                'title' => 'With the re-emergence of COVID-19 in Guyana, the oil and gas sector must continue to maintain and strengthen robust health and safety systems, particularly to protect employees operating in offshore environments.
READ  MORE HERE: oilnow.gy/featured/letter-to… #Opinions #OilNOW #COVID',
                'content' => 'With the re-emergence of COVID-19 in Guyana, the oil and gas sector must continue to maintain and strengthen robust health and safety systems, particularly to protect employees operating in offshore environments.
READ  MORE HERE: oilnow.gy/featured/letter-to… #Opinions #OilNOW #COVID',
                'url' => 'https://nitter.net/oilnowgy/status/1936019339326419074#m',
                'published_at' => '2001-06-20 04:00:00',
                'scraped_at' => '2025-07-06 08:47:57',
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'source' => 'Nitter Search',
                'category' => 'social',
                'title' => 'With support from key partners — JN Foundation, National Road Safety Council, and FIA Foundation — The National Helmet Wearing Coalition\'s Heads Up! Regional Think Tank includes expert voices from Guyana, Belize, Mexico and more.

Happening today and tomorrow at the AC Hotel, Kingston.

@jnfoundation @nrscja @fia_fdn

#HeadsUpThinkTank #HelmetSafety #RoadSafetyMatters #RegionalCollaboration #DriveChange',
                'content' => 'With support from key partners — JN Foundation, National Road Safety Council, and FIA Foundation — The National Helmet Wearing Coalition\'s Heads Up! Regional Think Tank includes expert voices from Guyana, Belize, Mexico and more.

Happening today and tomorrow at the AC Hotel, Kingston.

@jnfoundation @nrscja @fia_fdn

#HeadsUpThinkTank #HelmetSafety #RoadSafetyMatters #RegionalCollaboration #DriveChange',
                'url' => 'https://nitter.net/JamaicaObserver/status/1935788359336460749#m',
                'published_at' => '2001-06-19 04:00:00',
                'scraped_at' => '2025-07-06 08:47:58',
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'source' => 'Nitter Search',
                'category' => 'social',
                'title' => 'President Ali has announced a new tech-powered initiative to combat violence against women—set to launch soon as part of his gov\'t\'s commitment to safety and empowerment. 

READ MORE  guyanachronicle.com/2025/06/…

#Guyana #WomenEmpowerment #GuyanaChronicle #Trending',
                'content' => 'President Ali has announced a new tech-powered initiative to combat violence against women—set to launch soon as part of his gov\'t\'s commitment to safety and empowerment. 

READ MORE  guyanachronicle.com/2025/06/…

#Guyana #WomenEmpowerment #GuyanaChronicle #Trending',
                'url' => 'https://nitter.net/GYChronicle/status/1932489858561253780#m',
                'published_at' => '2001-06-10 04:00:00',
                'scraped_at' => '2025-07-06 08:48:00',
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'source' => 'Nitter Search',
                'category' => 'social',
                'title' => 'OSRL is heading to SEOGS 2025 🌍 Don\'t miss OSRL\'s Tristan Barston on June 20, 15:30–17:00, discussing subsea well intervention in the Suriname/Guyana Basin.
Also, join our Pre-Summit Masterclass on inland spill response on June 16, 12:00–13:30.

👉 Find out more and register here: eu1.hubs.ly/H0kDFFR0

#osrl #oilspillresponse #SEOGS2025 #SurinameOilGas',
                'content' => 'OSRL is heading to SEOGS 2025 🌍 Don\'t miss OSRL\'s Tristan Barston on June 20, 15:30–17:00, discussing subsea well intervention in the Suriname/Guyana Basin.
Also, join our Pre-Summit Masterclass on inland spill response on June 16, 12:00–13:30.

👉 Find out more and register here: eu1.hubs.ly/H0kDFFR0

#osrl #oilspillresponse #SEOGS2025 #SurinameOilGas',
                'url' => 'https://nitter.net/oilspillexperts/status/1932347127490826692#m',
                'published_at' => '2001-06-10 04:00:00',
                'scraped_at' => '2025-07-06 08:48:02',
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'source' => 'Nitter Search',
                'category' => 'social',
                'title' => 'I\'m running the People\'s Temple Special on 158% pure organic coffee straight from the forests of Guyana! I vouch for its safety. @DanielLMcAdams  @ShannonJoyRadio',
                'content' => 'I\'m running the People\'s Temple Special on 158% pure organic coffee straight from the forests of Guyana! I vouch for its safety. @DanielLMcAdams  @ShannonJoyRadio',
                'url' => 'https://nitter.net/TheAlexJimJones/status/1932203947894206523#m',
                'published_at' => '2001-06-09 04:00:00',
                'scraped_at' => '2025-07-06 08:48:04',
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'source' => 'Nitter Search',
                'category' => 'social',
                'title' => 'I\'m selling 158% pure organic coffee straight from the forests of Guyana. I vouch for its safety.
@andy_buksterlin
@ShannonJoyRadio
@CarlBunce',
                'content' => 'I\'m selling 158% pure organic coffee straight from the forests of Guyana. I vouch for its safety.
@andy_buksterlin
@ShannonJoyRadio
@CarlBunce',
                'url' => 'https://nitter.net/TheAlexJimJones/status/1932183728719094091#m',
                'published_at' => '2001-06-09 04:00:00',
                'scraped_at' => '2025-07-06 08:48:06',
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'source' => 'Nitter Search',
                'category' => 'social',
                'title' => 'A sharp rise in the combined asset base of Stabroek Block co-venturers ExxonMobil, Hess and CNOOC has strengthened the consortium\'s ability to financially respond to a potential offshore oil spill.
READ MORE HERE: oilnow.gy/featured/exxon-led…
#johncolling #oilandgas #exxonmobil',
                'content' => 'A sharp rise in the combined asset base of Stabroek Block co-venturers ExxonMobil, Hess and CNOOC has strengthened the consortium\'s ability to financially respond to a potential offshore oil spill.
READ MORE HERE: oilnow.gy/featured/exxon-led…
#johncolling #oilandgas #exxonmobil',
                'url' => 'https://nitter.net/oilnowgy/status/1930582670414684323#m',
                'published_at' => '2001-06-05 04:00:00',
                'scraped_at' => '2025-07-06 08:48:07',
                'created_at' => now(),
                'updated_at' => now(),
            ],
            [
                'source' => 'Nitter Search',
                'category' => 'social',
                'title' => 'Guyana has taken another big step to protect the rights and safety of children by passing a new law that will help deal with complex family issues involving children across different countries.

newsroom.gy/2025/06/03/guyan…

#newsroomguyana #politicsgy #lawgy #childprotectiongy',
                'content' => 'Guyana has taken another big step to protect the rights and safety of children by passing a new law that will help deal with complex family issues involving children across different countries.

newsroom.gy/2025/06/03/guyan…

#newsroomguyana #politicsgy #lawgy #childprotectiongy',
                'url' => 'https://nitter.net/newsroomgy/status/1929910241174405162#m',
                'published_at' => '2001-06-03 04:00:00',
                'scraped_at' => '2025-07-06 08:48:09',
                'created_at' => now(),
                'updated_at' => now(),
            ],
        ];

        DB::table('ai_scrapers')->insert($data);
    }

}