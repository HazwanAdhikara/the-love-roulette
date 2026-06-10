# The Love Roulette - Full Narrative & Battle System

# Character declarations with natural colors
define ar = Character("Arthur Pendelton", color="#4A90E2")
define ta = Character("Tabitha Vane", color="#D0021B")
define kp = Character("Kepala Polisi", color="#9B9B9B")
define mr = Character("Manajer Rumah Sakit", color="#7ED321")
define am = Character("Amelia", color="#F5A623")
define cl = Character("Clara", color="#BD10E0")
define el = Character("Elena", color="#9013FE")
define child = Character("Anak Kecil", color="#FFB6C1")


init python:
    import random

    MAX_ITEM_SLOTS = 3
    ITEM_POOL = ["pil_kebal", "borgol", "serpihan_kaca"]
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
    reload_cycles = 0
    total_bullets = 0

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
        item_name = random.choice(ITEM_POOL)
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
            battle_message = "Serpihan kaca mengintip isi ruang peluru."
            renpy.restart_interaction()
            return current_bullet_revealed
        battle_message = "Silinder kosong, tidak ada peluru untuk diintip."
        renpy.restart_interaction()
        return None

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
            battle_message = f"{owner_display_name(owner)} menelan Pil Kebal. Tubuhnya bersinar dengan perlindungan aneh."
        elif item_name == "borgol":
            if owner == "player":
                dealer_handcuffed = True
            else:
                player_handcuffed = True
            battle_message = f"{owner_display_name(owner)} memasang borgol pada lawannya dengan tawa sadis."
        elif item_name == "serpihan_kaca":
            return reveal_current_bullet()

        draw_item_for(owner)
        renpy.restart_interaction()
        return True

    def shoot_revolver(shooter, target):
        global player_hp, dealer_hp, player_shield, dealer_shield, current_bullet_revealed, battle_message

        if not revolver_cylinder:
            reload_revolver()

        bullet_live = revolver_cylinder.pop(0)
        current_bullet_revealed = None

        shooter_name = owner_display_name(shooter)
        target_name = owner_display_name(target)

        if bullet_live:
            if target == "player":
                if player_shield:
                    player_shield = False
                    battle_message = f"Peluru Live menghantam perlindungan. Shield {target_name} pecah dengan suara kaca."
                else:
                    player_hp = max(0, player_hp - 1)
                    battle_message = f"{shooter_name} menarik pelatuk. Pelurunya melaju. {target_name} terjatuh."
            else:
                if dealer_shield:
                    dealer_shield = False
                    battle_message = f"Peluru Live menghantam perlindungan. Shield {target_name} pecah dengan suara kaca."
                else:
                    dealer_hp = max(0, dealer_hp - 1)
                    battle_message = f"{shooter_name} menarik pelatuk. Pelurunya melaju. {target_name} terjatuh."
        else:
            if shooter == target:
                battle_message = f"{shooter_name} menempatkan revolver ke pelipis. Klik. Pelurunya kosong. Ia tersenyum gila."
            else:
                battle_message = f"{shooter_name} menembak {target_name}. Klik. Pelurunya kosong."

        draw_item_for(shooter)

        if not revolver_cylinder:
            reload_revolver()

        renpy.restart_interaction()
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
        global revolver_cylinder, current_bullet_revealed, player_items, dealer_items
        global battle_message, turn_owner, reload_cycles

        player_hp = 1
        dealer_hp = 1

        player_shield = False
        dealer_shield = False

        player_handcuffed = False
        dealer_handcuffed = False

        revolver_cylinder = populate_revolver()
        current_bullet_revealed = None

        player_items = []
        dealer_items = []

        battle_message = f"{owner_display_name('player')} dan {owner_display_name('dealer')} saling menatap di bawah ancaman revolver."
        turn_owner = "player"
        reload_cycles = 0

    def dealer_turn_ai():
        global battle_message
        action_note = ""

        if current_bullet_revealed is None and has_item("dealer", "serpihan_kaca"):
            use_item("dealer", "serpihan_kaca")
            action_note = f"{owner_display_name('dealer')} mengintip isi silinder dengan serpihan kaca."

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
                action_note = f"{owner_display_name('dealer')} memasang borgol sebelum menembak."
            elif has_item("dealer", "pil_kebal") and dealer_hp <= 1 and not dealer_shield:
                use_item("dealer", "pil_kebal")
                action_note = f"{owner_display_name('dealer')} menelan Pil Kebal untuk berjaga."

            shot_live = shoot_revolver("dealer", "player")
            if action_note:
                battle_message = f"{action_note} {battle_message}"
                renpy.restart_interaction()
            return shot_live

        if known_bullet == "Blank":
            shot_live = shoot_revolver("dealer", "dealer")
            if action_note:
                battle_message = f"{action_note} {battle_message}"
                renpy.restart_interaction()
            return shot_live

        live_ratio = float(live_count) / float(total_count) if total_count else 0.0

        if live_ratio >= 0.5:
            if has_item("dealer", "pil_kebal") and dealer_hp <= 1 and not dealer_shield:
                use_item("dealer", "pil_kebal")
                action_note = f"{owner_display_name('dealer')} menelan Pil Kebal. Situasi terlalu genting."
            elif has_item("dealer", "borgol") and live_ratio >= 0.65:
                use_item("dealer", "borgol")
                action_note = f"{owner_display_name('dealer')} memasang borgol untuk menekan {owner_display_name('player')}."

            shot_live = shoot_revolver("dealer", "player")
            if action_note:
                battle_message = f"{action_note} {battle_message}"
                renpy.restart_interaction()
            return shot_live

        shot_live = shoot_revolver("dealer", "dealer")
        if action_note:
            battle_message = f"{action_note} {battle_message}"
            renpy.restart_interaction()
        return shot_live


