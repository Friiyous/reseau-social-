import { Tabs } from 'expo-router';
import { Text } from 'react-native';
import { colors } from '@/lib/theme/colors';

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.gray400,
        tabBarStyle: {
          backgroundColor: colors.white,
          borderTopColor: colors.border,
          paddingTop: 5,
          paddingBottom: 5,
          height: 60,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '500',
        },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: 'Accueil',
          tabBarLabel: 'Accueil',
          tabBarIcon: ({ color, focused }) => (
            <Text style={{ fontSize: 20, opacity: focused ? 1 : 0.7 }}>🏠</Text>
          ),
        }}
      />
      <Tabs.Screen
        name="messages"
        options={{
          title: 'Messages',
          tabBarLabel: 'Messages',
          tabBarIcon: ({ color, focused }) => (
            <Text style={{ fontSize: 20, opacity: focused ? 1 : 0.7 }}>💬</Text>
          ),
        }}
      />
      <Tabs.Screen
        name="directory"
        options={{
          title: 'Annuaire',
          tabBarLabel: 'Annuaire',
          tabBarIcon: ({ color, focused }) => (
            <Text style={{ fontSize: 20, opacity: focused ? 1 : 0.7 }}>📋</Text>
          ),
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Profil',
          tabBarLabel: 'Profil',
          tabBarIcon: ({ color, focused }) => (
            <Text style={{ fontSize: 20, opacity: focused ? 1 : 0.7 }}>👤</Text>
          ),
        }}
      />
    </Tabs>
  );
}
