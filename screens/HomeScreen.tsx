import React, { useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    FlatList,
    TouchableOpacity,
    RefreshControl,
} from 'react-native';
import { usePosts } from '@/hooks/usePosts';
import { PostCard } from '@/components/social/PostCard';
import { CreatePostModal } from '@/components/social/CreatePostModal';
import { colors } from '@/lib/theme/colors';
import { spacing } from '@/lib/theme/spacing';
import { typography } from '@/lib/theme/typography';

export default function HomeScreen() {
    const { posts, loading, refreshing, refresh } = usePosts();
    const [showCreateModal, setShowCreateModal] = useState(false);

    return (
        <View style={styles.container}>
            <View style={styles.header}>
                <Text style={styles.title}>Le District</Text>
                <TouchableOpacity
                    style={styles.createButton}
                    onPress={() => setShowCreateModal(true)}
                >
                    <Text style={styles.createButtonText}>+ Publier</Text>
                </TouchableOpacity>
            </View>

            <FlatList
                data={posts}
                keyExtractor={(item) => item.id}
                renderItem={({ item }) => <PostCard post={item} />}
                contentContainerStyle={styles.list}
                refreshControl={
                    <RefreshControl
                        refreshing={refreshing}
                        onRefresh={refresh}
                        tintColor={colors.primary}
                    />
                }
                ListEmptyComponent={
                    !loading ? (
                        <View style={styles.empty}>
                            <Text style={styles.emptyText}>Aucune publication pour le moment</Text>
                            <Text style={styles.emptySubtext}>Soyez le premier à publier !</Text>
                        </View>
                    ) : null
                }
            />

            <CreatePostModal
                visible={showCreateModal}
                onClose={() => setShowCreateModal(false)}
            />
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: colors.backgroundSecondary,
    },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: spacing.base,
        backgroundColor: colors.white,
        borderBottomWidth: 1,
        borderBottomColor: colors.border,
    },
    title: {
        ...typography.h2,
        color: colors.primary,
    },
    createButton: {
        backgroundColor: colors.primary,
        paddingHorizontal: spacing.base,
        paddingVertical: spacing.sm,
        borderRadius: 20,
    },
    createButtonText: {
        ...typography.body2,
        color: colors.white,
        fontWeight: '600',
    },
    list: {
        padding: spacing.base,
    },
    empty: {
        alignItems: 'center',
        justifyContent: 'center',
        paddingVertical: spacing.xxxl,
    },
    emptyText: {
        ...typography.h3,
        color: colors.textSecondary,
        marginBottom: spacing.xs,
    },
    emptySubtext: {
        ...typography.body2,
        color: colors.textTertiary,
    },
});
