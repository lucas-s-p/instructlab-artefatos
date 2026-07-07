MinimalEncoder(String stringToEncode, Charset priorityCharset, boolean isGS1,
      ErrorCorrectionLevel ecLevel) throws WriterException {

    this.stringToEncode = stringToEncode;
    this.isGS1 = isGS1;
    this.encoders = new ECIEncoderSet(stringToEncode, priorityCharset, -1);
    this.ecLevel = ecLevel;
  }
