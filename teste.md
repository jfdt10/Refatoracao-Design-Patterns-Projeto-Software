Tratamento de Exceções:
Foi feito o tratamento de exceções com a criação de arquivo exceptions.py que centralizam as principais exceções customizadas da seguinte forma:

1. Exceções de Validação

Descrição: herdam de ValueError e representam erros de validação de entrada (e‑mail, telefone, CPF, senha).

Classes principais: InvalidEmailException, InvalidPhoneException, InvalidCPFException, InvalidPasswordException.

Onde são usadas: validações em ui.py (por exemplo, no fluxo registrar()) e nos setters da classe USER em models.py.

Exemplo de captura em registrar():

Python

try:
    registrar()
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
Exemplo (setters) em USER:

Python

@property
def email(self):
    return self.__email

@email.setter
def email(self, new_email):
    if not isinstance(new_email, str):
        raise TypeError("Email must be a string.")
    try:
        validate_email(new_email)
        self.__email = new_email.strip()
    except InvalidEmailException:
        raise

@property
def password(self):
    return self.__password

@password.setter
def password(self, new_password):
    if not isinstance(new_password, str):
        raise TypeError("Password must be a string.")
    if len(new_password) < 5:
        raise InvalidPasswordException("Password must have at least 5 characters.")
    self.__password = new_password

@property
def phone(self):
    return self.__phone

@phone.setter
def phone(self, new_phone):
    if new_phone is None:
        self.__phone = None
        return
    if not isinstance(new_phone, str):
        raise TypeError("Phone must be a string.")
    if new_phone.strip().startswith("()"):
        raise InvalidPhoneException(new_phone, "Invalid phone (empty area code).")

@property
def cpf(self):
    return self._cpf

@cpf.setter
def cpf(self, new_cpf):
    if new_cpf is None:
        self._cpf = None
        return
    if not isinstance(new_cpf, str):
        raise TypeError("CPF must be a string.")
    try:
        validate_cpf(new_cpf)
        self._cpf = re.sub(r"\D", "", new_cpf)
    except InvalidCPFException:
        raise
2. Exceções de Reserva

Descrição: herdam de RuntimeError e representam erros relacionados ao fluxo de reserva/confirmação de assentos.

Classes principais: BookingException, SeatAlreadyReservedException, ReservationExpiredException, SeatNotAvailableException.

Onde são usadas: states.py (padrão State: AvailableState, TemporaryReservedState, ConfirmedState), commands.py (padrão Command: CommandInvoker, PurchaseProductCommand, CancelProductCommand, PurchaseComboCommand), ui.py (funções como finalize_purchase, comprar_ingresso, cancelar_compra) e main.py (fluxo principal).

Exemplos (trechos simplificados):

Python

class AvailableState(SeatState):
    # ...
    def confirm(self, seat):
        raise SeatNotAvailableException(seat.row_and_number, "confirm")


class TemporaryReservedState(SeatState):
    # ...
    def check_expiry(self, seat):
        if seat.reservation_expiry and datetime.now() >= seat.reservation_expiry:
            expiry_time = seat.reservation_expiry
            self.release(seat)
            raise ReservationExpiredException(seat.row_and_number, expiry_time)
        return False


class ConfirmedState(SeatState):
    # ...
    def reserve(self, seat, user, minutes=0):
        raise SeatAlreadyReservedException(seat.row_and_number, "Confirmed")
Python

class CommandInvoker:
    # ...
    def execute_command(self, command: Command):
        try:
            command.execute()
            if getattr(command, "executed", False):
                self._history.append(command)
        except (BookingException, PaymentException, CouponException) as e:
            print(f"[COMMAND ERROR] Business logic error during execution: {e}")

    def undo_last(self):
        try:
            command.undo()
        except (BookingException, PaymentException, CouponException) as e:
            print(f"[COMMAND ERROR] Business logic error during undo: {e}")
Python

