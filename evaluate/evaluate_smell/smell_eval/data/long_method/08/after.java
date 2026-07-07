public static String guessEncoding(byte[] bytes, Map<DecodeHintType,?> hints) {
      Charset c = guessCharset(bytes, hints);
      if (c == SHIFT_JIS_CHARSET) {
          return "SJIS";
      } else if (c == StandardCharsets.UTF_8) {
          return "UTF8";
      } else if (c == StandardCharsets.ISO_8859_1) {
          return "ISO8859_1";
      }
      return c.name();
  }
