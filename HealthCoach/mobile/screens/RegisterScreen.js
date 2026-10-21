
import React, { useState } from 'react';
import {
  Modal,
  KeyboardAvoidingView,
  Platform,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { LinearGradient } from 'expo-linear-gradient';
import { Feather } from '@expo/vector-icons';
import { postApi } from '../services/api';

export default function RegisterScreen({ onBackToLogin }) {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [feedback, setFeedback] = useState({
    visible: false,
    type: 'success',
    title: '',
    message: '',
  });

  const handleRegister = async () => {
    if (isLoading) return;
    const nextErrors = {};

    if (!username.trim()) {
      nextErrors.username = 'Username wajib diisi.';
    }

    if (!email.trim()) {
      nextErrors.email = 'Email wajib diisi.';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      nextErrors.email = 'Format email tidak valid.';
    }

    if (!password) {
      nextErrors.password = 'Password wajib diisi.';
    } else if (password.length < 8) {
      nextErrors.password = 'Password minimal 8 karakter.';
    }

    if (!confirmPassword) {
      nextErrors.confirmPassword = 'Konfirmasi password wajib diisi.';
    } else if (password !== confirmPassword) {
      nextErrors.confirmPassword = 'Konfirmasi password tidak cocok.';
    }

    setErrors(nextErrors);

    if (Object.keys(nextErrors).length > 0) return;

    setIsLoading(true);

    try {
      await postApi('/auth/register/', {
        username: username.trim(),
        email: email.trim(),
        password,
      });

      setFeedback({
        visible: true,
        type: 'success',
        title: 'Registrasi berhasil!',
        message: 'Akun HealthCoach berhasil dibuat. Yuk, mulai perjalanan hidup sehatmu!',
      });
    } catch (error) {
      setFeedback({
        visible: true,
        type: 'error',
        title: 'Registrasi gagal',
        message: error.message || 'Tidak dapat terhubung ke server.',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar style="dark" />

      <LinearGradient
        colors={['#F3FBF8', '#E9F7F4', '#EFF6FD']}
        style={styles.background}
      >
        <KeyboardAvoidingView
          style={{ flex: 1 }}
          behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        >
          <ScrollView
            contentContainerStyle={styles.content}
            showsVerticalScrollIndicator={false}
            keyboardShouldPersistTaps="handled"
          >
            <TouchableOpacity
              style={styles.backButton}
              onPress={onBackToLogin}
            >
              <Feather name="arrow-left" size={19} color="#177D69" />
              <Text style={styles.backText}>Kembali ke Login</Text>
            </TouchableOpacity>

            <View style={styles.header}>
              <View style={styles.logo}>
                <Feather name="activity" size={22} color="#FFFFFF" />
              </View>

              <Text style={styles.brand}>HealthCoach</Text>
            </View>

            <Text style={styles.title}>Buat akun baru</Text>
            <Text style={styles.subtitle}>
              Mulai perjalanan hidup sehatmu bersama HealthCoach.
            </Text>

            <View style={styles.card}>
              <Text style={styles.label}>Username</Text>
              <View style={styles.inputRow}>
                <Feather name="user" size={18} color="#7A9990" />
                <TextInput
                  style={styles.input}
                  placeholder="Masukkan username"
                  placeholderTextColor="#9DAFA9"
                  autoCapitalize="none"
                  value={username}
                  onChangeText={setUsername}
                />
              </View>
              {errors.username ? (
                <Text style={styles.error}>{errors.username}</Text>
              ) : null}

              <Text style={styles.label}>Email</Text>
              <View style={styles.inputRow}>
                <Feather name="mail" size={18} color="#7A9990" />
                <TextInput
                  style={styles.input}
                  placeholder="nama@email.com"
                  placeholderTextColor="#9DAFA9"
                  autoCapitalize="none"
                  keyboardType="email-address"
                  value={email}
                  onChangeText={setEmail}
                />
              </View>
              {errors.email ? (
                <Text style={styles.error}>{errors.email}</Text>
              ) : null}

              <Text style={styles.label}>Password</Text>
              <View style={styles.inputRow}>
                <Feather name="lock" size={18} color="#7A9990" />
                <TextInput
                  style={styles.input}
                  placeholder="Minimal 8 karakter"
                  placeholderTextColor="#9DAFA9"
                  secureTextEntry={!showPassword}
                  value={password}
                  onChangeText={setPassword}
                />
                <TouchableOpacity
                  onPress={() => setShowPassword(!showPassword)}
                >
                  <Feather
                    name={showPassword ? 'eye-off' : 'eye'}
                    size={19}
                    color="#168A75"
                  />
                </TouchableOpacity>
              </View>
              {errors.password ? (
                <Text style={styles.error}>{errors.password}</Text>
              ) : null}

              <Text style={styles.label}>Konfirmasi Password</Text>
              <View style={styles.inputRow}>
                <Feather name="shield" size={18} color="#7A9990" />
                <TextInput
                  style={styles.input}
                  placeholder="Ulangi password"
                  placeholderTextColor="#9DAFA9"
                  secureTextEntry={!showPassword}
                  value={confirmPassword}
                  onChangeText={setConfirmPassword}
                />
              </View>
              {errors.confirmPassword ? (
                <Text style={styles.error}>
                  {errors.confirmPassword}
                </Text>
              ) : null}

              <TouchableOpacity
                onPress={handleRegister}
                disabled={isLoading}
                activeOpacity={0.85}
              >
                <LinearGradient
                  colors={['#138D76', '#2BAE96']}
                  style={styles.button}
                >
                  <Text style={styles.buttonText}>{isLoading ? "Memproses..." : "Daftar Akun"}</Text>
                  <Feather name="arrow-right" size={18} color="#FFF" />
                </LinearGradient>
              </TouchableOpacity>
            </View>

            <Text style={styles.footer}>
              HealthCoach © 2026
            </Text>
          </ScrollView>
        </KeyboardAvoidingView>
      </LinearGradient>

      <Modal
        visible={feedback.visible}
        transparent
        animationType="fade"
        onRequestClose={() =>
          setFeedback(prev => ({ ...prev, visible: false }))
        }
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalCard}>

            <View
              style={[
                styles.modalIconCircle,
                feedback.type === 'success'
                  ? styles.modalSuccessCircle
                  : styles.modalErrorCircle,
              ]}
            >
              <Feather
                name={feedback.type === 'success' ? 'check-circle' : 'alert-circle'}
                size={34}
                color={feedback.type === 'success' ? '#168A72' : '#D96868'}
              />
            </View>

            <Text style={styles.modalTitle}>
              {feedback.title}
            </Text>

            <Text style={styles.modalDescription}>
              {feedback.message}
            </Text>

            <TouchableOpacity
              style={styles.modalAction}
              activeOpacity={0.85}
              onPress={() => {
                const wasSuccess = feedback.type === 'success';

                setFeedback(prev => ({
                  ...prev,
                  visible: false,
                }));

                if (wasSuccess) {
                  onBackToLogin();
                }
              }}
            >
              <LinearGradient
                colors={['#138D76', '#2BAE96']}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
                style={styles.modalGradient}
              >
                <Text style={styles.modalButtonText}>
                  {feedback.type === 'success'
                    ? 'Lanjut ke Login'
                    : 'Coba Lagi'}
                </Text>

                <Feather
                  name={feedback.type === 'success' ? 'arrow-right' : 'refresh-cw'}
                  size={18}
                  color="#FFFFFF"
                />
              </LinearGradient>
            </TouchableOpacity>

          </View>
        </View>
      </Modal>

    </SafeAreaView>
  );
}

const styles = StyleSheet.create({

  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(20, 49, 44, 0.34)',
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 28,
  },
  modalCard: {
    width: '100%',
    maxWidth: 380,
    backgroundColor: '#FFFFFF',
    borderRadius: 28,
    paddingHorizontal: 26,
    paddingTop: 32,
    paddingBottom: 26,
    alignItems: 'center',
    shadowColor: '#164C40',
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.12,
    shadowRadius: 22,
    elevation: 10,
  },
  modalIconCircle: {
    width: 76,
    height: 76,
    borderRadius: 38,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
  },
  modalSuccessCircle: {
    backgroundColor: '#E0F5EC',
  },
  modalErrorCircle: {
    backgroundColor: '#FDECEC',
  },
  modalTitle: {
    fontSize: 23,
    fontWeight: '800',
    color: '#164C40',
    textAlign: 'center',
    marginBottom: 12,
  },
  modalDescription: {
    fontSize: 15,
    lineHeight: 23,
    color: '#69847B',
    textAlign: 'center',
    marginBottom: 26,
  },
  modalAction: {
    width: '100%',
    borderRadius: 16,
    overflow: 'hidden',
  },
  modalGradient: {
    minHeight: 54,
    paddingHorizontal: 18,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
    borderRadius: 16,
  },
  modalButtonText: {
    fontSize: 16,
    fontWeight: '700',
    color: '#FFFFFF',
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
    padding: 24,
    paddingBottom: 40,
  },
  backButton: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 25,
  },
  backText: {
    color: '#177D69',
    fontSize: 13,
    fontWeight: '700',
    marginLeft: 9,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 25,
  },
  logo: {
    width: 44,
    height: 44,
    borderRadius: 14,
    backgroundColor: '#168E75',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 11,
  },
  brand: {
    color: '#155748',
    fontSize: 19,
    fontWeight: '800',
  },
  title: {
    fontSize: 29,
    fontWeight: '800',
    color: '#123F36',
  },
  subtitle: {
    color: '#718B82',
    fontSize: 13,
    lineHeight: 21,
    marginTop: 10,
    marginBottom: 25,
  },
  card: {
    backgroundColor: 'rgba(255,255,255,0.94)',
    borderRadius: 23,
    padding: 22,
    borderWidth: 1,
    borderColor: '#E2EFE9',
  },
  label: {
    fontSize: 13,
    fontWeight: '700',
    color: '#365B50',
    marginBottom: 9,
  },
  inputRow: {
    height: 52,
    backgroundColor: '#F8FCFA',
    borderWidth: 1,
    borderColor: '#DDEBE5',
    borderRadius: 13,
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 14,
    marginBottom: 18,
  },
  input: {
    flex: 1,
    color: '#244A3E',
    fontSize: 14,
    marginHorizontal: 11,
  },
  error: {
    color: '#C95151',
    fontSize: 12,
    marginTop: -12,
    marginBottom: 14,
  },
  button: {
    height: 53,
    borderRadius: 13,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 6,
  },
  buttonText: {
    color: '#FFFFFF',
    fontWeight: '800',
    fontSize: 15,
    marginRight: 10,
  },
  footer: {
    textAlign: 'center',
    fontSize: 11,
    color: '#91A9A0',
    marginTop: 25,
  },
});
