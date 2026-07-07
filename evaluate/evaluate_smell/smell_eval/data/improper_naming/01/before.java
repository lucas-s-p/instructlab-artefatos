public class orderprocessor
{
private String CustomerName;
private double OrderTotal;
private String OrderStatus;

public orderprocessor(String CustomerName, double OrderTotal)
{
    this.CustomerName = CustomerName;
    this.OrderTotal   = OrderTotal;
    this.OrderStatus  = "PENDING";
}

public void ProcessOrder()
{
    if (OrderTotal > 0) {
        OrderStatus = "PROCESSING";
        ApplyDiscount();
    }
}

private void ApplyDiscount()
{
    if (OrderTotal > 1000) {
        OrderTotal = OrderTotal * 0.9;
    }
}

public String GetStatus()
{
    return OrderStatus;
}

public double GetTotal()
{
    return OrderTotal;
}
}