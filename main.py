import flet as ft
import colorgram
from PIL import Image  # Resim işleme motoru
import os

def main(page: ft.Page):
    # --- AYARLAR ---
    page.title = "Visual Brain"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0F0F1A"
    page.padding = 0
    page.scroll = "AUTO"

    # --- FONKSİYONLAR ---
    def rgb_to_cmyk(r, g, b):
        if (r, g, b) == (0, 0, 0):
            return 0, 0, 0, 100
        k = 1 - max(r/255, g/255, b/255)
        c = (1 - r/255 - k) / (1 - k)
        m = (1 - g/255 - k) / (1 - k)
        y = (1 - b/255 - k) / (1 - k)
        return round(c*100), round(m*100), round(y*100), round(k*100)

    def on_file_picked(e: ft.FilePickerResultEvent):
        if e.files:
            dosya_yolu = e.files[0].path
            analiz_baslat(dosya_yolu)

    def analiz_baslat(resim_yolu):
        loading_ring.visible = True
        btn_upload.visible = False
        img_preview.visible = False
        loading_text.value = "Görüntü işleniyor..."
        loading_text.visible = True
        page.update()

        try:
            # 1. RESMİ EKRANDA GÖSTER (Orijinal Kalite)
            img_preview.src = resim_yolu
            img_preview.visible = True
            
            # 2. TURBO MODU: Analiz için resmi küçült
            # Resmi Pillow ile aç
            img = Image.open(resim_yolu)
            # Resmi 150 piksele kadar küçült (Hız için yeterli)
            img.thumbnail((150, 150))
            # Küçük resmi geçici olarak kaydet
            kucuk_resim_yolu = os.path.join(os.path.dirname(resim_yolu), "temp_small_scan.jpg")
            img.save(kucuk_resim_yolu)

            # 3. RENKLERİ BUL (Küçük resimden - ŞİMŞEK GİBİ OLACAK)
            renkler = colorgram.extract(kucuk_resim_yolu, 5)
            colors_column.controls.clear()

            for renk in renkler:
                rgb = renk.rgb
                hex_kod = "#{:02x}{:02x}{:02x}".format(rgb.r, rgb.g, rgb.b)
                cmyk = rgb_to_cmyk(rgb.r, rgb.g, rgb.b)
                
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
            
            # Geçici dosyayı temizle
            if os.path.exists(kucuk_resim_yolu):
                os.remove(kucuk_resim_yolu)

            loading_ring.visible = False
            loading_text.visible = False
            btn_upload.text = "BAŞKA FOTOĞRAF SEÇ"
            btn_upload.visible = True
            page.update()

        except Exception as e:
            loading_ring.visible = False
            loading_text.visible = False
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
    
    btn_upload = ft.ElevatedButton(text="GALERİDEN SEÇ", icon=ft.Icons.PHOTO_LIBRARY, bgcolor="#00F3FF", color="black", width=250, height=50, on_click=lambda _: file_picker.pick_files(allow_multiple=False))

    loading_ring = ft.ProgressRing(color="#00F3FF", visible=False)
    loading_text = ft.Text("", color="yellow", visible=False) # Bilgi yazısı
    colors_column = ft.Column(spacing=10, scroll="AUTO")

    page.add(app_bar, ft.Column([ft.Container(height=20), img_preview, loading_ring, loading_text, ft.Container(height=20), btn_upload, ft.Container(height=20), colors_column], horizontal_alignment="CENTER", alignment="CENTER", scroll="AUTO"))

ft.app(target=main)
