import requests
import os
import azure.cognitiveservices.speech as speechsdk

#FUNCIONES API TRADUCTOR
def api_detectar_idioma(texto, endpoint, key, region):
    """
    Detecta el idioma de un texto usando la API REST de Translator.
    Devuelve el código de idioma (ej: 'es', 'en')
    """
    if not texto or len(texto.strip()) == 0:
        return None
    
    url = f"{endpoint}/detect?api-version=3.0"
    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Ocp-Apim-Subscription-Region": region,
        "Content-Type": "application/json"
    }
    body = [{"Text": texto}]
    
    try:
        response = requests.post(url, headers=headers, json=body)
        if response.status_code == 200:
            idioma_detectado = response.json()[0]["language"]
            return idioma_detectado
        else:
            print(f"Error detectando idioma (status {response.status_code}): {response.text}")
            return None
    except Exception as e:
        print(f"Excepción en api_detectar_idioma: {e}")
        return None


def api_traducir(texto, idioma_origen, idioma_destino, endpoint, key, region):
    """
    Traduce un texto de un idioma a otro usando la API REST de Translator.
    """
    if not texto or not idioma_destino:
        print(" Error: texto o idioma destino vacío")
        return None
    
    # Si idioma_origen es None, dejar que Azure lo detecte automáticamente
    url = f"{endpoint}/translate?api-version=3.0&to={idioma_destino}"
    if idioma_origen:
        url += f"&from={idioma_origen}"
    
    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Ocp-Apim-Subscription-Region": region,
        "Content-Type": "application/json"
    }
    body = [{"Text": texto}]
    
    try:
        response = requests.post(url, headers=headers, json=body)
        if response.status_code == 200:
            resultado = response.json()[0]["translations"][0]["text"]
            return resultado
        else:
            print(f"Error en API Translator (status {response.status_code}): {response.text}")
            return None
    except Exception as e:
        print(f"Excepción en api_traducir: {e}")
        return None


def api_listar_idiomas(endpoint, key, region):
    """
    Obtiene la lista de idiomas disponibles para traducción.
    Devuelve un diccionario: {codigo: nombre}
    """
    url = f"{endpoint}/languages?api-version=3.0&scope=translation"
    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Ocp-Apim-Subscription-Region": region
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None

    data = response.json()
    idiomas = {}

    for codigo, info in data.get("translation", {}).items():
        idiomas[codigo] = info.get("name", codigo)

    return idiomas

# FUNCIONES SDK SPEECH
def normalizar_idioma_speech(idioma):
    """Convierte códigos de idioma Translator (ej. 'es', 'en') a códigos Speech (ej. 'es-ES', 'en-US').

    Si el idioma ya tiene formato regional (incluye '-') se devuelve tal cual.
    Si no está en el mapeo fijo se intenta construir con patron generico.
    """
    if not idioma:
        return "es-ES"

    if "-" in idioma:
        return idioma 

    base = {
        "es": "es-ES",
        "en": "en-US",
        "fr": "fr-FR",
        "de": "de-DE",
        "it": "it-IT",
        "pt": "pt-BR",
        "ja": "ja-JP",
        "zh": "zh-CN",
        "ru": "ru-RU",
        "ar": "ar-SA",
        "nl": "nl-NL",
        "sv": "sv-SE",
        "no": "nb-NO",
        "fi": "fi-FI",
        "da": "da-DK",
        "ko": "ko-KR"
    }

    idioma_base = idioma.lower()
    if idioma_base in base:
        return base[idioma_base]

    # Construcción para idiomas no predefinidos
    if len(idioma_base) == 2:
        return f"{idioma_base}-{idioma_base.upper()}"

    return "es-ES"


def obtener_idiomas_speech(endpoint, key, region):
    """
        Devuelve diccionario de idiomas traducibles y sus códigos Speech (intento automático).
    """
    idiomas_translator = api_listar_idiomas(endpoint, key, region)
    if not idiomas_translator:
        return None

    idiomas_speech = {}
    for codigo, nombre in idiomas_translator.items():
        idiomas_speech[codigo] = {
            "nombre": nombre,
            "speech_code": normalizar_idioma_speech(codigo)
        }

    return idiomas_speech


