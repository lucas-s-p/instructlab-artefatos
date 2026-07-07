// Switch removido de Customer.statement() — delegado para movie.getCharge()
// CC do método statement() = 2 (base + while)
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
            Rental each = (Rental) it.next();
            double thisAmount = each.getMovie().getCharge(each.getDaysRented());
            frequentRenterPoints += each.getMovie().getFrequentRenterPoints(each.getDaysRented());
            result += "\t" + each.getMovie().getTitle() + "\t" + thisAmount + "\n";
            totalAmount += thisAmount;
        }

        result += "You owed " + totalAmount + "\n";
        result += "You earned " + frequentRenterPoints + " frequent renter points\n";
        return result;
    }
}