screen roulette_table():
    tag battle
    modal True

    frame:
        xalign 0.5
        yalign 0.5
        xsize 1280
        ysize 720
        background "#0f121acc"
        padding (36, 30)

        vbox:
            spacing 22

            text "THE LOVE ROULETTE" size 44 xalign 0.5 color "#F5F5F5"

            hbox:
                spacing 28
                xalign 0.5

                frame:
                    xsize 500
                    background "#13233bcc"
                    padding (22, 18)

                    vbox:
                        spacing 8
                        text f"{owner_display_name('player')}" size 30 color "#4A90E2"
                        text "HP: [player_hp]" size 26 color "#F0F0F0"
                        text "Shield: [\"Aktif\" if player_shield else \"Mati\"]" size 22 color "#F0F0F0"
                        text "Borgol: [\"Terpasang\" if player_handcuffed else \"Tidak\"]" size 22 color "#F0F0F0"
                        text "Item: [len(player_items)] / [MAX_ITEM_SLOTS]" size 22 color "#F0F0F0"

                frame:
                    xsize 500
                    background "#3b1115cc"
                    padding (22, 18)

                    vbox:
                        spacing 8
                        text f"{owner_display_name('dealer')}" size 30 color "#D0021B"
                        text "HP: [dealer_hp]" size 26 color "#F0F0F0"
                        text "Shield: [\"Aktif\" if dealer_shield else \"Mati\"]" size 22 color "#F0F0F0"
                        text "Borgol: [\"Terpasang\" if dealer_handcuffed else \"Tidak\"]" size 22 color "#F0F0F0"
                        text "Item: [len(dealer_items)] / [MAX_ITEM_SLOTS]" size 22 color "#F0F0F0"

            hbox:
                spacing 28
                xalign 0.5

                frame:
                    xsize 600
                    background "#1a1f27cc"
                    padding (20, 18)

                    vbox:
                        spacing 10
                        text "Status Duel" size 24 color "#F5F5F5"
                        text "Giliran: [owner_display_name('player') if turn_owner == 'player' else owner_display_name('dealer')]" size 22 color "#F5F5F5"
                        text "Peluru terintip: [current_bullet_revealed if current_bullet_revealed is not None else 'Belum diketahui']" size 22 color "#F5F5F5"
                        text "Peluru tersisa: [len(revolver_cylinder)] dari [total_bullets]" size 22 color "#F5F5F5"
                        text battle_message size 20 color "#F5F5F5"

                frame:
                    xsize 600
                    background "#151515cc"
                    padding (20, 18)

                    vbox:
                        spacing 12
                        text f"Inventori {owner_display_name('player')}" size 24 color "#F5F5F5"
                        grid 3 1:
                            spacing 10
                            for slot_index in range(MAX_ITEM_SLOTS):
                                $ slot_label = inventory_slot_label("player", slot_index)
                                textbutton slot_label:
                                    xsize 170
                                    ysize 62
                                    sensitive slot_label != "Kosong"
                                    action Function(use_item, "player", inventory_slot_item("player", slot_index))

            hbox:
                spacing 18
                xalign 0.5

                textbutton "Tembak Lawan":
                    xsize 240
                    ysize 70
                    text_size 24
                    action Return("shoot_dealer")

                textbutton "Tembak Diri Sendiri":
                    xsize 240
                    ysize 70
                    text_size 24
                    action Return("shoot_self")


