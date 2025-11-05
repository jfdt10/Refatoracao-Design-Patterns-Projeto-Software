import sys
import re
from datetime import datetime
import state
import uuid
from models import USER, ADMIN, MOVIE, SEAT, CINEMA
from services import notification_service, promotion_manager, Coupon
from utils import (
    NEW_MOVIE, NEW_SHOWTIME, DISCOUNT_COUPON, PERCENTAGE, FIXED_AMOUNT,
    PAYMENT_SUCCESS, BOOKING_CONFIRMED, BOOKING_CANCELLED, PAYMENT_REFUNDED, 
    CUSTOM_NOTIFICATION, TICKET_STANDARD, TICKET_STUDENT, TICKET_VIP, USER_ADMIN
)
from builders import ComboBuilder,ComboDirector
from observer import event_bus, analytics_observer
from commands import PurchaseComboCommand, CancelProductCommand
from facade import cinema_system
from decorator import SpecialPackagingDecorator, ExtraItemDecorator, GiftWrapDecorator
from services import multi_channel_service

from exceptions import (
    InvalidEmailException,
    InvalidCPFException,
    InvalidPhoneException,
    InvalidPasswordException,
    InvalidPaymentMethodException,
    PaymentLimitExceededException,
    PaymentProcessingException,
    InvalidCouponException,
    CouponExpiredException,
    CouponUsageLimitException,
    MinimumPurchaseException,
    NotificationDeliveryException,
    SeatAlreadyReservedException,
    SeatNotAvailableException,
    ReservationExpiredException,
    BookingException,
    PaymentException,
    CouponException,
    InvalidCredentialsException,
    UserNotFoundException,
    UnauthorizedAccessException
)


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
    
    marcela = USER("Marcela", "marcela", "12345", "marcela@email.com", "82 3344-9999")
    marcela.device_token = f"device_{uuid.uuid4().hex[:16]}"
    state.usuarios_registrados["marcela"] = marcela

    joao = USER("João", "joao", "senha123", "joao@cinema.com", "(11) 99999-2222")
    joao.device_token = f"device_{uuid.uuid4().hex[:16]}"
    state.usuarios_registrados["joao"] = joao
    
    pedro = USER("Pedro", "pedro", "senha456", "pedro@cinema.com") 
    state.usuarios_registrados["pedro"] = pedro

    admin = ADMIN("Admin", "admin", "admin123", "admin@cinema.com", "(11) 99999-0030")
    admin.device_token = f"device_{uuid.uuid4().hex[:16]}"
    state.usuarios_registrados["admin"] = admin
    
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
                except (ValueError, TypeError):
                    print("Invalid input. Please enter a valid number.")
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
        
        cinema_idx = int(escolha_cinema) - 1
        if not (0 <= cinema_idx < len(cinema_keys)):
            raise IndexError("Invalid cinema number.")
        
        cinema_nome = cinema_keys[cinema_idx]
        cinema_obj = state.cinemas[cinema_nome]

        print(f"\n--- Movies at {cinema_obj.name} ---")
        for i, movie in enumerate(cinema_obj.movies, 1):
            print(f"[{i}] {movie.name}")
        print("[0] Back")

        escolha_filme = input("Enter the number of the movie to see reviews for: ")
        if escolha_filme == '0':
            return
            
        movie_idx = int(escolha_filme) - 1
        if not (0 <= movie_idx < len(cinema_obj.movies)):
            raise IndexError("Invalid movie number.")
            
        movie_to_view = cinema_obj.movies[movie_idx]

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

    except (ValueError, IndexError) as e:
        print(f"Invalid option: {e}. Please enter a valid number.")
    except KeyError:
        print("Error: Cinema or movie not found in the system.")


def ver_bilhete_qrcode():
    active_bookings = [t for t in state.usuario_logado.booking_history if not getattr(t, "cancelled", False)]
    if not active_bookings:
        print("You have no active bookings to view.")
        return

    print("\n Your Active Bookings:")
    print("=" * 50)
    for i, ticket in enumerate(active_bookings, 1):
        try:
            movie_name = getattr(getattr(getattr(ticket, "showtime", None), "movie", None), "name", "N/A")
            seat = getattr(getattr(ticket, "seat", None), "row_and_number", "N/A")
            print(f"[{i}] {getattr(ticket, 'name', 'TICKET').upper()} - {movie_name} (Seat {seat})")
        except (AttributeError, TypeError):
            print(f"[{i}] {getattr(ticket, 'name', 'TICKET').upper()}")
    
    try:
        escolha = int(input("Enter the number of the booking to view the QR Code for (or '0' to go back): "))
        if escolha == 0:
            return
        
        index = escolha - 1
        if 0 <= index < len(active_bookings):
            ticket = active_bookings[index]
            ticket.generate_qr_code()
        else:
            print("Invalid booking number.")
    except (ValueError, TypeError):
        print("Invalid input. Please enter a number.")


