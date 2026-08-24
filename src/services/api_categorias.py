from src.clients.api_client import APIClient, APIError


class ApiCategorias(APIClient):
    def __init__(self, api_token):
        super().__init__(api_token)

    def get_categorias(self):
        return self.get("/categorias/")

    def get_categoria(self, categoria_id):
        return self.get(f"/categorias/{categoria_id}")

    def create_categoria(self, data):
        return self.post("/categorias/", json=data)

    def update_categoria(self, categoria_id, data):
        return self.put(f"/categorias/{categoria_id}", json=data)

    def delete_categoria(self, categoria_id):
        return self.delete(f"/categorias/{categoria_id}")