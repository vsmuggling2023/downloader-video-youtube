import yt_dlp
import os


def hook_progreso(d):
    if d['status'] == 'downloading':
        pct = d.get('_percent_str', '0%')
        speed = d.get('_speed_str', 'N/A')
        print(f"\r📥 {pct} | {speed}", end='', flush=True)
    elif d['status'] == 'finished':
        print()


def obtener_info(url, ignorar_errores=False):
    """Obtener información del video sin descargar"""
    opciones = {
        'quiet': True,
        'no_warnings': True,
        'geo_bypass': True,
        'cookiesfrombrowser': None,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'ignoreerrors': ignorar_errores,  # Ignora videos bloqueados en playlists
    }
    with yt_dlp.YoutubeDL(opciones) as ydl:
        try:
            return ydl.extract_info(url, download=False)
        except Exception as e:
            error_str = str(e)
            if 'Video unavailable' in error_str or 'copyright' in error_str.lower():
                raise Exception(f"Video bloqueado (copyright): {url}")
            raise


def mostrar_calidades(info):
    """Mostrar TODAS las calidades incluyendo 4K/VP9 con conversión automática a H.264"""
    formatos = {}
    resoluciones_vistas = set()
    print("\n📊 Calidades disponibles:")
    print("   (Las marcadas con ⚠️ requieren conversión a H.264 para Sony Vegas)")
    
    # TODOS los formatos de video
    todos_formatos = info.get('formats', [])
    
    # Primero mostrar formatos con audio (progressive)
    for f in todos_formatos:
        if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
            res = f.get('format_note', f.get('resolution', 'N/A'))
            if res not in resoluciones_vistas:
                resoluciones_vistas.add(res)
                ext = f.get('ext', 'mp4')
                size = f.get('filesize') or f.get('filesize_approx')
                size_str = f"{size/1024/1024:.1f} MB" if size else "Tamaño desconocido"
                height = f.get('height', 0)
                vcodec = f.get('vcodec', 'unknown')
                es_h264 = vcodec.startswith('avc1') or vcodec.startswith('h264')
                warning = " [✓ compatible Vegas]" if es_h264 else " ⚠️ [requiere conversión]"
                formatos[res] = {'format_id': f['format_id'], 'has_audio': True, 'height': height, 'vcodec': vcodec, 'es_h264': es_h264}
                print(f"  {len(formatos)}. {res} ({ext}) - {size_str}{warning}")
    
    # Luego mostrar formatos de alta calidad (DASH - video only)
    for f in sorted(todos_formatos, key=lambda x: x.get('height') or 0, reverse=True):
        if f.get('vcodec') != 'none' and f.get('acodec') == 'none':
            res = f.get('format_note', f.get('resolution', 'N/A'))
            if res not in resoluciones_vistas:
                resoluciones_vistas.add(res)
                height = f.get('height', 0)
                ext = f.get('ext', 'mp4')
                size = f.get('filesize') or f.get('filesize_approx')
                size_str = f"{size/1024/1024:.1f} MB" if size else "Tamaño desconocido"
                vcodec = f.get('vcodec', 'unknown')
                es_h264 = vcodec.startswith('avc1') or vcodec.startswith('h264')
                warning = " [✓ compatible Vegas]" if es_h264 else " ⚠️ [FFmpeg convertirá a H.264]"
                formatos[res] = {'format_id': f['format_id'], 'has_audio': False, 'height': height, 'vcodec': vcodec, 'es_h264': es_h264}
                print(f"  {len(formatos)}. {res} ({ext}) - {size_str}{warning}")
    
    if not formatos:
        print("  ⚠️  No se encontraron formatos disponibles.")
    
    return formatos


