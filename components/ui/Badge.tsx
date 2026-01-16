import React from 'react';
import { View, Text, StyleSheet, ViewStyle } from 'react-native';
import { colors } from '@/lib/theme/colors';
import { spacing } from '@/lib/theme/spacing';
import { typography } from '@/lib/theme/typography';

interface BadgeProps {
    count: number;
    variant?: 'primary' | 'error' | 'success';
    style?: ViewStyle;
}

export const Badge: React.FC<BadgeProps> = ({ count, variant = 'primary', style }) => {
    if (count === 0) return null;

    const getBackgroundColor = () => {
        switch (variant) {
            case 'error':
                return colors.error;
            case 'success':
                return colors.success;
            default:
                return colors.primary;
        }
    };

    return (
        <View style={[styles.badge, { backgroundColor: getBackgroundColor() }, style]}>
            <Text style={styles.text}>{count > 99 ? '99+' : count}</Text>
        </View>
    );
};

const styles = StyleSheet.create({
    badge: {
        minWidth: 20,
        height: 20,
        borderRadius: 10,
        alignItems: 'center',
        justifyContent: 'center',
        paddingHorizontal: spacing.xs,
    },
    text: {
        ...typography.caption,
        color: colors.white,
        fontWeight: '700',
        fontSize: 10,
    },
});
