public class ReportFormatter
{
    private final String currency;

    public ReportFormatter(String currency)
    {
        this.currency = currency;
    }

    public String formatTitle(String title)
    {
        return "=== " + title.toUpperCase() + " ===";
    }

    public String formatSubtitle(String subtitle)
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

    public String formatFooter(String footerText)
    {
        return footerText != null ? "* " + footerText : "";
    }

    public String formatTotal(double total)
    {
        return "TOTAL: " + currency + String.format(" %.2f", total);
    }
}

public class ReportExporter
{
    public void exportToFile(String content, String path)
            throws java.io.IOException
    {
        java.io.FileWriter fw = new java.io.FileWriter(path);
        fw.write(content);
        fw.close();
    }

    public void exportToCsv(List<String[]> rows, String path)
            throws java.io.IOException
    {
        java.io.FileWriter fw = new java.io.FileWriter(path);
        for (String[] row : rows) {
            fw.write(String.join(",", row) + "\\n");
        }
        fw.close();
    }

    public byte[] exportToBytes(String content)
    {
        return content.getBytes(java.nio.charset.StandardCharsets.UTF_8);
    }
}

public class ReportGenerator
{
    private String title;
    private String subtitle;
    private List<String[]> rows = new ArrayList<>();
    private String footerText;
    private boolean showTotals      = true;
    private boolean showPageNumbers = true;

    private final ReportFormatter formatter;
    private final ReportExporter  exporter;

    public ReportGenerator(String title, String subtitle,
                            String dateFormat, String currency)
    {
        this.title     = title;
        this.subtitle  = subtitle;
        this.formatter = new ReportFormatter(currency);
        this.exporter  = new ReportExporter();
    }

    public void addRow(String... columns)    { rows.add(columns); }
    public void setFooter(String text)        { this.footerText = text; }
    public void setShowTotals(boolean show)   { this.showTotals = show; }
    public void setShowPageNumbers(boolean s) { this.showPageNumbers = s; }

    public String buildTextReport()
    {
        StringBuilder sb = new StringBuilder();
        sb.append(formatter.formatTitle(title)).append("\\n");
        sb.append(formatter.formatSubtitle(subtitle)).append("\\n");
        for (String[] row : rows)
            sb.append(formatter.formatRow(row)).append("\\n");
        if (showTotals)
            sb.append(formatter.formatTotal(computeTotal())).append("\\n");
        sb.append(formatter.formatFooter(footerText)).append("\\n");
        if (showPageNumbers)
            sb.append("Page 1 of 1\\n");
        return sb.toString();
    }

    public void exportToFile(String path) throws java.io.IOException
    {
        exporter.exportToFile(buildTextReport(), path);
    }

    public void exportToCsv(String path) throws java.io.IOException
    {
        exporter.exportToCsv(rows, path);
    }

    public byte[] exportToBytes()
    {
        return exporter.exportToBytes(buildTextReport());
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