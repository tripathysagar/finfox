"""FASTAPI image uploader"""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_serverMLX.ipynb.

# %% auto 0
__all__ = ['prompt', 'test_server']

# %% ../nbs/01_serverMLX.ipynb 4
import sys


prompt =  """You are an AI specialized in recognizing and extracting text from all images in markdown format.
Your mission is to analyze the image document and generate the result while maintaining data integrity.Extract the each text in details as present. 
It is mission critical. Do not send anything extra. DO NOT MISS ANY INFORMATION. Double check."""

if sys.platform == "darwin":  # init iff the code is running in mac
    from finfox.core import *
    import mlx.core as mx
    from mlx_vlm import load, generate
    from mlx_vlm.prompt_utils import apply_chat_template, get_message_json
    from mlx_vlm.utils import load_config
    # Load the model
    #m_pth = "mlx-community/Qwen2.5-VL-7B-Instruct-bf16"
    m_pth = "mlx-community/Qwen2.5-VL-7B-Instruct-8bit"
    m_pth = "mlx-community/Qwen2.5-VL-7B-Instruct-4bit"
    m_pth = "mlx-community/Qwen2.5-VL-7B-Instruct-3bit"

    model, processor = load(m_pth)
    config = load_config(m_pth)

    formatted_prompt = apply_chat_template(
            processor, config, prompt, num_images=1
        )
    
    mx.eval(model.parameters()) 

# %% ../nbs/01_serverMLX.ipynb 6
from typing import List
from PIL import Image
if sys.platform == "darwin":  

    from fastapi import FastAPI, UploadFile, File, Header, Query
    import io
    from fastcore.all import *

    app = FastAPI()

    @app.post("/upload/")
    async def upload_image(
        files: List[UploadFile] = File(...),
        N: int = Query(..., alias="N")):
        
        im_li = []
        for i, file in enumerate(files):
            # Read the image
            data = await file.read()
            im = Image.open(io.BytesIO(data))
            fn = f"temp_{N}_{i}.png"
            qwen_resize(im, limit=256*3*28*28, fn=fn)
            im_li.append(fn)
        
        if sys.platform == "darwin":  
            return generate(model, 
                            processor, 
                            formatted_prompt,
                            im_li, 
                            verbose=True, 
                            max_tokens=4_056, 
                            repetition_penalty=1.1,
                            temperature=0.2 
                        )
        
        return [len(im_li)]
    
    

# %% ../nbs/01_serverMLX.ipynb 7
import httpx
    

async def test_server(images: List[Image.Image], N:int, url="http://localhost:9000/upload/"):
    """
    check uploading image to the server
    """
    try:
        files = []
        for i, img in enumerate(images):
            try:
                img_copy = img.copy()
                
                byte_arr = io.BytesIO()
                img_copy.save(byte_arr, format='PNG')
                byte_arr.seek(0)
                
                files.append(('files', (f'image_{i}.png', byte_arr.getvalue(), 'image/png')))
            except Exception as img_error:
                print(f"Error processing image {i}: {str(img_error)}")
                raise
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, 
                                         files=files, 
                                         headers= {"N":str(N)},
                                         timeout=600.0)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Server response text: {response.text}")
                return None
                
    except Exception as e:
        print(f"Error during upload: {str(e)}")
        return None
