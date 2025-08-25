from scan import scan_barcode
from supabase import create_client, Client
import os 
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def main():
    barcode = scan_barcode()
    print(f"Código escaneado: {barcode}")

    # Buscar en supa base
    dispositivo = supabase.table("dispositivo").select("id").eq("barcode", barcode).single().execute()
    if not dispositivo.data:
        print("Dispositivo no encontrado en la base de datos.")
        return

    id_dispositivo = dispositivo.data["id"]

    # Solicitar ID de empleado
    id_empleado = input("Ingrese el ID del empleado: ")

    # Insertar registro
    data = {
        "id_empleado": int(id_empleado),
        "id_dispositivo": id_dispositivo
    }
    result = supabase.table("registro").insert(data).execute()
    if result.data:
        print("Registro subido exitosamente a Supabase.")
    else:
        print("Error al subir el registro.")

if __name__ == "__main__":
    main()