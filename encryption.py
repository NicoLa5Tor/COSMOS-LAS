import os
class EnviromentVals:
    def key(self):
       api_key = os.environ.get('key_azure')
     #  print(api)
       return api_key


