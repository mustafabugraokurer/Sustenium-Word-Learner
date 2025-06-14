import tkinter as tk
from tkinter import messagebox
import random
import json
import pandas as pd
from itertools import chain
import time
import os
import sys

# PyInstaller ile paketlenmişse geçerli dizini ayarlayın
if getattr(sys, 'frozen', False):
    # PyInstaller ile paketlenmiş dosya konumu
    application_path = sys._MEIPASS
else:
    # Normal çalıştırma durumu
    application_path = os.path.dirname(__file__)

file_path = os.path.join(application_path, "The_Oxford_3000.xlsx")
# Renk Paleti
COLORS = {
    "background": "#ECF0F1",
    "primary": "#2C3E50",
    "accent": "#E67E22",
    "correct": "#27AE60",
    "wrong": "#E74C3C",
    "text": "#34495E",
    "button_bg": "#3498DB",
    "button_fg": "white"
}

# GUI Penceresi
root = tk.Tk()
root.title("SUSTENIUM")
root.geometry("700x650")
root.configure(bg=COLORS['background'])

# Excel Dosyasını Yükleme
df = pd.read_excel(file_path)

# Kategori Verileri
category_words = {
    "Bilmiyorum": {},
    "Orta": {},
    "Ogrendiklerim": {}
}


# Kategori Verilerini Kaydetme
def save_category_data():
    with open("category_data.json", "w") as f:
        json.dump(category_words, f)


# Kategori Verilerini Yükleme
def load_category_data():
    global category_words
    try:
        with open("category_data.json", "r") as f:
            loaded_data = json.load(f)
            category_words = {
                category: {word: correct_count for word, correct_count in words.items()}
                for category, words in loaded_data.items()
            }
    except FileNotFoundError:
        category_words = {
            "Bilmiyorum": {},
            "Orta": {},
            "Ogrendiklerim": {}
        }


# Rastgele Görülmemiş Bir Kelime Getirme Fonksiyonu
def get_random_unseen_word():
    used_words = set(chain(
        category_words["Bilmiyorum"].keys(),
        category_words["Orta"].keys(),
        category_words["Ogrendiklerim"].keys()
    ))
    unseen_words = df[~df['English Words'].isin(used_words)]['English Words'].tolist()
    return random.choice(unseen_words) if unseen_words else None


# Kelimeyi Kategoriye Ekleme
def add_to_category(word, category):
    if word not in category_words[category]:
        category_words[category][word] = 0  # Doğru cevap sayısını sıfırdan başlat
    save_category_data()
    update_category_counts()


# Geri Dön Fonksiyonu
def return_to_main_menu():
    for widget in root.winfo_children():
        widget.pack_forget()
    main_menu()


# Kategori verilerini sıfırlama
def reset_data():
    global category_words
    category_words = {
        "Bilmiyorum": {},
        "Orta": {},
        "Ogrendiklerim": {}
    }
    save_category_data()
    messagebox.showinfo("Sıfırla", "Tüm veriler sıfırlandı. Yeni kullanıcılar için başlangıç durumuna dönüldü.")
    update_category_counts()


# Kategori kelime sayısını güncelleme
def update_category_counts(frame=None):
    counts_text = f"Bilmiyorum: {len(category_words['Bilmiyorum'])} | Orta: {len(category_words['Orta'])} | Ogrendiklerim: {len(category_words['Ogrendiklerim'])}"
    if frame:
        counts_label = tk.Label(frame, text=counts_text, font=("Helvetica", 12), bg=COLORS['background'])
        counts_label.pack(pady=10)
    else:
        print(counts_text)


# Hakkında Bölümü
def show_about():
    messagebox.showinfo("Hakkında",
                        "Bu uygulama Oxford 3000, A1'den B2 seviyesine kadar İngilizce öğrenilmesi gereken en önemli 3000 kelimenin listesine göre hazırlanmıştır.\n\nYapımcı: Mustafa Buğra Okurer")


