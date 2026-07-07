public static void main(String[] args) throws Exception {

    File assetsDir = new File(args[0]);
    File englishHtmlDir = new File(assetsDir, "html-en");
    String language = args[1];
    File targetHtmlDir = new File(assetsDir, "html-" + language);
    targetHtmlDir.mkdirs();

    final Collection<String> fileNamesToTranslate = new ArrayList<String>();
    for (int i = 2; i < args.length; i++) {
      fileNamesToTranslate.add(args[i]);
    }

    File[] sourceFiles = englishHtmlDir.listFiles(new FilenameFilter() {
      public boolean accept(File dir, String name) {
        return name.endsWith(".html") && (fileNamesToTranslate.isEmpty() || fileNamesToTranslate.contains(name));
      }
    });

    for (File sourceFile : sourceFiles) {

      File destFile = new File(targetHtmlDir, sourceFile.getName());

      DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
      DocumentBuilder builder = factory.newDocumentBuilder();
      Document document = builder.parse(sourceFile);

      Element rootElement = document.getDocumentElement();
      rootElement.normalize();

      Queue<Node> nodes = new LinkedList<Node>();
      nodes.add(rootElement);

      while (!nodes.isEmpty()) {
        Node node = nodes.poll();
        if (shouldTranslate(node)) {
          NodeList children = node.getChildNodes();
          for (int i = 0; i < children.getLength(); i++) {
            nodes.add(children.item(i));
          }
        }
        if (node.getNodeType() == Node.TEXT_NODE) {
          String text = node.getTextContent();
          if (text.trim().length() > 0) {
            text = StringsResourceTranslator.translateString(text, language);
            node.setTextContent(' ' + text + ' ');
          }
        }
      }

      String translationTextTranslated =
          StringsResourceTranslator.translateString("Translated by Google Translate.", language);
      Node translateText = document.createTextNode(translationTextTranslated);
      Node paragraph = document.createElement("p");
      paragraph.appendChild(translateText);
      Node body = rootElement.getElementsByTagName("body").item(0);
      body.appendChild(paragraph);

      DOMImplementationRegistry registry = DOMImplementationRegistry.newInstance();
      DOMImplementationLS impl = (DOMImplementationLS) registry.getDOMImplementation("LS");
      LSSerializer writer = impl.createLSSerializer();
      writer.writeToURI(document, destFile.toURI().toString());
    }
  }
