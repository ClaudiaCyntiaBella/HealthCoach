import * as SecureStore from 'expo-secure-store';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL;

async function clearLocalTokens() {
  await SecureStore.deleteItemAsync('hc_access_token');
  await SecureStore.deleteItemAsync('hc_refresh_token');
}

export async function logoutUser() {
  const refresh = await SecureStore.getItemAsync(
    'hc_refresh_token'
  );

  if (!refresh) {
    await clearLocalTokens();
    return {
      success: true,
      message: 'Sesi lokal berhasil diakhiri.',
    };
  }

  if (!API_BASE_URL) {
    throw new Error('Alamat API HealthCoach belum dikonfigurasi.');
  }

  let response;

  try {
    response = await fetch(`${API_BASE_URL}/auth/logout/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh }),
    });
  } catch {
    throw new Error(
      'Tidak dapat menghubungi server untuk logout. Coba lagi.'
    );
  }

  let result;

  try {
    result = await response.json();
  } catch {
    throw new Error('Respons logout tidak dapat dibaca.');
  }

  if (!response.ok || result.success === false) {
    throw new Error(
      result.error?.message ||
      result.detail ||
      'Logout gagal. Silakan coba kembali.'
    );
  }

  await clearLocalTokens();

  return result;
}
