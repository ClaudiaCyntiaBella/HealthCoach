import { File } from 'expo-file-system';
import { fetch } from 'expo/fetch';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL;

const MAX_PHOTOS = 5;
const MAX_IMAGE_SIZE = 5 * 1024 * 1024;
const MAX_TOTAL_SIZE = 20 * 1024 * 1024;

export async function analyzeFood(photos) {
  const selected = photos.filter(Boolean);

  if (selected.length === 0) {
    throw new Error('Pilih minimal satu foto makanan.');
  }

  if (selected.length > MAX_PHOTOS) {
    throw new Error('Maksimal lima foto dalam satu analisis.');
  }

  const totalSize = selected.reduce(
    (sum, photo) => sum + (photo.fileSize || 0),
    0
  );

  if (totalSize > MAX_TOTAL_SIZE) {
    throw new Error('Total ukuran foto melebihi 20 MB.');
  }

  const formData = new FormData();

  selected.forEach((photo, index) => {
    const originalName = photo.fileName || '';
    const extension = (
      originalName.split('.').pop() ||
      photo.uri.split('?')[0].split('.').pop() ||
      ''
    ).toLowerCase();

    const type =
      extension === 'png' ? 'image/png' :
      extension === 'webp' ? 'image/webp' :
      ['jpg', 'jpeg'].includes(extension) ? 'image/jpeg' : null;

    if (!type) {
      throw new Error('Format foto harus JPG, JPEG, PNG, atau WEBP.');
    }

    if (photo.fileSize && photo.fileSize > MAX_IMAGE_SIZE) {
      throw new Error(`Foto ${index + 1} melebihi batas 5 MB.`);
    }

    const file = new File(photo.uri);

    if (!file.exists) {
      throw new Error(`Foto ${index + 1} tidak ditemukan di perangkat.`);
    }

    if (file.size > MAX_IMAGE_SIZE) {
      throw new Error(`Foto ${index + 1} melebihi batas 5 MB.`);
    }

    formData.append(
      'images',
      file,
      `healthcoach_${index + 1}.${extension}`
    );
  });

  if (!API_BASE_URL) {
    throw new Error('Alamat API HealthCoach belum dikonfigurasi.');
  }


  let response;

  try {
    response = await fetch(`${API_BASE_URL}/analyze/`, {
      method: 'POST',
      body: formData,
    });
  } catch (error) {
    console.error('[HealthCoach Upload] Fetch gagal:', error);
    throw new Error(
      `Upload gagal: ${error.message || 'Kesalahan jaringan tidak diketahui'}`
    );
  }

  let result;

  try {
    result = await response.json();
  } catch {
    throw new Error(
      'Server mengembalikan respons yang tidak dapat dibaca.'
    );
  }

  if (!response.ok || result.success === false) {
    const details = result.error?.details;
    const validationMessage = details
      ? Object.values(details).flat().join('\n')
      : null;

    throw new Error(
      validationMessage ||
      result.error?.message ||
      'Analisis makanan gagal. Silakan coba kembali.'
    );
  }

  return result;
}
