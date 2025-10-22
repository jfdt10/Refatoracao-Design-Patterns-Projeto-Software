# MovieTicketSystem
This project is a system for selling movie tickets and popcorn combos, developed in Python. It simulates a complete user experience through a command line interface, using the principles of Object-Oriented Programming (OOP).

### Features
Functions that have been implemented:
* Cinema and Movie Listings
* Seat Selection and Booking
* Payment Processing(Adicionado-Refatoração Melhorado a Usabilidade(simulação mais realista))
* User Account Management(Melhorado-Refatoração Adicionado Admin Painel)
* Booking History and Cancellations
* Promotions and Discounts(Melhorado-Refatoração)
* Real-Time Seat Availability(Melhorado-Refatoração)
* Customer Reviews and Ratings
* Ticket and popcorn combo
* Movie times and theaters
* Notification and Alerts: Sending notifications for new releases and booking confirmations.(Adicionado-Refatoração)
* Mobile Ticketing: Generating mobile tickets for ease of access(QR CODE MOBILE)(Adicionado-Refatoração)


### Refatoramento(Padrões Criacionais)
# Padrões de Projeto Criacionais Implementados (Creational Design Patterns)

### 1. Singleton
*   **Onde foi usado?** Nas classes `NotificationService` e `PromotionManager` dentro de `services.py`, utilizando uma Metaclasse `MetaSingleton` dentro de `utils.py`para garantir a unicidade.
*   **Motivo e Vantagem:** Serviços como o de notificação ou o gerenciador de promoções devem ser únicos em toda a aplicação. Não faz sentido ter múltiplos gerenciadores de cupons ou múltiplos centros de notificação, pois eles controlam um estado centralizado (a lista de notificações enviadas e a lista de cupons disponíveis). O Singleton garante que, não importa onde o serviço seja importado ou instanciado, ele sempre se referirá ao **mesmo objeto**, mantendo a consistência dos dados em todo o sistema.

### 2. Builder
*   **Onde foi usado?** Na classe `ComboBuilder` em `builders` para criar a compra final do cliente, que pode incluir um ingresso e vários itens extras (pipoca, refrigerante, etc.) e há implementação de diretor responsável pela montagem de combos pré-montados.
*   **Motivo e Vantagem:** A criação de um "combo" de compra é complexa. O preço final depende do tipo de ingresso, dos itens adicionais, de seus tamanhos e de cupons de desconto. O Builder permite construir esse objeto complexo passo a passo (`.add_ticket()`, `.add_popcorn()`, `.apply_coupon()`) sem sobrecarregar o construtor com dezenas de parâmetros. Isso torna o código na interface do usuário (`comprar_ingresso`) muito mais limpo e legível, além de facilitar a adição de novos produtos ao combo no futuro.

### 3. Factory Method
*   **Onde foi usado?** Na função `create_ticket_with_factory` e, de forma mais ampla, dentro das fábricas concretas como `StandardFactory` (com seus métodos `create_ticket`, `create_popcorn`, etc.). A função `get_factory_for_user` também atua como uma fábrica simples para decidir qual `AbstractFactory` usar.
*   **Motivo e Vantagem:** Em vez de ter uma série de `if/elif/else` na interface do usuário para decidir qual classe de ingresso instanciar (`if tipo == 'student': ticket = StudentTicket()`), delegamos essa responsabilidade a uma função de fábrica. A UI simplesmente diz: "fábrica, me dê um ingresso do tipo 'student'". A fábrica então lida com a lógica de instanciar o objeto `StudentTicket` correto. Isso desacopla a UI das classes concretas de ingresso, facilitando a adição de novos tipos de ingresso no futuro sem precisar alterar o código da UI.

### 4. Abstract Factory
*   **Onde foi usado?** É o padrão principal em `factories.py`, com a `AbstractFactory` e suas implementações `StandardFactory`, `StudentFactory` e `VIPFactory`.
*   **Motivo e Vantagem:** Este padrão eleva o Factory Method a um novo nível. Enquanto o Factory Method cria um produto, o Abstract Factory cria uma **família inteira de produtos consistentes**. Quando o `ComboBuilder` recebe a `StudentFactory`, ele tem a garantia de que *todos* os produtos criados por ela (ingresso, pipoca, refrigerante) seguirão as regras de preço para estudantes. Isso garante consistência e encapsula as regras de negócio de cada "tema" (Standard, Student, VIP) em sua própria fábrica, tornando o sistema extremamente flexível e fácil de estender.

