import { Stack } from 'expo-router';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { AuthProvider } from '../lib/AuthContext';

export default function RootLayout() {
    return (
        <SafeAreaProvider>
            <AuthProvider>
                <Stack screenOptions={{ headerShown: false }}>
                    <Stack.Screen name="index" />
                    <Stack.Screen name="register" />
                    <Stack.Screen name="(tabs)" />
                </Stack>
            </AuthProvider>
        </SafeAreaProvider>
    );
}