label start:
    scene bg black with fade
    
    "Tempat Kejadian Perkara - Pagi Hari"
    ""
    ar "Sir, saya telah mengumpulkan bukti untuk kasus pembunuhan ini. Ada dua benda yang sangat penting di sini."
    ""
    kp "Dua bukti? Tunjukkan aku, Pendelton."
    ""
    ar "Bukti pertama: Pisau dengan fingerprint yang jelas. Analisis forensik menunjukkan fingerprint ini berasal dari anggota Mafia Russo. Pisau ini adalah senjata utama dalam pembunuhan korban."
    ""
    "Arthur menunjukkan pisau dengan hati-hati, setiap detail terbaca di matanya."
    ""
    ar "Bukti kedua: Peluru yang ditemukan di TKP. Peluru ini memiliki pahatan unik yang sangat jarang. Hanya Carmine Family yang menggunakan tanda tangan ini pada proyektil mereka. Ini adalah bukti sekunder tapi sangat menarik."
    ""
    "Arthur menunjukkan peluru dengan percaya diri."
    ""
    kp "Dua bukti yang menarik, Pendelton. Mana yang akan kamu pilih untuk laporan resmi? Kedua-duanya memiliki arti penting, tapi biasanya satu bukti yang menjadi fokus utama investigasi."
    ""
    ar "Itu keputusan saya, Sir. Mana yang menurut Anda lebih kuat?"
    ""
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
    scene bg black with fade
    
    "Rumah Sakit - Waktu yang Sama"
    ""
    "Tabitha sedang merapihkan mainan anak-anak di ruang perawatan pediatrik dengan tangan yang lembut."
    ""
    child "Mbak Tabitha! Mbak Tabitha! Mau main apa?"
    ""
    ta "Halo sayang. Gimana kabarmu? Baik-baik saja?"
    ""
    child "Baik! Aku bosan. Mau main. Sesuatu yang menyenangkan!"
    ""
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
    ""
    child "Mbak Tabitha baik. Mbak Tabitha sayang sama aku."
    ""
    ta "Iya sayang. Aku sayang sama kamu. Jangan pernah lupa itu, ya?"

    jump gossip_scene


