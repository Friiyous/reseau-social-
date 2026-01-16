import React, { useState } from 'react';
import {
    View,
    Text,
    Image,
    StyleSheet,
    TouchableOpacity,
} from 'react-native';
import { formatDistanceToNow } from 'date-fns';
import { fr } from 'date-fns/locale';
import { Post } from '@/lib/types';
import { Avatar } from '@/components/ui/Avatar';
import { Card } from '@/components/ui/Card';
import CommentsList from '@/components/social/CommentsList';
import { usePosts } from '@/hooks/usePosts';
import { colors } from '@/lib/theme/colors';
import { spacing } from '@/lib/theme/spacing';
import { typography } from '@/lib/theme/typography';

interface PostCardProps {
    post: Post;
}

export const PostCard: React.FC<PostCardProps> = ({ post }) => {
    const { likePost, unlikePost } = usePosts();
    const [showComments, setShowComments] = useState(false);

    const handleLike = () => {
        if (post.is_liked) {
            unlikePost(post.id);
        } else {
            likePost(post.id);
        }
    };

    return (
        <Card style={styles.card}>
            <View style={styles.header}>
                <Avatar
                    uri={post.author?.avatar_url}
                    name={post.author?.full_name || 'Utilisateur'}
                    size={48}
                />
                <View style={styles.headerInfo}>
                    <Text style={styles.authorName}>{post.author?.full_name}</Text>
                    <Text style={styles.timestamp}>
                        {formatDistanceToNow(new Date(post.created_at), { addSuffix: true, locale: fr })}
                    </Text>
                </View>
            </View>

            <Text style={styles.content}>{post.content}</Text>

            {post.image_url && (
                <Image source={{ uri: post.image_url }} style={styles.image} />
            )}

            <View style={styles.actions}>
                <TouchableOpacity style={styles.actionButton} onPress={handleLike}>
                    <Text style={[styles.actionText, post.is_liked && styles.actionTextActive]}>
                        {post.is_liked ? '❤️' : '🤍'} {post.likes_count || 0}
                    </Text>
                </TouchableOpacity>

                <TouchableOpacity
                    style={styles.actionButton}
                    onPress={() => setShowComments(!showComments)}
                >
                    <Text style={styles.actionText}>
                        💬 {post.comments_count || 0}
                    </Text>
                </TouchableOpacity>
            </View>

            {showComments && <CommentsList postId={post.id} />}
        </Card>
    );
};

const styles = StyleSheet.create({
    card: {
        marginBottom: spacing.base,
    },
    header: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: spacing.md,
    },
    headerInfo: {
        marginLeft: spacing.md,
        flex: 1,
    },
    authorName: {
        ...typography.body1,
        fontWeight: '600',
        color: colors.textPrimary,
    },
    timestamp: {
        ...typography.caption,
        color: colors.textSecondary,
    },
    content: {
        ...typography.body1,
        color: colors.textPrimary,
        marginBottom: spacing.md,
    },
    image: {
        width: '100%',
        height: 200,
        borderRadius: 12,
        marginBottom: spacing.md,
        resizeMode: 'cover',
    },
    actions: {
        flexDirection: 'row',
        borderTopWidth: 1,
        borderTopColor: colors.borderLight,
        paddingTop: spacing.md,
    },
    actionButton: {
        flexDirection: 'row',
        alignItems: 'center',
        marginRight: spacing.lg,
    },
    actionText: {
        ...typography.body2,
        color: colors.textSecondary,
    },
    actionTextActive: {
        color: colors.error,
    },
});
