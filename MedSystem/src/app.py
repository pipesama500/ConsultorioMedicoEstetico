from flask import Flask, render_template, redirect, url_for, request
import os
import conexionBD as db

template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
template_dir = os.path.join(template_dir, 'src', 'templates')

app = Flask(__name__, template_folder=template_dir)

# Rutas

#----------------------|Inicio Sesion|----------------------------
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Consulta a la base de datos para autenticar al usuario
        cursor = db.database.cursor()
        query = "SELECT IdUsuario, IdRol FROM Usuarios WHERE Email = %s AND Contrasena = %s"
        cursor.execute(query, (email, password))
        usuario = cursor.fetchone()
        cursor.close()
        
        if usuario:
            id_usuario, id_rol = usuario
            if id_rol == 1:  # Administrador
                return redirect(url_for('adminInicio'))
            elif id_rol == 2:  # Trabajador
                return redirect(url_for('trabajadorInicio'))
        else:
            # Credenciales inválidas
            return render_template('login.html', error='Credenciales inválidas')
    
    return render_template('login.html')

@app.route('/adminInicio')
def adminInicio():
    return render_template('adminInicio.html')

@app.route('/adminInicio.html')  # Ruta para redireccionar al inicio
def admin_inicio():
    return redirect(url_for('adminInicio'))

@app.route('/trabajadorInicio')
def trabajadorInicio():
    return render_template('trabajadorInicio.html')

@app.route('/trabajadorInicio.html')
def trabajador_inicio():
    return redirect(url_for('trabajadorInicio'))

#------------------------------------|Vistas permitidas del trabajador|---------------------------------

@app.route('/trabajadoregresos')
def trabajadoregresos():
    cursor = db.database.cursor()
    cursor.execute("SELECT e.IdEgreso, e.Concepto, e.Monto, e.Fecha, e.Observaciones, mp.NombreMetodo, m.NombreMoneda FROM Egresos e JOIN MetodosPago mp ON e.IdMetodoPago = mp.IdMetodoPago JOIN Monedas m ON e.IdMoneda = m.IdMoneda")
    egresos = cursor.fetchall()
    cursor.execute("SELECT * FROM MetodosPago")
    metodos_pago = cursor.fetchall()
    cursor.execute("SELECT * FROM Monedas")
    monedas = cursor.fetchall()
    cursor.close()
    return render_template('trabajadoregresos.html', egresos=egresos, metodos_pago=metodos_pago, monedas=monedas )

@app.route('/trabajadorpacientes')
def trabajadorpacientes():
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM Pacientes")
    pacientes = cursor.fetchall()
    cursor.close()
    return render_template('trabajadorpacientes.html', pacientes=pacientes)

@app.route('/trabajadoringresos')
def trabajadoringresos():
    cursor = db.database.cursor()
    cursor.execute("SELECT i.IdIngreso, i.Cedula, i.IdProcedimiento, i.Fecha, i.MontoTotal, i.Observaciones, i.Descuento, i.IdMetodoPago, i.IdMoneda, p.Nombre, p.Apellido, pr.NombreProcedimiento, mp.NombreMetodo, m.NombreMoneda FROM Ingresos i JOIN Pacientes p ON i.Cedula = p.Cedula JOIN Procedimientos pr ON i.IdProcedimiento = pr.IdProcedimiento JOIN MetodosPago mp ON i.IdMetodoPago = mp.IdMetodoPago JOIN Monedas m ON i.IdMoneda = m.IdMoneda")
    ingresos = cursor.fetchall()
    cursor.execute("SELECT * FROM Pacientes")
    pacientes = cursor.fetchall()
    cursor.execute("SELECT * FROM Procedimientos")
    procedimientos = cursor.fetchall()
    cursor.execute("SELECT * FROM MetodosPago")
    metodos_pago = cursor.fetchall()
    cursor.execute("SELECT * FROM Monedas")
    monedas = cursor.fetchall()
    cursor.close()
    return render_template('trabajadoringresos.html', ingresos=ingresos, pacientes=pacientes, procedimientos=procedimientos, metodos_pago=metodos_pago, monedas=monedas)

@app.route('/trabajadorcaja')
def trabajadorcaja():
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM Caja")
    movimientos_caja = cursor.fetchall()
    cursor.close()
    return render_template('trabajadorcaja.html', movimientos_caja=movimientos_caja)

#------------------------------------|Acciones permitidas del trabajador|---------------------------------

