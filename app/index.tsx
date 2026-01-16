import { useEffect } from 'react';
import { useRouter } from 'expo-router';
import { useAuth } from '@/lib/AuthContext';
import LoginScreen from '../screens/LoginScreen';

export default function Index() {
    const { user, loading } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (!loading && user) {
            router.replace('/(tabs)');
        }
    }, [user, loading]);

    return <LoginScreen />;
}
