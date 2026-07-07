public class ReportGenerator
{
private String title;
private String subtitle;
private List<String[]> rows;
private String footerText;
private String dateFormat;
private String currency;
private boolean showTotals;
private boolean showPageNumbers;

public ReportGenerator(String title, String subtitle,
                        String dateFormat, String currency)
{
    this.title       = title;
    this.subtitle    = subtitle;
    this.dateFormat  = dateFormat;
    this.currency    = currency;
    this.rows        = new ArrayList<>();
    this.showTotals  = true;
    this.showPageNumbers = true;
}

public void addRow(String... columns)
{
    rows.add(columns);
}

public void setFooter(String text)
{
    this.footerText = text;
}

public void setShowTotals(boolean show)
{
    this.showTotals = show;
}

public void setShowPageNumbers(boolean show)
{
    this.showPageNumbers = show;
}

public String formatTitle()
{
    return "=== " + title.toUpperCase() + " ===";
}

public String formatSubtitle()
{
    return "--- " + subtitle + " ---";
}

public String formatRow(String[] columns)
{
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < columns.length; i++) {
        sb.append(String.format("%-20s", columns[i]));
        if (i < columns.length - 1) sb.append(" | ");
    }
    return sb.toString();
}

public String formatFooter()
{
    return footerText != null ? "* " + footerText : "";
}

public String formatTotal(double total)
{
    return "TOTAL: " + currency + String.format(" %.2f", total);
}

public String formatDate(java.util.Date date)
{
    return new java.text.SimpleDateFormat(dateFormat).format(date);
}

public String buildTextReport()
{
    StringBuilder sb = new StringBuilder();
    sb.append(formatTitle()).append("\\n");
    sb.append(formatSubtitle()).append("\\n");
    for (String[] row : rows) {
        sb.append(formatRow(row)).append("\\n");
    }
    if (showTotals) {
        sb.append(formatTotal(computeTotal())).append("\\n");
    }
    sb.append(formatFooter()).append("\\n");
    if (showPageNumbers) {
        sb.append("Page 1 of 1\\n");
    }
    return sb.toString();
}

public void exportToFile(String path) throws java.io.IOException
{
    java.io.FileWriter fw = new java.io.FileWriter(path);
    fw.write(buildTextReport());
    fw.close();
}

public void exportToCsv(String path) throws java.io.IOException
{
    java.io.FileWriter fw = new java.io.FileWriter(path);
    for (String[] row : rows) {
        fw.write(String.join(",", row) + "\\n");
    }
    fw.close();
}

public byte[] exportToBytes()
{
    return buildTextReport().getBytes(java.nio.charset.StandardCharsets.UTF_8);
}

private double computeTotal()
{
    double total = 0;
    for (String[] row : rows) {
        if (row.length > 0) {
            try { total += Double.parseDouble(row[row.length - 1]); }
            catch (NumberFormatException ignored) {}
        }
    }
    return total;
}
}