label gossip_scene:
    scene bg black with fade
    
    "Rumah Sakit - Kamar Istirahat - Sore Hari"
    ""
    "Tiga perawat, Amelia, Clara, dan Elena, berkumpul di kamar istirahat sambil membuat kopi."
    ""
    am "Duh, lihat Tabitha tadi? Segala sesuatu dia selesaikan sendiri, seolah-olah kita semua tidak berguna."
    ""
    cl "Iya! Dia kasar sekali kalau bicara. Pas aku minta bantuan kemarin, dia malah bentakin aku."
    ""
    el "Kalian tau ngga? Dia main dengan anak-anak itu, berpura-pura baik, tapi di belakang sangat jahat."
    ""
    am "Exactly! Perilaku twoface banget. Seperti dia punya dua wajah."
    ""
    cl "Mungkin kita harus laporin dia ke manager? Perilakunya benar-benar merugikan lingkungan kerja."
    ""
    el "Iya setuju. Manager perlu tahu bahwa Tabitha ini toxic untuk tim kita."

    "Ketiga wanita itu tersenyum jahat, merencanakan bagaimana cara melapor dengan paling efektif."

    jump manager_office_scene


label manager_office_scene:
    scene bg black with fade
    
    "Ruang Manager Rumah Sakit - Sore Hari"
    ""
    mr "..."
    ""
    "Manajer Rumah Sakit duduk di meja kerjanya, mengeluh dalam hati tentang pekerjaan yang menumpuk. Berkas-berkas bertumpuk di meja, jadwal shift yang berantakan, dan keluhan dari berbagai departemen."
    ""
    mr "Tuhan... kenapa semuanya jadi masalah di hari ini? Apa tidak ada yang bisa berjalan lancar?"

    "Pintu terbuka. Amelia, Clara, dan Elena masuk dengan ekspresi yang serius dan berpura-pura khawatir."
    ""
    am "Manager, bisa kami bicara sebentar?"
    ""
    mr "Apa lagi? Cepatlah, aku punya banyak pekerjaan."
    ""
    cl "Ini tentang Tabitha Vane. Kami ingin melaporkan perilakunya yang tidak layak."
    ""
    el "Dia sangat kasar terhadap kami. Dia memperlakukan kami dengan tidak hormat."
    ""
    mr "Kasar? Berapa banyak orang yang sudah melapor?"
    ""
    am "Kami bertiga. Dan kami yakin ada juga orang lain yang merasa hal yang sama."
    ""
    mr "Baiklah... baiklah. Ini adalah laporan resmi. Terima kasih atas informasinya."

    "Ketiga wanita itu pergi dengan senyuman yang puas, sementara manager menghela napas berat."

    jump firing_scene


label firing_scene:
    scene bg black with fade
    
    "Ruang Perawatan - Setelah Tabitha Selesai Bermain dengan Anak"
    ""
    "Tabitha sedang merapihkan mainan terakhir ketika manager datang dengan wajah serius."
    ""
    mr "Tabitha, kita perlu bicara. Sekarang."
    ""
    ta "Ada apa, Manager? Apa ada masalah?"
    ""
    mr "Masalah? Iya, ada. Ada tiga laporan masuk tentang perilakumu yang tidak profesional. Banyak yang mengatakan kamu kasar dan tidak menghormati rekan kerja."
    ""
    ta "Apa? Itu tidak benar. Siapa yang bilang? Aku tidak pernah kasar kepada siapa pun."
    ""
    mr "Kamu menolak laporan ini? Mereka bertiga sudah datang dan melaporkan hal yang sama. Kamu pikir mereka semua bohong?"
    ""
    ta "Tidak, aku hanya... mereka mengada-ada. Aku tidak pernah melakukan apa yang mereka katakan!"
    ""
    mr "Kamu terus denial, Tabitha. Lihat, hari ini saja aku sudah kelelahan mendengarkan komplen. Dan sekarang kamu menambah masalah. Aku tidak punya energi untuk ini."
    ""
    mr "Cukup! Cukup! Aku tidak mau mendengar alibi lagi. Banyak laporan masuk ke saya. Kamu ngeraguin saya? Cukup bekerja sesuai aturan atau pergi. Ambil barangmu dan keluar dari sini sebelum aku memutuskan untuk mem-PHK mu sekarang juga!"

    ta "Ini tidak adil..."
    ""
    mr "Adil? Adil itu ketika tim bisa bekerja tanpa ketakutan dengan rekan kerja mereka. Sekarang pergi."

    "Tabitha terdiam. Emosi campur aduk. Dia merasa difitnah, direndahkan, dan tidak dihargai."

    jump tabitha_leaving_hospital


