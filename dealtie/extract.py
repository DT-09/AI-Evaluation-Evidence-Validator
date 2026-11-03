import io
import re
import pandas as pd

def excel_col(n):
    s=""
    while n:
        n,r=divmod(n-1,26)
        s=chr(65+r)+s
    return s

def extract_excel(data, filename):
    book=pd.ExcelFile(io.BytesIO(data))
    out=[]
    for sheet in book.sheet_names:
        frame=pd.read_excel(io.BytesIO(data),sheet_name=sheet,header=None,dtype=object)
        for ri,row in frame.iterrows():
            for ci,value in row.items():
                if pd.notna(value) and str(value).strip():
                    out.append({"document":filename,"source_ref":f"{sheet}!{excel_col(int(ci)+1)}{int(ri)+1}","extracted_text":str(value)})
    return out

def extract_pdf(data, filename):
    from pypdf import PdfReader
    reader=PdfReader(io.BytesIO(data))
    out=[]
    for page_no,page in enumerate(reader.pages,1):
        for line_no,line in enumerate((page.extract_text() or "").splitlines(),1):
            line=re.sub(r"\\s+"," ",line).strip()
            if line:
                out.append({"document":filename,"source_ref":f"PDF p.{page_no}, line {line_no}","extracted_text":line})
    return out
