# YouTube Downloader (yt-dlp)

Un descargador de YouTube completo con soporte para videos individuales, playlists y múltiples formatos. 

## Características

- **Videos individuales** - Descarga cualquier video de YouTube
- **Playlists completas** - Descarga todas las canciones/videos de una playlist
- **Múltiples calidades** - Desde 360p hasta 4K/8K
- **Audio MP3** - Extrae audio como MP3 de alta calidad
- **Compatible con editores** - Convierte automáticamente a H.264 para Sony Vegas/Premiere
- **Detección de copyright** - Salta videos bloqueados automáticamente
- **Progreso en tiempo real** - Muestra velocidad y porcentaje de descarga
- **Loop continuo** - Pregunta si quieres descargar otro video

## Requisitos

- Python 3.8+
- FFmpeg (recomendado para conversión de codecs)
- yt-dlp

## Instalación

1. **Clonar o descargar el proyecto**
   ```bash
   git clone <repositorio>
   cd yt-downloader
   ```

2. **Instalar dependencias**
   ```bash
   pip install yt-dlp
   ```

3. **Instalar FFmpeg** (opcional pero recomendado)
   
   **Windows:**
   ```bash
   winget install Gyan.FFmpeg
   ```
   O descargar desde [ffmpeg.org](https://ffmpeg.org/download.html)

   **macOS:**
   ```bash
   brew install ffmpeg
   ```

   **Linux:**
   ```bash
   sudo apt install ffmpeg
   ```

## Uso

### Ejecutar el descargador

```bash
python yt_downloader.py
```

### Flujo de descarga

1. **Pega la URL** de YouTube
2. **Selecciona tipo de contenido:**
   - 1 = Video individual
   - 2 = Playlist completa
3. **Selecciona formato:**
   - 1 = Video (con selección de calidad)
   - 2 = Solo audio (MP3)
4. **Elige calidad** (si seleccionaste video)
5. **¡Descarga!** - El video se guardará en la carpeta actual

### Ejemplo de uso

```
==================================================
Descargador de YouTube (yt-dlp)
==================================================

URL de YouTube: https://www.youtube.com/watch?v=example

Tipo de contenido:
  1. Video individual
  2. Playlist

Selecciona (1 o 2): 1

Formato:
  1. Video
  2. Solo audio (MP3)

Selecciona (1 o 2): 1

Calidades disponibles:
   (Las marcadas con ⚠️ requieren conversión a H.264 para Sony Vegas)
  1. 360p (mp4) - 41.5 MB [✓ compatible Vegas]
  2. 1080p (mp4) - 150.3 MB [✓ compatible Vegas]
  3. 1440p (mp4) - 280.1 MB ⚠️ [FFmpeg convertirá a H.264]
  4. 2160p (mp4) - 520.5 MB ⚠️ [FFmpeg convertirá a H.264]

Selecciona número de calidad: 4

 Descargando video (FFmpeg convertirá a H.264 para compatibilidad con Vegas)...
 Completado: Nombre del video
```

### Formatos de salida

- **Video**: MP4 con codec H.264 (compatible con todos los editores)
- **Audio**: MP3 a 192kbps
- **4K/8K**: Convierte automáticamente a H.264 para compatibilidad

## Estructura de archivos

```
yt-downloader/
├── yt_downloader.py      # Script principal
├── requirements.txt      # Dependencias
├── README.md            # Este archivo
└── playlist_[nombre]/   # Carpetas de playlists (creadas automáticamente)
```

## Solución de problemas

### Videos bloqueados por copyright

```
 Video bloqueado (copyright): [URL]
```

**Soluciones:**
- El programa salta automáticamente videos bloqueados en playlists, descarga el video con la URL
- Para videos individuales, intenta usar VPN
- Algunos videos simplemente no están disponibles

### Error "JavaScript runtime"

```
WARNING: No supported JavaScript runtime could be found
```

**Solución:** No es crítico. El programa funcionará igual. Si quieres eliminar el warning:
```bash
pip install nodejs
```

### Sony Vegas no detecta el video

**Causa:** Video en VP9/AV1 en lugar de H.264

**Solución:**
1. Asegúrate de tener FFmpeg instalado
2. El programa convertirá automáticamente a H.264
3. Busca calidades marcadas con `✓ compatible Vegas`

### Errores de conexión

```
ERROR: [youtube] Unable to download webpage
```

**Soluciones:**
- Verifica tu conexión a internet
- Intenta con una VPN si el video está geo-bloqueado
- Espera unos minutos e intenta de nuevo

## Actualización

Para mantener yt-dlp actualizado:

```bash
pip install --upgrade yt-dlp
```

## Notas importantes

- **Videos 4K/8K**: YouTube los sirve en VP9, se convierten a H.264
- **Playlists**: Se crea una carpeta automáticamente con el nombre de la playlist
- **Videos privados/bloqueados**: Se saltan automáticamente en playlists
- **Conversión**: Requiere FFmpeg para convertir codecs incompatibles

## Legal

Este software es solo para uso personal y educativo. Respeta los derechos de autor y los términos de servicio de YouTube. No es responsable del mal uso del software.

---

**Creado usando yt-dlp**