label tabitha_leaving_hospital:
    scene bg black with fade
    
    "Tabitha berjalan ke loker untuk mengambil barang pribadi. Tangan nya gemetar karena kemarahan."
    ""
    ta "Aku tidak layak mendapat perlakuan ini... Mereka bohong. Semua bohong!"
    ""
    "Dia mengemas tasnya dengan kasar, menutup loker dengan pukulan ringan."
    ""
    ta "Pergi dari rumah sakit ini. Tidak ada tempat untuk orang seperti aku di sini."

    "Tabitha berjalan keluar dari rumah sakit dengan wajah merah dan mata yang berapi-api. Dendam dan kecewa mulai berkembang di hati."

    jump arthur_police_station


label arthur_police_station:
    scene bg black with fade
    
    "Kantor Polisi - Hari Berikutnya - Siang Hari"
    ""
    "Arthur datang untuk menanyakan hasil penyelidikan kasusnya. Dia masuk ke ruang kepala polisi dengan kepercayaan diri."
    ""
    ar "Sir, saya ingin mengetahui perkembangan kasus pembunuhan itu. Sudah diaresto?"
    ""
    kp "Pendelton... duduk."
    ""
    ar "Ada apa? Mereka sudah ditangkap?"
    ""
    kp "Tidak. Mereka tidak akan ditangkap. Kasus ini ditutup."
    ""
    ar "Ditutup? Bagaimana bisa? Ada bukti! Ada jenazah! Ada hukum!"
    ""
    kp "Ya, ada semua itu. Tapi ada juga donasi. Ada juga kontribusi. Ada juga kepentingan lebih besar dari satu kasus pembunuhan."
    ""
    ar "Jadi Anda bilang hukum bisa diabaikan jika ada uang yang cukup? Itulah kepolisian sekarang?"
    ""
    kp "Pendelton, ini bukan dunia hitam putih. Ada nuansa grey yang harus dipahami."
    ""
    ar "Tidak. Ini hitam putih. Pembunuh harus dipenjara. Titik. Tidak ada nuansa disini."
    ""
    kp "Kamu terus memperdebatkan ini tanpa mengerti situasi politis. Aku tidak butuh detektif yang tidak bisa bekerja dalam sistem. Lencana mu, ambil dari atas mejaku. Kamu dipecat. Selesai."

    "Arthur terdiam sejenak, kemudian tiba-tiba berdiri dan meneriaki seluruh kantor."
    ""
    ar "Kalian semua busuk! Korup! Tidak pantas menjadi penjaga hukum! Kalian adalah pencuri berseragam!"

    "Arthur meninggalkan kantor dengan marah, menutup pintu keras-keras."

    jump tabitha_arrives_home


label tabitha_arrives_home:
    scene bg black with fade
    
    "Rumah Arthur dan Tabitha - Sore Hari"
    ""
    "Tabitha tiba di rumah duluan. Dia berjalan ke depan rumah dengan pikiran yang masih kalut dari pengalaman di rumah sakit."
    ""
    ta "Akhirnya pulang. Rumah adalah tempat yang aman... atau seharusnya begitu."
    ""
    "Tiba-tiba matanya melihat sesuatu yang mengerikan. Kotoran anjing bertebaran di depan rumah. Dan di jendela..."
    ""
    ta "..."
    ""
    "Di jendela ada tulisan besar: 'GO KILL YOURSELF'"
    ""
    ta "Tidak... tidak mungkin..."
    ""
    "Tabitha merasa semua emosi meledak sekaligus. Pengkhianatan di rumah sakit, pengasingan, ketidakadilan... dan sekarang ini. Karena mereka. Amelia, Clara, Elena."
    ""
    ta "MEREKA!!! MEREKA YANG LAKUKAN INI!!!"

    "Tabitha berlari masuk ke rumah dengan marah yang sudah tidak bisa dikontrol."

    jump house_destruction


