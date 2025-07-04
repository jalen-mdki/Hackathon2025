<script setup lang="ts">
import InputError from '@/components/InputError.vue';
import TextLink from '@/components/TextLink.vue';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Head, useForm } from '@inertiajs/vue3';
import { Building2, Users, FileText, Globe, User, AtSign, Lock, KeyRound, Loader2, CheckCircle, Mountain, Phone, Home, File, ClipboardCheck } from 'lucide-vue-next';
import { ref, onMounted, computed } from 'vue';
import AppLogoIcon from '@/components/AppLogoIcon.vue';

const form = useForm({
    first_name: '',
    last_name: '',
    email: '',
    address: '',
    phone: '',
    password: '',
    password_confirmation: '',
});

const submitForm = () => {
    form.post(route('register'), {
        onFinish: () => form.reset('password', 'password_confirmation'),
    });
};

// For feature display
const activeFeature = ref(0);
const isSliding = ref(false);

    // Features list with their associated colors
const features = [
    {
        icon: File,
        title: "See Reports",
        description: "Manage HSSEGY.",
        bgColor: "bg-teal-600",
        cardColor: "bg-teal-800",
        buttonGradient: "from-teal-500 to-teal-600"
    },
    {
        icon: ClipboardCheck,
        title: "Ensure Safety Compliances",
        description: "Ensure Safety is managed.",
        bgColor: "bg-cyan-600",
        cardColor: "bg-cyan-800",
        buttonGradient: "from-cyan-500 to-cyan-600"
    },
    {
        icon: Globe,
        title: "Access Anywhere",
        description: "Cloud-based system accessible from any device, anytime, anywhere.",
        bgColor: "bg-green-600",
        cardColor: "bg-green-800",
        buttonGradient: "from-green-500 to-green-600"
    }
];

// Get the current feature's colors
const currentBgColor = computed(() => features[activeFeature.value].bgColor);
const currentCardColor = computed(() => features[activeFeature.value].cardColor);
const currentButtonGradient = computed(() => features[activeFeature.value].buttonGradient);

// Set active feature with animation
const setActiveFeature = (index) => {
    if (activeFeature.value === index || isSliding.value) return;
    
    isSliding.value = true;
    setTimeout(() => {
        activeFeature.value = index;
        isSliding.value = false;
    }, 300);
};

// Auto-rotate features
onMounted(() => {
    const interval = setInterval(() => {
        if (!isSliding.value) {
            isSliding.value = true;
            setTimeout(() => {
                activeFeature.value = (activeFeature.value + 1) % features.length;
                isSliding.value = false;
            }, 300);
        }
    }, 5000);
    
    return () => clearInterval(interval);
});
</script>

