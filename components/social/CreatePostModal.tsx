import React, { useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    Modal,
    TextInput,
    TouchableOpacity,
    Alert,
    Image,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { usePosts } from '@/hooks/usePosts';
import { Button } from '@/components/ui/Button';
import { colors } from '@/lib/theme/colors';
import { spacing } from '@/lib/theme/spacing';
import { typography } from '@/lib/theme/typography';

interface CreatePostModalProps {
    visible: boolean;
    onClose: () => void;
}

export const CreatePostModal: React.FC<CreatePostModalProps> = ({ visible, onClose }) => {
    const { createPost } = usePosts();
    const [content, setContent] = useState('');
    const [imageUri, setImageUri] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const pickImage = async () => {
        const result = await ImagePicker.launchImageLibraryAsync({
            mediaTypes: ImagePicker.MediaTypeOptions.Images,
            allowsEditing: true,
            aspect: [4, 3],
            quality: 0.8,
        });

        if (!result.canceled) {
            setImageUri(result.assets[0].uri);
        }
    };

    const handleSubmit = async () => {
        if (!content.trim()) {
            Alert.alert('Erreur', 'Veuillez saisir du contenu');
            return;
        }

        setLoading(true);
        try {
            // TODO: Upload image to Supabase Storage if imageUri exists
            await createPost(content, imageUri || undefined);
            setContent('');
            setImageUri(null);
            onClose();
        } catch (error: any) {
            Alert.alert('Erreur', error.message || 'Impossible de créer la publication');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Modal
            visible={visible}
            animationType="slide"
            transparent
            onRequestClose={onClose}
        >
            <View style={styles.overlay}>
                <View style={styles.modal}>
                    <View style={styles.header}>
                        <Text style={styles.title}>Nouvelle publication</Text>
                        <TouchableOpacity onPress={onClose}>
                            <Text style={styles.closeButton}>✕</Text>
                        </TouchableOpacity>
                    </View>

                    <TextInput
                        style={styles.input}
                        placeholder="Quoi de neuf ?"
                        placeholderTextColor={colors.gray400}
                        multiline
                        value={content}
                        onChangeText={setContent}
                        maxLength={500}
                    />

                    {imageUri && (
                        <View style={styles.imageContainer}>
                            <Image source={{ uri: imageUri }} style={styles.image} />
                            <TouchableOpacity
                                style={styles.removeImage}
                                onPress={() => setImageUri(null)}
                            >
                                <Text style={styles.removeImageText}>✕</Text>
                            </TouchableOpacity>
                        </View>
                    )}

                    <View style={styles.actions}>
                        <TouchableOpacity style={styles.imageButton} onPress={pickImage}>
                            <Text style={styles.imageButtonText}>📷 Photo</Text>
                        </TouchableOpacity>

                        <Button
                            title="Publier"
                            onPress={handleSubmit}
                            loading={loading}
                            disabled={!content.trim()}
                        />
                    </View>
                </View>
            </View>
        </Modal>
    );
};

const styles = StyleSheet.create({
    overlay: {
        flex: 1,
        backgroundColor: colors.overlay,
        justifyContent: 'flex-end',
    },
    modal: {
        backgroundColor: colors.white,
        borderTopLeftRadius: 24,
        borderTopRightRadius: 24,
        padding: spacing.lg,
        maxHeight: '80%',
    },
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: spacing.base,
    },
    title: {
        ...typography.h3,
        color: colors.textPrimary,
    },
    closeButton: {
        ...typography.h2,
        color: colors.textSecondary,
    },
    input: {
        ...typography.body1,
        minHeight: 120,
        textAlignVertical: 'top',
        marginBottom: spacing.base,
        color: colors.textPrimary,
    },
    imageContainer: {
        position: 'relative',
        marginBottom: spacing.base,
    },
    image: {
        width: '100%',
        height: 200,
        borderRadius: 12,
        resizeMode: 'cover',
    },
    removeImage: {
        position: 'absolute',
        top: spacing.sm,
        right: spacing.sm,
        backgroundColor: colors.overlay,
        width: 32,
        height: 32,
        borderRadius: 16,
        alignItems: 'center',
        justifyContent: 'center',
    },
    removeImageText: {
        color: colors.white,
        fontSize: 18,
    },
    actions: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    imageButton: {
        padding: spacing.md,
    },
    imageButtonText: {
        ...typography.body1,
        color: colors.primary,
    },
});
