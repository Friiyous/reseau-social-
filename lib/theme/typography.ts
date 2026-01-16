export const typography = {
    display: {
        fontSize: 57,
        lineHeight: 64,
        fontWeight: '700' as const,
    },
    h1: {
        fontSize: 36,
        lineHeight: 44,
        fontWeight: '700' as const,
    },
    h2: {
        fontSize: 30,
        lineHeight: 38,
        fontWeight: '600' as const,
    },
    h3: {
        fontSize: 26,
        lineHeight: 34,
        fontWeight: '600' as const,
    },
    h4: {
        fontSize: 22,
        lineHeight: 30,
        fontWeight: '600' as const,
    },
    body1: {
        fontSize: 16,
        lineHeight: 24,
        fontWeight: '400' as const,
    },
    body2: {
        fontSize: 14,
        lineHeight: 20,
        fontWeight: '400' as const,
    },
    caption: {
        fontSize: 12,
        lineHeight: 16,
        fontWeight: '400' as const,
    },
    button: {
        fontSize: 16,
        lineHeight: 24,
        fontWeight: '600' as const,
    },
};

export type TypographyKey = keyof typeof typography;
