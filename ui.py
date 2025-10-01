import sys
from datetime import datetime
import state
from models import USER, ADMIN, MOVIE, SEAT, CINEMA
from services import notification_service, promotion_manager, Coupon
from utils import (
    NEW_MOVIE, NEW_SHOWTIME, DISCOUNT_COUPON, PERCENTAGE, FIXED_AMOUNT,
    PAYMENT_SUCCESS, BOOKING_CONFIRMED
)
from builders import ComboBuilder


def inicializar_dados():
    cinesystem = CINEMA("Cinesystem")
    filme1_cinesystem = MOVIE("Divergent", 139, "Action")
    filme2_cinesystem = MOVIE("Notting Hill", 124, "Romance")
    filme1_cinesystem.add_showtime("19:00", 1, [SEAT(f"A{i}") for i in range(1, 11)])
    filme2_cinesystem.add_showtime("16:00", 2, [SEAT(f"B{i}") for i in range(1, 11)])
    cinesystem.add_movie(filme1_cinesystem)
    cinesystem.add_movie(filme2_cinesystem)

    kinoplex = CINEMA("Kinoplex")
    filme1_kinoplex = MOVIE("The conjuring", 112, "Horror")
    filme2_kinoplex = MOVIE("Interestelar", 169, "Sci-Fi")
    filme1_kinoplex.add_showtime("20:00", 3, [SEAT(f"C{i}") for i in range(1, 11)])
    filme2_kinoplex.add_showtime("17:00", 4, [SEAT(f"D{i}") for i in range(1, 11)])
    kinoplex.add_movie(filme1_kinoplex)
    kinoplex.add_movie(filme2_kinoplex)
    
    centerplex = CINEMA("Centerplex")
    filme1_centerplex = MOVIE("Toy Story", 81, "Animation")
    filme1_centerplex.add_showtime("21:00", 5, [SEAT(f"E{i}") for i in range(1, 11)])
    centerplex.add_movie(filme1_centerplex)

    state.cinemas["Cinesystem"] = cinesystem
    state.cinemas["Kinoplex"] = kinoplex
    state.cinemas["Centerplex"] = centerplex
    
    state.usuarios_registrados["marcela"] = USER("Marcela", "marcela", "12345", "marcela@email.com")
    state.usuarios_registrados["joao"] = USER("João", "joao", "senha123", "joao@cinema.com")
    state.usuarios_registrados["pedro"] = USER("Pedro", "pedro", "senha456", "pedro@cinema.com")
    state.usuarios_registrados["admin"] = ADMIN("Admin", "admin", "admin123", "admin@cinema.com")
    state.usuarios_registrados["system"] = USER("System", "system", "system", "system@cinema.com")

def menu_principal():
    print("\nWelcome to the Movie Ticketing System!")
    while True:
        print("\n--- Main Menu ---")
        if state.usuario_logado:
            print(f"Welcome, {state.usuario_logado.name}!")
            print("[1] Watch Movies")
            print("[2] My Reservations")
            print("[3] Notifications")
            print("[4] Review a Movie")
            print("[5] View Reviews")
            print("[6] View Available Coupons")
            print("[7] View Mobile Ticket with QR Code")
            print("[8] Cancel a Purchase")
            if isinstance(state.usuario_logado, ADMIN):
                print("[9] Admin Panel")
            print("[0] Logout")
        else:
            print("[1] Login")
            print("[2] Exit")
        
        escolha = input("Select an option: ")

        if not state.usuario_logado:
            if escolha == "1":
                login()
            elif escolha == "2":
                print("Thank you for using the system!")
                sys.exit()
            else:
                print("Invalid option. Please try again.")
        else:
            if escolha == "1":
                ver_cinemas()
            elif escolha == "2":
                state.usuario_logado.view_booking_history()
            elif escolha == "3":
                menu_notifications()
            elif escolha == "4":
                avaliar_filme()
            elif escolha == "5":
                ver_avaliacoes()
            elif escolha == "6":
                view_coupons()
            elif escolha == "7":
                ver_bilhete_qrcode()
            elif escolha == "8":
                cancelar_compra()
            elif escolha == "9" and isinstance(state.usuario_logado, ADMIN):
                admin_panel()
            elif escolha == "0":
                state.usuario_logado = None
                print("You have logged out of your account.")
            else:
                print("Invalid option. Please try again.")

