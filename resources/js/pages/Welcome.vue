<script setup lang="ts">
import { Head, Link } from '@inertiajs/vue3';
</script>

<template>
    <Head title="Guyana HSSE Portal">
        <link rel="preconnect" href="https://rsms.me/" />
        <link rel="stylesheet" href="https://rsms.me/inter/inter.css" />
    </Head>
    <div class="min-h-screen bg-gray-900 text-gray-100">
        <!-- Navigation -->
        <header class="py-6 px-8 w-full bg-gray-900/80 backdrop-blur-sm border-b border-gray-800 fixed z-50">
            <nav class="flex items-center justify-between max-w-7xl mx-auto">
                <div class="flex items-center space-x-2">
                    <svg class="w-8 h-8" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2L3 7L12 12L21 7L12 2Z" fill="#10B981" stroke="#10B981" stroke-width="2" stroke-linejoin="round"/>
                        <path d="M3 12L12 17L21 12" stroke="#10B981" stroke-width="2" stroke-linejoin="round"/>
                        <path d="M3 17L12 22L21 17" stroke="#10B981" stroke-width="2" stroke-linejoin="round"/>
                    </svg>
                    <span class="text-xl font-bold bg-gradient-to-r from-green-400 to-green-600 bg-clip-text text-transparent">Guyana HSSE</span>
                </div>
                <div class="flex items-center gap-6">
                    <Link :href="route('login')" class="font-medium hover:text-green-400 transition-colors">
                        Login
                    </Link>
                    <Link 
                        :href="route('register')" 
                        class="bg-green-600 hover:bg-green-700 text-white font-medium px-6 py-2 rounded-lg transition-colors"
                    >
                        Register
                    </Link>
                </div>
            </nav>
        </header>

        <!-- Hero Section -->
        <section class="pt-32 pb-16 px-8 max-w-7xl mx-auto">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                <div>
                    <h1 class="text-4xl md:text-5xl font-bold leading-tight mb-6">
                        <span class="bg-gradient-to-r from-green-400 to-green-600 bg-clip-text text-transparent">HSSE Excellence</span> for Guyana's Industries
                    </h1>
                    <p class="text-lg text-gray-400 mb-8">
                        A modern platform for comprehensive Health, Safety, Security, and Environment management tailored to Guyana's unique industrial landscape.
                    </p>
                    <div class="flex flex-wrap gap-4">
                        <Link 
                            :href="route('register')" 
                            class="bg-green-600 hover:bg-green-700 text-white font-bold px-8 py-3 rounded-lg transition-colors"
                        >
                            Get Started
                        </Link>
                        <Link 
                            href="#features" 
                            class="border-2 border-gray-700 hover:bg-gray-800/50 font-bold px-8 py-3 rounded-lg transition-colors"
                        >
                            Learn More
                        </Link>
                    </div>
                </div>
                <div class="relative">
                    <img src="https://images.unsplash.com/photo-1567954970774-58d6aa6c50dc?q=80&w=1332&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D" 
                         alt="Industrial safety in Guyana" 
                         class="rounded-xl shadow-2xl border-4 border-gray-800/50">
                    <div class="absolute -bottom-6 -right-6 bg-gray-800 text-green-400 p-4 rounded-lg shadow-lg border border-gray-700">
                        <div class="text-2xl font-bold">100%</div>
                        <div class="text-sm">Compliance Rate</div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Stats Section -->
        <section class="py-16 bg-gray-800/50 backdrop-blur-sm">
            <div class="max-w-7xl mx-auto px-8">
                <div class="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
                    <div class="p-6 bg-gray-800/50 rounded-lg border border-gray-700">
                        <div class="text-4xl font-bold text-green-400 mb-2">250+</div>
                        <div class="text-gray-400">Registered Companies</div>
                    </div>
                    <div class="p-6 bg-gray-800/50 rounded-lg border border-gray-700">
                        <div class="text-4xl font-bold text-green-400 mb-2">1.2K</div>
                        <div class="text-gray-400">Safety Reports</div>
                    </div>
                    <div class="p-6 bg-gray-800/50 rounded-lg border border-gray-700">
                        <div class="text-4xl font-bold text-green-400 mb-2">98%</div>
                        <div class="text-gray-400">Incident Resolution</div>
                    </div>
                    <div class="p-6 bg-gray-800/50 rounded-lg border border-gray-700">
                        <div class="text-4xl font-bold text-green-400 mb-2">24/7</div>
                        <div class="text-gray-400">Monitoring</div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Features Section -->
        <section id="features" class="py-16 px-8 max-w-7xl mx-auto">
            <div class="text-center mb-16">
                <h2 class="text-3xl font-bold mb-4">Comprehensive HSSE Solutions</h2>
                <p class="text-lg text-gray-400 max-w-3xl mx-auto">
                    Designed specifically for Guyana's industrial sectors with cutting-edge technology
                </p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                <div class="bg-gray-800/50 p-8 rounded-xl hover:bg-gray-800 transition-all border border-gray-700">
                    <div class="w-14 h-14 bg-green-500/20 rounded-lg flex items-center justify-center mb-6">
                        <svg class="w-8 h-8 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
                        </svg>
                    </div>
                    <h3 class="text-xl font-bold mb-3">Workplace Safety</h3>
                    <p class="text-gray-400">
                        Advanced hazard identification, risk assessment, and incident reporting tools to ensure worker safety.
                    </p>
                </div>

                <div class="bg-gray-800/50 p-8 rounded-xl hover:bg-gray-800 transition-all border border-gray-700">
                    <div class="w-14 h-14 bg-green-500/20 rounded-lg flex items-center justify-center mb-6">
                        <svg class="w-8 h-8 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                        </svg>
                    </div>
                    <h3 class="text-xl font-bold mb-3">Environmental Protection</h3>
                    <p class="text-gray-400">
                        Comprehensive tools for emissions tracking, waste management, and environmental compliance.
                    </p>
                </div>

                <div class="bg-gray-800/50 p-8 rounded-xl hover:bg-gray-800 transition-all border border-gray-700">
                    <div class="w-14 h-14 bg-green-500/20 rounded-lg flex items-center justify-center mb-6">
                        <svg class="w-8 h-8 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
                        </svg>
                    </div>
                    <h3 class="text-xl font-bold mb-3">Security Management</h3>
                    <p class="text-gray-400">
                        Integrated security protocols and threat assessment tools for industrial facilities.
                    </p>
                </div>

                <div class="bg-gray-800/50 p-8 rounded-xl hover:bg-gray-800 transition-all border border-gray-700">
                    <div class="w-14 h-14 bg-green-500/20 rounded-lg flex items-center justify-center mb-6">
                        <svg class="w-8 h-8 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                        </svg>
                    </div>
                    <h3 class="text-xl font-bold mb-3">Compliance Tracking</h3>
                    <p class="text-gray-400">
                        Automated compliance monitoring with Guyana's HSSE regulations and international standards.
                    </p>
                </div>

                <div class="bg-gray-800/50 p-8 rounded-xl hover:bg-gray-800 transition-all border border-gray-700">
                    <div class="w-14 h-14 bg-green-500/20 rounded-lg flex items-center justify-center mb-6">
                        <svg class="w-8 h-8 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                        </svg>
                    </div>
                    <h3 class="text-xl font-bold mb-3">Real-time Analytics</h3>
                    <p class="text-gray-400">
                        Dashboard with live data visualization for proactive HSSE management and decision making.
                    </p>
                </div>

                <div class="bg-gray-800/50 p-8 rounded-xl hover:bg-gray-800 transition-all border border-gray-700">
                    <div class="w-14 h-14 bg-green-500/20 rounded-lg flex items-center justify-center mb-6">
                        <svg class="w-8 h-8 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z"></path>
                        </svg>
                    </div>
                    <h3 class="text-xl font-bold mb-3">Training & Certification</h3>
                    <p class="text-gray-400">
                        Online courses and certification programs for HSSE professionals in Guyana.
                    </p>
                </div>
            </div>
        </section>

        <!-- Testimonials -->
        <section class="py-16 bg-gray-800/50 backdrop-blur-sm">
            <div class="max-w-7xl mx-auto px-8">
                <div class="text-center mb-12">
                    <h2 class="text-3xl font-bold mb-4">Trusted by Guyana's Leading Industries</h2>
                    <p class="text-lg text-gray-400 max-w-3xl mx-auto">
                        What our partners say about our HSSE solutions
                    </p>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                    <div class="bg-gray-800/50 p-8 rounded-xl border border-gray-700 hover:bg-gray-800 transition-all">
                        <div class="flex items-center mb-4">
                            <div class="w-12 h-12 rounded-full bg-green-500/20 flex items-center justify-center mr-4">
                                <span class="text-xl font-bold text-green-400">JD</span>
                            </div>
                            <div>
                                <h4 class="font-bold">John Doe</h4>
                                <p class="text-sm text-gray-400">Safety Manager, Oil Company</p>
                            </div>
                        </div>
                        <p class="text-gray-300 italic">
                            "This platform has transformed how we manage safety compliance across our operations in Guyana. The real-time reporting has helped us reduce incidents by 40%."
                        </p>
                    </div>

                    <div class="bg-gray-800/50 p-8 rounded-xl border border-gray-700 hover:bg-gray-800 transition-all">
                        <div class="flex items-center mb-4">
                            <div class="w-12 h-12 rounded-full bg-green-500/20 flex items-center justify-center mr-4">
                                <span class="text-xl font-bold text-green-400">MS</span>
                            </div>
                            <div>
                                <h4 class="font-bold">Maria Smith</h4>
                                <p class="text-sm text-gray-400">Environmental Officer, Mining Corp</p>
                            </div>
                        </div>
                        <p class="text-gray-300 italic">
                            "The environmental monitoring tools have been invaluable for ensuring we meet Guyana's strict regulations while maintaining operational efficiency."
                        </p>
                    </div>

                    <div class="bg-gray-800/50 p-8 rounded-xl border border-gray-700 hover:bg-gray-800 transition-all">
                        <div class="flex items-center mb-4">
                            <div class="w-12 h-12 rounded-full bg-green-500/20 flex items-center justify-center mr-4">
                                <span class="text-xl font-bold text-green-400">RG</span>
                            </div>
                            <div>
                                <h4 class="font-bold">Robert Greene</h4>
                                <p class="text-sm text-gray-400">Security Director, Energy Sector</p>
                            </div>
                        </div>
                        <p class="text-gray-300 italic">
                            "Integrated security features have streamlined our threat assessment processes and improved response times across all our Guyanese facilities."
                        </p>
                    </div>
                </div>
            </div>
        </section>

        <!-- CTA Section -->
        <section class="py-16 px-8">
            <div class="max-w-4xl mx-auto bg-gradient-to-r from-green-600 to-green-800 rounded-xl p-8 text-center">
                <h2 class="text-3xl font-bold text-white mb-4">Ready to Enhance Your HSSE Compliance?</h2>
                <p class="text-green-100 mb-8 text-lg">
                    Join Guyana's leading organizations in creating safer, more sustainable workplaces.
                </p>
                <Link 
                    :href="route('register')" 
                    class="bg-white hover:bg-gray-100 text-green-800 font-bold px-8 py-3 rounded-lg transition-colors inline-block"
                >
                    Get Started Today
                </Link>
            </div>
        </section>

        <!-- Footer -->
        <footer class="py-12 px-8 border-t border-gray-800">
            <div class="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8">
                <div>
                    <div class="flex items-center space-x-2 mb-4">
                        <svg class="w-8 h-8" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M12 2L3 7L12 12L21 7L12 2Z" fill="#10B981" stroke="#10B981" stroke-width="2" stroke-linejoin="round"/>
                            <path d="M3 12L12 17L21 12" stroke="#10B981" stroke-width="2" stroke-linejoin="round"/>
                            <path d="M3 17L12 22L21 17" stroke="#10B981" stroke-width="2" stroke-linejoin="round"/>
                        </svg>
                        <span class="text-xl font-bold bg-gradient-to-r from-green-400 to-green-600 bg-clip-text text-transparent">Guyana HSSE</span>
                    </div>
                    <p class="text-gray-400 text-sm">
                        Advancing Health, Safety, Security and Environment standards across Guyana's industries.
                    </p>
                </div>
                <div>
                    <h4 class="font-bold text-lg mb-4">Quick Links</h4>
                    <ul class="space-y-2">
                        <li><Link href="#" class="text-gray-400 hover:text-green-400 transition-colors">Home</Link></li>
                        <li><Link href="#features" class="text-gray-400 hover:text-green-400 transition-colors">Features</Link></li>
                        <li><Link href="#" class="text-gray-400 hover:text-green-400 transition-colors">About Us</Link></li>
                        <li><Link href="#" class="text-gray-400 hover:text-green-400 transition-colors">Contact</Link></li>
                    </ul>
                </div>
                <div>
                    <h4 class="font-bold text-lg mb-4">Resources</h4>
                    <ul class="space-y-2">
                        <li><Link href="#" class="text-gray-400 hover:text-green-400 transition-colors">Documentation</Link></li>
                        <li><Link href="#" class="text-gray-400 hover:text-green-400 transition-colors">Guides</Link></li>
                        <li><Link href="#" class="text-gray-400 hover:text-green-400 transition-colors">Regulations</Link></li>
                        <li><Link href="#" class="text-gray-400 hover:text-green-400 transition-colors">Training</Link></li>
                    </ul>
                </div>
                <div>
                    <h4 class="font-bold text-lg mb-4">Contact</h4>
                    <ul class="space-y-2">
                        <li class="text-gray-400">Georgetown, Guyana</li>
                        <li class="text-gray-400">info@guyana-hsse.gov.gy</li>
                        <li class="text-gray-400">+592 123 4567</li>
                    </ul>
                </div>
            </div>
            <div class="max-w-7xl mx-auto pt-8 mt-8 border-t border-gray-800 text-center text-gray-500 text-sm">
                <p>© 2023 Guyana HSSE Portal. All rights reserved.</p>
            </div>
        </footer>
    </div>
</template>