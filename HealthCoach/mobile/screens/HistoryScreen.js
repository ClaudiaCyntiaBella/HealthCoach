import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  FlatList,
  SafeAreaView,
  ScrollView,
  TextInput,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { LinearGradient } from 'expo-linear-gradient';
import { Feather, MaterialCommunityIcons } from '@expo/vector-icons';
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
  const details = data.recommendation_details || {};

  const foodName =
    food.food_name || nutrition.name || 'Makanan tidak diketahui';

  const nutritionSource = data.nutrition_source;
  const isDataset = nutritionSource === 'DATASET';
  const isEstimated = nutritionSource === 'AI_ESTIMATED';

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

  const recommendationSections = [
    ['Saran', details.saran],
    ['Alasan', details.alasan],
    ['Pendamping atau Alternatif', details.pendamping_alternatif],
    ['Catatan Nutrisi', details.catatan_nutrisi],
  ].filter(([, value]) =>
    typeof value === 'string' && value.trim()
  );

  return (
    <View>
      <Text style={historyStyles.foodName}>{foodName}</Text>

      {isDataset && (
        <Text style={historyStyles.reference}>
          Referensi nutrisi: {matching.reference_name || nutrition.name || 'Dataset HealthCoach'}
        </Text>
      )}

      {isEstimated && (
        <Text style={historyStyles.reference}>
          Sumber nutrisi: Estimasi AI
        </Text>
      )}

      {nutritionSource === 'UNAVAILABLE' && (
        <Text style={historyStyles.reference}>
          Informasi nutrisi belum tersedia.
        </Text>
      )}

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

      {(recommendationSections.length > 0 || recommendationText) && (
        <View style={historyStyles.infoCard}>
          <Text style={historyStyles.infoTitle}>
            Rekomendasi HealthCoach AI
          </Text>

          {recommendationSections.length > 0
            ? recommendationSections.map(([label, value]) => (
                <View key={label} style={{ marginTop: 12 }}>
                  <Text style={{
                    color: '#164C40',
                    fontWeight: '700',
                    fontSize: 14,
                    marginBottom: 5,
                  }}>
                    {label}
                  </Text>
                  <Text style={historyStyles.infoText}>
                    {value}
                  </Text>
                </View>
              ))
            : (
              <Text style={historyStyles.infoText}>
                {recommendationText}
              </Text>
            )}
        </View>
      )}

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

      {data.quality_warning ? (
        <Text style={historyStyles.note}>
          {data.quality_warning}
        </Text>
      ) : null}

      {isEstimated ? (
        <Text style={historyStyles.note}>
          Informasi nutrisi merupakan estimasi AI,
          bukan data resmi dataset HealthCoach.
        </Text>
      ) : (
        Boolean(data.note) && (
          <Text style={historyStyles.note}>
            {data.note}
          </Text>
        )
      )}

      <Text style={historyStyles.disclaimer}>
        Informasi ini bersifat edukatif, bukan diagnosis medis.
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

function getHistoryFoodName(item) {
  const result = item?.result || {};
  const name =
    result.identification?.food_name ||
    result.nutrition?.name;

  return typeof name === 'string' && name.trim()
    ? name.trim()
    : 'Nama makanan tidak tersedia';
}

function isDrink(name) {
  if (!name || typeof name !== 'string') return false;

  const normalized = name
    .toLocaleLowerCase('id-ID')
    .trim()
    .replace(/\s+/g, ' ');

  const drinkPrefixes = [
    'kopi',
    'teh',
    'jus',
    'juice',
    'susu',
    'boba',
    'smoothie',
    'milkshake',
    'cappuccino',
    'latte',
    'americano',
    'matcha',
    'soda',
    'sirup',
    'wedang',
    'cendol',
    'dawet',
    'minuman',
    'thai tea',
    'lemon tea',
    'air mineral',
    'air putih',
    'air kelapa',
    'es teh',
    'es kopi',
    'es jeruk',
    'es susu',
    'es cokelat',
    'es matcha',
    'es cendol',
    'es dawet',
    'es kelapa',
    'es campur',
    'es buah',
  ];

  return drinkPrefixes.some(
    (prefix) =>
      normalized === prefix ||
      normalized.startsWith(prefix + ' ')
  );
}

export default function HistoryScreen({ onBack }) {
  const [histories, setHistories] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
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

  const filteredHistories = histories.filter((item) =>
    getHistoryFoodName(item)
      .toLocaleLowerCase('id-ID')
      .includes(searchQuery.trim().toLocaleLowerCase('id-ID'))
  );

  const renderItem = ({ item }) => (
    <TouchableOpacity
      style={styles.card}
      activeOpacity={0.8}
      onPress={() => openDetail(item)}
      accessibilityLabel={`Lihat hasil analisis ${getHistoryFoodName(item)}`}
    >
      <View style={styles.itemIcon}>
        {(
          item.result?.identification?.identification_status === 'UNKNOWN' ||
          getHistoryFoodName(item) === 'Nama makanan tidak tersedia'
        ) ? (
          <Feather
            name="x-circle"
            size={25}
            color="#D96868"
          />
        ) : isDrink(getHistoryFoodName(item)) ? (
          <MaterialCommunityIcons
            name="cup"
            size={25}
            color="#168A75"
          />
        ) : (
          <MaterialCommunityIcons
            name="silverware-fork-knife"
            size={25}
            color="#168A75"
          />
        )}
      </View>
      <View style={styles.itemContent}>
        <Text style={styles.itemTitle} numberOfLines={2}>
          {getHistoryFoodName(item)}
        </Text>
        <Text style={styles.itemDate}>
          {formatDate(item.created_at)}
        </Text>
        <Text style={styles.itemHint}>
          Ketuk untuk melihat hasil
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
          {selected ? (
            <TouchableOpacity
              style={styles.backButton}
              onPress={() => setSelected(null)}
              accessibilityLabel="Kembali ke daftar riwayat"
            >
              <Feather
                name="arrow-left"
                size={23}
                color="#168A75"
              />
            </TouchableOpacity>
          ) : (
            <View style={styles.headerSpacer} />
          )}
          <Text style={styles.headerTitle}>
            {selected ? 'Detail Riwayat' : 'Riwayat Analisis'}
          </Text>
          <View style={styles.headerSpacer} />
        </View>

        {selected ? (
          <ScrollView contentContainerStyle={styles.content}>
            <View style={styles.cardVertical}>
              <Text style={styles.detailTitle}>
                {getHistoryFoodName(selected)}
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
            data={filteredHistories}
            keyExtractor={(item) => String(item.id)}
            renderItem={renderItem}
            contentContainerStyle={styles.content}
            keyboardShouldPersistTaps="handled"
            keyboardDismissMode="on-drag"
            refreshing={refreshing}
            onRefresh={() => loadHistories(true)}
            ListHeaderComponent={
              <View style={styles.listHeader}>
                <Text style={styles.description}>
                  Temukan kembali makanan yang pernah kamu analisis.
                </Text>

                <View style={styles.searchBox}>
                  <Feather
                    name="search"
                    size={20}
                    color="#168A75"
                  />

                  <TextInput
                    style={styles.searchInput}
                    placeholder="Cari nama makanan..."
                    placeholderTextColor="#829991"
                    value={searchQuery}
                    onChangeText={setSearchQuery}
                    autoCorrect={false}
                    returnKeyType="search"
                    accessibilityLabel="Cari riwayat berdasarkan nama makanan"
                  />

                  {searchQuery.length > 0 && (
                    <TouchableOpacity
                      onPress={() => setSearchQuery('')}
                      accessibilityLabel="Hapus pencarian"
                    >
                      <Feather
                        name="x-circle"
                        size={19}
                        color="#829991"
                      />
                    </TouchableOpacity>
                  )}
                </View>

                <Text style={styles.resultCount}>
                  {searchQuery.trim()
                    ? `${filteredHistories.length} hasil ditemukan`
                    : `${histories.length} riwayat tersimpan`}
                </Text>
              </View>
            }
            ListEmptyComponent={
              <View style={styles.empty}>
                <Feather
                  name={searchQuery.trim() ? 'search' : 'clock'}
                  size={44}
                  color="#168A75"
                />
                <Text style={styles.emptyTitle}>
                  {searchQuery.trim()
                    ? 'Makanan tidak ditemukan'
                    : 'Belum ada riwayat'}
                </Text>
                <Text style={styles.message}>
                  {searchQuery.trim()
                    ? 'Coba gunakan nama makanan atau kata kunci lain.'
                    : 'Hasil analisis makanan akan muncul di sini setelah berhasil disimpan.'}
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
  listHeader: {
    marginBottom: 8,
  },
  searchBox: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#E1F0EB',
    paddingHorizontal: 15,
    minHeight: 54,
    gap: 11,
    marginBottom: 10,
  },
  searchInput: {
    flex: 1,
    minWidth: 0,
    color: '#164C40',
    fontSize: 14,
    paddingVertical: 12,
  },
  resultCount: {
    color: '#738982',
    fontSize: 12,
    marginBottom: 12,
  },
  itemHint: {
    color: '#168A75',
    fontSize: 11,
    marginTop: 7,
    fontWeight: '600',
  },
  deleteText: { color: '#C74848', fontWeight: '700' },
});
