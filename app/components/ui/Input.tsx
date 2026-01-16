import React from 'react';
import { TextInput, Text, StyleSheet, TextInputProps } from 'react-native';

interface InputProps extends TextInputProps {
    error?: string;
}

export const Input: React.FC<InputProps> = ({ error, style, ...props }) => {
    return (
        <>
            <TextInput
                style={[styles.input, error && styles.inputError, style]}
                {...props}
            />
            {error && <Text style={styles.errorText}>{error}</Text>}
        </>
    );
};

const styles = StyleSheet.create({
    input: {
        borderWidth: 1,
        borderColor: '#ddd',
        padding: 15,
        marginBottom: 15,
        borderRadius: 8,
        fontSize: 16,
        backgroundColor: '#fff',
    },
    inputError: {
        borderColor: '#ff4444',
    },
    errorText: {
        color: '#ff4444',
        fontSize: 14,
        marginBottom: 15,
    },
});