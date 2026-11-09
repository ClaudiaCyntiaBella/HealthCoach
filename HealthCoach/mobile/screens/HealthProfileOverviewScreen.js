import React, { useEffect, useState } from 'react';
import {
  ActivityIndicator,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { Feather } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';

import { getHealthProfile } from '../services/healthProfile';

const GREEN = '#168A75';

const GENDERS = {
  male: 'Laki-laki',
  female: 'Perempuan',
  prefer_not_to_say: 'Tidak ingin menyebutkan',
};

const GOALS = {
  lose_weight: 'Menurunkan berat badan',
  maintain_weight: 'Menjaga berat badan',
  gain_weight: 'Meningkatkan berat badan',
  healthy_eating: 'Menjaga pola makan sehat',
};

const ACTIVITIES = {
  sedentary: 'Jarang bergerak',
  light: 'Aktivitas ringan',
  moderate: 'Aktivitas sedang',
  active: 'Aktif',
  very_active: 'Sangat aktif',
};

function displayNumber(value, unit) {
  if (value === null || value === undefined || value === '') {
    return 'Belum diisi';
  }

  const number = Number(value);

  if (!Number.isFinite(number)) {
    return 'Belum diisi';
  }

  return `${number.toLocaleString('id-ID', {
    maximumFractionDigits: 2,
  })} ${unit}`;
}

function displayDate(value) {
  if (!value) return 'Belum diisi';

  const parts = String(value).split('-');

  if (parts.length !== 3) return 'Belum diisi';

  const [year, month, day] = parts.map(Number);

  const date = new Date(Date.UTC(year, month - 1, day));

  if (
    Number.isNaN(date.getTime()) ||
    date.getUTCFullYear() !== year ||
    date.getUTCMonth() !== month - 1 ||
    date.getUTCDate() !== day
  ) {
    return 'Belum diisi';
  }

  return date.toLocaleDateString('id-ID', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    timeZone: 'UTC',
  });
}

function ProfileRow({ icon, label, value }) {
  return (
    <View style={styles.infoRow}>
      <View style={styles.infoIcon}>
        <Feather name={icon} size={18} color={GREEN} />
      </View>

      <View style={styles.infoContent}>
        <Text style={styles.infoLabel}>{label}</Text>
        <Text style={styles.infoValue}>{value}</Text>
      </View>
    </View>
  );
}

