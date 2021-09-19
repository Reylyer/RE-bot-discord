from types import SimpleNamespace
from pyppeteer import launch
import json

textCodeDict = {
  69: "OK",
  420: "NO CREDENTIAL",
  13: "NOT ENOUGH INFORMATION"
}


class Mahasiswa(): #kelas mahasiswa
  def __init__(self, id, mail = "NOT SET", password = "NOT SET"):
      self.id = id
      self.mail = mail
      self.password = password

async def set_credential(ctx, properties, value):
  print(properties)
  print(value)
  if properties == "" or value == "":
    await ctx.send("pastikan pengejaannya benar!")
  else:
    properties = properties.lower()
    if properties in ["mail", "password"]:
      
      with open("MAHASISWA.json", "r+") as f:
        content = f.read()
        #JSON to python Object not dict
        print(f"content = {content}")
        mahasiswas = json.loads(content, object_hook= lambda o: SimpleNamespace(**o))
        print(f"mahasiswas = {mahasiswas}")
        
        for mahasiswa in mahasiswas:
          
          print(f"{mahasiswa.id} == {ctx.author.id}")
          if mahasiswa.id == ctx.author.id:
            if properties == "mail":
              mahasiswa.mail = value
            elif properties == "password":
              mahasiswa.password = value
            # eval(f"mahasiswa.{properties} = \"{value}\"")
            censored = '\*'.join(['' for _ in range(0, len(value) -2)])
            
            await ctx.send(f"{properties} telah diset menjadi {censored}{value[-2]}{value[-1]}")
            break

        else:
          print(ctx.author.id)
          eval(f"mahasiswas.append(Mahasiswa(ctx.author.id, {properties} = '{value}'))")
        await ctx.message.delete()
        print(mahasiswas)
        mahasiswas = json.dumps([mahasiswa.__dict__ for mahasiswa in mahasiswas])
        print(mahasiswas)
        f.seek(0)
        f.write(mahasiswas)
        f.truncate()
        f.close()
    else:
      ctx.send("properti kemungkinan salah pengejaan")
      
async def absen(ctx, codeOrLink):
  with open("MAHASISWA.json", "w+") as f:
    mahasiswas = json.loads(f.read())
    [index, password, mail, resultCode] = await credential_check_of(mahasiswas, ctx.author.id)
    if resultCode == textCodeDict[69]:
      text = "OK"
      browser = await launch(headless = False)
      page = await browser.newPage()
      page.goto("https://form.undip.ac.id/questioner/monitoring_covid#")
    elif resultCode == textCodeDict[420]:
      text = "penuhi credential"
    elif resultCode == textCodeDict[13]:
      text = "belum di inisialisasi"
    f.close()
    
async def credential_check_of(mahasiswas, idTarget):
  textCode = ''
  [password, mail] = ["*", "*"]
  index = None
  for i, mahasiswa in enumerate(mahasiswas):
    if mahasiswa.id == idTarget:
      password = mahasiswa.password
      mail = mahasiswa.mail
      index = i
      if mahasiswa.mail != "*" and mahasiswa.password != "*":
        textCode = textCodeDict[69]
        pass
      else:
        textCode = textCodeDict[13] #belum lengkap credential
      break
  else:
    #not created
    textCode = textCodeDict[420]
  return index, password, mail, textCode
