import xml.etree.ElementTree as ET
import requests
from urllib import request

url = 'http://ams.tinnhanthuonghieu.vn:8009/bulkapi?wsdl'
xmlData = '''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:impl="http://impl.bulkSms.ws/">
   <soapenv:Header/>
   <soapenv:Body>
      <impl:wsCpMt>
         <!--Optional:-->
         <User>smsbrand_sfc</User>
         <!--Optional:-->
         <Password>123456aA@</Password>
         <!--Optional:-->
         <CPCode>SFC</CPCode>
         <!--Optional:-->
         <RequestID>1</RequestID>
         <!--Optional:-->
         <UserID>84936292787</UserID>
         <!--Optional:-->
         <ReceiverID>84936292787</ReceiverID>
         <!--Optional:-->
         <ServiceID>SFC</ServiceID>
         <!--Optional:-->
         <CommandCode>bulksms</CommandCode>
         <!--Optional:-->
         <Content>?</Content>
         <!--Optional:-->
         <ContentType>0</ContentType>
      </impl:wsCpMt>
   </soapenv:Body>
</soapenv:Envelope>'''

xml = ET.fromstring(xmlData)
for child in xml:
    print(child.tag)

body = xml.find('{http://schemas.xmlsoap.org/soap/envelope/}Body').find('{http://impl.bulkSms.ws/}wsCpMt')

content = "Bạn đã đặt lịch hẹn thành công phòng khám bác sỹ Nguyen Van A, mã phòng khám x, số thứ tự xx, giờ khám hh:mm ngày dd/mm"
body.find("Content").text = content
print(body.find("User").text)
print(body.find("Content").text)

p = requests.post(url,data=ET.tostring(xml,encoding="UTF-8"),headers={'Content-Type':'text/xml'})

print(p.content)
print(p)

