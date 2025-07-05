<script setup lang="ts">
defineProps({
    title: String,
    dark: Boolean
});
</script>

<template>
    <div class="rounded-lg p-4 transition-colors duration-200"
         :class="{'bg-white shadow-sm hover:shadow-md dark:bg-gray-800 dark:hover:bg-gray-700': !dark, 
                 'bg-gray-800 shadow-sm hover:shadow-md dark:bg-gray-700 dark:hover:bg-gray-600': dark}">
        <h3 class="text-lg font-medium mb-4" :class="{'text-gray-900 dark:text-white': !dark, 'text-white': dark}">
            {{ title }}
        </h3>
        <slot />
        <div class="mt-2 text-sm" :class="{'text-gray-500 dark:text-gray-400': !dark, 'text-gray-300': dark}">
            <slot name="insight" />
        </div>
    </div>
</template>