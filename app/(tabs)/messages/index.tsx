import React from 'react';
import { View, FlatList, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { useConversations } from '@/app/hooks/useConversations';
import { Conversation } from '@/lib/types';

export default function MessagesScreen() {
    const { conversations, loading } = useConversations();

    const renderConversation = ({ item }: { item: Conversation }) => {
        const otherParticipants = item.participants?.filter(p => p.id !== item.participants?.[0]?.id) || [];
        const conversationName = otherParticipants.map(p => p.full_name).join(', ') || 'Conversation';

        return (
            <TouchableOpacity style={styles.conversationItem}>
                <Text style={styles.conversationName}>{conversationName}</Text>
                {item.last_message && (
                    <Text style={styles.lastMessage}>
                        {item.last_message.sender?.full_name}: {item.last_message.content}
                    </Text>
                )}
            </TouchableOpacity>
        );
    };

    if (loading) {
        return (
            <View style={styles.center}>
                <Text>Chargement des conversations...</Text>
            </View>
        );
    }

    return (
        <View style={styles.container}>
            <FlatList
                data={conversations}
                keyExtractor={(item) => item.id}
                renderItem={renderConversation}
                ListEmptyComponent={
                    <View style={styles.center}>
                        <Text>Aucune conversation</Text>
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
    conversationItem: {
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
    conversationName: {
        fontSize: 16,
        fontWeight: 'bold',
        marginBottom: 5,
    },
    lastMessage: {
        fontSize: 14,
        color: '#666',
    },
});