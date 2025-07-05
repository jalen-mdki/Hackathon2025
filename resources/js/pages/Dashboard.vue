<script setup lang="ts">
import AppLayout from '@/layouts/AppLayout.vue';
import { Head, usePage } from '@inertiajs/vue3';
import { computed, ref, onMounted } from 'vue';
import { Pie, Bar, Line, Doughnut, PolarArea } from 'vue-chartjs';
import {
    Chart,
    Title,
    Tooltip,
    Legend,
    ArcElement,
    CategoryScale,
    LinearScale,
    BarElement,
    PointElement,
    LineElement,
    Filler,
    RadialLinearScale
} from 'chart.js';

Chart.register(
    Title, Tooltip, Legend, ArcElement, 
    CategoryScale, LinearScale, BarElement, 
    PointElement, LineElement, Filler, RadialLinearScale
);

const breadcrumbs = [
    { title: 'Dashboard', href: '/dashboard' },
];

const page = usePage();
const darkMode = ref(true);

// Consistent color palette matching the hero design
const colors = {
    primary: '#3B82F6',      // Blue
    success: '#10B981',      // Emerald
    warning: '#F59E0B',      // Amber
    danger: '#EF4444',       // Red
    purple: '#8B5CF6',       // Purple
    teal: '#14B8A6',         // Teal
    indigo: '#6366F1',       // Indigo
    pink: '#EC4899',         // Pink
    
    // Chart gradients
    gradients: {
        blue: 'linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)',
        emerald: 'linear-gradient(135deg, #10B981 0%, #047857 100%)',
        amber: 'linear-gradient(135deg, #F59E0B 0%, #D97706 100%)',
        red: 'linear-gradient(135deg, #EF4444 0%, #DC2626 100%)',
        purple: 'linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%)',
        teal: 'linear-gradient(135deg, #14B8A6 0%, #0D9488 100%)',
        indigo: 'linear-gradient(135deg, #6366F1 0%, #4F46E5 100%)',
        pink: 'linear-gradient(135deg, #EC4899 0%, #DB2777 100%)'
    }
};

// Enhanced chart data with consistent colors
const reportStatusData = computed(() => {
    const data = page.props.reportStatusData;
    return {
        ...data,
        datasets: [{
            ...data.datasets[0],
            backgroundColor: [
                colors.success,   // Completed
                colors.warning,   // In Progress
                colors.danger,    // Pending
                colors.primary,   // Other
            ],
            borderColor: '#1e293b',
            borderWidth: 3,
            hoverBorderWidth: 5,
            hoverOffset: 15,
            cutout: '65%'
        }]
    };
});

const trainingStatusData = computed(() => {
    const data = page.props.trainingStatusData;
    return {
        ...data,
        datasets: [{
            ...data.datasets[0],
            backgroundColor: [
                colors.success,   // Completed
                colors.danger,    // Not Completed
            ],
            borderColor: '#1e293b',
            borderWidth: 3,
            borderRadius: 8,
            hoverBorderWidth: 5,
        }]
    };
});

const hazardsByRiskData = computed(() => {
    const data = page.props.hazardsByRiskData;
    return {
        ...data,
        datasets: [{
            ...data.datasets[0],
            backgroundColor: [
                colors.danger,    // High Risk
                colors.warning,   // Medium Risk
                colors.success,   // Low Risk
            ],
            borderColor: '#1e293b',
            borderWidth: 2,
            pointRadius: 0,
            pointHoverRadius: 0,
        }]
    };
});

const reportsByMonthData = computed(() => {
    const data = page.props.reportsByMonthData;
    return {
        ...data,
        datasets: [{
            ...data.datasets[0],
            backgroundColor: colors.primary,
            borderColor: colors.primary,
            borderWidth: 0,
            borderRadius: 8,
            borderSkipped: false,
            hoverBackgroundColor: colors.indigo,
        }]
    };
});

// Enhanced metrics calculations
const totalReports = computed(() => {
    return reportStatusData.value.datasets[0].data.reduce((a, b) => a + b, 0);
});

const unresolvedPercentage = computed(() => {
    const data = reportStatusData.value.datasets[0].data;
    const unresolved = data[1] + data[2]; // In Progress + Pending
    return Math.round((unresolved / totalReports.value) * 100);
});

