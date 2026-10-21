import React, { useState } from 'react';
import {
  Modal,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { LinearGradient } from 'expo-linear-gradient';
import { Feather } from '@expo/vector-icons';
import { logoutUser } from '../services/auth';

export default function HomeScreen({ onLogout, onStartAnalysis }) {
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [logoutDialog, setLogoutDialog] = useState(null);
  const [logoutError, setLogoutError] = useState('');

  const handleLogout = () => {
    if (isLoggingOut) return;
    setLogoutError('');
    setLogoutDialog('confirm');
  };

  const confirmLogout = async () => {
    if (isLoggingOut) return;

    setIsLoggingOut(true);

    try {
      await logoutUser();
      setLogoutDialog(null);
      onLogout();
    } catch (error) {
      setLogoutError(
        error.message || 'Tidak dapat menghubungi server.'
      );
      setLogoutDialog('error');
    } finally {
      setIsLoggingOut(false);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar style="dark" />

      <LinearGradient
        colors={['#F3FBF8', '#E9F7F4', '#EFF6FD']}
        style={styles.background}
      >
        <ScrollView contentContainerStyle={styles.content}>
          <View style={styles.header}>
            <View style={styles.brand}>
              <View style={styles.logo}>
                <Feather name="activity" size={27} color="#FFFFFF" />
              </View>

              <View>
                <Text style={styles.brandName}>HealthCoach</Text>
                <Text style={styles.brandSubtitle}>
                  AI Nutrition Companion
                </Text>
              </View>
            </View>

            <TouchableOpacity
              style={styles.logoutButton}
              onPress={handleLogout}
              disabled={isLoggingOut}
              accessibilityLabel="Logout dari HealthCoach"
            >
              <Feather name="log-out" size={21} color="#168A75" />
            </TouchableOpacity>
          </View>

          <View style={styles.welcome}>
            <Text style={styles.eyebrow}>YOUR WELLNESS JOURNEY</Text>
            <Text style={styles.title}>
              Mulai perjalanan{' '}
              <Text style={styles.titleAccent}>sehatmu.</Text>
            </Text>
            <Text style={styles.description}>
              Kenali makananmu dan pahami informasi nutrisinya
              dengan bantuan teknologi AI.
            </Text>
          </View>

          <View style={styles.card}>
            <View style={styles.iconCircle}>
              <Feather name="camera" size={30} color="#168A75" />
            </View>

            <Text style={styles.cardTitle}>Analisis Makanan</Text>
            <Text style={styles.cardDescription}>
              Unggah foto makanan untuk memperoleh identifikasi,
              informasi nutrisi, dan rekomendasi dari HealthCoach.
            </Text>

            <TouchableOpacity
              activeOpacity={0.85}
              onPress={onStartAnalysis}
              disabled={!onStartAnalysis}
            >
              <LinearGradient
                colors={['#138D76', '#2BAE96']}
                style={styles.primaryButton}
              >
                <Text style={styles.primaryButtonText}>
                  Mulai Analisis
                </Text>
                <Feather
                  name="arrow-right"
                  size={19}
                  color="#FFFFFF"
                />
              </LinearGradient>
            </TouchableOpacity>
          </View>

          <View style={styles.note}>
            <Feather name="shield" size={19} color="#168A75" />
            <Text style={styles.noteText}>
              Akun kamu sudah terautentikasi melalui HealthCoach API.
            </Text>
          </View>

          <Text style={styles.footer}>HealthCoach © 2026</Text>
        </ScrollView>
      </LinearGradient>

      <Modal
        visible={logoutDialog !== null}
        transparent
        animationType="fade"
        onRequestClose={() => {
          if (!isLoggingOut) setLogoutDialog(null);
        }}
      >
        <View style={styles.logoutModalOverlay}>
          <View style={styles.logoutModalCard}>
            <View
              style={[
                styles.logoutModalIcon,
                logoutDialog === 'error' && styles.logoutModalErrorIcon,
              ]}
            >
              <Feather
                name={logoutDialog === 'error' ? 'alert-circle' : 'log-out'}
                size={32}
                color={logoutDialog === 'error' ? '#D96868' : '#168A75'}
              />
            </View>

            <Text style={styles.logoutModalTitle}>
              {logoutDialog === 'error'
                ? 'Logout gagal'
                : 'Keluar dari HealthCoach?'}
            </Text>

            <Text style={styles.logoutModalDescription}>
              {logoutDialog === 'error'
                ? logoutError
                : 'Sesi akun kamu akan diakhiri. Yakin ingin keluar?'}
            </Text>

            {logoutDialog === 'confirm' ? (
              <View style={styles.logoutModalActions}>
                <TouchableOpacity
                  style={styles.logoutCancelButton}
                  disabled={isLoggingOut}
                  onPress={() => setLogoutDialog(null)}
                  activeOpacity={0.85}
                >
                  <Text style={styles.logoutCancelText}>Batal</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={styles.logoutConfirmButton}
                  disabled={isLoggingOut}
                  onPress={confirmLogout}
                  activeOpacity={0.85}
                >
                  <LinearGradient
                    colors={['#138D76', '#2BAE96']}
                    style={styles.logoutGradient}
                  >
                    <Text style={styles.logoutConfirmText}>
                      {isLoggingOut ? 'Memproses...' : 'Ya, Logout'}
                    </Text>
                  </LinearGradient>
                </TouchableOpacity>
              </View>
            ) : (
              <TouchableOpacity
                style={styles.logoutFullButton}
                activeOpacity={0.85}
                onPress={() => setLogoutDialog(null)}
              >
                <LinearGradient
                  colors={['#138D76', '#2BAE96']}
                  style={styles.logoutGradient}
                >
                  <Text style={styles.logoutConfirmText}>Tutup</Text>
                </LinearGradient>
              </TouchableOpacity>
            )}
          </View>
        </View>
      </Modal>

    </SafeAreaView>
  );
}

const styles = StyleSheet.create({

  logoutModalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(20, 49, 44, 0.34)',
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 28,
  },
  logoutModalCard: {
    width: '100%',
    maxWidth: 380,
    backgroundColor: '#FFFFFF',
    borderRadius: 28,
    paddingHorizontal: 24,
    paddingTop: 30,
    paddingBottom: 26,
    alignItems: 'center',
    shadowColor: '#164C40',
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.12,
    shadowRadius: 22,
    elevation: 10,
  },
  logoutModalIcon: {
    width: 76,
    height: 76,
    borderRadius: 38,
    backgroundColor: '#E0F5EC',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 20,
  },
  logoutModalErrorIcon: {
    backgroundColor: '#FDECEC',
  },
  logoutModalTitle: {
    fontSize: 22,
    fontWeight: '800',
    color: '#164C40',
    textAlign: 'center',
    marginBottom: 12,
  },
  logoutModalDescription: {
    fontSize: 15,
    lineHeight: 23,
    color: '#69847B',
    textAlign: 'center',
    marginBottom: 26,
  },
  logoutModalActions: {
    width: '100%',
    flexDirection: 'row',
    gap: 12,
  },
  logoutCancelButton: {
    flex: 1,
    minHeight: 54,
    borderRadius: 16,
    backgroundColor: '#EAF4F0',
    alignItems: 'center',
    justifyContent: 'center',
  },
  logoutCancelText: {
    color: '#168A75',
    fontWeight: '700',
    fontSize: 15,
  },
  logoutConfirmButton: {
    flex: 1.4,
    borderRadius: 16,
    overflow: 'hidden',
  },
  logoutFullButton: {
    width: '100%',
    borderRadius: 16,
    overflow: 'hidden',
  },
  logoutGradient: {
    minHeight: 54,
    paddingHorizontal: 10,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
  },
  logoutConfirmText: {
    color: '#FFFFFF',
    fontSize: 15,
    fontWeight: '700',
    textAlign: 'center',
  },

  safeArea: {
    flex: 1,
    backgroundColor: '#F3FBF8',
  },
  background: {
    flex: 1,
  },
  content: {
    flexGrow: 1,
    paddingHorizontal: 24,
    paddingTop: 26,
    paddingBottom: 36,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  brand: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  logo: {
    width: 49,
    height: 49,
    borderRadius: 16,
    backgroundColor: '#168F78',
    alignItems: 'center',
    justifyContent: 'center',
  },
  brandName: {
    fontSize: 21,
    fontWeight: '800',
    color: '#164C40',
  },
  brandSubtitle: {
    fontSize: 12,
    color: '#7C948B',
    marginTop: 2,
  },
  logoutButton: {
    width: 46,
    height: 46,
    borderRadius: 15,
    backgroundColor: '#E0F5EC',
    alignItems: 'center',
    justifyContent: 'center',
  },
  welcome: {
    marginTop: 62,
    marginBottom: 34,
  },
  eyebrow: {
    fontSize: 12,
    fontWeight: '800',
    letterSpacing: 2,
    color: '#168A75',
    marginBottom: 18,
  },
  title: {
    fontSize: 37,
    lineHeight: 46,
    fontWeight: '800',
    color: '#164C40',
  },
  titleAccent: {
    color: '#168F78',
  },
  description: {
    marginTop: 17,
    fontSize: 16,
    lineHeight: 25,
    color: '#718B82',
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 28,
    padding: 25,
    borderWidth: 1,
    borderColor: '#E1ECE7',
  },
  iconCircle: {
    width: 66,
    height: 66,
    borderRadius: 22,
    backgroundColor: '#E0F5EC',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 22,
  },
  cardTitle: {
    fontSize: 24,
    fontWeight: '800',
    color: '#164C40',
    marginBottom: 11,
  },
  cardDescription: {
    fontSize: 15,
    color: '#718B82',
    lineHeight: 24,
    marginBottom: 26,
  },
  primaryButton: {
    borderRadius: 17,
    minHeight: 55,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 12,
  },
  primaryButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '700',
  },
  note: {
    marginTop: 22,
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 6,
    gap: 11,
  },
  noteText: {
    flex: 1,
    color: '#718B82',
    fontSize: 13,
    lineHeight: 20,
  },
  footer: {
    marginTop: 'auto',
    paddingTop: 44,
    color: '#9AADA6',
    textAlign: 'center',
    fontSize: 12,
  },
});