label house_destruction:
    scene bg black with fade
    
    "Dalam Rumah"
    ""
    "Tabitha mulai merusak barang-barang di rumah. Gelas pecah, bantal dilempar, meja terbalik. Emosi yang terpendam selama berbulan-bulan meledak dalam sekejap."
    ""
    ta "Semuanya! Semua orang jahat! Semua orang bohong! Aku tidak pantas hidup di dunia seperti ini!"
    ""
    "Dia jatuh di lantai di tengah kehancuran, menangis dengan marah dan frustrasi."

    jump arthur_arrives_home


label arthur_arrives_home:
    scene bg black with fade
    
    "Sekitar 5 menit kemudian, Arthur tiba di rumah. Dia sudah tahu sesuatu salah ketika melihat pintu terbuka dan kotoran anjing di depan jendela."
    ""
    ar "Apa yang...?"
    ""
    "Arthur berlari masuk dan melihat rumah yang berantakan."
    ""
    ar "Tabitha! Apa yang terjadi?! Kenapa rumah berantakan?!"
    ""
    ta "..."
    ""
    "Tabitha masih duduk di lantai, melihat Arthur dengan mata yang penuh dendam dan kecewa."
    ""
    ar "Jawab aku! Ada kotoran di depan, jendela dicorat-coret, dan sekarang rumah ancur! APA YANG TERJADI?!"
    ""
    ta "Dunia ini isinya orang-orang jahat! Mereka fitnah aku! Mereka tulis hal kejam di rumah kita! Dan apa yang kamu lakukan?!"
    ""
    ar "Aku? AKU BARU SAJA DIPECAT KARENA AKU MENCOBA MELAKUKAN YANG BENAR! Lalu aku pulang dan melihat ini! Semuanya hancur!"
    ""
    ta "Semuanya memang seharusnya hancur! Dunia ini tidak layak untuk dipertahankan!"
    ""
    ar "Jangan bilang aku tentang dunia! Aku tahu dunia itu kasar! Tapi kita harus bertahan, Tabitha!"
    ""
    ta "Bertahan? UNTUK APA?! Untuk apa bertahan jika semua orang akan mengkhianati kita?!"
    ""
    "Mereka saling berteriak, mencari siapa yang paling bersalah, siapa yang paling menderita. Debat yang tidak ada akhir tentang dunia yang kejam dan hati yang rusak."

    jump roulette_proposal


label roulette_proposal:
    scene bg black with fade
    
    "Setelah berdebat selama hampir satu jam, Arthur dan Tabitha sama-sama lelah. Lelah fisik, lelah mental, lelah secara emosional."
    ""
    ar "Kita tidak bisa lanjut seperti ini."
    ""
    ta "Aku tahu."
    ""
    ar "Setiap hari kita saling menyakiti. Setiap hari sama saja."
    ""
    ta "Iya."
    ""
    ar "Mungkin kita perlu cara lain untuk mengakhiri ini. Cara yang jujur. Cara yang final."
    ""
    ta "Apa maksudmu?"
    ""
    ar "Roulette."
    ""
    ta "..."
    ""
    ta "Baik."
    ""
    "Mereka mengeluarkan revolver dari lemari. Revolver yang sudah mereka persiapkan sejak lama untuk situasi seperti ini. Sebuah keputusan yang final. Sebuah permainan yang tidak ada pemenang sejati."

    jump character_selection


label character_selection:
    scene black with fade
    
    "Sebelum permainan dimulai, ada satu pilihan terakhir yang harus dibuat."
    ""
    "Kamu akan memainkan siapa?"
    ""

    menu:
        "Arthur Pendelton (Detektif)":
            $ player_character = "arthur"
            ar "Baik. Aku yang mulai."
        
        "Tabitha Vane (Perawat)":
            $ player_character = "tabitha"
            ta "Baik. Aku yang mulai."

    "Permainan dimulai."

    jump secret_chest_preparation


