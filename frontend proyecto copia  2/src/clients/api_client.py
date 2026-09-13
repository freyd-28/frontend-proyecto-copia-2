import httpx
from flask import current_app


class APIError(Exception):
    """Error controlado al comunicarse con la API."""

    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class APIClient:
    """Cliente HTTP centralizado para el backend BilleterAPP."""

    def __init__(self, api_token=None):
        self.api_token = api_token
        self.base_url = current_app.config["API_BASE_URL"].rstrip("/")

    def _headers(self):
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        return headers

    def request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._headers()
        headers.update(kwargs.pop("headers", {}) or {})
        try:
            response = httpx.request(
                method,
                url,
                headers=headers,
                timeout=httpx.Timeout(10.0, connect=5.0),
                **kwargs,
            )
        except httpx.RequestError as exc:
            raise APIError(
                "No fue posible conectar con el backend. "
                "Verifica que Flask esté ejecutándose en el puerto configurado."
            ) from exc

        if response.status_code >= 400:
            try:
                payload = response.json()
                message = payload.get("message") or payload.get("error") or "Error en la API"
            except (ValueError, TypeError):
                message = response.text.strip() or "Error en la API"
            raise APIError(message, response.status_code)

        if not response.content:
            return None
        try:
            return response.json()
        except ValueError:
            return response.text

    def get(self, endpoint):
        return self.request("GET", endpoint)

    def post(self, endpoint, json=None):
        return self.request("POST", endpoint, json=json)

    def put(self, endpoint, json=None):
        return self.request("PUT", endpoint, json=json)

    def delete(self, endpoint):
        return self.request("DELETE", endpoint)