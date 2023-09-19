import psycopg2
from sys import stdin


try: #se conecta con la base de datos
    connection = psycopg2.connect( 
        host = 'localhost',
        user = 'postgres',
        password = 'juan2013',
        database = 'postgres',
        port = '5433'
    )
    print("conexión exitosa")
except Exception as ex: print(ex)

cursordb = connection.cursor() #cursor que hara todas las operaciones



#guardamos la fecha actual
cursordb.execute("SELECT current_timestamp")
fechahoy = cursordb.fetchone()[0]

def crearTablas(): #crea todas las tablas iniciales
    cursordb.execute('''CREATE TABLE CLIENTE (cedula INTEGER PRIMARY KEY, nombre TEXT, puntos INTEGER)''') #cliente
    cursordb.execute('''CREATE TABLE INVENTARIO (codigo SERIAL PRIMARY KEY
                    , nombre TEXT, cantidad INTEGER, proveedor INTEGER,
                     precio INTEGER)''') #inventario/productos
    cursordb.execute('''CREATE TABLE CAJERO (cedula INTEGER PRIMARY KEY, nombre TEXT, caja INTEGER)''') #cajero
    cursordb.execute('''CREATE TABLE ADMIN (cedula INTEGER PRIMARY KEY, clave INTEGER)''') #administrador
    cursordb.execute('''CREATE TABLE PROVEEDOR (numero SERIAL PRIMARY KEY, clave INTEGER)''') #proveedor
    cursordb.execute('''CREATE TABLE PRODPROOV (numprov INTEGER REFERENCES PROVEEDOR(numero),
                    codprod INTEGER REFERENCES INVENTARIO(codigo),
                     PRIMARY KEY(numprov, codprod))''')#proveedor-producto
    cursordb.execute('''CREATE TABLE VENTA (id INTEGER PRIMARY KEY, total INTEGER, fecha DATE)''') #venta
    cursordb.execute('''CREATE TABLE VENTAPROD ( 
                    codprod INTEGER REFERENCES INVENTARIO(codigo),
                    idventa INTEGER,
                    cantidad INTEGER,
                    PRIMARY KEY (codprod, idventa))''') #venta-producto
    cursordb.execute('''INSERT INTO CAJERO (cedula, nombre, caja) VALUES
                        (1007370990, 'Ana López', 1),
                        (1005789321, 'Pedro Martínez', 2),
                        (1010598541, 'Sofía Ramírez', 1),
                        (1015374936, 'Luis González', 2);''')

    cursordb.execute('''INSERT INTO ADMIN (cedula, clave) VALUES
                        (1001874208, 12345),
                        (1002162306, 67890);''')

    cursordb.execute('''INSERT INTO PROVEEDOR (clave) VALUES
                        (2001),
                        (2002);''')

    cursordb.execute('''INSERT INTO INVENTARIO (nombre, cantidad, proveedor, precio) VALUES
                        ('Arroz', 100, 1, 5100),
                        ('Leche', 200, 2, 4700),
                        ('Pan', 150, 3, 3000),
                        ('Huevos', 300, 1, 18000),
                        ('Aceite de cocina', 50, 2, 7500);''')

    cursordb.execute('''INSERT INTO PRODPROOV (numprov, codprod) VALUES
                        (1, 1),
                        (2, 2),
                        (1, 3),
                        (2, 4),
                        (1, 5);''')


def resumenVent(): #el administrador pide un resumen de todas las ventas que se han hecho
    cursordb.execute("SELECT id,total,fecha FROM VENTA")
    for id, total, fecha in cursordb.fetchall():
        print("La venta ", id, "que se hizo el ", fecha, "tuvo un total de ",total)

def verCajeros(): #el administrador ve la informacion de los cajeros 
    cursordb.execute("SELECT nombre,caja FROM CAJERO")
    for nombre, caja in cursordb.fetchall():
        print(nombre, " esta asignado a la caja ",caja)
    
