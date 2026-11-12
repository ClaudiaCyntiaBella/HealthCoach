import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { Feather } from '@expo/vector-icons';

function NutritionItem({ label, value, unit }) {
  const available = value !== null &&
    value !== undefined && value !== '';

  return (
    <View style={styles.nutritionItem}>
      <Text style={styles.nutritionLabel}>{label}</Text>
      <Text style={styles.nutritionValue}>
        {available ? `${value} ${unit}` : 'Belum tersedia'}
      </Text>
    </View>
  );
}

export default function AnalysisResult({ result }) {
  if (!result?.data) return null;

  const data = result.data;
  const identification = data.identification || {};
  const matching = data.matching || {};
  const nutrition = data.nutrition;
  const unknown =
    identification.identification_status === 'UNKNOWN';
  const nutritionSource = data.nutrition_source || 'UNAVAILABLE';
  const isReference = nutritionSource === 'DATASET';
  const isEstimated = nutritionSource === 'AI_ESTIMATED';
  const details = data.recommendation_details || {};

  if (unknown) {
    const category = identification.image_category;
    const quality = identification.image_quality;

    const isBlurry = quality === 'TOO_BLURRY';
    const isNonFood = category === 'NON_FOOD';

    const title = isBlurry
      ? 'Foto Terlalu Buram'
      : isNonFood
        ? 'Foto Bukan Makanan atau Minuman'
        : 'Objek Belum Dapat Dikenali';

    const message = isBlurry
      ? 'Foto terlalu buram. Ambil ulang dengan pencahayaan cukup dan pastikan kamera fokus pada makanan atau minuman.'
      : isNonFood
        ? 'Foto ini bukan makanan atau minuman. Silakan pilih foto makanan atau minuman yang ingin dianalisis.'
        : 'Objek belum dapat dikenali dengan jelas. Coba ambil foto dari sudut lain.';

    return (
      <View style={styles.card}>
        <Feather name="alert-circle" size={30} color="#C78645" />
        <Text style={styles.title}>{title}</Text>
        <Text style={styles.description}>{message}</Text>
      </View>
    );
  }

  return (
    <View style={styles.card}>
      <Feather name="check-circle" size={27} color="#168A75" />
      <Text style={styles.eyebrow}>HASIL ANALISIS HEALTHCOACH</Text>

      <Text style={styles.title}>
        {identification.food_name || 'Hasil Identifikasi'}
      </Text>

      {isReference && nutrition && (
        <View style={styles.referenceCard}>
          <Text style={styles.referenceTitle}>
            Referensi Data Nutrisi
          </Text>
          <Text style={styles.referenceDescription}>
            {matching.reference_name || nutrition.name || 'Dataset HealthCoach'}
          </Text>
        </View>
      )}

      {isEstimated && (
        <Text style={styles.warning}>
          Nama makanan belum cocok dengan dataset HealthCoach.
          Nilai nutrisi yang ditampilkan merupakan estimasi AI.
        </Text>
      )}

      {nutritionSource === 'UNAVAILABLE' && (
        <Text style={styles.warning}>
          Informasi nutrisi belum tersedia untuk makanan ini.
        </Text>
      )}

      <View style={styles.divider} />

      <Text style={styles.sectionTitle}>Informasi Nutrisi</Text>

      {nutrition ? (
        <>
          <Text style={styles.description}>
            {isReference
              ? 'Data nutrisi berdasarkan dataset HealthCoach'
              : isEstimated
                ? 'Estimasi nutrisi oleh AI'
                : 'Informasi nutrisi'}
          </Text>
          <View style={styles.nutritionGrid}>
            <NutritionItem
              label="Kalori"
              value={nutrition.calories}
              unit="kcal"
            />
            <NutritionItem
              label="Protein"
              value={nutrition.proteins}
              unit="g"
            />
            <NutritionItem
              label="Karbohidrat"
              value={nutrition.carbohydrate}
              unit="g"
            />
            <NutritionItem
              label="Lemak"
              value={nutrition.fat}
              unit="g"
            />
          </View>
          <Text style={styles.disclaimer}>
            Nilai nutrisi dapat berbeda sesuai bahan, cara pengolahan,
            dan ukuran porsi yang dikonsumsi.
          </Text>
        </>
      ) : (
        <Text style={styles.description}>
          Data nutrisi makanan ini belum tersedia.
          HealthCoach tidak menampilkan angka perkiraan
          tanpa sumber data.
        </Text>
      )}

      <View style={styles.recommendation}>
        <Text style={styles.sectionTitle}>
          Rekomendasi HealthCoach AI
        </Text>

        {[
          ['Saran', details.saran],
          ['Alasan', details.alasan],
          ['Pendamping atau Alternatif', details.pendamping_alternatif],
          ['Catatan Nutrisi', details.catatan_nutrisi],
        ].some(([, value]) => typeof value === 'string' && value.trim())
          ? [
              ['Saran', details.saran],
              ['Alasan', details.alasan],
              ['Pendamping atau Alternatif', details.pendamping_alternatif],
              ['Catatan Nutrisi', details.catatan_nutrisi],
            ].map(([label, value]) =>
              typeof value === 'string' && value.trim() ? (
                <View key={label} style={{ marginTop: 10 }}>
                  <Text style={{
                    color: '#164C40',
                    fontWeight: '700',
                    marginBottom: 4,
                  }}>
                    {label}
                  </Text>
                  <Text style={styles.description}>
                    {value}
                  </Text>
                </View>
              ) : null
            )
          : (
            <Text style={styles.description}>
              {data.recommendation || 'Rekomendasi belum tersedia.'}
            </Text>
          )}
      </View>

      {Boolean(data.note) && isReference && (
        <Text style={styles.note}>{data.note}</Text>
      )}

      {isEstimated && (
        <Text style={styles.note}>
          Informasi nutrisi merupakan estimasi AI,
          bukan data resmi dataset HealthCoach.
        </Text>
      )}

      <Text style={styles.disclaimer}>
        Informasi ini bersifat edukatif, bukan diagnosis medis.
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    borderWidth: 1,
    borderColor: '#E1ECE7',
    padding: 20,
    marginTop: 18,
    gap: 11,
  },
  eyebrow: {
    fontSize: 11,
    fontWeight: '800',
    color: '#168A75',
    letterSpacing: 1,
  },
  title: {
    fontSize: 22,
    fontWeight: '800',
    color: '#164C40',
  },
  sectionTitle: {
    fontSize: 17,
    fontWeight: '800',
    color: '#164C40',
  },
  description: {
    fontSize: 14,
    color: '#658178',
    lineHeight: 22,
  },
  divider: {
    height: 1,
    backgroundColor: '#E4EFEA',
    marginVertical: 6,
  },
  warning: {
    color: '#A16F36',
    backgroundColor: '#FFF4E6',
    padding: 12,
    borderRadius: 12,
    lineHeight: 21,
  },
  referenceCard: {
    backgroundColor: '#FFF6E8',
    borderRadius: 15,
    padding: 15,
    gap: 7,
  },
  referenceTitle: {
    color: '#916322',
    fontSize: 14,
    fontWeight: '800',
  },
  referenceDescription: {
    color: '#896F49',
    fontSize: 13,
    lineHeight: 21,
  },
  nutritionGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  nutritionItem: {
    width: '47%',
    backgroundColor: '#F0FAF6',
    borderRadius: 14,
    padding: 14,
    gap: 6,
  },
  nutritionLabel: {
    color: '#658178',
    fontSize: 12,
  },
  nutritionValue: {
    color: '#164C40',
    fontWeight: '800',
    fontSize: 17,
  },
  recommendation: {
    backgroundColor: '#F0FAF6',
    borderRadius: 15,
    padding: 15,
    gap: 8,
  },
  note: {
    color: '#658178',
    fontSize: 13,
    lineHeight: 20,
  },
  disclaimer: {
    color: '#819990',
    fontSize: 12,
    lineHeight: 19,
    marginTop: 5,
  },
});