label secret_chest_preparation:
    scene bg black with fade
    
    "Di tengah ruang tamu, ada peti kayu tua yang mereka letakkan di lantai. Di dalamnya tersimpan tiga item misterius, masing-masing dalam kotak tertutup."
    ""
    if player_character == "arthur":
        ar "Setiap kita ambil dua item dari peti ini. Item ini akan membantu kita bertahan atau memberikan keuntungan di permainan."
        ta "Baik. Kamu ambil dulu."
    else:
        ta "Setiap kita ambil dua item dari peti ini. Item ini akan membantu kita bertahan atau memberikan keuntungan di permainan."
        ar "Baik. Kamu ambil dulu."

    "Mari kita lihat apa yang ada di peti ini..."

    jump player_draws_items


label player_draws_items:
    if player_character == "arthur":
        ar "Oke, aku ambil item pertama..."
        $ item1 = draw_item_for("player")
        ar f"Aku mendapat {ITEM_NAMES[item1]}."
        ""
        ar "Dan item kedua..."
        $ item2 = draw_item_for("player")
        ar f"Aku juga mendapat {ITEM_NAMES[item2]}."
        ""
        jump dealer_draws_items
    else:
        ta "Oke, aku ambil item pertama..."
        $ item1 = draw_item_for("player")
        ta f"Aku mendapat {ITEM_NAMES[item1]}."
        ""
        ta "Dan item kedua..."
        $ item2 = draw_item_for("player")
        ta f"Aku juga mendapat {ITEM_NAMES[item2]}."
        ""
        jump dealer_draws_items


label dealer_draws_items:
    if player_character == "arthur":
        ta "Sekarang giliran aku..."
        $ item3 = draw_item_for("dealer")
        ta f"Aku mendapat {ITEM_NAMES[item3]}."
        ""
        ta "Dan item kedua..."
        $ item4 = draw_item_for("dealer")
        ta f"Aku juga mendapat {ITEM_NAMES[item4]}."
    else:
        ar "Sekarang giliran aku..."
        $ item3 = draw_item_for("dealer")
        ar f"Aku mendapat {ITEM_NAMES[item3]}."
        ""
        ar "Dan item kedua..."
        $ item4 = draw_item_for("dealer")
        ar f"Aku juga mendapat {ITEM_NAMES[item4]}."

    jump revolver_loading


label revolver_loading:
    scene bg black with fade
    
    if player_character == "arthur":
        ar "Sekarang untuk revolver."
        ar "Aku muat peluru."
        $ reset_battle_state()
        $ turn_owner = "player"
        ar f"Ada {total_bullets} peluru. {sum(1 for b in revolver_cylinder if b)} yang hidup. {total_bullets - sum(1 for b in revolver_cylinder if b)} yang kosong."
        ar "Kamu mau mencoba keberuntunganmu terlebih dahulu. Kamu mulai."
    else:
        ta "Sekarang untuk revolver."
        ta "Aku muat peluru."
        $ reset_battle_state()
        $ turn_owner = "player"
        ta f"Ada {total_bullets} peluru. {sum(1 for b in revolver_cylinder if b)} yang hidup. {total_bullets - sum(1 for b in revolver_cylinder if b)} yang kosong."
        ta "Kamu mau mencoba keberuntunganmu terlebih dahulu. Kamu mulai."

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

        call screen roulette_table
        $ player_choice = _return

        if player_choice == "shoot_dealer":
            $ shot_live = shoot_revolver("player", "dealer")
            $ turn_owner = "dealer" if shot_live else "player"
        elif player_choice == "shoot_self":
            $ shot_live = shoot_revolver("player", "player")
            $ turn_owner = "dealer" if shot_live else "player"

        jump battle_turn

    if dealer_handcuffed:
        $ dealer_handcuffed = False
        $ battle_message = f"{owner_display_name('dealer')} kehilangan giliran karena borgol."
        $ turn_owner = "player"
        jump battle_turn

    $ shot_live = dealer_turn_ai()
    $ turn_owner = "player" if shot_live else "dealer"
    jump battle_turn


