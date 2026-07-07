private boolean encodeQRCodeContents(AddressBookParsedResult contact) {
    StringBuilder newContents = new StringBuilder(100);
    StringBuilder newDisplayContents = new StringBuilder(100);
    newContents.append("MECARD:");
    String[] names = contact.getNames();
    if (names != null && names.length > 0) {
      String name = trim(names[0]);
      if (name != null) {
        newContents.append("N:").append(escapeMECARD(name)).append(';');
        newDisplayContents.append(name);
      }
    }
    String[] addresses = contact.getAddresses();
    if (addresses != null) {
      for (String address : addresses) {
        address = trim(address);
        if (address != null) {
          newContents.append("ADR:").append(escapeMECARD(address)).append(';');
          newDisplayContents.append('\n').append(address);
        }
      }
    }
    String[] phoneNumbers = contact.getPhoneNumbers();
    if (phoneNumbers != null) {
      for (String phone : phoneNumbers) {
        phone = trim(phone);
        if (phone != null) {
          newContents.append("TEL:").append(escapeMECARD(phone)).append(';');
          newDisplayContents.append('\n').append(PhoneNumberUtils.formatNumber(phone));
        }
      }
    }
    String[] emails = contact.getEmails();
    if (emails != null) {
      for (String email : emails) {
        email = trim(email);
        if (email != null) {
          newContents.append("EMAIL:").append(escapeMECARD(email)).append(';');
          newDisplayContents.append('\n').append(email);
        }
      }
    }
    String url = trim(contact.getURL());
    if (url != null) {
      newContents.append("URL:").append(escapeMECARD(url)).append(';');
      newDisplayContents.append('\n').append(url);
    }
    // Make sure we've encoded at least one field.
    if (newDisplayContents.length() > 0) {
      newContents.append(';');
      contents = newContents.toString();
      displayContents = newDisplayContents.toString();
      title = activity.getString(R.string.contents_contact);
      return true;
    } else {
      contents = null;
      displayContents = null;
      return false;
    }
  }
