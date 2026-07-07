// Fonte: Codesai/code-smells-refactoring-training-java — birthday greetings kata (adaptado)
// sendGreetings: 4 params | sendMessage: 6 params → ambos ≥ threshold=4

public class BirthdayService {

    public void sendGreetings(String fileName, OurDate ourDate,
                              String smtpHost, int smtpPort) throws Exception {
        java.io.BufferedReader in = new java.io.BufferedReader(new java.io.FileReader(fileName));
        String str = in.readLine(); // pula cabeçalho
        while ((str = in.readLine()) != null) {
            String[] data = str.split(", ");
            Employee employee = new Employee(data[1], data[0], data[2], data[3]);
            if (employee.isBirthday(ourDate)) {
                String recipient = employee.getEmail();
                String body = "Happy Birthday, dear " + employee.getFirstName() + "!";
                String subject = "Happy Birthday!";
                sendMessage(smtpHost, smtpPort, "sender@here.com", subject, body, recipient);
            }
        }
    }

    private void sendMessage(String smtpHost, int smtpPort, String sender,
                             String subject, String body, String recipient) throws Exception {
        java.util.Properties props = new java.util.Properties();
        props.put("mail.smtp.host", smtpHost);
        props.put("mail.smtp.port", "" + smtpPort);
        System.out.println("Sending from " + sender + " to " + recipient
                + " via " + smtpHost + ":" + smtpPort
                + " subject=" + subject + " body=" + body);
    }
}
