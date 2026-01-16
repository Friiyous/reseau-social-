import { useState, useEffect } from 'react';
import { supabase } from '@/lib/supabase';
import { Message } from '@/lib/types';
import { useAuth } from @/lib/AuthContext';

export const useMessages = (conversationId: string) => {
    const { user } = useAuth();
    const [messages, setMessages] = useState<Message[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchMessages = async () => {
        try {
            const { data, error } = await supabase
                .from('messages')
                .select(`
          *,
          sender:profiles(*)
        `)
                .eq('conversation_id', conversationId)
                .order('created_at', { ascending: true });

            if (error) throw error;
            setMessages(data || []);
        } catch (error) {
            console.error('Error fetching messages:', error);
        } finally {
            setLoading(false);
        }
    };

    const sendMessage = async (content: string) => {
        if (!user) throw new Error('User not authenticated');

        const { error } = await supabase.from('messages').insert({
            conversation_id: conversationId,
            sender_id: user.id,
            content,
        });

        if (error) throw error;

        // Update conversation updated_at
        await supabase
            .from('conversations')
            .update({ updated_at: new Date().toISOString() })
            .eq('id', conversationId);
    };

    useEffect(() => {
        fetchMessages();

        // Subscribe to new messages
        const subscription = supabase
            .channel(`messages:${conversationId}`)
            .on(
                'postgres_changes',
                { event: 'INSERT', schema: 'public', table: 'messages', filter: `conversation_id=eq.${conversationId}` },
                () => {
                    fetchMessages();
                }
            )
            .subscribe();

        return () => {
            subscription.unsubscribe();
        };
    }, [conversationId]);

    return {
        messages,
        loading,
        sendMessage,
    };
};