def descargar(url, solo_audio=False, formato_id=None, carpeta=None, ignorar_errores=False):
    """Descargar video o audio"""
    opciones = {
        'progress_hooks': [hook_progreso],
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': ignorar_errores,
        'outtmpl': '%(title)s.%(ext)s',
        'geo_bypass': True,
        'geo_bypass_country': 'US',
        'cookiesfrombrowser': None,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    if carpeta:
        opciones['outtmpl'] = os.path.join(carpeta, '%(title)s.%(ext)s')
    
    if solo_audio:
        opciones['format'] = 'bestaudio/best'
        opciones['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
        print("🎵 Descargando audio...")
    else:
        if formato_id:
            # Descargar la calidad seleccionada (puede ser VP9)
            opciones['format'] = f"{formato_id}+bestaudio[ext=m4a]/bestaudio"
        else:
            # Default: mejor calidad con H.264 si está disponible
            opciones['format'] = 'best[vcodec^=avc1]/bestvideo+bestaudio/best'
        
        # Convertir a H.264 si es necesario (para VP9/AV1)
        opciones['postprocessors'] = [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }]
        print("📥 Descargando video (FFmpeg convertirá a H.264 para compatibilidad con Vegas)...")
    
    try:
        with yt_dlp.YoutubeDL(opciones) as ydl:
            info = ydl.extract_info(url, download=True)
            print(f"✅ Completado: {info.get('title', 'Sin título')}")
            return True
    except Exception as e:
        error_str = str(e)
        if 'Video unavailable' in error_str or 'copyright' in error_str.lower():
            print(f"⚠️  Video bloqueado (copyright): {url}")
        elif 'Private video' in error_str or 'privado' in error_str.lower():
            print(f"⚠️  Video privado: {url}")
        elif 'Premiere' in error_str or 'estreno' in error_str.lower():
            print(f"⚠️  Estreno/No disponible aún: {url}")
        else:
            print(f"❌ Error: {e}")
        
        if not ignorar_errores:
            return False
        return True


def descargar_video_individual(url):
    """Descargar video con selección de calidad"""
    try:
        print("\n🔍 Analizando video...")
        info = obtener_info(url)
        print(f"📺 {info.get('title', 'Sin título')}")
    except Exception as e:
        error_str = str(e)
        if 'bloqueado' in error_str.lower() or 'copyright' in error_str.lower():
            print(f"⚠️ {e}")
            return
        print(f"❌ Error: {e}")
        return
    
    # Preguntar formato
    print("\n💾 Formato:")
    print("  1. Video (elegir calidad)")
    print("  2. Solo audio (MP3)")
    opcion = input("\nSelecciona (1 o 2): ").strip()
    
    if opcion == "2":
        descargar(url, solo_audio=True)
    else:
        formatos = mostrar_calidades(info)
        
        if formatos:
            seleccion = input("\nSelecciona número de calidad: ").strip()
            try:
                idx = int(seleccion) - 1
                claves = list(formatos.keys())
                res_seleccionada = claves[idx]
                formato_info = formatos[res_seleccionada]
                
                # Usar filtro por altura (incluye VP9/4K si es necesario)
                height = formato_info['height']
                if formato_info['es_h264']:
                    # Ya es H.264, no necesita conversión
                    formato_id = f"bestvideo[height={height}][vcodec^=avc1]"
                    print(f"   → Calidad nativa H.264 seleccionada")
                else:
                    # Es VP9/AV1 - se convertirá con FFmpeg
                    formato_id = f"bestvideo[height={height}]"
                    print(f"   → {formato_info['vcodec'][:20]} detectado - FFmpeg convertirá a H.264")
                
            except (ValueError, IndexError):
                print("❌ Selección inválida, usando mejor calidad disponible")
                formato_id = None
        else:
            print("⚠️  Usando mejor calidad disponible (se convertirá a H.264 si es necesario)")
            formato_id = None
        
        descargar(url, solo_audio=False, formato_id=formato_id)


def descargar_playlist(url, solo_audio=False):
    """Descargar toda una playlist"""
    try:
        print("\n Analizando playlist...")
        info = obtener_info(url, ignorar_errores=True)
        
        if info is None:
            print("  No se pudo acceder a la playlist. Intenta usar una VPN o verificar la URL.")
            return
        
        titulo = info.get('title', 'playlist')
        nombre_carpeta = f"playlist_{titulo.replace(' ', '_').replace('/', '_')[:50]}"
        os.makedirs(nombre_carpeta, exist_ok=True)
        
        print(f"\n Playlist: {titulo}")
        entradas = info.get('entries', [])
        total = len(entradas) if entradas else 0
        print(f"🎬 Total videos: {total}")
        print("=" * 50)
        
        if total == 0:
            print("❌ No se encontraron videos")
            return
        
        exitosos = 0
        fallidos = 0
        
        for i, entrada in enumerate(entradas, 1):
            video_url = entrada.get('webpage_url') or entrada.get('url')
            if not video_url:
                continue
            
            print(f"\n[{i}/{total}]")
            resultado = descargar(video_url, solo_audio=solo_audio, carpeta=nombre_carpeta, ignorar_errores=True)
            if resultado:
                exitosos += 1
            else:
                fallidos += 1
        
        print(f"\n📊 Resumen: {exitosos} exitosos, {fallidos} fallidos")
        
        print(f"\n✅ Playlist guardada en: {nombre_carpeta}")
        
    except Exception as e:
        error_str = str(e)
        if 'Video unavailable' in error_str:
            print(f"⚠️  Algunos videos están bloqueados. Intenta usar una VPN o cookies de cuenta de YouTube.")
        else:
            print(f"❌ Error con playlist: {e}")


def main():
    while True:
        print("=" * 50)
        print("🎬 Descargador de YouTube (yt-dlp)")
        print("=" * 50)
        
        url = input("\n🔗 URL de YouTube: ").strip()
        
        if not url:
            print("❌ URL requerida")
            continue
        
        print("\n📋 Tipo de contenido:")
        print("  1. Video individual")
        print("  2. Playlist")
        tipo = input("\nSelecciona (1 o 2): ").strip()
        
        print("\n💾 Formato:")
        print("  1. Video")
        print("  2. Solo audio (MP3)")
        formato = input("\nSelecciona (1 o 2): ").strip()
        
        solo_audio = (formato == "2")
        
        if tipo == "2":
            descargar_playlist(url, solo_audio)
        elif tipo == "1":
            if solo_audio:
                descargar(url, solo_audio=True)
            else:
                descargar_video_individual(url)
        else:
            print("❌ Opción inválida")
        
        # Preguntar si quiere descargar otro
        print("\n" + "=" * 50)
        otra = input("¿Descargar otro video? (s/n): ").strip().lower()
        if otra not in ['s', 'si', 'sí', 'y', 'yes']:
            print("👋 Adiós!")
            break
        print()


if __name__ == "__main__":
    main()
