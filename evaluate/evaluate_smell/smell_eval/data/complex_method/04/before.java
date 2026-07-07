private boolean encodeContents(Intent intent) {
    if (intent == null) {
      return false;
    }
    String type = intent.getStringExtra(Intents.Encode.TYPE);
    if (type == null || type.length() == 0) {
      return false;
    }

    if (type.equals(Contents.Type.TEXT)) {
      String data = intent.getStringExtra(Intents.Encode.DATA);
      if (data != null && data.length() > 0) {
        mContents = data;
        mDisplayContents = data;
        mTitle = mActivity.getString(R.string.contents_text);
      }
    } else if (type.equals(Contents.Type.EMAIL)) {
      String data = intent.getStringExtra(Intents.Encode.DATA);
      if (data != null && data.length() > 0) {
        mContents = "mailto:" + data;
        mDisplayContents = data;
        mTitle = mActivity.getString(R.string.contents_email);
      }
    } else if (type.equals(Contents.Type.PHONE)) {
      String data = intent.getStringExtra(Intents.Encode.DATA);
      if (data != null && data.length() > 0) {
        mContents = "tel:" + data;
        mDisplayContents = PhoneNumberUtils.formatNumber(data);
        mTitle = mActivity.getString(R.string.contents_phone);
      }
    } else if (type.equals(Contents.Type.SMS)) {
      String data = intent.getStringExtra(Intents.Encode.DATA);
      if (data != null && data.length() > 0) {
        mContents = "sms:" + data;
        mDisplayContents = PhoneNumberUtils.formatNumber(data);
        mTitle = mActivity.getString(R.string.contents_sms);
      }
    } else if (type.equals(Contents.Type.CONTACT)) {
      Bundle bundle = intent.getBundleExtra(Intents.Encode.DATA);
      if (bundle != null) {
        StringBuilder newContents = new StringBuilder();
        StringBuilder newDisplayContents = new StringBuilder();
        newContents.append("MECARD:");
        String name = bundle.getString(Contacts.Intents.Insert.NAME);
        if (name != null && name.length() > 0) {
          newContents.append("N:").append(name).append(';');
          newDisplayContents.append(name);
        }
        String address = bundle.getString(Contacts.Intents.Insert.POSTAL);
        if (address != null && address.length() > 0) {
          newContents.append("ADR:").append(address).append(';');
          newDisplayContents.append('\n').append(address);
        }
        for (int x = 0; x < Contents.PHONE_KEYS.length; x++) {
          String phone = bundle.getString(Contents.PHONE_KEYS[x]);
          if (phone != null && phone.length() > 0) {
            newContents.append("TEL:").append(phone).append(';');
            newDisplayContents.append('\n').append(PhoneNumberUtils.formatNumber(phone));
          }
        }
        for (int x = 0; x < Contents.EMAIL_KEYS.length; x++) {
          String email = bundle.getString(Contents.EMAIL_KEYS[x]);
          if (email != null && email.length() > 0) {
            newContents.append("EMAIL:").append(email).append(';');
            newDisplayContents.append('\n').append(email);
          }
        }
        // Make sure we've encoded at least one field.
        if (newDisplayContents.length() > 0) {
          newContents.append(';');
          mContents = newContents.toString();
          mDisplayContents = newDisplayContents.toString();
          mTitle = mActivity.getString(R.string.contents_contact);
        } else {
          mContents = null;
          mDisplayContents = null;
        }
      }
    } else if (type.equals(Contents.Type.LOCATION)) {
      Bundle bundle = intent.getBundleExtra(Intents.Encode.DATA);
      if (bundle != null) {
        // These must use Bundle.getFloat(), not getDouble(), it's part of the API.
        float latitude = bundle.getFloat("LAT", Float.MAX_VALUE);
        float longitude = bundle.getFloat("LONG", Float.MAX_VALUE);
        if (latitude != Float.MAX_VALUE && longitude != Float.MAX_VALUE) {
          mContents = "geo:" + latitude + ',' + longitude;
          mDisplayContents = latitude + "," + longitude;
          mTitle = mActivity.getString(R.string.contents_location);
        }
      }
    }
    return mContents != null && mContents.length() > 0;
  }
