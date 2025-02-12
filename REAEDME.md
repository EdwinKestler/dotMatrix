# Video Filter App with PyQt5 and OpenCV

Este proyecto es una aplicación de filtro de video que utiliza PyQt5 para la interfaz de usuario y OpenCV para el procesamiento de video. La aplicación permite aplicar varios filtros a un video en tiempo real desde una cámara web o un archivo de video.

## Requisitos

Asegúrate de tener instaladas las siguientes dependencias antes de ejecutar la aplicación:

```
aiofiles==23.2.1
annotated-types==0.7.0
anyio==4.8.0
certifi==2025.1.31
charset-normalizer==3.4.1
click==8.1.8
colorama==0.4.6
cupy-cuda11x==13.3.0
decorator==4.4.2
fastapi==0.115.8
fastrlock==0.8.3
ffmpy==0.5.0
filelock==3.17.0
fsspec==2025.2.0
gradio==5.15.0
gradio_client==1.7.0
h11==0.14.0
httpcore==1.0.7
httpx==0.28.1
huggingface-hub==0.28.1
idna==3.10
imageio==2.37.0
imageio-ffmpeg==0.6.0
Jinja2==3.1.5
markdown-it-py==3.0.0
MarkupSafe==2.1.5
mdurl==0.1.2
moviepy==1.0.3
numpy==2.2.2
opencv-python==4.11.0.86
orjson==3.10.15
packaging==24.2
pandas==2.2.3
pillow==10.4.0
proglog==0.1.10
pydantic==2.10.6
pydantic_core==2.27.2
pydub==0.25.1
Pygments==2.19.1
PyQt5==5.15.11
PyQt5-Qt5==5.15.2
PyQt5_sip==12.17.0
python-dateutil==2.9.0.post0
python-dotenv==1.0.1
python-multipart==0.0.20
pytz==2025.1
PyYAML==6.0.2
requests==2.32.3
rich==13.9.4
ruff==0.9.6
safehttpx==0.1.6
semantic-version==2.10.0
shellingham==1.5.4
six==1.17.0
sniffio==1.3.1
starlette==0.45.3
tomlkit==0.13.2
tqdm==4.67.1
typer==0.15.1
typing_extensions==4.12.2
tzdata==2025.1
urllib3==2.3.0
uvicorn==0.34.0
websockets==14.2
```

**Ambiente**: Python 3.11.9, CUDA 11.x

## Instalación

1. Clona este repositorio:
    ```bash
    git clone https://github.com/tu_usuario/dotMatrix.git
    cd dotMatrix
    ```

2. Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

## Uso

Para ejecutar la aplicación, utiliza el siguiente comando:

```bash
python /e:/dotMatrix/src/pqtpydotmovie.py
```

### Características

- **Tamaño de punto ajustable**: Usa el control deslizante para cambiar el tamaño de los puntos en el filtro.
- **Umbral adaptativo**: Activa o desactiva el umbral adaptativo con la casilla de verificación.
- **Efecto de dithering**: Activa o desactiva el efecto de dithering (Floyd–Steinberg) con la casilla de verificación.
- **Carga de video**: Carga un archivo de video (.mp4, .avi, .mov) para aplicar los filtros.
- **Guardar salida**: Guarda el video procesado en un archivo de salida.

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o envía un pull request para cualquier mejora o corrección.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.