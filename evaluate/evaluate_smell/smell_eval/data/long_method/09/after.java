static List<Result> processStructuredAppend(List<Result> results) {
    List<Result> newResults = new ArrayList<>();
    List<Result> saResults = new ArrayList<>();
    for (Result result : results) {
      if (result.getResultMetadata().containsKey(ResultMetadataType.STRUCTURED_APPEND_SEQUENCE)) {
        saResults.add(result);
      } else {
        newResults.add(result);
      }
    }
    if (saResults.isEmpty()) {
      return results;
    }

    // sort and concatenate the SA list items
    Collections.sort(saResults, new SAComparator());
    StringBuilder newText = new StringBuilder();
    ByteArrayOutputStream newRawBytes = new ByteArrayOutputStream();
    ByteArrayOutputStream newByteSegment = new ByteArrayOutputStream();
    for (Result saResult : saResults) {
      newText.append(saResult.getText());
      byte[] saBytes = saResult.getRawBytes();
      newRawBytes.write(saBytes, 0, saBytes.length);
      @SuppressWarnings("unchecked")
      Iterable<byte[]> byteSegments =
          (Iterable<byte[]>) saResult.getResultMetadata().get(ResultMetadataType.BYTE_SEGMENTS);
      if (byteSegments != null) {
        for (byte[] segment : byteSegments) {
          newByteSegment.write(segment, 0, segment.length);
        }
      }
    }

    Result newResult = new Result(newText.toString(), newRawBytes.toByteArray(), NO_POINTS, BarcodeFormat.QR_CODE);
    if (newByteSegment.size() > 0) {
      newResult.putMetadata(ResultMetadataType.BYTE_SEGMENTS, Collections.singletonList(newByteSegment.toByteArray()));
    }
    newResults.add(newResult);
    return newResults;
  }
