MinimalEncoder(String stringToEncode, Charset priorityCharset, boolean isGS1,
      ErrorCorrectionLevel ecLevel) throws WriterException {

    this.stringToEncode = stringToEncode;
    this.isGS1 = isGS1;
    this.ecLevel = ecLevel;

    List<CharsetEncoder> neededEncoders = new ArrayList<>();
    neededEncoders.add(StandardCharsets.ISO_8859_1.newEncoder());
    boolean needUnicodeEncoder = priorityCharset != null && priorityCharset.name().startsWith("UTF");

    for (int i = 0; i < stringToEncode.length(); i++) {
      boolean canEncode = false;
      for (CharsetEncoder encoder : neededEncoders) {
        if (encoder.canEncode(stringToEncode.charAt(i))) {
          canEncode = true;
          break;
        }
      }

      if (!canEncode) {
        for (CharsetEncoder encoder : ENCODERS) {
          if (encoder.canEncode(stringToEncode.charAt(i))) {
            neededEncoders.add(encoder);
            canEncode = true;
            break;
          }
        }
      }

      if (!canEncode) {
        needUnicodeEncoder = true;
      }
    }

    if (neededEncoders.size() == 1 && !needUnicodeEncoder) {
      encoders = new CharsetEncoder[] { neededEncoders.get(0) };
    } else {
      encoders = new CharsetEncoder[neededEncoders.size() + 2];
      int index = 0;
      for (CharsetEncoder encoder : neededEncoders) {
        encoders[index++] = encoder;
      }

      encoders[index] = StandardCharsets.UTF_8.newEncoder();
      encoders[index + 1] = StandardCharsets.UTF_16BE.newEncoder();
    }

    int priorityEncoderIndexValue = -1;
    if (priorityCharset != null) {
      for (int i = 0; i < encoders.length; i++) {
        if (encoders[i] != null && priorityCharset.name().equals(encoders[i].charset().name())) {
          priorityEncoderIndexValue = i;
          break;
        }
      }
    }
    priorityEncoderIndex = priorityEncoderIndexValue;
  }
