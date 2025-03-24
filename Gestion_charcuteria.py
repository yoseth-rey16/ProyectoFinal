#importaciones necesarias para la ejecucion
import tkinter as tk #--el "alias" es tk
import customtkinter as ctk #--interfas moderna
import sqlite3 #--base de datos
from datetime import datetime #--fecha y hora
from tkinter import messagebox #--modulo de tk que da cuadros de dialogos 

DATABASE_FILE = "inventario_charcuteria.db"

class AplicacionCharcuteria(ctk.CTk): #--define la clase 
    def __init__(self):
        super().__init__() #--método constructor de la clase
        self.title("Sistema de inventario de Charcutería")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("green")

        self.create_widgets()
        self.crear_tabla()

    def crear_conexion(self):#con esta funcion se crea una conexion con la base de datos sql "inventario_charcuteria"
        conn = None
        try:
            conn = sqlite3.connect(DATABASE_FILE)
            return conn
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos", f"No se pudo conectar a la base de datos: {e}")
            return None

    def cerrar_conexion(self, conn):#cierra la conexion con la base de datos
        if conn:
            conn.close()

    def crear_tabla(self):#crea la tabla producto en la base de datos de inventario
        conn = self.crear_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Productos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT NOT NULL UNIQUE,
                        cantidad INTEGER NOT NULL,
                        precio REAL NOT NULL
                    )
                """)
                conn.commit()
            except sqlite3.Error as e:
                messagebox.showerror("Error de Base de Datos", f"Error al crear la tabla: {e}")
            finally:
                self.cerrar_conexion(conn)

    def create_widgets(self):
        self.tabview = ctk.CTkTabview(self, width=600, height=450)
        self.tabview.pack(padx=20, pady=20)

        self.tabview.add("Inventario")
        self.tabview.tab("Inventario").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Inventario").grid_rowconfigure((0, 1, 2, 3, 4), weight=1)

        self.create_inventario_tab()

    def create_inventario_tab(self):
        frame = self.tabview.tab("Inventario")

        label_titulo = ctk.CTkLabel(frame, text="Gestión de Inventario", font=ctk.CTkFont(size=20, weight="bold"))
        label_titulo.grid(row=0, column=0, pady=20, padx=20, sticky="ew")

        agregar_button = ctk.CTkButton(frame, text="Agregar Producto", command=self.abrir_ventana_agregar)
        agregar_button.grid(row=1, column=0, pady=10, padx=20, sticky="ew")

        ver_button = ctk.CTkButton(frame, text="Ver Inventario", command=self.ver_productos_gui)
        ver_button.grid(row=2, column=0, pady=10, padx=20, sticky="ew")

        modificar_button = ctk.CTkButton(frame, text="Modificar Producto", command=self.abrir_ventana_modificar)
        modificar_button.grid(row=3, column=0, pady=10, padx=20, sticky="ew")

        eliminar_button = ctk.CTkButton(frame, text="Eliminar Producto", command=self.abrir_ventana_eliminar)
        eliminar_button.grid(row=4, column=0, pady=10, padx=20, sticky="ew")

        buscar_button = ctk.CTkButton(frame, text="Buscar Producto", command=self.abrir_ventana_buscar)
        buscar_button.grid(row=5, column=0, pady=10, padx=20, sticky="ew")

    def abrir_ventana_agregar(self):
        ventana = ctk.CTkToplevel(self)
        ventana.title("Agregar Nuevo Producto")
        ventana.geometry("350x250")

        label_nombre = ctk.CTkLabel(ventana, text="Nombre:")
        label_nombre.pack(pady=10, padx=20, anchor="w")
        entry_nombre = ctk.CTkEntry(ventana)
        entry_nombre.pack(pady=5, padx=20, fill="x")

        label_cantidad = ctk.CTkLabel(ventana, text="Cantidad:")
        label_cantidad.pack(pady=10, padx=20, anchor="w")
        entry_cantidad = ctk.CTkEntry(ventana)
        entry_cantidad.pack(pady=5, padx=20, fill="x")

        label_precio = ctk.CTkLabel(ventana, text="Precio:")
        label_precio.pack(pady=10, padx=20, anchor="w")
        entry_precio = ctk.CTkEntry(ventana)
        entry_precio.pack(pady=5, padx=20, fill="x")

        def agregar_producto_handler():
            nombre = entry_nombre.get()
            try:
                cantidad = int(entry_cantidad.get())
                precio = float(entry_precio.get())
                if nombre and cantidad >= 0 and precio >= 0:
                    conn = self.crear_conexion()
                    if conn:
                        try:
                            cursor = conn.cursor()
                            cursor.execute("INSERT INTO Productos (nombre, cantidad, precio) VALUES (?, ?, ?)", (nombre, cantidad, precio))
                            conn.commit()
                            messagebox.showinfo("Éxito", f"Producto '{nombre}' agregado exitosamente.")
                            entry_nombre.delete(0, tk.END)
                            entry_cantidad.delete(0, tk.END)
                            entry_precio.delete(0, tk.END)
                        except sqlite3.IntegrityError:
                            messagebox.showerror("Error", f"Ya existe un producto con el nombre '{nombre}'.")
                        except sqlite3.Error as e:
                            messagebox.showerror("Error de Base de Datos", f"Error al agregar producto: {e}")
                        finally:
                            self.cerrar_conexion(conn)
                else:
                    messagebox.showerror("Error", "Por favor, ingrese datos válidos.")
            except ValueError:
                messagebox.showerror("Error", "Cantidad y precio deben ser números válidos.")

        agregar_button = ctk.CTkButton(ventana, text="Agregar", command=agregar_producto_handler)
        agregar_button.pack(pady=20, padx=20)

    def ver_productos_gui(self):
        ventana = ctk.CTkToplevel(self)
        ventana.title("Inventario de la Charcutería")
        ventana.geometry("450x350")

        label_titulo = ctk.CTkLabel(ventana, text="--- Inventario ---", font=ctk.CTkFont(weight="bold"))
        label_titulo.pack(pady=10)

        texto_inventario = ctk.CTkTextbox(ventana, width=400, height=250)
        texto_inventario.pack(padx=10, pady=10)
        texto_inventario.configure(state="disabled")

        conn = self.crear_conexion()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id, nombre, cantidad, precio FROM Productos ORDER BY nombre")
                productos = cursor.fetchall()
                if productos:
                    texto_inventario.configure(state="normal")
                    texto_inventario.delete("1.0", tk.END)
                    for producto in productos:
                        texto_inventario.insert(tk.END, f"ID: {producto[0]}, Nombre: {producto[1]}, Cantidad: {producto[2]}, Precio: ${producto[3]:.2f}\n")
                    texto_inventario.configure(state="disabled")
                else:
                    texto_inventario.configure(state="normal")
                    texto_inventario.delete("1.0", tk.END)
                    texto_inventario.insert(tk.END, "El inventario está vacío.\n")
                    texto_inventario.configure(state="disabled")
            except sqlite3.Error as e:
                messagebox.showerror("Error de Base de Datos", f"Error al obtener el inventario: {e}")
            finally:
                self.cerrar_conexion(conn)

        boton_cerrar = ctk.CTkButton(ventana, text="Cerrar", command=ventana.destroy)
        boton_cerrar.pack(pady=10)

    def abrir_ventana_modificar(self):
        ventana = ctk.CTkToplevel(self)
        ventana.title("Modificar Producto")
        ventana.geometry("350x280")

        label_id = ctk.CTkLabel(ventana, text="ID del Producto a Modificar:")
        label_id.pack(pady=10, padx=20, anchor="w")
        entry_id = ctk.CTkEntry(ventana)
        entry_id.pack(pady=5, padx=20, fill="x")

        label_cantidad = ctk.CTkLabel(ventana, text="Nueva Cantidad (dejar en blanco para no cambiar):")
        label_cantidad.pack(pady=10, padx=20, anchor="w")
        entry_cantidad = ctk.CTkEntry(ventana)
        entry_cantidad.pack(pady=5, padx=20, fill="x")

        label_precio = ctk.CTkLabel(ventana, text="Nuevo Precio (dejar en blanco para no cambiar):")
        label_precio.pack(pady=10, padx=20, anchor="w")
        entry_precio = ctk.CTkEntry(ventana)
        entry_precio.pack(pady=5, padx=20, fill="x")

        def modificar_producto_handler():
            producto_id_str = entry_id.get()
            if not producto_id_str.isdigit():
                messagebox.showerror("Error", "Ingrese un ID de producto válido.")
                return
            producto_id = int(producto_id_str)
            nueva_cantidad_str = entry_cantidad.get()
            nuevo_precio_str = entry_precio.get()

            nueva_cantidad = None
            if nueva_cantidad_str:
                try:
                    nueva_cantidad = int(nueva_cantidad_str)
                    if nueva_cantidad < 0:
                        messagebox.showerror("Error", "La nueva cantidad debe ser no negativa.")
                        return
                except ValueError:
                    messagebox.showerror("Error", "La nueva cantidad debe ser un número entero.")
                    return

            nuevo_precio = None
            if nuevo_precio_str:
                try:
                    nuevo_precio = float(nuevo_precio_str)
                    if nuevo_precio < 0:
                        messagebox.showerror("Error", "El nuevo precio debe ser no negativo.")
                        return
                except ValueError:
                    messagebox.showerror("Error", "El nuevo precio debe ser un número válido.")
                    return

            conn = self.crear_conexion()
            if conn:
                try:
                    cursor = conn.cursor()
                    if nueva_cantidad is not None and nuevo_precio is not None:
                        cursor.execute("UPDATE Productos SET cantidad = ?, precio = ? WHERE id = ?", (nueva_cantidad, nuevo_precio, producto_id))
                        mensaje = f"Producto con ID {producto_id} actualizado exitosamente."
                    elif nueva_cantidad is not None:
                        cursor.execute("UPDATE Productos SET cantidad = ? WHERE id = ?", (nueva_cantidad, producto_id))
                        mensaje = f"Cantidad del producto con ID {producto_id} actualizada exitosamente."
                    elif nuevo_precio is not None:
                        cursor.execute("UPDATE Productos SET precio = ? WHERE id = ?", (nuevo_precio, producto_id))
                        mensaje = f"Precio del producto con ID {producto_id} actualizado exitosamente."
                    else:
                        mensaje = "No se especificaron cambios."

                    if cursor.rowcount > 0:
                        messagebox.showinfo("Éxito", mensaje)
                    elif nueva_cantidad is not None or nuevo_precio is not None:
                        messagebox.showinfo("Información", "No se encontró el producto con el ID proporcionado.")
                    conn.commit()
                except sqlite3.Error as e:
                    messagebox.showerror("Error de Base de Datos", f"Error al modificar el producto: {e}")
                finally:
                    self.cerrar_conexion(conn)

        modificar_button = ctk.CTkButton(ventana, text="Modificar", command=modificar_producto_handler)
        modificar_button.pack(pady=20, padx=20)

    def abrir_ventana_eliminar(self):
        ventana = ctk.CTkToplevel(self)
        ventana.title("Eliminar Producto")
        ventana.geometry("300x150")

        label_id = ctk.CTkLabel(ventana, text="ID del Producto a Eliminar:")
        label_id.pack(pady=10, padx=20, anchor="w")
        entry_id = ctk.CTkEntry(ventana)
        entry_id.pack(pady=5, padx=20, fill="x")

        def eliminar_producto_handler():
            producto_id_str = entry_id.get()
            if not producto_id_str.isdigit():
                messagebox.showerror("Error", "Ingrese un ID de producto válido.")
                return
            producto_id = int(producto_id_str)

            confirmacion = messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de que desea eliminar el producto con ID {producto_id}?")
            if confirmacion:
                conn = self.crear_conexion()
                if conn:
                    try:
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM Productos WHERE id = ?", (producto_id,))
                        if cursor.rowcount > 0:
                            messagebox.showinfo("Éxito", f"Producto con ID {producto_id} eliminado exitosamente.")
                        else:
                            messagebox.showinfo("Información", f"Producto con ID {producto_id} no encontrado.")
                        conn.commit()
                    except sqlite3.Error as e:
                        messagebox.showerror("Error de Base de Datos", f"Error al eliminar el producto: {e}")
                    finally:
                        self.cerrar_conexion(conn)

        eliminar_button = ctk.CTkButton(ventana, text="Eliminar", command=eliminar_producto_handler)
        eliminar_button.pack(pady=20, padx=20)

    def abrir_ventana_buscar(self):
        ventana = ctk.CTkToplevel(self)
        ventana.title("Buscar Producto")
        ventana.geometry("300x150")

        label_busqueda = ctk.CTkLabel(ventana, text="Nombre o ID del Producto:")
        label_busqueda.pack(pady=10, padx=20, anchor="w")
        entry_busqueda = ctk.CTkEntry(ventana)
        entry_busqueda.pack(pady=5, padx=20, fill="x")

        def buscar_producto_handler():
            termino_busqueda = entry_busqueda.get()
            if not termino_busqueda:
                messagebox.showerror("Error", "Ingrese un término de búsqueda.")
                return

            conn = self.crear_conexion()
            if conn:
                try:
                    cursor = conn.cursor()
                    if termino_busqueda.isdigit():
                        cursor.execute("SELECT id, nombre, cantidad, precio FROM Productos WHERE id = ?", (termino_busqueda,))
                    else:
                        cursor.execute("SELECT id, nombre, cantidad, precio FROM Productos WHERE LOWER(nombre) LIKE ?", (f"%{termino_busqueda.lower()}%",))
                    productos = cursor.fetchall()
                    if productos:
                        resultado = "\n--- Resultados de la Búsqueda ---\n"
                        for producto in productos:
                            resultado += f"ID: {producto[0]}, Nombre: {producto[1]}, Cantidad: {producto[2]}, Precio: ${producto[3]:.2f}\n"
                        messagebox.showinfo("Resultados de la Búsqueda", resultado)
                    else:
                        messagebox.showinfo("Resultados de la Búsqueda", f"No se encontraron productos que coincidan con '{termino_busqueda}'.")
                except sqlite3.Error as e:
                    messagebox.showerror("Error de Base de Datos", f"Error al buscar el producto: {e}")
                finally:
                    self.cerrar_conexion(conn)

        buscar_button = ctk.CTkButton(ventana, text="Buscar", command=buscar_producto_handler)
        buscar_button.pack(pady=20, padx=20)

if __name__ == "__main__":
    aplicacion = AplicacionCharcuteria()
    aplicacion.mainloop() 