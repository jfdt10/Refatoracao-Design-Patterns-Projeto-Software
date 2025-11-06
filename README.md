# MovieTicketSystem

**Status:** ✔️ **Projeto Finalizado — v1.0** (Concluído em 04/11/2025)

**[Português](#português)** | **[English](#english)**

---

<a name="português"></a>
## 🇧🇷 Versão em Português

### Sobre o Projeto

Sistema de venda de ingressos de cinema e combos de pipoca, desenvolvido em Python. Simula uma experiência completa de usuário através de interface de linha de comando, utilizando princípios de Programação Orientada a Objetos (POO) e Padrões de Projeto.

### Funcionalidades Implementadas

**Funcionalidades Core:**
- Listagem de Cinemas e Filmes
- Seleção e Reserva de Assentos
- Processamento de Pagamentos (Crédito, Débito, PIX)
- Gerenciamento de Contas de Usuário
- Histórico de Reservas e Cancelamentos
- Promoções e Descontos
- Disponibilidade de Assentos em Tempo Real
- Avaliações e Comentários de Clientes
- Combos de Ingressos e Pipoca
- Sessões e Horários

**Funcionalidades Avançadas (Refatoração):**
- Sistema de Notificações e Alertas (Email, SMS, Push)
- Geração de Ingressos Móveis com QR Code
- Painel Administrativo
- Sistema de Analytics

---

### Padrões de Projeto Implementados

Este projeto implementa 10 padrões de design divididos em 3 categorias:

#### Padrões Criacionais (Creational Design Patterns)

**1. Singleton**
- **Onde foi usado:** Classes `NotificationService` e `PromotionManager` em `services.py`, utilizando Metaclasse `MetaSingleton` em `utils.py`
- **Justificativa:** Serviços como notificação e gerenciador de promoções devem ser únicos na aplicação. Múltiplas instâncias causariam inconsistência de dados
- **Benefícios:** Garante instância única, controle centralizado de recursos, consistência de dados em todo o sistema

**2. Builder**
- **Onde foi usado:** Classe `ComboBuilder` em `builders.py` para criar combos de compra complexos
- **Justificativa:** A criação de combos depende de múltiplos fatores (tipo de ingresso, itens extras, tamanhos, cupons). Builder permite construção passo-a-passo
- **Benefícios:** Interface fluente (`.add_ticket().add_popcorn()`), evita construtores com muitos parâmetros, código limpo e legível

**3. Factory Method**
- **Onde foi usado:** Função `create_ticket_with_factory` e métodos nas fábricas concretas (`StandardFactory`, etc.)
- **Justificativa:** Elimina condicionais `if/elif/else` para instanciar diferentes tipos de produtos, delegando à fábrica especializada
- **Benefícios:** Desacoplamento entre UI e classes concretas, facilita adição de novos tipos de produtos

**4. Abstract Factory**
- **Onde foi usado:** Interface `AbstractFactory` em `factories.py` com implementações `StandardFactory`, `StudentFactory`, `VIPFactory`
- **Justificativa:** Garante que todos os produtos criados (ingresso, pipoca, refrigerante) sigam as mesmas regras de precificação
- **Benefícios:** Consistência entre produtos relacionados, encapsula regras de negócio por tema, extremamente extensível

---

#### Padrões Comportamentais (Behavioral Design Patterns)

**1. State**
- **Onde foi usado:** Classe `SEAT` em `models.py` com estados concretos `AvailableState`, `TemporaryReservedState`, `ConfirmedState` em `states.py`
- **Justificativa:** Assentos têm comportamentos diferentes dependendo do estado. Sem State, seria necessário múltiplos `if/elif` na classe SEAT
- **Benefícios:** Encapsula lógica de cada estado separadamente, transições explícitas e seguras, fácil adicionar novos estados

**2. Observer**
- **Onde foi usado:** Sistema de eventos `EventBus` em `observer.py` com `NotificationObserver` e `AnalyticsObserver`
- **Justificativa:** Ações precisam disparar múltiplas reações independentes (notificações, analytics, UI) sem acoplamento
- **Benefícios:** Desacoplamento total entre emissor e receptores, novos observadores sem modificar código existente

**3. Command**
- **Onde foi usado:** Classes `CommandInvoker`, `PurchaseProductCommand`, `CancelProductCommand`, `PurchaseComboCommand` em `commands.py`
- **Justificativa:** Operações complexas podem falhar (pagamento rejeitado), exigindo rollback. Comandos compostos garantem atomicidade
- **Benefícios:** Suporte a undo/redo, histórico de operações, atomicidade em comandos compostos, facilita auditoria

---

#### Padrões Estruturais (Structural Design Patterns)

**1. Adapter**
- **Onde foi usado:** Classes `EmailNotificationAdapter`, `SMSNotificationAdapter`, `PushNotificationAdapter` em `adapter.py`
- **Justificativa:** Serviços externos têm interfaces incompatíveis (`send_email()`, `send_sms()`, `send_push()`). Adapter unifica em interface comum
- **Benefícios:** Tratamento homogêneo de canais, fácil adicionar novos canais, histórico por canal, isolamento de mudanças externas

**2. Decorator**
- **Onde foi usado:** Classe `ProductDecorator` com implementações `SpecialPackagingDecorator`, `ExtraItemDecorator`, `GiftWrapDecorator` em `decorator.py`
- **Justificativa:** Produtos podem ter múltiplas personalizações. Herança geraria explosão de subclasses
- **Benefícios:** Adiciona funcionalidades sem modificar classes originais, composição flexível em runtime, mantém polimorfismo

**3. Facade**
- **Onde foi usado:** Classe `CinemaSystemFacade` em `facade.py` unificando 5 subsistemas complexos
- **Justificativa:** Comprar ingresso envolve coordenar subsistemas de reserva, combo, cupom, pagamento, comando e eventos
- **Benefícios:** Interface simplificada, reduz linhas de código na UI, transações atômicas com rollback, facilita manutenção

---

### Tratamento de Exceções:

Foi feito o tratamento de exceções com a criação de arquivo **exceptions.py** que centralizam as principais exceções customizadas da seguinte forma:

**1. Exceções de Validação:**

- Foi utilizada herança de ValueError para caracterizar essas exceções personalizadas criando 4 classes: `InvalidEmailException`,`InvalidPhoneException`, `InvalidCPFException`, `InvalidPasswordException`, seus usos se deram em arquivos como ui.py que centraliza a lógica dos menus a fim de validar na função de `registrar()` e em `models.py` nos setters das classe `USER` :


```python
def registrar():
    #......
    try:
        pass
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
```

```python
@email.setter
def email(self, new_email):
    if not isinstance(new_email, str):
        raise TypeError("Email must be a string.")
    try:
        validate_email(new_email)
        self.__email = new_email.strip()
    except InvalidEmailException:
        raise

@password.setter
def password(self, new_password):
    if not isinstance(new_password, str):
        raise TypeError("Password must be a string.")
    if len(new_password) < 5:
        raise InvalidPasswordException("Password must have at least 5 characters.")
    self.__password = new_password


@phone.setter
def phone(self, new_phone):
    if new_phone is None:
        self.__phone = None
        return
    if not isinstance(new_phone, str):
        raise TypeError("Phone must be a string.")
    if new_phone.strip().startswith("()"):
        raise InvalidPhoneException(new_phone, "Invalid phone (empty area code).")

@cpf.setter
def cpf(self, new_cpf):
    if new_cpf is None:
        self._cpf = None
        return
    
    if not isinstance(new_cpf, str):
        raise TypeError("CPF must be a string.")
    try:
        validate_cpf(new_cpf)
        self._cpf = re.sub(r'\D', '', new_cpf)
    except InvalidCPFException:
        raise
```
**2. Exceções de Reserva:**
- Foi utilizada herança de RunTimeError para caracterizar essas exceções personalizadas de Reserva criando 4 classes(1 que herda diretamente de RuntimeError e outras que herdam dessa): `BookingException`,`SeatAlreadyReservedException`, `ReservationExpiredException`, `SeatNotAvailableException`, seus usos se deram em arquivos como `states.py` arquivo que faz o padrão de projeto STATE usando nas classes `AvailableState`,`TemporaryReservedState` e `ConfirmedState`, no arquivo `commands.py` que implementa o padrão de projeto COMMAND nas classes `CommandInvoker` `PurchaseProductCommand` `CancelProductCommand` `PurchaseComboCommand`, além de `ui.py` em funções como ``finalize_purchase`, `comprar_ingresso()`, `cancelar_compra()` e no arquivo `main.py` na inicialização dos dados do programa:


```python
class AvailableState(SeatState):
    #...
    def confirm(self, seat):
        raise SeatNotAvailableException(seat.row_and_number, "confirm")

class TemporaryReservedState(SeatState):
    #...
    def check_expiry(self, seat):
        if seat.reservation_expiry and datetime.now() >= seat.reservation_expiry:
            expiry_time = seat.reservation_expiry
            self.release(seat)
            raise ReservationExpiredException(seat.row_and_number, expiry_time)
        return False

class ConfirmedState(SeatState):
    #...
    def reserve(self, seat, user, minutes=0):
        raise SeatAlreadyReservedException(
            seat.row_and_number,
            "Confirmed"
        )
```


```python
class CommandInvoker:
    ###...
    def execute_command(self, command: Command):
        #...
        try:
            command.execute()
            if getattr(command, "executed", False):
                self._history.append(command)
        except (BookingException, PaymentException, CouponException) as e:
            print(f"[COMMAND ERROR] Business logic error during execution: {e}")

    def undo_last(self):
        #...
        try:
            command.undo()
        except (BookingException, PaymentException, CouponException) as e:
            print(f"[COMMAND ERROR] Business logic error during undo: {e}")
```

```python
class PurchaseProductCommand(Command):
    #...
    def execute(self):
        #...
        try:
            self.product.purchase_product(self.user)
            self.executed = True
        except (BookingException, PaymentException, CouponException) as e:
            print(f"PurchaseProductCommand execute error: {e}")
            self.executed = False
            raise

    def undo(self):
        #...
        try:
            self.product.cancel_purchase(self.user)
            self.executed = False
        except (BookingException, PaymentException, CouponException) as e:
            print(f"PurchaseProductCommand undo error: {e}")
```

```python

class CancelProductCommand(Command):
    #...
    def execute(self):
        #...
        try:
            self.product.cancel_purchase(self.user)
            self.executed = True
        except (BookingException, PaymentException, CouponException) as e:
            print(f"CancelProductCommand execute error: {e}")
            self.executed = False
            raise

    def undo(self):
        #...
        try:
            self.product.purchase_product(self.user)
            self.executed = False
        except (BookingException, PaymentException, CouponException) as e:
            print(f"CancelProductCommand undo error: {e}")
```

```python
class PurchaseComboCommand(Command):
    #...
    def execute(self):
        #...
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
                    try:
                        result = self.finalize_fn(self.combo, self.movie, self.showtime)
                    except Exception:
                        raise
                
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
```

```python
    def finalize_purchase(combo, movie, showtime, seat):
    #...
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
    #...

    except (BookingException, PaymentException, CouponException) as e:
        print(f"Error finalizing purchase: {e}")
        return False

def comprar_ingresso(movie):
    #...
    try:
        if assento_selecionado.temp_reserve(state.usuario_logado, minutes=10):
            print(f"Seat {assento_selecionado.row_and_number} temporarily reserved until {assento_selecionado.reservation_expiry}.")
            break
        else:
            print("Could not reserve seat. Please try another one.")
    except SeatAlreadyReservedException as e:
        print(f"Reservation error: {e}")
        continue

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
    #...
    try:
        cinema_system.invoker.execute_command(CancelProductCommand(extra, state.usuario_logado))
    except (BookingException, PaymentException, CouponException) as e:
        print(f"Warning: Failed to cancel extra '{extra.name}': {e}")
    #...
    try:
        cmd_ticket = CancelProductCommand(ticket, state.usuario_logado)
        cinema_system.invoker.execute_command(cmd_ticket)
    except (BookingException, PaymentException, CouponException) as e:
        print(f"Warning: Failed to cancel ticket: {e}")
```


```python
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
```

**3. Exceções de Pagamento:**
- Foi utilizada herança de RunTimeError para caracterizar essas exceções personalizadas de Pagamento criando 4 classes(1 que herda diretamente de RuntimeError e outras que herdam dessa): `PaymentException`,`PaymentLimitExceededException`, `PaymentProcessingException`, `InvalidPaymentMethodException`, seus usos se deram em arquivos como `Facade.py` arquivo que faz o padrão de projeto FACADE usando nas classes `PaymentSubsystem`,`CinemaSystemFacade`, e em `commands.py` que implementa o padrão de projeto COMMAND nas classes `CommandInvoker` `PurchaseProductCommand` `CancelProductCommand` `PurchaseComboCommand`, além de `ui.py` em funções como `payment()``finalize_purchase()`, `comprar_ingresso()`, `cancelar_compra()` e no arquivo `main.py` na inicialização dos dados do programa:


```python
class PaymentSubsystem:
    #...

    def process_payment(self, method: str, amount: float, user):
        #...

        if method not in method_mapping:
            raise InvalidPaymentMethodException(
                method, valid_methods=["Credit", "Debit", "PIX"]
            )
        
        method_key = method_mapping[method]
        limit = PAYMENT_LIMITS[method_key]

        if amount > limit:
            raise PaymentLimitExceededException(
                payment_method=method_key.upper(),
                amount=amount,
                limit=limit
            )
        if random.random() < PAYMENT_ERROR_RATE:
            raise PaymentProcessingException(
                "Error connecting to payment server",
                details="Please try again in a few seconds"
            )

class CinemaSystemFacade:
    #...
    try:
        #...
    except (PaymentLimitExceededException, PaymentProcessingException, 
            InvalidPaymentMethodException) as e:
        result["message"] = str(e)
        self.bookings.release_seat(seat, user)
        return result
```


```python
class CommandInvoker:
    ###...
    def execute_command(self, command: Command):
        #...
        try:
            command.execute()
            if getattr(command, "executed", False):
                self._history.append(command)
        except (BookingException, PaymentException, CouponException) as e:
            print(f"[COMMAND ERROR] Business logic error during execution: {e}")

    def undo_last(self):
        #...
        try:
            command.undo()
        except (BookingException, PaymentException, CouponException) as e:
            print(f"[COMMAND ERROR] Business logic error during undo: {e}")
```

```python
class PurchaseProductCommand(Command):
    #...
    def execute(self):
        #...
        try:
            self.product.purchase_product(self.user)
            self.executed = True
        except (BookingException, PaymentException, CouponException) as e:
            print(f"PurchaseProductCommand execute error: {e}")
            self.executed = False
            raise

    def undo(self):
        #...
        try:
            self.product.cancel_purchase(self.user)
            self.executed = False
        except (BookingException, PaymentException, CouponException) as e:
            print(f"PurchaseProductCommand undo error: {e}")
```

```python
class CancelProductCommand(Command):
    #...
    def execute(self):
        #...
        try:
            self.product.cancel_purchase(self.user)
            self.executed = True
        except (BookingException, PaymentException, CouponException) as e:
            print(f"CancelProductCommand execute error: {e}")
            self.executed = False
            raise

    def undo(self):
        #...
        try:
            self.product.purchase_product(self.user)
            self.executed = False
        except (BookingException, PaymentException, CouponException) as e:
            print(f"CancelProductCommand undo error: {e}")
```

```python
class PurchaseComboCommand(Command):
    # ...
    def execute(self):
        # ...
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
                    try:
                        result = self.finalize_fn(self.combo, self.movie, self.showtime)
                    except Exception:
                        raise
                
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
```
```python
def payment(valor):
    try:
        #...
    except (PaymentLimitExceededException, PaymentProcessingException, InvalidPaymentMethodException) as e:
        print(f"Payment error: {e}")
        retry = input("Try again? [Y/N]: ").strip().upper()
        if retry != "Y":
            return False
    else:
        print("Invalid credit card number. Please try again.")
```


```python
def finalize_purchase(combo, movie, showtime, seat):
    #...
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
    #...

    except (BookingException, PaymentException, CouponException) as e:
        print(f"Error finalizing purchase: {e}")
        return False

def comprar_ingresso(movie):
    #...
    try:
        if assento_selecionado.temp_reserve(state.usuario_logado, minutes=10):
            print(f"Seat {assento_selecionado.row_and_number} temporarily reserved until {assento_selecionado.reservation_expiry}.")
            break
        else:
            print("Could not reserve seat. Please try another one.")
    except SeatAlreadyReservedException as e:
        print(f"Reservation error: {e}")
        continue

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
    #...
    try:
        cinema_system.invoker.execute_command(CancelProductCommand(extra, state.usuario_logado))
    except (BookingException, PaymentException, CouponException) as e:
        print(f"Warning: Failed to cancel extra '{extra.name}': {e}")
    #...
    try:
        cmd_ticket = CancelProductCommand(ticket, state.usuario_logado)
        cinema_system.invoker.execute_command(cmd_ticket)
    except (BookingException, PaymentException, CouponException) as e:
        print(f"Warning: Failed to cancel ticket: {e}")
```


```python
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
```

**4. Exceções de Cupom:**
- Foi utilizada herança de RunTimeError para caracterizar essas exceções personalizadas de Cupom criando 5 classes(1 que herda diretamente de RuntimeError e outras que herdam dessa): `CouponException`,`InvalidCouponException`, `CouponExpiredException`, `CouponUsageLimitException`e `MinimumPurchaseException` seus usos se deram em arquivos como `serivces.py` arquivo que faz o padrão de projeto Singleton usando nas classes `Coupon`, e em `commands.py` que implementa o padrão de projeto COMMAND nas classes `CommandInvoker` `PurchaseProductCommand` `CancelProductCommand` `PurchaseComboCommand`, além de `ui.py` em funções como `finalize_purchase()`, `comprar_ingresso()`, `cancelar_compra()` e no arquivo `main.py` na inicialização dos dados do programa:


```python
class Coupon:
    #...

    def is_valid(self, raise_exception=False):
        if not self.is_active:
            if raise_exception:
                raise InvalidCouponException(self.code, "Cupom está inativo")
            return False
            
        if self.valid_until and datetime.now() > self.valid_until:
            if raise_exception:
                raise CouponExpiredException(self.code, self.valid_until)
            return False
            
        if self.max_uses and self.uses_count >= self.max_uses:
            if raise_exception:
                raise CouponUsageLimitException(self.code, self.max_uses)
            return False
        return True

    def can_apply(self, total_amount, ticket_type=None, cinema_name=None, movie_name=None, user_type=None, raise_exception=False):
        if total_amount < self.min_purchase:
            if raise_exception:
                raise MinimumPurchaseException(self.code, self.min_purchase, total_amount)
            return False
            
        if hasattr(self, 'applicable_ticket_types') and self.applicable_ticket_types and ticket_type not in self.applicable_ticket_types:
            if raise_exception:
                raise InvalidCouponException(
                    self.code, 
                    f"Cupom não aplicável ao tipo de ingresso '{ticket_type}'"
                )
            return False
            
        if self.applicable_cinemas and cinema_name not in self.applicable_cinemas:
            if raise_exception:
                raise InvalidCouponException(
                    self.code,
                    f"Cupom não aplicável ao cinema '{cinema_name}'"
                )
            return False
            
        if self.applicable_movies and movie_name not in self.applicable_movies:
            if raise_exception:
                raise InvalidCouponException(
                    self.code,
                    f"Cupom não aplicável ao filme '{movie_name}'"
                )
            return False
            
        if self.user_type and user_type != self.user_type:
            if raise_exception:
                raise InvalidCouponException(
                    self.code,
                    f"Cupom exclusivo para usuários do tipo '{self.user_type}'"
                )
            return False
            
        return True
    #...
```

```python
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
    #...
    try:
        cinema_system.invoker.execute_command(CancelProductCommand(extra, state.usuario_logado))
    except (BookingException, PaymentException, CouponException) as e:
        print(f"Warning: Failed to cancel extra '{extra.name}': {e}")
    #...
    try:
        cmd_ticket = CancelProductCommand(ticket, state.usuario_logado)
        cinema_system.invoker.execute_command(cmd_ticket)
    except (BookingException, PaymentException, CouponException) as e:
        print(f"Warning: Failed to cancel ticket: {e}")
```


```python
class CommandInvoker:
    ###...
    def execute_command(self, command: Command):
        #...
        try:
            command.execute()
            if getattr(command, "executed", False):
                self._history.append(command)
        except (BookingException, PaymentException, CouponException) as e:
            print(f"[COMMAND ERROR] Business logic error during execution: {e}")

    def undo_last(self):
        #...
        try:
            command.undo()
        except (BookingException, PaymentException, CouponException) as e:
            print(f"[COMMAND ERROR] Business logic error during undo: {e}")
```

```python
class PurchaseProductCommand(Command):
    #...
    def execute(self):
        #...
        try:
            self.product.purchase_product(self.user)
            self.executed = True
        except (BookingException, PaymentException, CouponException) as e:
            print(f"PurchaseProductCommand execute error: {e}")
            self.executed = False
            raise

    def undo(self):
        #...
        try:
            self.product.cancel_purchase(self.user)
            self.executed = False
        except (BookingException, PaymentException, CouponException) as e:
            print(f"PurchaseProductCommand undo error: {e}")
```

```python
class CancelProductCommand(Command):
    #...
    def execute(self):
        #...
        try:
            self.product.cancel_purchase(self.user)
            self.executed = True
        except (BookingException, PaymentException, CouponException) as e:
            print(f"CancelProductCommand execute error: {e}")
            self.executed = False
            raise
    def undo(self):
        #...
        try:
            self.product.purchase_product(self.user)
            self.executed = False
        except (BookingException, PaymentException, CouponException) as e:
            print(f"CancelProductCommand undo error: {e}")
```

```python
class PurchaseComboCommand(Command):
    # ...
    def execute(self):
        # ...
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
                    try:
                        result = self.finalize_fn(self.combo, self.movie, self.showtime)
                    except Exception:
                        raise
                
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
```

```python
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
```

**5. Exceções de Notificação:**
- Foi utilizada herança de RunTimeError para caracterizar essas exceções personalizadas de Cupom criando 3 classes(1 que herda diretamente de RuntimeError e outras que herdam dessa): `NotificationException`,`NotificationDeliveryException`, `InvalidNotificationChannelException` seus usos se deram em services.py que implementa Singleton de Funções de Notificações e em ui.py:

```python
class MultiChannelNotificationService(metaclass=MetaSingleton):
    #...
    for channel_name in channels:
        if channel_name not in self.channels:
            raise InvalidNotificationChannelException(
                channel_name, 
                list(self.channels.keys())
            )

    if failed_channels and len(failed_channels) == len(channels):
        raise NotificationDeliveryException(
            ", ".join(failed_channels),
            "Falha em todos os canais de notificação"
        )
```

```python
def add_movie_admin():
    #...
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
```

**6. Exceções de Autenticação:**
- Foi utilizada herança de RunTimeError para caracterizar essas exceções personalizadas de Cupom criando 4 classes(1 que herda diretamente de RuntimeError e outras que herdam dessa): `AuthenticationException`,`InvalidCredentialsException`, `UserNotFoundException`, `UnauthorizedAccessException` seus usos se deram em arquivo  `ui.py` em funções de admin e funções de processar login:


```python
def processar_login():
    #...
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


def add_showtime_admin():
    #...

    try:
        if "manage_movies" not in state.usuario_logado.permissions:
            raise UnauthorizedAccessException(
            state.usuario_logado.login if hasattr(state.usuario_logado, 'login') else "unknown",
            "manage_movies"
            )
    except UnauthorizedAccessException as e:
        print(f"Access denied: {e}")
        return
```

**7. Exceções Built-ins do Python:**
- Foi utilizado em diversos arquivos a exemplo de `ui.py`em função de `menu_notificacoes()` em `main.py`, `models.py` e outros como em propertys e setters de atributos da classe `USER`, entre outros.


```python
def menu_notifications():
    #...
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
```

```python
class USER:
    #...
    def cpf(self, new_cpf):
        if new_cpf is None:
            self._cpf = None
            return
        
        if not isinstance(new_cpf, str):
            raise TypeError("CPF must be a string.")
        try:
            validate_cpf(new_cpf)
            self._cpf = re.sub(r'\D', '', new_cpf)
        except InvalidCPFException:
            raise
```

```python
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
```

### Conceitos de POO Aplicados

O projeto foi construído sobre os pilares fundamentais da Programação Orientada a Objetos:

- **Herança e Classes Abstratas:** Classe `PRODUCT` é abstrata, define interface comum para `TICKET`, `POPCORN`, `DRINK`
- **Polimorfismo:** Métodos `purchase_product()`, `cancel_purchase()`, `promotion()` comportam-se diferentemente em cada subclasse
- **Encapsulamento:** Estados internos protegidos, acesso controlado via métodos públicos
- **Composição:** `CINEMA` contém `MOVIE`, que contém `SHOWTIME`, que contém `SEAT`
- **Abstração:** Interfaces abstratas definem contratos (`SeatState`, `Command`, `NotificationChannel`)

---

### Estrutura do Projeto

```
Refatoracao-Design-Patterns-Projeto-Software/
│
├── main.py                     # Ponto de entrada da aplicação
├── ui.py                       # Interface de linha de comando
├── models.py                   # Modelos de domínio (USER, CINEMA, MOVIE, SEAT)
├── products.py                 # Produtos (TICKET, POPCORN, DRINK, etc.)
├── exceptions.py               # Hierarquia de exceções personalizadas (20+ tipos)
│
├── Padrões Criacionais
│   ├── factories.py            # Abstract Factory & Factory Method
│   ├── builders.py             # Builder Pattern
│   └── services.py             # Singleton (NotificationService, PromotionManager)
│
├── Padrões Comportamentais
│   ├── states.py               # State Pattern
│   ├── observer.py             # Observer Pattern (EventBus)
│   └── commands.py             # Command Pattern
│
├── Padrões Estruturais
│   ├── adapter.py              # Adapter Pattern
│   ├── decorator.py            # Decorator Pattern
│   └── facade.py               # Facade Pattern
│
├── Utilitários
│   ├── utils.py                # MetaSingleton, constantes de eventos
│   └── state.py                # Estado global da aplicação
│
├── requirements.txt            # Dependências do projeto
├── README.md                   # Este arquivo
└── LICENSE                     # Licença MIT
```

---

### Como Executar

**Pré-requisitos:**
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

**Instalação:**

```bash
# Clone o repositório
git clone https://github.com/jfdt10/Refatoracao-Design-Patterns-Projeto-Software.git

# Navegue até o diretório
cd Refatoracao-Design-Patterns-Projeto-Software

# Instale as dependências
pip install -r requirements.txt

# Execute o programa
python main.py
```

**Dicas de Uso:**
- O programa roda no terminal com menus interativos
- Selecione assento, tipo de ingresso e forma de pagamento conforme instruções
- Sistema previne seleções duplicadas de assentos
- Cálculo automático de totais com aplicação de descontos
- Para sair, selecione a opção "Sair" no menu principal

---

### Contribuidores

| Nome | Papel | Contribuições |
|------|-------|--------------|
| Marcela Rocha Silva | Autora Original | Desenvolvimento inicial do sistema |
| Jean Felipe Duarte Tenório | Refatorador/Mantenedor | Implementação de Design Patterns, melhorias de arquitetura |

---

### Melhorias Futuras

**✔️ Concluído (v1.0):**
- Tratamento robusto de exceções (20+ exceções personalizadas, validações, handlers específicos)

**Planejado (v1.1+):**
- API REST com Flask/FastAPI
- Dashboard administrativo
- Relatórios e analytics avançados
- Integração com banco de dados real
- Autenticação e segurança (JWT, hashing)

---

### Licença

Este projeto está licenciado sob a MIT License - veja o arquivo LICENSE para detalhes.

---

<a name="english"></a>
## 🇺🇸 English Version

### About the Project

Cinema ticket and popcorn combo sales system, developed in Python. Simulates a complete user experience through command-line interface, using Object-Oriented Programming (OOP) principles and Design Patterns.

### Implemented Features

**Core Features:**
- Cinema and Movie Listings
- Seat Selection and Booking
- Payment Processing (Credit, Debit, PIX)
- User Account Management
- Booking History and Cancellations
- Promotions and Discounts
- Real-Time Seat Availability
- Customer Reviews and Ratings
- Ticket and Popcorn Combos
- Movie Sessions and Schedules

**Advanced Features (Refactoring):**
- Notification and Alert System (Email, SMS, Push)
- Mobile Ticket Generation with QR Code
- Admin Panel
- Analytics System

---

### Implemented Design Patterns

This project implements 10 design patterns divided into 3 categories:

#### Creational Design Patterns

**1. Singleton**
- **Where used:** `NotificationService` and `PromotionManager` classes in `services.py`, using `MetaSingleton` metaclass in `utils.py`
- **Rationale:** Services like notification and promotion manager must be unique in the application. Multiple instances would cause data inconsistency
- **Benefits:** Ensures single instance, centralized resource control, data consistency across the system

**2. Builder**
- **Where used:** `ComboBuilder` class in `builders.py` to create complex purchase combos
- **Rationale:** Combo creation depends on multiple factors (ticket type, extra items, sizes, coupons). Builder allows step-by-step construction
- **Benefits:** Fluent interface (`.add_ticket().add_popcorn()`), avoids constructors with many parameters, clean and readable code

**3. Factory Method**
- **Where used:** `create_ticket_with_factory` function and methods in concrete factories (`StandardFactory`, etc.)
- **Rationale:** Eliminates `if/elif/else` conditionals to instantiate different product types, delegating to specialized factory
- **Benefits:** Decoupling between UI and concrete classes, facilitates adding new product types

**4. Abstract Factory**
- **Where used:** `AbstractFactory` interface in `factories.py` with `StandardFactory`, `StudentFactory`, `VIPFactory` implementations
- **Rationale:** Ensures all created products (ticket, popcorn, soda) follow the same pricing rules
- **Benefits:** Consistency among related products, encapsulates business rules by theme, extremely extensible

---

#### Behavioral Design Patterns

**1. State**
- **Where used:** `SEAT` class in `models.py` with concrete states `AvailableState`, `TemporaryReservedState`, `ConfirmedState` in `states.py`
- **Rationale:** Seats have different behaviors depending on state. Without State, multiple `if/elif` would be needed in SEAT class
- **Benefits:** Encapsulates logic of each state separately, explicit and safe transitions, easy to add new states

**2. Observer**
- **Where used:** `EventBus` event system in `observer.py` with `NotificationObserver` and `AnalyticsObserver`
- **Rationale:** Actions need to trigger multiple independent reactions (notifications, analytics, UI) without coupling
- **Benefits:** Total decoupling between sender and receivers, new observers without modifying existing code

**3. Command**
- **Where used:** `CommandInvoker`, `PurchaseProductCommand`, `CancelProductCommand`, `PurchaseComboCommand` classes in `commands.py`
- **Rationale:** Complex operations can fail (rejected payment), requiring rollback. Composite commands ensure atomicity
- **Benefits:** Undo/redo support, operation history, atomicity in composite commands, facilitates auditing

---

#### Structural Design Patterns

**1. Adapter**
- **Where used:** `EmailNotificationAdapter`, `SMSNotificationAdapter`, `PushNotificationAdapter` classes in `adapter.py`
- **Rationale:** External services have incompatible interfaces (`send_email()`, `send_sms()`, `send_push()`). Adapter unifies into common interface
- **Benefits:** Homogeneous channel treatment, easy to add new channels, history per channel, isolation from external changes

**2. Decorator**
- **Where used:** `ProductDecorator` class with `SpecialPackagingDecorator`, `ExtraItemDecorator`, `GiftWrapDecorator` implementations in `decorator.py`
- **Rationale:** Products can have multiple customizations. Inheritance would generate explosion of subclasses
- **Benefits:** Adds functionality without modifying original classes, flexible composition at runtime, maintains polymorphism

**3. Facade**
- **Where used:** `CinemaSystemFacade` class in `facade.py` unifying 5 complex subsystems
- **Rationale:** Buying a ticket involves coordinating subsystems for booking, combo, coupon, payment, command and events
- **Benefits:** Simplified interface, reduces UI code lines, atomic transactions with rollback, facilitates maintenance

---

### Applied OOP Concepts

The project was built on fundamental Object-Oriented Programming pillars:

- **Inheritance and Abstract Classes:** `PRODUCT` class is abstract, defines common interface for `TICKET`, `POPCORN`, `DRINK`
- **Polymorphism:** Methods `purchase_product()`, `cancel_purchase()`, `promotion()` behave differently in each subclass
- **Encapsulation:** Internal states protected, controlled access via public methods
- **Composition:** `CINEMA` contains `MOVIE`, which contains `SHOWTIME`, which contains `SEAT`
- **Abstraction:** Abstract interfaces define contracts (`SeatState`, `Command`, `NotificationChannel`)

---
### Exception Handling:

Exception handling was implemented by creating an **exceptions.py** file that centralizes the main custom exceptions as follows:

**1. Validation Exceptions:**

- Inheritance from ValueError was used to characterize these custom exceptions, creating 4 classes: `InvalidEmailException`, `InvalidPhoneException`, `InvalidCPFException`, `InvalidPasswordException`. They are used in files like `ui.py`, which centralizes menu logic, to validate in the `registrar()` function, and in `models.py` in the setters of the `USER` class: :


```python
def registrar():
    #......
    try:
        #...
        pass
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
```

```python
@email.setter
def email(self, new_email):
    if not isinstance(new_email, str):
        raise TypeError("Email must be a string.")
    try:
        validate_email(new_email)
        self.__email = new_email.strip()
    except InvalidEmailException:
        raise

@password.setter
def password(self, new_password):
    if not isinstance(new_password, str):
        raise TypeError("Password must be a string.")
    if len(new_password) < 5:
        raise InvalidPasswordException("Password must have at least 5 characters.")
    self.__password = new_password


@phone.setter
def phone(self, new_phone):
    if new_phone is None:
        self.__phone = None
        return
    if not isinstance(new_phone, str):
        raise TypeError("Phone must be a string.")
    if new_phone.strip().startswith("()"):
        raise InvalidPhoneException(new_phone, "Invalid phone (empty area code).")

@cpf.setter
def cpf(self, new_cpf):
    if new_cpf is None:
        self._cpf = None
        return
    
    if not isinstance(new_cpf, str):
        raise TypeError("CPF must be a string.")
    try:
        validate_cpf(new_cpf)
        self._cpf = re.sub(r'\D', '', new_cpf)
    except InvalidCPFException:
        raise
```
**2. Reservation Exceptions:**
- Inheritance from RuntimeError was used to characterize these custom Reservation exceptions, creating 4 classes (1 inheriting directly from RuntimeError and others inheriting from it): `BookingException`, `SeatAlreadyReservedException`, `ReservationExpiredException`, `SeatNotAvailableException`. They are used in files like `states.py` (which implements the STATE design pattern using the classes `AvailableState`, `TemporaryReservedState`, and `ConfirmedState`), in the `commands.py` file (which implements the COMMAND design pattern in the classes `CommandInvoker`, `PurchaseProductCommand`, `CancelProductCommand`, ``PurchaseComboCommand`), as well as in `ui.py` in functions like `finalize_purchase`, `comprar_ingresso()`, `cancelar_compra()`, and in the `main.py` file during program data initialization:


