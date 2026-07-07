public class OrderProcessor
{
    public String validateAndProcess(String customerId, double amount, String productId)
    {
        if (customerId == null || customerId.isBlank()) {
            return "INVALID_CUSTOMER";
        }
        if (amount <= 0) {
            return "INVALID_AMOUNT";
        }
        if (productId == null || productId.isBlank()) {
            return "INVALID_PRODUCT";
        }
        if (amount > 10000) {
            if (requiresApproval(customerId)) {
                return "PENDING_APPROVAL";
            }
        }
        if (isProductAvailable(productId)) {
            reserveProduct(productId);
            chargeCustomer(customerId, amount);
            return "SUCCESS";
        } else {
            return "OUT_OF_STOCK";
        }
    }

    private boolean requiresApproval(String customerId) { return false; }
    private boolean isProductAvailable(String productId) { return true; }
    private void reserveProduct(String productId) {}
    private void chargeCustomer(String customerId, double amount) {}
}