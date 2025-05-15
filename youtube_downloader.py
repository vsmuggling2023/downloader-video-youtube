import os
import subprocess
import sys
import yt_dlp
import platform
from pathlib import Path
import requests
import zipfile
import io
import shutil
import traceback

# Configuración global de FFmpeg
FFMPEG_PATH = None
FFMPEG_INSTALADO = False

def verificar_ffmpeg():
    """Verifica si FFmpeg está instalado y accesible en el sistema"""
    global FFMPEG_PATH, FFMPEG_INSTALADO
    
    # Primero verifica si ya tenemos la ruta configurada
    if FFMPEG_PATH and os.path.exists(FFMPEG_PATH):
        FFMPEG_INSTALADO = True
        return True
    
    # Añade la ruta exacta (asegúrate de cambiar esto si tu ruta es diferente)
    custom_path = r'C:\ffmpeg\bin\ffmpeg.exe'
    if os.path.exists(custom_path):
        FFMPEG_PATH = custom_path
        FFMPEG_INSTALADO = True
        return True
        
    # Verifica en el PATH del sistema
    try:
        result = subprocess.run(['ffmpeg', '-version'],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              check=True)
        FFMPEG_PATH = 'ffmpeg'  # Usa el del PATH
        FFMPEG_INSTALADO = True
        return True
    except:
        # Busca en ubicaciones comunes
        common_paths = [
            r'C:\ffmpeg\ffmpeg.exe',  # Añadido sin 'bin'
            r'C:\ffmpeg\bin\ffmpeg.exe',
            r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
            os.path.join(os.environ.get('PROGRAMFILES', ''), 'ffmpeg', 'bin', 'ffmpeg.exe'),
            './ffmpeg.exe'
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                FFMPEG_PATH = path
                FFMPEG_INSTALADO = True
                return True
                
        return False

def descargar_e_instalar_ffmpeg():
    """Descarga e instala FFmpeg automáticamente para Windows"""
    global FFMPEG_PATH, FFMPEG_INSTALADO
    
    try:
        if platform.system() != 'Windows':
            print("La instalación automática solo está disponible para Windows")
            return False

        print("\n🔧 FFmpeg no está instalado. Iniciando instalación automática...")
        
        # URL de FFmpeg para Windows (versión estática)
        url = 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip'
        ffmpeg_dir = Path.home() / 'ffmpeg'
        ffmpeg_dir.mkdir(exist_ok=True)

        print("⬇️ Descargando FFmpeg... (Esto puede tomar unos minutos)")
        response = requests.get(url, stream=True)
        response.raise_for_status()

        print("📦 Extrayendo archivos...")
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            zip_ref.extractall(ffmpeg_dir)

        # Busca el directorio bin
        extracted_dir = next(ffmpeg_dir.glob('ffmpeg-*-essentials_build'))
        bin_dir = extracted_dir / 'bin'
        FFMPEG_PATH = str(bin_dir / 'ffmpeg.exe')
        
        # Añade al PATH temporalmente para esta sesión
        os.environ['PATH'] += os.pathsep + str(bin_dir)
        
        # Verificar instalación
        if verificar_ffmpeg():
            print(f"\n✅ FFmpeg instalado correctamente en: {bin_dir}")
            print("Nota: Esta instalación es temporal para la sesión actual.")
            print("Para instalación permanente, añade esta ruta a tu PATH:")
            print(f"{bin_dir}")
            FFMPEG_INSTALADO = True
            return True
        else:
            print("❌ La instalación automática falló")
            return False
            
    except Exception as e:
        print(f"\n❌ Error durante la instalación: {str(e)}")
        print("\nℹ️ Por favor instala FFmpeg manualmente:")
        print("1. Descarga desde https://www.gyan.dev/ffmpeg/builds/")
        print("2. Extrae el archivo ZIP")
        print("3. Añade la carpeta 'bin' a tu variable de entorno PATH")
        return False

def seleccionar_formato():
    """Pregunta al usuario por el formato de salida deseado"""
    print("\n📁 Selecciona el formato de salida:")
    print("1 - MP4 (método 1 - audio AAC)")
    print("2 - MP4 (método 2 - audio MP3)")
    print("3 - MP4 (método 3 - solo copiar)")
    print("4 - Solo audio (MP3)")
    print("5 - MP4 (sin conversión)")
    opcion = input("Elige una opción (1-5): ")

    formatos = {
        '1': {
            'ext': 'mp4',
            'requiere_ffmpeg': True,
            'formato_descarga': None,  # Se establecerá según la calidad seleccionada
            'postproc': {
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            },
            'post_args': {
                'FFmpegVideoConvertor': ['-c:v', 'copy', '-c:a', 'aac', '-strict', 'experimental']
            }
        },
        '2': {
            'ext': 'mp4',
            'requiere_ffmpeg': True,
            'formato_descarga': None,  # Se establecerá según la calidad seleccionada
            'postproc': {
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            },
            'post_args': {
                'FFmpegVideoConvertor': ['-c:v', 'copy', '-c:a', 'libmp3lame', '-q:a', '4']
            }
        },
        '3': {
            'ext': 'mp4',
            'requiere_ffmpeg': True,
            'formato_descarga': None,  # Se establecerá según la calidad seleccionada
            'postproc': {
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            },
            'post_args': {
                'FFmpegVideoConvertor': ['-c', 'copy']
            }
        },
        '4': {
            'ext': 'mp3',
            'requiere_ffmpeg': True,
            'formato_descarga': 'bestaudio/best',
            'postproc': {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }
        },
        '5': {
            'ext': 'mp4',
            'requiere_ffmpeg': False,
            'formato_descarga': None,  # Se establecerá según la calidad seleccionada
            'postproc': None
        }
    }

    return formatos.get(opcion, formatos['1'])

def progress_hook(d):
    if d['status'] == 'downloading':
        porcentaje = d.get('_percent_str', '??%')
        velocidad = d.get('_speed_str', '? KiB/s')
        eta = d.get('_eta_str', '??:??')
        # \r permite sobrescribir la línea actual
        if 'playlist_index' in d:
            sys.stdout.write(f"\r🎬 Playlist {d['playlist_index']}/{d.get('playlist_count', '?')} - {porcentaje} a {velocidad} | ETA: {eta}")
        else:
            sys.stdout.write(f"\r⬇️ Descargando: {porcentaje} a {velocidad} | ETA: {eta}")
        sys.stdout.flush()
    elif d['status'] == 'finished':
        print("\n✅ Descarga completa, procesando...")
    elif d['status'] == 'error':
        print(f"\n❌ Error: {d.get('error', 'desconocido')}")

def descargar_video(url, calidad, formato, es_playlist=False):
    """Descarga un video o playlist con la calidad y formato especificados"""
    global FFMPEG_PATH, FFMPEG_INSTALADO

    # Verificar si necesita FFmpeg
    if formato['requiere_ffmpeg'] and not FFMPEG_INSTALADO:
        if platform.system() == 'Windows':
            if not descargar_e_instalar_ffmpeg():
                print("\n⚠️ Usando formato alternativo que no requiere FFmpeg")
                formato = {
                    'ext': 'mp4',
                    'requiere_ffmpeg': False,
                    'formato_descarga': 'best[ext=mp4]',
                    'postproc': None
                }
        else:
            print("❌ FFmpeg no está instalado. Instálalo manualmente.")
            return

    # Si el formato no tiene un formato de descarga específico, usar la calidad seleccionada
    if formato['formato_descarga'] is None:
        formato_final = calidad
    else:
        formato_final = formato['formato_descarga']

    # Configurar opciones básicas
    ydl_opts = {
        'format': formato_final,
        'outtmpl': '%(title)s.%(ext)s',
        'progress_hooks': [progress_hook],
        'merge_output_format': 'mp4' if formato['ext'] == 'mp4' else None
    }

    # Configurar FFmpeg
    if formato['requiere_ffmpeg'] and FFMPEG_PATH:
        ydl_opts['ffmpeg_location'] = FFMPEG_PATH

    # Configurar postprocesamiento si es necesario
    if formato['postproc']:
        ydl_opts['postprocessors'] = [formato['postproc']]
        if 'post_args' in formato:
            ydl_opts['postprocessor_args'] = formato['post_args']

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            if es_playlist:
                # Sanitizar nombre de la carpeta (quitar caracteres no válidos en Windows)
                playlist_title = info.get('title', 'Playlist')
                playlist_title = "".join(c for c in playlist_title if c not in r'\/:*?"<>|')
                carpeta_playlist = Path(playlist_title).resolve()

                try:
                    carpeta_playlist.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    print(f"\n❌ No se pudo crear la carpeta '{carpeta_playlist}': {e}")
                    return

                # Cambiar plantilla de salida para que use la nueva carpeta
                ydl_opts['outtmpl'] = str(carpeta_playlist / '%(playlist_index)s - %(title)s.%(ext)s')
                ydl_opts['ignoreerrors'] = True

                print(f"\n📝 Información de la Playlist:")
                print(f"Título: {playlist_title}")
                print(f"Videos en playlist: {info.get('playlist_count', '?')}")
                print(f"Formato final: {formato['ext'].upper()}")
                print(f"Resolución seleccionada: {calidad}")
            else:
                print(f"\n📝 Información del video:")
                print(f"Título: {info.get('title', 'Desconocido')}")
                print(f"Duración: {info.get('duration_string', '?')}")
                print(f"Formato final: {formato['ext'].upper()}")
                print(f"Resolución seleccionada: {calidad}")

            confirmar = input("\n¿Confirmar descarga? (s/n): ").lower()
            if confirmar == 's':
                print("\n⬇️ Iniciando descarga...")
                ydl.download([url])
                print("\n✅ Descarga completada exitosamente!")
    except Exception as e:
        print(f"\n❌ Error al descargar: {str(e)}")

        if "ffmpeg is not installed" in str(e):
            print("ℹ️ Aunque FFmpeg está instalado, no se pudo acceder. Prueba reiniciando tu terminal/IDE.")
        elif "Postprocessing: Conversion failed!" in str(e):
            print("\n🔧 Sugerencias para resolver el error de conversión:")
            print("1. Prueba con otro método de formato MP4 (opciones 1, 2 o 3)")
            print("2. Intenta con una calidad menor (720p o 480p)")
            print("3. Verifica que tu versión de FFmpeg es completa:")
            print("   - Descarga 'essentials_build' desde https://www.gyan.dev/ffmpeg/builds/")
            print("   - Reemplaza tu instalación actual")

            if hasattr(e, 'stderr') and e.stderr:
                print("\n🔍 Error detallado de FFmpeg:")
                print(e.stderr)

def mostrar_calidades():
    print("\n🎬 Opciones de calidad:")
    print("1 - Mejor calidad disponible")
    print("2 - 1080p")
    print("3 - 720p HD")
    print("4 - 480p")
    print("5 - 360p")
    print("6 - Ver todos los formatos disponibles")
    print("0 - Volver al menú principal")

def seleccionar_calidad(url, es_playlist=False):
    while True:
        mostrar_calidades()
        opcion = input("Elige una opción: ")

        calidad_map = {
            '1': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            '2': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best',
            '3': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best',
            '4': 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best',
            '5': 'bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]/best'
        }

        if opcion == '6':
            try:
                with yt_dlp.YoutubeDL() as ydl:
                    info = ydl.extract_info(url, download=False)
                    print("\n📋 Formatos disponibles:")
                    if es_playlist and 'entries' in info:
                        # Mostrar formatos del primer video de la playlist
                        first_video = info['entries'][0]
                        for f in first_video['formats']:
                            print(f"{f['format_id']}: {f.get('ext', '?')} {f.get('resolution', '?')} {f.get('note', '')}")
                    else:
                        for f in info['formats']:
                            print(f"{f['format_id']}: {f.get('ext', '?')} {f.get('resolution', '?')} {f.get('note', '')}")
            except Exception as e:
                print(f"❌ Error al obtener formatos: {str(e)}")
            continue
        
        elif opcion in calidad_map:
            return calidad_map[opcion]

        elif opcion == '0':
            return None

        else:
            print("❌ Opción no válida. Intenta nuevamente.")

def es_url_playlist(url):
    """Determina si la URL es de una playlist de YouTube"""
    return 'list=' in url or 'playlist' in url

def main():
    print("📺 YouTube Downloader - Videos y Playlists (MP3 y MP4)")

    # Verificar dependencias
    try:
        import yt_dlp
        import requests
    except ImportError:
        print("❌ Faltan dependencias. Instala con:")
        print("pip install yt-dlp requests")
        sys.exit(1)

    # Verificar FFmpeg al inicio
    if verificar_ffmpeg():
        print(f"✅ FFmpeg encontrado en: {FFMPEG_PATH}")
    else:
        print("⚠️ FFmpeg no encontrado. Algunas funciones podrían no estar disponibles.")

    while True:
        url = input("\nIngresa la URL del video o playlist (o 'salir' para terminar): ")
        if url.lower() in ['salir', 'exit', '']:
            break

        es_playlist = es_url_playlist(url)
        
        if es_playlist:
            print("\n🔍 Se ha detectado una playlist de YouTube")

        calidad = seleccionar_calidad(url, es_playlist)
        if calidad is None:
            continue

        formato = seleccionar_formato()

        print(f"\n⚙️ Configuración seleccionada:")
        print(f"Tipo: {'Playlist' if es_playlist else 'Video individual'}")
        print(f"Resolución: {'Mejor disponible' if 'best' in calidad else calidad}")
        print(f"Formato final: {formato['ext'].upper()}")

        descargar_video(url, calidad, formato, es_playlist)

if __name__ == "__main__":
    main()