```python
class AvailableState(SeatState):
    #...
    def confirm(self, seat):
        raise SeatNotAvailableException(seat.row_and_number, "confirm")

class TemporaryReservedState(SeatState):
    #...
    def check_expiry(self, seat):
        if seat.reservation_expiry and datetime.now() >= seat.reservation_expiry:
            expiry_time = seat.reservation_expiry
            self.release(seat)
            raise ReservationExpiredException(seat.row_and_number, expiry_time)
        return False

class ConfirmedState(SeatState):
    #...
    def reserve(self, seat, user, minutes=0):
        raise SeatAlreadyReservedException(
            seat.row_and_number,
            "Confirmed"
        )
```


```python
class CommandInvoker:
    ###...
    def execute_command(self, command: Command):
        #...
        try:
            command.execute()
            if getattr(command, "executed", False):
                self._history.append(command)
        except (BookingException, PaymentException, CouponException) as e:
            print(f"[COMMAND ERROR] Business logic error during execution: {e}")

    def undo_last(self):
        #...
        try:
            command.undo()
        except (BookingException, PaymentException, CouponException) as e:
            print(f"[COMMAND ERROR] Business logic error during undo: {e}")
```

```python
class PurchaseProductCommand(Command):
    #...
    def execute(self):
        #...
        try:
            self.product.purchase_product(self.user)
            self.executed = True
        except (BookingException, PaymentException, CouponException) as e:
            print(f"PurchaseProductCommand execute error: {e}")
            self.executed = False
            raise

    def undo(self):
        #...
        try:
            self.product.cancel_purchase(self.user)
            self.executed = False
        except (BookingException, PaymentException, CouponException) as e:
            print(f"PurchaseProductCommand undo error: {e}")
```

