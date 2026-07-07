public DetectorResult detect(Hashtable hints) throws ReaderException {

    MonochromeBitmapSource image = this.image;
    if (!BlackPointEstimationMethod.TWO_D_SAMPLING.equals(image.getLastEstimationMethod())) {
      image.estimateBlackPoint(BlackPointEstimationMethod.TWO_D_SAMPLING, 0);
    }

    FinderPatternFinder finder = new FinderPatternFinder(image);
    FinderPatternInfo info = finder.find(hints);

    return processFinderPatternInfo(info);
  }
