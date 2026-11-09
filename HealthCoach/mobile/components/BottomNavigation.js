import React from 'react';
import {
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { Feather } from '@expo/vector-icons';

const GREEN = '#168A75';

const TABS = [
  { key: 'home', label: 'Beranda', icon: 'home' },
  { key: 'analysis', label: 'Analisis', icon: 'camera' },
  { key: 'history', label: 'Riwayat', icon: 'clock' },
  { key: 'profile', label: 'Profil', icon: 'user' },
];

export default function BottomNavigation({
  activeTab,
  onNavigate,
}) {
  return (
    <View style={styles.container}>
      {TABS.map((tab) => {
        const selected = activeTab === tab.key;

        return (
          <TouchableOpacity
            key={tab.key}
            activeOpacity={0.8}
            onPress={() => onNavigate?.(tab.key)}
            accessibilityRole="tab"
            accessibilityLabel={tab.label}
            accessibilityState={{ selected }}
            style={styles.tab}
          >
            <View
              style={[
                styles.iconBox,
                selected && styles.iconBoxActive,
              ]}
            >
              <Feather
                name={tab.icon}
                size={21}
                color={selected ? GREEN : '#849990'}
              />
            </View>

            <Text
              style={[
                styles.label,
                selected && styles.labelActive,
              ]}
            >
              {tab.label}
            </Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#E1F0EB',
    paddingHorizontal: 8,
    paddingTop: 10,
    paddingBottom: 8,
  },
  tab: {
    flex: 1,
    minHeight: 54,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 4,
  },
  iconBox: {
    width: 48,
    height: 32,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center',
  },
  iconBoxActive: {
    backgroundColor: '#E5F6EF',
  },
  label: {
    fontSize: 11,
    color: '#849990',
    fontWeight: '600',
  },
  labelActive: {
    color: GREEN,
    fontWeight: '800',
  },
});