```python
class CancelProductCommand(Command):
    #...
    def execute(self):
        #...
        try:
            self.product.cancel_purchase(self.user)
            self.executed = True
        except (BookingException, PaymentException, CouponException) as e:
            print(f"CancelProductCommand execute error: {e}")
            self.executed = False
            raise

    def undo(self):
        #...
        try:
            self.product.purchase_product(self.user)
            self.executed = False
        except (BookingException, PaymentException, CouponException) as e:
            print(f"CancelProductCommand undo error: {e}")
```

```python
class PurchaseComboCommand(Command):
    #...
    def execute(self):
        #...
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
                    try:
                        result = self.finalize_fn(self.combo, self.movie, self.showtime)
                    except Exception:
                        raise
                
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
```

```python
def finalize_purchase(combo, movie, showtime, seat):
    #...
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
    #...

    except (BookingException, PaymentException, CouponException) as e:
        print(f"Error finalizing purchase: {e}")
        return False

def comprar_ingresso(movie):
    #...
    try:
        if assento_selecionado.temp_reserve(state.usuario_logado, minutes=10):
            print(f"Seat {assento_selecionado.row_and_number} temporarily reserved until {assento_selecionado.reservation_expiry}.")
            break
        else:
            print("Could not reserve seat. Please try another one.")
    except SeatAlreadyReservedException as e:
        print(f"Reservation error: {e}")
        continue

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
    #...
    try:
        cinema_system.invoker.execute_command(CancelProductCommand(extra, state.usuario_logado))
    except (BookingException, PaymentException, CouponException) as e:
        print(f"Warning: Failed to cancel extra '{extra.name}': {e}")
    #...
    try:
        cmd_ticket = CancelProductCommand(ticket, state.usuario_logado)
        cinema_system.invoker.execute_command(cmd_ticket)
    except (BookingException, PaymentException, CouponException) as e:
        print(f"Warning: Failed to cancel ticket: {e}")
```


