import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Post } from '@/lib/types';

interface PostCardProps {
    post: Post;
    onLike: () => void;
    onComment: () => void;
}

export const PostCard: React.FC<PostCardProps> = ({ post, onLike, onComment }) => {
    return (
        <View style={styles.card}>
            <View style={styles.header}>
                <Text style={styles.author}>{post.author?.full_name || 'Anonyme'}</Text>
                <Text style={styles.date}>
                    {new Date(post.created_at).toLocaleDateString('fr-FR')}
                </Text>
            </View>

            <Text style={styles.content}>{post.content}</Text>

            <View style={styles.actions}>
                <TouchableOpacity onPress={onLike} style={styles.action}>
                    <Text style={[styles.actionText, post.is_liked && styles.liked]}>
                        ❤️ {post.likes_count || 0}
                    </Text>
                </TouchableOpacity>

                <TouchableOpacity onPress={onComment} style={styles.action}>
                    <Text style={styles.actionText}>💬 {post.comments_count || 0}</Text>
                </TouchableOpacity>
            </View>
        </View>
    );
};

const styles = StyleSheet.create({
    card: {
        backgroundColor: '#fff',
        padding: 15,
        marginBottom: 10,
        borderRadius: 8,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.1,
        shadowRadius: 2,
        elevation: 2,
    },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: 10,
    },
    author: {
        fontWeight: 'bold',
        fontSize: 16,
    },
    date: {
        fontSize: 12,
        color: '#666',
    },
    content: {
        fontSize: 14,
        lineHeight: 20,
        marginBottom: 10,
    },
    actions: {
        flexDirection: 'row',
        justifyContent: 'space-around',
    },
    action: {
        padding: 10,
    },
    actionText: {
        fontSize: 14,
    },
    liked: {
        color: '#ff4444',
    },
});