def admin_panel():
    while True:
        print("\n--- ADMIN PANEL ---")
        print("[1] Add New Movie")
        print("[2] Add New Showtime")
        print("[3] Create New Coupon")
        print("[4] View System Reports")
        print("[5] Send Custom Notification")
        print("[6] View Analytics Summary")
        print("[7] View Notification Channels Statistics")
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
        elif escolha == "6":
            view_analytics_summary()
        elif escolha == "7":
            view_notification_statistics_admin()
        elif escolha == "0":
            break
        else:
            print("Invalid option.")


def view_analytics_summary():
    try:
        if "view_reports" not in state.usuario_logado.permissions:
            raise UnauthorizedAccessException(
                state.usuario_logado.login if hasattr(state.usuario_logado, 'login') else "unknown",
                "view_reports"
            )
    except UnauthorizedAccessException as e:
        print(f"Access denied: {e}")
        return

    print(analytics_observer.get_report())
    input("\n Press ENTER to go back...")


def add_movie_admin():
    try:
        if "manage_movies" not in state.usuario_logado.permissions:
            raise UnauthorizedAccessException(
                state.usuario_logado.login if hasattr(state.usuario_logado, 'login') else "unknown",
                "manage_movies"
            )
    except UnauthorizedAccessException as e:
        print(f"Access denied: {e}")
        return
    
    print("\n--- ADD NEW MOVIE ---")
    
    try:
        name = input("Movie name: ").strip()
        if not name:
            print("Error: Movie name cannot be empty.")
            return
        
        try:
            duration_input = input("Duration (minutes): ").strip()
            duration = int(duration_input)
            if duration <= 0:
                print("Error: Duration must be a positive number.")
                return
        except ValueError:
            print("Error: Invalid duration. Must be a number.")
            return
        
        genre = input("Genre: ").strip()
        if not genre:
            print("Error: Genre cannot be empty.")
            return
        
        print("\nSelect cinema:")
        cinema_keys = list(state.cinemas.keys())
        for i, cinema_name in enumerate(cinema_keys, 1):
            print(f"[{i}] {cinema_name}")
        
        try:
            cinema_choice_input = input("Cinema number: ").strip()
            cinema_choice = int(cinema_choice_input) - 1
            
            if cinema_choice < 0 or cinema_choice >= len(cinema_keys):
                print(f"Error: Invalid cinema number. Please choose between 1 and {len(cinema_keys)}.")
                return
                
            cinema_name = cinema_keys[cinema_choice]
            cinema = state.cinemas[cinema_name]
            
        except ValueError:
            print("Error: Invalid input. Cinema number must be a number.")
            return
        except IndexError:
            print(f"Error: Invalid cinema number. Please choose between 1 and {len(cinema_keys)}.")
            return
        
        try:
            new_movie = MOVIE(name, duration, genre)
            cinema.add_movie(new_movie)
            print(f"Movie '{new_movie.name}' added to {cinema.name} successfully!")
        except Exception as e:
            print(f"Error creating movie: {e}")
            return

        print("\nSelect notification channels (comma-separated, e.g., app,email,sms,push):")
        print("Available channels: app, email, sms, push")
        channels_input = input("Channels: ").strip()
        
        if not channels_input:
            print("No channels selected. Movie added but no notifications sent.")
            return
        
        selected_channels = [c.strip().lower() for c in channels_input.split(',') if c.strip()]
        valid_channels = ['app', 'email', 'sms', 'push']
        invalid_channels = [ch for ch in selected_channels if ch not in valid_channels]
        
        if invalid_channels:
            print(f"Warning: Invalid channels ignored: {', '.join(invalid_channels)}")
            selected_channels = [ch for ch in selected_channels if ch in valid_channels]
        
        if not selected_channels:
            print("No valid channels selected. Movie added but no notifications sent.")
            return

        targets = [u for u in state.usuarios_registrados.values() if u.user_type != USER_ADMIN]
        
        try:
            event_bus.publish(NEW_MOVIE, {
                "movie_name": new_movie.name,
                "cinema_name": cinema.name,
                "genre": new_movie.genre,
                "targets": targets,
                "channels": selected_channels
            })
            print(f"New movie notification sent via channels: {', '.join(selected_channels)}.")
        except NotificationDeliveryException as e:
            print(f"Warning: Notification delivery issue - {e}")
        except Exception as e:
            print(f"Warning: Failed to send notifications - {e}")
            
    except KeyboardInterrupt:
        print("\nOperation canceled by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")