```python
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
```

**3. Payment Exceptions:**
- Inheritance from RuntimeError was used to characterize these custom Payment exceptions, creating 4 classes (1 inheriting directly from RuntimeError and others inheriting from it): `PaymentException`, `PaymentLimitExceededException`, `PaymentProcessingException`, `InvalidPaymentMethodException`. They are used in files like `facade.py` (which implements the FACADE design pattern using the classes `PaymentSubsystem`, `CinemaSystemFacade`), and in `commands.py` (which implements the COMMAND design pattern in the classes `CommandInvoker`, `PurchaseProductCommand`, `CancelProductCommand`, `PurchaseComboCommand`), as well as in `ui.py` in functions like `payment()`, `finalize_purchase()`, `comprar_ingresso()`, `cancelar_compra()`, and in the `main.py` file during program data initialization:


```python
class PaymentSubsystem:
    #...

    def process_payment(self, method: str, amount: float, user):
        #...

        if method not in method_mapping:
            raise InvalidPaymentMethodException(
                method, valid_methods=["Credit", "Debit", "PIX"]
            )
        
        method_key = method_mapping[method]
        limit = PAYMENT_LIMITS[method_key]

        if amount > limit:
            raise PaymentLimitExceededException(
                payment_method=method_key.upper(),
                amount=amount,
                limit=limit
            )
        if random.random() < PAYMENT_ERROR_RATE:
            raise PaymentProcessingException(
                "Error connecting to payment server",
                details="Please try again in a few seconds"
            )

class CinemaSystemFacade:
    #...
    try:
        #...
    except (PaymentLimitExceededException, PaymentProcessingException, 
            InvalidPaymentMethodException) as e:
        result["message"] = str(e)
        self.bookings.release_seat(seat, user)
        return result
```


