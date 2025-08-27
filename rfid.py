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
 
    # Dictionary  
    employeeDB = {
        "db9036ab": "Ivanovich Chiu",
        "de125fcb": "Andres Gonzalez"
    }

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
