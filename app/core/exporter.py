import csv
from app.core.store import store


def export_almacen_csv(path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Partida", "Descripción", "Unidad",
            "Cantidad", "Ubicación", "Proveedor"
        ])

        for i in store.almacen.values():
            writer.writerow([
                i.partida, i.descripcion, i.unidad,
                i.cantidad, i.ubicacion, i.proveedor
            ])
