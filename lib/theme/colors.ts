export const colors = {
    // Couleurs principales africaines
    primary: '#FF6B35',      // Orange africain vibrant
    primaryLight: '#FF8A5C',
    primaryDark: '#E55A2B',

    secondary: '#2D5016',    // Vert forêt
    secondaryLight: '#3D6B21',
    secondaryDark: '#1D3A0E',

    // Couleurs de statut
    success: '#10B981',      // Vert succès
    warning: '#F59E0B',      // Jaune avertissement
    error: '#EF4444',        // Rouge erreur
    info: '#3B82F6',         // Bleu information

    // Nuances de gris
    gray50: '#F9FAFB',
    gray100: '#F3F4F6',
    gray200: '#E5E7EB',
    gray300: '#D1D5DB',
    gray400: '#9CA3AF',
    gray500: '#6B7280',
    gray600: '#4B5563',
    gray700: '#374151',
    gray800: '#1F2937',
    gray900: '#111827',

    // Backgrounds
    background: '#FFFFFF',
    backgroundSecondary: '#F9FAFB',

    // Texte
    textPrimary: '#111827',
    textSecondary: '#6B7280',
    textTertiary: '#9CA3AF',

    // Bordures
    border: '#E5E7EB',
    borderLight: '#F3F4F6',

    // Overlay
    overlay: 'rgba(0, 0, 0, 0.5)',

    // Blanc et noir
    white: '#FFFFFF',
    black: '#000000',
};

export type ColorKey = keyof typeof colors;