const trainingCompletionRate = computed(() => {
    const completed = trainingStatusData.value.datasets[0].data[0];
    const total = trainingStatusData.value.datasets[0].data.reduce((a, b) => a + b, 0);
    return Math.round((completed / total) * 100);
});

const highRiskPercentage = computed(() => {
    const highRisk = hazardsByRiskData.value.datasets[0].data[0];
    const total = hazardsByRiskData.value.datasets[0].data.reduce((a, b) => a + b, 0);
    return Math.round((highRisk / total) * 100);
});

// Enhanced chart options with consistent styling
const chartOptions = (type: string) => ({
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
        intersect: false,
        mode: 'index'
    },
    animation: {
        duration: 1500,
        easing: 'easeInOutQuart'
    },
    plugins: {
        legend: {
            position: 'bottom',
            labels: {
                usePointStyle: true,
                pointStyle: 'circle',
                padding: 20,
                color: '#94a3b8',
                font: {
                    size: 12,
                    weight: '500'
                }
            }
        },
        tooltip: {
            backgroundColor: 'rgba(15, 23, 42, 0.95)',
            titleColor: '#f1f5f9',
            bodyColor: '#cbd5e1',
            borderColor: '#334155',
            borderWidth: 1,
            padding: 16,
            cornerRadius: 12,
            displayColors: true,
            usePointStyle: true,
            titleFont: {
                size: 14,
                weight: 'bold'
            },
            bodyFont: {
                size: 13
            },
            callbacks: {
                label: function(context: any) {
                    let label = context.dataset.label || '';
                    if (label) label += ': ';
                    
                    if (type === 'pie' || type === 'doughnut') {
                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                        const percentage = Math.round((context.parsed / total) * 100);
                        label += `${context.parsed} (${percentage}%)`;
                    } else {
                        label += context.parsed.y || context.parsed;
                    }
                    return label;
                }
            }
        }
    },
    scales: type === 'bar' || type === 'line' ? {
        x: {
            grid: {
                color: '#334155',
                lineWidth: 1,
                drawBorder: false
            },
            ticks: {
                color: '#94a3b8',
                font: {
                    size: 11,
                    weight: '500'
                },
                padding: 10
            }
        },
        y: {
            grid: {
                color: '#334155',
                lineWidth: 1,
                drawBorder: false
            },
            ticks: {
                color: '#94a3b8',
                font: {
                    size: 11,
                    weight: '500'
                },
                padding: 10
            },
            beginAtZero: true
        }
    } : type === 'polarArea' ? {
        r: {
            grid: {
                color: '#334155',
                lineWidth: 1
            },
            ticks: {
                color: '#94a3b8',
                font: {
                    size: 10
                },
                backdropColor: 'transparent'
            }
        }
    } : undefined
});

const toggleDarkMode = () => {
    darkMode.value = !darkMode.value;
    document.documentElement.classList.toggle('dark', darkMode.value);
};

onMounted(() => {
    document.documentElement.classList.toggle('dark', darkMode.value);
});
</script>