def add_showtime_admin():
    try:
        if "manage_movies" not in state.usuario_logado.permissions:
            raise UnauthorizedAccessException(
                state.usuario_logado.login if hasattr(state.usuario_logado, 'login') else "unknown",
                "manage_movies"
            )
    except UnauthorizedAccessException as e:
        print(f"Access denied: {e}")
        return
    
    print("\n--- ADD NEW SHOWTIME ---")
    try:
        print("\nSelect cinema:")
        cinema_keys = list(state.cinemas.keys())
        for i, cinema_name in enumerate(cinema_keys, 1):
            print(f"[{i}] {cinema_name}")
        
        try:
            cinema_choice_input = input("Cinema number: ").strip()
            cinema_choice = int(cinema_choice_input) - 1
            
            if cinema_choice < 0 or cinema_choice >= len(cinema_keys):
                print(f"Error: Invalid cinema number. Please choose between 1 and {len(cinema_keys)}.")
                return
                
            cinema_name = cinema_keys[cinema_choice]
            cinema = state.cinemas[cinema_name]
        except ValueError:
            print("Error: Invalid input. Cinema number must be a number.")
            return
        except IndexError:
            print(f"Error: Invalid cinema number. Please choose between 1 and {len(cinema_keys)}.")
            return

        if not cinema.movies:
            print(f"No movies in {cinema.name} to add a showtime to.")
            return

        print("\nSelect movie:")
        for i, movie in enumerate(cinema.movies, 1):
            print(f"[{i}] {movie.name}")
        
        try:
            movie_choice_input = input("Movie number: ").strip()
            movie_choice = int(movie_choice_input) - 1
            
            if movie_choice < 0 or movie_choice >= len(cinema.movies):
                print(f"Error: Invalid movie number. Please choose between 1 and {len(cinema.movies)}.")
                return
                
            selected_movie = cinema.movies[movie_choice]
        except ValueError:
            print("Error: Invalid input. Movie number must be a number.")
            return
        except IndexError:
            print(f"Error: Invalid movie number. Please choose between 1 and {len(cinema.movies)}.")
            return
        
        showtime_time = input("Showtime time (HH:MM): ").strip()
        if not showtime_time:
            print("Error: Showtime cannot be empty.")
            return
        
        if not re.match(r'^\d{1,2}:\d{2}$', showtime_time):
            print("Error: Invalid time format. Use HH:MM (e.g., 19:00).")
            return
        
        try:
            screen_number_input = input("Screen number: ").strip()
            screen_number = int(screen_number_input)
            if screen_number <= 0:
                print("Error: Screen number must be a positive number.")
                return
        except ValueError:
            print("Error: Invalid screen number. Must be a number.")
            return
        
        try:
            num_seats_input = input("Number of seats for this showtime: ").strip()
            num_seats = int(num_seats_input)
            if num_seats <= 0:
                print("Error: Number of seats must be a positive number.")
                return
            if num_seats > 100:
                print("Warning: Creating a large number of seats. Maximum is 100.")
                num_seats = 100
        except ValueError:
            print("Error: Invalid number of seats. Must be a number.")
            return
        
        try:
            seats = [SEAT(f"S{i}") for i in range(1, num_seats + 1)]
            selected_movie.add_showtime(showtime_time, screen_number, seats)
            print(f"Showtime {showtime_time} added to '{selected_movie.name}' successfully!")
        except Exception as e:
            print(f"Error adding showtime: {e}")
            return

        print("\nSelect notification channels (comma-separated, e.g., app,email,sms,push):")
        print("Available channels: app, email, sms, push")
        channels_input = input("Channels: ").strip()
        
        if not channels_input:
            print("No channels selected. Showtime added but no notifications sent.")
            return
        
        selected_channels = [c.strip().lower() for c in channels_input.split(',') if c.strip()]
        valid_channels = ['app', 'email', 'sms', 'push']
        invalid_channels = [ch for ch in selected_channels if ch not in valid_channels]
        
        if invalid_channels:
            print(f"Warning: Invalid channels ignored: {', '.join(invalid_channels)}")
            selected_channels = [ch for ch in selected_channels if ch in valid_channels]
        
        if not selected_channels:
            print("No valid channels selected. Showtime added but no notifications sent.")
            return

        targets = [u for u in state.usuarios_registrados.values() if u.user_type != USER_ADMIN]
        
        try:
            event_bus.publish(NEW_SHOWTIME, {
                "movie_name": selected_movie.name,
                "time": showtime_time,
                "targets": targets,
                "channels": selected_channels
            })
            print(f"New showtime notification sent via channels: {', '.join(selected_channels)}.")
        except NotificationDeliveryException as e:
            print(f"Warning: Notification delivery issue - {e}")
        except Exception as e:
            print(f"Warning: Failed to send notifications - {e}")
            
    except KeyboardInterrupt:
        print("\nOperation canceled by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")


