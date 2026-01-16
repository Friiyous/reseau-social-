import React from 'react';
import { View, StyleSheet, ViewStyle } from 'react-native';
import { colors } from '@/lib/theme/colors';
import { spacing } from '@/lib/theme/spacing';

interface CardProps {
    children: React.ReactNode;
    style?: ViewStyle;
}

export const Card: React.FC<CardProps> = ({ children, style }) => {
    return (
        <View style={[styles.card, style]}>
            {children}
        </View>
    );
};

const styles = StyleSheet.create({
    card: {
        backgroundColor: colors.white,
        borderRadius: 16,
        padding: spacing.base,
        shadowColor: colors.black,
        shadowOffset: {
            width: 0,
            height: 2,
        },
        shadowOpacity: 0.1,
        shadowRadius: 8,
        elevation: 3,
    },
});