# Ayarlar Menüsü
def settings_menu():
    for widget in root.winfo_children():
        widget.pack_forget()

    settings_frame = tk.Frame(root, bg=COLORS['background'])
    settings_frame.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(settings_frame, text="Ayarlar", font=("Helvetica", 24), bg=COLORS['background'],
             fg=COLORS['primary']).pack(pady=20)

    # Verileri Sıfırlama Butonu
    tk.Button(settings_frame, text="Verileri Sıfırla", command=reset_data, font=("Helvetica", 14),
              bg=COLORS['accent'], fg=COLORS['button_fg'], relief="solid", width=20).pack(pady=10)

    # Hakkında Butonu
    tk.Button(settings_frame, text="Hakkında", command=show_about, font=("Helvetica", 14),
              bg=COLORS['primary'], fg=COLORS['button_fg'], relief="solid", width=20).pack(pady=10)

    # Geri Dön Butonu
    tk.Button(settings_frame, text="Ana Menüye Dön", command=return_to_main_menu,
              font=("Helvetica", 14), bg=COLORS['wrong'], fg=COLORS['button_fg']).pack(pady=20)


# Yeni Kelime Göstermek için Ekran
def show_word_with_category_options():
    for widget in root.winfo_children():
        widget.pack_forget()

    word_frame = tk.Frame(root, bg=COLORS['background'])
    word_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def display_word():
        for widget in word_frame.winfo_children():
            widget.destroy()

        word = get_random_unseen_word()
        if word is None:
            messagebox.showinfo("Bilgi", "Kategoriye eklenmemiş yeni kelime kalmadı!")
            return_to_main_menu()
            return

        word_row = df[df['English Words'] == word].iloc[0]
        correct_answer = word_row['Türkçe anlamları']

        card_frame = tk.Frame(word_frame, width=350, height=250, bg=COLORS['primary'], relief="raised", bd=4)
        card_frame.pack(pady=10)
        front_text = tk.Label(card_frame, text=word, font=("Helvetica", 18, "bold"), bg=COLORS['primary'],
                              fg=COLORS['button_fg'])
        back_text = tk.Label(card_frame, text=correct_answer, font=("Helvetica", 18, "bold"), bg=COLORS['correct'],
                             fg=COLORS['button_fg'])
        front_text.place(relx=0.5, rely=0.5, anchor="center")

        is_flipped = [False]

        def flip():
            if not is_flipped[0]:
                flip_card(card_frame, front_text, back_text)
            else:
                flip_card(card_frame, back_text, front_text)
            is_flipped[0] = not is_flipped[0]

        tk.Button(word_frame, text="Anlamını Göster", command=flip, font=("Helvetica", 14),
                  bg=COLORS['button_bg'], fg=COLORS['button_fg'], relief="solid").pack(pady=10)

        category_buttons = [
            ("Bilmiyorum", lambda: add_to_category(word, "Bilmiyorum"), COLORS['wrong']),
            ("Orta", lambda: add_to_category(word, "Orta"), COLORS['accent']),
            ("Öğrendiklerim", lambda: add_to_category(word, "Ogrendiklerim"), COLORS['correct'])
        ]
        options_frame = tk.Frame(word_frame, bg=COLORS['background'])
        options_frame.pack(pady=10)

        for text, command, color in category_buttons:
            tk.Button(options_frame, text=text, command=command, font=("Helvetica", 14),
                      bg=color, fg=COLORS['button_fg'], relief="raised", width=15).pack(side="left", padx=5)

        # Sıradaki Kelimeye Geçiş Butonu
        tk.Button(word_frame, text="Sıradaki Kelime", command=display_word, font=("Helvetica", 14),
                  bg=COLORS['button_bg'], fg=COLORS['button_fg'], relief="solid").pack(pady=10)

        tk.Button(word_frame, text="Ana Menüye Dön", command=return_to_main_menu,
                  font=("Helvetica", 14), bg=COLORS['wrong'], fg=COLORS['button_fg']).pack(pady=20)

    display_word()


# Kart Döndürme Animasyonu
def flip_card(card_frame, front_text, back_text):
    for i in range(10):
        card_frame.update()
        card_frame.config(width=300 - (i * 10), height=200)
        time.sleep(0.02)
    front_text.place_forget()
    back_text.place(relx=0.5, rely=0.5, anchor="center")
    for i in range(10):
        card_frame.update()
        card_frame.config(width=100 + (i * 20), height=200)
        time.sleep(0.02)


