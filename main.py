import os
import fitz
import PyPDF2 as pypdf
from PyPDF2.generic import (
    DictionaryObject,
    NumberObject,
    FloatObject,
    NameObject,
    ArrayObject,
)

def main():
    # input param
    input_file_name = 'sample00.pdf'
    output_file_name = 'out' + input_file_name
    target_txt_list = ['love', 'Sample']

    # input path
    data_path = os.path.join(os.path.dirname(__file__), 'data')
    input_path = os.path.join(data_path, input_file_name)
    print('input: {}'.format(input_path))

    # output path
    output_path = os.path.join(data_path, output_file_name)
    print('output: {}'.format(output_path))

    # read
    input_stream = open(input_path, 'rb')
    pdf_in_ref = pypdf.PdfFileReader(input_stream)
    pdf_out_ref = pypdf.PdfFileWriter()

    pdf_ref_fitz = fitz.open(input_path)
    print('read done')

    # file info
    num_pages = pdf_in_ref.getNumPages()
    num_pages_fitz = pdf_ref_fitz.page_count
    print('num pages: {} (pypdf2) / {} (fitz)'.format(num_pages, num_pages_fitz))

    # find text in pages & create hightlight
    for i in range(num_pages):
        print('searching in page {}..'.format(i))
        page_ref = pdf_in_ref.getPage(i)
        page_ref_fitz = pdf_ref_fitz.load_page(i)

        # page size 
        media_box_ref = page_ref['/MediaBox'].getObject()
        page_width = media_box_ref[2]
        page_height = float(media_box_ref[3])
        print('\tpage size: {}, {}'.format(page_width, page_height))

        # find text
        for target_txt in target_txt_list:
            print('\ttarget text: {}'.format(target_txt))
            text_instances = page_ref_fitz.searchFor(target_txt)
            if len(text_instances) > 0:
                # extract coordinates
                for text_coordinates in text_instances:
                    x1 = text_coordinates[0]
                    y1 = text_coordinates[1]
                    # y1 = 563.25
                    x2 = text_coordinates[2]
                    y2 = text_coordinates[3]
                    # y2 = 574.25

                    y1_tmp = page_height - y1
                    y2_tmp = page_height - y2
                    y1 = y2_tmp
                    y2 = y1_tmp

                    print('\t\t [{:.2f}, {:.2f}, {:.2f}, {:.2f}]'.format(x1, y1, x2, y2))

                    # make hightlight ref
                    highlight_ref = DictionaryObject()
                    highlight_ref.update({
                        # color
                        NameObject('/C'):ArrayObject([
                            FloatObject(1),
                            FloatObject(0.94118),
                            FloatObject(0.4),
                        ]),
                        # rect
                        NameObject('/Rect'):ArrayObject([
                            FloatObject(x1),       # x1
                            FloatObject(y1),       # y1
                            FloatObject(x2),       # x2
                            FloatObject(y2),       # y2
                        ]),

                        # quad points
                        NameObject("/QuadPoints"): ArrayObject([
                            FloatObject(x1),
                            FloatObject(y2),
                            FloatObject(x2),
                            FloatObject(y2),
                            FloatObject(x1),
                            FloatObject(y1),
                            FloatObject(x2),
                            FloatObject(y1)
                        ]),

                        # Known
                        NameObject('/Type'): NameObject("/Annot"),
                        NameObject('/Subtype'): NameObject("/Highlight"),

                        # Unkown
                        NameObject("/F"): NumberObject(4),
                        NameObject("/CA"): NumberObject(1),
                        # NameObject("/AP"): ?,
                        # NameObject("/PDFIUM_HasGeneratedAP"): ?,
                    })

                    # add highlight to annots in page_ref
                    if "/Annots" in page_ref:
                        page_ref[NameObject("/Annots")].append(highlight_ref)
                    else:
                        page_ref[NameObject("/Annots")] = ArrayObject([highlight_ref])

        # copy to out pdf ref
        pdf_out_ref.addPage(page_ref)
    
    # make new pdf    
    outputStream = open(output_path, 'wb')
    pdf_out_ref.write(outputStream)

if __name__ == "__main__":
    main()