```python
class CommandInvoker:
    ###...
    def execute_command(self, command: Command):
        #...
        try:
            command.execute()
            if getattr(command, "executed", False):
                self._history.append(command)
        except (BookingException, PaymentException, CouponException) as e:
            print(f"[COMMAND ERROR] Business logic error during execution: {e}")

    def undo_last(self):
        #...
        try:
            command.undo()
        except (BookingException, PaymentException, CouponException) as e:
            print(f"[COMMAND ERROR] Business logic error during undo: {e}")
```

```python
class PurchaseProductCommand(Command):
    #...
    def execute(self):
        #...
        try:
            self.product.purchase_product(self.user)
            self.executed = True
        except (BookingException, PaymentException, CouponException) as e:
            print(f"PurchaseProductCommand execute error: {e}")
            self.executed = False
            raise

    def undo(self):
        #...
        try:
            self.product.cancel_purchase(self.user)
            self.executed = False
        except (BookingException, PaymentException, CouponException) as e:
            print(f"PurchaseProductCommand undo error: {e}")
```

```python
class CancelProductCommand(Command):
    #...
    def execute(self):
        #...
        try:
            self.product.cancel_purchase(self.user)
            self.executed = True
        except (BookingException, PaymentException, CouponException) as e:
            print(f"CancelProductCommand execute error: {e}")
            self.executed = False
            raise

    def undo(self):
        #...
        try:
            self.product.purchase_product(self.user)
            self.executed = False
        except (BookingException, PaymentException, CouponException) as e:
            print(f"CancelProductCommand undo error: {e}")
```

