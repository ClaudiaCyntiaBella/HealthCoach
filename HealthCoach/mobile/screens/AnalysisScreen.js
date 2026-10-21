import React, { useState } from 'react';
import {
  ActivityIndicator,
  Image,
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
import * as ImagePicker from 'expo-image-picker';
import { analyzeFood } from '../services/analysis';
import AnalysisResult from './AnalysisResult';

const PHOTO_SLOTS = [
  { title: 'Tampak Atas', subtitle: 'Foto seluruh makanan dari atas' },
  { title: 'Sudut Samping', subtitle: 'Perlihatkan bentuk dan porsi' },
  { title: 'Detail Makanan', subtitle: 'Perlihatkan tekstur dan bahan' },
];

export default function AnalysisScreen({ onBack }) {
  const [photos, setPhotos] = useState([null, null, null]);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);

  const updatePhoto = (index, asset) => {
    setPhotos((previous) =>
      previous.map((photo, i) => (i === index ? asset : photo))
    );
    setMessage('');
    setAnalysisResult(null);
  };

  const choosePhoto = async (index, source) => {
    try {
      setMessage('');

      let result;

      if (source === 'camera') {
        const permission =
          await ImagePicker.requestCameraPermissionsAsync();

        if (!permission.granted) {
          setMessage('Izin kamera diperlukan untuk mengambil foto.');
          return;
        }

        result = await ImagePicker.launchCameraAsync({
          mediaTypes: ['images'],
          allowsEditing: false,
          quality: 0.8,
        });
      } else {
        const permission =
          await ImagePicker.requestMediaLibraryPermissionsAsync();

        if (!permission.granted) {
          setMessage('Izin galeri diperlukan untuk memilih foto.');
          return;
        }

        result = await ImagePicker.launchImageLibraryAsync({
          mediaTypes: ['images'],
          allowsMultipleSelection: false,
          allowsEditing: false,
          quality: 0.8,
        });
      }

      if (result.canceled || !result.assets?.length) return;

      const asset = result.assets[0];
      const extension = (asset.fileName || asset.uri)
        .split('?')[0]
        .split('.')
        .pop()
        .toLowerCase();

      const supported = ['jpg', 'jpeg', 'png', 'webp'];

      if (!supported.includes(extension)) {
        setMessage('Gunakan foto JPG, JPEG, PNG, atau WEBP.');
        return;
      }

      if (asset.fileSize && asset.fileSize > 5 * 1024 * 1024) {
        setMessage('Ukuran foto maksimal 5 MB.');
        return;
      }

      updatePhoto(index, asset);
    } catch (error) {
      setMessage(
        error.message || 'Foto tidak dapat dipilih. Silakan coba lagi.'
      );
    }
  };

  const selectedCount = photos.filter(Boolean).length;

  const submitAnalysis = async () => {
    if (loading || selectedCount === 0) return;

    setLoading(true);
    setMessage('');
    setAnalysisResult(null);

    try {
      const response = await analyzeFood(photos);
      setAnalysisResult(response);
    } catch (error) {
      setMessage(
        error.message || 'Analisis gagal. Silakan coba kembali.'
      );
    } finally {
      setLoading(false);
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
          <TouchableOpacity
            style={styles.backButton}
            onPress={onBack}
            accessibilityLabel="Kembali ke HomeScreen"
          >
            <Feather name="arrow-left" size={21} color="#168A75" />
            <Text style={styles.backText}>Kembali</Text>
          </TouchableOpacity>

          <View style={styles.intro}>
            <Text style={styles.eyebrow}>HEALTHCOACH AI</Text>
            <Text style={styles.title}>Analisis Makanan</Text>
            <Text style={styles.description}>
              Tambahkan foto makanan yang sama dari beberapa
              sudut agar AI memperoleh informasi visual lebih lengkap.
            </Text>
          </View>

          <View style={styles.progressCard}>
            <Feather name="image" size={22} color="#168A75" />
            <View style={styles.progressInfo}>
              <Text style={styles.progressTitle}>
                {selectedCount} dari 3 foto dipilih
              </Text>
              <Text style={styles.progressSubtitle}>
                Minimal 1 foto • Direkomendasikan 3 foto
              </Text>
            </View>
          </View>

          {PHOTO_SLOTS.map((slot, index) => (
            <View key={slot.title} style={styles.photoCard}>
              <View style={styles.slotHeading}>
                <View style={styles.slotNumber}>
                  <Text style={styles.slotNumberText}>{index + 1}</Text>
                </View>
                <View style={styles.slotInfo}>
                  <Text style={styles.slotTitle}>{slot.title}</Text>
                  <Text style={styles.slotSubtitle}>{slot.subtitle}</Text>
                </View>
              </View>

              {photos[index] ? (
                <Image
                  source={{ uri: photos[index].uri }}
                  style={styles.preview}
                  resizeMode="cover"
                />
              ) : (
                <View style={styles.placeholder}>
                  <Feather name="image" size={32} color="#8BB7A7" />
                  <Text style={styles.placeholderText}>
                    Belum ada foto
                  </Text>
                </View>
              )}

              <View style={styles.actions}>
                <TouchableOpacity
                  style={styles.photoButton}
                  onPress={() => choosePhoto(index, 'gallery')}
                >
                  <Feather name="image" size={17} color="#168A75" />
                  <Text style={styles.photoButtonText}>Galeri</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={styles.photoButton}
                  onPress={() => choosePhoto(index, 'camera')}
                >
                  <Feather name="camera" size={17} color="#168A75" />
                  <Text style={styles.photoButtonText}>Kamera</Text>
                </TouchableOpacity>
              </View>

              {photos[index] && (
                <TouchableOpacity
                  style={styles.removeButton}
                  onPress={() => updatePhoto(index, null)}
                >
                  <Feather name="trash-2" size={15} color="#C75A5A" />
                  <Text style={styles.removeText}>Hapus foto</Text>
                </TouchableOpacity>
              )}
            </View>
          ))}

          {message ? (
            <View style={styles.errorCard}>
              <Feather name="alert-circle" size={18} color="#B64D4D" />
              <Text style={styles.errorText}>{message}</Text>
            </View>
          ) : null}

          <View style={styles.infoCard}>
            <Feather name="info" size={20} color="#168A75" />
            <Text style={styles.infoText}>
              Foto harus memperlihatkan makanan yang sama.
              Maksimal 5 MB per foto dan 20 MB keseluruhan.
              Hasil AI merupakan estimasi.
            </Text>
          </View>

          <TouchableOpacity
            disabled={selectedCount === 0 || loading}
            onPress={submitAnalysis}
            style={styles.analyzeButton}
            activeOpacity={0.85}
          >
            <LinearGradient
              colors={['#138D76', '#2BAE96']}
              style={[
                styles.analyzeGradient,
                (selectedCount === 0 || loading) &&
                  styles.disabledGradient,
              ]}
            >
              {loading ? (
                <ActivityIndicator color="#FFFFFF" />
              ) : (
                <Feather name="zap" size={19} color="#FFFFFF" />
              )}
              <Text style={styles.analyzeText}>
                {loading ? 'Menganalisis Makanan...' : 'Analisis Makanan'}
              </Text>
            </LinearGradient>
          </TouchableOpacity>

          {loading && (
            <Text style={styles.pendingText}>
              Foto sedang diproses oleh HealthCoach AI.
              Mohon tunggu dan jangan menutup halaman.
            </Text>
          )}

          {analysisResult && (
            <AnalysisResult result={analysisResult} />
          )}
        </ScrollView>
      </LinearGradient>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: '#F3FBF8' },
  background: { flex: 1 },
  content: { paddingHorizontal: 23, paddingTop: 18, paddingBottom: 48 },
  backButton: {
    flexDirection: 'row', alignItems: 'center', gap: 9,
    paddingVertical: 12,
  },
  backText: { color: '#168A75', fontSize: 15, fontWeight: '700' },
  intro: { marginTop: 24, marginBottom: 25 },
  eyebrow: {
    color: '#168A75', fontSize: 12,
    fontWeight: '800', letterSpacing: 1.5, marginBottom: 12,
  },
  title: { fontSize: 31, fontWeight: '800', color: '#164C40' },
  description: {
    fontSize: 15, lineHeight: 24, color: '#718B82', marginTop: 12,
  },
  progressCard: {
    flexDirection: 'row', alignItems: 'center', gap: 14,
    backgroundColor: '#E0F5EC', padding: 17,
    borderRadius: 19, marginBottom: 19,
  },
  progressInfo: { flex: 1 },
  progressTitle: { fontSize: 15, fontWeight: '800', color: '#164C40' },
  progressSubtitle: { color: '#69847B', fontSize: 12, marginTop: 4 },
  photoCard: {
    backgroundColor: '#FFFFFF', borderRadius: 24,
    borderWidth: 1, borderColor: '#E1ECE7',
    padding: 17, marginBottom: 16,
  },
  slotHeading: {
    flexDirection: 'row', alignItems: 'center',
    gap: 12, marginBottom: 15,
  },
  slotNumber: {
    width: 34, height: 34, borderRadius: 12,
    backgroundColor: '#E0F5EC',
    alignItems: 'center', justifyContent: 'center',
  },
  slotNumberText: { fontWeight: '800', color: '#168A75' },
  slotInfo: { flex: 1 },
  slotTitle: { fontSize: 17, fontWeight: '800', color: '#164C40' },
  slotSubtitle: { fontSize: 12, color: '#718B82', marginTop: 3 },
  placeholder: {
    height: 132, borderRadius: 17,
    backgroundColor: '#F3FAF7',
    alignItems: 'center', justifyContent: 'center', gap: 9,
  },
  placeholderText: { fontSize: 13, color: '#8AA99C' },
  preview: { width: '100%', height: 190, borderRadius: 17 },
  actions: { flexDirection: 'row', gap: 12, marginTop: 14 },
  photoButton: {
    flex: 1, minHeight: 44, borderRadius: 13,
    backgroundColor: '#EAF6F0',
    flexDirection: 'row', alignItems: 'center',
    justifyContent: 'center', gap: 8,
  },
  photoButtonText: { color: '#168A75', fontWeight: '700' },
  removeButton: {
    flexDirection: 'row', alignSelf: 'center',
    alignItems: 'center', gap: 6, paddingTop: 15,
  },
  removeText: { color: '#C75A5A', fontSize: 13, fontWeight: '600' },
  errorCard: {
    backgroundColor: '#FDECEC', borderRadius: 14,
    padding: 14, flexDirection: 'row', gap: 10, marginBottom: 16,
  },
  errorText: { color: '#B64D4D', flex: 1, lineHeight: 20 },
  infoCard: {
    flexDirection: 'row', gap: 12,
    backgroundColor: '#E0F5EC', borderRadius: 17, padding: 16,
  },
  infoText: { color: '#55796C', flex: 1, fontSize: 13, lineHeight: 21 },
  analyzeButton: { marginTop: 22, borderRadius: 16, overflow: 'hidden' },
  analyzeGradient: {
    minHeight: 56, flexDirection: 'row', alignItems: 'center',
    justifyContent: 'center', gap: 11,
  },
  disabledGradient: { opacity: 0.55 },
  analyzeText: { fontSize: 16, fontWeight: '800', color: '#FFFFFF' },
  pendingText: {
    color: '#8BA79B', fontSize: 12,
    textAlign: 'center', marginTop: 13, lineHeight: 19,
  },
});
