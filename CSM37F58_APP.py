import sys,time,os
from CSM37F58_APP_ui import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from serial.tools.list_ports import *
from picture_qrc import  *
import datetime
from IIC_CH341 import *
from PyQt5.QtCore import  QTimer
import numpy as np


class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    CMD_CSM37F58_IAP_CHECKSUM_ADDRESS = 0xEC00
    CMD_CSM37F58_IAP_GET_VERSION_ADDRESS = 0xFFFF

    def __init__(self):
        super(MyApp, self).__init__()
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)
        Ui_MainWindow.__init__(self)
        # logo
        self.setWindowIcon(QIcon(":picture/img/110.png"))
        # 默认时间戳
        self.time_stamp = datetime.datetime.now().strftime('%Y-%m-%d')

        # #初始化显示大小
        self.init_default_display()
        self.init_watch_table_all()
        self.init_read_timer()

        ##
        # #初始化信号槽
        self.btn_update_all.clicked.connect(self.update_watch_table_display)
        self.btn_cmd_1.clicked.connect(self.on_click_btn_cmd_1)
        self.btn_cmd_2.clicked.connect(self.on_click_btn_cmd_2)
        self.btn_cmd_3.clicked.connect(self.on_click_btn_cmd_3)
        self.btn_cmd_4.clicked.connect(self.on_click_btn_cmd_4)
        self.btn_cmd_5.clicked.connect(self.on_click_btn_cmd_5)
        self.btn_cmd_6.clicked.connect(self.on_click_btn_cmd_6)
        self.btn_cmd_7.clicked.connect(self.on_click_btn_cmd_7)
        self.btn_cmd_8.clicked.connect(self.on_click_btn_cmd_8)
        self.btn_cmd_9.clicked.connect(self.on_click_btn_cmd_9)
        self.btn_cmd_query.clicked.connect(self.on_click_btn_cmd_query)
        self.btn_cmd_write.clicked.connect(self.on_click_btn_cmd_write)
        self.btn_cmd_read.clicked.connect(self.on_click_btn_cmd_read)
        self.btn_cmd_reset.clicked.connect(self.on_clicked_btn_cmd_reset)
        self.btn_query_state.clicked.connect(self.on_clicked_btn_query_state)
        # IAP
        self.btn_iap_loadfile.clicked.connect(self.on_clicked_btn_iap_loadfile)
        self.btn_iap_start.clicked.connect(self.on_clicked_btn_iap_start)
        self.btn_iap_erase.clicked.connect(self.on_clicked_btn_iap_erase)
        self.btn_iap_get_version.clicked.connect(self.on_clicked_btn_iap_get_version)
        self.btn_iap_read_flash.clicked.connect(self.on_clicked_btn_iap_read_flash)
        #line
        self.line_body_height.textChanged.connect(self.on_changed_line_body_data)
        self.line_body_weight.textChanged.connect(self.on_changed_line_body_data)
        self.line_body_years_old.textChanged.connect(self.on_changed_line_body_data)
        self.line_body_gender.textChanged.connect(self.on_changed_line_body_data)
        self.line_body_mode.textChanged.connect(self.on_changed_line_body_data)

        self.btn_read_timer.clicked.connect(self.on_clicked_btn_read_timer)
        #
        self.read_timer = QTimer()
        self.read_timer.timeout.connect(self.read_timer_event)
        # self.read_timer.start(int(self.line_read_time.text()))

    def on_clicked_btn_read_timer(self):
        print("click read_timer")
        if(self.btn_read_timer.text()=="结束"):
            self.btn_read_timer.setText("开始")
            self.timer_event_enable = False
            # print("stop")
            self.read_timer.stop()
        else:
            #print("start")
            self.btn_read_timer.setText("结束")
            self.timer_event_enable = True
            # self.read_timer.timeout.connect(self.read_timer_event)
            self.read_timer.start(int(self.line_read_time.text()))

    def read_timer_event(self):
        print("timer_event:",datetime.datetime.now().strftime('%Y-%m-%d:%H:%M:%S'))
        if  self.timer_event_enable == True:
            self.i2c_read_bytes()

    def read_save_file(self,s):
        with open("./record.csv","a+") as f:
            f.write(s)

    def i2c_read_bytes(self):
        try:
            protocol = CH341AIIC()
            save_mode ='big'
            if self.comboBox_read_timer.currentText() == "小端模式":
                save_mode = 'little'

            address_read = int(self.line_timer_read_addr.text(),16)
            length = int(self.line_timer_read_byte_len.text())
            print("read：", hex(address_read))
            result = False
            read = bytearray()
            if length == 1:
                result, read = protocol.read_byte(address_read)
            else:
                result,read = protocol.read_bytes(address_read,length)
            # print("type:",type(read)) #bytes

            print(str(result),read.hex())

            if result:
                # QMessageBox.information(self, "提示", "读取成功")
                value = int.from_bytes(read,byteorder= save_mode)
                self.plainTextEdit_read_timer.appendPlainText("[" + datetime.datetime.now().strftime('%H:%M:%S') + "]: 0x" + read.hex()+","+str(value))
                self.read_save_file(str(value)+'\n')
                print(str(value))
            else:
                QMessageBox.information(self, "错误", "读取失败,请检查硬件")

        except Exception as e:
            print(str(e))
            self.timer_event_enable =False
            QMessageBox.information(self, "错误", "读取失败,请检查硬件" + str(e))

    def init_read_timer(self):
        self.line_timer_read_addr.setText("0x11AC")
        self.line_timer_read_byte_len.setText("1")
        self.comboBox_read_timer.addItems(["大端模式","小端模式"])
        f = open("./record.csv", "a+")
        f.close()

    def on_clicked_btn_iap_read_flash(self):
        try:
            protocol = CH341AIIC()
            self.progress_bar = QProgressDialog()
            self.progress_bar.setWindowTitle("读取Flash中....")
            self.progress_bar.setWindowIcon(QIcon(":picture/img/110.png"))
            self.progress_bar.show()
            self.textBrowser_iap_read.clear()
            self.refresh_app()
            print("read_flash:"+str(self.frame_cnt+2))
            self.textBrowser_iap_read.append("共加载%s包,加1包校验"%(self.frame_cnt+2))
            for i in range(self.frame_cnt+1):
                result,ret = protocol.read_bytes(i*512,512)
                print("正在读取第%s包"%(i+1))
                if not result:
                    self.progress_bar.close()
                    QMessageBox.information(self, "提示", "没有ACK信号,请检查模块")
                    break
                self.textBrowser_iap_read.append("第%s包(512):"%(i+1))
                self.progress_bar.setValue((i / (self.frame_cnt + 2) * 100))
                self.textBrowser_iap_read.append(ret.hex())
                self.refresh_app()
        #   读校验区
            time.sleep(0.1)
            result, ret = protocol.read_bytes(self.CMD_CSM37F58_IAP_CHECKSUM_ADDRESS,  512)
            self.textBrowser_iap_read.append("第%s包(校验码):" % (self.frame_cnt+2))
            self.textBrowser_iap_read.append(ret.hex())
            self.progress_bar.setValue(100)
        except Exception as e:
            print("on_clicked_btn_iap_read_flash",str(e))
            QMessageBox.information(self, "提示", "初始化CS341失败,请检查硬件")

    def on_clicked_btn_iap_get_version(self):
        print("获取版本")
        try:
            protocol = CH341AIIC()
            time.sleep(0.01)
            result,version = protocol.read_bytes(self.CMD_CSM37F58_IAP_GET_VERSION_ADDRESS,4)
            if  result:
                print(bytes(version).hex())
                QMessageBox.information(self, "提示","得到版本号: %s"%((bytes(version)).hex()))
            else:
                QMessageBox.information(self, "提示", "发送命令失败")
        except Exception as e:
            QMessageBox.information(self, "提示", "初始化CS341失败,请检查硬件")

    def on_clicked_btn_iap_erase(self):

        self.CSM37F58_IAP_CMD = [0xA0, 0x00, 0x00, 0xAA, 0x55, 0xA5, 0x5A]
        try:
            protocol = CH341AIIC()
            protocol.reset_io_D0(0.005)
            time.sleep(0.01)
            result = protocol.write_bytes(self.CSM37F58_IAP_CMD)
            if  result:
                self.btn_iap_start.setEnabled(True)
                QMessageBox.information(self, "提示","命令发送成功")
            else:
                QMessageBox.information(self, "提示", "发送命令失败")
        except Exception as e:
            QMessageBox.information(self, "提示", "初始化CS341失败,请检查硬件")
    def on_clicked_btn_iap_start(self):

        print("clicked iap start")
        try:
            file = open(self.bin_path,"rb")
            bin_data = file.read()
            file.close()
            print(len(bin_data),int(len(bin_data)/512))
            self.iic_send_bin_file(bin_data)
            self.btn_iap_start.setEnabled(False)
        except Exception as e:
            print(str(e))
            QMessageBox.information(self, "提示", "请先选择Bin文件！")

    def iic_send_bin_file(self,bin_data):
        self.progress_bar = QProgressDialog()
        print("正在准备发送...")
        try:
            protocol = CH341AIIC()
            self.frame_cnt = int(len(bin_data) / 512)
            self.progress_bar.setWindowTitle("在线升级中（IAP）....")
            self.progress_bar.setWindowIcon(QIcon(":picture/img/110.png"))
            self.progress_bar.show()
            self.refresh_app()
            for i in range(self.frame_cnt):
                data_512bytes = bin_data[i*512:i*512+512]
                result = protocol.write_iap_bytes(i*512,bytearray(data_512bytes))
                self.progress_bar.setValue((i/(self.frame_cnt+1)*100))
                if not result:
                    self.progress_bar.close()
                    QMessageBox.information(self, "提示", "发送失败,请检查硬件")
                    return
                time.sleep(0.01)
            # print("升级中..."+str(i))
            # 发送最后一帧，可能不满512bytes,补足0xff
            last_frame = bin_data[(self.frame_cnt)*512:]
            print("last_frame:"+str(len(last_frame))+":"+(last_frame.hex()))
            last = bytearray(512)
            for i in range(512):
                last[i] = 0xff
            for i in range(len(last_frame)):
                last[i] = last_frame[i]
            protocol.write_iap_bytes(self.frame_cnt*512,last)
            print(("发送last: "+bytes(last).hex()))
        #     send checksum
            protocol.write_iap_bytes(self.CMD_CSM37F58_IAP_CHECKSUM_ADDRESS,self.iap_checksum)
            self.progress_bar.setValue(100)
            print("升级完成")
        except Exception as e:
            print(str(e))
            QMessageBox.information(self, "提示", "发送失败,请检查硬件")

    def on_clicked_btn_iap_loadfile(self):
        print("load file clicked")
        try:
            self.bin_path, describe = QFileDialog.getOpenFileName(self, 'Open file', '.', "txt files (*.bin)")
            print(self.bin_path)

            file = open(self.bin_path, "rb");bin_data = file.read();file.close()
            # get checksum
            self.frame_cnt = int(len(bin_data)/512)
            # load
            self.textBrowser_iap.append("共加载到%sBytes,将发送%s包(加1包校验)"%(len(bin_data),int(len(bin_data)/512)+2))
            for i in range(self.frame_cnt):
                data_512bytes = bin_data[512*i:512*i + 512]
                self.textBrowser_iap.append("第%s包(512):"%(i+1))
                self.textBrowser_iap.append(data_512bytes.hex())
                self.refresh_app()
            # load_end
            self.iap_checksum = bytearray(512)
            for i in range(512):
                self.iap_checksum[i] = 0xff
            for i in range(self.frame_cnt):
                data_512bytes = bin_data[512*i:i*512+512]
                checksum = 0x00
                for j in range(512):
                    checksum += data_512bytes[j]
                self.iap_checksum[i+5] = checksum&0xff
                print(hex(checksum&0xff))
            # 最后一帧处理
            last_frame = bin_data[(self.frame_cnt)*512:]
            last = bytearray(512)
            for i in range(512):
                last[i] = 0xff
            for i in range(len(last_frame)):
                last[i] = last_frame[i]
            checksum = 0x00
            print("last_len:",len(last))
            for i in range(512):
                checksum += last[i]
            # last
            #
            self.iap_checksum[5+self.frame_cnt] = checksum&0xff
            self.iap_checksum[4] = self.frame_cnt+1
            self.textBrowser_iap.append("第%s包(512):" % (self.frame_cnt + 1))
            self.textBrowser_iap.append(bytes(last).hex())
            self.refresh_app()
            #main_checksum
            version = 0x00
            for i in range(self.frame_cnt+1):
                version +=self.iap_checksum[5+i]
            print("main_CHECKSUM:",version)
            version  =  version&0xffff
            main_version = (version&0xff00)>>8
            other_version = (version&0xff)
            self.iap_checksum[0] = main_version
            self.iap_checksum[1] = other_version
            self.iap_checksum[2] = (~main_version)&0xff
            self.iap_checksum[3] = (~other_version)&0xff
            checksum =0x00
            self.iap_checksum[511]=0x00
            for i in range(512):
                checksum +=self.iap_checksum[i]
            self.iap_checksum[511] = checksum&0xff

            self.textBrowser_iap.append("第%s包(校验码):" % (self.frame_cnt + 2))
            self.textBrowser_iap.append(bytes(self.iap_checksum).hex())
            print("checksum:"+bytes(self.iap_checksum).hex())
            self.btn_iap_loadfile.setText("已选择: "+self.bin_path)
            self.btn_iap_read_flash.setEnabled(True)
        except Exception as e:
            print(str(e))

    def on_clicked_btn_query_state(self):
        print("查询状态...")
        try:
            protocol = CH341AIIC()
            if not protocol.get_input_D7():
                QMessageBox.information(self,"提示","检测到低电平")
            else:
                QMessageBox.information(self, "提示", "检测到高电平")
        except Exception as e:
            QMessageBox.information(self,"提示","失败,请检查硬件")
    def on_clicked_btn_cmd_reset(self):
        try:
            protocol = CH341AIIC()
            protocol.reset_io_D0(0.005)
            print("event:按键复位")
            QMessageBox.information(self,"提示","发送成功")
        except Exception as e:
            QMessageBox.information(self,"提示","失败,请检查硬件")
    def on_changed_line_body_data(self):
        try:
            body_list = [0xA0,0x10,0x58,0x02,0xC1,0xAA,0x9E,0x00]
            body_height = int(self.line_body_height.text())
            body_weight = int(float(self.line_body_weight.text())*10)
            body_years_old = int(self.line_body_years_old.text())
            body_gender = self.line_body_gender.text() == "男"
            body_mode = 0
            body_list[3] = body_weight>>8
            body_list[4] = body_weight&0xff
            body_list[5] = body_height
            body_list[6] = body_gender*0x80 + body_years_old
            str_dis = ('0x'+' 0x'.join('{:02x}'.format(x)  for x in body_list))
            print(str_dis)
            self.line_cmd_2.setText(str_dis)
            print(str(body_height),str(body_weight),str(body_years_old),str(body_gender),str(body_mode))
        except Exception as e:
            print(str(e))
        print("editing...")

    def on_click_btn_cmd_1(self):

        self.iic_send_bytes(self.line_cmd_1.text(),True)

    def on_click_btn_cmd_2(self):
        hex_str = self.line_cmd_2.text()
        cmd_hex = hex_str.replace("0x","")
        cmd_bytes = bytes.fromhex(cmd_hex)
        cmd = [cmd_bytes[0],cmd_bytes[1],cmd_bytes[2],cmd_bytes[3]]
        self.iic_send_bytes(bytes(cmd).hex())
        cmd[2] = cmd_bytes[2]+1
        cmd[3] = cmd_bytes[4]
        self.iic_send_bytes(bytes(cmd).hex())
        cmd[2] = cmd_bytes[2]+2
        cmd[3] = cmd_bytes[5]
        self.iic_send_bytes(bytes(cmd).hex())
        cmd[2] = cmd_bytes[2]+3
        cmd[3] = cmd_bytes[6]
        self.iic_send_bytes(bytes(cmd).hex())
        cmd[2] = cmd_bytes[2]+4
        cmd[3] = cmd_bytes[7]
        self.iic_send_bytes(bytes(cmd).hex(),True)

    def on_click_btn_cmd_3(self):
        self.btn_cmd_3.setEnabled(False)
        self.iic_send_bytes(self.line_cmd_3.text(),True)
        self.btn_cmd_3.setEnabled(True)

    def on_click_btn_cmd_4(self):
        self.btn_cmd_4.setEnabled(False)
        self.iic_send_bytes(self.line_cmd_4.text(),True)
        self.btn_cmd_4.setEnabled(True)

    def on_click_btn_cmd_5(self):
        self.btn_cmd_5.setEnabled(False)
        self.iic_send_bytes(self.line_cmd_5.text(),True)
        self.btn_cmd_5.setEnabled(True)

    def on_click_btn_cmd_6(self):
        self.btn_cmd_6.setEnabled(False)
        self.iic_send_bytes(self.line_cmd_6.text(),True)
        self.btn_cmd_6.setEnabled(True)

    def on_click_btn_cmd_7(self):
        self.btn_cmd_7.setEnabled(False)
        self.iic_send_bytes(self.line_cmd_7.text(),True)
        self.btn_cmd_7.setEnabled(True)
    def on_click_btn_cmd_8(self):
        self.btn_cmd_8.setEnabled(False)
        self.iic_send_bytes(self.line_cmd_8.text(),True)
        self.btn_cmd_8.setEnabled(True)
    def on_click_btn_cmd_9(self):
        self.btn_cmd_9.setEnabled(False)
        self.iic_send_bytes(self.line_cmd_9.text(),True)
        self.btn_cmd_9.setEnabled(True)
    def on_click_btn_cmd_query(self):
        self.btn_cmd_query.setEnabled(False)
        self.iic_read_byte(self.line_cmd_query.text(), True, self.line_cmd_query_dis)
        self.btn_cmd_query.setEnabled(True)

    def on_click_btn_cmd_write(self):
        self.btn_cmd_write.setEnabled(False)
        self.iic_send_bytes(self.line_cmd_write.text(),True)
        self.btn_cmd_write.setEnabled(True)

    def on_click_btn_cmd_read(self):
        self.btn_cmd_read.setEnabled(False)
        self.iic_read_byte(self.line_cmd_read.text(),True,self.line_cmd_read_dis)
        self.btn_cmd_read.setEnabled(True)

    def iic_read_byte(self,hex_str,dis_success,dis_line):
        try:
            cmd_hex = hex_str.replace("0x", "")
            cmd_bytes = bytes.fromhex(cmd_hex)
            print(hex_str)
            protocol = CH341AIIC()
            print(hex(cmd_bytes[1]),hex(cmd_bytes[2]))
            address_read = (cmd_bytes[1]*256+cmd_bytes[2])
            print("read：", hex(address_read))
            result,read = protocol.read_byte(address_read)
            dis_line.setText("读取到数据："+hex(read[0]))
            if dis_success & result:
                QMessageBox.information(self, "提示", "读取成功")
            elif dis_success:
                QMessageBox.information(self, "错误", "读取失败,请检查硬件")
        except Exception as e:
            print(str(e))
            QMessageBox.information(self, "错误", "读取失败,请检查硬件" + str(e))

    def refresh_app(self):

        qApp.processEvents()

    def iic_send_bytes(self,hex_str, dis_success = False):

        try:
            cmd_hex = hex_str.replace("0x","")
            cmd_bytes = bytes.fromhex(cmd_hex)

            protocol = CH341AIIC()
            protocol.set_clk(protocol.IIC_CLK_100kHz)
            result = protocol.write_bytes(cmd_bytes)
            print(str(cmd_bytes.hex()))
            if dis_success&result:
                QMessageBox.information(self,"提示","发送成功")
            elif dis_success:
                QMessageBox.information(self, "错误", "发送失败,请检查硬件" )
        except Exception as e:
            print(str(e))
            QMessageBox.information(self,"错误","发送失败,请检查硬件"+str(e))



    def init_default_display(self):
        # size
        self.__desktop = QApplication.desktop()
        qRect = self.__desktop.screenGeometry()  # 设备屏幕尺寸
        self.resize(qRect.width() * 45/ 100, qRect.height() * 90 / 100)
        self.move(qRect.width() / 3, qRect.height() / 30)


    def init_watch_table_all(self):


        self.watch_modle_dev_set = QStandardItemModel(64, 3)
        self.watch_table_dev_set.setModel(self.watch_modle_dev_set)


        self.watch_modle_dev_info = QStandardItemModel(24, 3)
        self.watch_table_dev_info.setModel(self.watch_modle_dev_info)

        self.watch_modle_usr_info = QStandardItemModel(128, 3)
        self.watch_table_usr_info.setModel(self.watch_modle_usr_info)

        self.watch_modle_usr_bia = QStandardItemModel(128, 3)
        self.watch_table_usr_bia.setModel(self.watch_modle_usr_bia)

        # page2
        self.watch_modle_analy_result = QStandardItemModel(128, 3)
        self.watch_table_analy_result.setModel(self.watch_modle_analy_result)

        self.watch_modle_tst_middle = QStandardItemModel(128, 3)
        self.watch_table_tst_middle.setModel(self.watch_modle_tst_middle)

        self.watch_modle_com_log = QStandardItemModel(24, 3)
        self.watch_table_com_log.setModel(self.watch_modle_com_log)

        self.watch_modle_res_real = QStandardItemModel(128, 3)
        self.watch_table_res_real.setModel(self.watch_modle_res_real)



    def update_watch_table_display(self):

        # 查询数据库数据
        # self.watch_modle.setItem(0,0,QStandardItem("示例"))
        self.progress_bar = QProgressDialog()

        try:
            protocol = CH341AIIC()
            protocol.set_clk(protocol.IIC_CLK_100kHz)
            # print("逐个读地址：", hex(address_read))
            self.progress_bar.setWindowTitle("更新RAM中....")
            self.progress_bar_current = 0
            self.progress_bar_total = (64 + 24 + 128 + 128 + 128 + 128 + 128 + 24)
            self.progress_bar.setWindowIcon(QIcon(":picture/img/110.png"))
            self.progress_bar.show()

            self.update_table(protocol, start_addr=0x1000, read_length=64, watch_modle=self.watch_modle_dev_set)

            self.update_table(protocol, start_addr=0x1040, read_length=24, watch_modle=self.watch_modle_dev_info)

            self.update_table(protocol, start_addr=0x1058, read_length=128, watch_modle=self.watch_modle_usr_info)

            self.update_table(protocol, start_addr=0x10d8, read_length=128, watch_modle=self.watch_modle_usr_bia)

            # page 2
            self.update_table(protocol, start_addr=0x1158, read_length=128, watch_modle=self.watch_modle_analy_result)

            self.update_table(protocol, start_addr=0x11d8, read_length=128, watch_modle=self.watch_modle_tst_middle)

            self.update_table(protocol, start_addr=0x1258, read_length=24, watch_modle=self.watch_modle_com_log)

            self.update_table(protocol, start_addr=0x1270, read_length=128, watch_modle=self.watch_modle_res_real)
        except Exception as e:
            QMessageBox.information(self,"错误",str(e))





    def update_table(self,protocol, start_addr,read_length,watch_modle):
        for i in range(read_length):
            ret = protocol.read_byte(start_addr + i)
            if ret[0] == True:
                for x in ret[1]:
                    watch_modle.setItem(i, 0, QStandardItem("%s + "%(hex(start_addr))+str(hex(i)+"="+hex(start_addr+i))))
                    watch_modle.setItem(i, 1, QStandardItem(str(hex(x))))
                    self.progress_bar_current = self.progress_bar_current+1
                    self.progress_bar.setValue(self.progress_bar_current*100/self.progress_bar_total)
                    QtCore.QCoreApplication.processEvents()
            else:
                print("读取失败...")
                self.progress_bar.close()
                raise  Exception("读取失败，请检查硬件。")




    def on_click_watch_table_view(self, model_index):
        pass
        print("add:",model_index.row(),model_index.column())
        # QMessageBox.information(self,"提示","隐藏当前列",QMessageBox.Yes|QMessageBox.No)

class Custum_complains(QThread):
      # const
      def  __init__(self):
          super(Custum_complains, self).__init__()
      def run(self):
          pass
          try:
              # 串口工作主流程
              """主循环"""
              while True:
                pass
                time.sleep(0.1)
          except Exception as e:
                print(str(e))

      def mainloop_app(self):
          try:
              pass
              app = QtWidgets.QApplication(sys.argv)
              window = MyApp()
              window.show()
              pass
          except Exception as e:
              print(str(e))
          finally:
              sys.exit(app.exec_())

if __name__ == "__main__":
    try:
        custum = Custum_complains()
        custum.start()
        custum.mainloop_app()
    except Exception as e:
        print(str(e))
    finally:
        pass




