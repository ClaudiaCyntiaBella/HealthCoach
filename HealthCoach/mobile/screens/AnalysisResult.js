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
  const isReference = matching.status === 'REFERENCE_MATCH';

  if (unknown) {
    return (
      <View style={styles.card}>
        <Feather name="alert-circle" size={30} color="#C78645" />
        <Text style={styles.title}>Makanan Tidak Terdeteksi</Text>
        <Text style={styles.description}>
          HealthCoach belum dapat mengenali makanan pada foto.
          Pastikan foto memperlihatkan makanan yang jelas,
          lalu ganti foto dan coba kembali.
        </Text>
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
            Nutrisi Referensi Dataset
          </Text>
          <Text style={styles.referenceDescription}>
            Referensi nutrisi: {nutrition.name}.
            {' '}Nilai aktual dapat berbeda sesuai bahan dan porsi.
          </Text>
        </View>
      )}

      {matching.status === 'NOT_MATCHED' && (
        <Text style={styles.warning}>
          Makanan teridentifikasi, tetapi belum cocok dengan
          data nutrisi pada dataset HealthCoach.
        </Text>
      )}

      <View style={styles.divider} />

      <Text style={styles.sectionTitle}>Informasi Nutrisi</Text>

      {nutrition ? (
        <>
          <Text style={styles.description}>
            {nutrition.name || 'Data nutrisi HealthCoach'}
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
          {!isReference && (
            <Text style={styles.disclaimer}>
              Nilai mengikuti entri dataset HealthCoach dan
              belum tentu mencerminkan porsi dalam foto.
            </Text>
          )}
        </>
      ) : (
        <Text style={styles.description}>
          Data nutrisi makanan ini belum tersedia.
          HealthCoach tidak menampilkan angka perkiraan
          tanpa sumber data.
        </Text>
      )}

      <View style={styles.recommendation}>
        <Text style={styles.sectionTitle}>Rekomendasi AI</Text>
        <Text style={styles.description}>
          {data.recommendation ||
            'Rekomendasi belum tersedia. Informasi nutrisi tetap dapat dilihat.'}
        </Text>
      </View>

      {Boolean(data.note) && !isReference && (
        <Text style={styles.note}>{data.note}</Text>
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