def create_coupon_admin():
    try:
        if "manage_coupons" not in state.usuario_logado.permissions:
            raise UnauthorizedAccessException(
                state.usuario_logado.login if hasattr(state.usuario_logado, 'login') else "unknown",
                "manage_coupons"
            )
    except UnauthorizedAccessException as e:
        print(f"Access denied: {e}")
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
        if min_purchase > 0: 
            kwargs['min_purchase'] = min_purchase
            
        max_uses = int(input("Maximum uses (0 for unlimited): "))
        if max_uses > 0: 
            kwargs['max_uses'] = max_uses
            
        valid_until_str = input("Valid until (YYYY-MM-DD HH:MM) or leave blank: ")
        if valid_until_str: 
            kwargs['valid_until'] = datetime.strptime(valid_until_str, '%Y-%m-%d %H:%M')
            
        user_type = input("Applicable user type (student/regular) or leave blank: ")
        if user_type: 
            kwargs['user_type'] = user_type

        new_coupon = Coupon(code, coupon_type, value, description, **kwargs)
        promotion_manager.add_coupon(new_coupon)
        print(f"Coupon '{code}' created successfully!")

        targets = [u for u in state.usuarios_registrados.values() if u.user_type != USER_ADMIN]
        
        try:
            event_bus.publish(DISCOUNT_COUPON, {
                "coupon_code": new_coupon.code,
                "description": new_coupon.description,
                "targets": targets
            })
        except NotificationDeliveryException as e:
            print(f"Warning: {e}")

    except (ValueError, TypeError):
        print("Invalid input. Please check the format of your entries.")


def view_reports_admin():
    try:
        if "view_reports" not in state.usuario_logado.permissions:
            raise UnauthorizedAccessException(
                state.usuario_logado.login if hasattr(state.usuario_logado, 'login') else "unknown",
                "view_reports"
            )
    except UnauthorizedAccessException as e:
        print(f"Access denied: {e}")
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
    
    try:
        message = input("Enter the notification message to send to all users: ").strip()
        if not message:
            print("Error: Message cannot be empty.")
            return

        print("\nSelect notification channels (comma-separated, e.g., app,email,sms,push):")
        print("Available channels: app, email, sms, push")
        channels_input = input("Channels: ").strip()
        
        if not channels_input:
            print("Error: No channels selected. Notification will not be sent.")
            return
        
        selected_channels = [c.strip().lower() for c in channels_input.split(',') if c.strip()]
        valid_channels = ['app', 'email', 'sms', 'push']
        invalid_channels = [ch for ch in selected_channels if ch not in valid_channels]
        
        if invalid_channels:
            print(f"Warning: Invalid channels ignored: {', '.join(invalid_channels)}")
            selected_channels = [ch for ch in selected_channels if ch in valid_channels]
        
        if not selected_channels:
            print("Error: No valid channels selected. Notification will not be sent.")
            return

        targets = [u for u in state.usuarios_registrados.values() if u.user_type != USER_ADMIN]
        
        if not targets:
            print("Warning: No users to send notifications to.")
            return
        
        try:
            event_bus.publish(CUSTOM_NOTIFICATION, {
                "message": message,
                "targets": targets,
                "channels": selected_channels
            })
            print(f"Custom notifications sent to {len(targets)} users via channels: {', '.join(selected_channels)}.")
        except NotificationDeliveryException as e:
            print(f"Warning: Notification delivery issue - {e}")
        except Exception as e:
            print(f"Warning: Failed to send notifications - {e}")
            
    except KeyboardInterrupt:
        print("\nOperation canceled by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")


