import urllib.request
import urllib.parse
from datetime import datetime, date, timedelta

from django.conf import settings
from django.urls import reverse_lazy, reverse
from django.core.serializers import json
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect

from user.cart.cart import Cart
from user.vnpay.forms_vnpay import PaymentForm
from user.vnpay.vnpay import vnpay
from user.models import Payment, DoctorProfile, License
from user.license import license_dic, add_license




def index(request):
    return render(request, "index.html", {"title": "Danh sách demo"})


def payment(request):
    cart = Cart(request)   
    if request.method == 'POST':       
        # Process input data and build url payment
        form = PaymentForm(request.POST)
        if form.is_valid():
            
            # check license on checkout page
            if license_dic[cart.cart["license"]][1] != cart.cart["money"]:
                print(type(license_dic[cart.cart["license"]][1]))
                print(type(cart.cart["money"]))
                
                return JsonResponse({'code': 'invalid', 'Message': "Lỗi checkout"})
            
            print(form)
            form = form.save(commit=False)
            form.license = cart.cart["license"]
            form.amount = cart.cart["money"]
            form.order_desc = cart.cart["order_desc"]
            form.save()

            # order_type = form.cleaned_data['order_type']
            # order_id = form.cleaned_data['order_id']
            # amount = form.cleaned_data['amount']
            # order_desc = form.cleaned_data['order_desc']
            # bank_code = form.cleaned_data['bank_code']
            # language = form.cleaned_data['language']
            ipaddr = get_client_ip(request)
            # Build URL Payment
            vnp = vnpay()
            vnp.requestData['vnp_Version'] = '2.0.0'
            vnp.requestData['vnp_Command'] = 'pay'
            vnp.requestData['vnp_TmnCode'] = settings.VNPAY_TMN_CODE
            vnp.requestData['vnp_Amount'] = int(form.amount) * 100
            vnp.requestData['vnp_CurrCode'] = 'VND'
            vnp.requestData['vnp_TxnRef'] = form.order_id
            vnp.requestData['vnp_OrderInfo'] = form.order_desc
            vnp.requestData['vnp_OrderType'] = "130005" # Ma hang hoa
            # Check language, default: vn
            
            vnp.requestData['vnp_Locale'] = 'vn'
            # Check bank_code, if bank_code is empty, customer will be selected bank on VNPAY
            if form.bank_code and form.bank_code != "":
                vnp.requestData['vnp_BankCode'] = form.bank_code

            vnp.requestData['vnp_CreateDate'] = form.created.strftime('%Y%m%d%H%M%S')  # 20150410063022
            print(vnp.requestData['vnp_CreateDate'])
            vnp.requestData['vnp_IpAddr'] = ipaddr
            vnp.requestData['vnp_ReturnUrl'] = settings.VNPAY_RETURN_URL
            vnpay_payment_url = vnp.get_payment_url(settings.VNPAY_PAYMENT_URL, settings.VNPAY_HASH_SECRET_KEY)
            print(vnpay_payment_url)

            # if request.is_ajax():
                # Show VNPAY Popup
            #     result = JsonResponse({'code': '00', 'Message': 'Init Success', 'data': vnpay_payment_url})
            #     return result
            # else:
                # Redirect to VNPAY
            return redirect(vnpay_payment_url)
        else:
            print("Form input not validate")

            result = JsonResponse({'code': 'invalid', 'Message': form.errors["email"][0]})
            return result
            # return render(request, "user/vnpay/payment.html", {"cart":cart,"form":form})
    else:
        if cart.cart["email"] and cart.cart["license"] and cart.cart["money"]:
            doctor = DoctorProfile.objects.get(user__email=cart.cart["email"])
            return render(request, "user/vnpay/payment.html", {"cart":cart,"doctor":doctor})
        return redirect(reverse("license"))


def payment_ipn(request):
    inputData = request.GET
    if inputData:
        vnp = vnpay()
        vnp.responseData = inputData.dict()
        order_id = inputData['vnp_TxnRef']
        amount = str(int(inputData['vnp_Amount']) / 100)
        order_desc = inputData['vnp_OrderInfo']
        vnp_TransactionNo = inputData['vnp_TransactionNo']
        vnp_ResponseCode = inputData['vnp_ResponseCode']
        vnp_TmnCode = inputData['vnp_TmnCode']
        vnp_PayDate = inputData['vnp_PayDate']
        vnp_BankCode = inputData['vnp_BankCode']
        vnp_CardType = inputData['vnp_CardType']
        if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            # Check & Update Order Status in your Database
            # Check vnp_TxnRef
            try:
                payment = Payment.objects.get(order_id=order_id)
            except:
                return JsonResponse({'RspCode': '01', 'Message': 'Order not found'})
            # Check vnp_Amount
            if payment.amount != str(amount):
                return JsonResponse({'RspCode': '04', 'Message': 'Invalid amount'})

            # Check status
            if payment.status != 0:
                return JsonResponse({'RspCode': '02', 'Message': 'Order Already Update'})
            
            # Check vnp_ResponseCode
            if vnp_ResponseCode == '00':
                print('Payment Success. Your code implement here')
                payment.status = 1
                # add license to user doctor
                vnp_PayDate = datetime.strptime(vnp_PayDate,"%Y%m%d%H%M%S")
                paydate = date(year=vnp_PayDate.year,month=vnp_PayDate.month,day=vnp_PayDate.day)
                doctor = DoctorProfile.objects.get(user__email=payment.email)
                
                add_license(payment,doctor,paydate)
                
            else:
                print('Payment Error. Your code implement here')
                payment.status = 2

            payment.save()
            # Return VNPAY: Merchant update success
            result = JsonResponse({'RspCode': '00', 'Message': 'Confirm Success'})

        else:
            # Invalid Signature
            result = JsonResponse({'RspCode': '97', 'Message': 'Invalid Signature'})
    else:
        result = JsonResponse({'RspCode': '99', 'Message': 'Invalid request'})

    return result


