from src.clients.api_client import APIClient, APIError


class ApiFacturas(APIClient):
    def get_facturas(self):
        return self.get("/facturas/")

    def get_factura(self, factura_id):
        return self.get(f"/facturas/{factura_id}")

    def create_factura(self, data):
        return self.post("/facturas/", json=data)

    def update_factura(self, factura_id, data):
        return self.put(f"/facturas/{factura_id}", json=data)

    def delete_factura(self, factura_id):
        return self.delete(f"/facturas/{factura_id}")




class ApiFacturaDetalle(APIClient):
    def get_detalles_por_factura(self, factura_id):
        return self.get(f"/factura_detalle/factura/{factura_id}")

    def create_detalle(self, data):
        return self.post("/factura_detalle/", json=data)

    def update_detalle(self, detalle_id, data):
        return self.put(f"/factura_detalle/{detalle_id}", json=data)

    def delete_detalle(self, detalle_id):
        return self.delete(f"/factura_detalle/{detalle_id}")


    

