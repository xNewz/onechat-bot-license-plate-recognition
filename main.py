import requests
from flask import Flask, request, jsonify
from one_chat import init, send_message

app = Flask(__name__)

# Initialize OneChat
init(
    "YOUR_AUTHORIZATION_TOKEN",  # Replace with your token
    "DEFAULT_RECIPIENT_ID",      # Replace with user ID or group ID
    "YOUR_BOT_ID"                # Replace with your bot ID
)


@app.route("/webhook", methods=["POST"])
def webhook():
    if not request.is_json:
        return jsonify({"status": "error", "message": "Invalid request"}), 400

    data = request.get_json()
    if data.get("event") == "message":
        handle_message(data)

    return jsonify({"status": "success", "message": "Webhook received"}), 200


def convert_province(province):
    province_mapping = {
        "10": "กรุงเทพมหานคร",
        "11": "สมุทรปราการ",
        "12": "นนทบุรี",
        "13": "ปทุมธานี",
        "14": "พระนครศรีอยุธยา",
        "15": "อ่างทอง",
        "16": "ลพบุรี",
        "17": "สิงห์บุรี",
        "18": "ชัยนาท",
        "19": "สระบุรี",
        "20": "ชลบุรี",
        "21": "ระยอง",
        "22": "จันทบุรี",
        "23": "ตราด",
        "24": "ฉะเชิงเทรา",
        "25": "ปราจีนบุรี",
        "26": "นครนายก",
        "27": "สระแก้ว",
        "30": "นครราชสีมา",
        "31": "บุรีรัมย์",
        "32": "สุรินทร์",
        "33": "ศรีสะเกษ",
        "34": "อุบลราชธานี",
        "35": "ยโสธร",
        "36": "ชัยภูมิ",
        "37": "อำนาจเจริญ",
        "38": "บึงกาฬ",
        "39": "หนองบัวลำภู",
        "40": "ขอนแก่น",
        "41": "อุดรธานี",
        "42": "เลย",
        "43": "หนองคาย",
        "44": "มหาสารคาม",
        "45": "ร้อยเอ็ด",
        "46": "กาฬสินธุ์",
        "47": "สกลนคร",
        "48": "นครพนม",
        "49": "มุกดาหาร",
        "50": "เชียงใหม่",
        "51": "ลำพูน",
        "52": "ลำปาง",
        "53": "อุตรดิตถ์",
        "54": "แพร่",
        "55": "น่าน",
        "56": "พะเยา",
        "57": "เชียงราย",
        "58": "แม่ฮ่องสอน",
        "60": "นครสวรรค์",
        "61": "อุทัยธานี",
        "62": "กำแพงเพชร",
        "63": "ตาก",
        "64": "สุโขทัย",
        "65": "พิษณุโลก",
        "66": "พิจิตร",
        "67": "เพชรบูรณ์",
        "70": "ราชบุรี",
        "71": "กาญจนบุรี",
        "72": "สุพรรณบุรี",
        "73": "นครปฐม",
        "74": "สมุทรสาคร",
        "75": "สมุทรสงคราม",
        "76": "เพชรบุรี",
        "77": "ประจวบคีรีขันธ์",
        "80": "นครศรีธรรมราช",
        "81": "กระบี่",
        "82": "พังงา",
        "83": "ภูเก็ต",
        "84": "สุราษฎร์ธานี",
        "85": "ระนอง",
        "86": "ชุมพร",
        "90": "สงขลา",
        "91": "สตูล",
        "92": "ตรัง",
        "93": "พัทลุง",
        "94": "ปัตตานี",
        "95": "ยะลา",
        "96": "นราธิวาส",
        "97": "เบตง",
    }

    province_code = province.split("-")[-1]
    return province_mapping.get(province_code, "Unknown province code")


def handle_message(data):
    message_data = data.get("message", {})
    if message_data.get("type") == "image":
        file_url = message_data.get("file")
        if file_url:
            filename = download_image(file_url)
            if filename:
                result = process(filename)
                if result:
                    send_message(message=str(result))


def download_image(file_url):
    try:
        response = requests.get(file_url)
        if response.status_code == 200:
            filename = "image.jpg"
            with open(filename, "wb") as f:
                f.write(response.content)
            return filename
    except Exception as e:
        print(f"Error downloading image: {e}")
    return None


def process(filename):
    sk = "sk_xxxxxxxxx" # your openalpr secret key
    url = f"https://api.openalpr.com/v2/recognize?recognize_vehicle=1&country=th&secret_key={sk}"

    try:
        with open(filename, "rb") as image_file:
            r = requests.post(url, files={"image": image_file})

        if r.status_code == 200:
            result = r.json()
            if result.get("results"):
                plate_info = result["results"][0]
                license_plate = plate_info["plate"]
                province = convert_province(plate_info["region"])
                return f"ป้ายทะเบียน: {license_plate}\nจังหวัด: {province}"
    except Exception as e:
        print(f"Error processing image: {e}")

    return None


if __name__ == "__main__":
    app.run(ssl_context="adhoc", port=8080)
