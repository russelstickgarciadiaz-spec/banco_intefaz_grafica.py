import tkinter as tk
from tkinter import messagebox
import mysql.connector
from datetime import datetime
from reportlab.pdfgen import canvas
import os

# ---------------- CONEXIÓN MYSQL ----------------
conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="banco"
)
cursor = conexion.cursor(buffered=True)

# ---------------- VARIABLES ----------------
usuario_actual_id = None  # Guardará el ID del usuario que ingresó

# Colores y fuentes
COLOR_PRINCIPAL = "#ff9800"      # Naranja principal
COLOR_SECUNDARIO = "#ffe0b2"     # Naranja claro para fondos
COLOR_TEXTO = "#3e2723"          # Marrón oscuro para texto
COLOR_BOTON = "#fb8c00"          # Naranja botón
COLOR_BOTON_HOVER = "#ef6c00"    # Naranja más intenso al pasar el mouse
FUENTE_TITULO = ("Helvetica", 16, "bold")
FUENTE_NORMAL = ("Verdana", 12)
FUENTE_BOTON = ("Verdana", 12, "bold")

# ---------------- FUNCIONES BASE ----------------
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
    ventana.configure(bg=COLOR_SECUNDARIO)

    texto = tk.Text(ventana, width=50, height=15, font=FUENTE_NORMAL, bg="white", fg=COLOR_TEXTO)
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
        messagebox.showinfo("Información", "No hay movimientos para exportar")
        return

    # Carpeta PDFs
    if not os.path.exists("PDFs"):
        os.makedirs("PDFs")

    archivo_pdf = f"PDFs/movimientos_usuario{usuario_actual_id}.pdf"
    c = canvas.Canvas(archivo_pdf)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 800, f"Movimientos del usuario {usuario_actual_id}")
    y = 760
    c.setFont("Helvetica", 12)
    for f in filas:
        c.drawString(50, y, f"{f[0]} - {f[1]}: ${f[2]}")
        y -= 25
        if y < 50:
            c.showPage()
            y = 800
    c.save()
    messagebox.showinfo("Éxito", f"PDF generado: {archivo_pdf}")
    os.startfile(archivo_pdf)

def cerrar_aplicacion():
    conexion.close()
    root.destroy()

# ---------------- LOGIN ----------------
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

# ---------------- INTERFAZ PRINCIPAL ----------------
def iniciar_app():
    global root, lbl_saldo, entry_monto, btn_ingresar, btn_retirar, btn_mov, btn_pdf, btn_salir

    root = tk.Tk()
    root.title("Banco - Multiusuario")
    root.geometry("450x450")
    root.configure(bg=COLOR_SECUNDARIO)

    lbl_saldo = tk.Label(root, text=f"Saldo: ${obtener_saldo()}", font=FUENTE_TITULO, bg=COLOR_SECUNDARIO, fg=COLOR_TEXTO)
    lbl_saldo.pack(pady=15)

    entry_monto = tk.Entry(root, font=FUENTE_NORMAL, width=25, bg="white", fg=COLOR_TEXTO, bd=3, relief="ridge")
    entry_monto.pack(pady=10)

    btn_ingresar = tk.Button(root, text="Ingresar dinero", command=ingresar,
                             font=FUENTE_BOTON, fg="white", bg=COLOR_BOTON,
                             activebackground=COLOR_BOTON_HOVER, activeforeground="white", width=20, height=2, cursor="hand2")
    btn_ingresar.pack(pady=5)

    btn_retirar = tk.Button(root, text="Retirar dinero", command=retirar,
                            font=FUENTE_BOTON, fg="white", bg=COLOR_BOTON,
                            activebackground=COLOR_BOTON_HOVER, activeforeground="white", width=20, height=2, cursor="hand2")
    btn_retirar.pack(pady=5)

    btn_mov = tk.Button(root, text="Ver movimientos", command=ver_movimientos,
                        font=FUENTE_BOTON, fg="white", bg=COLOR_BOTON,
                        activebackground=COLOR_BOTON_HOVER, activeforeground="white", width=20, height=2, cursor="hand2")
    btn_mov.pack(pady=5)

    btn_pdf = tk.Button(root, text="Exportar PDF", command=exportar_pdf,
                        font=FUENTE_BOTON, fg="white", bg=COLOR_BOTON,
                        activebackground=COLOR_BOTON_HOVER, activeforeground="white", width=20, height=2, cursor="hand2")
    btn_pdf.pack(pady=5)

    btn_salir = tk.Button(root, text="Salir", command=cerrar_aplicacion,
                          font=FUENTE_BOTON, fg="white", bg="#e65100",
                          activebackground="#bf360c", activeforeground="white", width=20, height=2, cursor="hand2")
    btn_salir.pack(pady=15)

    root.mainloop()

# ---------------- LOGIN ESTÉTICO ----------------
login_window = tk.Tk()
login_window.title("Banco - Login")
login_window.geometry("350x250")
login_window.configure(bg=COLOR_SECUNDARIO)

tk.Label(login_window, text="Ingrese su documento:", font=FUENTE_TITULO, bg=COLOR_SECUNDARIO, fg=COLOR_TEXTO).pack(pady=20)
entry_doc = tk.Entry(login_window, font=FUENTE_NORMAL, width=25, bg="white", fg=COLOR_TEXTO, bd=3, relief="ridge")
entry_doc.pack(pady=10)

btn_login = tk.Button(login_window, text="Ingresar", command=login,
                      font=FUENTE_BOTON, fg="white", bg=COLOR_BOTON,
                      activebackground=COLOR_BOTON_HOVER, activeforeground="white",
                      width=20, height=2, cursor="hand2")
btn_login.pack(pady=15)

login_window.mainloop()