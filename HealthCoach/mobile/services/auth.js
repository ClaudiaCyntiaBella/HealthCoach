import * as SecureStore from 'expo-secure-store';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL;

export async function logoutUser() {
  const access = await SecureStore.getItemAsync('hc_access_token');
  const refresh = await SecureStore.getItemAsync('hc_refresh_token');

  if (!access || !refresh) {
    throw new Error('Sesi tidak ditemukan. Silakan login kembali.');
  }

  const response = await fetch(`${API_BASE_URL}/auth/logout/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${access}`,
    },
    body: JSON.stringify({ refresh }),
  });

  const result = await response.json();

  if (!response.ok || result.success === false) {
    throw new Error(
      result.error?.message || 'Logout gagal. Silakan coba kembali.'
    );
  }

  await SecureStore.deleteItemAsync('hc_access_token');
  await SecureStore.deleteItemAsync('hc_refresh_token');

  return result;
}
