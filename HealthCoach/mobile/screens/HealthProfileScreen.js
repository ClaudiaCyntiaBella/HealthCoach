import React, { useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Modal,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Feather } from '@expo/vector-icons';
import Slider from '@react-native-community/slider';

import {
  getHealthProfile,
  createHealthProfile,
  updateHealthProfile,
} from '../services/healthProfile';

const GREEN = '#168A75';

const GENDERS = [
  { label: 'Laki-laki', value: 'male' },
  { label: 'Perempuan', value: 'female' },
  { label: 'Tidak ingin menyebutkan', value: 'prefer_not_to_say' },
];

const GOALS = [
  { label: 'Menjaga berat badan', value: 'maintain_weight' },
  { label: 'Menurunkan berat badan', value: 'lose_weight' },
  { label: 'Meningkatkan berat badan', value: 'gain_weight' },
  { label: 'Menjaga pola makan sehat', value: 'healthy_eating' },
];

const ACTIVITIES = [
  { label: 'Jarang bergerak', value: 'sedentary' },
  { label: 'Aktivitas ringan', value: 'light' },
  { label: 'Aktivitas sedang', value: 'moderate' },
  { label: 'Aktif', value: 'active' },
  { label: 'Sangat aktif', value: 'very_active' },
];

function OptionGroup({ options, value, onChange }) {
  return (
    <View style={styles.optionGroup}>
      {options.map((option) => {
        const selected = value === option.value;

        return (
          <TouchableOpacity
            key={option.value}
            style={[
              styles.option,
              selected && styles.optionSelected,
            ]}
            onPress={() => onChange(option.value)}
            accessibilityRole="radio"
            accessibilityState={{ selected }}
          >
            <Feather
              name={selected ? 'check-circle' : 'circle'}
              size={18}
              color={selected ? GREEN : '#97A7A4'}
            />
            <Text
              style={[
                styles.optionText,
                selected && styles.optionTextSelected,
              ]}
            >
              {option.label}
            </Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
}

function NumberSlider({
  label,
  value,
  onChange,
  min,
  max,
  unit,
}) {
  return (
    <View style={styles.sliderSection}>
      <View style={styles.sliderHeader}>
        <Text style={styles.label}>{label}</Text>
        <Text style={styles.sliderValue}>
          {value} {unit}
        </Text>
      </View>

      <Slider
        minimumValue={min}
        maximumValue={max}
        step={1}
        value={value}
        onValueChange={onChange}
        minimumTrackTintColor={GREEN}
        maximumTrackTintColor="#D5EAE5"
        thumbTintColor={GREEN}
        accessibilityLabel={label}
      />

      <View style={styles.sliderLimits}>
        <Text style={styles.hint}>{min} {unit}</Text>
        <Text style={styles.hint}>{max} {unit}</Text>
      </View>
    </View>
  );
}

function isValidBirthDate(value) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    return false;
  }

  const [year, month, day] = value.split('-').map(Number);

  const date = new Date(Date.UTC(year, month - 1, day));
  const today = new Date();
  const todayUTC = Date.UTC(
    today.getFullYear(),
    today.getMonth(),
    today.getDate()
  );

  return (
    date.getUTCFullYear() === year &&
    date.getUTCMonth() === month - 1 &&
    date.getUTCDate() === day &&
    date.getTime() <= todayUTC
  );
}

export default function HealthProfileScreen({ onBack }) {
  const [existing, setExisting] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [dialog, setDialog] = useState(null);

  const closeDialog = () => {
    if (!dialog) return;

    const wasSuccess = dialog.kind === 'success';
    setDialog(null);

    if (wasSuccess) {
      onBack?.();
    }
  };

  const [gender, setGender] = useState(null);
  const [height, setHeight] = useState(165);
  const [weight, setWeight] = useState(60);
  const [heightChanged, setHeightChanged] = useState(false);
  const [weightChanged, setWeightChanged] = useState(false);
  const [goal, setGoal] = useState(null);
  const [birthDate, setBirthDate] = useState('');
  const [activity, setActivity] = useState(null);

  useEffect(() => {
    let active = true;

    const loadProfile = async () => {
      try {
        const data = await getHealthProfile();

        if (!active) return;

        if (data) {
          setExisting(true);
          setGender(data.gender ?? null);
          setHeight(
            data.height == null
              ? 165
              : Math.max(100, Math.min(220, Number(data.height)))
          );
          setWeight(
            data.weight == null
              ? 60
              : Math.max(25, Math.min(200, Number(data.weight)))
          );
          setGoal(data.nutrition_goal ?? null);
          setBirthDate(data.birth_date ?? '');
          setActivity(data.activity_level ?? null);
        }
      } catch (err) {
        if (active) {
          setError(err.message || 'Gagal mengambil profil.');
        }
      } finally {
        if (active) setLoading(false);
      }
    };

    loadProfile();

    return () => {
      active = false;
    };
  }, []);

  const handleSave = async () => {
    if (saving || loading || error) return;

    if (!gender || !goal) {
      setDialog({
        kind: 'warning',
        title: 'Profil Belum Lengkap',
        message: 'Pilih jenis kelamin dan tujuan nutrisi terlebih dahulu.',
      });
      return;
    }

    const trimmedDate = birthDate.trim();

    if (trimmedDate && !isValidBirthDate(trimmedDate)) {
      setDialog({
        kind: 'warning',
        title: 'Tanggal Tidak Valid',
        message: 'Gunakan format YYYY-MM-DD dan pastikan tanggal tidak melebihi hari ini.',
      });
      return;
    }

    const payload = {
      gender,
      nutrition_goal: goal,
    };

    if (!existing || heightChanged) {
      payload.height = String(height);
    }

    if (!existing || weightChanged) {
      payload.weight = String(weight);
    }

    if (trimmedDate) {
      payload.birth_date = trimmedDate;
    }

    if (activity) {
      payload.activity_level = activity;
    }

    setSaving(true);

    try {
      if (existing) {
        await updateHealthProfile(payload);
      } else {
        await createHealthProfile(payload);
      }

      setExisting(true);

      setDialog({
        kind: 'success',
        title: 'Berhasil Disimpan!',
        message: 'Informasi kesehatanmu berhasil disimpan. Kamu dapat memperbaruinya kapan saja.',
      });
    } catch (err) {
      setDialog({
        kind: 'error',
        title: 'Gagal Menyimpan',
        message: err.message || 'Silakan coba kembali.',
      });
    } finally {
      setSaving(false);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <LinearGradient
        colors={['#F3FBF8', '#E9F7F4', '#EFF6FD']}
        style={styles.background}
      >
        <ScrollView
          contentContainerStyle={styles.content}
          keyboardShouldPersistTaps="handled"
        >
          <TouchableOpacity
            onPress={onBack}
            style={styles.backButton}
          >
            <Feather name="arrow-left" size={21} color={GREEN} />
            <Text style={styles.backText}>Kembali</Text>
          </TouchableOpacity>

          <Text style={styles.eyebrow}>YOUR HEALTH PROFILE</Text>
          <Text style={styles.title}>Lengkapi Profilmu</Text>
          <Text style={styles.description}>
            Kenali kebutuhan tubuhmu melalui informasi
            kesehatan yang kamu isi.
          </Text>

          {loading ? (
            <View style={styles.center}>
              <ActivityIndicator size="large" color={GREEN} />
              <Text style={styles.hint}>
                Memuat profil kesehatan...
              </Text>
            </View>
          ) : error ? (
            <View style={styles.card}>
              <Text style={styles.errorText}>{error}</Text>
              <TouchableOpacity onPress={onBack}>
                <Text style={styles.backText}>
                  Kembali ke Beranda
                </Text>
              </TouchableOpacity>
            </View>
          ) : (
            <View style={styles.card}>
              <View style={styles.section}>
                <Text style={styles.label}>Jenis Kelamin</Text>
                <OptionGroup
                  options={GENDERS}
                  value={gender}
                  onChange={setGender}
                />
              </View>

              <NumberSlider
                label="Tinggi Badan"
                value={height}
                onChange={(value) => {
                  setHeight(value);
                  setHeightChanged(true);
                }}
                min={100}
                max={220}
                unit="cm"
              />

              <NumberSlider
                label="Berat Badan"
                value={weight}
                onChange={(value) => {
                  setWeight(value);
                  setWeightChanged(true);
                }}
                min={25}
                max={200}
                unit="kg"
              />

              <View style={styles.section}>
                <Text style={styles.label}>Tujuan Nutrisi</Text>
                <OptionGroup
                  options={GOALS}
                  value={goal}
                  onChange={setGoal}
                />
              </View>

              <View style={styles.section}>
                <Text style={styles.label}>
                  Tanggal Lahir (Opsional)
                </Text>
                <TextInput
                  style={styles.input}
                  value={birthDate}
                  onChangeText={setBirthDate}
                  placeholder="YYYY-MM-DD"
                  placeholderTextColor="#91A5A0"
                  keyboardType="numbers-and-punctuation"
                  maxLength={10}
                />
              </View>

              <View style={styles.section}>
                <Text style={styles.label}>
                  Tingkat Aktivitas (Opsional)
                </Text>
                <OptionGroup
                  options={ACTIVITIES}
                  value={activity}
                  onChange={setActivity}
                />
              </View>

              <TouchableOpacity
                onPress={handleSave}
                disabled={saving}
                style={[
                  styles.saveButton,
                  saving && styles.disabledButton,
                ]}
              >
                {saving ? (
                  <ActivityIndicator color="#FFFFFF" />
                ) : (
                  <>
                    <Feather name="save" size={19} color="#FFFFFF" />
                    <Text style={styles.saveText}>
                      {existing ? 'Perbarui Profil' : 'Simpan Profil'}
                    </Text>
                  </>
                )}
              </TouchableOpacity>
            </View>
          )}
        </ScrollView>

      <Modal
        visible={dialog !== null}
        transparent
        animationType="fade"
        onRequestClose={closeDialog}
      >
        <View style={styles.dialogOverlay}>
          <View
            style={styles.dialogCard}
            accessibilityViewIsModal
          >
            <View
              style={[
                styles.dialogIconContainer,
                dialog?.kind === 'error' && styles.dialogErrorIcon,
                dialog?.kind === 'warning' && styles.dialogWarningIcon,
              ]}
            >
              <Feather
                name={
                  dialog?.kind === 'success'
                    ? 'check-circle'
                    : dialog?.kind === 'warning'
                    ? 'alert-circle'
                    : 'x-circle'
                }
                size={34}
                color={
                  dialog?.kind === 'success'
                    ? GREEN
                    : dialog?.kind === 'warning'
                    ? '#D69A36'
                    : '#D96868'
                }
              />
            </View>

            <Text style={styles.dialogTitle}>
              {dialog?.title}
            </Text>

            <Text style={styles.dialogDescription}>
              {dialog?.message}
            </Text>

            <TouchableOpacity
              activeOpacity={0.85}
              style={styles.dialogButton}
              onPress={closeDialog}
              accessibilityRole="button"
              accessibilityLabel={
                dialog?.kind === 'success'
                  ? 'Kembali ke Beranda'
                  : 'Tutup pemberitahuan'
              }
            >
              <LinearGradient
                colors={['#138D76', '#2BAE96']}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 0 }}
                style={styles.dialogButtonGradient}
              >
                <Text style={styles.dialogButtonText}>
                  {dialog?.kind === 'success'
                    ? 'Kembali ke Beranda'
                    : 'Mengerti'}
                </Text>
                <Feather
                  name={
                    dialog?.kind === 'success'
                      ? 'arrow-right'
                      : 'check'
                  }
                  size={18}
                  color="#FFFFFF"
                />
              </LinearGradient>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
      </LinearGradient>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: '#F3FBF8' },
  background: { flex: 1 },
  content: { padding: 22, paddingBottom: 48 },
  backButton: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 28,
    gap: 8,
  },
  backText: { color: GREEN, fontWeight: '700', fontSize: 15 },
  eyebrow: {
    color: GREEN,
    fontSize: 11,
    fontWeight: '800',
    letterSpacing: 2,
  },
  title: {
    fontSize: 30,
    color: '#173C35',
    fontWeight: '800',
    marginTop: 8,
  },
  description: {
    color: '#647D76',
    fontSize: 14,
    lineHeight: 22,
    marginTop: 10,
    marginBottom: 24,
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 22,
    padding: 20,
    borderWidth: 1,
    borderColor: '#E1F0EB',
  },
  section: { marginBottom: 25 },
  label: {
    fontWeight: '700',
    fontSize: 15,
    color: '#24483F',
    marginBottom: 12,
  },
  optionGroup: { gap: 10 },
  option: {
    borderWidth: 1,
    borderColor: '#DFEAE6',
    borderRadius: 13,
    padding: 13,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  optionSelected: {
    borderColor: GREEN,
    backgroundColor: '#EAF8F3',
  },
  optionText: { color: '#526F66', fontSize: 14, flex: 1 },
  optionTextSelected: { color: GREEN, fontWeight: '700' },
  sliderSection: { marginBottom: 25 },
  sliderHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  sliderValue: {
    color: GREEN,
    fontSize: 17,
    fontWeight: '800',
  },
  sliderLimits: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  hint: { color: '#829991', fontSize: 12, marginTop: 7 },
  input: {
    borderWidth: 1,
    borderColor: '#DFEAE6',
    borderRadius: 12,
    padding: 14,
    color: '#24483F',
    fontSize: 15,
  },
  saveButton: {
    marginTop: 8,
    backgroundColor: GREEN,
    borderRadius: 14,
    minHeight: 54,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 10,
  },
  saveText: { color: '#FFFFFF', fontWeight: '800', fontSize: 15 },
  disabledButton: { opacity: 0.65 },
  errorText: { color: '#B42318', marginBottom: 15 },

  dialogOverlay: {
    flex: 1,
    backgroundColor: 'rgba(17, 43, 37, 0.52)',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 28,
  },
  dialogCard: {
    backgroundColor: '#FFFFFF',
    width: '100%',
    maxWidth: 390,
    borderRadius: 26,
    paddingHorizontal: 24,
    paddingTop: 32,
    paddingBottom: 24,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E1F0EB',
    shadowColor: '#163D34',
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.13,
    shadowRadius: 20,
    elevation: 8,
  },
  dialogIconContainer: {
    width: 76,
    height: 76,
    borderRadius: 38,
    backgroundColor: '#E7F7F1',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 20,
  },
  dialogErrorIcon: {
    backgroundColor: '#FDECEC',
  },
  dialogWarningIcon: {
    backgroundColor: '#FFF5DF',
  },
  dialogTitle: {
    fontSize: 21,
    fontWeight: '800',
    color: '#173C35',
    textAlign: 'center',
    marginBottom: 10,
  },
  dialogDescription: {
    fontSize: 14,
    color: '#647D76',
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: 26,
  },
  dialogButton: {
    width: '100%',
    borderRadius: 15,
    overflow: 'hidden',
  },
  dialogButtonGradient: {
    minHeight: 54,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
    paddingHorizontal: 14,
  },
  dialogButtonText: {
    color: '#FFFFFF',
    fontSize: 15,
    fontWeight: '800',
  },
  center: { paddingVertical: 45, alignItems: 'center' },
});
