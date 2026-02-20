import tkinter as tk
from tkinter import messagebox
import mysql.connector
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# ---------------- CONEXIÓN MYSQL ----------------
conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # Cambia si tu XAMPP tiene contraseña
    database="banco"
)
cursor = conexion.cursor(buffered=True)

# ---------------- VARIABLES GLOBALES ----------------
usuario_actual_id = None  # Guardará el ID del usuario que ingresó

# ---------------- FUNCIONES ----------------
def obtener_saldo():
    cursor.execute("SELECT saldo FROM usuarios WHERE id = %s", (usuario_actual_id,))
    resultado = cursor.fetchone()
    return resultado[0] if resultado else 0

def actualizar_saldo(nuevo_saldo):
    cursor.execute("UPDATE usuarios SET saldo = %s WHERE id = %s", (nuevo_saldo, usuario_actual_id))
    conexion.commit()
    lbl_saldo.config(text=f"Saldo: ${nuevo_saldo}")

def ingresar():
    try:
        monto = int(entry_monto.get())
        if monto <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Ingrese un monto válido")
        return

    saldo = obtener_saldo() + monto
    actualizar_saldo(saldo)

    fecha = datetime.now()
    cursor.execute(
        "INSERT INTO movimientos (usuario_id, fecha, tipo, monto) VALUES (%s, %s, %s, %s)",
        (usuario_actual_id, fecha, "Ingreso", monto)
    )
    conexion.commit()

    messagebox.showinfo("Éxito", f"Ingresó ${monto}")
    entry_monto.delete(0, tk.END)

def retirar():
    try:
        monto = int(entry_monto.get())
        if monto <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Ingrese un monto válido")
        return

    saldo_actual = obtener_saldo()
    if monto > saldo_actual:
        messagebox.showerror("Error", "Saldo insuficiente")
        return

    saldo = saldo_actual - monto
    actualizar_saldo(saldo)

    fecha = datetime.now()
    cursor.execute(
        "INSERT INTO movimientos (usuario_id, fecha, tipo, monto) VALUES (%s, %s, %s, %s)",
        (usuario_actual_id, fecha, "Retiro", monto)
    )
    conexion.commit()

    messagebox.showinfo("Éxito", f"Retiró ${monto}")
    entry_monto.delete(0, tk.END)

def ver_movimientos():
    ventana = tk.Toplevel(root)
    ventana.title("Movimientos")

    texto = tk.Text(ventana, width=50, height=15)
    texto.pack(padx=10, pady=10)

    cursor.execute("SELECT fecha, tipo, monto FROM movimientos WHERE usuario_id = %s ORDER BY fecha DESC", (usuario_actual_id,))
    filas = cursor.fetchall()

    if not filas:
        texto.insert(tk.END, "No hay movimientos registrados")
    else:
        for f in filas:
            texto.insert(tk.END, f"{f[0]} - {f[1]}: ${f[2]}\n")

def exportar_pdf():
    cursor.execute("SELECT fecha, tipo, monto FROM movimientos WHERE usuario_id = %s ORDER BY fecha DESC", (usuario_actual_id,))
    filas = cursor.fetchall()

    if not filas:
        messagebox.showinfo("Info", "No hay movimientos para exportar")
        return

    archivo_pdf = f"movimientos_usuario{usuario_actual_id}.pdf"
    c = canvas.Canvas(archivo_pdf, pagesize=letter)
    c.setFont("Helvetica", 12)

    c.drawString(50, 750, f"Movimientos del usuario {usuario_actual_id}")
    y = 720
    c.drawString(50, y, "Fecha - Tipo - Monto")
    y -= 20

    for f in filas:
        texto = f"{f[0]} - {f[1]} - ${f[2]}"
        c.drawString(50, y, texto)
        y -= 20
        if y < 50:  # Nueva página si se llena
            c.showPage()
            c.setFont("Helvetica", 12)
            y = 750

    c.save()
    messagebox.showinfo("Éxito", f"PDF creado: {archivo_pdf}")

def cerrar_aplicacion():
    conexion.close()
    root.destroy()

# ---------------- LOGIN POR DOCUMENTO ----------------
def login():
    global usuario_actual_id
    doc = entry_doc.get()
    cursor.execute("SELECT id FROM usuarios WHERE documento = %s", (doc,))
    resultado = cursor.fetchone()
    if resultado:
        usuario_actual_id = resultado[0]
        login_window.destroy()
        iniciar_app()
    else:
        messagebox.showerror("Error", "Documento no registrado")

# ---------------- INICIAR APLICACIÓN ----------------
def iniciar_app():
    global root, lbl_saldo, entry_monto, btn_ingresar, btn_retirar, btn_mov, btn_pdf, btn_salir

    root = tk.Tk()
    root.title("Banco - Multiusuario")

    lbl_saldo = tk.Label(root, text=f"Saldo: ${obtener_saldo()}", font=("Arial", 14))
    lbl_saldo.pack(pady=10)

    entry_monto = tk.Entry(root)
    entry_monto.pack(pady=5)

    btn_ingresar = tk.Button(root, text="Ingresar dinero", command=ingresar)
    btn_ingresar.pack(pady=5)

    btn_retirar = tk.Button(root, text="Retirar dinero", command=retirar)
    btn_retirar.pack(pady=5)

    btn_mov = tk.Button(root, text="Ver movimientos", command=ver_movimientos)
    btn_mov.pack(pady=5)

    btn_pdf = tk.Button(root, text="Exportar PDF", command=exportar_pdf)
    btn_pdf.pack(pady=5)

    btn_salir = tk.Button(root, text="Salir", command=cerrar_aplicacion)
    btn_salir.pack(pady=10)

    root.mainloop()

# ---------------- VENTANA DE LOGIN ----------------
login_window = tk.Tk()
login_window.title("Login - Documento")

tk.Label(login_window, text="Ingrese su documento:").pack(padx=10, pady=10)
entry_doc = tk.Entry(login_window)
entry_doc.pack(pady=5)

btn_login = tk.Button(login_window, text="Ingresar", command=login)
btn_login.pack(pady=10)

login_window.mainloop()