export default function HealthProfileOverviewScreen({
  onEditProfile,
}) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [retryKey, setRetryKey] = useState(0);

  useEffect(() => {
    let active = true;

    async function loadProfile() {
      setLoading(true);
      setError('');

      try {
        const data = await getHealthProfile();

        if (active) {
          setProfile(data || null);
        }
      } catch (err) {
        if (active) {
          setError(
            err.message || 'Gagal memuat profil kesehatan.'
          );
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadProfile();

    return () => {
      active = false;
    };
  }, [retryKey]);

  return (
    <SafeAreaView style={styles.safeArea}>
      <LinearGradient
        colors={['#F3FBF8', '#E9F7F4', '#EFF6FD']}
        style={styles.background}
      >
        <ScrollView
          contentContainerStyle={styles.content}
          showsVerticalScrollIndicator={false}
        >
          <View style={styles.header}>
            <View style={styles.headerText}>
              <Text style={styles.eyebrow}>
                YOUR HEALTH PROFILE
              </Text>
              <Text style={styles.title}>
                Profil Kesehatan
              </Text>
              <Text style={styles.description}>
                Informasi kesehatan pribadimu tersimpan
                dan dapat diperbarui kapan saja.
              </Text>
            </View>

            <View style={styles.headerIcon}>
              <Feather
                name="heart"
                size={25}
                color={GREEN}
              />
            </View>
          </View>

          {loading ? (
            <View style={styles.centerCard}>
              <ActivityIndicator
                size="large"
                color={GREEN}
              />
              <Text style={styles.muted}>
                Memuat informasi kesehatanmu...
              </Text>
            </View>
          ) : error ? (
            <View style={styles.centerCard}>
              <Feather
                name="alert-circle"
                size={35}
                color="#D96868"
              />

              <Text style={styles.emptyTitle}>
                Profil belum dapat dimuat
              </Text>

              <Text style={styles.muted}>
                {error}
              </Text>

              <TouchableOpacity
                style={styles.retryButton}
                onPress={() => setRetryKey((v) => v + 1)}
              >
                <Feather
                  name="refresh-cw"
                  size={17}
                  color={GREEN}
                />
                <Text style={styles.retryText}>
                  Coba Lagi
                </Text>
              </TouchableOpacity>
            </View>
          ) : !profile ? (
            <View style={styles.centerCard}>
              <View style={styles.emptyIcon}>
                <Feather
                  name="clipboard"
                  size={32}
                  color={GREEN}
                />
              </View>

              <Text style={styles.emptyTitle}>
                Lengkapi Profilmu
              </Text>

              <Text style={styles.muted}>
                Kamu belum memiliki profil kesehatan.
                Yuk, isi informasi tubuh dan tujuan nutrisimu.
              </Text>

              <TouchableOpacity
                activeOpacity={0.85}
                onPress={onEditProfile}
                style={styles.actionButton}
              >
                <LinearGradient
                  colors={['#138D76', '#2BAE96']}
                  style={styles.actionGradient}
                >
                  <Feather
                    name="plus-circle"
                    size={19}
                    color="#FFFFFF"
                  />
                  <Text style={styles.actionText}>
                    Lengkapi Profil
                  </Text>
                </LinearGradient>
              </TouchableOpacity>
            </View>
          ) : (
            <>
              <View style={styles.summaryCard}>
                <View style={styles.cardHeading}>
                  <Feather
                    name="activity"
                    size={19}
                    color={GREEN}
                  />
                  <Text style={styles.cardTitle}>
                    Informasi Tubuh
                  </Text>
                </View>

                <View style={styles.metricsRow}>
                  <View style={styles.metricBox}>
                    <Feather
                      name="trending-up"
                      size={21}
                      color={GREEN}
                    />
                    <Text style={styles.metricLabel}>
                      Tinggi Badan
                    </Text>
                    <Text style={styles.metricValue}>
                      {displayNumber(profile.height, 'cm')}
                    </Text>
                  </View>

                  <View style={styles.metricBox}>
                    <Feather
                      name="activity"
                      size={21}
                      color={GREEN}
                    />
                    <Text style={styles.metricLabel}>
                      Berat Badan
                    </Text>
                    <Text style={styles.metricValue}>
                      {displayNumber(profile.weight, 'kg')}
                    </Text>
                  </View>
                </View>
              </View>

              <View style={styles.summaryCard}>
                <View style={styles.cardHeading}>
                  <Feather
                    name="user"
                    size={19}
                    color={GREEN}
                  />
                  <Text style={styles.cardTitle}>
                    Detail Profil
                  </Text>
                </View>

                <ProfileRow
                  icon="users"
                  label="Jenis Kelamin"
                  value={
                    GENDERS[profile.gender] || 'Belum diisi'
                  }
                />

                <ProfileRow
                  icon="target"
                  label="Tujuan Nutrisi"
                  value={
                    GOALS[profile.nutrition_goal] ||
                    'Belum diisi'
                  }
                />

                <ProfileRow
                  icon="zap"
                  label="Tingkat Aktivitas"
                  value={
                    ACTIVITIES[profile.activity_level] ||
                    'Belum diisi'
                  }
                />

                <ProfileRow
                  icon="calendar"
                  label="Tanggal Lahir"
                  value={displayDate(profile.birth_date)}
                />
              </View>

              <TouchableOpacity
                activeOpacity={0.85}
                onPress={onEditProfile}
                style={styles.actionButton}
              >
                <LinearGradient
                  colors={['#138D76', '#2BAE96']}
                  style={styles.actionGradient}
                >
                  <Feather
                    name="edit-3"
                    size={19}
                    color="#FFFFFF"
                  />
                  <Text style={styles.actionText}>
                    Perbarui Profil
                  </Text>
                </LinearGradient>
              </TouchableOpacity>
            </>
          )}
        </ScrollView>
      </LinearGradient>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#F3FBF8',
  },
  background: {
    flex: 1,
  },
  content: {
    paddingHorizontal: 22,
    paddingTop: 26,
    paddingBottom: 36,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 25,
  },
  headerText: {
    flex: 1,
  },
  eyebrow: {
    color: GREEN,
    fontSize: 11,
    fontWeight: '800',
    letterSpacing: 1.7,
  },
  title: {
    color: '#173C35',
    fontSize: 29,
    fontWeight: '800',
    marginTop: 8,
  },
  description: {
    color: '#647D76',
    fontSize: 14,
    lineHeight: 22,
    marginTop: 9,
  },
  headerIcon: {
    width: 54,
    height: 54,
    borderRadius: 18,
    backgroundColor: '#DBF2E9',
    alignItems: 'center',
    justifyContent: 'center',
    marginLeft: 12,
  },
  summaryCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 22,
    borderWidth: 1,
    borderColor: '#E1F0EB',
    padding: 18,
    marginBottom: 18,
  },
  cardHeading: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 9,
    marginBottom: 18,
  },
  cardTitle: {
    color: '#24483F',
    fontSize: 17,
    fontWeight: '800',
  },
  metricsRow: {
    flexDirection: 'row',
    gap: 12,
  },
  metricBox: {
    flex: 1,
    minWidth: 0,
    borderRadius: 16,
    backgroundColor: '#EDF9F4',
    padding: 14,
    gap: 9,
  },
  metricLabel: {
    color: '#607A73',
    fontSize: 12,
  },
  metricValue: {
    color: '#164C40',
    fontWeight: '800',
    fontSize: 17,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 13,
    borderTopWidth: 1,
    borderTopColor: '#EDF3F0',
  },
  infoIcon: {
    width: 37,
    height: 37,
    borderRadius: 12,
    backgroundColor: '#EAF8F3',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  infoContent: {
    flex: 1,
    gap: 4,
  },
  infoLabel: {
    fontSize: 12,
    color: '#7A9087',
  },
  infoValue: {
    fontSize: 15,
    fontWeight: '700',
    color: '#24483F',
  },
  actionButton: {
    borderRadius: 15,
    overflow: 'hidden',
    marginTop: 5,
  },
  actionGradient: {
    minHeight: 54,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
    paddingHorizontal: 14,
  },
  actionText: {
    color: '#FFFFFF',
    fontSize: 15,
    fontWeight: '800',
  },
  centerCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 22,
    borderWidth: 1,
    borderColor: '#E1F0EB',
    padding: 26,
    alignItems: 'center',
    gap: 16,
  },
  emptyIcon: {
    width: 75,
    height: 75,
    borderRadius: 38,
    backgroundColor: '#E7F7F1',
    alignItems: 'center',
    justifyContent: 'center',
  },
  emptyTitle: {
    color: '#173C35',
    fontSize: 19,
    fontWeight: '800',
    textAlign: 'center',
  },
  muted: {
    color: '#647D76',
    fontSize: 14,
    lineHeight: 22,
    textAlign: 'center',
  },
  retryButton: {
    flexDirection: 'row',
    gap: 8,
    alignItems: 'center',
    padding: 12,
  },
  retryText: {
    color: GREEN,
    fontWeight: '800',
  },
});