def view_notification_statistics_admin():
    try:
        if "view_reports" not in state.usuario_logado.permissions:
            raise UnauthorizedAccessException(
                state.usuario_logado.login if hasattr(state.usuario_logado, 'login') else "unknown",
                "view_reports"
            )
    except UnauthorizedAccessException as e:
        print(f"Access denied: {e}")
        return
    print("\n" + "=" * 60)
    print(" NOTIFICATION CHANNELS STATISTICS")
    print("=" * 60)
    
    stats = multi_channel_service.get_channel_statistics()
    total_sent = sum(stats.values())
    
    print(f"\n Total messages sent across all channels: {total_sent}")
    print("-" * 60)

    for channel_name, channel in multi_channel_service.channels.items():
        count = stats.get(channel_name, 0)
        print(f"\n {channel_name.upper()} Channel: {count} messages sent")
        
        if channel and hasattr(channel, 'sent_messages') and channel.sent_messages:
            print(f"   Last 5 messages:")
            for i, msg in enumerate(channel.sent_messages[-5:], 1):
                timestamp = msg.get('timestamp', 'N/A')
                if isinstance(timestamp, datetime):
                    timestamp = timestamp.strftime("%d/%m/%Y %H:%M:%S")
                
                if channel_name == "email":
                    print(f"   [{i}] To: {msg.get('email', 'N/A')} | Subject: {msg.get('subject', 'N/A')} | Time: {timestamp}")
                elif channel_name == "sms":
                    print(f"   [{i}] To: {msg.get('phone', 'N/A')} | Time: {timestamp}")
                elif channel_name == "push":
                    device = msg.get('device_token', 'N/A')[:12] + "..." if msg.get('device_token') else 'N/A'
                    print(f"   [{i}] Device: {device} | Title: {msg.get('subject', 'N/A')} | Time: {timestamp}")
        else:
            print(f"   No messages sent yet.")
    
    print("\n" + "-" * 60)
    print(f" In-App Notifications: {len(multi_channel_service.notifications)} total")
    unread_count = sum(1 for n in multi_channel_service.notifications if not n['read'])
    read_count = len(multi_channel_service.notifications) - unread_count
    print(f"   Unread: {unread_count} | Read: {read_count}")
    
    print("=" * 60)
    input("\nPress ENTER to go back...")


def login():
    resposta = input("\nAre you already registered? \n[1] Yes\n[2] No\n ")
    
    if resposta == "1":
        processar_login()
    elif resposta == "2":
        registrar()
    else:
        print("Invalid option.")


def processar_login():
    try:
        login_user = input("Login: ").strip()
        password_user = input("Password: ").strip()
        
        if not login_user or not password_user:
            print("Error: Login and password cannot be empty.")
            return
        
        if login_user not in state.usuarios_registrados:
            raise UserNotFoundException(login_user)
        
        if state.usuarios_registrados[login_user].password != password_user:
            raise InvalidCredentialsException(login_user)
        
        state.usuario_logado = state.usuarios_registrados[login_user]
        print(f"Login successful! Welcome, {state.usuario_logado.name}.")
        
    except UserNotFoundException as e:
        print(f"Error: {e}")
    except InvalidCredentialsException as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nLogin canceled.")
    except Exception as e:
        print(f"Unexpected error during login: {e}")


def registrar():
    name = input("Name: ")
    login_user = input("Login: ")
    email = input("Email: ")
    password_user = input("Password: ")
    phone = input("Phone (optional, format: (82) 99900-0030 or leave blank): ").strip()
    cpf = input("CPF (optional, format: 123.456.789-01 or leave blank): ").strip()
    
    if login_user in state.usuarios_registrados:
        print("This login already exists. Please try another one.")
        return
    
    try:
        phone_value = phone if phone else None
        cpf_value = cpf if cpf else None
        
        new_user = USER(name, login_user, password_user, email, phone_value, cpf_value)

        if phone_value:
            new_user.device_token = f"device_{uuid.uuid4().hex[:16]}"
        
        state.usuarios_registrados[login_user] = new_user
        print("User successfully registered!")
        
        if cpf_value:
            print(f"CPF registered: {new_user.cpf_formatted}")
        if phone_value:
            print(f"SMS and Push notifications enabled for {phone_value}")
            
    except InvalidEmailException as e:
        print(f"Registration failed: {e}")
    except InvalidPhoneException as e:
        print(f"Registration failed: {e}")
    except InvalidCPFException as e:
        print(f"Registration failed: {e}")
    except InvalidPasswordException as e:
        print(f"Registration failed: {e}")
    except (ValueError, TypeError) as e:
        print(f"Registration failed: Invalid data format - {e}")


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
        except (ValueError, IndexError, TypeError):
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
        except (ValueError, IndexError, TypeError):
            print("Invalid option. Please enter a number.")


