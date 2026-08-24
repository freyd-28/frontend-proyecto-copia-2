from src.clients.api_client import APIClient, APIError


class ApiClientes(APIClient):
    def get_clientes(self):
        return self.get("/clientes/")

    def get_cliente(self, cliente_id):
        return self.get(f"/clientes/{cliente_id}")

    def create_cliente(self, data):
        return self.post("/clientes/", json=data)

    def update_cliente(self, cliente_id, data):
        return self.put(f"/clientes/{cliente_id}", json=data)

    def delete_cliente(self, cliente_id):
        return self.delete(f"/clientes/{cliente_id}")
        