class Employee:
    def __init__(self):
        self.idEmpleado = ""
        self.employeeName = ""

    def setIDEmpleado(self, idEmpleado):
        self.idEmpleado = idEmpleado

    def getIDEmpleado(self):
        return self.idEmpleado
    
    def setEmployeeName(self, employeeName):
        self.employeeName = employeeName
    

    # Cargar employeeDB desde un archivo externo employeeDB.txt
    @staticmethod
    def load_employee_db():
        import os
        db_path = os.path.join(os.path.dirname(__file__), 'UPDATE/employeeDB.txt')
        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Evalúa el contenido como un diccionario
                db = eval(content, {"__builtins__": {}})
                if isinstance(db, dict):
                    return db
        except Exception as e:
            print(f"Error loading employeeDB.txt: {e}")
        return {}

    employeeDB = load_employee_db.__func__()

    def setEmployeeNameByID(self, idEmpleado):
        self.setEmployeeName(self.employeeDB.get(idEmpleado, "Unknown Employee"))
        return self.getEmployeeName()

    def getEmployeeName(self):
        return self.employeeName

    # Asigna ambos atributos a partir del RFID
    def setEmpleadoByRFID(self, rfid):
        self.setIDEmpleado(rfid)
        self.setEmployeeNameByID(rfid)

    # Limpia ambos atributos
    def clearEmpleado(self):
        self.idEmpleado = ""
        self.employeeName = ""
