public BufferedImageLuminanceSource(BufferedImage image, int left, int top, int width, int height) {
    super(width, height);

    if (image.getType() == BufferedImage.TYPE_BYTE_GRAY) {
      this.image = image;
    } else {
      int sourceWidth = image.getWidth();
      int sourceHeight = image.getHeight();
      if (left + width > sourceWidth || top + height > sourceHeight) {
        throw new IllegalArgumentException("Crop rectangle does not fit within image data.");
      }

      this.image = new BufferedImage(sourceWidth, sourceHeight, BufferedImage.TYPE_BYTE_GRAY);

      WritableRaster raster = this.image.getRaster();
      int[] buffer = new int[width];
      for (int y = top; y < top + height; y++) {
        image.getRGB(left, y, width, 1, buffer, 0, sourceWidth);
        for (int x = 0; x < width; x++) {
          int pixel = buffer[x];

          // The color of fully-transparent pixels is irrelevant. They are often, technically, fully-transparent
          // black (0 alpha, and then 0 RGB). They are often used, of course as the "white" area in a
          // barcode image. Force any such pixel to be white:
          if ((pixel & 0xFF000000) == 0) {
            pixel = 0xFFFFFFFF; // = white
          }

          // .229R + 0.587G + 0.114B (YUV/YIQ for PAL and NTSC)
          buffer[x] =
              (306 * ((pixel >> 16) & 0xFF) +
               601 * ((pixel >> 8) & 0xFF) +
               117 * (pixel & 0xFF) +
               0x200) >> 10;
        }
        raster.setPixels(left, y, width, 1, buffer);
      }

    }
    this.left = left;
    this.top = top;
  }
