#!/usr/bin/env python
# coding=utf-8
# author:jingjian@datagrand.com
# datetime:2019/11/15 下午4:49
import os, sys, re, json, traceback, time
from  Crypto.Cipher import DES3
import base64
import binascii

class Prpcrypt():
    def __init__(self):
        self.mode = DES3.MODE_ECB # 加密模式
        self.BS = DES3.block_size

    def pad(self,s):
        # bw = self.BS - len(s) % self.BS
        # if bw!=8:
        #     # 每8位一组，不足8位需要补位。
        #     return s + (self.BS - len(s) % self.BS) * chr(self.BS - len(s) % self.BS)
        # else:
        #     return s
        return s + (self.BS - len(s) % self.BS) * chr(self.BS - len(s) % self.BS)

    def unpad(self,s):
        # bw = self.BS - len(s) % self.BS
        # if bw !=8:
        #     return s[0:-ord(s[-1])]
        # return s
        return s[0:-ord(s[-1])]

    def encrypt(self, text,key):
        # 加密
        text = self.pad(text)

        cryptor = DES3.new(key, self.mode)
        x = len(text) % 8
        if x != 0:
            text = text + '\0' * (8 - x)
        # print(text)
        self.ciphertext = cryptor.encrypt(text)
        return base64.standard_b64encode(self.ciphertext).decode("utf-8")

    def decrypt(self, text,key):
        # 解密
        cryptor = DES3.new(key, self.mode)
        de_text = base64.standard_b64decode(text)
        plain_text = cryptor.decrypt(de_text)
        st = str(plain_text.decode("utf-8")).rstrip('\0')
        out = self.unpad(st)
        return out

