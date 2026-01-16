import { useState, useEffect } from 'react';
import { supabase } from '@/lib/supabase';
import { Conversation, Message } from '@/lib/types';
import { useAuth } from @/lib/AuthContext';

export const useConversations = () => {
    const { user } = useAuth();
    const [conversations, setConversations] = useState<Conversation[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchConversations = async () => {
        if (!user) return;

        try {
            const { data, error } = await supabase
                .from('conversation_participants')
                .select(`
          conversation_id,
          conversations(
            id,
            created_at,
            updated_at
          )
        `)
                .eq('user_id', user.id);

            if (error) throw error;

            // Fetch participants and last message for each conversation
            const conversationsWithDetails = await Promise.all(
                (data || []).map(async (item: any) => {
                    const conversationId = item.conversations.id;

                    // Get participants
                    const { data: participantsData } = await supabase
                        .from('conversation_participants')
                        .select('user_id, profiles(*)')
                        .eq('conversation_id', conversationId);

                    // Get last message
                    const { data: messagesData } = await supabase
                        .from('messages')
                        .select('*')
                        .eq('conversation_id', conversationId)
                        .order('created_at', { ascending: false })
                        .limit(1);

                    return {
                        ...item.conversations,
                        participants: participantsData?.map((p: any) => p.profiles) || [],
                        last_message: messagesData?.[0] || null,
                    };
                })
            );

            setConversations(conversationsWithDetails);
        } catch (error) {
            console.error('Error fetching conversations:', error);
        } finally {
            setLoading(false);
        }
    };

    const createConversation = async (participantIds: string[]) => {
        if (!user) throw new Error('User not authenticated');

        // Create conversation
        const { data: conversationData, error: conversationError } = await supabase
            .from('conversations')
            .insert({})
            .select()
            .single();

        if (conversationError) throw conversationError;

        // Add participants
        const participants = [user.id, ...participantIds].map((userId) => ({
            conversation_id: conversationData.id,
            user_id: userId,
        }));

        const { error: participantsError } = await supabase
            .from('conversation_participants')
            .insert(participants);

        if (participantsError) throw participantsError;

        await fetchConversations();
        return conversationData.id;
    };

    useEffect(() => {
        fetchConversations();

        // Subscribe to new conversations
        if (user) {
            const subscription = supabase
                .channel('conversations')
                .on(
                    'postgres_changes',
                    { event: '*', schema: 'public', table: 'conversation_participants', filter: `user_id=eq.${user.id}` },
                    () => {
                        fetchConversations();
                    }
                )
                .subscribe();

            return () => {
                subscription.unsubscribe();
            };
        }
    }, [user]);

    return {
        conversations,
        loading,
        createConversation,
    };
};
