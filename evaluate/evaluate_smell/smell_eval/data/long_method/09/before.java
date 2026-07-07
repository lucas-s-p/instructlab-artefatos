static List<Result> processStructuredAppend(List<Result> results) {
    boolean hasSA = false;

    // first, check, if there is at least on SA result in the list
    for (Result result : results) {
      if (result.getResultMetadata().containsKey(ResultMetadataType.STRUCTURED_APPEND_SEQUENCE)) {
        hasSA = true;
        break;
      }
    }
    if (!hasSA) {
      return results;
    }

    // it is, second, split the lists and built a new result list
    List<Result> newResults = new ArrayList<>();
    List<Result> saResults = new ArrayList<>();
    for (Result result : results) {
      if (result.getResultMetadata().containsKey(ResultMetadataType.STRUCTURED_APPEND_SEQUENCE)) {
        saResults.add(result);
      } else {
        newResults.add(result);
      }
    }
    // sort and concatenate the SA list items
    Collections.sort(saResults, new SAComparator());
    StringBuilder concatedText = new StringBuilder();
    int rawBytesLen = 0;
    int byteSegmentLength = 0;
    for (Result saResult : saResults) {
      concatedText.append(saResult.getText());
      rawBytesLen += saResult.getRawBytes().length;
      if (saResult.getResultMetadata().containsKey(ResultMetadataType.BYTE_SEGMENTS)) {
        @SuppressWarnings("unchecked")
        Iterable<byte[]> byteSegments =
            (Iterable<byte[]>) saResult.getResultMetadata().get(ResultMetadataType.BYTE_SEGMENTS);
        for (byte[] segment : byteSegments) {
          byteSegmentLength += segment.length;
        }
      }
    }
    byte[] newRawBytes = new byte[rawBytesLen];
    byte[] newByteSegment = new byte[byteSegmentLength];
    int newRawBytesIndex = 0;
    int byteSegmentIndex = 0;
    for (Result saResult : saResults) {
      System.arraycopy(saResult.getRawBytes(), 0, newRawBytes, newRawBytesIndex, saResult.getRawBytes().length);
      newRawBytesIndex += saResult.getRawBytes().length;
      if (saResult.getResultMetadata().containsKey(ResultMetadataType.BYTE_SEGMENTS)) {
        @SuppressWarnings("unchecked")
        Iterable<byte[]> byteSegments =
            (Iterable<byte[]>) saResult.getResultMetadata().get(ResultMetadataType.BYTE_SEGMENTS);
        for (byte[] segment : byteSegments) {
          System.arraycopy(segment, 0, newByteSegment, byteSegmentIndex, segment.length);
          byteSegmentIndex += segment.length;
        }
      }
    }
    Result newResult = new Result(concatedText.toString(), newRawBytes, NO_POINTS, BarcodeFormat.QR_CODE);
    if (byteSegmentLength > 0) {
      Collection<byte[]> byteSegmentList = new ArrayList<>();
      byteSegmentList.add(newByteSegment);
      newResult.putMetadata(ResultMetadataType.BYTE_SEGMENTS, byteSegmentList);
    }
    newResults.add(newResult);
    return newResults;
  }