# Global değişken olarak result_label, remaining_words_label ve info_label tanımlıyoruz
result_label = None
remaining_words_label = None
info_label = None  # info_label'i global olarak tanımlıyoruz

# Ana Menü
def main_menu():
    global result_label, info_label

    for widget in root.winfo_children():
        widget.pack_forget()

    # Ana menü başlığı
    tk.Label(root, text="İngilizce-Türkçe Kelime Öğrenme", font=("Helvetica", 24), bg=COLORS['background'],
             fg=COLORS['primary']).pack(pady=20)

    # Kategori Butonları
    categories = [
        ("Yeni Kelime Ekle", show_word_with_category_options, COLORS['button_bg']),
        ("Bilmediklerim", lambda: start_category_quiz("Bilmiyorum"), COLORS['wrong']),
        ("Az Bildiklerim", lambda: start_category_quiz("Orta"), COLORS['accent']),
        ("Öğrendiklerim", lambda: start_category_quiz("Ogrendiklerim"), COLORS['correct'])
    ]

    # Kategori Butonlarını Gösterme
    for text, command, color in categories:
        tk.Button(root, text=text, command=command, font=("Helvetica", 16), bg=color,
                  fg=COLORS['button_fg'], relief="solid", width=30).pack(pady=10)

    # Ayarlar Butonu
    tk.Button(root, text="Ayarlar", command=settings_menu,
              font=("Helvetica", 14), bg=COLORS['accent'], fg=COLORS['button_fg'], relief="solid", width=15).pack(pady=10)

    # Çıkış Butonu
    tk.Button(root, text="Çıkış", command=root.quit, font=("Helvetica", 14),
              bg=COLORS['wrong'], fg=COLORS['button_fg'], relief="solid", width=15).pack(pady=10)

    # Kategori Bilgi Kutusu - Çıkış butonunun altında
    info_text = (
        f"Bilmediklerim: {len(category_words['Bilmiyorum'])} kelime\n"
        f"Az Bildiklerim: {len(category_words['Orta'])} kelime\n"
        f"Öğrendiklerim: {len(category_words['Ogrendiklerim'])} kelime"
    )
    # info_label'i yeniden oluşturup güncel bilgiyle ekliyoruz
    info_label = tk.Label(root, text=info_text, font=("Helvetica", 12), bg=COLORS['background'], fg=COLORS['text'])
    info_label.pack(pady=20)  # Bilgi kutusunu görünür hale getirmek için pack ekliyoruz

# Kategori Sınavını Başlatma
def start_category_quiz(category):
    global result_label, remaining_words_label  # Global değişkenlere erişiyoruz

    # Tüm widget'ları temizliyoruz
    for widget in root.winfo_children():
        widget.pack_forget()

    # Geri Bildirim Etiketi (Doğru/Yanlış) - Her kategoriye girişte yeniden oluşturuyoruz
    result_label = tk.Label(root, text="", font=("Helvetica", 16), bg=COLORS['background'])
    result_label.pack(pady=(20, 0))  # Ekranın üst kısmında yerleştiriyoruz

    # Quiz çerçevesini oluşturuyoruz
    quiz_frame = tk.Frame(root, bg=COLORS['background'])
    quiz_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Kalan kelime sayısını göster
    remaining_words = len(category_words[category])
    remaining_words_label = tk.Label(root, text=f"Kalan kelime sayısı: {remaining_words}",
                                     font=("Helvetica", 14, "bold"), bg=COLORS['background'], fg=COLORS['accent'])
    remaining_words_label.pack(pady=10)

    # İlk soruyu başlat
    show_category_quiz_question(quiz_frame, category)

