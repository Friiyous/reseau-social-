import React from 'react';
import { View, FlatList, RefreshControl, StyleSheet, Text } from 'react-native';
import { usePosts } from '@/app/hooks/usePosts';
import { PostCard } from '@/app/components/social/PostCard';

export default function HomeScreen() {
    const { posts, loading, refreshing, likePost, unlikePost, refresh } = usePosts();

    const handleLike = (postId: string, isLiked: boolean) => {
        if (isLiked) {
            unlikePost(postId);
        } else {
            likePost(postId);
        }
    };

    const handleComment = (postId: string) => {
        // TODO: Navigate to comments screen
        console.log('Comment on post:', postId);
    };

    if (loading && !refreshing) {
        return (
            <View style={styles.center}>
                <Text>Chargement...</Text>
            </View>
        );
    }

    return (
        <View style={styles.container}>
            <FlatList
                data={posts}
                keyExtractor={(item) => item.id}
                renderItem={({ item }) => (
                    <PostCard
                        post={item}
                        onLike={() => handleLike(item.id, item.is_liked || false)}
                        onComment={() => handleComment(item.id)}
                    />
                )}
                refreshControl={
                    <RefreshControl refreshing={refreshing} onRefresh={refresh} />
                }
                ListEmptyComponent={
                    <View style={styles.center}>
                        <Text>Aucun post pour le moment</Text>
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
});