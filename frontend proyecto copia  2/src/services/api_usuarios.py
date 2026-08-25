from src.clients.api_client import APIClient, APIError


class ApiUsuarios(APIClient):
    def get_usuarios(self):
        return self.get("/usuarios/")

    def create_usuario(self, data):
        return self.post("/usuarios/", json=data)

    def update_usuario(self, usuario_id, data):
        return self.put(f"/usuarios/{usuario_id}", json=data)

    def delete_usuario(self, usuario_id):
        return self.delete(f"/usuarios/{usuario_id}")