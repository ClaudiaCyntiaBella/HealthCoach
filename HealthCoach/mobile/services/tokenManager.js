import * as SecureStore from 'expo-secure-store';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL;

let refreshPromise = null;

export async function clearSession() {
  await SecureStore.deleteItemAsync('hc_access_token');
  await SecureStore.deleteItemAsync('hc_refresh_token');
}

export async function refreshAccessToken() {
  if (refreshPromise) {
    return refreshPromise;
  }

  refreshPromise = (async () => {
    const refresh = await SecureStore.getItemAsync(
      'hc_refresh_token'
    );

    if (!refresh) {
      await clearSession();
      throw new Error(
        'Sesi login telah berakhir. Silakan login kembali.'
      );
    }

    if (!API_BASE_URL) {
      throw new Error('Alamat API belum dikonfigurasi.');
    }

    let response;

    try {
      response = await fetch(
        `${API_BASE_URL}/auth/refresh/`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ refresh }),
        }
      );
    } catch {
      throw new Error(
        'Tidak dapat memperbarui sesi. Periksa koneksi internet.'
      );
    }

    if (!response.ok) {
      if (response.status === 400 ||
          response.status === 401) {
        await clearSession();
        throw new Error(
          'Sesi login telah berakhir. Silakan login kembali.'
        );
      }

      throw new Error(
        'Server gagal memperbarui sesi. Coba lagi.'
      );
    }

    let result;

    try {
      result = await response.json();
    } catch {
      throw new Error('Respons refresh token tidak valid.');
    }

    if (!result.access) {
      throw new Error(
        'Access token baru tidak ditemukan.'
      );
    }

    await SecureStore.setItemAsync(
      'hc_access_token',
      result.access
    );

    return result.access;
  })();

  try {
    return await refreshPromise;
  } finally {
    refreshPromise = null;
  }
}

export async function authenticatedFetch(
  url,
  options = {},
  fetcher = fetch
) {
  let accessToken = await SecureStore.getItemAsync(
    'hc_access_token'
  );

  if (!accessToken) {
    accessToken = await refreshAccessToken();
  }

  const sendRequest = (token) =>
    fetcher(url, {
      ...options,
      headers: {
        ...(options.headers || {}),
        Authorization: `Bearer ${token}`,
      },
    });

  let response = await sendRequest(accessToken);

  if (response.status === 401) {
    const currentToken = await SecureStore.getItemAsync(
      'hc_access_token'
    );

    const newToken =
      currentToken && currentToken !== accessToken
        ? currentToken
        : await refreshAccessToken();

    response = await sendRequest(newToken);
  }

  return response;
}
