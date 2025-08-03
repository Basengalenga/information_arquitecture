import streamlit as st
import psycopg2

def obtener_todo():
    try:
        # Establecer la conexión
        conn = psycopg2.connect(
            host="db",      # o la IP/URL de tu servidor
            port="5432",           # puerto por defecto de PostgreSQL
            user="postgres",
            password="example",
            database="postgres"
        )

        print("Conexión exitosa")

        # Crear un cursor para ejecutar consultas
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM plantas")

        query = cursor.fetchall()

        # Cerrar cursor y conexión
        cursor.close()
        conn.close()
        return query

    except psycopg2.Error as e:
        return e
    
def añadir_registro(nombre, precio, reino, division, clase):
    try:
        # Establecer la conexión
        conn = psycopg2.connect(
            host="db",      # o la IP/URL de tu servidor
            port="5432",           # puerto por defecto de PostgreSQL
            user="postgres",
            password="example",
            database="postgres"
        )

        print("Conexión exitosa")

        # Crear un cursor para ejecutar consultas
        cursor = conn.cursor()

        cursor.execute(f"""
            INSERT INTO plantas (nombreplanta, precio, reino, division, clase) VALUES
            ({nombre},{precio},{reino},{division},{clase}),
            """)


        # Cerrar cursor y conexión
        cursor.close()
        conn.close()
        return "Operación exitosa"
    except psycopg2.Error as e:
        return e
    
def eliminar_registro(nombre):
    try:
        # Establecer la conexión
        conn = psycopg2.connect(
            host="db",      # o la IP/URL de tu servidor
            port="5432",           # puerto por defecto de PostgreSQL
            user="postgres",
            password="example",
            database="postgres"
        )

        print("Conexión exitosa")

        # Crear un cursor para ejecutar consultas
        cursor = conn.cursor()

        cursor.execute(f"""
            DELETE FROM plantas
            WHERE nombreplanta = {nombre};
            """)


        # Cerrar cursor y conexión
        cursor.close()
        conn.close()
        return "Operación exitosa"
    except psycopg2.Error as e:
        return e

def todo():
    st.title(obtener_todo())

if __name__ == "__main__":
    todo()
