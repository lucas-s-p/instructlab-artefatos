static String translateString(String english, String language) throws IOException {
    if ("en".equals(language)) {
      return english;
    }
    String massagedLanguage = LANGUAGE_CODE_MASSAGINGS.get(language);
    if (massagedLanguage != null) {
      language = massagedLanguage;
    }
    System.out.println("  Need translation for " + english);

    long now = System.currentTimeMillis();
    if (now < nextAllowedAPICallTime) {
      try {
        Thread.sleep(nextAllowedAPICallTime - now);
      } catch (InterruptedException ie) {
        // continue
      }
    }
    nextAllowedAPICallTime = now + MIN_API_CALL_INTERVAL_MS;

    URL translateURL = new URL(
        "http://ajax.googleapis.com/ajax/services/language/translate?v=1.0&q=" +
        URLEncoder.encode(english, "UTF-8") +
        "&langpair=en%7C" + language);
    StringBuilder translateResult = new StringBuilder();
    Reader in = null;
    try {
      in = new InputStreamReader(translateURL.openStream(), UTF8);
      char[] buffer = new char[1024];
      int charsRead;
      while ((charsRead = in.read(buffer)) > 0) {
        translateResult.append(buffer, 0, charsRead);
      }
    } finally {
      quietClose(in);
    }
    Matcher m = TRANSLATE_RESPONSE_PATTERN.matcher(translateResult);
    if (!m.find()) {
      System.err.println("No translate result");
      return english;
    }
    String translation = m.group(1);
    System.out.println("  Got translation " + translation);

    // This is a little crude; unescape some common escapes in the raw response
    translation = translation.replaceAll("\\\\u0026quot;", "\"");
    translation = translation.replaceAll("\\\\u0026#39;", "'");
    translation = translation.replaceAll("\\\\u200b", "");

    return translation;
  }
