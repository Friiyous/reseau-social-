import { useState, useEffect } from 'react';
import { supabase } from '../../lib/supabase';
import { Post } from '../../lib/types';
import { useAuth } from '@/lib/AuthContext';

export const usePosts = () => {
    const { user } = useAuth();
    const [posts, setPosts] = useState<Post[]>([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);

    const fetchPosts = async () => {
        try {
            // Demo data for testing
            if (user?.email === 'demo@demo.com') {
                const demoPosts: Post[] = [
                    {
                        id: '1',
                        author_id: 'demo-user-id',
                        content: 'Bienvenue sur Le District ! Plateforme de networking pour les professionnels de santé en Côte d\'Ivoire.',
                        created_at: new Date().toISOString(),
                        author: {
                            id: 'demo-user-id',
                            email: 'demo@demo.com',
                            full_name: 'Dr. Marie Koné',
                            district: 'Abidjan',
                            created_at: new Date().toISOString(),
                        },
                        likes_count: 5,
                        comments_count: 2,
                        is_liked: false,
                    },
                    {
                        id: '2',
                        author_id: 'demo-user-id',
                        content: 'Session de formation sur les nouvelles technologies médicales ce weekend. Inscrivez-vous !',
                        created_at: new Date(Date.now() - 3600000).toISOString(),
                        author: {
                            id: 'demo-user-id',
                            email: 'demo@demo.com',
                            full_name: 'Dr. Jean Dupont',
                            district: 'Korhogo',
                            created_at: new Date().toISOString(),
                        },
                        likes_count: 12,
                        comments_count: 5,
                        is_liked: true,
                    },
                ];
                setPosts(demoPosts);
                setLoading(false);
                setRefreshing(false);
                return;
            }

            const { data, error } = await supabase
                .from('posts')
                .select(`
          *,
          author:profiles(*)
        `)
                .order('created_at', { ascending: false });

            if (error) throw error;

            // Transform data to include counts and is_liked
            const postsWithMeta = await Promise.all(
                (data || []).map(async (post: any) => {
                    const { count: likeCount } = await supabase
                        .from('post_likes')
                        .select('*', { count: 'exact', head: true })
                        .eq('post_id', post.id);

                    const { count: commentCount } = await supabase
                        .from('comments')
                        .select('*', { count: 'exact', head: true })
                        .eq('post_id', post.id);

                    const { data: userLikeData } = await supabase
                        .from('post_likes')
                        .select('user_id')
                        .eq('post_id', post.id)
                        .eq('user_id', user?.id || '');

                    return {
                        ...post,
                        likes_count: likeCount || 0,
                        comments_count: commentCount || 0,
                        is_liked: userLikeData && userLikeData.length > 0,
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