def menu_notifications():
    while True:
        print("\n--- Notifications ---")
        print("[1] View All Notifications")
        print("[2] View Unread Notifications")
        print("[3] Mark Notification as Read")
        print("[0] Back to main menu")

        escolha = input("Select an option: ")

        if escolha == "1":
            state.usuario_logado.view_notifications()
        elif escolha == "2":
            state.usuario_logado.view_notifications(unread_only=True)
        elif escolha == "3":
            notifications = state.usuario_logado.view_notifications(unread_only=True)
            if notifications:
                try:
                    notif_choice = int(input("Enter the notification number to mark as read: "))
                    if 1 <= notif_choice <= len(notifications):
                        notification_id = notifications[notif_choice - 1]['id']
                        if notification_service.mark_as_read(notification_id):
                            print("Notification marked as read.")
                        else:
                            print("Could not find notification.")
                    else:
                        print("Invalid number.")
                except ValueError:
                    print("Invalid input.")
        elif escolha == "0":
            return
        else:
            print("Invalid option. Please try again.")

def view_coupons():
    active_coupons = promotion_manager.list_active_coupons()
    if not active_coupons:
        print("No active coupons.")
    else:
        print("\nActive Coupons:")
        for coupon in active_coupons:
            print(f"\n Code: {coupon.code}")
            print(f" Description: {coupon.description}")
            if coupon.type == PERCENTAGE:
                print(f" Type: Percentage | Discount: {coupon.value}%")
            elif coupon.type == FIXED_AMOUNT:
                print(f" Type: Fixed Amount | Discount: R$ {coupon.value:.2f}")
            if coupon.min_purchase > 0:
                print(f" Minimum purchase: R$ {coupon.min_purchase:.2f}")
            if coupon.max_uses:
                print(f" Max uses: {coupon.max_uses} (Used {coupon.uses_count} times)")
            if coupon.valid_until:
                print(f" Valid until: {coupon.valid_until.strftime('%Y-%m-%d %H:%M:%S')}")
            if coupon.applicable_cinemas:
                print(f" Applicable cinemas: {', '.join(coupon.applicable_cinemas)}")
            if coupon.applicable_movies:
                print(f" Applicable movies: {', '.join(coupon.applicable_movies)}")
            if coupon.user_type:
                print(f" User type: {coupon.user_type}")
            print("-" * 50)

def ver_avaliacoes():
    print("\n--- Choose a Cinema to See Movie Reviews ---")
    cinema_keys = list(state.cinemas.keys())
    for i, cinema_nome in enumerate(cinema_keys, 1):
        print(f"[{i}] {cinema_nome}")
    print("[0] Back to main menu")

    try:
        escolha_cinema = input("Enter the theater number: ")
        if escolha_cinema == '0':
            return
        
        cinema_nome = cinema_keys[int(escolha_cinema) - 1]
        cinema_obj = state.cinemas[cinema_nome]

        print(f"\n--- Movies at {cinema_obj.name} ---")
        for i, movie in enumerate(cinema_obj.movies, 1):
            print(f"[{i}] {movie.name}")
        print("[0] Back")

        escolha_filme = input("Enter the number of the movie to see reviews for: ")
        if escolha_filme == '0':
            return
            
        movie_to_view = cinema_obj.movies[int(escolha_filme) - 1]

        print(f"\n--- Reviews for '{movie_to_view.name}' ---")
        if not movie_to_view.reviews:
            print("No reviews for this movie yet.")
        else:
            avg_rating = movie_to_view.get_average_rating()
            print(f"Average Rating: {avg_rating:.1f}/5.0")
            print("-" * 30)
            for i, review in enumerate(movie_to_view.reviews, 1):
                print(f"Review #{i} | Rating: {review['rating']}/5")
                print(f'"{review["comment"]}"')
                print("-" * 20)

    except (ValueError, IndexError):
        print("Invalid option. Please try again.")

