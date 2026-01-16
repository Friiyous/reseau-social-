import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ScrollView } from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '@/lib/AuthContext';

export default function RegisterScreen() {
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        full_name: '',
        phone: '',
        district: '',
        specialty: '',
        structure: '',
    });
    const [loading, setLoading] = useState(false);
    const { signUp } = useAuth();
    const router = useRouter();

    const updateFormData = (field: string, value: string) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    const handleRegister = async () => {
        const { email, password, full_name, phone, district, specialty, structure } = formData;

        if (!email || !password || !full_name || !district) {
            Alert.alert('Erreur', 'Veuillez remplir les champs obligatoires (email, mot de passe, nom complet, district)');
            return;
        }

        setLoading(true);
        try {
            await signUp(email, password, {
                full_name,
                phone: phone || undefined,
                district,
                specialty,
                structure,
            });
            // Navigation will happen automatically via AuthContext
        } catch (error: any) {
            Alert.alert('Erreur d\'inscription', error.message || 'Une erreur est survenue');
        } finally {
            setLoading(false);
        }
    };

    const goToLogin = () => {
        router.push('/');
    };

    return (
        <ScrollView style={styles.container}>
            <Text style={styles.title}>Inscription</Text>

            <TextInput
                style={styles.input}
                placeholder="Email *"
                value={formData.email}
                onChangeText={(value) => updateFormData('email', value)}
                keyboardType="email-address"
                autoCapitalize="none"
            />

            <TextInput
                style={styles.input}
                placeholder="Mot de passe *"
                value={formData.password}
                onChangeText={(value) => updateFormData('password', value)}
                secureTextEntry
            />

            <TextInput
                style={styles.input}
                placeholder="Nom complet *"
                value={formData.full_name}
                onChangeText={(value) => updateFormData('full_name', value)}
            />

            <TextInput
                style={styles.input}
                placeholder="Téléphone"
                value={formData.phone}
                onChangeText={(value) => updateFormData('phone', value)}
                keyboardType="phone-pad"
            />

            <TextInput
                style={styles.input}
                placeholder="District *"
                value={formData.district}
                onChangeText={(value) => updateFormData('district', value)}
            />

            <TextInput
                style={styles.input}
                placeholder="Spécialité"
                value={formData.specialty}
                onChangeText={(value) => updateFormData('specialty', value)}
            />

            <TextInput
                style={styles.input}
                placeholder="Structure"
                value={formData.structure}
                onChangeText={(value) => updateFormData('structure', value)}
            />

            <TouchableOpacity
                style={[styles.button, loading && styles.buttonDisabled]}
                onPress={handleRegister}
                disabled={loading}
            >
                <Text style={styles.buttonText}>
                    {loading ? 'Inscription...' : 'S\'inscrire'}
                </Text>
            </TouchableOpacity>

            <TouchableOpacity onPress={goToLogin}>
                <Text style={styles.link}>Déjà un compte ? Se connecter</Text>
            </TouchableOpacity>
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        padding: 20,
        backgroundColor: '#fff',
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        textAlign: 'center',
        marginBottom: 30,
        marginTop: 20,
    },
    input: {
        borderWidth: 1,
        borderColor: '#ddd',
        padding: 15,
        marginBottom: 15,
        borderRadius: 8,
        fontSize: 16,
    },
    button: {
        backgroundColor: '#007AFF',
        padding: 15,
        borderRadius: 8,
        alignItems: 'center',
        marginBottom: 15,
    },
    buttonDisabled: {
        backgroundColor: '#ccc',
    },
    buttonText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: 'bold',
    },
    link: {
        color: '#007AFF',
        textAlign: 'center',
        fontSize: 16,
    },
});