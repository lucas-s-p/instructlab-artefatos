public static URI unredirect(URI uri) throws IOException {
    if (!REDIRECTOR_DOMAINS.contains(uri.getHost())) {
      return uri;
    }
    URL url = uri.toURL();

    URLConnection conn = url.openConnection();
    if (!(conn instanceof HttpURLConnection)) {
      throw new IOException();
    }
    HttpURLConnection connection = (HttpURLConnection) conn;
    connection.setInstanceFollowRedirects(false);
    connection.setDoInput(false);
    connection.setRequestMethod("HEAD");
    connection.setRequestProperty("User-Agent", "ZXing (Android)");
    try {
      try {
        connection.connect();
      } catch (NullPointerException npe) {
        // this is an Android bug: http://code.google.com/p/android/issues/detail?id=16895
        Log.w(TAG, "Bad URI? " + uri);
        throw new IOException(npe.toString());
      } catch (IllegalArgumentException iae) {
        // Also seen this in the wild, not sure what to make of it. Probably a bad URL
        Log.w(TAG, "Bad URI? " + uri);
        throw new IOException(iae.toString());
      } catch (SecurityException se) {
        // due to bad VPN settings?
        Log.w(TAG, "Restricted URI? " + uri);
        throw new IOException(se);
      }
      int responseCode;
      try {
        responseCode = connection.getResponseCode();
      } catch (NullPointerException npe) {
        // this is maybe this Android bug: http://code.google.com/p/android/issues/detail?id=15554
        Log.w(TAG, "Bad URI? " + uri);
        throw new IOException(npe.toString());
      }
      switch (responseCode) {
        case HttpURLConnection.HTTP_MULT_CHOICE:
        case HttpURLConnection.HTTP_MOVED_PERM:
        case HttpURLConnection.HTTP_MOVED_TEMP:
        case HttpURLConnection.HTTP_SEE_OTHER:
        case 307: // No constant for 307 Temporary Redirect ?
          String location = connection.getHeaderField("Location");
          if (location != null) {
            try {
              return new URI(location);
            } catch (URISyntaxException e) {
              // nevermind
            }
          }
      }
      return uri;
    } finally {
      connection.disconnect();
    }
  }
