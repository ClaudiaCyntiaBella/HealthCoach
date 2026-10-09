from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler


class HealthCoachServiceError(Exception):
    """Kesalahan layanan internal yang aman dipetakan menjadi respons API."""

    code = "SERVICE_ERROR"
    status_code = 500
    public_message = "Terjadi kesalahan saat memproses permintaan."

    def __init__(self, message: str | None = None):
        super().__init__(message or self.public_message)


class GeminiConfigurationError(HealthCoachServiceError):
    code = "GEMINI_NOT_CONFIGURED"
    status_code = 503
    public_message = "Layanan AI belum dikonfigurasi."


class GeminiTimeoutError(HealthCoachServiceError):
    code = "GEMINI_TIMEOUT"
    status_code = 504
    public_message = "Layanan AI melewati batas waktu. Silakan coba lagi."


class GeminiResponseError(HealthCoachServiceError):
    code = "GEMINI_INVALID_RESPONSE"
    status_code = 502
    public_message = "Layanan AI memberikan respons yang tidak dapat diproses."


class GeminiUnavailableError(HealthCoachServiceError):
    code = "GEMINI_UNAVAILABLE"
    status_code = 502
    public_message = "Layanan AI sedang tidak tersedia. Silakan coba lagi."


class NutritionDataError(HealthCoachServiceError):
    code = "NUTRITION_DATA_UNAVAILABLE"
    status_code = 503
    public_message = "Data nutrisi belum tersedia."


def healthcoach_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None and isinstance(exc, HealthCoachServiceError):
        api_exc = APIException(exc.public_message, code=exc.code)
        api_exc.status_code = exc.status_code
        response = exception_handler(api_exc, context)

    if response is None:
        return None

    if isinstance(response.data, dict) and "detail" in response.data:
        message = str(response.data["detail"])
        code = getattr(response.data["detail"], "code", "REQUEST_ERROR")
        details = None
    else:
        message = "Input tidak valid."
        code = "VALIDATION_ERROR"
        details = response.data

    response.data = {
        "success": False,
        "error": {
            "code": str(code).upper(),
            "message": message,
            "details": details,
        },
    }
    return response

