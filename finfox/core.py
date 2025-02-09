"""Fill in a module description here"""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_core.ipynb.

# %% auto 0
__all__ = ['make_dirs', 'download_url', 'rn_zip_extract', 'download_rename', 'pdfPC', 'pdf2imgOffset', 'devide_img', 'save_md']

# %% ../nbs/00_core.ipynb 3
import httpx
import zipfile
from fastcore.all import *
from fastcore.utils import *
import pandas as pd

# %% ../nbs/00_core.ipynb 5
def make_dirs(base:Path, df:pd.core.frame.DataFrame):
    """
    Takes in base directory make all the directory for given dataframe wrt index and and columns in hierarchy
    Example:
    If df has columns ['A', 'B'] and index ['X', 'Y'], the following structure is created:
    
    base/
    ├── A/
    │   ├── X/
    │   └── Y/
    └── B/
        ├── X/
        └── Y/
    """
    base.mkdir(exist_ok=True)
    for c in df.columns:
        dir = base/c
        dir.mkdir(exist_ok=True)
        for i in df.index:
            if "Right " not in i:
                (dir/i).mkdir(exist_ok=True)

# %% ../nbs/00_core.ipynb 8
import httpx
async def download_url(url:str, fn:Path):
    """
    download given url and write it a given fn.
    """
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/pdf,*/*'
    }
    timeout = httpx.Timeout(connect=20.0, read=120.0, write=30.0, pool=60.0)

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        try:
            res = await client.get(url, headers=headers)
            if res.status_code == 200:
                with open(fn, 'wb') as f:
                    f.write(res.content)
                return True
            else:
                print(f"Error downloading: Status code {res.status_code}")
                return False
        except httpx.RequestError as e:
            print(f"Request failed: {e}")
            return False

# %% ../nbs/00_core.ipynb 12
def rn_zip_extract(zipf, fn):
    """
    Donwload and extract the given files with filename fn 
    """
    home = Path(zipf).parent
    with zipfile.ZipFile(zipf, 'r') as zip_ref:
        f = zip_ref.namelist()[0]
        zip_ref.extractall(path=home)
        fi = home/f
        fi.rename(fn)

# %% ../nbs/00_core.ipynb 15
async def download_rename(url, fn, dir):
    """
    download given url and rename the file only handles zip and pdf
    """
    fn, dir = Path(fn), Path(dir)
    dir.mkdir(exist_ok=True)

    if ".zip" in url:
        zip = dir/"temp.zip"
        await download_url(url, zip)
        rn_zip_extract(zip, fn)
        Path(dir/"temp.zip").unlink()
    elif ".pdf" in url:
        await download_url(url, fn)

# %% ../nbs/00_core.ipynb 19
import PyPDF2

def pdfPC(pth):
    """
    given pdf file name returns the no of pages 
    """
    with open(pth, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        return len(reader.pages)

# %% ../nbs/00_core.ipynb 21
from pdf2image import convert_from_path
from PIL.PpmImagePlugin import PpmImageFile
from typing import Tuple, Callable, List, Optional
from PIL import Image

# %% ../nbs/00_core.ipynb 22
def pdf2imgOffset(
    fn: str, 
    limit: Tuple[int, int], 
    transform: Optional[Callable[[Image.Image], Image.Image]] = None,
    dir:Optional[Path] = None) -> List[Image.Image]:
    """
    given a pdf file it `fn` and limit -> [first_page, last_page] it return pdf in image
    transform: performs the operation on a given image if given
    dir: save the images to a file
    """
    fp, lp = limit
    ims =  convert_from_path(str(fn), dpi=200, first_page=fp, last_page=lp)
    
    if transform is not None:
        ims = [transform(i) for i in ims]

    if dir:
        [im.save(dir/"{0}.png".format(fp+i)) for i, im in enumerate(ims) ]  
    else:  
        return ims

# %% ../nbs/00_core.ipynb 23
def devide_img(im:Image, n:float=0.5):
    """
    Devide the image by factor `n`
    """
    w, h = im.size
    im.thumbnail((int(w*n), int(h*n) ), Image.LANCZOS)
    return im

# %% ../nbs/00_core.ipynb 33
def save_md(fn: str, txt: str):
    """
    Writes the given text to a markdown file as binary (UTF-8 encoded).
    Parameters:
    fn (str): Filename or path to save the markdown file.
    txt (str): Content to write to the file.
    """
    try:
        # Open the file in binary write mode and encode the text to bytes
        with open(fn, 'wb') as f:
            f.write(txt.encode('utf-8'))
    except Exception as e:
        print(f"Error writing to file {fn}: {e}")
    