@app.route('/trabajador_edit_paciente/<int:id>', methods=['POST'])
def trabajador_editar_paciente(id):
    cedula = request.form['cedula']
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    telefono = request.form['telefono']
    correo = request.form['correo']

    cursor = db.database.cursor()
    sql = "UPDATE Pacientes SET Cedula = %s, Nombre = %s, Apellido = %s, Telefono = %s, Correo = %s WHERE cedula = %s"
    data = (cedula, nombre, apellido, telefono, correo, id)
    cursor.execute(sql, data)
    db.database.commit()
    cursor.close()

    return redirect(url_for('trabajadorpacientes'))

@app.route('/trabajador_add_paciente', methods=['POST'])
def trabajador_agregar_paciente():
    cedula = request.form['cedula']
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    telefono = request.form['telefono']
    correo = request.form['correo']

    cursor = db.database.cursor()
    sql = "INSERT INTO Pacientes (Cedula, Nombre, Apellido, Telefono, Correo) VALUES (%s, %s, %s, %s, %s)"
    data = (cedula, nombre, apellido, telefono, correo)
    cursor.execute(sql, data)
    db.database.commit()
    cursor.close()

    return redirect(url_for('trabajadorpacientes'))

@app.route('/trabajador_edit_ingreso/<int:id>', methods=['POST'])
def trabajador_edit_ingreso(id):
    cedula = request.form['cedula']
    procedimiento = request.form['procedimiento1']
    fecha = request.form['fecha']
    monto_total = request.form['monto_total1']
    metodo_pago = request.form['metodo_pago']
    moneda = request.form['moneda']
    descuento = request.form['descuento1']
    observaciones = request.form['observaciones']
    concepto = request.form['concepto1']

    cursor = db.database.cursor()
    cursor.execute("UPDATE Ingresos SET Cedula=%s, IdProcedimiento=%s, Fecha=%s, MontoTotal=%s, IdMetodoPago=%s, IdMoneda=%s, Descuento=%s, Observaciones=%s WHERE IdIngreso=%s", (cedula, procedimiento, fecha, monto_total, metodo_pago, moneda, descuento, observaciones, id))
    db.database.commit()
    
    # Actualizar el registro correspondiente en la tabla Caja
    cursor.execute("UPDATE Caja SET Fecha=%s, Concepto=%s, Monto=%s, IdMetodoPago=%s, IdMoneda=%s, Observaciones=%s WHERE IdIngreso=%s", (fecha, concepto, monto_total, metodo_pago, moneda, observaciones, id))
    db.database.commit()
    
    cursor.close()

    return redirect(url_for('trabajadoringresos'))

