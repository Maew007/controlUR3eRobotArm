import time
import socket
import math  # ใช้แปลงองศาเป็นเรเดียน

# IP และ PORT ของหุ่นยนต์ UR3e
ROBOT_IP = "10.1.63.10"
ROBOT_PORT = 30003  #หมายเลขพอร์ตที่ใช้ค่าเริ่มต้นตามโรงงานอยู่ที่หมายเลข 30003

def send_ur_script(script):
    """ส่ง URScript ไปยังหุ่นยนต์ UR3e"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        #เชื่อมต่อกับแขนกล
        sock.connect((ROBOT_IP, ROBOT_PORT))
        #้ถ้าสามารถเชื่อมต่อได้ให้ทำการเข้ารหัสสคลิปเพื่อส่งไปยังแขนกล
        sock.sendall(script.encode())

def stop_robot():
    print("---- สั่งให้แขนกลหยุดการทำงาน ----")
    script = """
    def my_program():
        stopj(2.0) # a=2.0 is the acceleration
        end
    """
    send_ur_script(script)
def move_joint_to(base=0,shoulder=-90,elbow=0,wrist1=-90,wrist2=0,wrist3=0):    
    base = math.radians(base)
    shoulder = math.radians(shoulder)
    elbow = math.radians(elbow)
    wrist1 = math.radians(wrist1)
    wrist2 = math.radians(wrist2)
    wrist3 = math.radians(wrist3)
    script = f"""
    def my_program():    
        movej([{base},{shoulder},{elbow},{wrist1},{wrist2},{wrist3}] , a=1, v=0.5)
        end
    """
    send_ur_script(script)
def move_to_org():    
    # คำสั่ง URScript ให้แขนไปที่ตำแหน่งที่กำหนด
    base = math.radians(0)
    shoulder = math.radians(-90)
    elbow = math.radians(0)
    wrist1 = math.radians(-90)
    wrist2 = math.radians(0)
    wrist3 = math.radians(0)
    script = f"""
    def my_program():    
        movej([{base},{shoulder},{elbow},{wrist1},{wrist2},{wrist3}] , a=1, v=0.5)
        end
    """
    send_ur_script(script)
if __name__ == "__main__":
    try:
        while True:
            #move_joint(base,elbow,sholder,wrist1,wrist2,wrist3,)  # สามารถกำหนดค่ามุมเป็น องศา Degree ได้เลย
            move_to_org()    
            print("แขนกลของท่านได้อยู่ในตำแหน่งเริ่มต้นพร้อมใช้งานแล้ว")      



    except KeyboardInterrupt:       
        stop_robot()
        print("\nDetected Ctrl + C. หยุดการทำงาน robot...")

    except ConnectionRefusedError:
        print(f"Connection refused. Please check the robot IP address ({ROBOT_IP}) and ensure the correct port ({ROBOT_PORT}) is open.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        print("Robot control program exited.")
