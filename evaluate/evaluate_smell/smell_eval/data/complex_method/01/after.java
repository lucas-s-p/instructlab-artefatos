public class OrderProcessor
{
    public String validateAndProcess(String customerId, double amount, String productId)
    {
        String validationError = validate(customerId, amount, productId);
        if (validationError != null) return validationError;
        if (amount > 10000 && requiresApproval(customerId)) return "PENDING_APPROVAL";
        return processOrder(customerId, amount, productId);
    }

    private String validate(String customerId, double amount, String productId)
    {
        if (customerId == null || customerId.isBlank()) return "INVALID_CUSTOMER";
        if (amount <= 0)                                return "INVALID_AMOUNT";
        if (productId == null || productId.isBlank())   return "INVALID_PRODUCT";
        return null;
    }

    private String processOrder(String customerId, double amount, String productId)
    {
        if (!isProductAvailable(productId)) return "OUT_OF_STOCK";
        reserveProduct(productId);
        chargeCustomer(customerId, amount);
        return "SUCCESS";
    }

    private boolean requiresApproval(String customerId) { return false; }
    private boolean isProductAvailable(String productId) { return true; }
    private void reserveProduct(String productId) {}
    private void chargeCustomer(String customerId, double amount) {}
}