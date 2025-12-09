import flet as ft
import colorgram
from PIL import Image  # Resim sıkıştırma motoru
import os

def main(page: ft.Page):
    # --- AYARLAR ---
    page.title = "Visual Brain"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0F0F1A"
    page.padding = 0
    page.scroll = "AUTO"

    # --- RENK DÖNÜŞÜMÜ ---
    def rgb_to_cmyk(r, g, b):
        if (r, g, b) == (0, 0, 0):
            return 0, 0, 0, 100
        k = 1 - max(r/255, g/255, b/255)
        c = (1 - r/255 - k) / (1 - k)
        m = (1 - g/255 - k) / (1 - k)
        y = (1 - b/255 - k) / (1 - k)
        return round(c*100), round(m*100), round(y*100), round(k*100)

    # --- DOSYA SEÇİLİNCE ---
    def on_file_picked(e: ft.FilePickerResultEvent):
        if e.files:
            dosya_yolu = e.files[0].path
            analiz_baslat(dosya_yolu)

    # --- ANALİZ MOTORU (TURBO MODU) ---
    def analiz_baslat(resim_yolu):
        # Arayüzü Hazırla
        loading_ring.visible = True
        buttons_container.visible = False # Butonları gizle
        img_preview.visible = False
        loading_text.value = "Görüntü işleniyor..."
        loading_text.visible = True
        page.update()

        try:
            # 1. Önizleme
            img_preview.src = resim_yolu
            img_preview.visible = True
            
            # 2. Sıkıştırma (Hız için)
            img = Image.open(resim_yolu)
            img.thumbnail((150, 150)) # Küçük kopyasını oluştur
            kucuk_resim_yolu = os.path.join(os.path.dirname(resim_yolu), "temp_small_scan.jpg")
            img.save(kucuk_resim_yolu)

            # 3. Renk Analizi
            renkler = colorgram.extract(kucuk_resim_yolu, 5)
            colors_column.controls.clear()

            for renk in renkler:
                rgb = renk.rgb
                hex_kod = "#{:02x}{:02x}{:02x}".format(rgb.r, rgb.g, rgb.b)
                cmyk = rgb_to_cmyk(rgb.r, rgb.g, rgb.b)
                
                # Renk Kartı
                kart = ft.Container(
                    content=ft.Row([
                        ft.Container(width=60, height=60, bgcolor=hex_kod, border_radius=10, border=ft.border.all(1, "#00F3FF")),
                        ft.Column([
                            ft.Text(hex_kod, size=18, weight="BOLD", color="#00F3FF", font_family="Consolas"),
                            ft.Text(f"RGB: {rgb.r},{rgb.g},{rgb.b}", size=12, color="white"),
                            ft.Text(f"CMYK: {cmyk}", size=12, color="#FF00FF")
                        ], spacing=2)
                    ]),
                    bgcolor="#1B1B2F",
                    padding=15,
                    border_radius=15,
                    on_click=lambda e, code=hex_kod: pano_kopyala(code)
                )
                colors_column.controls.append(kart)
            
            # Temizlik
            if os.path.exists(kucuk_resim_yolu):
                os.remove(kucuk_resim_yolu)

            # Bitiş
            loading_ring.visible = False
            loading_text.visible = False
            buttons_container.visible = True # Butonları geri getir
            page.update()

        except Exception as e:
            loading_ring.visible = False
            loading_text.visible = False
            buttons_container.visible = True
            page.snack_bar = ft.SnackBar(ft.Text(f"Hata: {e}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    def pano_kopyala(kod):
        page.set_clipboard(kod)
        page.snack_bar = ft.SnackBar(content=ft.Text(f"Kopyalandı: {kod}", color="black", weight="BOLD"), bgcolor="#00F3FF")
        page.snack_bar.open = True
        page.update()

    # --- ARAYÜZ ---
    file_picker = ft.FilePicker(on_result=on_file_picked)
    page.overlay.append(file_picker)

    app_bar = ft.AppBar(title=ft.Text("VISUAL BRAIN", weight="BOLD", color="#00F3FF"), bgcolor="#1B1B2F", center_title=True)
    
    img_preview = ft.Image(src="", width=300, height=300, fit=ft.ImageFit.CONTAIN, visible=False, border_radius=15)
    
    # --- YENİ BUTONLAR ---
    btn_gallery = ft.ElevatedButton(
        text="GALERİ", 
        icon=ft.Icons.IMAGE, 
        bgcolor="#1B1B2F", color="#00F3FF", 
        width=140, height=50, 
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10), side=ft.BorderSide(1, "#00F3FF")),
        on_click=lambda _: file_picker.pick_files(allow_multiple=False)
    )

    btn_camera = ft.ElevatedButton(
        text="KAMERA", 
        icon=ft.Icons.CAMERA_ALT, 
        bgcolor="#00F3FF", color="black", 
        width=140, height=50, 
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        on_click=lambda _: file_picker.pick_files(allow_multiple=False) 
        # Not: Mobilde dosya seçici açılınca "Kamera" seçeneği çıkar.
    )

    # Butonları yan yana koymak için Row (Satır) kullanıyoruz
    buttons_container = ft.Row([btn_gallery, btn_camera], alignment="CENTER", spacing=20)

    loading_ring = ft.ProgressRing(color="#00F3FF", visible=False)
    loading_text = ft.Text("", color="yellow", visible=False)
    
    colors_column = ft.Column(spacing=10, scroll="AUTO")

    # Sayfaya Ekle
    page.add(
        app_bar, 
        ft.Column([
            ft.Container(height=20), 
            img_preview, 
            loading_ring, 
            loading_text, 
            ft.Container(height=20), 
            buttons_container, # Çift butonu buraya koyduk
            ft.Container(height=20), 
            colors_column
        ], horizontal_alignment="CENTER", alignment="CENTER", scroll="AUTO")
    )

ft.app(target=main)
