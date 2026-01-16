import { useState, useEffect } from 'react';
import { supabase } from '@/lib/supabase';
import { Post } from '@/lib/types';
import { useAuth } from '@/lib/AuthContext';

export const usePosts = () => {
    const { user } = useAuth();
    const [posts, setPosts] = useState<Post[]>([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);

    const fetchPosts = async () => {
        try {
            const { data, error } = await supabase
                .from('posts')
                .select(`
          *,
          author:profiles(*),
          post_likes(count),
          comments(count)
        `)
                .order('created_at', { ascending: false });

            if (error) throw error;

            // Transform data to include counts and is_liked
            const postsWithMeta = await Promise.all(
                (data || []).map(async (post: any) => {
                    const { data: likeData } = await supabase
                        .from('post_likes')
                        .select('user_id')
                        .eq('post_id', post.id)
                        .eq('user_id', user?.id || '');

                    return {
                        ...post,
                        likes_count: post.post_likes?.[0]?.count || 0,
                        comments_count: post.comments?.[0]?.count || 0,
                        is_liked: likeData && likeData.length > 0,
                    };
                })
            );

            setPosts(postsWithMeta);
        } catch (error) {
            console.error('Error fetching posts:', error);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    const createPost = async (content: string, imageUrl?: string) => {
        if (!user) throw new Error('User not authenticated');

        const { error } = await supabase.from('posts').insert({
            author_id: user.id,
            content,
            image_url: imageUrl,
        });

        if (error) throw error;
        await fetchPosts();
    };

    const likePost = async (postId: string) => {
        if (!user) return;

        const { error } = await supabase.from('post_likes').insert({
            post_id: postId,
            user_id: user.id,
        });

        if (error) throw error;
        await fetchPosts();
    };

    const unlikePost = async (postId: string) => {
        if (!user) return;

        const { error } = await supabase
            .from('post_likes')
            .delete()
            .eq('post_id', postId)
            .eq('user_id', user.id);

        if (error) throw error;
        await fetchPosts();
    };

    const refresh = () => {
        setRefreshing(true);
        fetchPosts();
    };

    useEffect(() => {
        fetchPosts();

        // Subscribe to new posts
        const subscription = supabase
            .channel('posts')
            .on('postgres_changes', { event: '*', schema: 'public', table: 'posts' }, () => {
                fetchPosts();
            })
            .subscribe();

        return () => {
            subscription.unsubscribe();
        };
    }, [user]);

    return {
        posts,
        loading,
        refreshing,
        createPost,
        likePost,
        unlikePost,
        refresh,
    };
};
