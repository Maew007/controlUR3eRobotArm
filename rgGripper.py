import pycurl
from io import BytesIO
import xmlrpc.client
class RG2:
    def __init__(self, robot_ip, rg_id):
        self.rg_id = rg_id
        self.robot_ip = robot_ip

    def get_rg_width(self):
        xml_request = f"""<?xml version="1.0"?>
    <methodCall>
        <methodName>rg_get_width</methodName>
            <params>
                <param>
                    <value><int>{self.rg_id}</int></value>
                </param>
            </params>
    </methodCall>"""

        headers = ["Content-Type: application/x-www-form-urlencoded"]

        data = xml_request.replace('\r\n','').encode()

        # Create a new cURL object
        curl = pycurl.Curl()

        # Set the URL to fetch
        curl.setopt(curl.URL, f'http://{self.robot_ip}:41414')
        curl.setopt(curl.HTTPHEADER, headers)
        curl.setopt(curl.POSTFIELDS, data)
        # Create a BytesIO object to store the response
        buffer = BytesIO()
        curl.setopt(curl.WRITEDATA, buffer)

        # Perform the request
        curl.perform()

        # Get the response body
        response = buffer.getvalue()

        # Print the response
        print(response.decode('utf-8'))

        # Close the cURL object
        curl.close()

        xml_response = xmlrpc.client.loads(response.decode('utf-8'))
        rg_width = float(xml_response[0][0])
        #print(rg_width)
        return rg_width


    def rg_grip(self, target_width: float = 100, target_force: float= 10) -> bool:
        #assert target_width <= 100 and target_width >= 0, 'Target Width must be within the range [0,100]'
        #assert target_force <= 40 or target_force >= 0, 'Target force must be within the range [0,40]'

        # WARNING: params will be sent straight to electrical system with no error checking on robot!
        # if (target_width > 100):
        #     target_width = 100
        # if(target_width < 0):
        #     target_width = 0
        # if(target_force > 40):
        #     target_force = 40
        # if(target_force < 0):
        #     target_force = 0

        xml_request = f"""<?xml version="1.0"?>
    <methodCall>
    <methodName>rg_grip</methodName>
        <params>
            <param>
                <value><int>{self.rg_id}</int></value>
            </param>
            <param>
                <value><double>{target_width}</double></value>
            </param>
            <param>
                <value><double>{target_force}</double></value>
            </param>
        </params>
    </methodCall>"""

        headers = ["Content-Type: application/x-www-form-urlencoded"]

        # headers = ["User-Agent: Python-PycURL", "Accept: application/json"]
        data = xml_request.replace('\r\n','').encode()
        # Create a new cURL object
        curl = pycurl.Curl()

        # Set the URL to fetch
        curl.setopt(curl.URL, f'http://{self.robot_ip}:41414')
        curl.setopt(curl.HTTPHEADER, headers)
        curl.setopt(curl.POSTFIELDS, data)
        # Create a BytesIO object to store the response
        buffer = BytesIO()
        curl.setopt(curl.WRITEDATA, buffer)

        # Perform the request
        curl.perform()

        # Get the response body
        response = buffer.getvalue()

        # Print the response
        print(response.decode('utf-8'))

        # Close the cURL object
        curl.close()