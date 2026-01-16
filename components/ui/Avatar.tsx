import React from 'react';
import { View, Text, Image, StyleSheet } from 'react-native';
import { colors } from '@/lib/theme/colors';
import { typography } from '@/lib/theme/typography';

interface AvatarProps {
    uri?: string;
    name: string;
    size?: number;
}

export const Avatar: React.FC<AvatarProps> = ({ uri, name, size = 40 }) => {
    const getInitials = (fullName: string): string => {
        const names = fullName.trim().split(' ');
        if (names.length >= 2) {
            return `${names[0][0]}${names[names.length - 1][0]}`.toUpperCase();
        }
        return fullName.substring(0, 2).toUpperCase();
    };

    const fontSize = size * 0.4;

    return (
        <View style={[styles.container, { width: size, height: size, borderRadius: size / 2 }]}>
            {uri ? (
                <Image source={{ uri }} style={[styles.image, { width: size, height: size, borderRadius: size / 2 }]} />
            ) : (
                <Text style={[styles.initials, { fontSize }]}>{getInitials(name)}</Text>
            )}
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        backgroundColor: colors.primary,
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'hidden',
    },
    image: {
        resizeMode: 'cover',
    },
    initials: {
        color: colors.white,
        fontWeight: '600',
    },
});
