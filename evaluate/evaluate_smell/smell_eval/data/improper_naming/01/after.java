public class OrderProcessor
{
private String customerName;
private double orderTotal;
private String orderStatus;

public OrderProcessor(String customerName, double orderTotal)
{
    this.customerName = customerName;
    this.orderTotal   = orderTotal;
    this.orderStatus  = "PENDING";
}

public void processOrder()
{
    if (orderTotal > 0) {
        orderStatus = "PROCESSING";
        applyDiscount();
    }
}

private void applyDiscount()
{
    if (orderTotal > 1000) {
        orderTotal = orderTotal * 0.9;
    }
}

public String getStatus()
{
    return orderStatus;
}

public double getTotal()
{
    return orderTotal;
}
}