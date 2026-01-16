import 'react-native-url-polyfill/auto';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { createClient } from '@supabase/supabase-js';
import Constants from 'expo-constants';

const rawUrl = Constants.expoConfig?.extra?.supabaseUrl || process.env.EXPO_PUBLIC_SUPABASE_URL || '';
const rawKey = Constants.expoConfig?.extra?.supabaseAnonKey || process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY || '';

// Prevent crash with placeholders for frontend-only viewing
const supabaseUrl = rawUrl.includes('your_supabase_project_url') || !rawUrl ? 'https://placeholder-project.supabase.co' : rawUrl;
const supabaseAnonKey = rawKey.includes('your_supabase_anon_key') || !rawKey ? 'placeholder-key' : rawKey;

if (supabaseUrl === 'https://placeholder-project.supabase.co') {
    console.warn('⚠️ Supabase URL is using a placeholder. The app will work but data operations will fail.');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
    auth: {
        storage: AsyncStorage,
        autoRefreshToken: true,
        persistSession: true,
        detectSessionInUrl: false,
    },
});
