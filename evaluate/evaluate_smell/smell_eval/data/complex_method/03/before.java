public DetectorResult detect(Hashtable hints) throws ReaderException {
      if (!BlackPointEstimationMethod.TWO_D_SAMPLING.equals(image
            .getLastEstimationMethod())) {
         image.estimateBlackPoint(BlackPointEstimationMethod.TWO_D_SAMPLING, 0);
      }
      int width = image.getWidth();
      int height = image.getHeight();
      if (debug)
         System.out.println("Width= " + width);
      if (debug)
         System.out.println("Height= " + height);

      long t2;
      long t1 = System.currentTimeMillis();
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
         if (debug) {
            t2 = System.currentTimeMillis();
            System.out.println("Elapsed time in ms - Find Vertices "
                  + (t2 - t1));
         }

         float moduleWidth = computeModuleWidth(vertices);
         if (moduleWidth < 1.0f) {
            if (debug)
               System.out.println("Module Size is less than 1.0f="
                     + moduleWidth);
            throw ReaderException.getInstance();
         }
         if (debug)
            System.out.println("Module Size=" + moduleWidth);

         int dimension = computeDimension(vertices[4], vertices[6],
               vertices[5], vertices[7], moduleWidth);
         if (debug)
            System.out.println("Dimension=" + dimension);

         // Deskew and sample image
         t1 = System.currentTimeMillis();
         BitMatrix bits = sampleGrid(image, vertices[4], vertices[5],
               vertices[6], vertices[7], dimension);
         //bits.setModuleWidth(moduleWidth);
         if (debug) {
            t2 = System.currentTimeMillis();
            System.out
                  .println("Elapsed time in ms - Sampled Grid " + (t2 - t1));
         }
         return new DetectorResult(bits, new ResultPoint[] { vertices[4],
               vertices[5], vertices[6], vertices[7] });
      } else {
         if (debug) {
            System.out.println("Unable to locate vertices");
         }
         throw ReaderException.getInstance();
      }
   }
