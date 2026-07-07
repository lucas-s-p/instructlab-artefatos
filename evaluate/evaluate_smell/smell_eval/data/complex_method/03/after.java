public DetectorResult detect(Hashtable hints) throws ReaderException {
    if (!BlackPointEstimationMethod.TWO_D_SAMPLING.equals(image
        .getLastEstimationMethod())) {
      image.estimateBlackPoint(BlackPointEstimationMethod.TWO_D_SAMPLING, 0);
    }

    ResultPoint[] vertices = findVertices(image);
    if (vertices == null) { // Couldn't find the vertices
      // Maybe the image is rotated 180 degrees?
      vertices = findVertices180(image);
      /*
      * // Don't need this because the PDF417 code won't fit into // the
      * camera view finder when it is rotated. if (vertices == null) { //
      * Couldn't find the vertices // Maybe the image is rotated 90 degrees?
      * vertices = findVertices90(image); if (vertices == null) { //
      * Couldn't find the vertices // Maybe the image is rotated 270
      * degrees? vertices = findVertices270(image); } }
      */
    }
    if (vertices != null) {
      float moduleWidth = computeModuleWidth(vertices);
      if (moduleWidth < 1.0f) {
        throw ReaderException.getInstance();
      }

      int dimension = computeDimension(vertices[4], vertices[6],
          vertices[5], vertices[7], moduleWidth);

      // Deskew and sample image
      BitMatrix bits = sampleGrid(image, vertices[4], vertices[5],
          vertices[6], vertices[7], dimension);
      //bits.setModuleWidth(moduleWidth);
      return new DetectorResult(bits, new ResultPoint[]{vertices[4],
          vertices[5], vertices[6], vertices[7]});
    } else {
      throw ReaderException.getInstance();
    }
  }
