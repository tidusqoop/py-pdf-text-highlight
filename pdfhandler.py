import os
import datetime
import fitz
import PyPDF2 as pypdf
from PyPDF2.generic import (
    DictionaryObject,
    NumberObject,
    FloatObject,
    NameObject,
    ArrayObject,
)

dash_cout = 90

def _print_summary(output_summary_file, summary_json):
    data_path = os.path.join(os.path.dirname(__file__), 'data')
    output_summary_path = os.path.join(data_path, output_summary_file)

    with open(output_summary_path, 'w') as f:
        f.write('target_txt_list:\n')
        for target_txt in summary_json['target_txt_list']:
            f.write('\t- {}\n'.format(target_txt))

        f.write('target_file_list:\n')
        for file_name in summary_json['target_file_list']:
            f.write('\t- {}\n'.format(file_name))

        f.write('summary:\n')
        for target_txt in list(summary_json['summary'].keys()):
            f.write('\t- {}\n'.format(target_txt))

            for file_name in list(summary_json['summary'][target_txt].keys()):
                if len(summary_json['summary'][target_txt][file_name]) > 0:
                    f.write('\t\t- {}: {}\n'.format(file_name, list(set(summary_json['summary'][target_txt][file_name]))))
                else:
                    f.write('\t\t- {}: null\n'.format(file_name))

def find_word(target_file_list, target_txt_list):
    print('='*dash_cout)
    # input param
    print('input param')
    print('\t- target_file_list: {}'.format(target_file_list))
    print('\t- target_txt_list: {}'.format(target_txt_list))

    if (type(target_file_list) != type(list()) or type(target_txt_list) != type(list())):
        print("wrong type input param")
        return

    if (len(target_file_list) == 0) or (len(target_txt_list) == 0):
        print("wrong type input param")
        return

    # output
    print('output')
    output_file_list = list(map(lambda x: 'out_' + x, target_file_list))
    
    now_time = datetime.datetime.now()
    output_summary_file = 'out_summary_{}.txt'.format(now_time.strftime("%Y%m%d_%H%M%S"))
    print('\t- output_file_list: {}'.format(output_file_list))
    print('\t- output_summary_file: {}'.format(output_summary_file))
    summary_json = {
        'target_file_list': target_file_list,
        'target_txt_list': target_txt_list,
        'summary': {}
    }
    for target_txt in target_txt_list:
        summary_json['summary'][target_txt] = {}
        for input_file_name in target_file_list:
            summary_json['summary'][target_txt][input_file_name] = []
    print('='*dash_cout)


    # proc each file
    data_path = os.path.join(os.path.dirname(__file__), 'data')
    for idx, input_file_name in enumerate(target_file_list):
        # input path
        input_path = os.path.join(data_path, input_file_name)
        print('input: {}'.format(input_path))

        # output path
        output_path = os.path.join(data_path, output_file_list[idx])
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
        # print('num pages: {} (pypdf2) / {} (fitz)'.format(num_pages, num_pages_fitz))
        print('num pages: {}'.format(num_pages))

        # find text in pages & create hightlight
        for i in range(num_pages):
            print('searching in page {}..'.format(i+1))
            page_ref = pdf_in_ref.getPage(i)
            page_ref_fitz = pdf_ref_fitz.load_page(i)

            # page size 
            media_box_ref = page_ref['/MediaBox'].getObject()
            page_width = media_box_ref[2]
            page_height = float(media_box_ref[3])
            # print('\tpage size: {}, {}'.format(page_width, page_height))

            # find text
            for target_txt in target_txt_list:
                text_instances = page_ref_fitz.searchFor(target_txt)
                if len(text_instances) > 0:
                    print('\ttarget text: {}'.format(target_txt))
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
                        summary_json['summary'][target_txt][input_file_name].append(i + 1)

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

        print('='*dash_cout)
    
    _print_summary(output_summary_file, summary_json)

if __name__ == "__main__":
    find_word(['sample00.pdf', 'sample01.pdf'], ['love', 'Sample'])