label ending_player_wins:
    scene bg black with fade
    
    if player_character == "arthur":
        ar "Tabitha..."
        "Arthur menatap jasad Tabitha. Dunia yang dingin, penuh kebohongan, tiba-tiba terasa lebih dingin lagi."
        ""
        ar "Dunia ini tidak punya arti tanpa kekacauan hangat yang kau bawa. Bahkan dalam kebencian, kau membuat sesuatu yang nyata."
        ""
        "Arthur menangis. Kemudian, dengan tangan gemetar, dia mengarahkan revolver ke kepalanya sendiri dan menarik pelatuk."
        scene black with fade
    else:
        ta "Arthur..."
        "Tabitha menatap jasad Arthur. Kesunyian ruangan terasa membelah dada."
        ""
        ta "Kamu adalah orang pertama yang mencoba memahami aku. Dan aku membunuhmu. Dunia ini memang kejam, bukan?"
        ""
        "Kegilaan Tabitha mencapai puncaknya. Dia keluar dari rumah dengan mata yang kosong, mencari tiga wanita yang menghancurkan hidupnya."
        scene black with fade

    return


label ending_player_loses:
    scene bg black with fade
    
    if player_character == "arthur":
        ta "Arthur..."
        "Tabitha menatap jasad Arthur. Dalam amarah dan dendam, dia telah membunuh satu-satunya orang yang memahaminya."
        ""
        ta "Dunia ini sudah mengalahkan kita. Sekarang giliran aku."
        ""
        "Kegilaan Tabitha meledak. Dia meninggalkan rumah dalam keadaan penuh dendam, mencari balas dendam terhadap tiga wanita yang menghancurkan segalanya."
        scene black with fade
    else:
        ar "Tabitha..."
        "Arthur menatap jasad Tabitha dengan hati yang pecah."
        ""
        ar "Aku gagal menyelamatkan dirinya. Aku gagal menyelamatkan kita."
        ""
        "Arthur mengarahkan revolver ke kepalanya sendiri. Dalam kegelapan dan keputusasaan, dia menarik pelatuk terakhirnya."
        scene black with fade

    return


label ending_draw:
    scene bg black with fade
    
    if player_character == "arthur":
        ar "Kehabisan peluru."
        ta "Kehabisan peluru."
        ar "Tapi kemarahan tidak habis."
        ta "Tidak habis."
        ""
        "Mereka berdua berdiri, mata merah, berkeringat, dan luka."
        ""
        ar "Kita muat lagi."
        ta "Kita muat lagi."
        ""
        "Mereka mengambil dua revolver baru. Menodongkan ke kepala satu sama lain. Tersenyum gila, dalam cinta yang rusak dan pengkhianatan yang saling bertoleransi."
        ""
        ar "Bersamaan?"
        ta "Bersamaan."
        ""
        "Dua pelatuk ditarik dalam harmoni yang mengerikan."
        scene black with fade
    else:
        ta "Kehabisan peluru."
        ar "Kehabisan peluru."
        ta "Tapi kemarahan tidak habis."
        ar "Tidak habis."
        ""
        "Mereka berdua berdiri, mata merah, berkeringat, dan luka."
        ""
        ta "Kita muat lagi."
        ar "Kita muat lagi."
        ""
        "Mereka mengambil dua revolver baru. Menodongkan ke kepala satu sama lain. Tersenyum gila, dalam cinta yang rusak dan pengkhianatan yang saling bertoleransi."
        ""
        ta "Bersamaan?"
        ar "Bersamaan."
        ""
        "Dua pelatuk ditarik dalam harmoni yang mengerikan."
        scene black with fade

    return
