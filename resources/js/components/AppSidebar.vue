<script setup lang="ts">
import NavFooter from '@/components/NavFooter.vue';
import NavMain from '@/components/NavMain.vue';
import NavUser from '@/components/NavUser.vue';
import { Sidebar, SidebarContent, SidebarFooter, SidebarHeader, SidebarMenu, SidebarMenuButton, SidebarMenuItem } from '@/components/ui/sidebar';
import { type NavItem } from '@/types';
import { Link } from '@inertiajs/vue3';
import { BookOpen, Building, Clipboard, ClipboardList, Folder, LayoutGrid, LucideGraduationCap, Users2 } from 'lucide-vue-next';
import AppLogo from './AppLogo.vue';

const mainNavItems: NavItem[] = [
    {
        title: 'Dashboard',
        href: '/dashboard',
        icon: LayoutGrid,
    },
    {
        title: 'Organizations',
        href: '/admin/organizations',
        icon: Building
    },
    {
        title: 'Reports',
        href: '/admin/reports',
        icon: ClipboardList
    },
    {
        title: 'Proactive Monitoring',
        href: '/ai-scrapers',
        icon: ClipboardList
    },
    {
        title: 'Training',
        href: '/admin/trainings',
        icon: LucideGraduationCap
    },
    {
        title: 'Users',
        href: '/admin/users',
        icon: Users2
    },
];

const footerNavItems: NavItem[] = [
    {
        title: 'Documentation',
        href: 'https://fiducia.gy',
        icon: BookOpen,
    },
];
</script>

<template>
    <Sidebar collapsible="icon" variant="inset">
        <SidebarHeader>
            <SidebarMenu>
                <SidebarMenuItem>
                    <SidebarMenuButton size="lg" as-child>
                        <Link :href="route('dashboard')">
                            <AppLogo />
                        </Link>
                    </SidebarMenuButton>
                </SidebarMenuItem>
            </SidebarMenu>
        </SidebarHeader>

        <SidebarContent>
            <NavMain :items="mainNavItems" />
        </SidebarContent>

        <SidebarFooter>
            <NavFooter :items="footerNavItems" />
            <NavUser />
        </SidebarFooter>
    </Sidebar>
    <slot />
</template>