<template>
    <Head title="Safety Dashboard" />

    <AppLayout :breadcrumbs="breadcrumbs">
        <div class="min-h-screen bg-slate-50 dark:bg-gray-900">
            <!-- Hero Section -->
            <div class="relative bg-gradient-to-br from-blue-800 via-blue-900 to-slate-700 overflow-hidden">
                <!-- Background Pattern -->
                <div class="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmZmZmYiIGZpbGwtb3BhY2l0eT0iMC4xIj48cGF0aCBkPSJNMzYgMzRjMC0yLjIwOTEzOS0xLjc5MDg2MS00LTQtNHMtNCA1Ljc5MDg2MS00IDhMNCA2MGg4VjQwaDI0eiIvPjwvZz48L2c+PC9zdmc+')] opacity-20"></div>
                
                <div class="relative px-6 py-16">
                    <div class="max-w-7xl mx-auto">
                        <!-- Header -->
                        <div class="flex items-center justify-between mb-12">
                            <div class="flex items-center gap-4">
                                <div class="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center">
                                    <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                    </svg>
                                </div>
                                <div>
                                    <h1 class="text-4xl font-bold text-white">Safety Command Center</h1>
                                    <p class="text-blue-100 text-lg mt-2">Real-time safety monitoring and analytics</p>
                                </div>
                            </div>
                            
                            <div class="flex items-center gap-4">
                                <div class="flex items-center gap-2 px-4 py-2 bg-white/20 backdrop-blur-sm rounded-xl">
                                    <div class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                                    <span class="text-white font-medium">Live Data</span>
                                </div>
                                
                                <button @click="toggleDarkMode" 
                                        class="p-3 rounded-xl bg-white/20 hover:bg-white/30 backdrop-blur-sm transition-all duration-200">
                                    <svg v-if="darkMode" class="w-5 h-5 text-yellow-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path>
                                    </svg>
                                    <svg v-else class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path>
                                    </svg>
                                </button>
                            </div>
                        </div>

                        <!-- Hero Metrics -->
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                            <!-- Total Reports -->
                            <div class="bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20 p-6 hover:bg-white/15 transition-all duration-200">
                                <div class="flex items-center justify-between">
                                    <div>
                                        <p class="text-blue-100 text-sm font-medium">Total Reports</p>
                                        <p class="text-4xl font-bold text-white mt-2">{{ totalReports }}</p>
                                        <p class="text-green-300 text-sm mt-3 flex items-center gap-1">
                                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 11l5-5m0 0l5 5m-5-5v12"></path>
                                            </svg>
                                            +12% from last month
                                        </p>
                                    </div>
                                    <div class="w-12 h-12 bg-blue-500/30 rounded-xl flex items-center justify-center">
                                        <svg class="w-6 h-6 text-blue-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                                        </svg>
                                    </div>
                                </div>
                            </div>

                            <!-- High Risk Hazards -->
                            <div class="bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20 p-6 hover:bg-white/15 transition-all duration-200">
                                <div class="flex items-center justify-between">
                                    <div>
                                        <p class="text-blue-100 text-sm font-medium">High Risk Hazards</p>
                                        <p class="text-4xl font-bold text-white mt-2">{{ hazardsByRiskData.datasets[0].data[0] }}</p>
                                        <p class="text-red-300 text-sm mt-3 flex items-center gap-1">
                                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 15.5c-.77.833.192 2.5 1.732 2.5z"></path>
                                            </svg>
                                            Requires attention
                                        </p>
                                    </div>
                                    <div class="w-12 h-12 bg-red-500/30 rounded-xl flex items-center justify-center">
                                        <svg class="w-6 h-6 text-red-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 15.5c-.77.833.192 2.5 1.732 2.5z"></path>
                                        </svg>
                                    </div>
                                </div>
                            </div>

                            <!-- Training Completed -->
                            <div class="bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20 p-6 hover:bg-white/15 transition-all duration-200">
                                <div class="flex items-center justify-between">
                                    <div>
                                        <p class="text-blue-100 text-sm font-medium">Training Completed</p>
                                        <p class="text-4xl font-bold text-white mt-2">{{ trainingCompletionRate }}%</p>
                                        <p class="text-green-300 text-sm mt-3 flex items-center gap-1">
                                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 11l5-5m0 0l5 5m-5-5v12"></path>
                                            </svg>
                                            +18% from last quarter
                                        </p>
                                    </div>
                                    <div class="w-12 h-12 bg-green-500/30 rounded-xl flex items-center justify-center">
                                        <svg class="w-6 h-6 text-green-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                                        </svg>
                                    </div>
                                </div>
                            </div>

                            <!-- Avg Resolution Time -->
                            <div class="bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20 p-6 hover:bg-white/15 transition-all duration-200">
                                <div class="flex items-center justify-between">
                                    <div>
                                        <p class="text-blue-100 text-sm font-medium">Avg. Resolution</p>
                                        <p class="text-4xl font-bold text-white mt-2">3.2d</p>
                                        <p class="text-green-300 text-sm mt-3 flex items-center gap-1">
                                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 11l5-5m0 0l5 5m-5-5v12"></path>
                                            </svg>
                                            -0.5 days improvement
                                        </p>
                                    </div>
                                    <div class="w-12 h-12 bg-purple-500/30 rounded-xl flex items-center justify-center">
                                        <svg class="w-6 h-6 text-purple-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                        </svg>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Main Content -->
            <div class="max-w-7xl mx-auto px-6 py-8">
                <!-- Charts Section -->
                <div class="grid grid-cols-1 xl:grid-cols-2 gap-8 mb-8">
                    <!-- Incident Status Chart -->
                    <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-xl border border-slate-200 dark:border-slate-700 p-6">
                        <div class="flex items-center justify-between mb-6">
                            <div>
                                <h3 class="text-xl font-bold text-slate-900 dark:text-slate-100">Incident Status Overview</h3>
                                <p class="text-slate-600 dark:text-slate-400 text-sm mt-1">Current incident distribution and resolution progress</p>
                            </div>
                            <div class="flex items-center gap-2 px-3 py-1 bg-green-100 dark:bg-green-900/30 rounded-full">
                                <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                                <span class="text-green-700 dark:text-green-300 text-sm font-medium">Live</span>
                            </div>
                        </div>
                        
                        <div class="h-80">
                            <Doughnut 
                                :data="reportStatusData" 
                                :options="chartOptions('doughnut')"
                            />
                        </div>
                        
                        <div class="mt-6 p-4 bg-orange-50 dark:bg-orange-900/20 rounded-xl border-l-4 border-orange-400">
                            <div class="flex items-center gap-2 mb-2">
                                <svg class="w-5 h-5 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 15.5c-.77.833.192 2.5 1.732 2.5z"></path>
                                </svg>
                                <span class="font-semibold text-orange-800 dark:text-orange-200">Action Required</span>
                            </div>
                            <p class="text-orange-700 dark:text-orange-300 text-sm">
                                {{ unresolvedPercentage }}% of incidents need immediate attention. Focus on pending and in-progress cases.
                            </p>
                        </div>
                    </div>

                    <!-- Monthly Trends Chart -->
                    <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-xl border border-slate-200 dark:border-slate-700 p-6">
                        <div class="flex items-center justify-between mb-6">
                            <div>
                                <h3 class="text-xl font-bold text-slate-900 dark:text-slate-100">Monthly Incident Trends</h3>
                                <p class="text-slate-600 dark:text-slate-400 text-sm mt-1">Track incident patterns and seasonal variations</p>
                            </div>
                            <div class="flex items-center gap-2 px-3 py-1 bg-blue-100 dark:bg-blue-900/30 rounded-full">
                                <svg class="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                                </svg>
                                <span class="text-blue-700 dark:text-blue-300 text-sm font-medium">Trending</span>
                            </div>
                        </div>
                        
                        <div class="h-80">
                            <Bar 
                                :data="reportsByMonthData" 
                                :options="chartOptions('bar')"
                            />
                        </div>
                        
                        <div class="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-xl border-l-4 border-blue-400">
                            <div class="flex items-center gap-2 mb-2">
                                <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                                </svg>
                                <span class="font-semibold text-blue-800 dark:text-blue-200">Trend Analysis</span>
                            </div>
                            <p class="text-blue-700 dark:text-blue-300 text-sm">
                                Monthly incidents show seasonal patterns. Consider implementing preventive measures during peak periods.
                            </p>
                        </div>
                    </div>
                </div>

                <!-- Risk Analysis Chart -->
                <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-xl border border-slate-200 dark:border-slate-700 p-6 mb-8">
                    <div class="flex items-center justify-between mb-6">
                        <div>
                            <h3 class="text-xl font-bold text-slate-900 dark:text-slate-100">Risk Assessment Matrix</h3>
                            <p class="text-slate-600 dark:text-slate-400 text-sm mt-1">Comprehensive hazard risk analysis with priority indicators</p>
                        </div>
                        <div class="flex items-center gap-3">
                            <div class="px-3 py-1 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-full text-sm font-medium">
                                High Risk Alert
                            </div>
                        </div>
                    </div>
                    
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        <div class="h-96">
                            <PolarArea 
                                :data="hazardsByRiskData" 
                                :options="chartOptions('polarArea')"
                            />
                        </div>
                        
                        <div class="space-y-6">
                            <!-- Risk Breakdown -->
                            <div>
                                <h4 class="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">Risk Distribution</h4>
                                
                                <div class="space-y-3">
                                    <div class="flex items-center justify-between p-4 bg-red-50 dark:bg-red-900/20 rounded-xl border border-red-200 dark:border-red-800">
                                        <div class="flex items-center gap-3">
                                            <div class="w-4 h-4 bg-red-500 rounded-full"></div>
                                            <span class="font-medium text-slate-900 dark:text-slate-100">High Risk</span>
                                        </div>
                                        <span class="font-bold text-red-600 dark:text-red-400">{{ hazardsByRiskData.datasets[0].data[0] }}</span>
                                    </div>
                                    
                                    <div class="flex items-center justify-between p-4 bg-amber-50 dark:bg-amber-900/20 rounded-xl border border-amber-200 dark:border-amber-800">
                                        <div class="flex items-center gap-3">
                                            <div class="w-4 h-4 bg-amber-500 rounded-full"></div>
                                            <span class="font-medium text-slate-900 dark:text-slate-100">Medium Risk</span>
                                        </div>
                                        <span class="font-bold text-amber-600 dark:text-amber-400">{{ hazardsByRiskData.datasets[0].data[1] }}</span>
                                    </div>
                                    
                                    <div class="flex items-center justify-between p-4 bg-emerald-50 dark:bg-emerald-900/20 rounded-xl border border-emerald-200 dark:border-emerald-800">
                                        <div class="flex items-center gap-3">
                                            <div class="w-4 h-4 bg-emerald-500 rounded-full"></div>
                                            <span class="font-medium text-slate-900 dark:text-slate-100">Low Risk</span>
                                        </div>
                                        <span class="font-bold text-emerald-600 dark:text-emerald-400">{{ hazardsByRiskData.datasets[0].data[2] }}</span>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Quick Actions -->
                            <div>
                                <h4 class="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4">Quick Actions</h4>
                                
                                <div class="space-y-3">
                                    <button class="w-full p-4 bg-red-50 dark:bg-red-900/20 hover:bg-red-100 dark:hover:bg-red-900/30 rounded-xl border border-red-200 dark:border-red-800 text-left transition-all duration-200 group">
                                        <div class="flex items-center gap-3">
                                            <div class="w-10 h-10 bg-red-500 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                                                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 15.5c-.77.833.192 2.5 1.732 2.5z"></path>
                                                </svg>
                                            </div>
                                            <div>
                                                <span class="font-medium text-slate-900 dark:text-slate-100 block">Review High Risk Items</span>
                                                <span class="text-sm text-slate-600 dark:text-slate-400">Immediate attention required</span>
                                            </div>
                                        </div>
                                    </button>
                                    
                                    <button class="w-full p-4 bg-blue-50 dark:bg-blue-900/20 hover:bg-blue-100 dark:hover:bg-blue-900/30 rounded-xl border border-blue-200 dark:border-blue-800 text-left transition-all duration-200 group">
                                        <div class="flex items-center gap-3">
                                            <div class="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                                                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                                                </svg>
                                            </div>
                                            <div>
                                                <span class="font-medium text-slate-900 dark:text-slate-100 block">Generate Risk Report</span>
                                                <span class="text-sm text-slate-600 dark:text-slate-400">Comprehensive analysis</span>
                                            </div>
                                        </div>
                                    </button>
                                    
                                    <button class="w-full p-4 bg-emerald-50 dark:bg-emerald-900/20 hover:bg-emerald-100 dark:hover:bg-emerald-900/30 rounded-xl border border-emerald-200 dark:border-emerald-800 text-left transition-all duration-200 group">
                                        <div class="flex items-center gap-3">
                                            <div class="w-10 h-10 bg-emerald-500 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                                                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"></path>
                                                </svg>
                                            </div>
                                            <div>
                                                <span class="font-medium text-slate-900 dark:text-slate-100 block">Schedule Safety Audit</span>
                                                <span class="text-sm text-slate-600 dark:text-slate-400">Preventive measures</span>
                                            </div>
                                        </div>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mt-6 p-4 bg-red-50 dark:bg-red-900/20 rounded-xl border-l-4 border-red-500">
                        <div class="flex items-center gap-2 mb-2">
                            <svg class="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 15.5c-.77.833.192 2.5 1.732 2.5z"></path>
                            </svg>
                            <span class="font-semibold text-red-800 dark:text-red-200">Critical Risk Alert</span>
                        </div>
                        <p class="text-red-700 dark:text-red-300 text-sm">
                            {{ highRiskPercentage }}% of hazards are classified as high risk. Immediate intervention required for critical safety areas.
                        </p>
                    </div>
                </div>

                <!-- Training Progress and Analytics -->
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    <!-- Training Progress Chart -->
                    <div class="lg:col-span-2 bg-white dark:bg-slate-800 rounded-2xl shadow-xl border border-slate-200 dark:border-slate-700 p-6">
                        <div class="flex items-center justify-between mb-6">
                            <div>
                                <h3 class="text-xl font-bold text-slate-900 dark:text-slate-100">Training Completion Dashboard</h3>
                                <p class="text-slate-600 dark:text-slate-400 text-sm mt-1">Monitor employee safety training progress and compliance</p>
                            </div>
                            <div class="flex items-center gap-2 px-3 py-1 bg-emerald-100 dark:bg-emerald-900/30 rounded-full">
                                <svg class="w-4 h-4 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                                <span class="text-emerald-700 dark:text-emerald-300 text-sm font-medium">{{ trainingCompletionRate }}% Complete</span>
                            </div>
                        </div>
                        
                        <div class="h-64">
                            <Bar 
                                :data="trainingStatusData" 
                                :options="{
                                    ...chartOptions('bar'),
                                    indexAxis: 'y',
                                    plugins: {
                                        ...chartOptions('bar').plugins,
                                        legend: {
                                            ...chartOptions('bar').plugins.legend,
                                            position: 'bottom'
                                        }
                                    }
                                }"
                            />
                        </div>
                        
                        <div class="mt-6 p-4 bg-emerald-50 dark:bg-emerald-900/20 rounded-xl border-l-4 border-emerald-500">
                            <div class="flex items-center gap-2 mb-2">
                                <svg class="w-5 h-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                                <span class="font-semibold text-emerald-800 dark:text-emerald-200">Progress Update</span>
                            </div>
                            <p class="text-emerald-700 dark:text-emerald-300 text-sm">
                                Training completion rate is {{ trainingCompletionRate }}%. Target goal is 95% - {{ 95 - trainingCompletionRate }}% remaining to achieve compliance.
                            </p>
                        </div>
                    </div>
                    
                    <!-- Training Insights Panel -->
                    <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-xl border border-slate-200 dark:border-slate-700 p-6">
                        <h4 class="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-6">Training Insights</h4>
                        
                        <div class="space-y-6">
                            <!-- Completion Rate Circle -->
                            <div class="flex flex-col items-center">
                                <div class="relative w-32 h-32">
                                    <svg class="w-32 h-32 transform -rotate-90" viewBox="0 0 36 36">
                                        <path class="text-slate-200 dark:text-slate-700" 
                                              stroke="currentColor" 
                                              stroke-width="3" 
                                              fill="transparent"
                                              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                                        <path class="text-emerald-500" 
                                              stroke="currentColor" 
                                              stroke-width="3" 
                                              fill="transparent"
                                              stroke-dasharray="{{ trainingCompletionRate }}, 100"
                                              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                                    </svg>
                                    <div class="absolute inset-0 flex items-center justify-center">
                                        <span class="text-2xl font-bold text-slate-900 dark:text-slate-100">{{ trainingCompletionRate }}%</span>
                                    </div>
                                </div>
                                <p class="text-slate-600 dark:text-slate-400 text-sm mt-2 text-center">Overall Completion</p>
                            </div>
                            
                            <!-- Training Stats -->
                            <div class="space-y-3">
                                <div class="flex justify-between items-center p-3 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg border border-emerald-200 dark:border-emerald-800">
                                    <span class="text-sm font-medium text-slate-700 dark:text-slate-300">Completed</span>
                                    <span class="font-bold text-emerald-600 dark:text-emerald-400">{{ trainingStatusData.datasets[0].data[0] }}</span>
                                </div>
                                
                                <div class="flex justify-between items-center p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
                                    <span class="text-sm font-medium text-slate-700 dark:text-slate-300">Pending</span>
                                    <span class="font-bold text-red-600 dark:text-red-400">{{ trainingStatusData.datasets[0].data[1] }}</span>
                                </div>
                                
                                <div class="flex justify-between items-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                                    <span class="text-sm font-medium text-slate-700 dark:text-slate-300">Next Deadline</span>
                                    <span class="font-bold text-blue-600 dark:text-blue-400">7 days</span>
                                </div>
                            </div>
                            
                            <!-- Action Buttons -->
                            <div class="space-y-2">
                                <button class="w-full p-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors">
                                    Send Reminders
                                </button>
                                <button class="w-full p-3 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-800 dark:text-slate-200 rounded-lg font-medium transition-colors">
                                    View Details
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Additional Analytics Row -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-8">
                    <!-- Recent Activity -->
                    <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-xl border border-slate-200 dark:border-slate-700 p-6">
                        <h4 class="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4 flex items-center gap-2">
                            <svg class="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                            Recent Activity
                        </h4>
                        
                        <div class="space-y-3">
                            <div class="flex items-start gap-3 p-3 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg border border-emerald-200 dark:border-emerald-800">
                                <div class="w-2 h-2 bg-emerald-500 rounded-full mt-2 flex-shrink-0"></div>
                                <div>
                                    <p class="text-sm font-medium text-slate-900 dark:text-slate-100">Incident #INV-2024-089 resolved</p>
                                    <p class="text-xs text-slate-600 dark:text-slate-400">2 hours ago</p>
                                </div>
                            </div>
                            
                            <div class="flex items-start gap-3 p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
                                <div class="w-2 h-2 bg-amber-500 rounded-full mt-2 flex-shrink-0"></div>
                                <div>
                                    <p class="text-sm font-medium text-slate-900 dark:text-slate-100">New high-risk hazard reported</p>
                                    <p class="text-xs text-slate-600 dark:text-slate-400">4 hours ago</p>
                                </div>
                            </div>
                            
                            <div class="flex items-start gap-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                                <div class="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                                <div>
                                    <p class="text-sm font-medium text-slate-900 dark:text-slate-100">Training module updated</p>
                                    <p class="text-xs text-slate-600 dark:text-slate-400">6 hours ago</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Safety Score -->
                    <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-xl border border-slate-200 dark:border-slate-700 p-6">
                        <h4 class="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4 flex items-center gap-2">
                            <svg class="w-5 h-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                            Safety Score
                        </h4>
                        
                        <div class="text-center">
                            <div class="relative inline-flex items-center justify-center w-24 h-24 mb-4">
                                <svg class="w-24 h-24 transform -rotate-90" viewBox="0 0 36 36">
                                    <path class="text-slate-200 dark:text-slate-700" 
                                          stroke="currentColor" 
                                          stroke-width="3" 
                                          fill="transparent"
                                          d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                                    <path class="text-emerald-500" 
                                          stroke="currentColor" 
                                          stroke-width="3" 
                                          fill="transparent"
                                          stroke-dasharray="87, 100"
                                          d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                                </svg>
                                <span class="absolute text-xl font-bold text-slate-900 dark:text-slate-100">87</span>
                            </div>
                            <p class="text-slate-600 dark:text-slate-400 text-sm mb-2">Excellent Safety Performance</p>
                            <div class="text-xs text-emerald-600 dark:text-emerald-400 flex items-center justify-center gap-1">
                                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 11l5-5m0 0l5 5m-5-5v12"></path>
                                </svg>
                                +5 points this month
                            </div>
                        </div>
                    </div>
                    
                    <!-- Upcoming Events -->
                    <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-xl border border-slate-200 dark:border-slate-700 p-6">
                        <h4 class="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4 flex items-center gap-2">
                            <svg class="w-5 h-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                            </svg>
                            Upcoming Events
                        </h4>
                        
                        <div class="space-y-3">
                            <div class="flex items-center gap-3 p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                                <div class="w-10 h-10 bg-purple-500 rounded-lg flex items-center justify-center text-white text-sm font-bold">
                                    15
                                </div>
                                <div>
                                    <p class="text-sm font-medium text-slate-900 dark:text-slate-100">Safety Audit</p>
                                    <p class="text-xs text-slate-600 dark:text-slate-400">Manufacturing Floor</p>
                                </div>
                            </div>
                            
                            <div class="flex items-center gap-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                                <div class="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center text-white text-sm font-bold">
                                    22
                                </div>
                                <div>
                                    <p class="text-sm font-medium text-slate-900 dark:text-slate-100">Training Session</p>
                                    <p class="text-xs text-slate-600 dark:text-slate-400">Emergency Procedures</p>
                                </div>
                            </div>
                            
                            <div class="flex items-center gap-3 p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
                                <div class="w-10 h-10 bg-amber-500 rounded-lg flex items-center justify-center text-white text-sm font-bold">
                                    28
                                </div>
                                <div>
                                    <p class="text-sm font-medium text-slate-900 dark:text-slate-100">Risk Assessment</p>
                                    <p class="text-xs text-slate-600 dark:text-slate-400">Quarterly Review</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </AppLayout>
</template>