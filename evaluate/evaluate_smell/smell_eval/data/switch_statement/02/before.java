// Fonte: Codesai/code-smells-refactoring-training-java — video store kata (adaptado)
// CC do método statement() = 8 (base + switch 3 cases + default + while + 2 ifs)
public class Customer {

    private String name;
    private java.util.ArrayList rentals = new java.util.ArrayList();

    public Customer(String name) {
        this.name = name;
    }

    public void addRental(Rental rental) {
        rentals.add(rental);
    }

    public String getName() {
        return name;
    }

    public String statement() {
        double totalAmount = 0;
        int frequentRenterPoints = 0;
        java.util.Iterator it = rentals.iterator();
        String result = "Rental Record for " + getName() + "\n";

        while (it.hasNext()) {
            double thisAmount = 0;
            Rental each = (Rental) it.next();

            switch (each.getMovie().getPriceCode()) {
                case Movie.REGULAR:
                    thisAmount += 2;
                    if (each.getDaysRented() > 2)
                        thisAmount += (each.getDaysRented() - 2) * 1.5;
                    break;
                case Movie.NEW_RELEASE:
                    thisAmount += each.getDaysRented() * 3;
                    break;
                case Movie.CHILDRENS:
                    thisAmount += 1.5;
                    if (each.getDaysRented() > 3)
                        thisAmount += (each.getDaysRented() - 3) * 1.5;
                    break;
                default:
                    throw new IllegalArgumentException("Unknown price code");
            }

            frequentRenterPoints++;
            if (each.getMovie().getPriceCode() == Movie.NEW_RELEASE && each.getDaysRented() > 1)
                frequentRenterPoints++;

            result += "\t" + each.getMovie().getTitle() + "\t" + thisAmount + "\n";
            totalAmount += thisAmount;
        }

        result += "You owed " + totalAmount + "\n";
        result += "You earned " + frequentRenterPoints + " frequent renter points\n";
        return result;
    }
}