class PurchaseProductCommand(Command):
    # ...
    def execute(self):
        try:
            self.product.purchase_product(self.user)
            self.executed = True
        except (BookingException, PaymentException, CouponException) as e:
            print(f"PurchaseProductCommand execute error: {e}")
            self.executed = False
            raise

    def undo(self):
        try:
            self.product.cancel_purchase(self.user)
            self.executed = False
        except (BookingException, PaymentException, CouponException) as e:
            print(f"PurchaseProductCommand undo error: {e}")
Python

class CancelProductCommand(Command):
    # ...
    def execute(self):
        try:
            self.product.cancel_purchase(self.user)
            self.executed = True
        except (BookingException, PaymentException, CouponException) as e:
            print(f"CancelProductCommand execute error: {e}")
            self.executed = False
            raise

    def undo(self):
        try:
            self.product.purchase_product(self.user)
            self.executed = False
        except (BookingException, PaymentException, CouponException) as e:
            print(f"CancelProductCommand undo error: {e}")
Python

class PurchaseComboCommand(Command):
    # ...
    def execute(self):
        try:
            for extra in extras:
                cmd = PurchaseProductCommand(extra, self.user)
                try:
                    cmd.execute()
                    if not getattr(cmd, "executed", False):
                        print("PurchaseComboCommand: failed to purchase an extra. Rolling back extras...")
                        for done in reversed(self._sub_commands):
                            try:
                                done.undo()
                            except Exception:
                                pass
                        return
                    self._sub_commands.append(cmd)
                except (BookingException, PaymentException, CouponException) as e:
                    print(f"PurchaseComboCommand: failed to purchase extra: {e}. Rolling back...")
                    for done in reversed(self._sub_commands):
                        try:
                            done.undo()
                        except Exception:
                            pass
                    raise

            try:
                result = None
                try:
                    result = self.finalize_fn(self.combo, self.movie, self.showtime, self.seat)
                except TypeError:
                    result = self.finalize_fn(self.combo, self.movie, self.showtime)

                if result is False:
                    raise BookingException("finalize function indicated failure")
            except (BookingException, PaymentException, CouponException) as e:
                print(f"PurchaseComboCommand: finalize failed: {e}. Rolling back extras...")
                for done in reversed(self._sub_commands):
                    try:
                        done.undo()
                    except Exception:
                        pass
                raise

            self.executed = True

        except (BookingException, PaymentException, CouponException) as e:
            print(f"PurchaseComboCommand execute error: {e}")
            for done in reversed(self._sub_commands):
                try:
                    done.undo()
                except Exception:
                    pass
            self.executed = False
            raise
Trechos do fluxo de UI (exemplos simplificados):

Python

def finalize_purchase(combo, movie, showtime, seat):
    # ...
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
    except (BookingException, PaymentException, CouponException) as e:
        print(f"Error finalizing purchase: {e}")
        return False
Python

def comprar_ingresso(movie):
    # ...
    try:
        if assento_selecionado.temp_reserve(state.usuario_logado, minutes=10):
            print(f"Seat {assento_selecionado.row_and_number} temporarily reserved until {assento_selecionado.reservation_expiry}.")
        else:
            print("Could not reserve seat. Please try another one.")
    except SeatAlreadyReservedException as e:
        print(f"Reservation error: {e}")
        return

    try:
        combo = builder.build()
        print("\nPurchase Summary:")
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

def cancelar_compra():
    # ...
    try:
        cinema_system.invoker.execute_command(CancelProductCommand(extra, state.usuario_logado))
    except (BookingException, PaymentException, CouponException) as e:
        print(f"Warning: Failed to cancel extra '{extra.name}': {e}")

    try:
        cmd_ticket = CancelProductCommand(ticket, state.usuario_logado)
        cinema_system.invoker.execute_command(cmd_ticket)
    except (BookingException, PaymentException, CouponException) as e:
        print(f"Warning: Failed to cancel ticket: {e}")
Trechos do fluxo de main.