def ver_bilhete_qrcode():
    if not state.usuario_logado.booking_history:
        print("You have no bookings to view.")
        return

    state.usuario_logado.view_booking_history()
    try:
        escolha = int(input("Enter the number of the booking to view the QR Code for (or '0' to go back): "))
        if escolha == 0:
            return
        
        index = escolha - 1
        if 0 <= index < len(state.usuario_logado.booking_history):
            ticket = state.usuario_logado.booking_history[index]
            ticket.generate_qr_code()
        else:
            print("Invalid booking number.")
    except ValueError:
        print("Invalid input. Please enter a number.")

def admin_panel():
    while True:
        print("\n--- ADMIN PANEL ---")
        print("[1] Add New Movie")
        print("[2] Add New Showtime")
        print("[3] Create New Coupon")
        print("[4] View System Reports")
        print("[5] Send Custom Notification")
        print("[0] Back to Main Menu")
        
        escolha = input("Select an option: ")
        
        if escolha == "1":
            add_movie_admin()
        elif escolha == "2":
            add_showtime_admin()
        elif escolha == "3":
            create_coupon_admin()
        elif escolha == "4":
            view_reports_admin() 
        elif escolha == "5":
            send_custom_notification_admin()
        elif escolha == "0":
            break
        else:
            print("Invalid option.")

def add_movie_admin():
    if "manage_movies" not in state.usuario_logado.permissions:
        print("Access denied.")
        return
    
    print("\n--- ADD NEW MOVIE ---")
    name = input("Movie name: ")
    duration = int(input("Duration (minutes): "))
    genre = input("Genre: ")
    
    print("\nSelect cinema:")
    cinema_keys = list(state.cinemas.keys())
    for i, cinema_name in enumerate(cinema_keys, 1):
        print(f"[{i}] {cinema_name}")
    
    try:
        cinema_choice = int(input("Cinema number: ")) - 1
        cinema_name = cinema_keys[cinema_choice]
        cinema = state.cinemas[cinema_name]
        
        new_movie = MOVIE(name, duration, genre)
        cinema.add_movie(new_movie)
        print(f"Movie '{new_movie.name}' added to {cinema.name} successfully!")

        for user in state.usuarios_registrados.values():
            if user.user_type != "admin":
                message = f"New movie available: '{new_movie.name}' at {cinema.name}!"
                data = {"movie_name": new_movie.name, "cinema_name": cinema.name, "genre": new_movie.genre}
                notification_service.send_notification(user, NEW_MOVIE, message, data)
                
    except (ValueError, IndexError):
        print("Invalid option.")

def add_showtime_admin():
    if "manage_movies" not in state.usuario_logado.permissions:
        print("Access denied.")
        return
    
    print("\n--- ADD NEW SHOWTIME ---")
    try:
        print("\nSelect cinema:")
        cinema_keys = list(state.cinemas.keys())
        for i, cinema_name in enumerate(cinema_keys, 1):
            print(f"[{i}] {cinema_name}")
        cinema_choice = int(input("Cinema number: ")) - 1
        cinema_name = cinema_keys[cinema_choice]
        cinema = state.cinemas[cinema_name]

        if not cinema.movies:
            print(f"No movies in {cinema.name} to add a showtime to.")
            return

        print("\nSelect movie:")
        for i, movie in enumerate(cinema.movies, 1):
            print(f"[{i}] {movie.name}")
        movie_choice = int(input("Movie number: ")) - 1
        selected_movie = cinema.movies[movie_choice]
        
        showtime_time = input("Showtime time (HH:MM): ")
        screen_number = int(input("Screen number: "))
        num_seats = int(input("Number of seats for this showtime: "))
        
        seats = [SEAT(f"S{i}") for i in range(1, num_seats + 1)]
        
        selected_movie.add_showtime(showtime_time, screen_number, seats)
        print(f"Showtime {showtime_time} added to '{selected_movie.name}' successfully!")

        for user in state.usuarios_registrados.values():
            if user.user_type != "admin":
                message = f"New showtime available: '{selected_movie.name}' at {showtime_time}!"
                data = {"movie_name": selected_movie.name, "time": showtime_time}
                notification_service.send_notification(user, NEW_SHOWTIME, message, data)

    except (ValueError, IndexError):
        print("Invalid option.")

