# MovieTicketSystem
This project is a system for selling movie tickets and popcorn combos, developed in Python. It simulates a complete user experience through a command line interface, using the principles of Object-Oriented Programming (OOP).
### Features
Functions that have been implemented:
* Cinema and Movie Listings
* Seat Selection and Booking
* Payment Processing
* User Account Management
* Booking History and Cancellations
* Promotions and Discounts
* Real-Time Seat Availability
* Customer Reviews and Ratings
* Ticket and popcorn combo
* Movie times and theaters


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
