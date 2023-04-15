def overlay_hocr_page(self, dpi, hocr_filename, img_filename):
        hocr_dir, hocr_basename = os.path.split(hocr_filename)
        img_dir, img_basename = os.path.split(img_filename)
        logging.debug("hocr_filename:%s, hocr_dir:%s, hocr_basename:%s" % (hocr_filename, hocr_dir, hocr_basename))
        assert(img_dir == hocr_dir)

        #basename = hocr_basename.split('.')[0]
        basename = os.path.splitext(hocr_basename)[0]
        pdf_filename = os.path.join("text_%s_ocr.pdf" % (basename))

        # Switch to the hocr directory to make this easier
        cwd = os.getcwd()
        if hocr_dir != "":
            os.chdir(hocr_dir)

        with open(pdf_filename, "wb") as f:
            logging.info("Overlaying hocr and creating text pdf %s" % pdf_filename)
            pdf = Canvas(f, pageCompression=1)
            pdf.setCreator('pypdfocr')
            print("pypdfocr")
            pdf.setTitle(os.path.basename(hocr_filename))
            pdf.setPageCompression(1)

            width, height, dpi_jpg = self._get_img_dims(img_basename)
            pdf.setPageSize((width,height))
            logging.info("Page width=%f, height=%f" % (width, height))

            pg_num = 1

            logging.info("Adding text to page %s" % pdf_filename)
            self.add_text_layer(pdf,hocr_basename,pg_num,height,dpi)
            pdf.showPage()
            pdf.save()

        os.chdir(cwd)
        return os.path.join(hocr_dir, pdf_filename)