```python
class PurchaseComboCommand(Command):
    # ...
    def execute(self):
        # ...
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
                    try:
                        result = self.finalize_fn(self.combo, self.movie, self.showtime)
                    except Exception:
                        raise
                
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
```
```python
def payment(valor):
    try:
        #...
    except (PaymentLimitExceededException, PaymentProcessingException, InvalidPaymentMethodException) as e:
        print(f"Payment error: {e}")
        retry = input("Try again? [Y/N]: ").strip().upper()
        if retry != "Y":
            return False
    else:
        print("Invalid credit card number. Please try again.")
```


```python
def finalize_purchase(combo, movie, showtime, seat):
    #...
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
    #...

    except (BookingException, PaymentException, CouponException) as e:
        print(f"Error finalizing purchase: {e}")
        return False

def comprar_ingresso(movie):
    #...
    try:
        if assento_selecionado.temp_reserve(state.usuario_logado, minutes=10):
            print(f"Seat {assento_selecionado.row_and_number} temporarily reserved until {assento_selecionado.reservation_expiry}.")
            break
        else:
            print("Could not reserve seat. Please try another one.")
    except SeatAlreadyReservedException as e:
        print(f"Reservation error: {e}")
        continue

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
    #...
    try:
        cinema_system.invoker.execute_command(CancelProductCommand(extra, state.usuario_logado))
    except (BookingException, PaymentException, CouponException) as e:
        print(f"Warning: Failed to cancel extra '{extra.name}': {e}")
    #...
    try:
        cmd_ticket = CancelProductCommand(ticket, state.usuario_logado)
        cinema_system.invoker.execute_command(cmd_ticket)
    except (BookingException, PaymentException, CouponException) as e:
        print(f"Warning: Failed to cancel ticket: {e}")
```


