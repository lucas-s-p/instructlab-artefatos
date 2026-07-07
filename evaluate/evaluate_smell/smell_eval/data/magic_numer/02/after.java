// Literais extraídos para constantes nomeadas — sem NumericLiteral em condições if
public class RentalPriceCalculator {

    public static final int REGULAR     = 0;
    public static final int NEW_RELEASE = 1;
    public static final int CHILDRENS   = 2;

    private static final int    REGULAR_RENTAL_THRESHOLD  = 2;
    private static final double REGULAR_BASE_AMOUNT       = 2.0;
    private static final double REGULAR_EXTRA_PER_DAY     = 1.5;
    private static final int    CHILDRENS_RENTAL_THRESHOLD = 3;
    private static final double CHILDRENS_BASE_AMOUNT     = 1.5;
    private static final double CHILDRENS_EXTRA_PER_DAY   = 1.5;
    private static final double NEW_RELEASE_RATE          = 3.0;
    private static final int    BONUS_RENTAL_THRESHOLD    = 1;

    public double getCharge(int priceCode, int daysRented) {
        double result = 0;
        switch (priceCode) {
            case REGULAR:
                result += REGULAR_BASE_AMOUNT;
                if (daysRented > REGULAR_RENTAL_THRESHOLD)
                    result += (daysRented - REGULAR_RENTAL_THRESHOLD) * REGULAR_EXTRA_PER_DAY;
                break;
            case NEW_RELEASE:
                result += daysRented * NEW_RELEASE_RATE;
                break;
            case CHILDRENS:
                result += CHILDRENS_BASE_AMOUNT;
                if (daysRented > CHILDRENS_RENTAL_THRESHOLD)
                    result += (daysRented - CHILDRENS_RENTAL_THRESHOLD) * CHILDRENS_EXTRA_PER_DAY;
                break;
            default:
                throw new IllegalArgumentException("Unknown price code: " + priceCode);
        }
        return result;
    }

    public int getFrequentRenterPoints(int priceCode, int daysRented) {
        if (priceCode == NEW_RELEASE && daysRented > BONUS_RENTAL_THRESHOLD)
            return 2;
        return 1;
    }
}
