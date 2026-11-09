import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  FlatList,
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
import {
  deleteHistory,
  getHistories,
  getHistoryDetail,
} from '../services/history';

function formatDate(value) {
  if (!value) return 'Tanggal tidak tersedia';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return 'Tanggal tidak tersedia';
  return date.toLocaleString('id-ID', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}


function HistoryResult({ result }) {
  const data = result || {};
  const food = data.identification || {};
  const nutrition = data.nutrition || {};
  const matching = data.matching || {};

  const foodName =
    food.food_name || nutrition.name || 'Makanan tidak diketahui';

  const nutrients = [
    ['Kalori', nutrition.calories, 'kcal'],
    ['Protein', nutrition.proteins ?? nutrition.protein, 'g'],
    ['Karbohidrat', nutrition.carbohydrate, 'g'],
    ['Lemak', nutrition.fat, 'g'],
  ];

  const recommendation =
    data.recommendation || data.recommendations ||
    data.ai_recommendation || null;

  const recommendationText =
    typeof recommendation === 'string'
      ? recommendation
      : recommendation?.message ||
        recommendation?.text ||
        recommendation?.advice ||
        null;

  return (
    <View>
      <Text style={historyStyles.foodName}>{foodName}</Text>

      {nutrition.name ? (
        <Text style={historyStyles.reference}>
          Referensi nutrisi: {nutrition.name}
        </Text>
      ) : null}

      <View style={historyStyles.nutritionGrid}>
        {nutrients.map(([label, value, unit]) => (
          <View key={label} style={historyStyles.nutritionCard}>
            <Text style={historyStyles.nutritionLabel}>
              {label}
            </Text>
            <Text style={historyStyles.nutritionValue}>
              {value != null && value !== ''
                ? `${value} ${unit}`
                : 'Tidak tersedia'}
            </Text>
          </View>
        ))}
      </View>

      {recommendationText ? (
        <View style={historyStyles.infoCard}>
          <Text style={historyStyles.infoTitle}>
            Rekomendasi AI
          </Text>
          <Text style={historyStyles.infoText}>
            {recommendationText}
          </Text>
        </View>
      ) : null}

      {food.notes ? (
        <View style={historyStyles.infoCard}>
          <Text style={historyStyles.infoTitle}>
            Catatan Identifikasi
          </Text>
          <Text style={historyStyles.infoText}>
            {food.notes}
          </Text>
        </View>
      ) : null}

      {data.note ? (
        <Text style={historyStyles.note}>{data.note}</Text>
      ) : null}

      {matching.reference_name ? (
        <Text style={historyStyles.note}>
          Data nutrisi menggunakan referensi:
          {' '}{matching.reference_name}.
        </Text>
      ) : null}

      <Text style={historyStyles.disclaimer}>
        Informasi bersifat edukatif, bukan diagnosis medis.
      </Text>
    </View>
  );
}

const historyStyles = StyleSheet.create({
  foodName: {
    fontSize: 23,
    fontWeight: '800',
    color: '#164C40',
    marginBottom: 8,
  },
  reference: {
    fontSize: 14,
    color: '#718780',
    marginBottom: 18,
  },
  nutritionGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 18,
  },
  nutritionCard: {
    width: '48%',
    backgroundColor: '#EDF9F5',
    borderRadius: 17,
    padding: 15,
    marginBottom: 12,
  },
  nutritionLabel: {
    fontSize: 13,
    color: '#718780',
    marginBottom: 7,
  },
  nutritionValue: {
    fontSize: 18,
    fontWeight: '800',
    color: '#164C40',
  },
  infoCard: {
    backgroundColor: '#EDF9F5',
    padding: 18,
    borderRadius: 19,
    marginBottom: 15,
  },
  infoTitle: {
    color: '#164C40',
    fontWeight: '800',
    fontSize: 17,
    marginBottom: 10,
  },
  infoText: {
    color: '#607A73',
    fontSize: 14,
    lineHeight: 23,
  },
  note: {
    color: '#607A73',
    fontSize: 13,
    lineHeight: 21,
    marginTop: 10,
  },
  disclaimer: {
    color: '#718780',
    fontSize: 12,
    marginTop: 25,
    lineHeight: 19,
  },
});

