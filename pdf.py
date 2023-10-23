from PyPDF2 import PdfFileWriter, PdfFileReader,PdfFileMerger
import os
import glob
import time

def remove_blank():
    files = os.listdir('temp')
    print(len(files))
    for i in range(len(files)):
        input_pdf = PdfFileReader(open(f"temp/temp{i}.pdf", "rb"))
        output_pdf = PdfFileWriter()
        output_pdf.addPage(input_pdf.getPage(0))
        with open(f"temp\_temp{i}.pdf", "wb") as output_file:
            output_pdf.write(output_file)

def remove_all_file():
    folder_path = 'temp'
    file_list = glob.glob(folder_path + '/*')
    for file_path in file_list:
        os.remove(file_path)
    
    
def merge(name):
    remove_blank()
    time.sleep(2)
    pdf_count = 0
    files = os.listdir('temp')
    pdf_count = int(len(files)/2)
    merger = PdfFileMerger()
    print(pdf_count)
    for i in range(pdf_count):
        file_name = f"temp/_temp{i}.pdf"
        merger.append(open(file_name, "rb"))
    with open(f"pdfs/{name}.pdf", "wb") as output_file:
        merger.write(output_file)
        time.sleep(2)
    
    time.sleep(2)

# merge("new")
