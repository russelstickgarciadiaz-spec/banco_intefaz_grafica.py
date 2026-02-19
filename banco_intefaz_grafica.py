import tkinter as tk
from tkinter import messagebox
import sqlite3
import time

# ---------------- BASE DE DATOS ----------------
conexion = sqlite3.connect("banco.db")
cursor = conexion.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS cuenta (
    id INTEGER PRIMARY KEY,
    saldo INTEGER
)
""") 
print("hola mundo")

cursor.execute("""
CREATE TABLE IF NOT EXISTS movimientos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT,
    tipo TEXT,
    monto INTEGER
)
""")

# Inicializar saldo si no existe
cursor.execute("SELECT saldo FROM cuenta WHERE id = 1")
if cursor.fetchone() is None:
    cursor.execute("INSERT INTO cuenta VALUES (1, 0)")
    conexion.commit()


# ---------------- FUNCIONES ----------------
def obtener_saldo():
    cursor.execute("SELECT saldo FROM cuenta WHERE id = 1")
    return cursor.fetchone()[0]


def actualizar_saldo(nuevo_saldo):
    cursor.execute("UPDATE cuenta SET saldo = ? WHERE id = 1", (nuevo_saldo,))
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

    fecha = time.strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO movimientos (fecha, tipo, monto) VALUES (?, ?, ?)",
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

    fecha = time.strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO movimientos (fecha, tipo, monto) VALUES (?, ?, ?)",
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

    cursor.execute("SELECT fecha, tipo, monto FROM movimientos")
    filas = cursor.fetchall()

    if not filas:
        texto.insert(tk.END, "No hay movimientos registrados")
    else:
        for f in filas:
            texto.insert(tk.END, f"{f[0]} - {f[1]}: ${f[2]}\n")


# ---------------- INTERFAZ ----------------
root = tk.Tk()
root.title("Banco")

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

btn_salir = tk.Button(root, text="Salir", command=root.quit)
btn_salir.pack(pady=10)

root.mainloop()