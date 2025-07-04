<script setup lang="ts">
import InputError from '@/components/InputError.vue';
import TextLink from '@/components/TextLink.vue';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Head, useForm } from '@inertiajs/vue3';
import { AtSign, Lock, Loader2, Key, ShieldCheck, BuildingIcon, Mail, CheckCircle } from 'lucide-vue-next';
import { ref, onMounted, computed } from 'vue';
import AppLogoIcon from '@/components/AppLogoIcon.vue';

defineProps<{
    status?: string;
    canResetPassword: boolean;
}>();

const form = useForm({
    email: '',
    password: '',
    remember: false,
});

const submit = () => {
    form.post(route('login'), {
        onFinish: () => form.reset('password'),
    });
};

// For feature display
const activeFeature = ref(0);
const isSliding = ref(false);

// Features list with their associated colors
const features = [
    {
        icon: BuildingIcon,
        title: "Business Dashboard",
        description: "Access your business data in one centralized location.",
        bgColor: "bg-teal-600",
        cardColor: "bg-teal-800",
        buttonGradient: "from-teal-500 to-teal-600"
    },
    {
        icon: ShieldCheck,
        title: "Secure Access",
        description: "Enterprise-grade security to protect your sensitive data.",
        bgColor: "bg-cyan-600",
        cardColor: "bg-cyan-800",
        buttonGradient: "from-cyan-500 to-cyan-600"
    },
    {
        icon: Key,
        title: "Role-Based Permissions",
        description: "Control who sees what with customizable access levels.",
        bgColor: "bg-emerald-600",
        cardColor: "bg-emerald-800",
        buttonGradient: "from-emerald-500 to-emerald-600"
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
    <Head title="Log in | HSSEGY" />
    
    <div class="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 text-white flex items-center justify-center px-4 py-12">
        <div class="w-full max-w-5xl grid grid-cols-1 md:grid-cols-2 rounded-2xl shadow-2xl bg-gray-900 overflow-hidden">
            
            <!-- Left Side: Features Showcase with dynamic background -->
            <div 
                class="hidden md:flex md:flex-col justify-between p-10 text-white transition-colors duration-500"
                :class="currentBgColor"
            >
                <div>
                    <h2 class="text-3xl font-bold mb-2 text-center">Welcome Back</h2>
                    <p class="text-lg opacity-90 text-center">Log in to access your HSSE dashboard.</p>
                </div>
                
                <!-- Status Message (if any) -->
                <div v-if="status" class="mb-6 p-4 rounded-lg text-center">
                    <p class="text-sm font-medium text-green-400">{{ status }}</p>
                </div>
                

                <!-- Feature Card with dynamic background -->
                <div 
                class="mt-8 relative rounded-xl p-6 shadow-lg transition-colors duration-500 flex flex-col items-center text-center space-y-6"
                :class="currentCardColor"
                >
                    <!-- Animated Feature Content -->
                    <div 
                        class="transition-all duration-300 ease-in-out w-full"
                        :class="isSliding ? 'opacity-0 -translate-y-4' : 'opacity-100 translate-y-0'"
                    >
                        <!-- Icon -->
                        <div class="mb-4 flex h-14 w-14 items-center justify-center rounded-xl bg-white/20 p-3 mx-auto">
                        <component :is="features[activeFeature].icon" class="h-8 w-8 text-white" />
                        </div>

                        <!-- Title & Description -->
                        <h3 class="text-xl font-bold mb-1">{{ features[activeFeature].title }}</h3>
                        <p class="text-white/90 text-sm leading-relaxed">{{ features[activeFeature].description }}</p>
                    </div>

                    <!-- Stats Block -->
                    <div class="w-full rounded-xl px-4 py-5 bg-white/10 space-y-4">
                        <h4 class="font-semibold text-sm text-white/80">Trusted by businesses countrywide</h4>
                        <div class="grid grid-cols-3 gap-4 text-center text-white">
                        <div>
                            <div class="text-xl font-bold">500+</div>
                            <div class="text-xs text-white/70">Happy clients</div>
                        </div>
                        <div>
                            <div class="text-xl font-bold">98%</div>
                            <div class="text-xs text-white/70">Satisfaction rate</div>
                        </div>
                        <div>
                            <div class="text-xl font-bold">24/7</div>
                            <div class="text-xs text-white/70">Support</div>
                        </div>
                        </div>
                    </div>
                </div>


                <!-- Feature Navigation Dots - Now below the card -->
                <div class="flex justify-center space-x-3 mt-4 mb-8">
                    <button 
                        v-for="(feature, index) in features" 
                        :key="index"
                        @click="setActiveFeature(index)"
                        class="h-2.5 w-2.5 rounded-full transition-all duration-300 focus:outline-none"
                        :class="index === activeFeature ? 'bg-white scale-110' : 'bg-white/40 hover:bg-white/60'"
                        :aria-label="`Show feature: ${feature.title}`"
                    ></button>
                </div>
            </div>
    
            <!-- Right Side: Login Form -->
            <div class="p-8 md:p-12 bg-gray-950">
                <div class="mb-8 text-center">
                    <div class="mx-auto flex size-16 items-center justify-center rounded-full bg-white shadow-lg ring-2 ring-cyan-500">
                        <AppLogoIcon class="size-16 text-teal-600" />
                    </div>
                    <h1 class="mt-4 text-2xl font-bold tracking-tight">Log in to your account</h1>
                    <p class="mt-1 text-sm text-gray-400">Enter your credentials to access your dashboard</p>
                </div>

                <!-- Remove the status message from the right panel -->
                
                <form @submit.prevent="submit" class="space-y-5">
                    <div class="relative">
                        <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-gray-400">
                            <Mail class="h-5 w-5" />
                        </div>
                        <Input 
                            id="email" 
                            v-model="form.email" 
                            type="email"
                            placeholder="Email Address" 
                            required
                            autofocus
                            :tabindex="1"
                            autocomplete="email"
                            class="pl-10 py-3 bg-gray-800/50 border-gray-700 rounded-md focus:border-cyan-500 focus:ring-cyan-500"
                        />
                        <InputError :message="form.errors.email" />
                    </div>
                    
                    <div class="relative">
                        <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-gray-400">
                            <Lock class="h-5 w-5" />
                        </div>
                        <Input 
                            id="password" 
                            v-model="form.password" 
                            type="password"
                            placeholder="Password" 
                            required
                            :tabindex="2"
                            autocomplete="current-password"
                            class="pl-10 py-3 bg-gray-800/50 border-gray-700 rounded-md focus:border-cyan-500 focus:ring-cyan-500"
                        />
                        <InputError :message="form.errors.password" />
                    </div>
                    
                    <div class="flex items-center justify-between">
                        <div class="flex items-center">
                            <Checkbox id="remember" v-model="form.remember" :tabindex="3" class="border-gray-600 bg-gray-800" />
                            <Label for="remember" class="ml-2 text-sm text-gray-300">Remember me</Label>
                        </div>
                        
                        <TextLink 
                            v-if="canResetPassword" 
                            :href="route('password.request')" 
                            class="text-sm text-cyan-400 hover:text-cyan-300"
                            :tabindex="4"
                        >
                            Forgot password?
                        </TextLink>
                    </div>
                    
                    <button
                        type="submit"
                        :disabled="form.processing"
                        class="flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r px-6 py-3 text-white font-semibold transition-all hover:scale-105 disabled:opacity-60 mt-6"
                        :class="currentButtonGradient"
                        :tabindex="5"
                    >
                        <Loader2 v-if="form.processing" class="h-5 w-5 animate-spin" />
                        <span>{{ form.processing ? 'Logging in...' : 'Log in' }}</span>
                    </button>
                </form>
                
                <div class="mt-8 pt-6 border-t border-gray-800">
                    <p class="text-center text-sm text-gray-500">
                        Don't have an account?
                        <TextLink :href="route('register')" class="text-cyan-400 hover:text-cyan-300 font-medium" :tabindex="6">
                            Create an account
                        </TextLink>
                    </p>
                </div>
            </div>
        </div>
    </div>
</template>