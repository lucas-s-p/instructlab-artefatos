static int lookAheadTest(CharSequence msg, int startpos, int currentMode) {
    int newMode = lookAheadTestIntern(msg, startpos, currentMode);
    if (currentMode == X12_ENCODATION && newMode == X12_ENCODATION) {
      int endpos = Math.min(startpos + 3, msg.length());
      for (int i = startpos; i < endpos; i++) {
        if (!isNativeX12(msg.charAt(i))) {
          return ASCII_ENCODATION;
        }
      }
    } else if (currentMode == EDIFACT_ENCODATION && newMode == EDIFACT_ENCODATION) {
      int endpos = Math.min(startpos + 4, msg.length());
      for (int i = startpos; i < endpos; i++) {
        if (!isNativeEDIFACT(msg.charAt(i))) {
          return ASCII_ENCODATION;
        }
      }
    }
    return newMode;
  }
