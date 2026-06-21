# The Love Roulette - Full Narrative & Battle System

# Character declarations with natural colors
define ar = Character("Arthur Pendelton", color="#4A90E2",
    side_image = "images/characters/arthur.png")
define ta = Character("Tabitha Vane", color="#D0021B",
    side_image = "images/characters/tabitha.png")
define kp = Character("Kepala Polisi", color="#9B9B9B",
    side_image = "images/characters/polisi.png")
define mr = Character("Manajer Rumah Sakit", color="#7ED321",
    side_image = "images/characters/manager.png")
define am = Character("Amelia", color="#F5A623",
    side_image = "images/characters/Amelia.png")
define cl = Character("Clara", color="#BD10E0",
    side_image = "images/characters/Clara.png")
define el = Character("Elena", color="#9013FE",
    side_image = "images/characters/Elena.png")
define child = Character("Anak Kecil", color="#FFB6C1",
    side_image = "images/characters/anak.png")

# Fullscreen background definitions
image bg_investigasi = Transform("images/bg_investigasi.jpg", xsize=1920, ysize=1080, fit="cover")
image bg_anak_rumah_sakit = Transform("images/bg_anak_rumah_sakit.jpg", xsize=1920, ysize=1080, fit="cover")
image bg_gosip_rumah_sakit = Transform("images/bg_gosip_rumah_sakit.jpg", xsize=1920, ysize=1080, fit="cover")
image bg_ruang_manager = Transform("images/bg_ruang_manager.jpg", xsize=1920, ysize=1080, fit="cover")
image bg_loker_rumah_sakit = Transform("images/bg_loker_rumah_sakit.jpg", xsize=1920, ysize=1080, fit="cover")
image bg_kantor_polisi = Transform("images/bg_kantor_polisi.jpg", xsize=1920, ysize=1080, fit="cover")
image bg_rumah = Transform("images/bg_rumah.jpg", xsize=1920, ysize=1080, fit="cover")
image bg_berantakan = Transform("images/bg_berantakan.jpg", xsize=1920, ysize=1080, fit="cover")
image bg_ruang_tamu = Transform("images/bg_ruang_tamu.jpg", xsize=1920, ysize=1080, fit="cover")