def payment(valor):
    print(f"\n--- Payment Process of R${valor:.2f} ---")
    while True:
        forma_de_pagamento = input("Choose a payment method: \n[1] Credit Card\n[2] Debit Card\n[3] Pix\n[4] Cancel\nOption: ").strip()

        if forma_de_pagamento == "1":
            numero = input("Number of credit card (16 digits): ").strip()
            if len(numero) == 16 and numero.isdigit():
                try:
                    success, transaction_id = cinema_system.payments.process_payment("credit", valor, state.usuario_logado)
                    if success:
                        print(f"Payment made with Credit Card of R${valor:.2f}.")
                        print(f"Transaction ID: {transaction_id}")
                        return True
                    else:
                        print("Payment failed. Please try again.")
                except (PaymentLimitExceededException, PaymentProcessingException, InvalidPaymentMethodException) as e:
                    print(f"Payment error: {e}")
                    retry = input("Try again? [Y/N]: ").strip().upper()
                    if retry != "Y":
                        return False
            else:
                print("Invalid credit card number. Please try again.")
                
        elif forma_de_pagamento == "2":
            numero = input("Number of debit card (16 digits): ").strip()
            if len(numero) == 16 and numero.isdigit():
                try:
                    success, transaction_id = cinema_system.payments.process_payment("debit", valor, state.usuario_logado)
                    if success:
                        print(f"Payment made with Debit Card of R${valor:.2f}.")
                        print(f"Transaction ID: {transaction_id}")
                        return True
                    else:
                        print("Payment failed. Please try again.")
                except (PaymentLimitExceededException, PaymentProcessingException, InvalidPaymentMethodException) as e:
                    print(f"Payment error: {e}")
                    retry = input("Try again? [Y/N]: ").strip().upper()
                    if retry != "Y":
                        return False
            else:
                print("Invalid debit card number. Please try again.")
                
        elif forma_de_pagamento == "3":
            print("Pix Key: cinemaenterprises.com")
            print(f"Value: R${valor:.2f}")
            try:
                success, transaction_id = cinema_system.payments.process_payment("pix", valor, state.usuario_logado)
                if success:
                    print(f"Payment made with Pix of R${valor:.2f} Successfully completed.")
                    print(f"Transaction ID: {transaction_id}")
                    return True
                else:
                    print("Payment failed. Please try again.")
            except (PaymentLimitExceededException, PaymentProcessingException, InvalidPaymentMethodException) as e:
                print(f"Payment error: {e}")
                retry = input("Try again? [Y/N]: ").strip().upper()
                if retry != "Y":
                    return False
                    
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
            try:
                builder.apply_coupon(coupon_code)
            except (InvalidCouponException, CouponExpiredException, CouponUsageLimitException, MinimumPurchaseException) as e:
                print(f"Coupon error: {e}")
        
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
            print("[11] Decorate a Product")
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
                        try:
                            builder.apply_coupon(coupon_code=coupon_code)
                            break
                        except (InvalidCouponException, CouponExpiredException, CouponUsageLimitException, MinimumPurchaseException) as e:
                            print(f"Coupon error: {e}")
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
                except (ValueError, TypeError):
                    print("Invalid input. Please enter a number.")
            elif extra_choice == "11":
                if not builder._extras:
                    print("No products to decorate. Add a product first.")
                    continue
                
                print("\nSelect a product to decorate:")
                for i, extra in enumerate(builder._extras, 1):
                    print(f"[{i}] {extra.name} - R$ {extra.price:.2f}")
                
                try:
                    idx = int(input("Enter the number of the product to decorate: ")) - 1
                    if 0 <= idx < len(builder._extras):
                        product = builder._extras[idx]
                        
                        print("\nChoose decoration:")
                        print("[1] Special Packaging (+R$5.00)")
                        print("[2] Add Extra Item")
                        print("[3] Gift Wrap (+R$3.00)")
                        print("[0] Cancel")
                        
                        dec_choice = input("Select decoration: ").strip()
                        
                        if dec_choice == "1":
                            builder._total_price -= product.price
                            decorated_product = SpecialPackagingDecorator(product)
                            builder._extras[idx] = decorated_product
                            builder._total_price += decorated_product.price
                            print(f"Added special packaging to {product.name}!")
                            
                        elif dec_choice == "2":
                            extra_item = input("Enter extra item name: ").strip()
                            try:
                                extra_price = float(input("Enter extra price: R$"))
                                builder._total_price -= product.price
                                decorated_product = ExtraItemDecorator(product, extra_item, extra_price)
                                builder._extras[idx] = decorated_product
                                builder._total_price += decorated_product.price
                                print(f"Added {extra_item} to {product.name}!")
                            except (ValueError, TypeError):
                                print("Invalid price. Decoration canceled.")
                                
                        elif dec_choice == "3":
                            message = input("Enter gift message (optional): ").strip()
                            builder._total_price -= product.price
                            decorated_product = GiftWrapDecorator(product, message)
                            builder._extras[idx] = decorated_product
                            builder._total_price += decorated_product.price
                            print(f"Added gift wrap to {product.name}!")
                            
                        elif dec_choice == "0":
                            print("Decoration canceled.")
                        else:
                            print("Invalid option.")
                    else:
                        print("Invalid selection.")
                except (ValueError, TypeError):
                    print("Please enter a valid number.")
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
            try:
                builder.apply_coupon(coupon_code)
            except (InvalidCouponException, CouponExpiredException, CouponUsageLimitException, MinimumPurchaseException) as e:
                print(f"Coupon error: {e}")
        return True
    
    else:
        print("Invalid option.")
        return False