def create_coupon_admin():
    if "manage_coupons" not in state.usuario_logado.permissions:
        print("Access denied.")
        return

    print("\n--- CREATE NEW COUPON ---")
    try:
        code = input("Coupon code: ")
        description = input("Coupon description: ")
        coupon_type = input("Coupon type (percentage/fixed_amount): ").lower()
        if coupon_type not in [PERCENTAGE, FIXED_AMOUNT]:
            print("Invalid type.")
            return
        
        value = float(input("Discount value (e.g., 10 for 10% or 10.0 for R$10): "))
        
        kwargs = {}
        min_purchase = float(input("Minimum purchase amount (0 for none): "))
        if min_purchase > 0: kwargs['min_purchase'] = min_purchase
            
        max_uses = int(input("Maximum uses (0 for unlimited): "))
        if max_uses > 0: kwargs['max_uses'] = max_uses
            
        valid_until_str = input("Valid until (YYYY-MM-DD HH:MM) or leave blank: ")
        if valid_until_str: kwargs['valid_until'] = datetime.strptime(valid_until_str, '%Y-%m-%d %H:%M')
            
        user_type = input("Applicable user type (student/regular) or leave blank: ")
        if user_type: kwargs['user_type'] = user_type

        new_coupon = Coupon(code, coupon_type, value, description, **kwargs)
        promotion_manager.add_coupon(new_coupon)
        print(f"Coupon '{code}' created successfully!")

        for user in state.usuarios_registrados.values():
            if user.user_type != "admin":
                message = f"New discount coupon available: {new_coupon.code} - {new_coupon.description}"
                data = {"coupon_code": new_coupon.code, "description": new_coupon.description}
                notification_service.send_notification(user, DISCOUNT_COUPON, message, data)

    except ValueError:
        print("Invalid input. Please check the format of your entries.")

def view_reports_admin():
    if "view_reports" not in state.usuario_logado.permissions:
        print("Access denied.")
        return
    
    print("\n--- System Reports ---")
    print("=" * 50)
    total_bookings = sum(len(user.booking_history) for user in state.usuarios_registrados.values())
    print(f"System-Wide Total Bookings: {total_bookings}")
    print(f"System-Wide Active Coupons: {len(promotion_manager.list_active_coupons())}")
    print(f"Total Registered Users: {len(state.usuarios_registrados)}")
    print("-" * 50)

    for cinema in state.cinemas.values():
        for movie in cinema.movies:
            print(f"\nMovie: {movie.name} ({cinema.name})")
            print("-" * 30)
            print(f"Total tickets sold: {movie.total_tickets_sold}")
            print(f"Total revenue: R$ {movie.total_revenue:.2f}")
            avg_price = movie.average_ticket_price
            print(f"Average ticket price: R$ {avg_price:.2f}")
            print("-" * 30)

def send_custom_notification_admin():
    if "send_notifications" not in state.usuario_logado.permissions:
        print("Access denied.")
        return

    print("\n--- SEND CUSTOM NOTIFICATION ---")
    message = input("Enter the notification message to send to all users: ")
    if not message:
        print("Message cannot be empty.")
        return

    for user in state.usuarios_registrados.values():
        if user.user_type != "admin":
            notification_service.send_notification(user, "custom_message", message)
    print("Custom notifications sent to all users.")

def login():
    resposta = input("\nAre you already registered? \n[1] Yes\n[2] No\n ")
    
    if resposta == "1":
        processar_login()
    elif resposta == "2":
        registrar()
    else:
        print("Invalid option.")

