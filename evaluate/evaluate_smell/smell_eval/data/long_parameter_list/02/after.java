// sendGreetings: 3 params | sendMessage: 2 params — abaixo do threshold

public class SmtpConfig {
    private final String host;
    private final int port;
    private final String sender;

    public SmtpConfig(String host, int port, String sender) {
        this.host = host;
        this.port = port;
        this.sender = sender;
    }

    public String getHost()   { return host;   }
    public int    getPort()   { return port;   }
    public String getSender() { return sender; }
}

public class EmailMessage {
    private final String subject;
    private final String body;
    private final String recipient;

    public EmailMessage(String subject, String body, String recipient) {
        this.subject   = subject;
        this.body      = body;
        this.recipient = recipient;
    }

    public String getSubject()   { return subject;   }
    public String getBody()      { return body;      }
    public String getRecipient() { return recipient; }
}

public class BirthdayService {

    public void sendGreetings(String fileName, OurDate ourDate,
                              SmtpConfig smtp) throws Exception {
        java.io.BufferedReader in = new java.io.BufferedReader(new java.io.FileReader(fileName));
        String str = in.readLine(); // pula cabeçalho
        while ((str = in.readLine()) != null) {
            String[] data = str.split(", ");
            Employee employee = new Employee(data[1], data[0], data[2], data[3]);
            if (employee.isBirthday(ourDate)) {
                EmailMessage email = new EmailMessage(
                        "Happy Birthday!",
                        "Happy Birthday, dear " + employee.getFirstName() + "!",
                        employee.getEmail()
                );
                sendMessage(smtp, email);
            }
        }
    }

    private void sendMessage(SmtpConfig smtp, EmailMessage email) throws Exception {
        java.util.Properties props = new java.util.Properties();
        props.put("mail.smtp.host", smtp.getHost());
        props.put("mail.smtp.port", "" + smtp.getPort());
        System.out.println("Sending from " + smtp.getSender()
                + " to " + email.getRecipient()
                + " via " + smtp.getHost() + ":" + smtp.getPort()
                + " subject=" + email.getSubject());
    }
}