def finalize_purchase(combo, movie, showtime, seat):
    print(f"\nConfirming seat {seat.row_and_number} (current: {seat.get_status()})...")
    
    try:
        if seat.confirm():
            print(f"Seat {seat.row_and_number} is now {seat.get_status()}.")
        else:
            print(f"Could not confirm seat {seat.row_and_number}. Current status: {seat.get_status()}")
            return False
    except SeatNotAvailableException as e:
        print(f"Error confirming seat: {e}")
        return False

    try:
        combo.ticket.extras = combo.extras
        
        combo.ticket.purchase_product(state.usuario_logado)
        
        for extra in combo.extras:
            if hasattr(extra, 'purchase_product'):
                extra.purchase_product(state.usuario_logado)

        state.usuario_logado.add_booking(combo.ticket)
        
        movie.total_tickets_sold += 1
        movie.total_revenue += combo.total_price

        event_bus.publish(PAYMENT_SUCCESS, {
            "user": state.usuario_logado,
            "amount": combo.total_price,
            "movie": movie.name,
            "time": showtime.time,
            "seat": seat.row_and_number
        })

        event_bus.publish(BOOKING_CONFIRMED, {
            "user": state.usuario_logado,
            "movie": movie.name,
            "time": showtime.time,
            "seat": seat.row_and_number
        })

        print("\nPurchase completed successfully!")
        combo.ticket.generate_qr_code()
        return True
        
    except (BookingException, PaymentException, CouponException) as e:
        print(f"Error finalizing purchase: {e}")
        return False


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
            
        status = assento_selecionado.get_status()
        print(f"Seat {escolha_assento} status: {status}")
        if status != "Available":
            print("Seat not available. Showing history:")
            assento_selecionado.get_history()
            continue
        
        try:
            if assento_selecionado.temp_reserve(state.usuario_logado, minutes=10):
                print(f"Seat {assento_selecionado.row_and_number} temporarily reserved until {assento_selecionado.reservation_expiry}.")
                break
            else:
                print("Could not reserve seat. Please try another one.")
        except SeatAlreadyReservedException as e:
            print(f"Reservation error: {e}")
            continue

    while True:
        tipo_ingresso_input = input("Enter the ticket type (Standard, Student, VIP): ").strip().lower()
        if tipo_ingresso_input in ["standard", "student", "vip"]:
            tipo_ingresso = {"standard": TICKET_STANDARD, "student": TICKET_STUDENT, "vip": TICKET_VIP}[tipo_ingresso_input]
            break
        else:
            print("Invalid ticket type. Please choose from Standard, Student, or VIP.")
    
    builder = ComboBuilder(state.usuario_logado)
    builder.add_ticket(tipo_ingresso, assento_selecionado, showtime_selecionado)
    
    if not handle_combo_addition(builder):
        assento_selecionado.release(state.usuario_logado)
        return
    
    try:
        if assento_selecionado.check_expiry():
            print("Your temporary reservation expired. Seat released.")
            return
    except ReservationExpiredException as e:
        try:
            assento_selecionado.release(state.usuario_logado)
        except Exception:
            pass
        print(f"Reservation expired: {e}. Seat released.")
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
    except (BookingException, PaymentException, CouponException) as e:
        print(f"Error building combo: {e}")
        assento_selecionado.release(state.usuario_logado)
        return

    pagar = input(f"Proceed with payment of R$ {combo.total_price:.2f}? \n[1] Yes\n[2] No\n ").strip()
    if pagar == "1":
        try:
            if assento_selecionado.check_expiry():
                print("Your temporary reservation has expired. Please start over.")
                return
        except ReservationExpiredException as e:
            try:
                assento_selecionado.release(state.usuario_logado)
            except Exception:
                pass
            print(f"Reservation expired: {e}. Please start over.")
            return
            
        if payment(combo.total_price):
            cmd = PurchaseComboCommand(combo, movie, showtime_selecionado, assento_selecionado, state.usuario_logado, finalize_purchase)
            try:
                cinema_system.invoker.execute_command(cmd)
                if not getattr(cmd, "executed", False):
                    print("Purchase failed. Seat will be released.")
                    assento_selecionado.release(state.usuario_logado)
            except (BookingException, PaymentException, CouponException) as e:
                print(f"Purchase error: {e}. Seat will be released.")
                try:
                    assento_selecionado.release(state.usuario_logado)
                    print(f"Seat {assento_selecionado.row_and_number} released.")
                except (BookingException, SeatNotAvailableException) as e2:
                    print(f"Warning: Could not release seat: {e2}")
        else:
            print("Payment failed. Releasing seat.")
            assento_selecionado.release(state.usuario_logado)
    else:
        print("Purchase canceled. Releasing seat.")
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

            rating = int(input("Your rating (1 to 5): "))
            if rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5")
            comment = input("Your comment: ")
            
            movie_to_review.add_review(rating, comment)
            print("Review successfully submitted!")
            return

        except (ValueError, IndexError, TypeError) as e:
            print(f"Invalid option: {e}. Please try again.")


