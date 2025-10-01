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
*   **Onde foi usado?** Nas classes `NotificationService` e `PromotionManager` dentro de `system.py`, utilizando uma Metaclasse `MetaSingleton` para garantir a unicidade.
*   **Motivo e Vantagem:** Serviços como o de notificação ou o gerenciador de promoções devem ser únicos em toda a aplicação. Não faz sentido ter múltiplos gerenciadores de cupons ou múltiplos centros de notificação, pois eles controlam um estado centralizado (a lista de notificações enviadas e a lista de cupons disponíveis). O Singleton garante que, não importa onde o serviço seja importado ou instanciado, ele sempre se referirá ao **mesmo objeto**, mantendo a consistência dos dados em todo o sistema.

### 2. Builder
*   **Onde foi usado?** Na classe `ComboBuilder` em `system.py` para criar a compra final do cliente, que pode incluir um ingresso e vários itens extras (pipoca, refrigerante, etc.) e há implementação de diretor responsável pela montagem de combos pré-montados.
*   **Motivo e Vantagem:** A criação de um "combo" de compra é complexa. O preço final depende do tipo de ingresso, dos itens adicionais, de seus tamanhos e de cupons de desconto. O Builder permite construir esse objeto complexo passo a passo (`.add_ticket()`, `.add_popcorn()`, `.apply_coupon()`) sem sobrecarregar o construtor com dezenas de parâmetros. Isso torna o código na interface do usuário (`comprar_ingresso`) muito mais limpo e legível, além de facilitar a adição de novos produtos ao combo no futuro.

### 3. Factory Method
*   **Onde foi usado?** Na função `create_ticket_with_factory` e, de forma mais ampla, dentro das fábricas concretas como `StandardFactory` (com seus métodos `create_ticket`, `create_popcorn`, etc.). A função `get_factory_for_user` também atua como uma fábrica simples para decidir qual `AbstractFactory` usar.
*   **Motivo e Vantagem:** Em vez de ter uma série de `if/elif/else` na interface do usuário para decidir qual classe de ingresso instanciar (`if tipo == 'student': ticket = StudentTicket()`), delegamos essa responsabilidade a uma função de fábrica. A UI simplesmente diz: "fábrica, me dê um ingresso do tipo 'student'". A fábrica então lida com a lógica de instanciar o objeto `StudentTicket` correto. Isso desacopla a UI das classes concretas de ingresso, facilitando a adição de novos tipos de ingresso no futuro sem precisar alterar o código da UI.

### 4. Abstract Factory
*   **Onde foi usado?** É o padrão principal em `system.py`, com a `AbstractFactory` e suas implementações `StandardFactory`, `StudentFactory` e `VIPFactory`.
*   **Motivo e Vantagem:** Este padrão eleva o Factory Method a um novo nível. Enquanto o Factory Method cria um produto, o Abstract Factory cria uma **família inteira de produtos consistentes**. Quando o `ComboBuilder` recebe a `StudentFactory`, ele tem a garantia de que *todos* os produtos criados por ela (ingresso, pipoca, refrigerante) seguirão as regras de preço para estudantes. Isso garante consistência e encapsula as regras de negócio de cada "tema" (Standard, Student, VIP) em sua própria fábrica, tornando o sistema extremamente flexível e fácil de estender.



### Applied OOP Concepts
The project was built based on important pillars of Object-Oriented Programming:
* Inheritance and Abstract Classes: The PRODUCT class is an abstract class that defines a common interface for all products (such as TICKET and POPCORN). The child classes (TICKET, POPCORN) inherit this interface and provide their own implementations of the methods.
* Polymorphism: The purchase_product(), cancel_purchase(), and promotion() methods are polymorphic. They act differently depending on the object they are called on. For example, .promotion() on a POPCORN applies a discount by size, while on a TICKET it applies a discount by customer type.
* Composition: The project uses composition to model the relationship between objects. For example:
    * A CINEMA has a list of MOVIES.
    * A MOVIE has a list of SHOWTIMES.
    * A SHOWTIME has a MOVIE and a list of SEATS.
    * A TICKET has a SEAT and a SHOWTIME.
  

## Tips for Use

- The program will run on the terminal with interactive menus.
- Select your seat, ticket type, and payment method according to the instructions.
- The system prevents duplicate seat selections and calculates the total automatically.
- The program will only stop running when you select the “exit” option.

---

# How to run the program
- pip install -r requirements.txt
- cd Refatoracao-Design-Patterns-Projeto-Software
## Versão dividida em Módulos
- python main.py
## Versão Unificada Refatorada:
- python system.py