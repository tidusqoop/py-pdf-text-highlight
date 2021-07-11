import os
import PyPDF2 as pypdf
from PyPDF2.generic import (
    DictionaryObject,
    NumberObject,
    FloatObject,
    NameObject,
    TextStringObject,
    ArrayObject,
    IndirectObject
)

def main():
    # input param
    input_file_name = 'sample01.pdf'
    output_file_name = 'outsample01.pdf'
    target_txt = 'TURNKEY'

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
    print('read done')

    # file info
    num_pages = pdf_in_ref.getNumPages()
    print('num pages: {}'.format(num_pages))

    # find text in pages & create hightlight
    # for i in range(num_pages):
    for i in range(2):
        print('searching in page {}..'.format(i))
        page_ref = pdf_in_ref.getPage(i)
        print('\t page')
        print(page_ref)
        
        print('\t content')
        contents_ref = page_ref.getContents()
        print(contents_ref)

        # print('\t contents_ref')
        # contents_ref = page_ref['/Contents'].getObject()
        # print(contents_ref)

        # print('\t text')
        # text = page_ref.extractText()
        # print(text)

        # if "/Annots" in page_ref:
        #     print('\t annots')
        #     annots_ref = page_ref['/Annots'].getObject()
        #     print(annots_ref[0].getObject())
        #     print(annots_ref[1].getObject())
        
        # modify pages
        highlight_ref = None
        try:
            highlight_ref = DictionaryObject()
            x1 = 245
            y1 = 563.25
            x2 = 265
            y2 = 574.2
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

            if "/Annots" in page_ref:
                page_ref[NameObject("/Annots")].append(highlight_ref)
            else:
                page_ref[NameObject("/Annots")] = ArrayObject([highlight_ref])
        except Exception as e:
            print('err: {}'.format(e))

        pdf_out_ref.addPage(page_ref)
        print('='*40)

    # make new pdf    
    outputStream = open(output_path, 'wb')
    pdf_out_ref.write(outputStream)

    pass

if __name__ == "__main__":
    main()