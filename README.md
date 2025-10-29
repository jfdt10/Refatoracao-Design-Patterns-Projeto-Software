# MovieTicketSystem

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

**Em Desenvolvimento:**
- Tratamento robusto de exceções

**Planejado:**
- API REST com Flask/FastAPI
- Dashboard administrativo
- Relatórios e analytics avançados

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

### Project Structure

```
Refatoracao-Design-Patterns-Projeto-Software/
│
├── main.py                     # Application entry point
├── ui.py                       # Command-line interface
├── models.py                   # Domain models (USER, CINEMA, MOVIE, SEAT)
├── products.py                 # Products (TICKET, POPCORN, DRINK, etc.)
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

**In Development:**
- Robust exception handling 

**Planned:**
- REST API with Flask/FastAPI
- Administrative dashboard
- Advanced reports and analytics

---

### License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Repository:** [github.com/jfdt10/Refatoracao-Design-Patterns-Projeto-Software](https://github.com/jfdt10/Refatoracao-Design-Patterns-Projeto-Software)