def sdk_speech_tts(texto, key, region, idioma="es-ES", voz="es-ES-ElviraNeural", archivo_salida="traduccion.wav"):
    """
        Convierte texto a audio usando el SDK de Azure Speech.
        Crea el archivo de salida en la carpeta del proyecto
    """
    if not texto or len(texto.strip()) == 0:
        print("Error: texto vacío o None")
        return None
    
    archivo_salida = ruta_archivo_proyecto(archivo_salida)

    speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
    speech_config.speech_synthesis_voice_name = voz
    audio_config = speechsdk.audio.AudioOutputConfig(filename=archivo_salida)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    result = synthesizer.speak_text_async(texto).get()
    return archivo_salida if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted else None


def sdk_speech_stt(archivo_audio, key, region, idioma="es-ES"):
    """
    Convierte un archivo de audio a texto usando el SDK de Azure Speech.
    """
    ruta = ruta_archivo_proyecto(archivo_audio)
    
    if not os.path.exists(ruta):
        print(f" Archivo no encontrado: {ruta}")
        return None
    
    idioma_speech = normalizar_idioma_speech(idioma)
    speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
    speech_config.speech_recognition_language = idioma_speech
    audio_config = speechsdk.audio.AudioConfig(filename=ruta)
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    
    print(f"Procesando archivo: {archivo_audio}")
    result = recognizer.recognize_once()
    
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    else:
        print(f"No reconocido: {result.reason}")
        return None


def sdk_speech_stt_microfono(key, region, idioma="es-ES", archivo_fallback="test.wav"):
    """
        Escucha audio del micrófono y convierte a texto.
        Si no se reconoce nada, usa el archivo de fallback.
        Devuelve (texto_reconocido, fuente) donde fuente es 'microfono' o 'fallback'.
    """
    # Intento 1: micrófono 
    print("Escuchando micrófono... (habla ahora)")

    #Configuracion
    idioma_speech = normalizar_idioma_speech(idioma)
    speech_config_mic = speechsdk.SpeechConfig(subscription=key, region=region)
    speech_config_mic.speech_recognition_language = idioma_speech
    audio_config_mic = speechsdk.audio.AudioConfig(use_default_microphone=True)
    recognizer_mic = speechsdk.SpeechRecognizer(speech_config=speech_config_mic, audio_config=audio_config_mic)
    result_mic = recognizer_mic.recognize_once()

    if result_mic.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result_mic.text, "microfono"

    # Intento 2: Si falla o no se reconoce el micro se usa el archivo de prueba para probar funcionalidad
    ruta_fallback = ruta_archivo_proyecto(archivo_fallback)
    print(f"No se reconocio audio del microfono. Usando archivo: {ruta_fallback}")

    if not os.path.exists(ruta_fallback):
        print(f" Archivo '{ruta_fallback}' no encontrado.")
        return None, None

    try:
        texto_fallback = sdk_speech_stt(archivo_fallback, key, region, idioma)
        if texto_fallback:
            return texto_fallback, "fallback"
        else:
            print("Fallback también fallo: no se reconoció texto en el archivo.")
            return None, None

    except Exception as e:
        print(f"Error al leer fallback: {e}")
        return None, None


# FUNCIONES AUXILIARES

def ruta_archivo_proyecto(nombre_archivo):
    """
        Devuelve la ruta absoluta de un archivo en la carpeta del proyecto 
    """
    ruta_base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(ruta_base, nombre_archivo)

def mostrar_idiomas(lista_idiomas):
    """
    Muestra una lista de idiomas numerada.
    """
    if not lista_idiomas:
        print("No hay idiomas disponibles.")
        return

    print("\n📋 Idiomas disponibles:")
    for i, (codigo, nombre) in enumerate(lista_idiomas.items(), start=1):
        print(f"{i}. {nombre} [{codigo}]")


def seleccionar_idioma(lista_idiomas):
    """
    Pide al usuario que seleccione idioma por número.
    Devuelve (codigo, nombre)
    """
    if not lista_idiomas:
        return None, None
    
    codigos = list(lista_idiomas.keys())
    nombres = list(lista_idiomas.values())
    
    try:
        opcion = int(input("Selecciona número: ")) - 1
        if 0 <= opcion < len(codigos):
            codigo = codigos[opcion]
            nombre = nombres[opcion]
            print(f"Seleccionado: {nombre} [{codigo}]")
            return codigo, nombre
        print("Opción fuera de rango.")
        return None, None
    except ValueError:
        print("Debes introducir un número.")
        return None, None


def menu_opciones():
    """
    Muestra el menú principal.
    """
    print("\n-- TRADUCTOR AZURE --")
    print("1. Traducir texto → texto")
    print("2. Traducir audio → texto")
    print("0. Salir")
    return input("Opción: ")


