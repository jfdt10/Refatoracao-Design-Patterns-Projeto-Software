import sys
from ui import menu_principal, inicializar_dados
from exceptions import BookingException, PaymentException, CouponException

if __name__ == "__main__":
    try:
        inicializar_dados()
        menu_principal()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user.")
    except (BookingException, PaymentException, CouponException) as e:
        print(f"Error: {e}")
    finally:
        print("See you next time!")
        sys.exit(0)