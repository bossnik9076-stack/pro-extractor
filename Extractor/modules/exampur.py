import base64
import json
import logging
import os
import re
from datetime import datetime
import pytz
import requests
from config import BOT_TEXT
from Extractor import app
from Extractor.core.utils import forward_to_log

try:
    from Cryptodome.Cipher import AES
except ImportError:
    from Crypto.Cipher import AES

logger = logging.getLogger(__name__)

# Constants & Encryption Configuration for Exampur
BASE_URL = "https://appapi.videocrypt.in/data_model"
APP_ID = "724"
AUTH_BEARER = "Bearer 01*#NerglnwwebOI)30@I*Dm'@@"
L_KEY = "%!F*&^$)_*%3f&B+"
Y_IV = "#*$DJvyw2w%!_-$@"
D_LEN = 16

BASE_HEADERS = {
    "Appid": APP_ID,
    "Authorization": AUTH_BEARER,
    "Lang": "1",
    "Devicetype": "4",
    "Jwt": "jwt",
    "Userid": "0",
    "Version": "1",
    "Content-Type": "application/json",
    "Origin": "https://app.exampur.com",
    "Referer": "https://app.exampur.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def b_pad(s: str) -> str:
    if len(s) < D_LEN:
        return s.ljust(D_LEN, "0")
    elif len(s) > D_LEN:
        return s[:D_LEN]
    return s

def h_permute(e: str, t: str) -> str:
    r = list(e)
    i = ""
    for char in t:
        if char.isdigit():
            idx = int(char)
            if idx < len(r):
                i += r[idx]
            else:
                i += r[0]
        else:
            i += r[0]
    return i

def pad_pkcs7(data: bytes) -> bytes:
    pad_len = 16 - (len(data) % 16)
    return data + bytes([pad_len] * pad_len)

def unpad_pkcs7(data: bytes) -> bytes:
    if not data:
        return data
    pad_len = data[-1]
    if pad_len < 1 or pad_len > 16:
        return data
    return data[:-pad_len]

def enc_payload(payload_dict: dict, t: str) -> str:
    r = h_permute(L_KEY, t) if t else L_KEY
    a = h_permute(Y_IV, t) if t else Y_IV
    key = b_pad(r).encode('utf-8')
    iv = a.encode('utf-8')
    cipher = AES.new(key, AES.MODE_CBC, iv)
    raw = json.dumps(payload_dict).encode('utf-8')
    padded = pad_pkcs7(raw)
    encrypted = cipher.encrypt(padded)
    b64_cipher = base64.b64encode(encrypted).decode('utf-8')
    fixed_iv = base64.b64encode(b"1234567890123456").decode('utf-8')
    return b64_cipher + ":" + fixed_iv

def dec_response(cipher_text: str, t: str) -> dict:
    if cipher_text.startswith('"') and cipher_text.endswith('"'):
        cipher_text = json.loads(cipher_text)
    r = h_permute(L_KEY, t) if t else L_KEY
    a = h_permute(Y_IV, t) if t else Y_IV
    key = b_pad(r).encode('utf-8')
    iv = a.encode('utf-8')
    cipher_part = cipher_text.split(":")[0]
    cipher_bytes = base64.b64decode(cipher_part)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad_pkcs7(cipher.decrypt(cipher_bytes))
    return json.loads(decrypted.decode('utf-8'))

def api_post(endpoint: str, payload_dict: dict, t_key: str, jwt_token: str = None, user_id: str = None) -> dict:
    headers = dict(BASE_HEADERS)
    if jwt_token:
        headers["Jwt"] = jwt_token
    if user_id:
        headers["Userid"] = str(user_id)
    
    enc_data = enc_payload(payload_dict, t_key)
    res = requests.post(f"{BASE_URL}/{endpoint}", headers=headers, json=enc_data, timeout=30)
    res_text = res.text.strip()
    return dec_response(res_text, t_key)

def extract_course_contents(course_id: str, t_user: str, jwt_token: str, user_id: str):
    """
    Recursively extracts all video & PDF links from an Exampur batch.
    """
    detail_res = api_post("course_deprecated/get_course_detail", {"course_id": str(course_id)}, t_user, jwt_token, user_id)
    if not detail_res.get("status"):
        return []
    
    data = detail_res.get("data", {})
    tiles = data.get("tiles", [])
    all_extracted_items = []
    
    for tile in tiles:
        tile_id = str(tile.get("id", ""))
        tile_name = tile.get("tile_name", "")
        if tile_id == "0":
            continue
        
        revert_api = tile.get("revert_api") or "1#0#0#0"
        
        def fetch_folder(folder_id="0", parent_id="0", page=1):
            folder_payload = {
                "course_id": str(course_id),
                "parent_id": str(parent_id),
                "folder_id": str(folder_id),
                "tile_id": str(tile_id),
                "type": f"content{tile_id}",
                "revert_api": revert_api,
                "page": page
            }
            try:
                res = api_post("content/get_folder_list", folder_payload, t_user, jwt_token, user_id)
                if not res.get("status"):
                    return
                
                res_data = res.get("data", {})
                if isinstance(res_data, dict):
                    file_results = res_data.get("file_result", [])
                    for f in file_results:
                        f_title = f.get("title", "").strip()
                        f_url = f.get("file_url", "").strip()
                        v_type = str(f.get("video_type", ""))
                        
                        # Formatting video URLs
                        if v_type == "1" or "youtube.com" in f_url or "youtu.be" in f_url or (f_url and not f_url.startswith("http") and len(f_url) < 20):
                            if not f_url.startswith("http"):
                                f_url = f"https://www.youtube.com/watch?v={f_url}"
                        
                        if f_url:
                            all_extracted_items.append((f_title, f_url))
                        
                        # Extract PDF if attached
                        if str(f.get("had_pdf")) == "1" or f.get("pdf_view_url"):
                            v_id = str(f.get("id", ""))
                            try:
                                pdf_res = api_post("poll/get_content_pdf", {"course_id": str(course_id), "video_id": v_id}, t_user, jwt_token, user_id)
                                if pdf_res.get("status"):
                                    for p in pdf_res.get("data", []):
                                        p_title = (p.get("pdf_title") or f"{f_title} (PDF)").strip()
                                        p_url = p.get("pdf_url") or p.get("tmp_pdf_url")
                                        if p_url:
                                            all_extracted_items.append((p_title, p_url))
                            except Exception as pe:
                                logger.error(f"Error fetching PDF: {pe}")
                    
                    # Traverse subfolders
                    folder_results = res_data.get("folder_result", [])
                    for sub_f in folder_results:
                        sub_id = str(sub_f.get("id"))
                        fetch_folder(folder_id=sub_id, parent_id=folder_id, page=1)
            except Exception as fe:
                logger.error(f"Error in folder {folder_id}: {fe}")
        
        fetch_folder(folder_id="0", parent_id="0", page=1)
        
    return all_extracted_items

async def exampur_txt(app, message):
    try:
        start_time = datetime.now()
        
        # User login prompt in Devanagari
        input1 = await app.ask(
            message.chat.id, 
            "👑 <b>EXAMPUR EXTRACTOR (NEW API 2026)</b> 👑\n\n"
            "कृपया अपनी लॉगिन जानकारी भेजें:\n"
            "1️⃣ <b>मोबाइल नंबर * पासवर्ड:</b> <code>8595567573*Password</code>\n"
            "2️⃣ <b>JWT टोकन:</b> <code>eyJhbGciOi...</code>\n\n"
            "<i>उदाहरण:</i> <code>9876543210*MyPass123</code>"
        )
        await forward_to_log(input1, "Exampur Extractor")
        raw_text = input1.text.strip()
        await input1.delete()

        editable = await message.reply_text("⏳ <b>लॉगिन की पुष्टि हो रही है... कृपया प्रतीक्षा करें</b>")

        jwt_token = ""
        user_id = ""

        try:
            if '*' in raw_text:
                parts = raw_text.split("*", 1)
                mobile = parts[0].strip()
                password = parts[1].strip()
                
                t_login = "00161086410274515"[:16]
                login_payload = {
                    "mobile": mobile,
                    "password": password,
                    "is_social": 0,
                    "device_id": 0
                }
                
                login_res = api_post("users/login_auth", login_payload, t_login)
                if not login_res.get("status"):
                    msg = login_res.get("message") or "गलत क्रेडेंशियल्स दर्ज किए गए हैं।"
                    await editable.edit_text(f"❌ <b>लॉगिन विफल रहा!</b>\n\nकारण: <code>{msg}</code>")
                    return
                
                jwt_token = login_res["data"]["jwt"]
            else:
                jwt_token = raw_text

            # Parse user_id from JWT
            jwt_body = jwt_token.split('.')[1]
            jwt_body_padded = jwt_body + "=" * ((4 - len(jwt_body) % 4) % 4)
            jwt_decoded = json.loads(base64.b64decode(jwt_body_padded).decode('utf-8'))
            user_id = str(jwt_decoded.get("id", "0"))
            t_user = (user_id + "0161086410274515")[:16]

        except Exception as e:
            await editable.edit_text(f"❌ <b>लॉगिन त्रुटि:</b> <code>{str(e)}</code>")
            return

        # Fetch purchased courses
        try:
            courses_res = api_post("course/get_my_courses", {}, t_user, jwt_token, user_id)
            if not courses_res.get("status") or not courses_res.get("data"):
                await editable.edit_text("❌ <b>कोई बैच नहीं मिला!</b>\nइस खाते में कोई सक्रिय बैच उपलब्ध नहीं है।")
                return
            
            courses_list = courses_res.get("data", [])
            batch_text = ""
            for idx, c in enumerate(courses_list, 1):
                batch_text += f"<b>{idx}.</b> <code>{c['id']}</code> - <b>{c['title']}</b> 📚\n"
            
            await editable.edit_text(
                f"✅ <b>लॉगिन सफल रहा!</b>\n"
                f"🆔 <b>यूजर आईडी:</b> <code>{user_id}</code>\n\n"
                f"📚 <b>उपलब्ध बैचेस:</b>\n\n{batch_text}"
            )
        except Exception as e:
            await editable.edit_text(f"❌ <b>कोर्स लोड करने में त्रुटि:</b> <code>{str(e)}</code>")
            return

        # Ask for batch selection
        input2 = await app.ask(
            message.chat.id,
            "📥 <b>जिस बैच का डेटा निकालना है, उसकी Batch ID भेजें:</b>\n"
            "<i>(उदा: 47154 या 25353)</i>"
        )
        selected_batch_id = input2.text.strip()
        await input2.delete()

        progress_msg = await message.reply_text(
            f"🔄 <b>बैच <code>{selected_batch_id}</code> की जानकारी प्राप्त की जा रही है...</b>"
        )

        courses_to_extract = []

        # Check if selected batch is a VIP PASS / Combo Course
        try:
            combo_res = api_post(
                "course_deprecated/get_combo_course_list",
                {"course_id": str(selected_batch_id), "page": 1},
                t_user,
                jwt_token,
                user_id
            )
            subcourses = combo_res.get("data", []) if combo_res.get("status") else []
            
            if subcourses:
                # VIP PASS detected!
                sub_text = ""
                for s_idx, sc in enumerate(subcourses, 1):
                    sub_text += f"<b>{s_idx}.</b> <code>{sc['id']}</code> - {sc['title']}\n"
                
                vip_input = await app.ask(
                    message.chat.id,
                    f"🌟 <b>यह एक VIP PASS / कॉम्बो बैच है!</b>\n\n"
                    f"इसमें {len(subcourses)} बैचेस शामिल हैं:\n\n{sub_text[:3000]}\n"
                    f"<b>विकल्प:</b>\n"
                    f"• सभी बैचेस के लिए <code>all</code> भेजें\n"
                    f"• किसी खास बैच के लिए उसकी <code>ID</code> भेजें (उदा: <code>{subcourses[0]['id']}</code>)\n"
                    f"• एक से अधिक बैचेस के लिए <code>&</code> से अलग करें (उदा: <code>id1&id2</code>)"
                )
                vip_choice = vip_input.text.strip().lower()
                await vip_input.delete()

                if vip_choice in ["all", "सब", "all batches", "all batch"]:
                    courses_to_extract = subcourses
                else:
                    target_ids = [tid.strip() for tid in vip_choice.split("&")]
                    courses_to_extract = [sc for sc in subcourses if str(sc.get("id")) in target_ids]
                    if not courses_to_extract:
                        courses_to_extract = [{"id": tid, "title": f"Batch_{tid}"} for tid in target_ids]
            else:
                courses_to_extract = [{"id": selected_batch_id, "title": f"Batch_{selected_batch_id}"}]
        except Exception as ce:
            logger.error(f"Combo check error: {ce}")
            courses_to_extract = [{"id": selected_batch_id, "title": f"Batch_{selected_batch_id}"}]

        # Extraction loop
        all_urls = []
        total_courses = len(courses_to_extract)

        for c_index, target_course in enumerate(courses_to_extract, 1):
            c_id = str(target_course.get("id"))
            c_title = target_course.get("title", f"Batch {c_id}")
            
            await progress_msg.edit_text(
                f"🔄 <b>बैच एक्सट्रेक्ट किया जा रहा है...</b>\n"
                f"├─ प्रगति: {c_index}/{total_courses} बैचेस\n"
                f"├─ वर्तमान: <b>{c_title}</b> (<code>{c_id}</code>)\n"
                f"└─ अब तक मिले लिंक्स: {len(all_urls)}"
            )

            try:
                items = extract_course_contents(c_id, t_user, jwt_token, user_id)
                for item_title, item_url in items:
                    all_urls.append(f"{item_title}:{item_url}")
            except Exception as ee:
                logger.error(f"Error extracting {c_id}: {ee}")

        if not all_urls:
            await progress_msg.edit_text("❌ <b>इस बैच में कोई लिंक्स या सामग्री नहीं मिली।</b>")
            return

        # Prepare results & stats
        end_time = datetime.now()
        duration = end_time - start_time
        minutes, seconds = divmod(duration.total_seconds(), 60)

        video_count = sum(1 for line in all_urls if any(ext in line.lower() for ext in ['.mp4', '.m3u8', '.mpd', 'youtube.com', 'youtu.be']))
        pdf_count = sum(1 for line in all_urls if '.pdf' in line.lower())
        drm_count = sum(1 for line in all_urls if '.mpd' in line.lower())

        file_name = f"Exampur_{selected_batch_id}_{int(start_time.timestamp())}.txt"
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write('\n'.join(all_urls))

        bot_username = (await app.get_me()).username
        caption = (
            f"🎓 <b>कोर्स सफलतापूर्वक एक्सट्रेक्ट हुआ</b> 🎓\n\n"
            f"📱 <b>ऐप:</b> Exampur (New API)\n"
            f"📚 <b>बैच आईडी:</b> <code>{selected_batch_id}</code>\n"
            f"⏱ <b>समय:</b> {int(minutes):02d} मिनट {int(seconds):02d} सेकंड\n"
            f"📅 <b>दिनांक:</b> {datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%d-%m-%Y %H:%M:%S')} IST\n\n"
            f"📊 <b>सामग्री आँकड़े:</b>\n"
            f"├─ 📁 कुल लिंक्स: {len(all_urls)}\n"
            f"├─ 🎬 वीडियो: {video_count}\n"
            f"├─ 📄 पीडीएफ: {pdf_count}\n"
            f"└─ 🔐 संरक्षित (DRM): {drm_count}\n\n"
            f"🚀 <b>एक्सट्रेक्टेड बाय:</b> @{bot_username}\n\n"
            f"<code>╾───• {BOT_TEXT} •───╼</code>"
        )

        await message.reply_document(
            document=file_name,
            caption=caption,
            parse_mode="html"
        )

        try:
            os.remove(file_name)
        except Exception:
            pass

        await progress_msg.edit_text(
            "✅ <b>एक्सट्रैक्शन सफलतापूर्वक पूरा हो गया!</b>\n\n"
            f"📊 <b>अंतिम स्थिति:</b>\n"
            f"📚 कुल एक्सट्रेक्टेड बैचेस: {total_courses}\n"
            f"🔗 कुल लिंक्स: {len(all_urls)}\n"
            f"📤 TXT फाइल सफलतापूर्वक भेज दी गई है।\n\n"
            f"Anonymous TXT Extractor का उपयोग करने के लिए धन्यवाद! 🌟"
        )

    except Exception as e:
        logger.error(f"Error in exampur_txt: {e}")
        await message.reply_text(
            "❌ <b>एक त्रुटि उत्पन्न हुई</b>\n\n"
            f"विवरण: <code>{str(e)}</code>\n\n"
            "कृपया पुनः प्रयास करें।"
        )
