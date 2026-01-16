import { useState, useEffect } from 'react';
import { supabase } from '@/lib/supabase';
import { Comment } from '@/lib/types';

export const useComments = (postId: string) => {
    const [comments, setComments] = useState<Comment[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchComments = async () => {
        try {
            const { data, error } = await supabase
                .from('comments')
                .select(`
          *,
          author:profiles(*)
        `)
                .eq('post_id', postId)
                .order('created_at', { ascending: true });

            if (error) throw error;
            setComments(data || []);
        } catch (error) {
            console.error('Error fetching comments:', error);
        } finally {
            setLoading(false);
        }
    };

    const addComment = async (content: string, authorId: string) => {
        const { error } = await supabase.from('comments').insert({
            post_id: postId,
            author_id: authorId,
            content,
        });

        if (error) throw error;
        await fetchComments();
    };

    useEffect(() => {
        fetchComments();

        // Subscribe to new comments
        const subscription = supabase
            .channel(`comments:${postId}`)
            .on(
                'postgres_changes',
                { event: 'INSERT', schema: 'public', table: 'comments', filter: `post_id=eq.${postId}` },
                () => {
                    fetchComments();
                }
            )
            .subscribe();

        return () => {
            subscription.unsubscribe();
        };
    }, [postId]);

    return {
        comments,
        loading,
        addComment,
    };
};