```python
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
```

**4. Coupon Exceptions:**
- Inheritance from RuntimeError was used to characterize these custom Coupon exceptions, creating 5 classes (1 inheriting directly from RuntimeError and others inheriting from it): `CouponException`, `InvalidCouponException`, `CouponExpiredException`, `CouponUsageLimitException`, and `MinimumPurchaseException`. They are used in files like `services.py` (which implements the Singleton design pattern in the Coupon class), and in `commands.py` (which implements the COMMAND design pattern in the classes `CommandInvoker`, `PurchaseProductCommand`, `CancelProductCommand`, `PurchaseComboCommand`), as well as in `ui.py` in functions like `finalize_purchase()`, `comprar_ingresso()`, `cancelar_compra()`, and in the `main.py` file during program data initialization:


```python
class Coupon:
    #...
    def is_valid(self, raise_exception=False):
        if not self.is_active:
            if raise_exception:
                raise InvalidCouponException(self.code, "Cupom está inativo")
            return False
            
        if self.valid_until and datetime.now() > self.valid_until:
            if raise_exception:
                raise CouponExpiredException(self.code, self.valid_until)
            return False
            
        if self.max_uses and self.uses_count >= self.max_uses:
            if raise_exception:
                raise CouponUsageLimitException(self.code, self.max_uses)
            return False
        return True

    def can_apply(self, total_amount, ticket_type=None, cinema_name=None, movie_name=None, user_type=None, raise_exception=False):
        if total_amount < self.min_purchase:
            if raise_exception:
                raise MinimumPurchaseException(self.code, self.min_purchase, total_amount)
            return False
            
        if hasattr(self, 'applicable_ticket_types') and self.applicable_ticket_types and ticket_type not in self.applicable_ticket_types:
            if raise_exception:
                raise InvalidCouponException(
                    self.code, 
                    f"Cupom não aplicável ao tipo de ingresso '{ticket_type}'"
                )
            return False
            
        if self.applicable_cinemas and cinema_name not in self.applicable_cinemas:
            if raise_exception:
                raise InvalidCouponException(
                    self.code,
                    f"Cupom não aplicável ao cinema '{cinema_name}'"
                )
            return False
            
        if self.applicable_movies and movie_name not in self.applicable_movies:
            if raise_exception:
                raise InvalidCouponException(
                    self.code,
                    f"Cupom não aplicável ao filme '{movie_name}'"
                )
            return False
            
        if self.user_type and user_type != self.user_type:
            if raise_exception:
                raise InvalidCouponException(
                    self.code,
                    f"Cupom exclusivo para usuários do tipo '{self.user_type}'"
                )
            return False
            
        return True
    #...
```

```python
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
    #...
    try:
        cinema_system.invoker.execute_command(CancelProductCommand(extra, state.usuario_logado))
    except (BookingException, PaymentException, CouponException) as e:
        print(f"Warning: Failed to cancel extra '{extra.name}': {e}")
    #...
    try:
        cmd_ticket = CancelProductCommand(ticket, state.usuario_logado)
        cinema_system.invoker.execute_command(cmd_ticket)
    except (BookingException, PaymentException, CouponException) as e:
        print(f"Warning: Failed to cancel ticket: {e}")
```


