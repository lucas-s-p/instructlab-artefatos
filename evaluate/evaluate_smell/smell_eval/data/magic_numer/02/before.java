// Fonte: Codesai/code-smells-refactoring-training-java — video store kata (adaptado)
// Literais numéricos em condições if: 3 (childrens rental threshold)
// Regra XPath: //IfStatement//NumericLiteral[not(@Image = ('0', '1', '-1', '2'))]
public class RentalPriceCalculator {

    public static final int REGULAR   = 0;
    public static final int NEW_RELEASE = 1;
    public static final int CHILDRENS = 2;

    public double getCharge(int priceCode, int daysRented) {
        double result = 0;
        switch (priceCode) {
            case REGULAR:
                result += 2;
                if (daysRented > 2)
                    result += (daysRented - 2) * 1.5;
                break;
            case NEW_RELEASE:
                result += daysRented * 3;
                break;
            case CHILDRENS:
                result += 1.5;
                if (daysRented > 3)
                    result += (daysRented - 3) * 1.5;
                break;
            default:
                throw new IllegalArgumentException("Unknown price code: " + priceCode);
        }
        return result;
    }

    public int getFrequentRenterPoints(int priceCode, int daysRented) {
        if (priceCode == NEW_RELEASE && daysRented > 1)
            return 2;
        return 1;
    }
}
