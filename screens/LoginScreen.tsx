import React, { useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    KeyboardAvoidingView,
    Platform,
    ScrollView,
    Alert,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '@/lib/AuthContext';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { colors } from '@/lib/theme/colors';
import { spacing } from '@/lib/theme/spacing';
import { typography } from '@/lib/theme/typography';

export default function LoginScreen() {
    const router = useRouter();
    const { signIn } = useAuth();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [errors, setErrors] = useState<{ email?: string; password?: string }>({});

    const validate = (): boolean => {
        const newErrors: { email?: string; password?: string } = {};

        if (!email) {
            newErrors.email = 'Email requis';
        } else if (!/\S+@\S+\.\S+/.test(email)) {
            newErrors.email = 'Email invalide';
        }

        if (!password) {
            newErrors.password = 'Mot de passe requis';
        } else if (password.length < 6) {
            newErrors.password = 'Minimum 6 caractères';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSignIn = async () => {
        if (!validate()) return;

        setLoading(true);
        try {
            await signIn(email, password);
            router.replace('/(tabs)');
        } catch (error: any) {
            Alert.alert('Erreur de connexion', error.message || 'Une erreur est survenue');
        } finally {
            setLoading(false);
        }
    };

    return (
        <KeyboardAvoidingView
            behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
            style={styles.container}
        >
            <ScrollView contentContainerStyle={styles.scrollContent}>
                <View style={styles.header}>
                    <Text style={styles.title}>Le District</Text>
                    <Text style={styles.subtitle}>Plateforme des agents de santé</Text>
                </View>

                <View style={styles.form}>
                    <Input
                        label="Email"
                        value={email}
                        onChangeText={setEmail}
                        placeholder="votre@email.com"
                        keyboardType="email-address"
                        autoCapitalize="none"
                        error={errors.email}
                    />

                    <Input
                        label="Mot de passe"
                        value={password}
                        onChangeText={setPassword}
                        placeholder="••••••••"
                        secureTextEntry
                        error={errors.password}
                    />

                    <Button
                        title="Se connecter"
                        onPress={handleSignIn}
                        loading={loading}
                        fullWidth
                        style={styles.button}
                    />

                    <Button
                        title="Créer un compte"
                        onPress={() => router.push('/register')}
                        variant="outline"
                        fullWidth
                    />
                </View>
            </ScrollView>
        </KeyboardAvoidingView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: colors.backgroundSecondary,
    },
    scrollContent: {
        flexGrow: 1,
        justifyContent: 'center',
        padding: spacing.lg,
    },
    header: {
        alignItems: 'center',
        marginBottom: spacing.xxxl,
    },
    title: {
        ...typography.display,
        color: colors.primary,
        marginBottom: spacing.sm,
    },
    subtitle: {
        ...typography.body1,
        color: colors.textSecondary,
        textAlign: 'center',
    },
    form: {
        width: '100%',
    },
    button: {
        marginBottom: spacing.base,
    },
});
