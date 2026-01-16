export const HEALTH_CATEGORIES = [
    {
        id: 'nurse',
        name: 'Infirmier(ère)',
        icon: '💉',
    },
    {
        id: 'doctor',
        name: 'Médecin',
        icon: '👨‍⚕️',
    },
    {
        id: 'community-agent',
        name: 'Agent de santé communautaire',
        icon: '🏥',
    },
    {
        id: 'administrator',
        name: 'Administrateur de district',
        icon: '📋',
    },
];

export type HealthCategory = typeof HEALTH_CATEGORIES[number];
