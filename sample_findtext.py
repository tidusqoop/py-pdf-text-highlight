import os
import fitz
print(fitz.__doc__)

def main():
    # input param
    input_file_name = 'sample01.pdf'
    target_txt = 'for'

    # input path
    data_path = os.path.join(os.path.dirname(__file__), 'data')
    input_path = os.path.join(data_path, input_file_name)
    print('input: {}'.format(input_path))

    # read
    pdf_ref_fitz = fitz.open(input_path)

    # file info
    num_pages_fitz = pdf_ref_fitz.page_count
    print('num pages: {}'.format(num_pages_fitz))

    # find text
    for i in range(1):
        print('searching in page {}..'.format(i))
        page_ref_fitz = pdf_ref_fitz.load_page(i)
        text_instances = page_ref_fitz.searchFor(target_txt)
        print(len(text_instances))
        print(text_instances)
        for text_coordinates in text_instances:
            x1 = text_coordinates[0]
            y1 = text_coordinates[1]
            x2 = text_coordinates[2]
            y2 = text_coordinates[3]
            print('({}, {}) - ({}, {})'.format(x1, y1, x2, y2))


if __name__ == "__main__":
    main()