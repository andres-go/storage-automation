import serial
import serial.tools.list_ports
import time


# Mostrar todos los puertos para saber sus nombres (raspPi "\dev\ttyACM0 description: DM150 Reader")
# Nombre de puertos varian en dispositivo 
#for port in ports:-
 #   print(f"Port: {port.device}, Description: {port.description}")

# 2. Buscar puerto con la descripcion DM150 Reader
def find_dataman_port():
    # 1. Buscar el puerto
    ports = serial.tools.list_ports.comports()

    for port in ports:
        if "DataMan" in port.description:
            # print(f"Found DataMan device at {port.device}")

            return port.device
    print("ERROR : DataMan device not found.")
    return None

# 3. Leer barcode
def read_barcode():

    # Asignar puerto encontrado con find_dataman_port()
    port = find_dataman_port()
    # print(f"Port: {port}")
    if not port:
        return

    # Inicializar Serial
    try:
        # Configuraciones del DataMan 
        ser = serial.Serial(port, 115200, timeout=1, rtscts=True)
        # print(f"Connected to port {ser}")

        #  Inicializar temporizador (5 segundos para escanear)
        start_time = time.time()
        while time.time() - start_time < 5:
            if ser.in_waiting > 0:
                # print("Waiting for barcode...")

                # leer linea pasada por serial, al acabar la linea termina el mensaje
                # .decode() evtia carateres no deseados
                barcode = ser.readline().decode('utf-8').strip()
                print(f'Barcode scanned: {barcode}')

                if(barcode):
                    return barcode
        else:
            # No data  
            #print("ERROR : No barcode detected in 5 seconds.")
            return "ERROR : No barcode detected in 5 seconds."


    #  Captar error y mostrar 
    except Exception as e:
        print(f"ERROR : {e}")
    
    #  Cerrar conexion serial 
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            #print("Serial connection closed.")

# Ejecutar código 
if __name__ == '__main__':
    read_barcode()