```python
class CommandInvoker:
    ###...
    def execute_command(self, command: Command):
        #...
        try:
            command.execute()
            if getattr(command, "executed", False):
                self._history.append(command)
        except (BookingException, PaymentException, CouponException) as e:
            print(f"[COMMAND ERROR] Business logic error during execution: {e}")

    def undo_last(self):
        #...
        try:
            command.undo()
        except (BookingException, PaymentException, CouponException) as e:
            print(f"[COMMAND ERROR] Business logic error during undo: {e}")
```

```python
class PurchaseProductCommand(Command):
    #...
    def execute(self):
        #...
        try:
            self.product.purchase_product(self.user)
            self.executed = True
        except (BookingException, PaymentException, CouponException) as e:
            print(f"PurchaseProductCommand execute error: {e}")
            self.executed = False
            raise

    def undo(self):
        #...
        try:
            self.product.cancel_purchase(self.user)
            self.executed = False
        except (BookingException, PaymentException, CouponException) as e:
            print(f"PurchaseProductCommand undo error: {e}")
```

```python
class CancelProductCommand(Command):
    #...
    def execute(self):
        #...
        try:
            self.product.cancel_purchase(self.user)
            self.executed = True
        except (BookingException, PaymentException, CouponException) as e:
            print(f"CancelProductCommand execute error: {e}")
            self.executed = False
            raise

    def undo(self):
        #...
        try:
            self.product.purchase_product(self.user)
            self.executed = False
        except (BookingException, PaymentException, CouponException) as e:
            print(f"CancelProductCommand undo error: {e}")
```

```python
class PurchaseComboCommand(Command):
    # ...
    def execute(self):
        # ...
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
                    try:
                        result = self.finalize_fn(self.combo, self.movie, self.showtime)
                    except Exception:
                        raise
                
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
```

```python
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
```

**5. Notification Exceptions:**
- Inheritance from RuntimeError was used to characterize these custom Notification exceptions, creating 3 classes (1 inheriting directly from RuntimeError and others inheriting from it): `NotificationException`, `NotificationDeliveryException`, `InvalidNotificationChannelException`. They are used in `services.py`, which implements a Singleton for Notification Functions, and in `ui.py`:

```python
class MultiChannelNotificationService(metaclass=MetaSingleton):
    #...
    for channel_name in channels:
        if channel_name not in self.channels:
            raise InvalidNotificationChannelException(
                channel_name, 
                list(self.channels.keys())
            )

    if failed_channels and len(failed_channels) == len(channels):
        raise NotificationDeliveryException(
            ", ".join(failed_channels),
            "Falha em todos os canais de notificação"
        )
```

```python
def add_movie_admin():
    #...
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
```

**6. Authentication Exceptions:**
- Inheritance from RuntimeError was used to characterize these custom Authentication exceptions, creating 4 classes (1 inheriting directly from RuntimeError and others inheriting from it): `AuthenticationException`, `InvalidCredentialsException`, `UserNotFoundException`, `UnauthorizedAccessException`. They are used in the `ui.py` file in admin functions and login processing functions:


```python
def processar_login():
    #...
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


def add_showtime_admin():
    #...

    try:
        if "manage_movies" not in state.usuario_logado.permissions:
            raise UnauthorizedAccessException(
            state.usuario_logado.login if hasattr(state.usuario_logado, 'login') else "unknown",
            "manage_movies"
            )
    except UnauthorizedAccessException as e:
        print(f"Access denied: {e}")
        return
```

**7. Python Built-in Exceptions:**
- These were used in various files, for example, in `ui.py` in the `menu_notificacoes()` function, in `main.py`, `models.py`, and others, such as in properties and setters for attributes of the `USER` class, among others.


```python
def menu_notifications():
    #...
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
```

```python
class USER:
    #...
    def cpf(self, new_cpf):
        if new_cpf is None:
            self._cpf = None
            return
        
        if not isinstance(new_cpf, str):
            raise TypeError("CPF must be a string.")
        try:
            validate_cpf(new_cpf)
            self._cpf = re.sub(r'\D', '', new_cpf)
        except InvalidCPFException:
            raise
```

```python
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
```

### Project Structure

```
Refatoracao-Design-Patterns-Projeto-Software/
│
├── main.py                     # Application entry point
├── ui.py                       # Command-line interface
├── models.py                   # Domain models (USER, CINEMA, MOVIE, SEAT)
├── products.py                 # Products (TICKET, POPCORN, DRINK, etc.)
├── exceptions.py               # Custom exception hierarchy (20+ types)
│
├── Creational Patterns
│   ├── factories.py            # Abstract Factory & Factory Method
│   ├── builders.py             # Builder Pattern
│   └── services.py             # Singleton (NotificationService, PromotionManager)
│
├── Behavioral Patterns
│   ├── states.py               # State Pattern
│   ├── observer.py             # Observer Pattern (EventBus)
│   └── commands.py             # Command Pattern
│
├── Structural Patterns
│   ├── adapter.py              # Adapter Pattern
│   ├── decorator.py            # Decorator Pattern
│   └── facade.py               # Facade Pattern
│
├── Utilities
│   ├── utils.py                # MetaSingleton, event constants
│   └── state.py                # Global application state
│
├── requirements.txt            # Project dependencies
├── README.md                   # This file
└── LICENSE                     # MIT License
```

---

### How to Run

**Prerequisites:**
- Python 3.8 or higher
- pip (Python package manager)

**Installation:**

```bash
# Clone the repository
git clone https://github.com/jfdt10/Refatoracao-Design-Patterns-Projeto-Software.git

# Navigate to directory
cd Refatoracao-Design-Patterns-Projeto-Software

# Install dependencies
pip install -r requirements.txt

# Run the program
python main.py
```

**Usage Tips:**
- The program runs in terminal with interactive menus
- Select seat, ticket type, and payment method according to instructions
- System prevents duplicate seat selections
- Automatic total calculation with discount application
- To exit, select "Exit" option in main menu

---

### Contributors

| Name | Role | Contributions |
|------|------|--------------|
| Marcela Rocha Silva | Original Author | Initial system development |
| Jean Felipe Duarte Tenório | Refactorer/Maintainer | Design Patterns implementation, architecture improvements |

---

### Future Improvements

**✔️ Completed (v1.0):**
- Robust exception handling (20+ custom exceptions, validations, specific handlers)

**Planned (v1.1+):**
- REST API with Flask/FastAPI
- Administrative dashboard
- Advanced reports and analytics
- Real database integration
- Authentication and security (JWT, hashing)

---

### License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Repository:** [github.com/jfdt10/Refatoracao-Design-Patterns-Projeto-Software](https://github.com/jfdt10/Refatoracao-Design-Patterns-Projeto-Software)