# Traductor Azure - UT4 Ejercicio 1 - Álvaro Fernández Becerra

Aplicación de traducción de texto y audio utilizando los servicios de Microsoft Azure: **Azure Translator** y **Azure Speech**.

## Funcionalidades **Traducir texto a texto**: Introduce un texto en el idioma origen y obtén la traduccion al idioma destino

1. **Traducir audio a texto**: Captura audio del micrófono en el idioma origen, lo transcribe y lo traduce al idioma destino
3. **Reproducción en audio**: Tras cada traducción, se ofrece la opción de escuchar el resultado medainte TTS
4. **Detección automática de idioma**: Se detecta el idioma del texto introducido y se avisa si difiere del seleccionado
5. **Listado de idiomas dinámico**: Los idiomas disponibles se obtienen en tiempo real desde la API de Azure Translator

## Servicios Azure utilizados

- **Azure Translator** (API REST): Detección de idioma, listado de idiomas disponibles y traducción de texto
- **Azure Speech** (SDK): Text-to-Speech (TTS) para generar audio y Speech-to-Text (STT) para reconocer voz desde micrófono o archivo

## Requisitos previos

- Python 3.8+
- Suscripción activa a **Azure AI Services** con los recursos:
  - Azure Translator (clave, endpoint y región)
  - Azure Speech (clave y región)
- Micrófono disponible (opcional; si no hay audio válido se usa `test.wav` como fallback)

## Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
```

### 2. Crear y activar entorno virtual 

```bash
python -m venv venv
```

En Windows:

```bash
venv\Scripts\activate
```

En Linux/Mac:

```bash
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno (.env)

Modifica el archivo `env-ejemplo` con tus claves y renombralo a `.env`

O crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```
TRAD_KEY1=tu_clave_azure_translator
ENDPOINT_TRAD=https://api.cognitive.microsofttranslator.com
SPEECH_KEY1=tu_clave_azure_speech
ENDPOINT_SPEECH=https://tu-region.api.cognitive.microsoft.com
REGION=tu_region_azure
```

Puedes obtener las claves desde el portal de Azure: https://portal.azure.com

## Uso

```bash
python main.py
```

### Menú interactivo

```
-- TRADUCTOR AZURE --
1. Traducir texto → texto
2. Traducir audio → texto
0. Salir
```

**Opción 1 - Texto a texto:**

- Selecciona el idioma de origen y destino de la lista numerada.
- Escribe el texto a traducir
- Se muestra la traducción; se ofrece reproducirla en audio

**Opción 2 - Audio a texto:**

- Selecciona el idioma de origen y destino de la lista numerada
- Habla al micrófono (si no se detecta audio se usará `test.wav` automáticamente)
- Se muestra el texto reconocido y su traducción; se ofrece reproducirla en audio

## Estructura del proyecto

```
.
├── main.py              # Menú principal y flujo de la aplicación
├── funciones.py         # Funciones de API Translator, SDK Speech y auxiliares
├── test.wav             # Audio de prueba (fallback si el micrófono no funciona)
├── requirements.txt     # Dependencias Python
├── .env-ejemplo         # Variables de entorno con claves Azure 
├── .gitignore           # Archivos a ignorar en Git
└── README.md            # Este archivo
```

### Archivos principales

**main.py**
Contiene el menú principal y las funciones `probar_texto_a_texto()` y `audio_a_texto()` que completan el flujo de la aplicacion.

**funciones.py**
Módulo con todas las funciones divididas en tres bloques:

- **API Translator**: `api_detectar_idioma()`, `api_traducir()`, `api_listar_idiomas()`
- **SDK Speech**: `sdk_speech_tts()`, `sdk_speech_stt()`, `sdk_speech_stt_microfono()`, `normalizar_idioma_speech()`
- **Auxiliares**: `mostrar_idiomas()`, `seleccionar_idioma()`, `menu_opciones()`, `ruta_archivo_proyecto()`

**requirements.txt**
Dependencias del proyecto:

- `requests`: Llamadas a la API REST de Azure Translator
- `python-dotenv`: Lectura de variables de entorno desde `.env`
- `azure-cognitiveservices-speech`: SDK oficial de Azure Speech para TTS y STT

**test.wav**
Archivo de audio de prueba usado como fallback cuando el micrófono no está disponible o no se reconoce audio.

## Obtener credenciales Azure

1. Acceder a https://portal.azure.com
2. Crear un recurso **Translator** en **Azure AI Services**
3. Crear un recurso **Speech** en **Azure AI Services**
4. Copiar las claves y región de cada recurso en el archivo `.env`

Con la suscripción gratuita (F0) se pueden realizar hasta 2 millones de caracteres/mes en Translator y 5 horas de audio/mes en Speech.

## Autor

Álvaro Fernández Becerra
