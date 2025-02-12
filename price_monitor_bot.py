import requests
from bs4 import BeautifulSoup
import os
import schedule
import time
from telegram import Bot

# Configuración de Telegram
TELEGRAM_BOT_TOKEN = "7973005442:AAGqj1wxlhFLr6VPeEVwd1xRhfHWHic-cRw"
TELEGRAM_CHAT_ID = "5370766675"

# URL del producto en Costco
URL = "https://www.costco.com.mx/Jardin-Flores-y-Mascotas/Mascotas/Gatos/Kirkland-Signature-Alimento-para-Gato-Pollo-y-Arroz-113kg/p/52296"

# Función para obtener el precio
def obtener_precio():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        price_tag = soup.find("span", class_="notranslate ng-star-inserted")
        if price_tag:
            precio = price_tag.text.strip().replace("$", "").replace(",", "")
            return float(precio)
    return None

# Funciones para manejar el precio almacenado
def leer_precio_anterior():
    if os.path.exists("precio_anterior.txt"):
        with open("precio_anterior.txt", "r") as file:
            return float(file.read().strip())
    return None

def guardar_precio_actual(precio):
    with open("precio_anterior.txt", "w") as file:
        file.write(str(precio))

# Función para enviar notificación por Telegram
def enviar_notificacion(mensaje):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=mensaje)
    print("Mensaje enviado por Telegram")

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
        enviar_notificacion(f"¡Oferta! El precio bajó a ${precio_actual}")
    elif precio_actual > precio_anterior:
        print(f"El precio subió de ${precio_anterior} a ${precio_actual}")
    
    guardar_precio_actual(precio_actual)

# Función para enviar mensaje de verificación cada 24 horas
def enviar_mensaje_verificacion():
    enviar_notificacion("Verificando el precio!")

# Programación para ejecutar periódicamente
schedule.every(5).minutes.do(verificar_cambio)
schedule.every(5).hours.do(enviar_mensaje_verificacion)

print("Monitoreo iniciado...")

while True:
    schedule.run_pending()
    time.sleep(60)

