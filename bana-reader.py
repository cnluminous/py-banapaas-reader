import binascii
import serial
import serial.tools.list_ports
import sys


def sst(data, start, end):
    data = data.replace(" ", "")
    list = []
    i = 0
    b = -2
    c = 0
    while len(data) / 2 > i:
        b = b + 2
        c = c + 2
        li = data[b:c]
        list.append(li)
        i = i + 1
    stt = list
    # print(stt)
    data = bytes.fromhex(stt[start])[0]
    i = 6
    while i <= end:
        data = data + bytes.fromhex(stt[i])[0]
        # print(bytes.fromhex(stt[i])[0])
        i = i + 1
    hex_data = hex(int(data))
    data = ("00" + str(hex_data))[-2:]
    # print(data)
    bin_data = bin(int(data, 16)).lstrip("0b")
    # print(bin_data)
    if len(bin_data) == 8:
        bi = ""
        for s in bin_data:
            if s == "1":
                # print(1)
                bi = bi + str(0)
            else:
                # print(0)
                bi = bi + str(1)
        # print(bi)
        sr = "1"
        bin_fan = bin(int(bi, 2) + int(sr, 2))[2:]
        bin_hex = hex(int(bin_fan, 2)).lstrip("0x").upper()
        return (bin_hex)
    else:
        bin_data = ("00000000" + bin_data)[-8:]
        # print(bin_data)
        bi = ""
        for s in bin_data:
            if s == "1":
                # print(1)
                bi = bi + str(0)
            else:
                # print(0)
                bi = bi + str(1)
        # print(bi)
        sr = "1"
        bin_fan = bin(int(bi, 2) + int(sr, 2))[2:]
        bin_hex = hex(int(bin_fan, 2)).lstrip("0x").upper()
        return (bin_hex)

# 寻找设备
def findSerialDevice():
    port_list = list(serial.tools.list_ports.comports())
    if len(port_list) > 0:
        for ser in port_list:
            device = serial.Serial(ser[0], 115200, timeout=0.5)
            device.bytesize = 8
            device.parity = serial.PARITY_NONE 
            device.stopbits = 1 
            if wakeUp(device) == "0000ff00ff000000ff02fed5151600":
                return device

# 唤醒设备
def wakeUp(device):
    da1 = bytes.fromhex("55 55 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ff 03 fd d4 14 01 17 00")
    device.write(da1)
    result = str(binascii.b2a_hex(device.read(25)))[2:-1]
    return result

#获取卡号
def getCardId(device):
    data = bytes.fromhex("00 00 FF 04 FC D4 4A 02 00 E0 00")
    device.write(data)
    redata_yid = str(binascii.b2a_hex(device.read(25)))[2:-1]
    if len(redata_yid) == 50:
        id = redata_yid[-12:-4]
        return id

#验证密码
def verifyKey(device,password,id):
    Sector = "00"
    yss = "00 00 FF 0F F1 D4 40 01 60" + Sector + password + id + "b2 00"
    dcs = "00 00 FF 0F F1 D4 40 01 60" + Sector + password + id + sst(yss, 5, 19) + " 00"
    dcs = dcs.replace(" ", "")
    yanze = bytes.fromhex(dcs)
    device.write(yanze)
    erok = str(binascii.b2a_hex(device.read(32)))[2:-1]
    code = erok[-8:-4]
    if code == "4100":
        return True
    else:
        return False

#读取数据
def readdata(device,blo):
    reco = "00 00 ff 05 fb D4 40 01 30 " + blo + "86  00"
    recode = bytes.fromhex("00 00 ff 05 fb D4 40 01 30 " + blo + sst(reco, 5, 9) + " 00")
    device.write(recode)
    ss = str(binascii.b2a_hex(device.read(64)))[2:-1]
    if ss[-9:-4] != "54113":
        block_d = ss[-36:-4]
        return block_d

#关闭串口
def closeSerial(device):
    device.close


def getChipId(device):
    chipId = readdata(device,"00")
    return chipId.upper()
def getAccessCode(device):    
    accessCode = readdata(device,"02")[12:]
    return accessCode.upper()

password = "6090D00632F5"

if __name__ == '__main__':
    device = findSerialDevice()
    if device is not None:
        id = getCardId(device)
        if id is not None:
            vk = verifyKey(device,password,id)
            if vk ==True:
                chipid = getChipId(device)
                accesscode = getAccessCode(device)

                print(chipid)
                print(accesscode)
