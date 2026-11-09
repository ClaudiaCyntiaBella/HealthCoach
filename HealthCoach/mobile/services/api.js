const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL;

export async function postApi(endpoint, payload) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  const result = await response.json();

  if (!response.ok || result.success === false) {
    const details = result.error?.details;

    const validationMessage = details
      ? Object.values(details).flat().join('\n')
      : null;

    throw new Error(
      validationMessage ||
      result.error?.message ||
      'Terjadi kesalahan pada server.'
    );
  }

  return result;
}
