import React, { useState, useEffect } from 'react';
import { View, FlatList, Text, StyleSheet } from 'react-native';
import { supabase } from '@/lib/supabase';
import { HealthProfessional } from '@/lib/types';

interface ProfessionalWithProfile extends HealthProfessional {
    profiles: {
        full_name: string;
        district: string;
        phone?: string;
    };
}

export default function DirectoryScreen() {
    const [professionals, setProfessionals] = useState<ProfessionalWithProfile[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchProfessionals();
    }, []);

    const fetchProfessionals = async () => {
        try {
            const { data, error } = await supabase
                .from('health_professionals')
                .select(`
          *,
          profiles(
            full_name,
            district,
            phone
          )
        `);

            if (error) throw error;
            setProfessionals(data || []);
        } catch (error) {
            console.error('Error fetching professionals:', error);
        } finally {
            setLoading(false);
        }
    };

    const renderProfessional = ({ item }: { item: ProfessionalWithProfile }) => (
        <View style={styles.professionalCard}>
            <Text style={styles.name}>{item.profiles.full_name}</Text>
            <Text style={styles.specialty}>{item.specialty}</Text>
            {item.structure && <Text style={styles.structure}>{item.structure}</Text>}
            <Text style={styles.district}>{item.profiles.district}</Text>
            {item.profiles.phone && <Text style={styles.phone}>{item.profiles.phone}</Text>}
        </View>
    );

    if (loading) {
        return (
            <View style={styles.center}>
                <Text>Chargement de l'annuaire...</Text>
            </View>
        );
    }

    return (
        <View style={styles.container}>
            <FlatList
                data={professionals}
                keyExtractor={(item) => item.user_id}
                renderItem={renderProfessional}
                ListEmptyComponent={
                    <View style={styles.center}>
                        <Text>Aucun professionnel trouvé</Text>
                    </View>
                }
            />
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f5f5f5',
    },
    center: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    professionalCard: {
        backgroundColor: '#fff',
        padding: 15,
        marginBottom: 10,
        marginHorizontal: 10,
        borderRadius: 8,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.1,
        shadowRadius: 2,
        elevation: 2,
    },
    name: {
        fontSize: 18,
        fontWeight: 'bold',
        marginBottom: 5,
    },
    specialty: {
        fontSize: 16,
        color: '#007AFF',
        marginBottom: 5,
    },
    structure: {
        fontSize: 14,
        color: '#666',
        marginBottom: 5,
    },
    district: {
        fontSize: 14,
        color: '#666',
        marginBottom: 5,
    },
    phone: {
        fontSize: 14,
        color: '#007AFF',
    },
});