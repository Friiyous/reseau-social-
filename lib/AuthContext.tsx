import React, { createContext, useContext, useEffect, useState } from 'react';
import { Session, User } from '@supabase/supabase-js';
import { supabase } from './supabase';
import { Profile } from './types';

interface AuthContextType {
    user: User | null;
    profile: Profile | null;
    session: Session | null;
    loading: boolean;
    signIn: (email: string, password: string) => Promise<void>;
    signUp: (email: string, password: string, userData: Partial<Profile>) => Promise<void>;
    signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [profile, setProfile] = useState<Profile | null>(null);
    const [session, setSession] = useState<Session | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Get initial session
        supabase.auth.getSession().then(({ data: { session } }) => {
            setSession(session);
            setUser(session?.user ?? null);
            if (session?.user) {
                loadProfile(session.user.id);
            } else {
                setLoading(false);
            }
        });

        // Listen for auth changes
        const authListener = supabase.auth.onAuthStateChange((_event, session) => {
            setSession(session);
            setUser(session?.user ?? null);
            if (session?.user) {
                loadProfile(session.user.id);
            } else {
                setProfile(null);
                setLoading(false);
            }
        });

        return () => {
            authListener.data.subscription?.unsubscribe();
        };
    }, []);

    const loadProfile = async (userId: string) => {
        try {
            const { data, error } = await supabase
                .from('profiles')
                .select('*')
                .eq('id', userId)
                .single();

            if (error) throw error;
            setProfile(data);
        } catch (error) {
            console.error('Error loading profile:', error);
        } finally {
            setLoading(false);
        }
    };

    const signIn = async (email: string, password: string) => {
        // Demo mode for testing
        if (email === 'demo@demo.com' && password === 'demo123') {
            const fakeUser = {
                id: 'demo-user-id',
                email: 'demo@demo.com',
            } as User;
            const fakeProfile = {
                id: 'demo-user-id',
                email: 'demo@demo.com',
                full_name: 'Utilisateur Demo',
                phone: '+225 01 02 03 04',
                district: 'Abidjan',
                created_at: new Date().toISOString(),
            } as Profile;
            setUser(fakeUser);
            setProfile(fakeProfile);
            setSession({ user: fakeUser } as Session);
            return;
        }

        const { error } = await supabase.auth.signInWithPassword({
            email,
            password,
        });
        if (error) throw error;
    };

    const signUp = async (email: string, password: string, userData: Partial<Profile>) => {
        // Create auth user
        const { data: authData, error: authError } = await supabase.auth.signUp({
            email,
            password,
            options: {
                data: {
                    full_name: userData.full_name,
                },
            },
        });

        if (authError) throw authError;
        if (!authData.user) throw new Error('User creation failed');

        // Update profile with additional data
        const { error: profileError } = await supabase
            .from('profiles')
            .update({
                full_name: userData.full_name,
                phone: userData.phone,
                district: userData.district,
            })
            .eq('id', authData.user.id);

        if (profileError) throw profileError;

        // Create health professional record if specialty is provided
        if (userData.district) {
            const { error: healthError } = await supabase
                .from('health_professionals')
                .insert({
                    user_id: authData.user.id,
                    specialty: (userData as any).specialty || 'Non spécifié',
                    structure: (userData as any).structure,
                });

            if (healthError) throw healthError;
        }
    };

    const signOut = async () => {
        const { error } = await supabase.auth.signOut();
        if (error) throw error;
    };

    const value = {
        user,
        profile,
        session,
        loading,
        signIn,
        signUp,
        signOut,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};