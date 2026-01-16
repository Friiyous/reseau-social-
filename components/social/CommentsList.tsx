import React, { useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    FlatList,
    TextInput,
    TouchableOpacity,
} from 'react-native';
import { useComments } from '@/hooks/useComments';
import { useAuth } from '@/lib/AuthContext';
import { Avatar } from '@/components/ui/Avatar';
import { colors } from '@/lib/theme/colors';
import { spacing } from '@/lib/theme/spacing';
import { typography } from '@/lib/theme/typography';
import { formatDistanceToNow } from 'date-fns';
import { fr } from 'date-fns/locale';

interface CommentsListProps {
    postId: string;
}

const CommentsList: React.FC<CommentsListProps> = ({ postId }) => {
    const { user } = useAuth();
    const { comments, addComment } = useComments(postId);
    const [newComment, setNewComment] = useState('');

    const handleSubmit = async () => {
        if (!newComment.trim() || !user) return;

        try {
            await addComment(newComment, user.id);
            setNewComment('');
        } catch (error) {
            console.error('Error adding comment:', error);
        }
    };

    return (
        <View style={styles.container}>
            <View style={styles.inputContainer}>
                <TextInput
                    style={styles.input}
                    placeholder="Ajouter un commentaire..."
                    placeholderTextColor={colors.gray400}
                    value={newComment}
                    onChangeText={setNewComment}
                />
                <TouchableOpacity
                    style={styles.sendButton}
                    onPress={handleSubmit}
                    disabled={!newComment.trim()}
                >
                    <Text style={styles.sendButtonText}>➤</Text>
                </TouchableOpacity>
            </View>

            <FlatList
                data={comments}
                keyExtractor={(item) => item.id}
                renderItem={({ item }) => (
                    <View style={styles.comment}>
                        <Avatar
                            uri={item.author?.avatar_url}
                            name={item.author?.full_name || 'Utilisateur'}
                            size={32}
                        />
                        <View style={styles.commentContent}>
                            <Text style={styles.commentAuthor}>{item.author?.full_name}</Text>
                            <Text style={styles.commentText}>{item.content}</Text>
                            <Text style={styles.commentTime}>
                                {formatDistanceToNow(new Date(item.created_at), { addSuffix: true, locale: fr })}
                            </Text>
                        </View>
                    </View>
                )}
                scrollEnabled={false}
            />
        </View>
    );
};

export default CommentsList;

const styles = StyleSheet.create({
    container: {
        marginTop: spacing.md,
        borderTopWidth: 1,
        borderTopColor: colors.borderLight,
        paddingTop: spacing.md,
    },
    inputContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: spacing.md,
    },
    input: {
        flex: 1,
        ...typography.body2,
        backgroundColor: colors.backgroundSecondary,
        borderRadius: 20,
        paddingHorizontal: spacing.base,
        paddingVertical: spacing.sm,
        marginRight: spacing.sm,
        color: colors.textPrimary,
    },
    sendButton: {
        width: 36,
        height: 36,
        borderRadius: 18,
        backgroundColor: colors.primary,
        alignItems: 'center',
        justifyContent: 'center',
    },
    sendButtonText: {
        color: colors.white,
        fontSize: 18,
    },
    comment: {
        flexDirection: 'row',
        marginBottom: spacing.md,
    },
    commentContent: {
        flex: 1,
        marginLeft: spacing.sm,
        backgroundColor: colors.backgroundSecondary,
        borderRadius: 12,
        padding: spacing.md,
    },
    commentAuthor: {
        ...typography.body2,
        fontWeight: '600',
        color: colors.textPrimary,
        marginBottom: spacing.xs,
    },
    commentText: {
        ...typography.body2,
        color: colors.textPrimary,
        marginBottom: spacing.xs,
    },
    commentTime: {
        ...typography.caption,
        color: colors.textSecondary,
    },
});
