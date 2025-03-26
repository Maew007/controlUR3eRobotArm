import socket
import time
import math
import struct

class UR3Controller:
    def __init__(self, host, port=30002):
        """
        เริ่มต้นการเชื่อมต่อกับ UR3 ผ่าน TCP/IP
        
        Args:
            host (str): IP address ของแขนกล UR3
            port (int): พอร์ตสำหรับการเชื่อมต่อ (ค่าเริ่มต้นคือ 30002 สำหรับควบคุมโดยตรง)
        """
        self.host = host
        self.port = port
        self.socket = None
        
    def connect(self):
        """เชื่อมต่อกับแขนกล UR3"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"เชื่อมต่อกับ UR3 ที่ {self.host}:{self.port} สำเร็จแล้ว")
            return True
        except Exception as e:
            print(f"การเชื่อมต่อล้มเหลว: {e}")
            return False
            
    def disconnect(self):
        """ยกเลิกการเชื่อมต่อจาก UR3"""
        if self.socket:
            self.socket.close()
            self.socket = None
            print("ยกเลิกการเชื่อมต่อแล้ว")
            
    def move_to_pose(self, x, y, z, rx, ry, rz, a=1.2, v=0.25, t=0, r=0):
        """
        ส่งคำสั่งให้แขนกล UR3 เคลื่อนที่ไปยังตำแหน่งและการหมุนที่กำหนด
        
        Args:
            x, y, z (float): ตำแหน่งปลายแขนกลใน (เมตร)
            rx, ry, rz (float): การหมุนรอบแกน x, y, z (เรเดียน)
            a (float): ความเร่ง (m/s^2)
            v (float): ความเร็ว (m/s)
            t (float): เวลาที่ใช้ในการเคลื่อนที่ (วินาที) - 0 หมายถึงใช้ความเร็วและความเร่งที่กำหนด
            r (float): รัศมีการเคลื่อนที่ (เมตร) - 0 คือหยุดที่จุดที่กำหนดอย่างเต็มที่
        
        Returns:
            bool: สถานะการส่งคำสั่ง
        """
        if not self.socket:
            print("ไม่ได้เชื่อมต่อกับ UR3 กรุณาเชื่อมต่อก่อน")
            return False
            
        try:
            # สร้างคำสั่ง URScript สำหรับการเคลื่อนที่
            command = f"movej(p[{x}, {y}, {z}, {rx}, {ry}, {rz}], a={a}, v={v}, t={t}, r={r})\n"
            
            # ส่งคำสั่งไปยัง UR3
            self.socket.send(command.encode('utf-8'))
            print(f"ส่งคำสั่งเคลื่อนที่ไปยัง: x={x}, y={y}, z={z}, rx={rx}, ry={ry}, rz={rz}")
            return True
        except Exception as e:
            print(f"การส่งคำสั่งล้มเหลว: {e}")
            return False
            
    def move_linear(self, x, y, z, rx, ry, rz, a=1.2, v=0.11, t=0, r=0):
        """
        ส่งคำสั่งให้แขนกล UR3 เคลื่อนที่เป็นเส้นตรงไปยังตำแหน่งและการหมุนที่กำหนด
        
        Args:
            คล้ายกับ move_to_pose แต่ใช้การเคลื่อนที่เป็นเส้นตรง
        
        Returns:
            bool: สถานะการส่งคำสั่ง
        """
        if not self.socket:
            print("ไม่ได้เชื่อมต่อกับ UR3 กรุณาเชื่อมต่อก่อน")
            return False
            
        try:
            # สร้างคำสั่ง URScript สำหรับการเคลื่อนที่เป็นเส้นตรง
            command = f"movel(p[{x}, {y}, {z}, {rx}, {ry}, {rz}], a={a}, v={v}, t={t}, r={r})\n"
            
            # ส่งคำสั่งไปยัง UR3
            self.socket.send(command.encode('utf-8'))
            print(f"ส่งคำสั่งเคลื่อนที่เป็นเส้นตรงไปยัง: x={x}, y={y}, z={z}, rx={rx}, ry={ry}, rz={rz}")
            return True
        except Exception as e:
            print(f"การส่งคำสั่งล้มเหลว: {e}")
            return False
    
    def get_current_pose(self):
        """
        ขอข้อมูลตำแหน่งปัจจุบันของแขนกล UR3
        
        Returns:
            list: [x, y, z, rx, ry, rz] หรือ None ถ้าล้มเหลว
        """
        if not self.socket:
            print("ไม่ได้เชื่อมต่อกับ UR3 กรุณาเชื่อมต่อก่อน")
            return None
            
        try:
            # วิธีที่ 1: ใช้ RTDE (Real-Time Data Exchange) หรือช่องทางข้อมูลแบบเรียลไทม์
            # สร้างซ็อกเก็ตใหม่สำหรับพอร์ต 30003 (Real-time data)
            data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            data_socket.connect((self.host, 30003))
            data_socket.settimeout(1)
            
            # รับข้อมูลไบนารี (ไม่ใช่ UTF-8)
            data = data_socket.recv(1116)  # ขนาดข้อมูลที่ UR ส่งมา (อาจแตกต่างกันตามรุ่น)
            data_socket.close()
            
            if len(data) >= 444:  # ตรวจสอบว่าได้รับข้อมูลเพียงพอหรือไม่
                # แปลงข้อมูลไบนารีเป็นค่าตำแหน่ง
                # ตำแหน่ง TCP เริ่มต้นที่ตำแหน่ง 444 ในข้อมูล (สำหรับ UR3 รุ่นใหม่)
                # ข้อมูลแต่ละตัวเป็น double (8 ไบต์)
                x = struct.unpack('!d', data[444:452])[0]
                y = struct.unpack('!d', data[452:460])[0]
                z = struct.unpack('!d', data[460:468])[0]
                rx = struct.unpack('!d', data[468:476])[0]
                ry = struct.unpack('!d', data[476:484])[0]
                rz = struct.unpack('!d', data[484:492])[0]
                
                return [x, y, z, rx, ry, rz]
            else:
                print("ได้รับข้อมูลไม่เพียงพอจาก UR3")
                return None
                
        except Exception as e:
            print(f"การรับข้อมูลตำแหน่งล้มเหลว: {e}")
            
            # วิธีที่ 2: ใช้การส่งคำสั่งและรอรับผลลัพธ์
            try:
                # ส่งคำสั่งเพื่อขอข้อมูลตำแหน่ง
                command = "get_actual_tcp_pose()\n"
                self.socket.send(command.encode('utf-8'))
                
                # รอรับข้อมูลผลลัพธ์ (อาจต้องปรับเปลี่ยนตามรุ่นของ UR)
                time.sleep(0.1)  # รอให้ UR3 ประมวลผลคำสั่ง
                result = self.socket.recv(1024)
                
                # แยกข้อมูลและแปลงเป็นตัวเลข
                # หมายเหตุ: รูปแบบผลลัพธ์อาจแตกต่างกันขึ้นอยู่กับรุ่นและเฟิร์มแวร์
                result_str = result.decode('utf-8', errors='replace')  # ใช้ 'replace' เพื่อจัดการกับข้อมูลที่ไม่ใช่ UTF-8
                
                # แยกส่วนที่เป็นตำแหน่ง
                # ตัวอย่าง: "p[0.1, 0.2, 0.3, 0.0, 3.14, 0.0]"
                start_idx = result_str.find("p[")
                end_idx = result_str.find("]", start_idx)
                
                if start_idx != -1 and end_idx != -1:
                    pose_str = result_str[start_idx+2:end_idx]
                    pose_values = [float(val.strip()) for val in pose_str.split(',')]
                    if len(pose_values) == 6:
                        return pose_values
                
                print("ไม่สามารถแยกค่าตำแหน่งจากผลลัพธ์ได้")
                return None
                
            except Exception as e2:
                print(f"วิธีที่ 2 ล้มเหลว: {e2}")
                
                # วิธีที่ 3: ใช้ Dashboard Server (พอร์ต 29999)
                try:
                    dashboard = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    dashboard.connect((self.host, 29999))
                    dashboard.settimeout(1)
                    
                    # ส่งคำสั่ง get pose ผ่าน Dashboard
                    dashboard.send("get actual_tcp_pose\n".encode('utf-8'))
                    response = dashboard.recv(1024)
                    dashboard.close()
                    
                    response_str = response.decode('utf-8', errors='replace')
                    # ตัวอย่างผลลัพธ์: "p[0.1, 0.2, 0.3, 0.0, 3.14, 0.0]"
                    start_idx = response_str.find("p[")
                    end_idx = response_str.find("]", start_idx)
                    
                    if start_idx != -1 and end_idx != -1:
                        pose_str = response_str[start_idx+2:end_idx]
                        pose_values = [float(val.strip()) for val in pose_str.split(',')]
                        if len(pose_values) == 6:
                            return pose_values
                    
                    print("ไม่สามารถอ่านตำแหน่งผ่าน Dashboard Server ได้")
                    return None
                    
                except Exception as e3:
                    print(f"ทุกวิธีล้มเหลว: {e3}")
                    return None

    def send_ur_script(script):
        """ส่ง URScript ไปยังหุ่นยนต์ UR3e"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            #เชื่อมต่อกับแขนกล
            sock.connect((ur3_ip, 30002))
            #้ถ้าสามารถเชื่อมต่อได้ให้ทำการเข้ารหัสสคลิปเพื่อส่งไปยังแขนกล
            sock.sendall(script.encode())
    def move_to_org():    
        # คำสั่ง URScript ให้แขนไปที่ตำแหน่งที่กำหนด
        base = math.radians(0)
        shoulder = math.radians(-90)
        elbow = math.radians(-90)
        wrist1 = math.radians(-90)
        wrist2 = math.radians(90)
        wrist3 = math.radians(0)
        script = f"""
        def my_program():    
            movej([{base},{shoulder},{elbow},{wrist1},{wrist2},{wrist3}] , a=1, v=0.5)
            end
        """
        UR3Controller.send_ur_script(script)
    
    def move_to_org2():  
        x, y, z = 0.3000, 0.00, 0.3500  # ตำแหน่ง (เมตร)
        rx, ry, rz = 2.2185,-2.2185, 0.0006  # การหมุน (เรเดียน)
        robot.move_linear(x,y,z,rx,ry,rz)
        print("รอให้แขนกลเคลื่อนที่เสร็จ...")
        time.sleep(5)    

    def stop_robot():
        print("---- สั่งให้แขนกลหยุดการทำงาน ----")
        script = """
        def my_program():
            stopj(2.0) # a=2.0 is the acceleration
            end
        """
        UR3Controller.send_ur_script(script)
