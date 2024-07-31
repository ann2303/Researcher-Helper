import pdfplumber
import PyPDF2



class Pdf:
    def __init__(self, input_pdf):
        self.pdf_opened = pdfplumber.open(input_pdf)

    def extract_text_from_pdf(self):
        text = ""
        for page in self.pdf_opened.pages:
            text += page.extract_text() + "\n"
        return text.strip()

    def crop_image(self, element, pageObj):
        [image_left, image_top, image_right, image_bottom] = element
        pageObj.mediabox.lower_left = (image_left, image_bottom)
        pageObj.mediabox.upper_right = (image_right, image_top)
        return pageObj

    def extract_and_crop_tables(self, output_pdf):
        pdfFileObj = open(self.pdf_opened.stream.name, 'rb')
        pdfReaded = PyPDF2.PdfReader(pdfFileObj)
        cropped_pdf_writer = PyPDF2.PdfWriter()

        for page_num, page in enumerate(self.pdf_opened.pages):
            tables = page.find_tables()
            pageObj = pdfReaded.pages[page_num]
            
            for table in tables:
                pageObj = pdfReaded.pages[page_num]
                table_top = page.height - table.bbox[1]
                table_left = table.bbox[0]
                table_width = table.bbox[2] - table.bbox[0]
                table_right = table_left + table_width
                table_height = table.bbox[3] - table.bbox[1]
                table_bottom = table_top - table_height
                
                cropped_pdf_writer.add_page(self.crop_image((table_left, table_top, table_right, table_bottom), pageObj))

        with open(output_pdf, "wb") as output_file:
            cropped_pdf_writer.write(output_file)

        pdfFileObj.close()

    def close(self):
        self.pdf_opened.close()
        
        
        