def informeProv(numProv): #el proveedor pide informe de ventas de sus productos
    cursordb.execute('''SELECT COUNT(numero) FROM PROVEEDOR WHERE numero = '{}' '''.format(numProv))
    if cursordb.fetchone() == 0: #si el proveedor no existe
        print("Error: Numero de proveedor invalido\n")
    else:#imprimir el reporte
        cursordb.execute("SELECT codprod FROM PRODPROOV WHERE numprov = '{}'" .format(numProv)) #para todos los productos
        producprov = cursordb.fetchall()
        suma = 0
        for producto in producprov:
            codprod = producto[0] #escoge el codigo del producto que es la primera posicion
            cursordb.execute("SELECT SUM(cantidad) FROM VENTAPROD WHERE codprod = '{}'".format(codprod))
            cantvend = cursordb.fetchone()[0] or 0 #0 si no se ha vendido
            cursordb.execute("SELECT precio, nombre FROM INVENTARIO WHERE codigo = '{}'".format(codprod))
            todo = cursordb.fetchone()
            precio = todo[0]
            nombre = todo[1]
            totalprod= cantvend * precio
            print("El producto ",nombre," se vendio ", cantvend, " veces y recaudo ", totalprod)
            suma += totalprod
        print("Total de ventas para el proveedor ",numProv, " es ", suma)

def topFive():
    cursordb.execute('''
        SELECT INVENTARIO.nombre, SUM(VENTAPROD.cantidad) as cantidad_vendida
        FROM VENTAPROD
        INNER JOIN INVENTARIO ON VENTAPROD.codprod = INVENTARIO.codigo
        GROUP BY INVENTARIO.nombre
        ORDER BY cantidad_vendida DESC
        LIMIT 5;
    ''')
    topCinco = cursordb.fetchall()
    i = 1
    for nombre, cant in topCinco:
        print(i, ".)", nombre, " ", cant)
        i+=1
def agregarUsuario(cedula, nombre):
    cursordb.execute('''SELECT COUNT(cedula) FROM CLIENTE WHERE cedula = '{}' '''.format(cedula))
    if cursordb.fetchone()[0] !=0: 
        print("Error: La cedula ya esta asignada a un usuario\n")
    else:
        cursordb.execute('''insert into cliente(cedula,nombre,puntos) values ('{}','{}',0)'''.format(cedula,nombre))

def agregarProducto(nombre, cantidad, proveedor, precio):
    cursordb.execute('''SELECT COUNT(nombre) FROM INVENTARIO WHERE nombre = '{}' '''.format(nombre))
    if cursordb.fetchone()[0] !=0: print("El producto ya existe")
    else: 
        cursordb.execute('''insert into inventario(nombre, cantidad, proveedor, precio) values ('{}','{}','{}','{}')'''.format(nombre,cantidad,proveedor,precio))

def vender(fecha):
    total = 0
    print("1.Usuario registrado\n2.Usuario no registrado\n3.Usuario nuevo\nOpc:")
    opc = int(input())
    if opc == 1:
        print("Ingrese la cedula del usuario:")
        ced = int(input())
    if opc == 3:
        print("Ingrese la cedula del usuario:")
        ced = int(input())
        print("Ingrese el nombre del usuario:")
        nomb = stdin.readline()
        agregarUsuario(ced,nomb)
    cursordb.execute("SELECT max(id) FROM VENTA")
    actventa = cursordb.fetchone()[0] or 0  # Si no hay ventas, comienza desde 0
    print("Elija como buscar producto:\n1.Codigo\n2.Nombre\n0.Salir\nOpc:")
    op2 = int(input())
    while op2 != 0:
        if op2 == 1:
            print("Ingrese el codigo: ")
            cod = int(input())
            cursordb.execute('''SELECT nombre,precio FROM INVENTARIO WHERE codigo = '{}' '''.format(cod))
            todo = cursordb.fetchone()
            nombre = todo[0]
            precio = todo[1]
        elif op2 == 2:
            print("Ingrese el nombre: ")
            nombre = stdin.readline().strip()
            cursordb.execute('''SELECT codigo,precio FROM INVENTARIO WHERE nombre = '{}' '''.format(nombre))
            todo = cursordb.fetchone()
            print(todo)
            cod = todo[0]
            precio = todo[1]
        print("Cuantos ", nombre, "va a comprar: ")
        cant = int(input())
        cursordb.execute('''SELECT cantidad FROM INVENTARIO WHERE codigo = '{}' '''.format(cod))
        cantdisp = cursordb.fetchone()[0]
        if cant > cantdisp: print("No hay suficientes existencias de ese producto")
        else:
            total += precio * cant
            newcant = cantdisp - cant
            if newcant < 50:
                print("El suministro del producto ", nombre,  " está bajo")
            cursordb.execute('''UPDATE INVENTARIO SET cantidad = '{}' WHERE codigo = '{}' '''.format(newcant,cod))
            cursordb.execute("INSERT INTO VENTAPROD (idventa, codprod, cantidad) VALUES ('{}', '{}', '{}')".format(actventa + 1, cod, cant))
        print("Elija como buscar producto:\n1.Codigo\n2.Nombre\n0.Salir\nOpc:")
        op2 = int(input())
    cursordb.execute("INSERT INTO VENTA (id, total, fecha) VALUES ('{}', '{}', '{}')".format(actventa + 1, total, fecha))
    puntos = int(total/100)
    print(puntos)
    if opc == 1 or opc == 3:
        cursordb.execute('''SELECT puntos FROM CLIENTE WHERE cedula = '{}' '''.format(ced))
        oldpoints = cursordb.fetchone()[0] or 0
        cursordb.execute('''UPDATE CLIENTE SET puntos = '{}' WHERE cedula = '{}' '''.format(puntos + oldpoints,ced))