init python:
    import random

    MAX_ITEM_SLOTS = 3
    ITEM_POOL = ["pil_kebal", "borgol", "serpihan_kaca"]
    ITEM_WEIGHTS = {
        "pil_kebal": 15,
        "serpihan_kaca": 35,
        "borgol": 50,
    }
    ITEM_NAMES = {
        "pil_kebal": "Pil Kebal",
        "borgol": "Borgol",
        "serpihan_kaca": "Serpihan Kaca",
    }

    # Player-controlled character
    player_character = "arthur"

    # Game state
    player_hp = 1
    dealer_hp = 1

    player_shield = False
    dealer_shield = False

    player_handcuffed = False
    dealer_handcuffed = False

    revolver_cylinder = []
    current_bullet_revealed = None

    player_items = []
    dealer_items = []

    battle_message = ""
    turn_owner = "player"
    previous_turn = "dealer"
    reload_cycles = 0
    total_bullets = 0
    shield_blocked = False
    ai_target = "player"
    dealer_item_narration = ""

    def inventory_for(owner):
        return player_items if owner == "player" else dealer_items

    def owner_display_name(owner):
        if player_character == "arthur":
            return "Arthur" if owner == "player" else "Tabitha"
        else:
            return "Tabitha" if owner == "player" else "Arthur"

    def inventory_slot_label(owner, slot_index):
        inventory = inventory_for(owner)
        if slot_index < len(inventory):
            return ITEM_NAMES.get(inventory[slot_index], inventory[slot_index])
        return "Kosong"

    def inventory_slot_item(owner, slot_index):
        inventory = inventory_for(owner)
        if slot_index < len(inventory):
            return inventory[slot_index]
        return None

    def has_item(owner, item_name):
        return item_name in inventory_for(owner)

    def add_item(owner, item_name):
        inventory = inventory_for(owner)
        if len(inventory) >= MAX_ITEM_SLOTS:
            return False
        inventory.append(item_name)
        return True

    def remove_item(owner, item_name):
        inventory = inventory_for(owner)
        if item_name in inventory:
            inventory.remove(item_name)
            return True
        return False

    def draw_item_for(owner):
        if len(inventory_for(owner)) >= MAX_ITEM_SLOTS:
            return None
        item_name = random.choices(ITEM_POOL, weights=[ITEM_WEIGHTS[item] for item in ITEM_POOL], k=1)[0]
        add_item(owner, item_name)
        return item_name

    def populate_revolver():
        global total_bullets
        total_bullets = random.randint(2, 6)
        live_bullets = random.randint(1, total_bullets - 1)
        cylinder = [True] * live_bullets + [False] * (total_bullets - live_bullets)
        random.shuffle(cylinder)
        return cylinder

    def reload_revolver():
        global revolver_cylinder, current_bullet_revealed, reload_cycles
        revolver_cylinder = populate_revolver()
        current_bullet_revealed = None
        reload_cycles += 1

    def bullet_label(value):
        return "Live" if value else "Blank"

    def reveal_current_bullet():
        global current_bullet_revealed, battle_message
        if revolver_cylinder:
            current_bullet_revealed = bullet_label(revolver_cylinder[0])
            battle_message = "Serpihan kaca memperlihatkan isi peluru."
            return current_bullet_revealed
        battle_message = "Silinder kosong, tidak ada peluru untuk diintip."
        return None

    def use_item_by_slot(owner, slot_index):
        """Use item from specific slot index"""
        if slot_index < 0 or slot_index >= MAX_ITEM_SLOTS:
            return False
        item = inventory_slot_item(owner, slot_index)
        if item is None:
            return False
        return use_item(owner, item)

    def use_item(owner, item_name):
        global player_shield, dealer_shield, player_handcuffed, dealer_handcuffed, battle_message

        if item_name is None:
            return False

        if not remove_item(owner, item_name):
            return False

        if item_name == "pil_kebal":
            if owner == "player":
                player_shield = True
            else:
                dealer_shield = True
            battle_message = f"{owner_display_name(owner)} menelan Pil Kebal. Tubuhnya diselimuti cahaya."
        elif item_name == "borgol":
            if owner == "player":
                dealer_handcuffed = True
            else:
                player_handcuffed = True
            battle_message = f"{owner_display_name(owner)} memasang borgol pada lawannya."
        elif item_name == "serpihan_kaca":
            return reveal_current_bullet()
        return True

    def shoot_revolver(shooter, target):
        global player_hp, dealer_hp, player_shield, dealer_shield, current_bullet_revealed, battle_message, shield_blocked

        if not revolver_cylinder:
            reload_revolver()

        bullet_live = revolver_cylinder.pop(0)
        current_bullet_revealed = None
        shield_blocked = False

        shooter_name = owner_display_name(shooter)
        target_name = owner_display_name(target)

        if bullet_live:
            renpy.sound.play("audio/gunshot.mp3")
            if target == "player":
                if player_shield:
                    player_shield = False
                    shield_blocked = True
                    battle_message = f"Live shot! Shield {target_name} hancur, tapi {target_name} selamat."
                else:
                    player_hp = max(0, player_hp - 1)
                    battle_message = f"{shooter_name} menembak {target_name}. Live. {target_name} roboh."
            else:
                if dealer_shield:
                    dealer_shield = False
                    shield_blocked = True
                    battle_message = f"Live shot! Shield {target_name} hancur, tapi {target_name} selamat."
                else:
                    dealer_hp = max(0, dealer_hp - 1)
                    battle_message = f"{shooter_name} menembak {target_name}. Live. {target_name} roboh."
        else:
            if shooter == target:
                battle_message = f"{shooter_name} menembak diri sendiri. Blank. Hanya suara klik."
            else:
                battle_message = f"{shooter_name} menembak {target_name}. Blank."

        if not revolver_cylinder:
            reload_revolver()

        return bullet_live

    def check_end_state():
        if player_hp <= 0 and dealer_hp <= 0:
            return "ending_draw"
        if dealer_hp <= 0:
            return "ending_player_wins"
        if player_hp <= 0:
            return "ending_player_loses"
        if reload_cycles >= 3 and player_hp > 0 and dealer_hp > 0:
            return "ending_draw"
        return None

    def reset_battle_state():
        global player_hp, dealer_hp, player_shield, dealer_shield, player_handcuffed, dealer_handcuffed
        global revolver_cylinder, current_bullet_revealed
        global battle_message, turn_owner, reload_cycles

        player_hp = 1
        dealer_hp = 1

        player_shield = False
        dealer_shield = False

        player_handcuffed = False
        dealer_handcuffed = False

        revolver_cylinder = populate_revolver()
        current_bullet_revealed = None

        battle_message = f"{owner_display_name('player')} dan {owner_display_name('dealer')} saling menatap di bawah ancaman revolver."
        turn_owner = "player"
        reload_cycles = 0

    def dealer_turn_ai():
        global battle_message, ai_target, dealer_item_narration
        dealer_item_narration = ""

        if current_bullet_revealed is None and has_item("dealer", "serpihan_kaca"):
            use_item("dealer", "serpihan_kaca")
            dealer_item_narration = f"{owner_display_name('dealer')} mengintip peluru dengan serpihan kaca."

        known_bullet = current_bullet_revealed
        live_count = sum(1 for bullet in revolver_cylinder if bullet)
        total_count = len(revolver_cylinder)

        if total_count == 0:
            reload_revolver()
            live_count = sum(1 for bullet in revolver_cylinder if bullet)
            total_count = len(revolver_cylinder)
            known_bullet = current_bullet_revealed

        if known_bullet == "Live":
            if has_item("dealer", "borgol") and live_count >= max(3, total_count // 2):
                use_item("dealer", "borgol")
                dealer_item_narration = f"{owner_display_name('dealer')} memasang borgol pada {owner_display_name('player')}."
            elif has_item("dealer", "pil_kebal") and dealer_hp <= 1 and not dealer_shield:
                use_item("dealer", "pil_kebal")
                dealer_item_narration = f"{owner_display_name('dealer')} menelan Pil Kebal."

            ai_target = "player"
            shot_live = shoot_revolver("dealer", "player")
            return shot_live

        if known_bullet == "Blank":
            ai_target = "dealer"
            shot_live = shoot_revolver("dealer", "dealer")
            return shot_live

        live_ratio = float(live_count) / float(total_count) if total_count else 0.0

        if live_ratio >= 0.5:
            if has_item("dealer", "pil_kebal") and dealer_hp <= 1 and not dealer_shield:
                use_item("dealer", "pil_kebal")
                dealer_item_narration = f"{owner_display_name('dealer')} menelan Pil Kebal."
            elif has_item("dealer", "borgol") and live_ratio >= 0.65:
                use_item("dealer", "borgol")
                dealer_item_narration = f"{owner_display_name('dealer')} memasang borgol pada {owner_display_name('player')}."

            ai_target = "player"
            shot_live = shoot_revolver("dealer", "player")
            return shot_live

        ai_target = "dealer"
        shot_live = shoot_revolver("dealer", "dealer")
        return shot_live


screen roulette_table():
    tag battle
    modal True

    add "bg_ruang_tamu"
    frame:
        background "#080406dd"
        xfill True
        yfill True

    add "bg_ruang_tamu":
        alpha 0.08
        blur 20

    frame:
        xalign 0.5 yalign 0.5
        xsize 1340 ysize 940
        background "#0a0a10f0"
        padding (32, 28)

        vbox:
            spacing 22

            text "☦  ROULETTE  ☦" size 52 xalign 0.5 color "#6b0f0f" bold True

            frame:
                xfill True ysize 2 background "#6b0f0f33"

            hbox:
                spacing 40
                xalign 0.5

                frame:
                    xsize 520
                    background "#0c1625e0"
                    padding (24, 18)
                    vbox:
                        spacing 8
                        text f"{owner_display_name('player')}" size 28 color "#4A90E2" bold True
                        text "HP: [player_hp]" size 22 color "#c8c8c8"
                        text "Shield: [\"Aktif ✓\" if player_shield else \"Mati ✗\"]" size 20 color "#c8c8c8"
                        text "Borgol: [\"Terpasang ✓\" if player_handcuffed else \"—\"]" size 20 color "#c8c8c8"
                        text "Item: [len(player_items)] / [MAX_ITEM_SLOTS]" size 20 color "#c8c8c8"

                frame:
                    xsize 520
                    background "#250a0ae0"
                    padding (24, 18)
                    vbox:
                        spacing 8
                        text f"{owner_display_name('dealer')}" size 28 color "#cc1a1a" bold True
                        text "HP: [dealer_hp]" size 22 color "#c8c8c8"
                        text "Shield: [\"Aktif ✓\" if dealer_shield else \"Mati ✗\"]" size 20 color "#c8c8c8"
                        text "Borgol: [\"Terpasang ✓\" if dealer_handcuffed else \"—\"]" size 20 color "#c8c8c8"
                        text "Item: [len(dealer_items)] / [MAX_ITEM_SLOTS]" size 20 color "#c8c8c8"

            frame:
                xfill True
                background "#111116e0"
                padding (20, 14)
                hbox:
                    spacing 40
                    xalign 0.5
                    vbox:
                        spacing 4
                        text "GILIRAN" size 16 color "#555"
                        text "[owner_display_name('player') if turn_owner == 'player' else owner_display_name('dealer')]" size 24 color "#e0e0e0" bold True
                    vbox:
                        spacing 4
                        text "PELURU" size 16 color "#555"
                        text "[sum(1 for b in revolver_cylinder if b)] live / [total_bullets - sum(1 for b in revolver_cylinder if b)] blank" size 24 color "#e0e0e0"
                    vbox:
                        spacing 4
                        text "SISA" size 16 color "#555"
                        text "[len(revolver_cylinder)] dari [total_bullets]" size 24 color "#e0e0e0"

            if battle_message:
                text battle_message size 20 xalign 0.5 color "#bb3030" italic True

            if current_bullet_revealed is not None:
                text "Peluru terintip: [current_bullet_revealed]" size 18 xalign 0.5 color "#666"

            frame:
                xfill True
                background "#0c0c0ce0"
                padding (18, 14)
                vbox:
                    spacing 10
                    text f"INVENTORI" size 18 color "#444" bold True
                    grid 3 1:
                        spacing 10
                        for slot_index in range(MAX_ITEM_SLOTS):
                            $ slot_label = inventory_slot_label("player", slot_index)
                            textbutton slot_label:
                                xsize 180 ysize 60
                                text_size 18
                                text_color "#888"
                                sensitive slot_label != "Kosong"
                                background "#181818"
                                hover_background "#2a1010"
                                selected_background "#2a1010"
                                action Return(("item", slot_index))

            hbox:
                spacing 30
                xalign 0.5

                textbutton "TEMBAK LAWAN":
                    xsize 300 ysize 78
                    text_size 24 text_color "#cc1a1a" text_bold True
                    background "#1a0505"
                    hover_background "#3a0a0a"
                    action Return("shoot_dealer")

                textbutton "TEMBAK DIRI":
                    xsize 200 ysize 60
                    text_size 16 text_color "#555"
                    background "#0d0d0d"
                    hover_background "#1a1a1a"
                    action Return("shoot_self")


label start:
    scene bg_investigasi with fade
    play music "audio/investigasi.mp3" fadein 1.0
    
    "Tempat Kejadian Perkara - Pagi Hari"
    ""
    ar "Pak, saya telah mengumpulkan bukti untuk kasus pembunuhan ini. Ada dua benda yang sangat penting di sini."
    kp "Dua bukti? Tunjukkan aku, Pendelton."
    ar "Bukti pertama: Pisau dengan fingerprint yang jelas. Analisis forensik menunjukkan fingerprint ini berasal dari anggota Mafia Russo. Pisau ini adalah senjata utama dalam pembunuhan korban."
    ""
    "Arthur menunjukkan pisau dengan hati-hati, setiap detail terbaca di matanya."
    ""
    ar "Bukti kedua: Peluru yang ditemukan di TKP. Peluru ini memiliki pahatan unik yang sangat jarang. Hanya Carmine Family yang menggunakan tanda tangan ini pada proyektil mereka. Ini adalah bukti sekunder tapi sangat menarik."
    ""
    "Arthur menunjukkan peluru dengan percaya diri."
    ""
    kp "Dua bukti yang menarik, Pendelton. Mana yang akan kamu pilih untuk laporan resmi? Kedua-duanya memiliki arti penting, tapi biasanya satu bukti yang menjadi fokus utama investigasi."
    ar "Itu keputusan saya, Pak. Mana yang menurut Anda lebih kuat?"
    kp "Keputusan itu ada di tanganmu. Pilih dengan bijak."

    menu:
        "Fokus pada bukti pisau (Fingerprint Russo)":
            ar "Saya memilih untuk melaporkan pisau ini sebagai bukti utama. Fingerprint tidak bisa dibantah. Ini jelas dan langsung menunjukkan siapa yang melakukan pembunuhan."
            $ case_choice = "knife"
        
        "Fokus pada bukti peluru (Pahatan Carmine)":
            ar "Saya akan melaporkan peluru ini sebagai bukti utama. Pahatan unik ini adalah signature Carmine Family. Ini lebih dari sekadar kebetulan."
            $ case_choice = "bullet"

    "Arthur mengumpulkan bukti dan meninggalkan ruangan dengan keputusan yang sudah bulat."
    ""
    ar "Kasusnya akan saya selesaikan dengan benar."

    jump hospital_scene


label hospital_scene:
    scene bg_anak_rumah_sakit with fade
    play music "audio/hospital.mp3" fadein 1.0
    "Rumah Sakit - Waktu yang Sama"
    ""
    "Tabitha sedang merapihkan mainan anak-anak di ruang perawatan pediatrik dengan tangan yang lembut."
    ""
    child "Mbak Tabitha! Mbak Tabitha! Mau main apa?"
    ta "Halo sayang. Gimana kabarmu? Baik-baik saja?"
    child "Baik! Aku bosan. Mau main. Sesuatu yang menyenangkan!"
    ta "Baik baik. Kita punya dua pilihan. Kita bisa merakit puzzle besar, atau membuat origami yang keren. Kamu mau yang mana?"

    menu:
        "Merakit Puzzle":
            child "Puzzle! Puzzle! Suka puzzle!"
            ta "Bagus! Kita rakit puzzle bersama-sama. Ada gambar istana yang indah di dalamnya."
            $ activity_choice = "puzzle"
            "Tabitha dan anak kecil itu duduk bersama, menyusun potongan puzzle dengan sabar. Anak itu tertawa bahagia setiap kali menemukan potongan yang cocok. Tabitha tersenyum tulus melihat kebahagiaan gadis itu."

        "Membuat Origami":
            child "Origami! Origami! Burung yang terbang!"
            ta "Iya, kita buat burung kertas yang cantik. Bisa terbang loh."
            $ activity_choice = "origami"
            "Tabitha melipat kertas dengan hati-hati, mengajari anak kecil itu cara membuat sayap. Akhirnya mereka ciptakan burung origami yang cantik. Anak itu berlari-lari di sekitar ruangan, membuat burung itu 'terbang'."

    ta "Lihat? Kamu sudah bisa bikin mainanmu sendiri. Kamu sangat hebat."
    child "Mbak Tabitha baik. Mbak Tabitha sayang sama aku."
    ta "Iya sayang. Aku sayang sama kamu. Jangan pernah lupa itu, ya?"

    jump gossip_scene


label gossip_scene:
    scene bg_gosip_rumah_sakit with fade
    play music "audio/gossip.mp3" fadein 1.0
    "Rumah Sakit - Kamar Istirahat - Sore Hari"
    ""
    "Tiga perawat, Amelia, Clara, dan Elena, berkumpul di ruang istirahat sambil membuat kopi."
    ""
    am "Duh, lihat Tabitha tadi? Segala sesuatu dia selesaikan sendiri, seolah-olah kita semua tidak berguna."
    cl "Iya! Dia kasar sekali kalau bicara. Pas aku minta bantuan kemarin, dia malah bentakin aku."
    el "Kalian tau ngga? Dia kalo main bareng anak-anak kelihatannya baik banget, tapi kalo di belakang jahat sebenernya."
    am "Exactly! Sepertinya dia punya dua wajah."
    cl "Kita harus laporin dia ke manager. Kelakuannya benar-benar sering ganggu."
    el "Iya setuju. Manager perlu tahu bahwa Tabitha ini toxic untuk tim kita."

    "Ketiga wanita itu tersenyum jahat, merencanakan bagaimana cara melapor dengan paling efektif."

    jump manager_office_scene


label manager_office_scene:
    scene bg_ruang_manager with fade
    "Ruang Manager Rumah Sakit - Sore Hari"
    ""
    mr "..."
    ""
    "Manajer Rumah Sakit duduk di meja kerjanya, mengeluh dalam hati tentang pekerjaan yang menumpuk. Berkas-berkas bertumpuk di meja, jadwal shift yang berantakan, dan keluhan dari berbagai departemen."
    ""
    mr "Tuhan... kenapa banyak banget masalah di hari ini? Kerjanya pada gimana sih?"

    "Pintu terbuka. Amelia, Clara, dan Elena masuk dengan ekspresi yang serius dan berpura-pura khawatir."
    ""
    am "Manager, bisa kami bicara sebentar?"
    mr "Apa lagi? Cepatlah, aku punya banyak pekerjaan."
    cl "Ini tentang Tabitha Vane. Kami ingin melaporkan tentang perilakunya yang tidak layak."
    el "Dia sangat kasar terhadap kami. Dia memperlakukan kami dengan tidak hormat."
    mr "Kasar? Berapa banyak orang yang sudah melapor?"
    am "Kami bertiga. Dan kami yakin ada juga orang lain yang merasa hal yang sama."
    mr "Baiklah... baiklah. Ini adalah laporan resmi. Terima kasih atas informasinya."

    "Ketiga wanita itu pergi dengan senyuman yang puas, sementara manager menghela napas berat."

    jump firing_scene


label firing_scene:
    scene bg_anak_rumah_sakit with fade
    "Ruang Perawatan - Setelah Tabitha Selesai Bermain dengan Anak"
    ""
    "Tabitha sedang merapihkan mainan terakhir ketika manager datang dengan wajah serius."
    ""
    mr "Tabitha, kita perlu bicara. Sekarang."
    ta "Ada apa, Manager? Apa ada masalah?"
    mr "Masalah? Iya, ada. Ada tiga laporan masuk tentang perilakumu yang tidak profesional. Banyak yang mengatakan kamu kasar dan tidak menghormati rekan kerja."
    ta "Apa? Itu tidak benar. Siapa yang bilang? Aku tidak pernah kasar kepada siapa pun."
    mr "Kamu menolak laporan ini? Mereka bertiga sudah datang dan melaporkan hal yang sama. Kamu pikir mereka semua bohong?"
    ta "Tidak, aku hanya... mereka mengada-ada. Aku tidak pernah melakukan apa yang mereka katakan!"
    mr "Kamu terus denial, Tabitha. Lihat, hari ini saja aku sudah kelelahan mendengarkan komplen. Dan sekarang kamu menambah masalah. Aku tidak punya energi untuk ini."
    mr "Cukup! Cukup! Aku tidak mau mendengar alibi lagi. Banyak laporan masuk ke saya. Kamu ngeraguin saya? Cukup bekerja sesuai aturan atau pergi. Ambil barangmu dan keluar dari sini sebelum aku memutuskan untuk mem-PHK mu sekarang juga!"

    ta "Ini tidak adil..."
    mr "Adil? Adil itu ketika tim bisa bekerja tanpa ketakutan dengan rekan kerja mereka. Sekarang pergi."

    "Tabitha terdiam. Emosi campur aduk. Dia merasa difitnah, direndahkan, dan tidak dihargai."

    jump tabitha_leaving_hospital


label tabitha_leaving_hospital:
    scene bg_loker_rumah_sakit with fade
    stop music fadeout 2.0
    "Tabitha berjalan ke loker untuk mengambil barang pribadi. Tangan nya gemetar karena kemarahan."
    ta "Aku tidak layak mendapat perlakuan ini... Mereka bohong. Semua bohong!"
    "Dia mengemas tasnya dengan kasar, menutup loker dengan pukulan ringan."
    ta "Aku akan pergi dari rumah sakit ini. Aku memberikan yang terbaik pun orang tidak bisa menghargai perbuatanku."

    "Tabitha berjalan keluar dari rumah sakit dengan wajah kesal dan penuh amarah. Rasa dendam dan kecewa muncul di hati Tabitha."

    jump arthur_police_station


label arthur_police_station:
    scene bg_kantor_polisi with fade
    play music "audio/police.mp3" fadein 1.0
    "Kantor Polisi - Hari Berikutnya - Siang Hari"
    ""
    "Arthur datang untuk menanyakan hasil penyelidikan kasusnya. Dia masuk ke ruang kepala polisi dengan kepercayaan diri."
    ""
    ar "Pak, saya ingin mengetahui perkembangan kasus pembunuhan itu. Gimana kelanjutannya?"
    kp "Pendelton... duduk."
    ar "Ada apa? Mereka sudah ditangkap?"
    kp "Tidak. Mereka tidak akan ditangkap. Kasus ini ditutup."
    ar "Ditutup? Bagaimana bisa? Ada bukti! Ada jenazah! Ada hukum!"
    kp "Ya, semua bukti memang sudah jelas. Tapi mereka adalah donatur utama bagi kami. Kamu tahu kan gaji kami hanya cukup untuk kebutuhan sehari-hari?. Jika kasus ini dilanjutkan itu akan berbahaya bagi instansi kedepannya."
    ar "Jadi Anda bilang kasus pembunuhan ini bisa ditutup dengan uang? Seperti ini ya ternyata kepolisian sekarang."
    kp "Pendelton... dunia ini tidak selamanya hitam putih."
    ar "Tidak. Ini hitam putih. Pembunuh harus dipenjara. Titik. Tidak ada alasan yang bisa menutup kasus ini."
    kp "Kamu terus memperdebatkan ini tanpa mengerti situasi politis. Aku tidak butuh detektif yang tidak bisa bekerja dalam sistem. Taruh seragam kamu di mejaku. Kamu dipecat. Selesai."

    "Arthur terdiam sejenak, kemudian tiba-tiba berdiri dan meneriaki seluruh kantor."
    ""
    ar "Kalian semua busuk! Korup! Tidak pantas menjadi penjaga hukum! Kalian semua PEMBUNUH!"

    "Arthur meninggalkan kantor dengan marah, ia pun membanting pintu keras-keras."

    jump tabitha_arrives_home


label tabitha_arrives_home:
    scene bg_rumah with fade
    play music "audio/destruction.mp3" fadein 1.0
    "Rumah Arthur dan Tabitha - Malam Hari"
    ""
    "Tabitha tiba di rumah duluan. Dia berjalan ke depan rumah dengan pikiran yang berantakan akibat dari pengalaman di rumah sakit."
    ""
    ta "Akhirnya pulang. Rumah adalah satu-satunya tempat yang tidak pernah berkhianat."
    ""
    "Tiba-tiba matanya melihat sesuatu yang mengejutkan. Kotoran anjing bertebaran di depan rumah. Dan di jendela..."
    ""
    ta "..."
    ""
    "Di jendela ada tulisan besar: 'GO KILL YOURSELF'"
    ""
    ta "Tidak... tidak mungkin..."
    ""
    "Tabitha merasa semua emosi meledak sekaligus. Pengkhianatan di rumah sakit, pengasingan, ketidakadilan... dan sekarang ini. Karena mereka. Amelia, Clara, Elena."
    ""
    ta "MEREKA!!! PASTI MEREKA YANG LAKUKAN INI SEMUA!!!"

    "Tabitha berlari masuk ke rumah dengan amarah yang tidak terkontrol."

    jump house_destruction


label house_destruction:
    scene bg_berantakan with fade
    "Dalam Rumah"
    ""
    "Tabitha mulai merusak barang-barang di rumah. Gelas pecah, bantal dilempar, meja terbalik. Emosi yang terpendam selama berbulan-bulan meledak dalam sekejap."
    ""
    ta "Semuanya! Semua orang jahat! Semua orang bohong! Aku tidak pantas hidup di dunia seperti ini!"
    ""
    "Dia jatuh di lantai di tengah kehancuran, menangis dengan marah dan frustrasi."

    jump arthur_arrives_home


label arthur_arrives_home:
    scene bg_rumah with fade
    "Sekitar 5 menit kemudian, Arthur tiba di rumah. Dia menyadari ada sesuatu yang janggal ketika melihat pintu terbuka dan banyak kotoran anjing di depan jendela."
    ""
    ar "Apa yang...?"
    ""
    "Arthur berlari masuk dan melihat rumah yang berantakan."
    ""
    ar "Tabitha! Apa yang terjadi?! Kenapa seisi rumah berantakan?!"
    ta "..."
    ""
    "Tabitha masih duduk di lantai, melihat Arthur dengan mata yang penuh dendam dan kecewa."
    ""
    ar "Jawab aku! Ada kotoran di depan, jendela dicorat-coret, dan sekarang rumah ancur! APA YANG TERJADI?!"
    ta "Dunia ini isinya orang-orang jahat! Mereka fitnah aku! Mereka mengotori rumah kita!"
    ar "BUKAN CUMAN KAMU YANG BISA MARAH-MARAH AKU BARU SAJA DIPECAT KARENA AKU MENCOBA MELAKUKAN YANG BENAR! Lalu aku pulang dan melihat ini! Semuanya hancur!"
    ta "Semuanya memang seharusnya hancur! Dunia ini tidak layak untuk dipertahankan!"
    ar "Aku tahu dunia itu kasar! Tapi kita harus bertahan, Tabitha!"
    ta "Bertahan? UNTUK APA?! Untuk apa bertahan jika semua orang akan mengkhianati kita?!"
    ""
    "Mereka saling berteriak. Debat yang tidak ada akhir tentang dunia yang kejam dan hati yang rusak."

    jump roulette_proposal


label roulette_proposal:
    scene bg_ruang_tamu with fade
    play music "audio/roulette.mp3" fadein 1.0
    "Berjam-jam mereka saling berteriak. Menyalahkan. Hancur."
    ""
    "Sekarang, hanya ada kelelahan yang terjadi diantara mereka berdua."
    ""
    ar "Kita tidak bisa lanjut seperti ini."
    ta "Aku tahu."
    ""
    "Dunia mendadak sunyi. Hanya jam dinding yang berdetak dan suara angin yang berhembus di luar yang terdengar. Mereka saling menatap, mencari jawaban satu sama lain."
    ""
    ar "Setiap hari dunia ini semakin sakit. Setiap hari sama saja."
    ta "Iya."
    ar "Mungkin kita perlu cara lain untuk mengakhiri ini. Cara yang jujur. Cara yang final."
    ta "Apa maksudmu?"
    ""
    "Arthur menatap Tabitha. Bukan dengan cinta. Bukan dengan benci. Tapi dengan sesuatu yang jauh lebih gelap..."
    ""
    ar "Roulette."
    ""
    "Kata itu bergema di kepala mereka. Berat. Tidak bisa ditarik kembali."
    ""
    ta "..."
    ta "Baik."
    ""
    "Mereka berjalan ke lemari tua di sudut ruangan. Dari dalam, Arthur mengeluarkan sebuah revolver perak yang sudah lama disimpan."
    "Revolver yang sudah mereka simpan sejak lama."
    ""
    "Sebuah keputusan yang final. Sebuah permainan yang tidak ada pemenang."

    jump character_selection


label character_selection:
    scene bg_ruang_tamu with fade
    "Di tengah ruangan yang berantakan, di antara pecahan kaca dan isi ruangan yang hancur, mereka berdiri saling berhadapan."
    "Revolver di tangan. Takdir di ujung laras."
    ""
    "Satu pertanyaan terakhir. Satu keputusan yang akan menentukan segalanya."
    ""
    "Siapa yang akan memegang kendali?"
    "Siapa yang akan menarik pelatuk pertama?"
    "Dan siapa yang akan menjadi korban di malam ini?"
    ""

    menu:
        "Arthur Pendelton — Detektif":
            $ player_character = "arthur"
            "Arthur menarik nafas dalam-dalam. Tatapannya kosong."
            ar "Baik. Aku yang mulai."
        
        "Tabitha Vane — Perawat":
            $ player_character = "tabitha"
            "Tabitha mengambil revolver. Jari-jarinya melingkar dengan ekspresi yang datar."
            ta "Baik. Aku yang mulai."

    "Permainan paling kelam dalam hidup mereka akan segera dimulai."

    jump secret_chest_preparation


label secret_chest_preparation:
    scene bg_ruang_tamu with fade
    "Arthur membuka sebuah peti kayu tua di sudut ruangan. Engselnya berderit, seperti suara terakhir seseorang sebelum mati."
    ""
    "Di dalamnya, ada kotak misterius tersusun rapi. Berisi benda yang bisa menjadi penolong—atau penunda kematian."
    ""
    $ player_items = []
    $ dealer_items = []
    if player_character == "arthur":
        ar "Dua item. Masing-masing dari kita ambil dua."
        "Suara Arthur datar. Seperti sedang membicarakan daftar belanja, bukan perlengkapan untuk permainan maut."
        ta "Kau duluan."
    else:
        ta "Dua item. Masing-masing dari kita ambil dua."
        "Suara Tabitha tenang. Terlalu tenang."
        ar "Kau duluan."

    "Mari kita lihat apa yang ada di dalam peti ini..."

    jump player_draws_items


label player_draws_items:
    if player_character == "arthur":
        "Arthur memasukkan tangannya ke dalam peti. Jari-jarinya meraba-raba di antara benda-benda dingin."
        ""
        $ item1 = draw_item_for("player")
        if item1 is not None:
            "Dia menarik satu benda. [ITEM_NAMES[item1]]. Berguna. Atau setidaknya, lebih baik daripada tidak sama sekali."
        else:
            "Peti itu kosong. Tidak ada yang tersisa."
        ""
        "Satu lagi."
        $ item2 = draw_item_for("player")
        if item2 is not None:
            "Dia mengambil yang kedua. [ITEM_NAMES[item2]]."
        else:
            "Tidak ada lagi."
        ""
        jump dealer_draws_items
    else:
        "Tabitha merogoh peti. Tangannya tidak ragu-ragu."
        ""
        $ item1 = draw_item_for("player")
        if item1 is not None:
            "Benda pertama. [ITEM_NAMES[item1]]. Senyum tipis mengembang di wajahnya."
        else:
            "Peti itu kosong."
        ""
        "Satu lagi."
        $ item2 = draw_item_for("player")
        if item2 is not None:
            "[ITEM_NAMES[item2]]. Cukup untuk bertahan."
        else:
            "Tidak ada."
        ""
        jump dealer_draws_items


label dealer_draws_items:
    if player_character == "arthur":
        ta "Giliranku."
        "Tabitha merogoh peti dengan gerakan yang anggun—tapi mengancam."
        ""
        $ item3 = draw_item_for("dealer")
        if item3 is not None:
            ta "[ITEM_NAMES[item3]]. Kau pasti suka kalau aku pakai ini nanti."
        else:
            ta "Habis."
        ta "Dan satu lagi."
        $ item4 = draw_item_for("dealer")
        if item4 is not None:
            ta "[ITEM_NAMES[item4]]."
        else:
            ta "Tidak ada lagi."
    else:
        ar "Giliranku."
        "Arthur mengambil alih peti."
        ""
        $ item3 = draw_item_for("dealer")
        if item3 is not None:
            ar "[ITEM_NAMES[item3]]. Ini cukup untuk membuatmu berpikir dua kali."
        else:
            ar "Habis."
        ar "Satu lagi."
        $ item4 = draw_item_for("dealer")
        if item4 is not None:
            ar "[ITEM_NAMES[item4]]."
        else:
            ar "Tidak ada lagi."

    jump revolver_loading


label revolver_loading:
    scene bg_ruang_tamu with fade
    if player_character == "arthur":
        "Arthur mengambil revolver. Silindernya terbuka dengan bunyi klik yang tajam."
        ""
        $ reset_battle_state()
        $ turn_owner = "player"
        $ previous_turn = "dealer"
        "Dia memasukkan peluru satu per satu. [total_bullets] butir. [sum(1 for b in revolver_cylinder if b)] di antaranya hidup. [total_bullets - sum(1 for b in revolver_cylinder if b)] kosong."
        "Silinder berputar. Nasib acak yang tidak bisa diprediksi."
        ""
        ar "Kau mulai."
    else:
        "Tabitha memutar silinder revolver. Jari-jarinya bergerak dengan keahlian yang mengganggu."
        ""
        $ reset_battle_state()
        $ turn_owner = "player"
        $ previous_turn = "dealer"
        "Dia memasukkan peluru. [total_bullets] butir. [sum(1 for b in revolver_cylinder if b)] hidup. [total_bullets - sum(1 for b in revolver_cylinder if b)] kosong."
        "Silinder berputar. Roda roulette tanpa ampun."
        ""
        ta "Kau mulai."

    jump battle_turn


label battle_turn:
    $ pending_ending = check_end_state()
    if pending_ending:
        jump expression pending_ending

    if turn_owner == "player":
        if player_handcuffed:
            $ player_handcuffed = False
            $ battle_message = f"{owner_display_name('player')} kehilangan giliran karena borgol."
            $ turn_owner = "dealer"
            jump battle_turn

        if previous_turn == "dealer":
            $ previous_turn = "player"
            scene bg black with fade
            if player_character == "arthur":
                "Arthur memegang revolver lagi."
            else:
                "Revolver kembali ke tangan Tabitha."

        call screen roulette_table
        $ player_choice = _return

        if isinstance(player_choice, tuple) and player_choice[0] == "item":
            $ slot_index = player_choice[1]
            $ use_item_by_slot("player", slot_index)
            jump battle_turn

        elif player_choice == "shoot_dealer":
            $ shot_live = shoot_revolver("player", "dealer")
            $ turn_owner = "dealer"
            jump player_to_dealer_transition

        elif player_choice == "shoot_self":
            $ shot_live = shoot_revolver("player", "player")
            if not shot_live:
                $ turn_owner = "player"
            else:
                if player_hp <= 0:
                    jump ending_player_self_shot
                elif shield_blocked:
                    $ turn_owner = "dealer"
                    $ previous_turn = "player"
                    jump shield_saved_self_shot
                else:
                    $ turn_owner = "dealer"
                    $ previous_turn = "player"
                    jump player_to_dealer_transition

        jump battle_turn

    # Dealer's turn
    $ dealer_handcuff_skip = dealer_handcuffed
    if dealer_handcuff_skip:
        $ dealer_handcuffed = False
        $ battle_message = f"{owner_display_name('dealer')} kehilangan giliran karena borgol."
        $ turn_owner = "player"
        jump battle_turn

    if previous_turn == "player":
        $ previous_turn = "dealer"
        scene bg black with fade
        if player_character == "arthur":
            "Arthur menyerahkan revolver. Tabitha mengambilnya."
        else:
            "Revolver berpindah ke tangan Arthur."

    call dealer_turn_scene
    jump battle_turn


label player_to_dealer_transition:
    scene bg black with fade
    $ previous_turn = "dealer"
    if player_character == "arthur":
        "Arthur meletakkan revolver."
    else:
        "Tabitha menyerahkan revolver."
    
    jump battle_turn


label dealer_turn_scene:
    scene bg black with fade
    
    if player_character == "arthur":
        ta "Giliranku, Arthur."
    else:
        ar "Giliranku, Tabitha."

    $ shot_live = dealer_turn_ai()
    if dealer_item_narration:
        "[dealer_item_narration]"
    "[battle_message]"
    
    if shot_live:
        $ turn_owner = "player"
    elif ai_target == "player":
        $ turn_owner = "player"
    else:
        $ turn_owner = "dealer"
    
    return


label ending_player_wins:
    scene bg black with fade
    
    if player_character == "arthur":
        "Tabitha jatuh. Darah menggenang di lantai."
        jump ending_tabitha_dies
    else:
        "Arthur jatuh. Darah menggenang di lantai."
        jump ending_arthur_dies


label ending_player_loses:
    scene bg black with fade
    
    if player_character == "arthur":
        "Arthur jatuh. Darah menggenang di lantai."
        jump ending_arthur_dies
    else:
        "Tabitha jatuh. Darah menggenang di lantai."
        jump ending_tabitha_dies


label ending_player_self_shot:
    scene bg black with fade
    
    if player_character == "arthur":
        "Arthur menekan laras ke pelipisnya."
        "BANG."
        "Tubuhnya roboh."
        jump ending_arthur_dies
    else:
        "Tabitha menekan laras ke pelipisnya."
        "BANG."
        "Tubuhnya roboh."
        jump ending_tabitha_dies


label shield_saved_self_shot:
    scene bg black with fade
    
    if player_character == "arthur":
        "Arthur mengarahkan revolver ke pelipisnya."
        "BANG!"
        "Shield-nya menyala. Peluru berhenti."
        ta "Arthur!"
        ta "Kau masih hidup."
        ta "Giliranku."
    else:
        "Tabitha mengarahkan revolver ke pelipisnya."
        "BANG!"
        "Shield-nya menyala. Peluru berhenti."
        ar "Tabitha!"
        ar "Kau baik-baik saja?"
        ar "Giliranku."
    
    $ turn_owner = "dealer"
    jump player_to_dealer_transition


label ending_arthur_dies:
    "Arthur—satu-satunya manusia yang pernah masuk ke dalam hidup Tabitha—telah pergi."
    "..."
    "Tabitha memandang tangannya. Darah masih hangat."
    "Ia tidak menangis. Dunia sudah mengajarinya bahwa air mata tidak pernah menolong siapa pun."
    "..."
    "Dia berjalan keluar dari rumah."
    "Malam ini, tiga orang akan mati."
    "Amelia, Clara, Elena."
    "Masing-masing dengan cara yang berbeda."
    "..."
    "Dunia akan menjadi saksi."
    scene black with fade
    jump ending_credits


label ending_tabitha_dies:
    "Tabitha—satu-satunya yang berhasil menembus tembok dingin Arthur—telah pergi."
    "..."
    "Arthur duduk di sampingnya. Diam."
    "Sepanjang hidupnya, tidak ada yang pernah benar-benar berarti."
    "Tabitha adalah satu-satunya."
    "Dan sekarang ia pergi."
    "..."
    "Diam-diam, Arthur mengambil revolver."
    "BANG."
    scene black with fade
    jump ending_credits


label ending_draw:
    scene bg black with fade
    
    if player_character == "arthur":
        ar "Kehabisan peluru."
        ta "Kehabisan peluru."
    else:
        ta "Kehabisan peluru."
        ar "Kehabisan peluru."
    
    "..."
    "Mereka saling memandang. Marah. Frustrasi."
    "Tidak ada yang menang. Tidak ada yang kalah."
    "..."
    "Mereka mengambil revolver lain. Mengisi penuh amunisi."
    "Menodongkan ke satu sama lain."
    "..."
    if player_character == "arthur":
        ar "Bersamaan?"
        ta "Bersamaan."
    else:
        ta "Bersamaan?"
        ar "Bersamaan."
    "Dua pelatuk ditarik."
    scene black with fade
    jump ending_credits


label ending_credits:
    stop music fadeout 2.0
    $ renpy.pause(1.0)
    play music "audio/ending.mp3" fadein 1.0
    scene black
    $ renpy.pause(0.5)
    show screen ending_text("THE END")
    $ renpy.pause(3.0, hard=True)
    hide screen ending_text
    $ renpy.pause(0.5)
    show screen ending_text("A Game by Hazwan Adhikara Nasution")
    $ renpy.pause(4.0, hard=True)
    hide screen ending_text
    stop music fadeout 2.0
    return

screen ending_text(msg):
    text msg:
        color "#FFFFFF"
        size 60
        xalign 0.5
        yalign 0.5