if __name__ == "__main__":
    p = Prpcrypt()
    from conf.conf import DOC_IN_CHECK_REDIECT_KEY
    from conf.conf import des3_key
    # text = '{"agreeNum":"2071910176560001"}'
    # # key = "12"
    # content = 'jPfBEriddtfk6HDmXOOzQk5ct/UeFklcV7oItOs9Kq+3pm5GfkDwbM/pwqaGg9HIzB/RGaBAd044bCZZStxXKhwGQCjqC3hHyr4HGxg10ues9oJkK3ZxnCfpeWB4KON2b7MJthJabjV08+CP3a3qDRLG2OghYLkwdchxop+I3vazxdSNY1TBraGpBbNM2nN+GUkSs6BMKQcUfETtsrikAtWKyVsVTZW4IZ2wIEUJARK1ZE30kp8tV5koKdmWni6Ii3Sh7gGvxy46sOfk014mjseEJdzMYcMHtLYLumi+aqo6Z1U+U9qaEJaMj38xPo1SvLyWiv5T1kDZsh1WCuK/3qZILvBLqYSXfN8WLd2GeQ6vHec7GOtW2owZE68p06eMIXn4NwGkX8YlK3lBcK3cFTEo9Y07ZsBYy2q9DqlsDciCCD/bGY+6woJQLXxf8oNKKR7F2X5lm7ZRSj1CvWipdQxRL4iYGqwTzPK6HuU0qsp3ig03Ib5VBIunlreC4z+JGHi3q02DTnDyZ/YOmff9hiUreUFwrdwVMSj1jTtmwFiXw48HWKOy7BnMANNnNSQEbLTu3LrSV6XHzYt4+PtD0WkBRE5qo1dUjmr2QIc1dnDf2UtzESxrI4Ad+qaNMehE7VJL6ErLMZX3+Rm98xPpMW8E9WTypYhG7WuO/MG6rZhQQFWIMj7G4s5aL1lYV0nZ+HdxnJP5PHLgqfDRVE4GtMKqFjt8gn6GZyAuvhR8L2f2FEWqPEHijFh45p5HlVVS0KPANjbNxnSbLSaUwnjsdLrJwUZFSecCsAj60kktSA4srO7X4S6BzefRvFMzrbBIVXy9PJwLeXF5MnFbASZ7PXOi1kXwPYsanwODuGgQMlkQV/Zw5AE/3CRyIdtdU9BefSkAtS+vIvghGDA8gcSs0OS9JZfoAuoIvLyWiv5T1kCHE/935tuGAZtkeUsbwELr1HFA/Tkm6AIah2KjCvsdqssFLBVR5HtM8uERX9eckSfLwJwatMYuIU/+jSpvdsqcHka2r8OOfp6+HqpQYPLCH7y8lor+U9ZAhxP/d+bbhgGnT4F7A9vaGVJSgMJu2U2tWo83FERtz8uCUC18X/KDSikexdl+ZZu2UUo9Qr1oqXUFSADHeiDMEjT/8SD1tYl7SfXoHgJT/dyxoddX54czJI7P0f/Gs2qWu/ZOB9Dz02C6CAbfN9N99/aqmxPyFJSmGHi3q02DTnDyZ/YOmff9hiUreUFwrdwVkQfShXT5Ipyf0nAIs20TN9K3Q5RsWAThCHBaIPrC42OZfnPYImCSNqRGZVppkCId0uwwjDwyTD6tMeFGhehOKSUreUFwrdwVa31eXRkGuVE29pX+8qLuRW1oBhJ4CSkjUD466xvZUyn3+Rm98xPpMZTTRlO2bpZzVG10VdNLn+g5Vcy2EoK9Z/g/19qVO9Ige3fSVhXomsUwZHCYx/aq7qRhVCeL/Vn2dMFJU0zvXzRQNnZuUjI81uN8GhyljRz+hC6Gyiyk4KXmox4T3gx4UDb99zal/Skpp8u+ktIbrfPEjFLS1GQSR+fz/dZHy8UiLakmzC3cV/s/eNNgNo4KL+M+H/5II2zIt3WxxRshLgoTFM5uMM90I8LVddxzB0tQPhHpNqnVhXEWXAW+64Mi9AvP7IojsFm99fP5mXZnnfJD8fy7iJ7E5sr2w7bhu50D49lfL+uXT+Hmox4T3gx4UDb99zal/SkpFGIAWAlLNKViTb+vLIsG9wkyUWQk7RLiyQTkdx4T2Q4aCok/9aUIL6SD9fOK8lKu9tvFwKK3qHcaYOhBcLsVRHspRYqbztRAbdqrDTY6DuT6v5+BM5J9f6lDAy1btkDEz3o39Ntg6ft7d9JWFeiaxTBkcJjH9qrukbz4dhYJLk90wUlTTO9fNLnBMYYzugg+43waHKWNHP4KN5Tqw9R3HVGLWWs3JEIixIxS0tRkEkfn8/3WR8vFIi2pJswt3Ff7P3jTYDaOCi/jPh/+SCNsyLd1scUbIS4KExTObjDPdCPC1XXccwdLUJIsndJO6rUxARJgkqOTtjiwC9YEHemeMkREP6i5BAZWvrjRwLqV962F/93F42x9WwCKrv8hp2YDI9KpETCDI7KT889jSvSEpdopmJBLffoeKBfupHLJaRVHVBzRXOqaiy47GXvr1T/ZlSZWr22LPlB5iRN9YXwuUM9HVFTEJ2ISuwJR3L5FVj3oL9MtbzWsD506NvjMa+JF3LJtCvmX1yuqDfuYc4GOKDs8l6ANzuhjBO/UNiBl6i0IezUVfIg7gCA8UauFAr/0zttxW6v5XhIiHMgpgMyyMEpZ0XK6V25BpIP184ryUq67d3pZSj7DOFdQNhcuPkey50MZVrTCYYEaWhFIBjz4hcUnnHjhdqIHqV/kW+Mc5ni8vJaK/lPWQHRXd8Dq3mCVG4Vbw99vDt6IflBc6/eKZrHUd0K5fvy86el5ZkVkcyXjfBocpY0c/nLi+TTCgVKDft3U885IvgTLBSwVUeR7TFJLoLbKYTiwnTCrk/3YTMVdPvFHj+gfzLiCH2vlQqP96gJwKdWZahFs/b72HcY9fsvQkZaFuNOHI+7nsDPSpC6c5y423UtnuKVAsIXS6X3NZrK4xH8+h/3SHC7sfLOr2Zu0XBPJqtEGCcUxCSIVfc1g7iXKpNhjP87bcVur+V4SIhzIKYDMsjA/wfaoQG//MasxWcp6DfufYie+bw71laOpSadLHw/7+6SD9fOK8lKuu3d6WUo+wzhXUDYXLj5HsudDGVa0wmGBGloRSAY8+IXFJ5x44XaiB6lf5FvjHOZ4vLyWiv5T1kDAgPKc+Eio+xZcBb7rgyL0Dc2KTRK/agJt2lJ5nD9O+NFFZFh7GUkYyvbDtuG7nQPj2V8v65dP4UnMA0JAg0qgTzJ/i7uMKfTL4cOyUE34uWJNv68siwb3h9kFZR+WzcHwNz1YiDcimMgZIyXDDATLlSZWr22LPlB5iRN9YXwuUDKxslvcdzdMuwJR3L5FVj0+wHSTJSrlhIlsR7u9rnuO/jNlSY1A0VMZzADTZzUkBGpyVrhYmzepy2q9DqlsDcgZzADTZzUkBClHekgxf2a4l8OPB1ijsuxWm3UCcZYDzW3PYduGAPbN9BcNssBX10qMqy4+voWYRge+0UC5ZKomUKB3nnV74DoLy1F2z0CPOkmbYcv1Do66/eWVfgqC80sN8nd1sWf6PMGW0YCqUAOdELxWU4dxQl6DXmjb89PTisO0o09eN34EyWVd2DX8RLmvd0CQ5/2gj6cP1w4cRkIT04Ctsyr344lf74PovvnZroeqMQ5Z+uXXAaYCFzKm7uU/6gaoLx+h9UgVRM8OTAOPcqDILosB+GwQYeC6EJaQWQ5x3Vvkk+eAF9vbmx226RMi+czaGzeSZq1Uexy7PItRHvkHJmXnvS68KZA9dUnZoeoMv3/oifezdST8d3DKxEXGZWPLFOpclzilMXa/Vugmp0OO3P9XnOA+mSyR6EXfvt0fHG4iGrNpIKpqr++KXijLo938YsmndAFjKb3K/cn2waLt9ogN8sUPY+vU+tucwRfOKk+PKFYYgOnVoGchsje7vQ52oZy98G5z0eoAA8mSLEZ+VbjOAA7g7IPh22og3GL04FFg+LycH/yR5V2yx7v09I5W/igehv62VnMOPwvKNerIa3h6Qde8vJaK/lPWQHzwS6ktTAUUowFWWq73dixcJwZ07gZQv+8JAzij0Td1RBvOzCTMt/Xf5ppgtIIMRjtJQA7w0JcnHWQUax6wHjG+MI4F6IPFzO3H7nS/JzCrio4mokX/0p98D4Rjf4H5ein57Kres6YYMGXsMoxvOkqId0NVdvIhOQCKrv8hp2YDABAn53Guz1yrGtaoBg/Dt9hkPSBrZe1FrlnGNozs9Tdoaxv8TWPDaQGmAhcypu7lP+oGqC8fofU8VYFDXUSTDbBIM9xmYMMNDoi2LlXC9Dqosi1FmI9nIx53ImOnjKDrhKaJllUfFz3HloFmc8B9o9WH+yCZv9Yn+cYUx7koS5bUdJIsh5igWoY5kRayizyNBDgCCPyUVJgzZVgkdQvLSS6BhEl0ubloNIDyoXDkZbamnqSVbhha8kgelAMKFxE7GIO3IWl0hqbLBSwVUeR7TFwnBnTuBlC/7wkDOKPRN3VEG87MJMy39d/mmmC0ggxGnYokPxDTLmem6AjgqcykZj5IlXxyNNdmvUYcTSsXPox8WoGO3rXL/OMWcrzzamLtEYRxPTVjQZS/25sCaLGdvSIcjwg9UMkGrmuZvKFO2+Ue9j8ZE4HZloIyYxRx5F/FofDExlQ9NL6BK6v1jpEhlSYN/R5EZyi0crZE8mbx1AASMFFyVlVdrinH3UIWUPVpiYtMpfaHhilAStMb2LZT6vAKEhV3EJVO77+PfiBkh7ikRmVaaZAiHV89ZlzPtF2pxU5ySasfksMtnj0FkOIbLn7QVdt3XHHCU6DfSgOfZas3jKNCU0Ofl/OaNQt+DC7u6c65/N5ADgby7Wson5hnNbdxvzM7K7V4t+FVKOqKdDNyldBfci31D1uhrg/yNmc5r4PVUxMfOqRst9e80uwTa+iXMy/NnEIZSLXwRp9XAje3NTw/gGWoD8xAq9q5YO9unLu/VdhbxQIlK3lBcK3cFc3CzX0eFSlfM3SXRXYoQ6fYwyrvcmaICfGVGHAth2jVwEgP7DOb6Swq9DugVbPwFFqV3TdX4xXwi7uPplsL4cc5Uy5W3JChGuJQHhKiCEE1IZqaFHj8k6ED4yiLQTm98s83MaNjZaAPLZqSiLXIz5hDmT3MQhTiznUhYIkw+6NCHEaHzKgoI1QlK3lBcK3cFXhAjEuE0nZT2CF2cZo7gLlcfb5CH9gjf3HVOVgc0UadnvMhZWZ+eFCQp5yGq2yL55aUdZCsQ/Xd8UfEOPPp4xe0rysgk/T2+g9j69T625zBolPuHm8AH7IBpgIXMqbu5T6ZLJHoRd++JO19OCASt2qBGPuAGPmjGk/DjSHYYm5Cr6z9AsOMwJEiXtXOmimut9OArbMq9+OJkLaSyczd7pMz0z18oHCDMtY4gE2PlbBjZYYQXwx9aNExC9blWcTjXvldF2nA2XQWnCTA5s50iBfEROM9TwCzO1z+q9/Zz3b4kZvv5aTK3CQmOjtrdCRGbq+s/QLDjMCRWy5d9oWezL3BltGAqlADnT9402A2jgovZKtWhnRsqippE6AR4iZRio8wxbMYsii5UlJxSzrpm+u77sutsIVNDsE4Bq8GPE9Aq9QozHiEfztV87beeFwR0GeDX8/iwunI5D5HMhEvXbX2fD3ozDI2chElWQMq4hpZsl+VwO+rnItzc8nFX4ZJVwGmAhcypu7lkipWSIYNXjf4r5jrq2PAVby8lor+U9ZAXLUIUY/m8mTbGqdSVyaydcI9H3A6QdMuBnKd9MJXZUmhwNSNWfnMu9ri0RopQOX2DcFkFEx4iIDPnAViotc2owO7cs0Ui8CJ27iBiTAaIydElTiql8HDs3VWkt7pHrWqwj0fcDpB0y4sUH2Z55i4+Niq2jH8QS15LG/8VefPJ+Qty/mzOK5MVOJCEE3UaURme9u+AWzH+9pAq7+X3P/7TLSvSFs2SuqggOnVoGchsjeqs/nfgmMZKWtiFuvK2zzhABAn53Guz1zSAtUAg7b7/uBeR3KtuJsb7LmjysdWxI5/9dMW94z44NJW5wZ3BMqtV8CJjO+J9oq7UtL6ZuCriubzljZ69kLrBLh47B2MfcQ0r7v0cdwQtAeUnc+UGynmSviLSI7ysgADV16PJWm8BAqjjLuNMxmj8jMnxhfEZcfIbYa1w8JxstbAx/UITurla5IVr1PNY54XRzWG5a5jWlZNHf8oMsDLz6f77GtBw7gU4NSpCVovU5PtpD5MGaKgNFoMhxWwFNqkwnvo44rJlaBaG+Rgu8AHzaCJlM/gwWfxFS76xbrtVZRybK7NFQJPHGwm0wfmPaMUAP4nxfW4EETjf2x0F/NOTxRhoEFDBn4='
    # # print(bytes(key,encoding="utf-8"))
    # # print(key.encode())
    # key = "XB5DZaVmZ1HpSUtsAJ1vTH6yE1c1dHd0"
    # print(base64.b64decode(key))
    key_64 = base64.b64decode(des3_key)
    # print(key_64)
    # # print(p.pad(base64.b64decode(key)))
    # text_mi = p.encrypt(text,key_64)
    # print(p.encrypt(text,key_64))
    # # print(p.pad(key))
    # content_feimi = p.decrypt(content,key_64)
    # print(p.decrypt(content,key_64))
    # print(json.dumps(json.loads(content_feimi),ensure_ascii=False,indent=2))
    # text = "+mniROSqXDg="
    # print(p.decrypt(text, DOC_IN_CHECK_REDIECT_KEY))
    print(p.encrypt("17656", key_64))