def payment_return(request):
    inputData = request.GET
    if inputData:
        vnp = vnpay()
        vnp.responseData = inputData.dict()
        order_id = inputData['vnp_TxnRef']
        amount = int(int(inputData['vnp_Amount']) / 100)
        order_desc = inputData['vnp_OrderInfo']
        vnp_TransactionNo = inputData['vnp_TransactionNo']
        vnp_ResponseCode = inputData['vnp_ResponseCode']
        vnp_TmnCode = inputData['vnp_TmnCode']
        vnp_PayDate = inputData['vnp_PayDate']
        vnp_BankCode = inputData['vnp_BankCode']
        vnp_CardType = inputData['vnp_CardType']
        if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            # Check & Update Order Status in your Database
            # Check vnp_TxnRef
            try:
                payment = Payment.objects.get(order_id=order_id)
            except:
                return HttpResponse("Mã đơn hàng không tồn tại.")
            # Check vnp_Amount
            if payment.amount != str(amount):
                return HttpResponse("Số tiền không hợp lệ.")

            vnp_PayDate = datetime.strptime(vnp_PayDate,"%Y%m%d%H%M%S")
            if vnp_ResponseCode == "00":
                return render(request, "user/vnpay/payment_return.html", {"title": "Kết quả thanh toán", "id":payment.id,"vnp_PayDate":vnp_PayDate,"result": "Thành công","amount": amount,"order_desc": order_desc,"vnp_TransactionNo": vnp_TransactionNo,"vnp_ResponseCode": vnp_ResponseCode})
            else:
                return render(request, "user/vnpay/payment_return.html", {"title": "Kết quả thanh toán", "id":payment.id,"vnp_PayDate":vnp_PayDate,
                "result": "Lỗi",
                "amount": amount,
                "order_desc": order_desc,
                "vnp_TransactionNo": vnp_TransactionNo,
                "vnp_ResponseCode": vnp_ResponseCode})
        else:
            return render(request, "user/vnpay/payment_return.html",
                {"title": "Kết quả thanh toán", "result": "Lỗi", "amount": amount,"vnp_PayDate":vnp_PayDate,
                "order_desc": order_desc, "vnp_TransactionNo": vnp_TransactionNo,
                "vnp_ResponseCode": vnp_ResponseCode, "msg": "Sai checksum"})
    else:
        return render(request, "user/vnpay/payment_return.html", {"title": "Kết quả thanh toán", "result": "","amount": "1000000","vnp_PayDate":datetime.strptime("20150924130500","%Y%m%d%H%M%S"),"vnp_TransactionNo": "02", "vnp_ResponseCode": "02"})


def query(request):
    if request.method == 'GET':
        return render(request, "query.html", {"title": "Kiểm tra kết quả giao dịch"})
    else:
        # Add paramter
        vnp = vnpay()
        vnp.requestData = {}
        vnp.requestData['vnp_Command'] = 'querydr'
        vnp.requestData['vnp_Version'] = '2.0.0'
        vnp.requestData['vnp_TmnCode'] = settings.VNPAY_TMN_CODE
        vnp.requestData['vnp_TxnRef'] = request.POST['order_id']
        vnp.requestData['vnp_OrderInfo'] = 'Kiem tra ket qua GD OrderId:' + request.POST['order_id']
        vnp.requestData['vnp_TransDate'] = request.POST['trans_date']  # 20150410063022
        vnp.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')  # 20150410063022
        vnp.requestData['vnp_IpAddr'] = get_client_ip(request)
        requestUrl = vnp.get_payment_url(settings.VNPAY_API_URL, settings.VNPAY_HASH_SECRET_KEY)
        responseData = urllib.request.urlopen(requestUrl).read().decode()
        print('RequestURL:' + requestUrl)
        print('VNPAY Response:' + responseData)
        data = responseData.split('&')
        for x in data:
            tmp = x.split('=')
            if len(tmp) == 2:
                vnp.responseData[tmp[0]] = urllib.parse.unquote(tmp[1]).replace('+', ' ')

        print('Validate data from VNPAY:' + str(vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY)))
        return render(request, "query.html", {"title": "Kiểm tra kết quả giao dịch", "data": vnp.responseData})


def refund(request):
    return render(request, "refund.html", {"title": "Gửi yêu cầu hoàn tiền"})


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