def processar_login():
    login_user = input("Login: ")
    password_user = input("Password: ")
    
    if login_user in state.usuarios_registrados and state.usuarios_registrados[login_user].password == password_user:
        state.usuario_logado = state.usuarios_registrados[login_user]
        print(f"Login successful! Welcome, {state.usuario_logado.name}.")
    else:
        print("Incorrect login or password.")

def registrar():
    name = input("Name: ")
    login_user = input("Login: ")
    print("The password must be a string and have at least 5 characters.")
    password_user = input("Password: ")
    
    if login_user in state.usuarios_registrados:
        print("This login already exists. Please try another one.")
    elif len(password_user) < 5:
         print("The password must be a string and have at least 5 characters.")
    else:
        state.usuarios_registrados[login_user] = USER(name, login_user, password_user)
        print("User successfully registered!")

def ver_cinemas():
    print("\n--- Choose a Cinema ---")
    cinema_keys = list(state.cinemas.keys())
    for i, cinema_nome in enumerate(cinema_keys, 1):
        print(f"[{i}] {cinema_nome}")
    print("[0] Back to main menu")
    
    while True:
        escolha = input("Enter the theater number: \n")
        if escolha == '0':
            return
        try:
            cinema_nome = cinema_keys[int(escolha) - 1]
            ver_filmes(state.cinemas[cinema_nome])
            break
        except (ValueError, IndexError):
            print("Invalid option.")
            
def ver_filmes(cinema_obj):
    print(f"\n--- Movies at {cinema_obj.name} ---")
    cinema_obj.list_movies()
    print("-" * 30)

    for i, movie in enumerate(cinema_obj.movies, 1):
        print(f"[{i}] {movie.name}")
    print("[0] Back to previous menu")
        
    while True:
        try:
            escolha_filme = input("Enter the number of the movie you want to buy tickets for: ")
            if escolha_filme == '0':
                return

            index_filme = int(escolha_filme) - 1
            if 0 <= index_filme < len(cinema_obj.movies):
                filme_selecionado = cinema_obj.movies[index_filme]
                comprar_ingresso(filme_selecionado)
                break 
            else:
                print("Invalid movie number. Please try again.")
        except (ValueError, IndexError):
            print("Invalid option. Please enter a number.")
        
def payment(valor):
    print(f"\n--- Payment Process of R${valor:.2f} ---")
    while True:
        forma_de_pagamento = input("Choose a payment method: \n[1] Credit Card\n[2] Debit Card\n[3] Pix\n[4] Cancel\n") 

        if forma_de_pagamento == "1":
            numero = input("Number of credit card(16 digits):").strip()
            if len(numero) == 16 and numero.isdigit():
                print(f"Payment made with Credit Card of R${valor:.2f}.")
                return True
            else:
                print("Invalid credit card number. Please try again.")
        elif forma_de_pagamento == "2":
            numero = input("Number of debit card(16 digits): ").strip()
            if len(numero) == 16 and numero.isdigit():
                print(f"Payment made with Debit Card of R${valor:.2f}.")
                return True
            else:
                print("Invalid debit card number. Please try again.")
        elif forma_de_pagamento == "3":
            print("Pix Key: cinemaenterprises.com")
            print(f"Value: R${valor:.2f}")
            print(f"Payment made with Pix of R${valor:.2f} Successfully completed.")
            return True
        elif forma_de_pagamento == "4":
            print("Payment canceled.")
            return False
        else:
            print("Invalid option. Please try again.")

