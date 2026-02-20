import tkinter as tk
from tkinter import messagebox
import mysql.connector
from datetime import datetime

# ---------------- CONEXIÓN MYSQL ----------------
conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # En XAMPP normalmente está vacío
    database="banco"
)

cursor = conexion.cursor()

# ---------------- FUNCIONES ----------------
def obtener_saldo():
    cursor.execute("SELECT saldo FROM cuenta WHERE id = 1")
    resultado = cursor.fetchone()
    return resultado[0] if resultado else 0


def actualizar_saldo(nuevo_saldo):
    cursor.execute("UPDATE cuenta SET saldo = %s WHERE id = 1", (nuevo_saldo,))
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
        "INSERT INTO movimientos (fecha, tipo, monto) VALUES (%s, %s, %s)",
        (fecha, "Ingreso", monto)
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
        "INSERT INTO movimientos (fecha, tipo, monto) VALUES (%s, %s, %s)",
        (fecha, "Retiro", monto)
    )
    conexion.commit()

    messagebox.showinfo("Éxito", f"Retiró ${monto}")
    entry_monto.delete(0, tk.END)


def ver_movimientos():
    ventana = tk.Toplevel(root)
    ventana.title("Movimientos")

    texto = tk.Text(ventana, width=50, height=15)
    texto.pack(padx=10, pady=10)

    cursor.execute("SELECT fecha, tipo, monto FROM movimientos ORDER BY fecha DESC")
    filas = cursor.fetchall()

    if not filas:
        texto.insert(tk.END, "No hay movimientos registrados")
    else:
        for f in filas:
            texto.insert(tk.END, f"{f[0]} - {f[1]}: ${f[2]}\n")


def cerrar_aplicacion():
    conexion.close()
    root.destroy()


# ---------------- INTERFAZ ----------------
root = tk.Tk()
root.title("Banco - MySQL")

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

btn_salir = tk.Button(root, text="Salir", command=cerrar_aplicacion)
btn_salir.pack(pady=10)

root.mainloop()