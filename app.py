from potassium import Potassium, Request, Response
import subprocess
import uuid
import os
import requests

app = Potassium("nougat")

def get_pdf(pdf_link):
  dir_name = "input"
  if not os.path.exists(dir_name):
      os.makedirs(dir_name)
  unique_filename = f"{dir_name}/downloaded_paper_{uuid.uuid4().hex}.pdf"
  response = requests.get(pdf_link)
  if response.status_code == 200:
      with open(unique_filename, 'wb') as pdf_file:
          pdf_file.write(response.content)
  return unique_filename

def nougat_ocr(file_name):
  cli_command = [
      'nougat',
      '--out', 'output',
      'pdf', f'{file_name}',
      '--checkpoint', 'nougat',
      '--markdown'
  ]
  subprocess.run(cli_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
  return

@app.init
def init():
    #no need for context
    context = {}
    return context

@app.handler()
def handler(context: dict, request: Request) -> Response:
    pdf_link = request.json.get("pdf_link")
    if pdf_link is None:
        return Response(json = {"message": "No data provided. Make sure to provide a pdf link and try again!"}, status=400)
    else:
        file_name = get_pdf(pdf_link)
    nougat_ocr(file_name)
    file_name = file_name.split('/')[-1][:-4]
    with open(f'output/{file_name}.mmd', 'r') as file:
        content = file.read()
    content = content.replace(r'\(', '$').replace(r'\)', '$').replace(r'\[', '$$').replace(r'\]', '$$')
    return Response(json = {"content": content}, status=200)

if __name__ == "__main__":
    app.serve()