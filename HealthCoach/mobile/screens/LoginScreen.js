
import React, { useEffect, useRef, useState } from 'react';
import {
  Modal,
  Animated,
  Easing,
  KeyboardAvoidingView,
  Platform,
  SafeAreaView,
  ScrollView,
  StatusBar as NativeStatusBar,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';

import { StatusBar } from 'expo-status-bar';
import { LinearGradient } from 'expo-linear-gradient';
import { Feather } from '@expo/vector-icons';
import * as SecureStore from 'expo-secure-store';
import { postApi } from '../services/api';

export default function LoginScreen({ onGoToRegister, onLoginSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [usernameError, setUsernameError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [feedback, setFeedback] = useState({
    visible: false,
    type: 'success',
    title: '',
    message: '',
  });
  const [passwordError, setPasswordError] = useState('');

  // Animasi latar belakang HealthCoach Aero
  const motion = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    const animation = Animated.loop(
      Animated.sequence([
        Animated.timing(motion, {
          toValue: 1,
          duration: 6000,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
        Animated.timing(motion, {
          toValue: 0,
          duration: 6000,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
      ])
    );

    animation.start();

    return () => animation.stop();
  }, [motion]);

  const glowMovement = motion.interpolate({
    inputRange: [0, 1],
    outputRange: [0, 24],
  });

  const glowOpacity = motion.interpolate({
    inputRange: [0, 1],
    outputRange: [0.35, 0.65],
  });

  // Validasi username sesuai API Django
  const validateUsername = (value) => {
    if (!value.trim()) {
      return 'Username wajib diisi.';
    }
    return '';
  };

  // Validasi password
  const validatePassword = (value) => {
    if (!value) {
      return 'Password wajib diisi.';
    }

    if (value.length < 8) {
      return 'Password minimal 8 karakter.';
    }

    return '';
  };

  // Autentikasi menggunakan Django REST API + JWT
  const handleLogin = async () => {
    if (isLoading) return;

    const usernameMessage = validateUsername(username);
    const passwordMessage = validatePassword(password);

    setUsernameError(usernameMessage);
    setPasswordError(passwordMessage);

    if (usernameMessage || passwordMessage) return;

    setIsLoading(true);

    try {
      const result = await postApi('/auth/login/', {
        username: username.trim(),
        password,
      });

      // Mendukung respons SimpleJWT standar atau data wrapper.
      const tokens = result.data || result;
      const access = tokens.access;
      const refresh = tokens.refresh;

      if (
        typeof access !== 'string' ||
        typeof refresh !== 'string' ||
        !access ||
        !refresh
      ) {
        throw new Error(
          'Login diterima, tetapi token JWT tidak ditemukan pada respons.'
        );
      }

      await SecureStore.setItemAsync('hc_access_token', access);
      await SecureStore.setItemAsync('hc_refresh_token', refresh);

      setPassword('');

      setFeedback({
        visible: true,
        type: 'success',
        title: 'Login berhasil!',
        message: 'Selamat datang di HealthCoach.',
      });
    } catch (error) {
      setFeedback({
        visible: true,
        type: 'error',
        title: 'Login gagal',
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
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.background}
      >
        {/* Efek cahaya bergerak lembut */}
        <View
          pointerEvents="none"
          style={StyleSheet.absoluteFill}
        >
          <Animated.View
            style={[
              styles.glowOne,
              {
                opacity: glowOpacity,
                transform: [{ translateY: glowMovement }],
              },
            ]}
          />

          <Animated.View
            style={[
              styles.glowTwo,
              {
                opacity: glowOpacity,
                transform: [
                  {
                    translateY: Animated.multiply(
                      glowMovement,
                      -0.6
                    ),
                  },
                ],
              },
            ]}
          />
        </View>

        <KeyboardAvoidingView
          style={styles.flex}
          behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        >
          <ScrollView
            showsVerticalScrollIndicator={false}
            keyboardShouldPersistTaps="handled"
            contentContainerStyle={styles.content}
          >
            {/* Identitas aplikasi */}
            <View style={styles.brandRow}>
              <LinearGradient
                colors={['#10886F', '#28AD95']}
                style={styles.logo}
              >
                <Feather
                  name="activity"
                  size={23}
                  color="#FFFFFF"
                />
              </LinearGradient>

              <View style={styles.brandText}>
                <Text style={styles.brandName}>
                  HealthCoach
                </Text>

                <Text style={styles.brandCaption}>
                  AI Nutrition Companion
                </Text>
              </View>

              <View style={styles.aiBadge}>
                <View style={styles.aiDot} />
                <Text style={styles.aiText}>AI</Text>
              </View>
            </View>

            {/* Headline */}
            <View style={styles.intro}>
              <View style={styles.eyebrowRow}>
                <View style={styles.eyebrowLine} />

                <Text style={styles.eyebrow}>
                  YOUR WELLNESS JOURNEY
                </Text>
              </View>

              <Text style={styles.headline}>
                Mulai hidup sehat,{'\n'}
                <Text style={styles.headlineAccent}>
                  dengan lebih cerdas.
                </Text>
              </Text>

              <Text style={styles.description}>
                Pahami nutrisi makananmu dengan bantuan
                teknologi AI, dalam satu aplikasi.
              </Text>
            </View>

            {/* Form Login */}
            <View style={styles.card}>
              <View style={styles.cardHeader}>
                <Text style={styles.cardTitle}>
                  Selamat datang
                </Text>

                <Text style={styles.cardSubtitle}>
                  Masuk untuk melanjutkan ke HealthCoach.
                </Text>
              </View>

              {/* Username */}
              <Text style={styles.label}>Username</Text>

              <View
                style={[
                  styles.inputRow,
                  usernameError ? styles.inputInvalid : null,
                ]}
              >
                <Feather
                  name="user"
                  size={18}
                  color="#7A9990"
                />

                <TextInput
                  style={styles.input}
                  placeholder="Masukkan username"
                  placeholderTextColor="#9DAFA9"
                  keyboardType="default"
                  autoCapitalize="none"
                  autoCorrect={false}
                  autoComplete="username"
                  value={username}
                  onChangeText={(value) => {
                    setUsername(value);
                    setUsernameError('');
                  }}
                />
              </View>

              {usernameError ? (
                <Text style={styles.error}>
                  {usernameError}
                </Text>
              ) : null}

              {/* Password */}
              <Text style={styles.label}>Password</Text>

              <View
                style={[
                  styles.inputRow,
                  passwordError ? styles.inputInvalid : null,
                ]}
              >
                <Feather
                  name="lock"
                  size={18}
                  color="#7A9990"
                />

                <TextInput
                  style={styles.input}
                  placeholder="Masukkan password"
                  placeholderTextColor="#9DAFA9"
                  secureTextEntry={!showPassword}
                  autoCapitalize="none"
                  autoComplete="current-password"
                  value={password}
                  onChangeText={(value) => {
                    setPassword(value);
                    setPasswordError('');
                  }}
                />

                <TouchableOpacity
                  onPress={() =>
                    setShowPassword(!showPassword)
                  }
                  accessibilityRole="button"
                  accessibilityLabel={
                    showPassword
                      ? 'Sembunyikan password'
                      : 'Tampilkan password'
                  }
                >
                  <Feather
                    name={showPassword ? 'eye-off' : 'eye'}
                    size={19}
                    color="#168A75"
                  />
                </TouchableOpacity>
              </View>

              {passwordError ? (
                <Text style={styles.error}>
                  {passwordError}
                </Text>
              ) : null}

              {/* Tombol Login */}
              <TouchableOpacity
                onPress={handleLogin}
                disabled={isLoading}
                activeOpacity={0.85}
                accessibilityRole="button"
              >
                <LinearGradient
                  colors={['#138D76', '#2BAE96']}
                  start={{ x: 0, y: 0 }}
                  end={{ x: 1, y: 0 }}
                  style={styles.button}
                >
                  <Text style={styles.buttonText}>
                    {isLoading ? 'Memproses...' : 'Masuk'}
                  </Text>

                  <Feather
                    name="arrow-right"
                    size={18}
                    color="#FFFFFF"
                  />
                </LinearGradient>
              </TouchableOpacity>
            </View>

            {/* Navigasi Registrasi */}
            <View style={styles.registerRow}>
              <Text style={styles.registerText}>
                Belum punya akun?{' '}
              </Text>

              <TouchableOpacity
                onPress={onGoToRegister}
                accessibilityRole="button"
                accessibilityLabel="Buka halaman registrasi"
              >
                <Text style={styles.registerLink}>
                  Daftar sekarang
                </Text>
              </TouchableOpacity>
            </View>

            {/* Footer */}
            <View style={styles.footer}>
              <Feather
                name="heart"
                size={13}
                color="#8EACA3"
              />

              <Text style={styles.footerText}>
                HealthCoach © 2026
              </Text>
            </View>
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

            <Text style={styles.modalTitle}>{feedback.title}</Text>
            <Text style={styles.modalDescription}>
              {feedback.message}
            </Text>

            <TouchableOpacity
              activeOpacity={0.85}
              style={styles.modalAction}
              onPress={() => {
                const succeeded = feedback.type === 'success';
                setFeedback(prev => ({ ...prev, visible: false }));
                if (succeeded && onLoginSuccess) onLoginSuccess();
              }}
            >
              <LinearGradient
                colors={['#138D76', '#2BAE96']}
                style={styles.modalGradient}
              >
                <Text style={styles.modalButtonText}>
                  {feedback.type === 'success' ? 'Lanjutkan' : 'Coba Lagi'}
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

  flex: {
    flex: 1,
  },

  safeArea: {
    flex: 1,
    backgroundColor: '#F3FBF8',
    paddingTop:
      Platform.OS === 'android'
        ? NativeStatusBar.currentHeight || 0
        : 0,
  },

  background: {
    flex: 1,
  },

  content: {
    flexGrow: 1,
    paddingHorizontal: 25,
    paddingTop: 23,
    paddingBottom: 26,
    justifyContent: 'center',
  },

  glowOne: {
    position: 'absolute',
    width: 270,
    height: 270,
    borderRadius: 135,
    top: -65,
    right: -105,
    backgroundColor: '#BBDFFE',
  },

  glowTwo: {
    position: 'absolute',
    width: 270,
    height: 270,
    borderRadius: 135,
    bottom: 35,
    left: -130,
    backgroundColor: '#B9EBDB',
  },

  brandRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 39,
  },

  logo: {
    width: 45,
    height: 45,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
  },

  brandText: {
    flex: 1,
    marginLeft: 11,
  },

  brandName: {
    fontSize: 19,
    fontWeight: '800',
    color: '#155748',
    letterSpacing: -0.5,
  },

  brandCaption: {
    color: '#77948A',
    fontSize: 11,
    marginTop: 2,
  },

  aiBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.78)',
    borderWidth: 1,
    borderColor: '#DDEDE6',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
  },

  aiDot: {
    width: 7,
    height: 7,
    borderRadius: 4,
    backgroundColor: '#23AE93',
    marginRight: 7,
  },

  aiText: {
    fontSize: 11,
    fontWeight: '800',
    color: '#3D8B79',
  },

  intro: {
    marginBottom: 30,
  },

  eyebrowRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 14,
  },

  eyebrowLine: {
    width: 19,
    height: 2,
    backgroundColor: '#25A88B',
    marginRight: 9,
  },

  eyebrow: {
    fontSize: 10,
    letterSpacing: 1.5,
    fontWeight: '800',
    color: '#348F7C',
  },

  headline: {
    fontSize: 29,
    lineHeight: 38,
    letterSpacing: -0.9,
    fontWeight: '800',
    color: '#123F36',
  },

  headlineAccent: {
    color: '#189B82',
  },

  description: {
    color: '#718B82',
    fontSize: 13,
    lineHeight: 21,
    marginTop: 12,
    maxWidth: 310,
  },

  card: {
    backgroundColor: 'rgba(255,255,255,0.92)',
    borderWidth: 1,
    borderColor: '#E2EFE9',
    borderRadius: 23,
    paddingHorizontal: 22,
    paddingVertical: 25,
    shadowColor: '#5C9F8C',
    shadowOpacity: 0.08,
    shadowRadius: 18,
    shadowOffset: { width: 0, height: 8 },
    elevation: 3,
  },

  cardHeader: {
    marginBottom: 25,
  },

  cardTitle: {
    fontSize: 21,
    fontWeight: '800',
    color: '#163F36',
    letterSpacing: -0.4,
  },

  cardSubtitle: {
    color: '#839A92',
    fontSize: 12,
    marginTop: 6,
    lineHeight: 19,
  },

  label: {
    fontSize: 13,
    fontWeight: '700',
    color: '#365B50',
    marginBottom: 9,
  },

  inputRow: {
    minHeight: 52,
    backgroundColor: '#F8FCFA',
    borderRadius: 13,
    borderWidth: 1,
    borderColor: '#DDEBE5',
    paddingHorizontal: 14,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },

  inputInvalid: {
    borderColor: '#D97373',
    backgroundColor: '#FFF9F8',
  },

  input: {
    flex: 1,
    color: '#244A3E',
    fontSize: 14,
    marginHorizontal: 11,
    paddingVertical: 12,
    minWidth: 0,
  },

  error: {
    color: '#C95151',
    fontSize: 12,
    marginTop: -13,
    marginBottom: 14,
  },

  button: {
    height: 53,
    borderRadius: 13,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 3,
  },

  buttonText: {
    color: '#FFFFFF',
    fontWeight: '800',
    fontSize: 15,
    marginRight: 10,
  },

  registerRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 23,
  },

  registerText: {
    color: '#718B82',
    fontSize: 12,
  },

  registerLink: {
    color: '#138D76',
    fontSize: 12,
    fontWeight: '800',
  },

  footer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 20,
  },

  footerText: {
    fontSize: 11,
    color: '#91A9A0',
    marginLeft: 7,
  },
});
