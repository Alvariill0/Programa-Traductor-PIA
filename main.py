from dotenv import load_dotenv
import os

from funciones import (
    api_listar_idiomas,
    api_detectar_idioma,
    api_traducir,
    sdk_speech_stt_microfono,
    sdk_speech_tts,
    mostrar_idiomas,
    seleccionar_idioma,
    menu_opciones
)

load_dotenv()

TRAD_KEY = os.getenv("TRAD_KEY1")
TRAD_ENDPOINT = os.getenv("ENDPOINT_TRAD")
SPEECH_KEY = os.getenv("SPEECH_KEY1")
SPEECH_ENDPOINT = os.getenv("ENDPOINT_SPEECH")
REGION = os.getenv("REGION")
  

def probar_texto_a_texto():
    idiomas = api_listar_idiomas(TRAD_ENDPOINT, TRAD_KEY, REGION)
    if not idiomas:
        print("No se pudieron cargar los idiomas.")
        return
    
    mostrar_idiomas(idiomas)

    print("\nIdioma origen:")
    idioma_origen_codigo, idioma_origen_nombre = seleccionar_idioma(idiomas)
    if not idioma_origen_codigo:
        return

    print("\nIdioma destino:")
    idioma_destino_codigo, idioma_destino_nombre = seleccionar_idioma(idiomas)
    if not idioma_destino_codigo:
        return

    texto = input("\nEscribe el texto a traducir: ")
    idioma_detectado = api_detectar_idioma(texto, TRAD_ENDPOINT, TRAD_KEY, REGION)
    if idioma_detectado and idioma_detectado != idioma_origen_codigo:
        print(f" Texto detectado en {idioma_detectado}, pero se seleccionó {idioma_origen_nombre}.")

    traduccion = api_traducir(texto, idioma_origen_codigo, idioma_destino_codigo, TRAD_ENDPOINT, TRAD_KEY, REGION)

    if traduccion:
        print(f"\nORIGEN ({idioma_origen_nombre}): {texto}")
        print(f"DESTINO ({idioma_destino_nombre}): {traduccion}")
    else:
        print("Error en traducción.")
    
    # Opcion reproducir audio:
    if traduccion:
        respuesta = input("\n¿Reproducir traducción en audio? (s/n): ").strip().lower()
    if respuesta == "s":
        archivo_audio = sdk_speech_tts(traduccion, SPEECH_KEY, REGION)
        if archivo_audio:
            print(f"Audio guardado: {archivo_audio}")
        else:
            print("Error generando audio.")



def audio_a_texto():
    idiomas = api_listar_idiomas(TRAD_ENDPOINT, TRAD_KEY, REGION)
    if not idiomas:
        print("No se pudieron cargar los idiomas.")
        return

    mostrar_idiomas(idiomas)

    print("\nIdioma origen:")
    idioma_origen_codigo, idioma_origen_nombre = seleccionar_idioma(idiomas)
    if not idioma_origen_codigo:
        return

    print("\nIdioma destino:")
    idioma_destino_codigo, idioma_destino_nombre = seleccionar_idioma(idiomas)
    if not idioma_destino_codigo:
        return

    # STT con fallback a test.wav
    texto_reconocido, fuente = sdk_speech_stt_microfono(
        SPEECH_KEY, REGION,
        idioma=idioma_origen_codigo,
        archivo_fallback="test.wav"
    )

    if not texto_reconocido:
        print("No se pudo reconocer audio.")
        return

    print(f"\nReconocido ({fuente}): {texto_reconocido}")

    # Detectar el idioma del texto reconocido y traducirlo
    idioma_origen_detectado = api_detectar_idioma(texto_reconocido, TRAD_ENDPOINT, TRAD_KEY, REGION)

    if idioma_origen_detectado and idioma_origen_detectado != idioma_origen_codigo:
        print(f"Texto detectado en {idioma_origen_detectado}, pero se seleccionó {idioma_origen_nombre}.")

    idioma_origen_trad = idioma_origen_detectado or idioma_origen_codigo
    traduccion = api_traducir(texto_reconocido, idioma_origen_trad, idioma_destino_codigo, TRAD_ENDPOINT, TRAD_KEY, REGION)

    print(f"\n----------------------------------------")
    print(f"AUDIO -> TEXTO: {idioma_origen_nombre} → {idioma_destino_nombre}")
    print(f"RECONOCIDO: {texto_reconocido}")
    if traduccion:
        print(f"TRADUCCIÓN: {traduccion}")
    else:
        print("Error en traducción.")
    print(f"----------------------------------------")

    # Preguntar si quiere escuchar la traducción (solo si existe)
    if traduccion:
        respuesta = input("\n¿Reproducir traducción en audio? (s/n): ").strip().lower()
        if respuesta == "s":
            archivo_audio = sdk_speech_tts(traduccion, SPEECH_KEY, REGION)
            if archivo_audio:
                print(f"Audio guardado: {archivo_audio}")
            else:
                print("Error generando audio.")
    else:
        print("⚠️  No se puede generar audio sin traducción válida.")


def main():
    while True:
        opcion = menu_opciones()

        if opcion == "1":
            probar_texto_a_texto()
        elif opcion == "2":
            audio_a_texto()
        elif opcion == "0":
            print("Chao pescao ")
            break
        else:
            print("Opción no válida ")

if __name__ == "__main__":
    main()
