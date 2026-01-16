import React from 'react';
import { TouchableOpacity, Text, StyleSheet, TouchableOpacityProps } from 'react-native';

interface ButtonProps extends TouchableOpacityProps {
    title: string;
    variant?: 'primary' | 'secondary';
    loading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
    title,
    variant = 'primary',
    loading = false,
    style,
    disabled,
    ...props
}) => {
    const buttonStyle = [
        styles.button,
        variant === 'primary' ? styles.primary : styles.secondary,
        (disabled || loading) && styles.disabled,
        style,
    ];

    return (
        <TouchableOpacity
            style={buttonStyle}
            disabled={disabled || loading}
            {...props}
        >
            <Text style={[styles.text, variant === 'primary' ? styles.primaryText : styles.secondaryText]}>
                {loading ? 'Chargement...' : title}
            </Text>
        </TouchableOpacity>
    );
};

const styles = StyleSheet.create({
    button: {
        padding: 15,
        borderRadius: 8,
        alignItems: 'center',
        marginBottom: 15,
    },
    primary: {
        backgroundColor: '#007AFF',
    },
    secondary: {
        backgroundColor: 'transparent',
        borderWidth: 1,
        borderColor: '#007AFF',
    },
    disabled: {
        opacity: 0.6,
    },
    text: {
        fontSize: 16,
        fontWeight: 'bold',
    },
    primaryText: {
        color: '#fff',
    },
    secondaryText: {
        color: '#007AFF',
    },
});