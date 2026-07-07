private boolean encodeContents(Intent intent) {
    if (intent == null) {
      return false;
    }
    
    // default to QR_CODE if no format given
    String format = intent.getStringExtra(Intents.Encode.FORMAT);
    if (format == null || format.length() == 0 || 
        format.equals(Contents.Format.QR_CODE)) {
      String type = intent.getStringExtra(Intents.Encode.TYPE);
      if (type == null || type.length() == 0) {
        return false;
      }
      mFormat = BarcodeFormat.QR_CODE;
      encodeQRCodeContents(intent, type);
    } else {
      String data = intent.getStringExtra(Intents.Encode.DATA);
      if (data != null && data.length() != 0) {
        mContents = data;
        mDisplayContents = data;
        mTitle = mActivity.getString(R.string.contents_text);
        if (format.equals(Contents.Format.CODE_128))
          mFormat = BarcodeFormat.CODE_128;
        else if (format.equals(Contents.Format.CODE_39))
          mFormat = BarcodeFormat.CODE_39;
        else if (format.equals(Contents.Format.EAN_8))
          mFormat = BarcodeFormat.EAN_8;
        else if (format.equals(Contents.Format.EAN_13))
          mFormat = BarcodeFormat.EAN_13;
        else if (format.equals(Contents.Format.UPC_A))
          mFormat = BarcodeFormat.UPC_A;
        else if (format.equals(Contents.Format.UPC_E))
          mFormat = BarcodeFormat.UPC_E;
      }
    }
    return mContents != null && mContents.length() > 0;
  }
