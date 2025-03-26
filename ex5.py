
import rgGripper
import time

def test_start():

    # Default id is zero, if you have multiple grippers, 
    # see logs in UR Teach Pendant to know which is which :)
    print("Main")
    rg_id = 0
    ip = "10.1.63.10"
    rg_gripper = rgGripper.RG2(ip,rg_id)

    rg_width = rg_gripper.get_rg_width()
    print("rg_width: ",rg_width)
    
    target_force = 40.00

    rg_gripper.rg_grip(100.0, target_force)
    time.sleep(3)
    rg_gripper.rg_grip(50.0, target_force)
    time.sleep(3)
    rg_gripper.rg_grip(80.0, target_force)
    time.sleep(3)
    rg_gripper.rg_grip(10.0, target_force)
    time.sleep(3)


if __name__ == "__main__":
        print("เริ่มการทำงาน")
        try:
            test_start()
        except KeyboardInterrupt:    
           
            print("\nDetected Ctrl + C. หยุดการทำงาน robot...")

        finally:
            # ยกเลิกการเชื่อมต่อเมื่อเสร็จสิ้น
             print("\nDetected Ctrl + C. หยุดการทำงาน robot...")  