def cancelar_compra():
    active_bookings = [t for t in state.usuario_logado.booking_history if not getattr(t, "cancelled", False)]
    
    if not active_bookings:
        print("You have no active bookings to cancel.")
        return False

    print("\n Your Active Bookings:")
    print("=" * 50)
    for i, ticket in enumerate(active_bookings, 1):
        try:
            movie_name = getattr(getattr(getattr(ticket, "showtime", None), "movie", None), "name", "N/A")
            seat = getattr(getattr(ticket, "seat", None), "row_and_number", "N/A")
            print(f"[{i}] {getattr(ticket, 'name', 'TICKET').upper()} - {movie_name} (Seat {seat})")
        except (AttributeError, TypeError):
            print(f"[{i}] {getattr(ticket, 'name', 'TICKET').upper()}")
    
    escolha = input("Enter the number of the booking you want to cancel (or '0' to go back): ").strip()
    if escolha == "0":
        return False
    
    try:
        index = int(escolha) - 1
        if not (0 <= index < len(active_bookings)):
            raise IndexError("Invalid booking number.")
    except (ValueError, TypeError):
        print("Invalid input. Please enter a number.")
        return False
    except IndexError as e:
        print(f"Error: {e}")
        return False

    ticket = active_bookings[index]
    seat = getattr(ticket, "seat", None)
    showtime = getattr(ticket, "showtime", None)
    movie = getattr(showtime, "movie", None)

    try:
        total_refund = float(getattr(ticket, "price", 0.0) or 0.0)
    except (ValueError, TypeError):
        total_refund = 0.0
        
    for extra in getattr(ticket, "extras", []) or []:
        try:
            total_refund += float(getattr(extra, "price", 0.0) or 0.0)
        except (ValueError, TypeError):
            pass

    print(f"Canceling ticket: {getattr(ticket, 'name', 'TICKET')} - R$ {float(getattr(ticket, 'price', 0.0) or 0.0):.2f}")

    for extra in getattr(ticket, "extras", []) or []:
        if hasattr(extra, "cancel_purchase"):
            try:
                cinema_system.invoker.execute_command(CancelProductCommand(extra, state.usuario_logado))
            except (BookingException, PaymentException, CouponException) as e:
                print(f"Warning: Failed to cancel extra '{extra.name}': {e}")

    if seat:
        seat_id = getattr(seat, "row_and_number", "N/A")
        print(f"Seat {seat_id} current status: {seat.get_status()}")
    else:
        seat_id = "N/A"

    if hasattr(ticket, "cancel_purchase"):
        try:
            cmd_ticket = CancelProductCommand(ticket, state.usuario_logado)
            cinema_system.invoker.execute_command(cmd_ticket)
        except (BookingException, PaymentException, CouponException) as e:
            print(f"Warning: Failed to cancel ticket: {e}")

    if seat and hasattr(seat, "release"):
        try:
            seat.release(state.usuario_logado)
        except (BookingException, SeatNotAvailableException) as e:
            print(f"Warning: Could not release seat: {e}")

    if movie:
        try:
            movie.total_tickets_sold = max(0, getattr(movie, "total_tickets_sold", 0) - 1)
            movie.total_revenue = max(0.0, getattr(movie, "total_revenue", 0.0) - total_refund)
        except (ValueError, TypeError):
            pass

    if hasattr(state.usuario_logado, "cancel_booking"):
        state.usuario_logado.cancel_booking(ticket)

    try:
        event_bus.publish(BOOKING_CANCELLED, {
            "user": state.usuario_logado,
            "movie": getattr(movie, "name", None),
            "time": getattr(showtime, "time", None),
            "seat": seat_id,
            "refund": total_refund
        })
        event_bus.publish(PAYMENT_REFUNDED, {
            "user": state.usuario_logado,
            "amount": total_refund,
            "seat": seat_id
        })
    except NotificationDeliveryException as e:
        print(f"Warning: Notification failed: {e}")

    print(f"\nBooking and associated extras cancelled successfully! R$ {total_refund:.2f} will be refunded.")
    return True
