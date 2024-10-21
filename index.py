from pynput import keyboard
from PIL import ImageGrab
import threading
from pathlib import Path
from time import sleep
from datetime import datetime

pressed_keys = set()
screenshot_thread = None
output_folder = Path(__file__).parent / "screenshots" / datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
jugada = 0

# Crear la carpeta de salida si no existe
if not output_folder.exists():
    output_folder.mkdir(parents=True, exist_ok=True)

def take_screenshot():
    # Crear el nombre basado en las teclas presionadas
    keys_combination = ''.join(sorted(pressed_keys)) or "none"
    screenshot_path = output_folder / f"{keys_combination}_{jugada}_{datetime.now().strftime("%H-%M-%S")}.jpg"
    
    # Verificar si ya existe un archivo con el mismo nombre, y si es así, agregar un sufijo numérico
    counter = 1
    while screenshot_path.exists():
        screenshot_path = output_folder / f"{keys_combination}_{jugada}_{datetime.now().strftime("%H-%M-%S")}_{counter}.jpg"
        counter += 1
    
    # Tomar la captura y guardarla
    screenshot = ImageGrab.grab()
    try:
        screenshot.save(screenshot_path, "JPEG", quality=70)
        print(f"Screenshot guardada en {screenshot_path}")
    except:
        print(f"Error al guardar {screenshot_path}")
        screenshot.save(str(screenshot_path).replace('\0x3', ''), "JPEG", quality=70)

def screenshot_loop():
    while True:
        if pressed_keys:  # Solo toma captura si hay teclas presionadas
            take_screenshot()
        threading.Event().wait(0.2)  # Espera 0.5 segundos entre capturas

def on_press(key):
    try:
        if hasattr(key, 'char') and key.char:
            pressed_keys.add(key.char)  # Captura teclas normales
        else:
            key_str = str(key)
            # Filtrar caracteres no imprimibles
            if key_str.isprintable():
                pressed_keys.add(key_str)  # Captura teclas especiales
            else:
                pressed_keys.add(key.name)  # Captura teclas especiales
    except AttributeError:
        pressed_keys.add(str(key))

def on_release(key):
    global jugada
    try:
        if len(pressed_keys) == 0:
            jugada += 1
        if hasattr(key, 'char') and key.char in pressed_keys:
            pressed_keys.remove(key.char)
        elif str(key) in pressed_keys:
            pressed_keys.remove(str(key))
    except KeyError:
        pass

def main():
    # Inicia el hilo para tomar screenshots
    screenshot_thread = threading.Thread(target=screenshot_loop)
    screenshot_thread.daemon = True  # Se cerrará cuando termine el programa principal
    screenshot_thread.start()

    # Listener de teclado
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()  # Mantiene el listener activo

if __name__ == "__main__":
    print("El programa comenzará en 5 segundos...")
    sleep(5)  # Espera antes de iniciar
    main()
