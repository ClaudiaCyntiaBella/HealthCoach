import { authenticatedFetch } from './tokenManager';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL;

const ALLOWED_FIELDS = [
  'weight',
  'height',
  'gender',
  'birth_date',
  'activity_level',
  'nutrition_goal',
];

function getBaseUrl() {
  if (!API_BASE_URL) {
    throw new Error('Alamat API HealthCoach belum dikonfigurasi.');
  }
  return `${API_BASE_URL}/health-profile/`;
}

async function profileRequest(method, payload) {
  const options = { method };

  if (payload !== undefined) {
    if (!payload || typeof payload !== 'object' ||
        Array.isArray(payload)) {
      throw new Error('Data profil tidak valid.');
    }

    const keys = Object.keys(payload);

    if (!keys.length) {
      throw new Error('Pilih minimal satu data profil.');
    }

    if (keys.some((key) => !ALLOWED_FIELDS.includes(key))) {
      throw new Error('Terdapat field profil yang tidak dikenal.');
    }

    options.headers = {
      'Content-Type': 'application/json',
    };
    options.body = JSON.stringify(payload);
  }

  let response;

  try {
    response = await authenticatedFetch(getBaseUrl(), options);
  } catch (error) {
    throw new Error(
      error.message || 'Tidak dapat menghubungi server HealthCoach.'
    );
  }

  let result;

  try {
    result = await response.json();
  } catch {
    throw new Error('Respons server tidak dapat dibaca.');
  }

  if (!response.ok || result.success === false) {
    const details = result.error?.details;
    const detailMessage =
      details && typeof details === 'object'
        ? Object.values(details).flat().join(' ')
        : null;

    throw new Error(
      detailMessage ||
      result.error?.message ||
      result.detail ||
      'Gagal memproses profil kesehatan.'
    );
  }

  return result.data;
}

export async function getHealthProfile() {
  return profileRequest('GET');
}

export async function createHealthProfile(payload) {
  return profileRequest('POST', payload);
}

export async function updateHealthProfile(payload) {
  return profileRequest('PATCH', payload);
}
