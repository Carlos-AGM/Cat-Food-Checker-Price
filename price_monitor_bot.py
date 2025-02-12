import requests
from bs4 import BeautifulSoup
import os
import schedule
import time
import asyncio
from telegram import Bot

# Configuración de Telegram
TELEGRAM_BOT_TOKEN = "7973005442:AAGqj1wxlhFLr6VPeEVwd1xRhfHWHic-cRw"
TELEGRAM_CHAT_ID = "5370766675"

# URL del producto en Costco
URL = "https://www.costco.com.mx/Jardin-Flores-y-Mascotas/Mascotas/Gatos/Kirkland-Signature-Alimento-para-Gato-Pollo-y-Arroz-113kg/p/52296"

# Función para obtener el precio
def obtener_precio():
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(URL, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error al obtener el precio: {e}")
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    price_tag = soup.find("span", class_="notranslate ng-star-inserted")
    
    if price_tag:
        try:
            precio = price_tag.text.strip().replace("$", "").replace(",", "")
            return float(precio)
        except ValueError:
            print("No se pudo convertir el precio a número.")
            return None
    
    print("No se encontró el precio en la página.")
    return None

# Funciones para manejar el precio almacenado
def leer_precio_anterior():
    if os.path.exists("precio_anterior.txt"):
        try:
            with open("precio_anterior.txt", "r") as file:
                return float(file.read().strip())
        except ValueError:
            print("El archivo de precio está corrupto, se ignorará.")
            return None
    return None

def guardar_precio_actual(precio):
    with open("precio_anterior.txt", "w") as file:
        file.write(str(precio))

# Función asíncrona para enviar notificación por Telegram
async def enviar_notificacion(mensaje):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=mensaje)
        print("Mensaje enviado por Telegram")
    except Exception as e:
        print(f"Error al enviar el mensaje por Telegram: {e}")

# Función para ejecutar la notificación sin bloquear el loop
def ejecutar_enviar_notificacion(mensaje):
    asyncio.run(enviar_notificacion(mensaje))  # Ejecuta la función asíncrona correctamente

# Función para verificar el cambio de precio
def verificar_cambio():
    precio_actual = obtener_precio()
    
    if precio_actual is None:
        print("No se pudo obtener el precio.")
        return
    
    precio_anterior = leer_precio_anterior()
    
    if precio_anterior is None:
        print(f"Guardando precio inicial: ${precio_actual}")
        guardar_precio_actual(precio_actual)
        return
    
    if precio_actual < precio_anterior:
        print(f"¡Bajó el precio! De ${precio_anterior} a ${precio_actual}")
        ejecutar_enviar_notificacion(f"¡Oferta! El precio bajó a ${precio_actual}")
    elif precio_actual > precio_anterior:
        print(f"El precio subió de ${precio_anterior} a ${precio_actual}")
    
    guardar_precio_actual(precio_actual)

# Función para enviar mensaje de verificación cada 24 horas
def enviar_mensaje_verificacion():
    ejecutar_enviar_notificacion("Verificando el precio!")

# Programación para ejecutar periódicamente
schedule.every(5).minutes.do(verificar_cambio)
schedule.every(24).hours.do(enviar_mensaje_verificacion)

print("Monitoreo iniciado...")

while True:
    schedule.run_pending()
    time.sleep(10)  