# Padrões de Projeto Comportamentais Implementados (Behavorial Design Patterns)

### 1. State
* **Onde foi usado?** Na classe SEAT em models.py, utilizando o padrão State com a interface abstrata SeatState e os estados concretos AvailableState, TemporaryReservedState e ConfirmedState definidos em states.py. O objeto SEAT delega comportamentos como reserve(), release(), confirm() e check_expiry() ao seu atributo self.state, que muda dinamicamente entre os estados.
* **Motivo e Vantagem:** O gerenciamento de assentos em um cinema é complexo, pois um assento pode estar disponível, reservado temporariamente (com expiração) ou confirmado permanentemente, e cada estado exige comportamentos diferentes (ex.: não é possível reservar um assento já confirmado). O padrão State encapsula essa lógica em classes separadas, evitando um grande if/elif na classe SEAT e tornando o código mais modular e extensível. Por exemplo, adicionar um novo estado (como "Bloqueado para manutenção") requer apenas criar uma nova classe concreta, sem alterar o código existente. Isso também facilita testes e manutenção, garantindo que transições de estado sejam consistentes e publiquem eventos via event_bus para notificações em tempo real.

### 2. Observer
* **Onde foi usado?** No sistema de eventos com EventBus em observer.py, onde NotificationObserver e AnalyticsObserver se inscrevem para eventos como "seat_reserved", "payment_success" ou "booking_confirmed". O EventBus notifica os observadores quando eventos são publicados, permitindo reações automáticas (ex.: enviar notificações ao usuário ou atualizar métricas de analytics).
* **Motivo e Vantagem:** Em um sistema de vendas de ingressos, ações como confirmar um pagamento ou reservar um assento precisam disparar múltiplas reações independentes (notificações push, logs de analytics, atualizações de UI). O padrão Observer desacopla o emissor de eventos (ex.: SEAT.reserve()) dos receptores (observadores), permitindo adicionar novos observadores sem modificar o código do emissor. Isso promove reutilização e extensibilidade — por exemplo, o AnalyticsObserver coleta dados silenciosamente em background, enquanto o NotificationObserver envia alertas em tempo real, tudo sem interferir na lógica principal do sistema.

### 3. Command
*  **Onde foi usado?** Nas classes CommandInvoker, PurchaseProductCommand, CancelProductCommand e PurchaseComboCommand em commands.py. Cada comando encapsula uma ação (ex.: comprar um produto ou cancelar uma reserva) e suporta execução (execute()) e desfazimento (undo()), com o CommandInvoker gerenciando um histórico de comandos para operações reversíveis.
* **Motivo e Vantagem:** Operações como comprar ingressos ou combos são complexas e podem falhar (ex.: pagamento rejeitado), exigindo rollback. O padrão Command encapsula essas operações em objetos, permitindo executá-las de forma desacoplada e reversível, facilitando undo/redo e testes. Por exemplo, PurchaseComboCommand agrupa subcomandos para extras (pipoca, etc.) e o ingresso principal, garantindo atomicidade — se um falha, todos são desfeitos. Isso melhora a robustez do sistema, especialmente em cenários de erro, e permite extensões como logging ou replay de comandos sem alterar a lógica de negócio.

# Padrões de Projeto Estruturais Implementados (Structural Design Patterns)

### 1. Adapter
* **Onde foi usado?** Nas classes `EmailNotificationAdapter`, `SMSNotificationAdapter` e `PushNotificationAdapter` em `adapter.py`, que adaptam serviços externos (`EmailService`, `SMSService`, `PushNotificationService`) para a interface comum `NotificationChannel`. O `MultiChannelNotificationService` em `services.py` utiliza esses adaptadores para enviar notificações por múltiplos canais.
* **Motivo e Vantagem:** Os serviços externos de email, SMS e push têm interfaces incompatíveis entre si (ex.: `send_email()` vs `send_sms()` vs `send_push()`). O padrão Adapter converte essas interfaces distintas em uma interface unificada (`send(user, subject, message, data)`), permitindo que o sistema trate todos os canais de notificação de forma homogênea. Isso facilita a adição de novos canais (ex.: WhatsApp, Telegram) sem alterar o código existente — basta criar um novo adapter. Além disso, cada adapter mantém seu histórico de mensagens enviadas (`sent_messages`), facilitando auditoria e debugging.

