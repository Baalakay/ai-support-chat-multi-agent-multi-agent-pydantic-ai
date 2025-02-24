import pdfplumber
from pdfplumber.pdf import PDFStructTree
import pandas as pd
import pprint
import re

#mypdf = "../uploads/pdfs/5ace7475-1f69-4918-b22f-1449703155ba_HSR-302R-Series-Rev-G.pdf"
#mypdf = "../uploads/pdfs/b7947df6-147b-4bae-92f8-bfa9bf6c5b09_HSR-520R-Series-Rev-K.pdf"
#mypdf = "../uploads/pdfs/5ace7475-1f69-4918-b22f-1449703155ba_HSR-302R-Series-Rev-G.pdf"
mypdf = "uploads/pdfs/87240fbe-6e79-4f66-a4ab-1b97875d4ea3_HSR-190R-Series-Rev-H.pdf"



def extract_features():
    with pdfplumber.open(mypdf) as pdf:
        p0 = pdf.pages[0]
        feat_bounding_box = (0, 150, 295, 210)
        feat_crop_area = p0.within_bbox(feat_bounding_box)
        feat_crop_text = feat_crop_area.extract_text().split('\n')
        for text in feat_crop_text:
            print(text)
    return ''


def extract_advantages():
    with pdfplumber.open(mypdf) as pdf:
        p0 = pdf.pages[0]
        adv_bounding_box = (300, 150, 610, 210)
        adv_crop_area = p0.within_bbox(adv_bounding_box)
        adv_crop_text = adv_crop_area.extract_text().split('\n')
        for text in adv_crop_text:
            print(text)
    return ''



if __name__ == '__main__':
    #print(extract_text_bbox_keep_chars())
    print(extract_features())
    print(extract_advantages())