@app.route('/trabajador_add_ingreso', methods=['POST'])
def trabajador_add_ingreso():
    cedula = request.form['cedula']
    procedimiento = request.form['procedimiento']
    fecha = request.form['fecha']
    monto_total = request.form['monto_total']
    metodo_pago = request.form['metodo_pago']
    moneda = request.form['moneda']
    descuento = request.form['descuento']
    observaciones = request.form['observaciones']
    concepto = request.form['concepto']

    cursor = db.database.cursor()
    cursor.execute("INSERT INTO Ingresos (Cedula, IdProcedimiento, Fecha, MontoTotal, IdMetodoPago, IdMoneda, Descuento, Observaciones) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (cedula, procedimiento, fecha, monto_total, metodo_pago, moneda, descuento, observaciones))
    db.database.commit()  # Confirmar la transacción antes de obtener el ID
    ingreso_id = cursor.lastrowid  # Obtener el ID del ingreso recién insertado
    # Insertar en la tabla Caja
    cursor.execute("INSERT INTO Caja (Fecha, TipoMovimiento, IdIngreso, Concepto, Monto, IdMetodoPago, IdMoneda, Observaciones) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (fecha, 'Ingreso', ingreso_id, concepto, monto_total, metodo_pago, moneda, observaciones))
    
    db.database.commit()
    cursor.close()

    return redirect(url_for('trabajadoringresos'))

@app.route('/trabajador_edit_egreso/<int:id>', methods=['POST'])
def trabajador_edit_egreso(id):
    concepto = request.form['concepto']
    monto = request.form['monto']
    fecha = request.form['fecha']
    metodo_pago = request.form['metodo_pago']
    moneda = request.form['moneda']
    observaciones = request.form['observaciones']

    cursor = db.database.cursor()
    cursor.execute("UPDATE Egresos SET Concepto=%s, Monto=%s, Fecha=%s, IdMetodoPago=%s, IdMoneda=%s, Observaciones=%s WHERE IdEgreso=%s", (concepto, monto, fecha, metodo_pago, moneda, observaciones, id))
    db.database.commit()

    # Actualizar el registro correspondiente en la tabla Caja
    cursor.execute("UPDATE Caja SET Fecha=%s, Concepto=%s, Monto=%s, IdMetodoPago=%s, IdMoneda=%s, Observaciones=%s WHERE IdEgreso=%s", (fecha, concepto, monto, metodo_pago, moneda, observaciones, id))
    db.database.commit()

    cursor.close()

    return redirect(url_for('trabajadoregresos'))

@app.route('/trabajador_add_egreso', methods=['POST'])
def trabajador_add_egreso():
    concepto = request.form['concepto']
    monto = request.form['monto']
    fecha = request.form['fecha']
    metodo_pago = request.form['metodo_pago']
    moneda = request.form['moneda']
    observaciones = request.form['observaciones']

    cursor = db.database.cursor()
    cursor.execute("INSERT INTO Egresos (Concepto, Monto, Fecha, IdMetodoPago, IdMoneda, Observaciones) VALUES (%s, %s, %s, %s, %s, %s)", (concepto, monto, fecha, metodo_pago, moneda, observaciones))
    db.database.commit()  # Confirmar la transacción antes de obtener el ID
    egreso_id = cursor.lastrowid  # Obtener el ID del egreso recién insertado
    # Insertar en la tabla Caja
    cursor.execute("INSERT INTO Caja (Fecha, TipoMovimiento, IdEgreso, Concepto, Monto, IdMetodoPago, IdMoneda, Observaciones) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (fecha, 'Egreso', egreso_id, concepto, monto, metodo_pago, moneda, observaciones))
    
    db.database.commit()
    cursor.close()

    return redirect(url_for('trabajadoregresos'))



#------------------------------|Manejo de Roles|------------------------------

@app.route('/roles')
def roles():
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM Roles")
    roles = cursor.fetchall()
    cursor.close()
    return render_template('roles.html', roles=roles)

@app.route('/add_role', methods=['POST'])
def add_role():
    if request.method == 'POST':
        nombre = request.form['nombre']
        try:
            # Verificar si el rol ya existe en la base de datos
            cursor = db.database.cursor()
            cursor.execute("SELECT COUNT(*) FROM Roles WHERE NombreRol = %s", (nombre,))
            rol_existente = cursor.fetchone()[0] > 0
            
            if rol_existente:
                # Si el rol ya existe, cerrar el cursor y mostrar un mensaje de error
                cursor.close()
                #return render_template('roles.html', error='El rol ya existe. Por favor, elige otro.')
                return redirect(url_for('roles', error='El rol ya existe. Por favor, elige otro.'))
            else:
                # Si el rol no existe, proceder con la inserción del nuevo rol en la base de datos
                cursor.execute("INSERT INTO Roles (NombreRol) VALUES (%s)", (nombre,))
                db.database.commit()
                cursor.close()
                #return render_template('roles.html', success_msg='Rol agregado exitosamente.')
                return redirect(url_for('roles', success_msg='Rol agregado exitosamente.'))
        except db.Error as e:
            db.database.rollback()
            print("Error al agregar el rol:", e)
            return render_template('roles.html', error='Error al agregar el rol')
    else:
        return redirect(url_for('roles'))

@app.route('/edit_role/<int:id>', methods=['POST'])
def edit_role(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        cursor = db.database.cursor()
        cursor.execute("UPDATE Roles SET NombreRol = %s WHERE IdRol = %s", (nombre, id))
        db.database.commit()
        cursor.close()
    return redirect(url_for('roles'))

@app.route('/delete_role/<int:id>')
def delete_role(id):
    cursor = db.database.cursor()
    cursor.execute("DELETE FROM Roles WHERE IdRol = %s", (id,))
    db.database.commit()
    cursor.close()
    return redirect(url_for('roles'))

#------------------------------------|Manejo de usuarios|---------------------------------

@app.route('/usuarios')
def usuarios():
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM Usuarios")
    users = cursor.fetchall()
    cursor.execute("SELECT IdRol FROM Roles")
    roles = cursor.fetchall()
    cursor.close()
    return render_template('usuarios.html', users=users, roles=roles)

@app.route('/add_user', methods=['POST'])
def add_user():
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    email = request.form['email']
    contrasena = request.form['contrasena']
    idRol = request.form['idRol']

    cursor = db.database.cursor()
    cursor.execute("INSERT INTO Usuarios (Nombre, Apellido, Email, Contrasena, IdRol) VALUES (%s, %s, %s, %s, %s)", (nombre, apellido, email, contrasena, idRol))
    db.database.commit()
    cursor.close()

    return redirect(url_for('usuarios'))

@app.route('/delete_user/<int:id>')
def delete_user(id):
    cursor = db.database.cursor()
    cursor.execute("DELETE FROM Usuarios WHERE IdUsuario=%s", (id,))
    db.database.commit()
    cursor.close()
    return redirect(url_for('usuarios'))

@app.route('/edit_user/<int:id>', methods=['POST'])
def edit_user(id):
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    contrasena = request.form['contrasena']
    email = request.form['email']
    idRol = request.form['idRol']

    cursor = db.database.cursor()
    cursor.execute("UPDATE Usuarios SET Nombre=%s, Apellido=%s, Email=%s, Contrasena=%s, IdRol=%s WHERE IdUsuario=%s", (nombre, apellido, email, contrasena, idRol, id))
    db.database.commit()
    cursor.close()

    return redirect(url_for('usuarios'))

#------------------------------------|Manejo de categorias|---------------------------------

@app.route('/categorias')
def categorias():
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM Categorias")
    categorias = cursor.fetchall()
    cursor.close()
    return render_template('categorias.html', categorias=categorias)

@app.route('/add_categoria', methods=['POST'])
def add_categoria():
    nombre = request.form['nombre']

    cursor = db.database.cursor()
    cursor.execute("INSERT INTO Categorias (NombreCategoria) VALUES (%s)", (nombre,))
    db.database.commit()
    cursor.close()

    return redirect(url_for('categorias'))

@app.route('/delete_categoria/<int:id>')
def delete_categoria(id):
    cursor = db.database.cursor()
    cursor.execute("DELETE FROM Categorias WHERE IdCategoria=%s", (id,))
    db.database.commit()
    cursor.close()
    return redirect(url_for('categorias'))

@app.route('/edit_categoria/<int:id>', methods=['POST'])
def edit_categoria(id):
    nombre = request.form['nombre']

    cursor = db.database.cursor()
    cursor.execute("UPDATE Categorias SET NombreCategoria=%s WHERE IdCategoria=%s", (nombre, id))
    db.database.commit()
    cursor.close()

    return redirect(url_for('categorias'))

#------------------------------------|Manejo de proveedores|---------------------------------

@app.route('/proveedores')
def proveedores():
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM Proveedores")
    proveedores = cursor.fetchall()
    cursor.close()
    return render_template('proveedores.html', proveedores=proveedores)

@app.route('/add_proveedor', methods=['POST'])
def add_proveedor():
    nombre = request.form['nombre']
    contacto = request.form['contacto']

    cursor = db.database.cursor()
    cursor.execute("INSERT INTO Proveedores (NombreProveedor, Contacto) VALUES (%s, %s)", (nombre, contacto))
    db.database.commit()
    cursor.close()

    return redirect(url_for('proveedores'))

@app.route('/delete_proveedor/<int:id>')
def delete_proveedor(id):
    cursor = db.database.cursor()
    cursor.execute("DELETE FROM Proveedores WHERE IdProveedor=%s", (id,))
    db.database.commit()
    cursor.close()
    return redirect(url_for('proveedores'))

@app.route('/edit_proveedor/<int:id>', methods=['POST'])
def edit_proveedor(id):
    nombre = request.form['nombre']
    contacto = request.form['contacto']

    cursor = db.database.cursor()
    cursor.execute("UPDATE Proveedores SET NombreProveedor=%s, Contacto=%s WHERE IdProveedor=%s", (nombre, contacto, id))
    db.database.commit()
    cursor.close()

    return redirect(url_for('proveedores'))

#------------------------------------|Manejo de productos|---------------------------------

@app.route('/productos')
def productos():
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM Productos")
    productos = cursor.fetchall()
    cursor.execute("SELECT IdCategoria, NombreCategoria FROM Categorias")
    categorias = cursor.fetchall()
    cursor.execute("SELECT IdProveedor, NombreProveedor FROM Proveedores")
    proveedores = cursor.fetchall()
    cursor.close()
    return render_template('productos.html', productos=productos, categorias=categorias, proveedores=proveedores)

@app.route('/add_producto', methods=['POST'])
def add_producto():
    nombre = request.form['nombre']
    categoria = request.form['categoria']
    proveedor = request.form['proveedor']
    precio_compra = request.form['precio_compra']
    descripcion = request.form['descripcion']
    stock_minimo = request.form['stock_minimo']
    stock_actual = request.form['stock_actual']

    cursor = db.database.cursor()
    cursor.execute("INSERT INTO Productos (NombreProducto, IdCategoria, IdProveedor, PrecioCompra, Descripcion, StockMinimo, StockActual) VALUES (%s, %s, %s, %s, %s, %s, %s)", (nombre, categoria, proveedor, precio_compra, descripcion, stock_minimo, stock_actual))
    db.database.commit()
    cursor.close()

    return redirect(url_for('productos'))

@app.route('/delete_producto/<int:id>')
def delete_producto(id):
    cursor = db.database.cursor()
    cursor.execute("DELETE FROM Productos WHERE IdProducto=%s", (id,))
    db.database.commit()
    cursor.close()
    return redirect(url_for('productos'))

@app.route('/edit_producto/<int:id>', methods=['POST'])
def edit_producto(id):
    nombre = request.form['nombre']
    categoria = request.form['categoria']
    proveedor = request.form['proveedor']
    precio_compra = request.form['precio_compra']
    descripcion = request.form['descripcion']
    stock_minimo = request.form['stock_minimo']
   
    stock_agregar = request.form['stock_agregar']

    cursor = db.database.cursor()

    # Obtener el stock actual del producto antes de la edición
    cursor.execute("SELECT StockActual FROM Productos WHERE IdProducto=%s", (id,))
    stock_actual_anterior = cursor.fetchone()[0]

    # Calcular el nuevo stock actual sumando la cantidad a agregar
    nuevo_stock_actual = int(stock_actual_anterior) + int(stock_agregar)

    cursor.execute("UPDATE Productos SET NombreProducto=%s, IdCategoria=%s, IdProveedor=%s, PrecioCompra=%s, Descripcion=%s, StockMinimo=%s, StockActual=%s WHERE IdProducto=%s", (nombre, categoria, proveedor, precio_compra, descripcion, stock_minimo, nuevo_stock_actual, id))
    db.database.commit()
    cursor.close()

    return redirect(url_for('productos'))

#------------------------------------|Manejo de procedimientos|---------------------------------

@app.route('/procedimientos')
def procedimientos():
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM Procedimientos")
    procedimientos = cursor.fetchall()
    cursor.execute("SELECT IdProducto, NombreProducto FROM Productos")
    productos = cursor.fetchall()
    cursor.close()
    return render_template('procedimientos.html', procedimientos=procedimientos, productos=productos)

@app.route('/add_procedimiento', methods=['POST'])
def add_procedimiento():
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio_venta = request.form['precio_venta']
    producto_principal = request.form['producto_principal']

    cursor = db.database.cursor()
    cursor.execute("INSERT INTO Procedimientos (NombreProcedimiento, Descripcion, PrecioVenta, IdProductoPrincipal) VALUES (%s, %s, %s, %s)", (nombre, descripcion, precio_venta, producto_principal))
    db.database.commit()
    cursor.close()

    return redirect(url_for('procedimientos'))

@app.route('/edit_procedimiento/<int:id>', methods=['POST'])
def edit_procedimiento(id):
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio_venta = request.form['precio_venta']
    producto_principal = request.form['producto_principal']

    cursor = db.database.cursor()
    cursor.execute("UPDATE Procedimientos SET NombreProcedimiento=%s, Descripcion=%s, PrecioVenta=%s, IdProductoPrincipal=%s WHERE IdProcedimiento=%s", (nombre, descripcion, precio_venta, producto_principal, id))
    db.database.commit()
    cursor.close()

    return redirect(url_for('procedimientos'))

@app.route('/delete_procedimiento/<int:id>')
def delete_procedimiento(id):
    cursor = db.database.cursor()
    cursor.execute("DELETE FROM Procedimientos WHERE IdProcedimiento=%s", (id,))
    db.database.commit()
    cursor.close()
    return redirect(url_for('procedimientos'))

#------------------------------------|Manejo de pacientes|---------------------------------

@app.route('/pacientes')
def listar_pacientes():
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM Pacientes")
    pacientes = cursor.fetchall()
    cursor.close()
    return render_template('pacientes.html', pacientes=pacientes)

# Ruta para agregar un paciente
@app.route('/add_paciente', methods=['POST'])
def agregar_paciente():
    cedula = request.form['cedula']
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    telefono = request.form['telefono']
    correo = request.form['correo']

    cursor = db.database.cursor()
    sql = "INSERT INTO Pacientes (Cedula, Nombre, Apellido, Telefono, Correo) VALUES (%s, %s, %s, %s, %s)"
    data = (cedula, nombre, apellido, telefono, correo)
    cursor.execute(sql, data)
    db.database.commit()
    cursor.close()

    return redirect(url_for('listar_pacientes'))

# Ruta para editar un paciente
@app.route('/edit_paciente/<int:id>', methods=['POST'])
def editar_paciente(id):
    cedula = request.form['cedula']
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    telefono = request.form['telefono']
    correo = request.form['correo']

    cursor = db.database.cursor()
    sql = "UPDATE Pacientes SET Cedula = %s, Nombre = %s, Apellido = %s, Telefono = %s, Correo = %s WHERE cedula = %s"
    data = (cedula, nombre, apellido, telefono, correo, id)
    cursor.execute(sql, data)
    db.database.commit()
    cursor.close()

    return redirect(url_for('listar_pacientes'))

# Ruta para eliminar un paciente
@app.route('/delete_paciente/<int:id>')
def eliminar_paciente(id):
    cursor = db.database.cursor()
    sql = "DELETE FROM Pacientes WHERE IdPaciente = %s"
    data = (id,)
    cursor.execute(sql, data)
    db.database.commit()
    cursor.close()

    return redirect(url_for('listar_pacientes'))

#------------------------------------|Manejo de ingresos|---------------------------------


@app.route('/ingresoAdmin')
def ingresos():
    cursor = db.database.cursor()
    cursor.execute("SELECT i.IdIngreso, i.Cedula, i.IdProcedimiento, i.Fecha, i.MontoTotal, i.Observaciones, i.Descuento, i.IdMetodoPago, i.IdMoneda, p.Nombre, p.Apellido, pr.NombreProcedimiento, mp.NombreMetodo, m.NombreMoneda FROM Ingresos i JOIN Pacientes p ON i.Cedula = p.Cedula JOIN Procedimientos pr ON i.IdProcedimiento = pr.IdProcedimiento JOIN MetodosPago mp ON i.IdMetodoPago = mp.IdMetodoPago JOIN Monedas m ON i.IdMoneda = m.IdMoneda")
    ingresos = cursor.fetchall()
    cursor.execute("SELECT * FROM Pacientes")
    pacientes = cursor.fetchall()
    cursor.execute("SELECT * FROM Procedimientos")
    procedimientos = cursor.fetchall()
    cursor.execute("SELECT * FROM MetodosPago")
    metodos_pago = cursor.fetchall()
    cursor.execute("SELECT * FROM Monedas")
    monedas = cursor.fetchall()
    cursor.close()
    return render_template('ingresoAdmin.html', ingresos=ingresos, pacientes=pacientes, procedimientos=procedimientos, metodos_pago=metodos_pago, monedas=monedas)

@app.route('/add_ingreso', methods=['POST'])
def add_ingreso():
    cedula = request.form['cedula']
    procedimiento = request.form['procedimiento']
    fecha = request.form['fecha']
    monto_total = request.form['monto_total']
    metodo_pago = request.form['metodo_pago']
    moneda = request.form['moneda']
    descuento = request.form['descuento']
    observaciones = request.form['observaciones']
    concepto = request.form['concepto']

    cursor = db.database.cursor()
    cursor.execute("INSERT INTO Ingresos (Cedula, IdProcedimiento, Fecha, MontoTotal, IdMetodoPago, IdMoneda, Descuento, Observaciones) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (cedula, procedimiento, fecha, monto_total, metodo_pago, moneda, descuento, observaciones))
    db.database.commit()  # Confirmar la transacción antes de obtener el ID
    ingreso_id = cursor.lastrowid  # Obtener el ID del ingreso recién insertado
    # Insertar en la tabla Caja
    cursor.execute("INSERT INTO Caja (Fecha, TipoMovimiento, IdIngreso, Concepto, Monto, IdMetodoPago, IdMoneda, Observaciones) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (fecha, 'Ingreso', ingreso_id, concepto, monto_total, metodo_pago, moneda, observaciones))
    
    db.database.commit()
    cursor.close()

    return redirect(url_for('ingresos'))

@app.route('/edit_ingreso/<int:id>', methods=['POST'])
def edit_ingreso(id):
    cedula = request.form['cedula']
    procedimiento = request.form['procedimiento1']
    fecha = request.form['fecha']
    monto_total = request.form['monto_total1']
    metodo_pago = request.form['metodo_pago']
    moneda = request.form['moneda']
    descuento = request.form['descuento1']
    observaciones = request.form['observaciones']
    concepto = request.form['concepto1']

    cursor = db.database.cursor()
    cursor.execute("UPDATE Ingresos SET Cedula=%s, IdProcedimiento=%s, Fecha=%s, MontoTotal=%s, IdMetodoPago=%s, IdMoneda=%s, Descuento=%s, Observaciones=%s WHERE IdIngreso=%s", (cedula, procedimiento, fecha, monto_total, metodo_pago, moneda, descuento, observaciones, id))
    db.database.commit()
    
    # Actualizar el registro correspondiente en la tabla Caja
    cursor.execute("UPDATE Caja SET Fecha=%s, Concepto=%s, Monto=%s, IdMetodoPago=%s, IdMoneda=%s, Observaciones=%s WHERE IdIngreso=%s", (fecha, concepto, monto_total, metodo_pago, moneda, observaciones, id))
    db.database.commit()
    
    cursor.close()

    return redirect(url_for('ingresos'))

@app.route('/delete_ingreso/<int:id>')
def delete_ingreso(id):
    cursor = db.database.cursor()
    
    # Obtener el ID de ingreso correspondiente en la tabla Caja
    cursor.execute("SELECT IdIngreso FROM Caja WHERE IdIngreso=%s", (id,))
    caja_id = cursor.fetchone()
    
    if caja_id:
        caja_id = caja_id[0]
        
        # Eliminar el registro correspondiente en la tabla Caja
        cursor.execute("DELETE FROM Caja WHERE IdIngreso=%s", (caja_id,))
        db.database.commit()
    
    # Eliminar el registro de la tabla Ingresos
    cursor.execute("DELETE FROM Ingresos WHERE IdIngreso=%s", (id,))
    db.database.commit()
    
    cursor.close()
    
    return redirect(url_for('ingresos'))



#------------------------------------|Manejo de egresos|---------------------------------

@app.route('/egresos')
def egresos():
    cursor = db.database.cursor()
    cursor.execute("SELECT e.IdEgreso, e.Concepto, e.Monto, e.Fecha, e.Observaciones, mp.NombreMetodo, m.NombreMoneda FROM Egresos e JOIN MetodosPago mp ON e.IdMetodoPago = mp.IdMetodoPago JOIN Monedas m ON e.IdMoneda = m.IdMoneda")
    egresos = cursor.fetchall()
    cursor.execute("SELECT * FROM MetodosPago")
    metodos_pago = cursor.fetchall()
    cursor.execute("SELECT * FROM Monedas")
    monedas = cursor.fetchall()
    cursor.close()
    return render_template('egresos.html', egresos=egresos, metodos_pago=metodos_pago, monedas=monedas)

@app.route('/add_egreso', methods=['POST'])
def add_egreso():
    concepto = request.form['concepto']
    monto = request.form['monto']
    fecha = request.form['fecha']
    metodo_pago = request.form['metodo_pago']
    moneda = request.form['moneda']
    observaciones = request.form['observaciones']

    cursor = db.database.cursor()
    cursor.execute("INSERT INTO Egresos (Concepto, Monto, Fecha, IdMetodoPago, IdMoneda, Observaciones) VALUES (%s, %s, %s, %s, %s, %s)", (concepto, monto, fecha, metodo_pago, moneda, observaciones))
    db.database.commit()  # Confirmar la transacción antes de obtener el ID
    egreso_id = cursor.lastrowid  # Obtener el ID del egreso recién insertado
    # Insertar en la tabla Caja
    cursor.execute("INSERT INTO Caja (Fecha, TipoMovimiento, IdEgreso, Concepto, Monto, IdMetodoPago, IdMoneda, Observaciones) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (fecha, 'Egreso', egreso_id, concepto, monto, metodo_pago, moneda, observaciones))
    
    db.database.commit()
    cursor.close()

    return redirect(url_for('egresos'))

@app.route('/edit_egreso/<int:id>', methods=['POST'])
def edit_egreso(id):
    concepto = request.form['concepto']
    monto = request.form['monto']
    fecha = request.form['fecha']
    metodo_pago = request.form['metodo_pago']
    moneda = request.form['moneda']
    observaciones = request.form['observaciones']

    cursor = db.database.cursor()
    cursor.execute("UPDATE Egresos SET Concepto=%s, Monto=%s, Fecha=%s, IdMetodoPago=%s, IdMoneda=%s, Observaciones=%s WHERE IdEgreso=%s", (concepto, monto, fecha, metodo_pago, moneda, observaciones, id))
    db.database.commit()

    # Actualizar el registro correspondiente en la tabla Caja
    cursor.execute("UPDATE Caja SET Fecha=%s, Concepto=%s, Monto=%s, IdMetodoPago=%s, IdMoneda=%s, Observaciones=%s WHERE IdEgreso=%s", (fecha, concepto, monto, metodo_pago, moneda, observaciones, id))
    db.database.commit()

    cursor.close()

    return redirect(url_for('egresos'))

@app.route('/delete_egreso/<int:id>')
def delete_egreso(id):
    cursor = db.database.cursor()

    # Obtener el ID de egreso correspondiente en la tabla Caja
    cursor.execute("SELECT IdEgreso FROM Caja WHERE IdEgreso=%s", (id,))
    caja_id = cursor.fetchone()

    if caja_id:
        caja_id = caja_id[0]

        # Eliminar el registro correspondiente en la tabla Caja
        cursor.execute("DELETE FROM Caja WHERE IdEgreso=%s", (caja_id,))
        db.database.commit()

    # Eliminar el registro de la tabla Egresos
    cursor.execute("DELETE FROM Egresos WHERE IdEgreso=%s", (id,))
    db.database.commit()

    cursor.close()

    return redirect(url_for('egresos'))

#------------------------------------|Manejo de monedas|---------------------------------

@app.route('/monedas')
def monedas():
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM Monedas")
    monedas = cursor.fetchall()
    cursor.close()
    return render_template('monedas.html', monedas=monedas)

@app.route('/add_moneda', methods=['POST'])
def add_moneda():
    if request.method == 'POST':
        nombre = request.form['nombre']
        cursor = db.database.cursor()
        cursor.execute("INSERT INTO Monedas (NombreMoneda) VALUES (%s)", (nombre,))
        db.database.commit()
        cursor.close()
    return redirect(url_for('monedas'))

@app.route('/edit_moneda/<int:id>', methods=['POST'])
def edit_moneda(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        cursor = db.database.cursor()
        cursor.execute("UPDATE Monedas SET NombreMoneda = %s WHERE IdMoneda = %s", (nombre, id))
        db.database.commit()
        cursor.close()
    return redirect(url_for('monedas'))

@app.route('/delete_moneda/<int:id>')
def delete_moneda(id):
    cursor = db.database.cursor()
    cursor.execute("DELETE FROM Monedas WHERE IdMoneda = %s", (id,))
    db.database.commit()
    cursor.close()
    return redirect(url_for('monedas'))

#------------------------------------|Manejo de metodoPago|---------------------------------

@app.route('/metodoPago')
def metodoPago():
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM MetodosPago")
    metodos_pago = cursor.fetchall()
    cursor.close()
    return render_template('metodoPago.html', metodos_pago=metodos_pago)

# Ruta para agregar un método de pago
@app.route('/add_metodo_pago', methods=['POST'])
def agregar_metodo_pago():
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']

    cursor = db.database.cursor()
    sql = "INSERT INTO MetodosPago (NombreMetodo, Descripcion) VALUES (%s, %s)"
    data = (nombre, descripcion)
    cursor.execute(sql, data)
    db.database.commit()
    cursor.close()

    return redirect(url_for('metodoPago'))

# Ruta para editar un método de pago
@app.route('/edit_metodo_pago/<int:id>', methods=['POST'])
def editar_metodo_pago(id):
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']

    cursor = db.database.cursor()
    sql = "UPDATE MetodosPago SET NombreMetodo = %s, Descripcion = %s WHERE IdMetodoPago = %s"
    data = (nombre, descripcion, id)
    cursor.execute(sql, data)
    db.database.commit()
    cursor.close()

    return redirect(url_for('metodoPago'))

# Ruta para eliminar un método de pago
@app.route('/delete_metodo_pago/<int:id>')
def eliminar_metodo_pago(id):
    cursor = db.database.cursor()
    cursor.execute("DELETE FROM MetodosPago WHERE IdMetodoPago = %s", (id,))
    db.database.commit()
    cursor.close()
    return redirect(url_for('metodoPago'))

#------------------------------------|Manejo de caja|---------------------------------

@app.route('/caja')
def caja():
    cursor = db.database.cursor()
    cursor.execute("SELECT * FROM Caja")
    movimientos_caja = cursor.fetchall()
    cursor.close()
    return render_template('caja.html', movimientos_caja=movimientos_caja)

@app.route('/edit_movimiento_caja/<int:id>', methods=['POST'])
def edit_movimiento_caja(id):
    fecha = request.form['fecha']
    tipo_movimiento = request.form['tipo_movimiento']
    concepto = request.form['concepto']
    monto = request.form['monto']
    id_metodo_pago = request.form['id_metodo_pago']
    id_moneda = request.form['id_moneda']
    observaciones = request.form['observaciones']

    cursor = db.database.cursor()
    cursor.execute("UPDATE Caja SET Fecha=%s, TipoMovimiento=%s, Concepto=%s, Monto=%s, IdMetodoPago=%s, IdMoneda=%s, Observaciones=%s WHERE IdMovimiento=%s", (fecha, tipo_movimiento, concepto, monto, id_metodo_pago, id_moneda, observaciones, id))
    db.database.commit()
    cursor.close()

    return redirect(url_for('caja'))

@app.route('/delete_movimiento_caja/<int:id>')
def delete_movimiento_caja(id):
    cursor = db.database.cursor()
    cursor.execute("DELETE FROM Caja WHERE IdMovimiento=%s", (id,))
    db.database.commit()
    cursor.close()
    return redirect(url_for('caja'))

if __name__ == '__main__':
    app.run(debug=True, port=4500)