### 2. Decorator
* **Onde foi usado?** Na classe abstrata `ProductDecorator` e suas implementações concretas `SpecialPackagingDecorator`, `ExtraItemDecorator` e `GiftWrapDecorator` em `decorator.py`. Os decoradores envolvem produtos (pipoca, refrigerantes, etc.) para adicionar funcionalidades extras (embalagem especial +R$5, itens adicionais, embrulho para presente +R$3) sem modificar as classes de produtos originais.
* **Motivo e Vantagem:** Em um sistema de venda de combos, produtos podem ser personalizados de várias formas (embalagem especial, extras, presentes), e combinar essas opções manualmente geraria uma explosão de subclasses (ex.: `PopcornComEmbalagamEspecial`, `PopcornComEmbalagamEPresenteEExtra`). O padrão Decorator permite compor funcionalidades dinamicamente em tempo de execução (`SpecialPackagingDecorator(ExtraItemDecorator(produto))`), mantendo o código limpo e extensível. Além disso, os decoradores delegam automaticamente métodos como `purchase_product()` e `promotion()` ao produto decorado, preservando o polimorfismo e garantindo que descontos e cupons funcionem corretamente em produtos decorados.

### 3. Facade
* **Onde foi usado?** Na classe `CinemaSystemFacade` em `facade.py`, que unifica cinco subsistemas complexos: `Notification_Subsystem`, `Promotion_Subsystem`, `ComboManagementSubsystem`, `PaymentSubsystem` e `BookingSubsystem`. A facade expõe métodos simplificados como `complete_ticket_purchase()` e `cancel_booking()` que orquestram múltiplas operações internas.
* **Motivo e Vantagem:** Processos como comprar um ingresso envolvem coordenar subsistemas de reserva de assentos, criação de combos, aplicação de cupons, processamento de pagamento, execução de comandos e publicação de eventos — uma complexidade que não deve vazar para a interface do usuário. A Facade encapsula toda essa lógica em métodos de alto nível, simplificando drasticamente o código em `ui.py` (que antes tinha dezenas de linhas para uma compra, agora reduzidas a uma chamada). Isso promove manutenibilidade, pois mudanças nos subsistemas (ex.: adicionar novo método de pagamento) não afetam a UI, apenas a implementação interna da facade. Além disso, a facade gerencia transações de forma atômica, garantindo rollback automático em caso de falhas (ex.: liberar assento se o pagamento falhar).

### Applied OOP Concepts
The project was built based on important pillars of Object-Oriented Programming:
* Inheritance and Abstract Classes: The PRODUCT class is an abstract class that defines a common interface for all products (such as TICKET and POPCORN). The child classes (TICKET, POPCORN) inherit this interface and provide their own implementations of the methods.
* Polymorphism: The purchase_product(), cancel_purchase(), and promotion() methods are polymorphic. They act differently depending on the object they are called on. For example, .promotion() on a POPCORN applies a discount by size, while on a TICKET it applies a discount by customer type.
* Composition: The project uses composition to model the relationship between objects. For example:
    * A CINEMA has a list of MOVIES.
    * A MOVIE has a list of SHOWTIMES.
    * A SHOWTIME has a MOVIE and a list of SEATS.
    * A TICKET has a SEAT and a SHOWTIME.
  

## Contributors

* Marcela Rocha Silva — Autora original
* Jean Felipe Duarte Tenório — Refatorador / Manutenção (refatoração e implementação de novos padrões)

## Tips for Use

- The program will run on the terminal with interactive menus.
- Select your seat, ticket type, and payment method according to the instructions.
- The system prevents duplicate seat selections and calculates the total automatically.
- The program will only stop running when you select the “exit” option.

---

# How to run the program
- pip install -r requirements.txt
- cd Refatoracao-Design-Patterns-Projeto-Software

# Run 
- python main.py