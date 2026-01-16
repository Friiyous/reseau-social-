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
import { Picker } from '@react-native-picker/picker';
import { useRouter } from 'expo-router';
import { useAuth } from '@/lib/AuthContext';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { colors } from '@/lib/theme/colors';
import { spacing } from '@/lib/theme/spacing';
import { typography } from '@/lib/theme/typography';
import { KORHOGO_DISTRICTS } from '@/lib/locations/korhogo';
import { HEALTH_CATEGORIES } from '@/lib/health-categories';

export default function RegisterScreen() {
    const router = useRouter();
    const { signUp } = useAuth();
    const [formData, setFormData] = useState({
        fullName: '',
        email: '',
        password: '',
        confirmPassword: '',
        phone: '',
        district: '',
        specialty: '',
        structure: '',
    });
    const [loading, setLoading] = useState(false);
    const [errors, setErrors] = useState<Record<string, string>>({});

    const validate = (): boolean => {
        const newErrors: Record<string, string> = {};

        if (!formData.fullName) newErrors.fullName = 'Nom complet requis';
        if (!formData.email) {
            newErrors.email = 'Email requis';
        } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
            newErrors.email = 'Email invalide';
        }
        if (!formData.password) {
            newErrors.password = 'Mot de passe requis';
        } else if (formData.password.length < 6) {
            newErrors.password = 'Minimum 6 caractères';
        }
        if (formData.password !== formData.confirmPassword) {
            newErrors.confirmPassword = 'Les mots de passe ne correspondent pas';
        }
        if (!formData.district) newErrors.district = 'District requis';
        if (!formData.specialty) newErrors.specialty = 'Spécialité requise';

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSignUp = async () => {
        if (!validate()) return;

        setLoading(true);
        try {
            await signUp(formData.email, formData.password, {
                full_name: formData.fullName,
                phone: formData.phone,
                district: formData.district,
                specialty: formData.specialty,
                structure: formData.structure,
            } as any);
            Alert.alert('Succès', 'Compte créé avec succès !', [
                { text: 'OK', onPress: () => router.replace('/(tabs)') },
            ]);
        } catch (error: any) {
            Alert.alert('Erreur', error.message || 'Une erreur est survenue');
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
                    <Text style={styles.title}>Créer un compte</Text>
                    <Text style={styles.subtitle}>Rejoignez Le District</Text>
                </View>

                <View style={styles.form}>
                    <Input
                        label="Nom complet"
                        value={formData.fullName}
                        onChangeText={(text) => setFormData({ ...formData, fullName: text })}
                        placeholder="Jean Kouassi"
                        error={errors.fullName}
                    />

                    <Input
                        label="Email"
                        value={formData.email}
                        onChangeText={(text) => setFormData({ ...formData, email: text })}
                        placeholder="votre@email.com"
                        keyboardType="email-address"
                        autoCapitalize="none"
                        error={errors.email}
                    />

                    <Input
                        label="Téléphone"
                        value={formData.phone}
                        onChangeText={(text) => setFormData({ ...formData, phone: text })}
                        placeholder="+225 XX XX XX XX XX"
                        keyboardType="phone-pad"
                        error={errors.phone}
                    />

                    <View style={styles.pickerContainer}>
                        <Text style={styles.label}>District sanitaire</Text>
                        <View style={styles.pickerWrapper}>
                            <Picker
                                selectedValue={formData.district}
                                onValueChange={(value) => setFormData({ ...formData, district: value })}
                                style={styles.picker}
                            >
                                <Picker.Item label="Sélectionner un district" value="" />
                                {KORHOGO_DISTRICTS.map((district) => (
                                    <Picker.Item key={district.id} label={district.name} value={district.id} />
                                ))}
                            </Picker>
                        </View>
                        {errors.district && <Text style={styles.error}>{errors.district}</Text>}
                    </View>

                    <View style={styles.pickerContainer}>
                        <Text style={styles.label}>Spécialité</Text>
                        <View style={styles.pickerWrapper}>
                            <Picker
                                selectedValue={formData.specialty}
                                onValueChange={(value) => setFormData({ ...formData, specialty: value })}
                                style={styles.picker}
                            >
                                <Picker.Item label="Sélectionner une spécialité" value="" />
                                {HEALTH_CATEGORIES.map((category) => (
                                    <Picker.Item key={category.id} label={category.name} value={category.id} />
                                ))}
                            </Picker>
                        </View>
                        {errors.specialty && <Text style={styles.error}>{errors.specialty}</Text>}
                    </View>

                    <Input
                        label="Structure (optionnel)"
                        value={formData.structure}
                        onChangeText={(text) => setFormData({ ...formData, structure: text })}
                        placeholder="Centre de santé de..."
                        error={errors.structure}
                    />

                    <Input
                        label="Mot de passe"
                        value={formData.password}
                        onChangeText={(text) => setFormData({ ...formData, password: text })}
                        placeholder="••••••••"
                        secureTextEntry
                        error={errors.password}
                    />

                    <Input
                        label="Confirmer le mot de passe"
                        value={formData.confirmPassword}
                        onChangeText={(text) => setFormData({ ...formData, confirmPassword: text })}
                        placeholder="••••••••"
                        secureTextEntry
                        error={errors.confirmPassword}
                    />

                    <Button
                        title="Créer mon compte"
                        onPress={handleSignUp}
                        loading={loading}
                        fullWidth
                        style={styles.button}
                    />

                    <Button
                        title="J'ai déjà un compte"
                        onPress={() => router.back()}
                        variant="ghost"
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
        padding: spacing.lg,
        paddingTop: spacing.xxxl,
    },
    header: {
        alignItems: 'center',
        marginBottom: spacing.xl,
    },
    title: {
        ...typography.h1,
        color: colors.primary,
        marginBottom: spacing.xs,
    },
    subtitle: {
        ...typography.body1,
        color: colors.textSecondary,
    },
    form: {
        width: '100%',
    },
    pickerContainer: {
        marginBottom: spacing.base,
    },
    label: {
        ...typography.body2,
        fontWeight: '600',
        color: colors.textPrimary,
        marginBottom: spacing.xs,
    },
    pickerWrapper: {
        backgroundColor: colors.white,
        borderWidth: 1,
        borderColor: colors.border,
        borderRadius: 12,
        overflow: 'hidden',
    },
    picker: {
        height: 50,
    },
    error: {
        ...typography.caption,
        color: colors.error,
        marginTop: spacing.xs,
    },
    button: {
        marginTop: spacing.base,
        marginBottom: spacing.base,
    },
});
