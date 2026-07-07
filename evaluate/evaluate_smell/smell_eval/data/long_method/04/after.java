public static void main(String[] args) throws Exception {
    EncoderConfig config = new EncoderConfig();
    JCommander jCommander = new JCommander(config, args);
    jCommander.setProgramName(CommandLineEncoder.class.getSimpleName());
    if (config.help) {
      jCommander.usage();
      return;
    }

    String outFileString = config.outputFileBase;
    if (EncoderConfig.DEFAULT_OUTPUT_FILE_BASE.equals(outFileString)) {
      outFileString += '.' + config.imageFormat.toLowerCase(Locale.ENGLISH);
    }
    
    BitMatrix matrix = new MultiFormatWriter().encode(
        config.contents.get(0), config.barcodeFormat, config.width, config.height);
    MatrixToImageWriter.writeToPath(matrix, config.imageFormat, Paths.get(outFileString));
  }
