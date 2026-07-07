public static void main(String[] args) throws Exception {
    File assetsDir = new File(args[0]);
    Collection<String> languagesToTranslate = parseLanguagesToTranslate(assetsDir, args[1]);
    Collection<String> filesToTranslate = parseFilesToTranslate(args);
    for (String language : languagesToTranslate) {
      translateOneLanguage(assetsDir, language, filesToTranslate);
    }
  }
