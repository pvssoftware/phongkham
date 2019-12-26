import xml.etree.ElementTree as ET
import requests, re
from urllib import request
from datetime import datetime

def send_sms(tenBS,maPK,soTT,ngayKham,phone):
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
            <ContentType>1</ContentType>
         </impl:wsCpMt>
      </soapenv:Body>
   </soapenv:Envelope>'''

   xml = ET.fromstring(xmlData)
   phone = re.sub(r"^0","84",phone)
   # for child in xml:
   #     print(child.tag)

   body = xml.find('{http://schemas.xmlsoap.org/soap/envelope/}Body').find('{http://impl.bulkSms.ws/}wsCpMt')

   content = "Bạn đã đặt lịch hẹn thành công bác sỹ "+tenBS+", mã phòng khám "+str(maPK)+", số thứ tự "+soTT+ ", giờ khám " +ngayKham.strftime("%H:%M")+" ngày "+ngayKham.strftime("%d/%m")+". Cảm ơn Quý khách đã sử dụng dịch vụ của chúng tôi. Trân trọng!"

   content1 = "Bạn đã đặt lịch hẹn thành công bác sỹ "+tenBS+", mã phòng khám "+str(maPK)+", số thứ tự "+soTT+ ", ngày "+ngayKham.strftime("%d/%m")+". Cảm ơn Quý khách đã sử dụng dịch vụ của chúng tôi. Trân trọng!"
   now = datetime.now()
   # content1 = "Ban da dat lich hen thanh cong phong kham bac si Nguyen Van A, ma phong kham x, so thu tu xx, gio kham hh:mm ngay dd/mm"+ngayKham.strftime("%d/%m/%Y")
   # print(type(body.find("UserID").text))
   if now < ngayKham:
      body.find("Content").text = content
   else:
      body.find("Content").text = content1
   body.find("UserID").text = phone
   body.find("ReceiverID").text = phone
   # print(body.find("User").text)
   # print(body.find("Content").text)

   
   # print(re.sub(r"^0","84","0936002787"))

   p = requests.post(url,data=ET.tostring(xml,encoding="UTF-8"),headers={'Content-Type':'text/xml'})

   print(p.content)
# print(p)

