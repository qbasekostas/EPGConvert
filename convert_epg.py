import os
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
# Χρειαζόμαστε τη βιβλιοθήκη pytz για σωστή διαχείριση ζωνών ώρας
# Το GitHub Action θα την εγκαταστήσει αυτόματα
import pytz

# --- Ρυθμίσεις ---
# Παίρνουμε το URL από τις μεταβλητές περιβάλλοντος του GitHub Action
EPG_URL = os.environ.get("EPG_URL")
# Όνομα του αρχείου που θα αποθηκευτεί
OUTPUT_FILE = "epg_greece.xml"
# Ορίζουμε τη ζώνη ώρας της Ελλάδας
GREECE_TZ = pytz.timezone('Europe/Athens')
# Η τυπική μορφή ώρας στα EPG αρχεία (π.χ. 20231120180000 +0000)
TIME_FORMAT = '%Y%m%d%H%M%S %z'

def convert_epg():
    if not EPG_URL:
        print("!!! Σφάλμα: Το EPG_URL δεν έχει οριστεί.")
        return

    print(f"-> Λήψη EPG από: {EPG_URL}")
    try:
        # Κατεβάζουμε το περιεχόμενο του EPG
        with urllib.request.urlopen(EPG_URL) as response:
            xml_content = response.read()
    except Exception as e:
        print(f"!!! Σφάλμα κατά τη λήψη του EPG: {e}")
        return

    print("-> Επεξεργασία XML...")
    # Δημιουργούμε ένα XML tree από το περιεχόμενο
    root = ET.fromstring(xml_content)
    
    # Βρίσκουμε όλα τα <programme> tags
    programmes_processed = 0
    for programme in root.findall('programme'):
        for time_attr in ['start', 'stop']:
            original_time_str = programme.get(time_attr)
            if original_time_str:
                try:
                    # Μετατρέπουμε το string σε datetime object με πληροφορία ζώνης ώρας
                    original_dt = datetime.strptime(original_time_str, TIME_FORMAT)
                    
                    # Μετατρέπουμε το datetime object στη ζώνη ώρας της Ελλάδας
                    greece_dt = original_dt.astimezone(GREECE_TZ)
                    
                    # Μορφοποιούμε το νέο datetime πίσω σε string για το XML
                    new_time_str = greece_dt.strftime(TIME_FORMAT)
                    
                    # Ενημερώνουμε το attribute στο XML
                    programme.set(time_attr, new_time_str)
                except ValueError:
                    print(f"   - Προειδοποίηση: Δεν ήταν δυνατή η επεξεργασία της ώρας '{original_time_str}'")

        programmes_processed += 1

    print(f"-> Επεξεργάστηκαν {programmes_processed} προγράμματα.")

    # Αποθηκεύουμε το τροποποιημένο XML σε νέο αρχείο
    tree = ET.ElementTree(root)
    # Χρησιμοποιούμε encoding='utf-8' για υποστήριξη ελληνικών χαρακτήρων
    tree.write(OUTPUT_FILE, encoding='utf-8', xml_declaration=True)
    print(f"-> Το EPG αποθηκεύτηκε με επιτυχία στο αρχείο: {OUTPUT_FILE}")

if __name__ == "__main__":
    convert_epg()
