from src.clients.api_client import APIClient, APIError


class ApiProductos(APIClient):
    def get_productos(self):
        return self.get("/productos/")

    def get_producto(self, producto_id):
        return self.get(f"/productos/{producto_id}")

    def create_producto(self, data):
        return self.post("/productos/", json=data)

    def update_producto(self, producto_id, data):
        return self.put(f"/productos/{producto_id}", json=data)

    def delete_producto(self, producto_id):
        return self.delete(f"/productos/{producto_id}")