# ตัวอย่างการใช้งาน
if __name__ == "__main__":
    # กำหนด IP address ของแขนกล UR3
    ur3_ip = "10.1.63.10"  # แก้ไขเป็น IP address จริงของแขนกล
    
    # สร้างอ็อบเจกต์ควบคุม
    robot = UR3Controller(ur3_ip)
    
    # เชื่อมต่อกับแขนกล
    if robot.connect():
        try:
            while True:
                #UR3Controller.move_to_org()
                #time.sleep(5)
                # อ่านตำแหน่งปัจจุบันก่อน
                print("กำลังอ่านตำแหน่งปัจจุบัน...")
                current_pose = robot.get_current_pose()
                if current_pose:
                    print(f"ตำแหน่งปัจจุบัน: x={current_pose[0]:.4f}, y={current_pose[1]:.4f}, z={current_pose[2]:.4f}, rx={current_pose[3]:.4f}, ry={current_pose[4]:.4f}, rz={current_pose[5]:.4f}")
                
                # ตัวอย่างการเคลื่อนที่ไปยังตำแหน่งที่กำหนด
                # ค่าตำแหน่งในหน่วยเมตร และมุมในหน่วยเรเดียน
                x, y, z = 0.3000, -0.1415, 0.3500 # ตำแหน่ง (เมตร)
                rx, ry, rz = 2.2185,-2.2185, 0.0006  # การหมุน (เรเดียน)
                
                # ส่งคำสั่งเคลื่อนที่
                print(f"กำลังเคลื่อนที่ไปยัง ตำแหน่งที่ 1: x={x}, y={y}, z={z}, rx={rx}, ry={ry}, rz={rz}")
                robot.move_to_pose(x, y, z, rx, ry, rz)
                
                # รอให้แขนกลเคลื่อนที่เสร็จ
                print("รอให้แขนกลเคลื่อนที่เสร็จ...")
                time.sleep(5)
                
                # อ่านตำแหน่งปัจจุบันอีกครั้ง
                current_pose = robot.get_current_pose()
                if current_pose:
                    print(f"ตำแหน่งปัจจุบัน: x={current_pose[0]:.4f}, y={current_pose[1]:.4f}, z={current_pose[2]:.4f}, rx={current_pose[3]:.4f}, ry={current_pose[4]:.4f}, rz={current_pose[5]:.4f}")
                    
                # ตัวอย่างการเคลื่อนที่เป็นเส้นตรง
                print("กำลังเคลื่อนที่เป็นเส้นตรง...จุดที่ 2")
                x, y, z = 0.3000, 0.3287, 0.3500  # ตำแหน่ง (เมตร)
                rx, ry, rz = 2.2185,-2.2185, 0.0006  # การหมุน (เรเดียน)
                robot.move_linear(x,y,z,rx,ry,rz)
                print("รอให้แขนกลเคลื่อนที่เสร็จ...")
                time.sleep(5)
                
                current_pose = robot.get_current_pose()
                if current_pose:
                    print(f"ตำแหน่งปัจจุบัน: x={current_pose[0]:.4f}, y={current_pose[1]:.4f}, z={current_pose[2]:.4f}, rx={current_pose[3]:.4f}, ry={current_pose[4]:.4f}, rz={current_pose[5]:.4f}")
                    
                # ตัวอย่างการเคลื่อนที่เป็นเส้นตรง
                print("กำลังเคลื่อนที่เป็นเส้นตรง... จุดที่ 3")
                x, y, z = 0.3130, 0.3287, 0.3500  # ตำแหน่ง (เมตร)
                rx, ry, rz = 2.2185,-2.2185, 0.0006  # การหมุน (เรเดียน)
                robot.move_linear(x,y,z,rx,ry,rz)
                print("รอให้แขนกลเคลื่อนที่เสร็จ...")
                time.sleep(5)
                
                current_pose = robot.get_current_pose()
                if current_pose:
                    print(f"ตำแหน่งปัจจุบัน: x={current_pose[0]:.4f}, y={current_pose[1]:.4f}, z={current_pose[2]:.4f}, rx={current_pose[3]:.4f}, ry={current_pose[4]:.4f}, rz={current_pose[5]:.4f}")
                    
                # ตัวอย่างการเคลื่อนที่เป็นเส้นตรง
                print("กำลังเคลื่อนที่เป็นเส้นตรง... จุดที่ 4")
                x, y, z = -0.080, 0.3287, 0.3500  # ตำแหน่ง (เมตร)
                rx, ry, rz = 2.2185,-2.2185, 0.0006  # การหมุน (เรเดียน)
                robot.move_linear(x,y,z,rx,ry,rz)
                print("รอให้แขนกลเคลื่อนที่เสร็จ...")
                time.sleep(5)
                
                current_pose = robot.get_current_pose()
                if current_pose:
                    print(f"ตำแหน่งปัจจุบัน: x={current_pose[0]:.4f}, y={current_pose[1]:.4f}, z={current_pose[2]:.4f}, rx={current_pose[3]:.4f}, ry={current_pose[4]:.4f}, rz={current_pose[5]:.4f}")
                    
                # ตัวอย่างการเคลื่อนที่เป็นเส้นตรง
                print("กำลังเคลื่อนที่เป็นเส้นตรง... จุดที่ 5")
                x, y, z = -0.080, 0.2308, 0.3500  # ตำแหน่ง (เมตร)
                rx, ry, rz = 2.2185,-2.2185, 0.0006  # การหมุน (เรเดียน)
                robot.move_linear(x,y,z,rx,ry,rz)
                print("รอให้แขนกลเคลื่อนที่เสร็จ...")
                time.sleep(5)
                
                current_pose = robot.get_current_pose()
                if current_pose:
                    print(f"ตำแหน่งปัจจุบัน: x={current_pose[0]:.4f}, y={current_pose[1]:.4f}, z={current_pose[2]:.4f}, rx={current_pose[3]:.4f}, ry={current_pose[4]:.4f}, rz={current_pose[5]:.4f}")
                    
                # ตัวอย่างการเคลื่อนที่เป็นเส้นตรง
                print("กำลังเคลื่อนที่เป็นเส้นตรง... จุดที่ 6")
                x, y, z = 0.3713, 0.2308, 0.3500  # ตำแหน่ง (เมตร)
                rx, ry, rz = 2.2185,-2.2185, 0.0006  # การหมุน (เรเดียน)
                robot.move_linear(x,y,z,rx,ry,rz)
                print("รอให้แขนกลเคลื่อนที่เสร็จ...")
                time.sleep(5)
                
                current_pose = robot.get_current_pose()
                if current_pose:
                    print(f"ตำแหน่งปัจจุบัน: x={current_pose[0]:.4f}, y={current_pose[1]:.4f}, z={current_pose[2]:.4f}, rx={current_pose[3]:.4f}, ry={current_pose[4]:.4f}, rz={current_pose[5]:.4f}")
                    
                # ตัวอย่างการเคลื่อนที่เป็นเส้นตรง
                print("กำลังเคลื่อนที่เป็นเส้นตรง... จุดที่ 7")
                x, y, z = 0.3713, -0.1415, 0.3500  # ตำแหน่ง (เมตร)
                rx, ry, rz = 2.2185,-2.2185, 0.0006  # การหมุน (เรเดียน) ตำเเหน่งขวาสุด
                robot.move_linear(x,y,z,rx,ry,rz)
                print("รอให้แขนกลเคลื่อนที่เสร็จ...")
                time.sleep(5)
                
                current_pose = robot.get_current_pose()
                if current_pose:
                    print(f"ตำแหน่งปัจจุบัน: x={current_pose[0]:.4f}, y={current_pose[1]:.4f}, z={current_pose[2]:.4f}, rx={current_pose[3]:.4f}, ry={current_pose[4]:.4f}, rz={current_pose[5]:.4f}")
                    
                # ตัวอย่างการเคลื่อนที่เป็นเส้นตรง
                print("กำลังเคลื่อนที่เป็นเส้นตรง... จุดที่ 8")
                x, y, z = 0.3713, 0.2467, 0.3500  # ตำแหน่ง (เมตร)
                rx, ry, rz = 2.2185,-2.2185, 0.0006  # การหมุน (เรเดียน) ตำเเหน่งขวาสุด
                robot.move_linear(x,y,z,rx,ry,rz)
                print("รอให้แขนกลเคลื่อนที่เสร็จ...")
                time.sleep(5)
                
                current_pose = robot.get_current_pose()
                if current_pose:
                    print(f"ตำแหน่งปัจจุบัน: x={current_pose[0]:.4f}, y={current_pose[1]:.4f}, z={current_pose[2]:.4f}, rx={current_pose[3]:.4f}, ry={current_pose[4]:.4f}, rz={current_pose[5]:.4f}")
                    
                # ตัวอย่างการเคลื่อนที่เป็นเส้นตรง
                print("กำลังเคลื่อนที่เป็นเส้นตรง... จุดที่ 9")
                x, y, z = 0.3130, 0.2467, 0.3500  # ตำแหน่ง (เมตร)
                rx, ry, rz = 2.2185,-2.2185, 0.0006  # การหมุน (เรเดียน) ตำเเหน่งขวาสุด
                robot.move_linear(x,y,z,rx,ry,rz)
                print("รอให้แขนกลเคลื่อนที่เสร็จ...")
                time.sleep(5)
                
                current_pose = robot.get_current_pose()
                if current_pose:
                    print(f"ตำแหน่งปัจจุบัน: x={current_pose[0]:.4f}, y={current_pose[1]:.4f}, z={current_pose[2]:.4f}, rx={current_pose[3]:.4f}, ry={current_pose[4]:.4f}, rz={current_pose[5]:.4f}")
                    
                # ตัวอย่างการเคลื่อนที่เป็นเส้นตรง
                print("กำลังเคลื่อนที่เป็นเส้นตรง...")
                x, y, z = 0.3130, 0.3287, 0.3500  # ตำแหน่ง (เมตร)
                rx, ry, rz = 2.2185,-2.2185, 0.0006  # การหมุน (เรเดียน)
                robot.move_linear(x,y,z,rx,ry,rz)
                print("รอให้แขนกลเคลื่อนที่เสร็จ...")
                time.sleep(5)
                
                current_pose = robot.get_current_pose()
                if current_pose:
                    print(f"ตำแหน่งปัจจุบัน: x={current_pose[0]:.4f}, y={current_pose[1]:.4f}, z={current_pose[2]:.4f}, rx={current_pose[3]:.4f}, ry={current_pose[4]:.4f}, rz={current_pose[5]:.4f}")
                    
                # ตัวอย่างการเคลื่อนที่เป็นเส้นตรง
                print("กำลังเคลื่อนที่เป็นเส้นตรง...")
                x, y, z = 0.3000, 0.3287, 0.3500  # ตำแหน่ง (เมตร)
                rx, ry, rz = 2.2185,-2.2185, 0.0006  # การหมุน (เรเดียน)
                robot.move_linear(x,y,z,rx,ry,rz)
                print("รอให้แขนกลเคลื่อนที่เสร็จ...")
                time.sleep(5)
                

                

            
            
                


        except KeyboardInterrupt:       
            #UR3Controller.move_to_org2() 
            #print("\nกลับไปที่จุดเริ่มต้น")   
            #time.sleep(5)
             # อ่านตำแหน่งปัจจุบันก่อน
            print("กำลังอ่านตำแหน่งปัจจุบัน...")
            current_pose = robot.get_current_pose()
            if current_pose:
                print(f"ตำแหน่งปัจจุบัน: x={current_pose[0]:.4f}, y={current_pose[1]:.4f}, z={current_pose[2]:.4f}, rx={current_pose[3]:.4f}, ry={current_pose[4]:.4f}, rz={current_pose[5]:.4f}")
            
            UR3Controller.stop_robot()
            print("\nDetected Ctrl + C. หยุดการทำงาน robot...")

        finally:
            # ยกเลิกการเชื่อมต่อเมื่อเสร็จสิ้น
            robot.disconnect()