import React from 'react';
import { TouchableOpacity, Text, StyleSheet, ActivityIndicator, ViewStyle, TextStyle } from 'react-native';
import { colors } from '@/lib/theme/colors';
import { spacing } from '@/lib/theme/spacing';
import { typography } from '@/lib/theme/typography';

interface ButtonProps {
    title: string;
    onPress: () => void;
    variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
    disabled?: boolean;
    loading?: boolean;
    fullWidth?: boolean;
    style?: ViewStyle;
}

const Button: React.FC<ButtonProps> = ({
    title,
    onPress,
    variant = 'primary',
    disabled = false,
    loading = false,
    fullWidth = false,
    style,
}) => {
    const getButtonStyle = (): ViewStyle => {
        const baseStyle: ViewStyle = {
            paddingVertical: spacing.md,
            paddingHorizontal: spacing.lg,
            borderRadius: 12,
            alignItems: 'center',
            justifyContent: 'center',
            flexDirection: 'row',
        };

        if (fullWidth) {
            baseStyle.width = '100%';
        }

        switch (variant) {
            case 'primary':
                return { ...baseStyle, backgroundColor: colors.primary };
            case 'secondary':
                return { ...baseStyle, backgroundColor: colors.secondary };
            case 'outline':
                return { ...baseStyle, backgroundColor: 'transparent', borderWidth: 2, borderColor: colors.primary };
            case 'ghost':
                return { ...baseStyle, backgroundColor: 'transparent' };
            default:
                return baseStyle;
        }
    };

    const getTextStyle = (): TextStyle => {
        const baseStyle: TextStyle = {
            ...typography.button,
        };

        switch (variant) {
            case 'primary':
            case 'secondary':
                return { ...baseStyle, color: colors.white };
            case 'outline':
            case 'ghost':
                return { ...baseStyle, color: colors.primary };
            default:
                return baseStyle;
        }
    };

    return (
        <TouchableOpacity
            style={[
                getButtonStyle(),
                disabled && styles.disabled,
                style,
            ]}
            onPress={onPress}
            disabled={disabled || loading}
            activeOpacity={0.7}
        >
            {loading ? (
                <ActivityIndicator color={variant === 'primary' || variant === 'secondary' ? colors.white : colors.primary} />
            ) : (
                <Text style={getTextStyle()}>{title}</Text>
            )}
        </TouchableOpacity>
    );
};

const styles = StyleSheet.create({
    disabled: {
        opacity: 0.5,
    },
});

export default Button;
