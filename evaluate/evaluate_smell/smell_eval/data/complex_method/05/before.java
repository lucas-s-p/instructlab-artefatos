private Result doDecode(MonochromeBitmapSource image, Hashtable hints, boolean tryHarder) throws ReaderException {

    int width = image.getWidth();
    int height = image.getHeight();

    BitArray row = new BitArray(width);

    int barcodesToSkip = 0;
    if (hints != null) {
      Integer number = (Integer) hints.get(DecodeHintType.SKIP_N_BARCODES);
      if (number != null) {
        barcodesToSkip = number.intValue();
      }
    }

    // We're going to examine rows from the middle outward, searching alternately above and below the middle,
    // and farther out each time. rowStep is the number of rows between each successive attempt above and below
    // the middle. So we'd scan row middle, then middle - rowStep, then middle + rowStep,
    // then middle - 2*rowStep, etc.
    // rowStep is bigger as the image is taller, but is always at least 1. We've somewhat arbitrarily decided
    // that moving up and down by about 1/16 of the image is pretty good; we try more of the image if
    // "trying harder"
    int middle = height >> 1;
    int rowStep = Math.max(1, height >> (tryHarder ? 7 : 4));
    int maxLines;
    if (tryHarder || barcodesToSkip > 0) {
      maxLines = height; // Look at the whole image; looking for more than one barcode
    } else {
      maxLines = 7;
    }

    Result lastResult = null;

    for (int x = 0; x < maxLines; x++) {

      int rowStepsAboveOrBelow = (x + 1) >> 1;
      boolean isAbove = (x & 0x01) == 0; // i.e. is x even?
      int rowNumber = middle + rowStep * (isAbove ? rowStepsAboveOrBelow : -rowStepsAboveOrBelow);
      if (rowNumber < 0 || rowNumber >= height) {
        break;
      }

      try {
        image.estimateBlackPoint(BlackPointEstimationMethod.ROW_SAMPLING, rowNumber);
      } catch (ReaderException re) {
        continue;
      }
      image.getBlackRow(rowNumber, row, 0, width);

      for (int attempt = 0; attempt < 2; attempt++) {
        if (attempt == 1) { // trying again?
          if (tryHarder) { // only if "trying harder"
            row.reverse(); // reverse the row and continue
          } else {
            break;
          }
        }
        try {
          Result result = decodeRow(rowNumber, row, hints);
          if (lastResult == null || !lastResult.getText().equals(result.getText())) {
            // Found new barcode, not just the last one again
            if (barcodesToSkip > 0) { // See if we should skip and keep looking
              barcodesToSkip--;
              lastResult = result; // Remember what we just saw
            } else {
              if (attempt == 1) {
                // Found it, but upside-down:
                result.putMetadata(ResultMetadataType.ORIENTATION, new Integer(180));
              }
              return result;
            }
          }
        } catch (ReaderException re) {
          // continue
        }
      }
    }

    throw new ReaderException("No barcode found");
  }