# Kategori Sınavı Sorusu
def show_category_quiz_question(frame, category):
    global result_label, remaining_words_label  # Global değişkenlere erişiyoruz

    # Kelime listesi boşsa kullanıcıya sınavın bittiğini göster
    if not category_words[category]:
        result_label.config(text="Sınav bitti! Kategoriye eklenmiş başka kelime yok.", fg=COLORS['accent'])
        tk.Button(root, text="Ana Menüye Dön", command=return_to_main_menu, font=("Helvetica", 14),
                  bg=COLORS['wrong'], fg='white').pack(pady=20)
        return

    word = random.choice(list(category_words[category].keys()))
    word_row = df[df['English Words'] == word]

    # Kelime veri çerçevesinde bulunamazsa ana menüye dön
    if word_row.empty:
        result_label.config(text="Kelime bulunamadı", fg=COLORS['wrong'])
        return_to_main_menu()
        return

    correct_answer = word_row.iloc[0]['Türkçe anlamları']
    tk.Label(frame, text=word, font=("Helvetica", 16, "bold"), bg=COLORS['background']).pack(pady=10)

    wrong_answers = df[df['Türkçe anlamları'] != correct_answer].sample(3)['Türkçe anlamları'].tolist()
    options = wrong_answers + [correct_answer]
    random.shuffle(options)

    def check_answer(selected_option):
        if selected_option == correct_answer:
            result_label.config(text="Doğru!", fg=COLORS['correct'])
            category_words[category][word] += 1
            if category_words[category][word] >= 4:
                advance_word_to_next_stage(word, category)
        else:
            result_label.config(text=f"Yanlış! Doğru cevap: {correct_answer}", fg=COLORS['wrong'])

        # Kalan kelime sayısını güncelleyerek remaining_words_label'i güncelliyoruz
        remaining_words = len(category_words[category])
        remaining_words_label.config(text=f"Kalan kelime sayısı: {remaining_words}")

        # Soru bittikten sonra frame içindekileri temizliyoruz ama result_label ve remaining_words_label üst seviyede kalıyor
        for widget in frame.winfo_children():
            widget.destroy()

        show_category_quiz_question(frame, category)

    for option in options:
        tk.Button(frame, text=option, command=lambda opt=option: check_answer(opt), font=("Helvetica", 14),
                  bg='#D6EAF8', width=25).pack(pady=5)

    tk.Button(frame, text="Ana Menüye Dön", command=return_to_main_menu, font=("Helvetica", 14),
              bg=COLORS['wrong'], fg='white').pack(pady=20)

# Ana Menüye Dönüş Fonksiyonu
def return_to_main_menu():
    global result_label, remaining_words_label  # result_label ve remaining_words_label'i temizliyoruz

    for widget in root.winfo_children():
        widget.pack_forget()

    # Ana menü arayüzünü yeniden başlatıyoruz
    main_menu()

# Kelimeyi Bir Sonraki Aşamaya Taşıma
def advance_word_to_next_stage(word, current_category):
    if current_category == "Bilmiyorum":
        del category_words["Bilmiyorum"][word]
        category_words["Orta"][word] = 0
    elif current_category == "Orta":
        del category_words["Orta"][word]
        category_words["Ogrendiklerim"][word] = 0

    save_category_data()
    update_category_counts()


# Ana Menü
def main_menu():
    main_menu_frame = tk.Frame(root, bg=COLORS['background'])
    main_menu_frame.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(main_menu_frame, text="İngilizce-Türkçe Kelime Öğrenme", font=("Helvetica", 24), bg=COLORS['background'],
             fg=COLORS['primary']).pack(pady=20)

    # Ana Menü Butonları
    button_info = [
        ("Yeni Kelime Ekle", show_word_with_category_options, COLORS['button_bg']),
        ("Bilmediklerim", lambda: start_category_quiz("Bilmiyorum"), COLORS['wrong']),
        ("Az Bildiklerim", lambda: start_category_quiz("Orta"), COLORS['accent']),
        ("Öğrendiklerim", lambda: start_category_quiz("Ogrendiklerim"), COLORS['correct']),
    ]

    for text, command, color in button_info:
        tk.Button(main_menu_frame, text=text, command=command, font=("Helvetica", 16),
                  bg=color, fg=COLORS['button_fg'], relief="solid", width=25).pack(pady=10)

    # Ayarlar Butonu
    tk.Button(main_menu_frame, text="Ayarlar", command=settings_menu,
              font=("Helvetica", 14), bg=COLORS['accent'], fg=COLORS['button_fg'], relief="solid", width=15).pack(
        pady=10)

    # Çıkış Butonu
    tk.Button(main_menu_frame, text="Çıkış", command=root.quit, font=("Helvetica", 14),
              bg=COLORS['wrong'], fg=COLORS['button_fg'], relief="solid", width=15).pack(pady=10)


# Uygulamanın Başlangıcı
load_category_data()
main_menu()
root.mainloop()