def handle_combo_addition(builder):
    print("\n--- Combo Options ---")
    print("[1] Choose a Pre-built Combo (Quick)")
    print("[2] Customize Your Own Combo")
    print("[3] No combo, just the ticket")
    
    combo_option = input("Select an option: ").strip()
    
    if combo_option == "1":
        from builders import ComboDirector
        director = ComboDirector()
        director.builder = builder
        
        print("\n--- Pre-built Combos ---")
        print("[1] Basic Combo - Popcorn M + Soda M")
        print("[2] Premium Combo - Popcorn L + Soda L + Candy")
        print("[3] Family Combo - 2 Popcorns L + 4 Sodas M")
        print("[4] Student Combo - Popcorn S + Water")
        print("[0] Back")
        
        combo_choice = input("Select combo: ").strip()
        
        if combo_choice == "1":
            builder.add_popcorn(size="M")
            builder.add_soda(size="M")
            print("Basic Combo added!")
        elif combo_choice == "2":
            builder.add_popcorn(size="L")
            builder.add_soda(size="L")
            builder.add_candy(candy_type="Chocolate")
            print("Premium Combo added!")
        elif combo_choice == "3":
            builder.add_popcorn(size="L")
            builder.add_popcorn(size="L")
            builder.add_soda(size="M")
            builder.add_soda(size="M")
            builder.add_soda(size="M")
            builder.add_soda(size="M")
            print("Family Combo added!")
        elif combo_choice == "4":
            builder.add_popcorn(size="S")
            builder.add_water(size="M")
            print("Student Combo added!")
        elif combo_choice == "0":
            return False
        else:
            print("Invalid option.")
            return False
        
        apply_coupon = input("\nDo you have a coupon? \n[1] Yes\n[2] No\n ").strip()
        if apply_coupon == "1":
            coupon_code = input("Enter coupon code: ").strip()
            builder.apply_coupon(coupon_code)
        
        return True
    
    elif combo_option == "2":
        while True:
            print("\n--- Add Extras to Your Combo ---")
            print("[1] Add Popcorn")
            print("[2] Add Soda")
            print("[3] Add Juice")
            print("[4] Add Water")
            print("[5] Add Candy")
            print("[6] Add Nachos")
            print("[7] Add Hot Dog")
            print("[8] Apply Coupon")
            print("[9] Finish and Proceed to Payment")
            print("[10] Remove an Extra")
            print("[0] Cancel")
            extra_choice = input("Select an option: ").strip()

            if extra_choice == "1":
                while True:
                    size = input("Popcorn size (S, M, L): ").upper()
                    if size in ["S", "M", "L"]:
                        builder.add_popcorn(size=size)
                        break
                    else:
                        print("Invalid size. Please choose S, M, or L.")
            elif extra_choice == "2":
                while True:
                    size = input("Soda size (S, M, L): ").upper()
                    if size in ["S", "M", "L"]:
                        builder.add_soda(size=size)
                        break
                    else:
                        print("Invalid size. Please choose S, M, or L.")
            elif extra_choice == "3":
                while True:
                    size = input("Juice size (S, M, L): ").upper()
                    if size in ["S", "M", "L"]:
                        builder.add_juice(size=size)
                        break
                    else:
                        print("Invalid size. Please choose S, M, or L.")
            elif extra_choice == "4":
                while True:
                    size = input("Water size (S, M, L): ").upper()
                    if size in ["S", "M", "L"]:
                        builder.add_water(size=size)
                        break
                    else:
                        print("Invalid size. Please choose S, M, or L.")
            elif extra_choice == "5":
                while True:
                    candy_type = input("Candy type (e.g., Mixed, Chocolate): ").strip()
                    if candy_type:
                        builder.add_candy(candy_type=candy_type)
                        break
                    else:
                        print("Invalid candy type. Please enter a valid type.")
            elif extra_choice == "6":
                while True:
                    topping = input("Nachos topping (e.g., cheese, guacamole, jalapeño): ").strip()
                    if topping:
                        builder.add_nachos(topping=topping)
                        break
                    else:
                        print("Invalid topping. Please enter a valid topping.")
            elif extra_choice == "7":
                while True:
                    size = input("Hot Dog size (small, regular, jumbo): ").strip()
                    if size in ["small", "regular", "jumbo"]:
                        builder.add_hotdog(size=size)
                        break
                    else:
                        print("Invalid size. Please choose small, regular, or jumbo.")
            elif extra_choice == "8":
                while True:
                    coupon_code = input("Enter coupon code: ").strip()
                    if coupon_code:
                        builder.apply_coupon(coupon_code=coupon_code)
                        break
                    else:
                        print("Invalid coupon code. Please enter a valid code.")
            elif extra_choice == "9":
                break
            elif extra_choice == "10":
                if not builder._extras:
                    print("No extras to remove.")
                    continue
                print("\nCurrent Extras in Combo:")
                for i, extra in enumerate(builder._extras, 1):
                    print(f"[{i}] {extra.name} - R$ {extra.price:.2f}")
                try:
                    remove_choice = int(input("Enter the number of the extra to remove: ")) - 1
                    if 0 <= remove_choice < len(builder._extras):
                        builder.remove_extra(remove_choice)
                    else:
                        print("Invalid number.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
            elif extra_choice == "0":
                print("Combo addition canceled.")
                return False
            else:
                print("Invalid option. Please try again.")
        return True
    
    elif combo_option == "3":
        apply_coupon = input("\nDo you have a coupon? \n[1] Yes\n[2] No\n ").strip()
        if apply_coupon == "1":
            coupon_code = input("Enter coupon code: ").strip()
            builder.apply_coupon(coupon_code)
        return True
    
    else:
        print("Invalid option.")
        return False

def finalize_purchase(combo, movie, showtime, seat):
    seat.reservation_expiry = None
    combo.ticket.extras = combo.extras
    combo.ticket.purchase_product()
    for extra in combo.extras:
        if hasattr(extra, 'purchase_product'):
            extra.purchase_product()
    state.usuario_logado.add_booking(combo.ticket)
    movie.total_tickets_sold += 1
    movie.total_revenue += combo.total_price
    combo.ticket.generate_qr_code()

    notification_service.send_notification(
        state.usuario_logado, PAYMENT_SUCCESS,
        f"Payment confirmed: R$ {combo.total_price:.2f}",
        {"movie": movie.name, "time": showtime.time, "seat": seat.row_and_number}
    )
    notification_service.send_notification(
        state.usuario_logado, BOOKING_CONFIRMED,
        f"Booking confirmed for '{movie.name}'",
        {"movie": movie.name, "time": showtime.time, "seat": seat.row_and_number}
    )
    print("\nPurchase completed successfully!")

def comprar_ingresso(movie):
    print(f"\n--- Buy Ticket for '{movie.name}' ---")
    movie.list_showtimes()
    
    escolha_horario = input("Enter the session time (ex: 19:00): ")
    showtime_selecionado = next((s for s in movie.showtimes if s.time == escolha_horario), None)
    
    if not showtime_selecionado:
        print("Invalid time. Please try again.")
        return
        
    print(f"\nSelected time: {showtime_selecionado.time} | Room: {showtime_selecionado.screen_number}")
    showtime_selecionado.list_available_seats()
    
    assento_selecionado = None
    while True:
        escolha_assento = input("Enter the number of the seat you want (ex: A5): ").upper()
        assento_selecionado = next((s for s in showtime_selecionado.seats if s.row_and_number.upper() == escolha_assento), None)
        
        if not assento_selecionado:
            print("Invalid seat. Please try again.")
            continue
            
        if assento_selecionado.is_reserved:
            print("Seat already reserved. History:")
            assento_selecionado.get_history()
            continue
            
        if assento_selecionado.temp_reserve(state.usuario_logado, minutes=10):
            break
        else:
            print("Could not reserve seat. Please try another one.")

    while True:
        tipo_ingresso_input = input("Enter the ticket type (Standard, Student, VIP): ").strip().lower()
        if tipo_ingresso_input in ["standard", "student", "vip"]:
            tipo_ingresso = {"standard": "Standard", "student": "Student", "vip": "VIP"}[tipo_ingresso_input]
            break
        else:
            print("Invalid ticket type. Please choose from Standard, Student, or VIP.")
    
    builder = ComboBuilder(state.usuario_logado)
    builder.add_ticket(tipo_ingresso, assento_selecionado, showtime_selecionado)
    
    if not handle_combo_addition(builder):
        assento_selecionado.release(state.usuario_logado)
        return

    try:
        combo = builder.build()
        print(f"\nPurchase Summary:")
        print(f" Movie: {movie.name}")
        print(f" Session: {showtime_selecionado.time} - Room {showtime_selecionado.screen_number}")
        print(f" Seat: {assento_selecionado.row_and_number}")
        print(f" Ticket: {combo.ticket.name} - R$ {combo.ticket.price:.2f}")
        if combo.extras:
            for extra in combo.extras:
                print(f" Extra: {extra.name} - R$ {extra.price:.2f}")
        print(f" Total: R$ {combo.total_price:.2f}")
    except Exception as e:
        print(f"Error building combo: {e}")
        assento_selecionado.release(state.usuario_logado)
        return

    pagar = input(f"Proceed with payment of R$ {combo.total_price:.2f}? \n[1] Yes\n[2] No\n ").strip()
    if pagar == "1":
        if not assento_selecionado.check_expiry():
            if payment(combo.total_price):
                finalize_purchase(combo, movie, showtime_selecionado, assento_selecionado)
            else:
                print("Payment failed. Releasing seat.")
                assento_selecionado.release(state.usuario_logado)
        else:
            print("Your temporary reservation has expired. Please start over.")
    else:
        print("Purchase canceled.")
        assento_selecionado.release(state.usuario_logado)

def avaliar_filme():
    print("\n--- Choose a Cinema to Rate a Movie ---")
    cinema_keys = list(state.cinemas.keys())
    for i, cinema_nome in enumerate(cinema_keys, 1):
        print(f"[{i}]. {cinema_nome}")
    print("[0]. Back to main menu")

    while True:
        escolha = input("Enter the theater number: ")
        if escolha == '0':
            return
        try:
            cinema_nome = cinema_keys[int(escolha) - 1]
            cinema_obj = state.cinemas[cinema_nome]
            
            print(f"\n--- Movies available on {cinema_obj.name} ---")
            for i, movie in enumerate(cinema_obj.movies, 1):
                print(f"[{i}]. {movie.name}")
            
            escolha_filme = input("Enter the number of the movie you want to rate: ")
            movie_to_review = cinema_obj.movies[int(escolha_filme) - 1]

            rating = int(input("Your rating (1 a 5): "))
            if rating < 1 or rating > 5:
                raise ValueError
            comment = input("Your comment: ")
            
            movie_to_review.add_review(rating, comment)
            print("Review successfully submitted!")
            return

        except (ValueError, IndexError):
            print("Invalid option. Please try again.")

def cancelar_compra():
    if not state.usuario_logado.booking_history:
        print("You have no bookings to cancel.")
        return
    
    state.usuario_logado.view_booking_history()
    
    escolha = input("Enter the number of the booking you want to cancel (or '0' to go back): ")
    if escolha == '0':
        return
    
    try:
        index = int(escolha) - 1
        if 0 <= index < len(state.usuario_logado.booking_history):
            ticket_to_cancel = state.usuario_logado.booking_history[index]
            movie = ticket_to_cancel.showtime.movie
            
            total_canceled_value = ticket_to_cancel.price
            print(f"Canceling ticket: {ticket_to_cancel.name} - R$ {ticket_to_cancel.price:.2f}")

            for extra in ticket_to_cancel.extras:
                total_canceled_value += extra.price
                if hasattr(extra, 'cancel_purchase'):
                    extra.cancel_purchase()

            movie.total_revenue -= total_canceled_value
            movie.total_tickets_sold -= 1
    
            ticket_to_cancel.cancel_purchase()
            
            state.usuario_logado.remove_booking(ticket_to_cancel)
            
            print(f"Booking and associated extras cancelled successfully! R$ {total_canceled_value:.2f} will be refunded.")
        else:
            print("Invalid number.")
    except (ValueError, IndexError):
        print("Invalid option. Please try again.")