import { authenticatedFetch } from './tokenManager';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL;

async function historyRequest(endpoint, method = 'GET') {
  if (!API_BASE_URL) {
    throw new Error('Alamat API HealthCoach belum dikonfigurasi.');
  }

  let response;

  try {
    response = await authenticatedFetch(
      `${API_BASE_URL}${endpoint}`,
      { method }
    );
  } catch (error) {
    throw new Error(
      error.message || 'Tidak dapat terhubung ke server HealthCoach.'
    );
  }

  let result;

  try {
    result = await response.json();
  } catch {
    throw new Error('Respons server tidak dapat dibaca.');
  }

  if (response.status === 401) {
    throw new Error(
      'Sesi login tidak valid. Silakan login kembali.'
    );
  }

  if (!response.ok || result.success === false) {
    throw new Error(
      result.error?.message ||
      result.detail ||
      'Gagal memproses riwayat analisis.'
    );
  }

  return result;
}

export async function getHistories() {
  const result = await historyRequest('/history/');
  return result.data;
}

export async function getHistoryDetail(historyId) {
  const id = Number(historyId);

  if (!Number.isSafeInteger(id) || id <= 0) {
    throw new Error('ID riwayat tidak valid.');
  }

  const result = await historyRequest(`/history/${id}/`);
  return result.data;
}

export async function deleteHistory(historyId) {
  const id = Number(historyId);

  if (!Number.isSafeInteger(id) || id <= 0) {
    throw new Error('ID riwayat tidak valid.');
  }

  return historyRequest(`/history/${id}/`, 'DELETE');
}