def consVent():
    print("Ingrese el id de la venta al consultar: ")
    id = int(input())
    cursordb.execute('''SELECT COUNT(id) FROM VENTA WHERE id = '{}' '''.format(id))
    if cursordb.fetchone()[0] == 0: print("Esa venta no existe\n")
    else:
        print("En la venta ", id, "se vendieron los siguientes productos:\n")
        cursordb.execute("SELECT codprod, cantidad FROM VENTAPROD WHERE idventa = '{}'".format(id))
        prodvend = cursordb.fetchall()
        for producto in prodvend:
            cod = producto[0]
            cantidad = producto[1]
            cursordb.execute("SELECT nombre FROM INVENTARIO WHERE codigo = '{}' ".format(cod))
            nombre = cursordb.fetchone()[0]
            print(nombre,"X",cantidad)

def menuAdmin(): #resumen de ventas,  ver cajeros
    print("Escoja una opcion:\n1.Resumen de ventas\n2.Ver cajeros\n3.Consultar venta\n4.Top productos\nOpc:")
    opc = int(input())
    if opc == 1: resumenVent()
    elif opc == 2: verCajeros()
    elif opc == 3: consVent()
    elif opc == 4: topFive()
    else: print("Error: La opcion dada es invalido\n")

def menuProveedor(num):
    print("Escoja una opcion:\n1.Resumen de venta de sus productos\n2.Agregar producto\nOpc:")
    opc = int(input())
    if opc == 1:
        informeProv(num)
    if opc == 2:
        print("Nombre de producto(Primera letra siempre en mayuscula:\n)")
        nombre = stdin.readline().strip()
        print("Cantidad de producto:\n)")
        cantidad = int(input())
        print("Precio de producto:\n)")
        precio = int(input())
        agregarProducto(nombre, cantidad, num, precio)
    

def menu():
    print("**********************************************************Bienvenido**********************************************************")
    print("Ingrese su rol:\n1.Administrador\n2.Cajero\n3.Proveedor\n0.Salir\nOpc: ")
    opc = int(input())
    if opc == 1: #administrador
        print("Ingrese la cedula:")
        ced = int(input())
        print("Ingrese la clave:")
        clave = int(input())
        cursordb.execute('''SELECT clave FROM ADMIN WHERE cedula = '{}' '''.format(ced))
        if cursordb.fetchone()[0] == clave: menuAdmin()
        else: print("Clave incorrecta")
    elif opc == 2: #cajero
        (print("Ingresando a venta...\n"))
        vender(fechahoy)
    elif opc == 3:#proveedor
        print("Ingrese el numero de proveedor:")
        ced = int(input())
        print("Ingrese la clave:")
        clave = int(input())
        cursordb.execute('''SELECT clave FROM PROVEEDOR WHERE numero = '{}' '''.format(ced))
        if cursordb.fetchone()[0] == clave: menuProveedor(ced)
        else: 
            print("Clave incorrecta")
    elif opc == 0: return 0
    else: print("Error: Entrada invalida\n")
    menu()

#crearTablas()
menu()
connection.commit()
cursordb.close()
connection.close()

