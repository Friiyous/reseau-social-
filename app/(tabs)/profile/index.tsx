import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import { useAuth } from '../../../lib/AuthContext';

export default function ProfileScreen() {
    const { user, profile, signOut } = useAuth();

    const handleSignOut = () => {
        Alert.alert(
            'Déconnexion',
            'Êtes-vous sûr de vouloir vous déconnecter ?',
            [
                { text: 'Annuler', style: 'cancel' },
                { text: 'Déconnexion', onPress: signOut },
            ]
        );
    };

    return (
        <View style={styles.container}>
            <View style={styles.profileCard}>
                <Text style={styles.title}>Mon Profil</Text>

                <View style={styles.infoSection}>
                    <Text style={styles.label}>Email:</Text>
                    <Text style={styles.value}>{user?.email}</Text>
                </View>

                <View style={styles.infoSection}>
                    <Text style={styles.label}>Nom complet:</Text>
                    <Text style={styles.value}>{profile?.full_name || 'Non défini'}</Text>
                </View>

                <View style={styles.infoSection}>
                    <Text style={styles.label}>Téléphone:</Text>
                    <Text style={styles.value}>{profile?.phone || 'Non défini'}</Text>
                </View>

                <View style={styles.infoSection}>
                    <Text style={styles.label}>District:</Text>
                    <Text style={styles.value}>{profile?.district || 'Non défini'}</Text>
                </View>

                {profile && (
                    <View style={styles.infoSection}>
                        <Text style={styles.label}>Membre depuis:</Text>
                        <Text style={styles.value}>{new Date(profile.created_at).toLocaleDateString('fr-FR')}</Text>
                    </View>
                )}
            </View>

            <TouchableOpacity style={styles.signOutButton} onPress={handleSignOut}>
                <Text style={styles.signOutText}>Se déconnecter</Text>
            </TouchableOpacity>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f5f5f5',
        padding: 20,
    },
    profileCard: {
        backgroundColor: '#fff',
        padding: 20,
        borderRadius: 8,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.1,
        shadowRadius: 2,
        elevation: 2,
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        marginBottom: 20,
        textAlign: 'center',
    },
    infoSection: {
        marginBottom: 15,
    },
    label: {
        fontSize: 14,
        color: '#666',
        marginBottom: 5,
    },
    value: {
        fontSize: 16,
        fontWeight: '500',
    },
    signOutButton: {
        backgroundColor: '#ff4444',
        padding: 15,
        borderRadius: 8,
        alignItems: 'center',
        marginTop: 20,
    },
    signOutText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: 'bold',
    },
});