export default function HistoryScreen({ onBack }) {
  const [histories, setHistories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [selected, setSelected] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const loadHistories = useCallback(async (refresh = false) => {
    if (refresh) setRefreshing(true);
    else setLoading(true);
    setError('');

    try {
      const data = await getHistories();
      if (!Array.isArray(data)) {
        throw new Error('Format daftar riwayat tidak sesuai.');
      }
      setHistories(data);
    } catch (err) {
      setError(err.message || 'Riwayat tidak dapat dimuat.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadHistories();
  }, [loadHistories]);

  const openDetail = async (item) => {
    setDetailLoading(true);
    try {
      const detail = await getHistoryDetail(item.id);
      setSelected(detail);
    } catch (err) {
      Alert.alert('Gagal membuka detail', err.message);
    } finally {
      setDetailLoading(false);
    }
  };

  const confirmDelete = () => {
    if (!selected || deleting) return;

    Alert.alert(
      'Hapus riwayat?',
      'Riwayat analisis ini akan dihapus secara permanen.',
      [
        { text: 'Batal', style: 'cancel' },
        {
          text: 'Hapus',
          style: 'destructive',
          onPress: async () => {
            setDeleting(true);
            try {
              await deleteHistory(selected.id);
              setSelected(null);
              await loadHistories(true);
            } catch (err) {
              Alert.alert('Gagal menghapus', err.message);
            } finally {
              setDeleting(false);
            }
          },
        },
      ]
    );
  };

  const renderItem = ({ item }) => (
    <TouchableOpacity
      style={styles.card}
      activeOpacity={0.8}
      onPress={() => openDetail(item)}
      accessibilityLabel={`Buka riwayat analisis ${item.id}`}
    >
      <View style={styles.itemIcon}>
        <Feather name="file-text" size={23} color="#168A75" />
      </View>
      <View style={styles.itemContent}>
        <Text style={styles.itemTitle}>Analisis #{item.id}</Text>
        <Text style={styles.itemDate}>
          {formatDate(item.created_at)}
        </Text>
      </View>
      <Feather name="chevron-right" size={21} color="#168A75" />
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar style="dark" />
      <LinearGradient
        colors={['#F3FBF8', '#E9F7F4', '#EFF6FD']}
        style={styles.background}
      >
        <View style={styles.header}>
          <TouchableOpacity
            style={styles.backButton}
            onPress={selected ? () => setSelected(null) : onBack}
            accessibilityLabel="Kembali"
          >
            <Feather name="arrow-left" size={23} color="#168A75" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>
            {selected ? 'Detail Riwayat' : 'Riwayat Analisis'}
          </Text>
          <View style={styles.headerSpacer} />
        </View>

        {selected ? (
          <ScrollView contentContainerStyle={styles.content}>
            <View style={styles.cardVertical}>
              <Text style={styles.detailTitle}>
                Analisis #{selected.id}
              </Text>
              <Text style={styles.itemDate}>
                {formatDate(selected.created_at)}
              </Text>
              <Text style={styles.sectionTitle}>Hasil Analisis</Text>
              <HistoryResult result={selected.result} />
            </View>
            <TouchableOpacity
              style={styles.deleteButton}
              onPress={confirmDelete}
              disabled={deleting}
            >
              <Feather name="trash-2" size={18} color="#C74848" />
              <Text style={styles.deleteText}>
                {deleting ? 'Menghapus...' : 'Hapus Riwayat'}
              </Text>
            </TouchableOpacity>
          </ScrollView>
        ) : loading || detailLoading ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color="#168A75" />
            <Text style={styles.message}>Memuat riwayat...</Text>
          </View>
        ) : error ? (
          <View style={styles.center}>
            <Feather name="alert-circle" size={40} color="#C74848" />
            <Text style={styles.message}>{error}</Text>
            <TouchableOpacity
              style={styles.actionButton}
              onPress={() => loadHistories()}
            >
              <Text style={styles.actionText}>Coba Lagi</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <FlatList
            data={histories}
            keyExtractor={(item) => String(item.id)}
            renderItem={renderItem}
            contentContainerStyle={styles.content}
            refreshing={refreshing}
            onRefresh={() => loadHistories(true)}
            ListHeaderComponent={
              <Text style={styles.description}>
                Lihat kembali hasil analisis makanan yang tersimpan.
              </Text>
            }
            ListEmptyComponent={
              <View style={styles.empty}>
                <Feather name="clock" size={44} color="#168A75" />
                <Text style={styles.emptyTitle}>Belum ada riwayat</Text>
                <Text style={styles.message}>
                  Hasil analisis makanan akan muncul di sini
                  setelah berhasil disimpan.
                </Text>
              </View>
            }
          />
        )}
      </LinearGradient>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: '#F3FBF8' },
  background: { flex: 1 },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 22,
    paddingTop: 20,
    paddingBottom: 18,
  },
  backButton: {
    width: 42, height: 42, borderRadius: 15,
    backgroundColor: '#FFFFFF',
    alignItems: 'center', justifyContent: 'center',
  },
  headerTitle: {
    fontSize: 20, fontWeight: '800', color: '#164C40',
  },
  headerSpacer: { width: 42 },
  content: { paddingHorizontal: 22, paddingBottom: 36, flexGrow: 1 },
  description: { color: '#607A73', fontSize: 14, marginBottom: 18 },
  card: {
    backgroundColor: '#FFFFFF', borderRadius: 20,
    padding: 17, marginBottom: 13,
    flexDirection: 'row', alignItems: 'center',
  },
  itemIcon: {
    width: 48, height: 48, borderRadius: 16,
    backgroundColor: '#E0F5EC',
    alignItems: 'center', justifyContent: 'center',
  },
  itemContent: { flex: 1, paddingHorizontal: 13 },
  itemTitle: { fontSize: 16, fontWeight: '700', color: '#164C40' },
  itemDate: { color: '#738982', fontSize: 12, marginTop: 5 },
  center: {
    flex: 1, justifyContent: 'center',
    alignItems: 'center', paddingHorizontal: 30, gap: 15,
  },
  message: {
    fontSize: 14, lineHeight: 21, color: '#607A73',
    textAlign: 'center', marginTop: 10,
  },
  empty: { alignItems: 'center', paddingTop: 85 },
  emptyTitle: {
    fontSize: 19, fontWeight: '800',
    color: '#164C40', marginTop: 20,
  },
  actionButton: {
    backgroundColor: '#168A75', paddingHorizontal: 25,
    paddingVertical: 13, borderRadius: 14,
  },
  actionText: { color: '#FFFFFF', fontWeight: '700' },
  cardVertical: {
    backgroundColor: '#FFFFFF', borderRadius: 22,
    padding: 22, marginBottom: 18,
  },
  detailTitle: {
    fontSize: 22, fontWeight: '800', color: '#164C40',
  },
  sectionTitle: {
    fontSize: 17, fontWeight: '700', color: '#164C40',
    marginTop: 26, marginBottom: 14,
  },
  resultText: {
    fontSize: 13, color: '#405A52',
    lineHeight: 21, fontFamily: 'monospace',
  },
  deleteButton: {
    flexDirection: 'row', alignItems: 'center',
    justifyContent: 'center', padding: 17,
    borderRadius: 18, backgroundColor: '#FDECEC',
    gap: 10,
  },
  deleteText: { color: '#C74848', fontWeight: '700' },
});
