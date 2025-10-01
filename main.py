import sys
from ui import menu_principal, inicializar_dados

if __name__ == "__main__":
    inicializar_dados()
    
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\nPrograma encerrado pelo usuário. Até mais!")
        sys.exit(0)