<template>
    <Head title="Create Account | HSSEGY" />
    
    <div class="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 text-white flex items-center justify-center px-4 py-12">
        <div class="w-full max-w-5xl grid grid-cols-1 md:grid-cols-2 rounded-2xl shadow-2xl bg-gray-900 overflow-hidden">
            
            <!-- Left Side: Features Showcase with dynamic background -->
            <div 
                class="hidden md:flex md:flex-col justify-between p-10 text-white transition-colors duration-500"
                :class="currentBgColor"
            >
                <div>
                    <h2 class="text-3xl font-bold mb-4">The Complete HSSE Solution</h2>
                    <p class="text-lg opacity-90">Powerful tools for your business hsse needs.</p>
                </div>
                
                <!-- Feature Card with dynamic background -->
                <div 
                    class="mt-8 relative overflow-hidden rounded-xl p-6 shadow-lg transition-colors duration-500"
                    :class="currentCardColor"
                >
                    <div 
                        class="transition-all duration-300 ease-in-out flex flex-col items-center text-center"
                        :class="isSliding ? 'opacity-0 -translate-y-8' : 'opacity-100 translate-y-0'"
                    >
                        <div class="mb-4 flex h-14 w-14 items-center justify-center rounded-xl bg-white/20 p-3">
                            <component :is="features[activeFeature].icon" class="h-8 w-8 text-white" />
                        </div>
                        <h3 class="text-xl font-bold mb-2">{{ features[activeFeature].title }}</h3>
                        <p class="text-white/90">{{ features[activeFeature].description }}</p>
                    </div>
                </div>
                
                <!-- Feature Navigation Dots - Now below the card -->
                <div class="flex justify-center space-x-3 mt-3 mb-2">
                    <button 
                        v-for="(feature, index) in features" 
                        :key="index"
                        @click="setActiveFeature(index)"
                        class="h-2.5 w-2.5 rounded-full transition-all duration-300 focus:outline-none"
                        :class="index === activeFeature ? 'bg-white scale-110' : 'bg-white/40 hover:bg-white/60'"
                        :aria-label="`Show feature: ${feature.title}`"
                    ></button>
                </div>
                
                <!-- Benefits -->
                <ul class="space-y-4">
                    <li class="flex items-center gap-3">
                        <CheckCircle class="w-5 h-5 text-white" />
                        <span>Secure & fast setup process</span>
                    </li>
                    <li class="flex items-center gap-3">
                        <CheckCircle class="w-5 h-5 text-white" />
                        <span>All core features included</span>
                    </li>
                    <li class="flex items-center gap-3">
                        <CheckCircle class="w-5 h-5 text-white" />
                        <span>Free plan available to start</span>
                    </li>
                </ul>
            </div>
    
            <!-- Right Side: Form -->
            <div class="p-8 md:p-12 bg-gray-950">
                <div class="mb-6 text-center">
                    <div class="mx-auto flex size-16 items-center justify-center rounded-full bg-white shadow-lg ring-2 ring-cyan-500">
                        <AppLogoIcon class="size-16 text-teal-600" />
                    </div>
                    <h1 class="mt-4 text-2xl font-bold tracking-tight">Create Account</h1>
                    <p class="mt-1 text-sm text-gray-400">Let's get you started with HSSEGY.</p>
                </div>
    
                <form @submit.prevent="submitForm" class="space-y-5">
                    <div class="relative">
                        <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-gray-400">
                            <User class="h-5 w-5" />
                        </div>
                        <Input 
                            v-model="form.first_name" 
                            placeholder="First Name" 
                            class="pl-10 py-3 bg-gray-800/50 rounded-md border-gray-700 focus:border-cyan-500 focus:ring-cyan-500"
                        />
                        <InputError :message="form.errors.first_name" />
                    </div>

                    <div class="relative">
                        <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-gray-400">
                            <User class="h-5 w-5" />
                        </div>
                        <Input 
                            v-model="form.last_name" 
                            placeholder="Last Name" 
                            class="pl-10 py-3 bg-gray-800/50 border-gray-700 rounded-md focus:border-cyan-500 focus:ring-cyan-500"
                        />
                        <InputError :message="form.errors.last_name" />
                    </div>
                    
                    <div class="relative">
                        <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-gray-400">
                            <AtSign class="h-5 w-5" />
                        </div>
                        <Input 
                            v-model="form.email" 
                            placeholder="Email Address" 
                            type="email"
                            class="pl-10 py-3 bg-gray-800/50 border-gray-700 rounded-md focus:border-cyan-500 focus:ring-cyan-500"
                        />
                        <InputError :message="form.errors.email" />
                    </div>

                    <div class="relative">
                        <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-gray-400">
                            <Phone class="h-5 w-5" />
                        </div>
                        <Input 
                            v-model="form.phone" 
                            placeholder="Phone Number" 
                            class="pl-10 py-3 bg-gray-800/50 border-gray-700 rounded-md focus:border-cyan-500 focus:ring-cyan-500"
                        />
                        <InputError :message="form.errors.phone" />
                    </div>

                    <div class="relative">
                        <div class="pointer-events-none absolute left-0 top-3 flex items-center pl-3 text-gray-400">
                            <Home class="h-5 w-5" />
                        </div>
                        <textarea
                            v-model="form.address"
                            placeholder="Address"
                            rows="3"
                            class="w-full rounded-md border-gray-700 bg-gray-800/50 pl-10 py-2 text-white focus:border-cyan-500 focus:ring-cyan-500"
                        ></textarea>
                        <InputError :message="form.errors.address" />
                    </div>
                    
                    <div class="relative">
                        <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-gray-400">
                            <Lock class="h-5 w-5" />
                        </div>
                        <Input 
                            v-model="form.password" 
                            placeholder="Password" 
                            type="password"
                            class="pl-10 py-3 bg-gray-800/50 border-gray-700 rounded-md focus:border-cyan-500 focus:ring-cyan-500"
                        />
                        <InputError :message="form.errors.password" />
                    </div>
                    
                    <div class="relative">
                        <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-gray-400">
                            <KeyRound class="h-5 w-5" />
                        </div>
                        <Input 
                            v-model="form.password_confirmation" 
                            placeholder="Confirm Password" 
                            type="password"
                            class="pl-10 py-3 bg-gray-800/50 border-gray-700 rounded-md focus:border-cyan-500 focus:ring-cyan-500"
                        />
                        <InputError :message="form.errors.password_confirmation" />
                    </div>
    
                    <button
                        type="submit"
                        :disabled="form.processing"
                        class="flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r px-6 py-3 text-white font-semibold transition-all hover:scale-105 disabled:opacity-60"
                        :class="currentButtonGradient"
                    >
                        <Loader2 v-if="form.processing" class="h-5 w-5 animate-spin" />
                        <span>{{ form.processing ? 'Creating account...' : 'Create Account' }}</span>
                    </button>
                </form>
    
                <p class="mt-6 text-center text-sm text-gray-500">
                    Already have an account?
                    <TextLink :href="route('login')" class="text-cyan-400 hover:underline">Log in</TextLink>
                </p>
            </div>
        </div>
    </div>
</template>

<style scoped>
/* Optional: Add any additional styling here */
</style>