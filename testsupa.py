from dotenv import load_dotenv
load_dotenv()

import os
from supabase import create_client, Client

# import from scan.py
from scan import read_barcode

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)


# UPDATE
# response = (
#     supabase.table("automation")
#     .update({"empleado": "iva"})
#     .eq("id", 4)
#     .execute()
# )
barcode = read_barcode()
if barcode and not barcode.startswith("ERROR"):
    # Insertar en Supabase
    response = (
        supabase.table("registro")
        .insert({"empleado": "PEDRO", "barcode": barcode})
        .execute()
    )
    print("Insert response:", response)
else:
    print("No se pudo obtener un código de barras válido.")



# # INSERT
# response = (
#     supabase.table("automation")
#     .insert({"empleado": "iva", "barcode": "KINGHEARTS"})
#     .execute()
# )
# print(select.data)

# DELETE
# response = (
#     supabase.table("automation")
#     .delete()
#     .eq("id", 3)
#     .execute()
# )

# SELECT  
select = (
    supabase.table("registro")
    .select("*") # Select 
    # .eq("id", 3) #Where 
    .execute() # Run the query
)
print(select.data)
