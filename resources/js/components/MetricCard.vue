<script setup lang="ts">
defineProps({
    title: String,
    value: [String, Number],
    trend: String,
    icon: String,
    positive: Boolean,
    dark: Boolean
});
</script>

<template>
    <div class="rounded-lg p-4 transition-colors duration-200" 
         :class="{'bg-white shadow-sm hover:shadow-md dark:bg-gray-800 dark:hover:bg-gray-700': !dark, 
                 'bg-gray-800 shadow-sm hover:shadow-md dark:bg-gray-700 dark:hover:bg-gray-600': dark}">
        <div class="flex items-center justify-between">
            <div>
                <p class="text-sm font-medium" :class="{'text-gray-500 dark:text-gray-400': !dark, 'text-gray-300': dark}">
                    {{ title }}
                </p>
                <p class="mt-1 text-2xl font-semibold" 
                   :class="{'text-gray-900 dark:text-white': !dark, 'text-white': dark}">
                    {{ value }}
                </p>
            </div>
            <span class="text-2xl">{{ icon }}</span>
        </div>
        <div class="mt-2 text-xs flex items-center" 
             :class="{'text-gray-500 dark:text-gray-400': !dark, 'text-gray-300': dark}">
            <span class="flex items-center" :class="{'text-green-600 dark:text-green-400': positive, 'text-red-600 dark:text-red-400': !positive}">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          :d="positive ? 'M5 15l7-7 7 7' : 'M19 9l-7 7-7-7'" />
                </svg>
                {{ trend }}
            </span>
        </div>
    </div>
</template>