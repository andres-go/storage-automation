import requests
import datetime
import json

API_URL = "https://api.monday.com/v2"

headers = {
    "Authorization": "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjU1NDA3NDAxNywiYWFpIjoxMSwidWlkIjo3NDgwODgyOCwiaWFkIjoiMjAyNS0wOC0yNVQxNDoyMTo1MS4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6OTExMTQ5MCwicmduIjoidXNlMSJ9.thTm9sSH1hy_a5MPKa6BDhAbTGqDxbtMz71w3cwtqSI",
    "Content-Type": "application/json"
}


# --- CONFIGURACIÓN GLOBAL DE COLUMNAS Y BOARDS ---
INVENTORY_BOARD_ID = "9233233911"
CHECKED_BOARD_ID = "9900506946"
UID_COLUMN_ID = "text_mkrabj2m"
SERIAL_COLUMN_ID = "text_mkrabj2m"
PART_COLUMN_ID = "text_mkra6xgc"
STATUS_COLUMN_ID = "color_mkrdamvf"
CHECKED_BOARD_COLUMN_MAPPING = {
    'serial': 'text_mkv6yqsc',
    'part': 'text_mkv6k92e',
    'person': 'text_mkv5g3a2',
    'motive': 'text_mkv632ex'
}

#query board based on qrcode, for serial, part and status
#check status = !checked, continue

#modify INVENTORY board status = checked

#object register
  #insert serial, part, person, motive

#modify checked board with object


class Register:

    def __init__(self, uid=None, serial=None, part=None, person=None, motive=None, status=None):
        self._uid = uid
        self._serial = serial
        self._part = part
        self._person = person
        self._motive = motive
        self._status = status
    

    # Traditional getters and setters
    def get_uid(self):
        return self._uid

    def set_uid(self, value):
        self._uid = value

    def get_serial(self):
        return self._serial

    def set_serial(self, value):
        self._serial = value

    def get_part(self):
        return self._part

    def set_part(self, value):
        self._part = value

    def get_person(self):
        return self._person

    def set_person(self, value):
        self._person = value

    def get_motive(self):
        return self._motive

    def set_motive(self, value):
        self._motive = value

    def get_status(self):
        return self._status

    def set_status(self, value):
        self._status = value
    
    def __str__(self):
        return f"ObjectRegister(uid={self._uid}, serial={self._serial}, part={self._part}, person={self._person}, motive={self._motive}, status={self._status})"

def query_inventory_board_by_uid(board_id, uid_column_id, uid_value):
    """
    Query board based on qrcode, for serial, part and status
    Uses items_page_by_column_values for efficient filtering
    """
    query = '''
    query ($board_id: ID!, $column_id: String!, $column_value: String!) {
      items_page_by_column_values (
        board_id: $board_id,
        columns: [
          {
            column_id: $column_id,
            column_values: [$column_value]
          }
        ]
      ) {
        items {
          id
          name
          column_values {
            id
            text
            value
          }
        }
      }
    }
    '''

    variables = {
        "board_id": str(board_id),
        "column_id": uid_column_id,
        "column_value": str(uid_value)
    }

    response = requests.post(API_URL, json={"query": query, "variables": variables}, headers=headers)
    result = response.json()
    
    # # Debug: Print the full API response
    # print("API Response:")
    # print(json.dumps(result, indent=2))
    # print("-" * 30)
    
    if 'errors' in result:
        print("Error querying inventory board:", result['errors'])
        return None
    
    # Check if any items were found
    items = result['data']['items_page_by_column_values']['items']
    if not items:
        print(f"No item found with UID: {uid_value}")
        return None
    
    # Return the first matching item
    item = items[0]
    return {
        'item_id': item['id'],
        'item_name': item['name'],
        'column_values': item['column_values']
    }

def query_inventory_board_by_uid_fallback(board_id, uid_column_id, uid_value):
    """
    Fallback method using boards query if items_page_by_column_values doesn't work
    """
    query = '''
    query ($board_id: ID!, $limit: Int!) {
    boards (ids: [$board_id]) {
        items (limit: $limit) {
        id
        name
        column_values {
            id
            text
            value
        }
        }
    }
    }
    '''

    variables = {
        "board_id": str(board_id),
        "limit": 500
    }

    response = requests.post(API_URL, json={"query": query, "variables": variables}, headers=headers)
    result = response.json()
    
    # Debug: Print the full API response
    print("API Response (Fallback):")
    print(json.dumps(result, indent=2))
    print("-" * 30)
    
    if 'errors' in result:
        print("Error querying inventory board:", result['errors'])
        return None
    
    # Find item with matching UID
    for board in result['data']['boards']:
        for item in board['items']:
            for column in item['column_values']:
                if column['id'] == uid_column_id and column['text'] == str(uid_value):
                    return {
                        'item_id': item['id'],
                        'item_name': item['name'],
                        'column_values': item['column_values']
                    }
    
    print(f"No item found with UID: {uid_value}")
    return None

def get_item_status_by_uid(board_id, uid_column_id, uid_value, status_column_id):
    """
    Query board for a specific UID and return just the Status value
    Returns status text if found, None if not found
    """
    item_data = query_inventory_board_by_uid(board_id, uid_column_id, uid_value)
    if not item_data:
        return None
    
    # Find and return the status value
    for column in item_data['column_values']:
        if column['id'] == status_column_id:
            return column['text']
    
    print(f"Status column not found for item with UID: {uid_value}")
    return None

def extract_item_data(item_data, serial_column_id, part_column_id, status_column_id):
    """
    Extract serial, part, and status from item data
    Returns Register with extracted data
    """
    obj_register = Register()

    for column in item_data['column_values']:
        if column['id'] == serial_column_id:
            obj_register.set_serial(column['text'])
        elif column['id'] == part_column_id:
            obj_register.set_part(column['text'])
        elif column['id'] == status_column_id:
            obj_register.set_status(column['text'])

    return obj_register

def check_status_not_checked_out(status_text):

    return status_text != "Checked Out"

def update_item_status(board_id, item_id, status_column_id, checked_status_text="Checked Out"):

    status_query = '''
    mutation ($board_id: ID!, $item_id: ID!, $column_id: String!, $value: JSON!) {
      change_column_value (
        board_id: $board_id,
        item_id: $item_id,
        column_id: $column_id,
        value: $value
      ) {
        id
        name
      }
    }
    '''
    
    status_variables = {
        "board_id": str(board_id),
        "item_id": str(item_id),
        "column_id": status_column_id,
        "value": json.dumps({"label": checked_status_text})
    }
    
    response = requests.post(API_URL, json={"query": status_query, "variables": status_variables}, headers=headers)
    result = response.json()
    
    if 'errors' in result:
        print("Error updating status:", result['errors'])
        return False

    print("inventory board status updated to 'Checked Out'")
    return True

def create_item_checked_board(board_id, obj_register, column_mapping, person_override=None, motive_override=None):
    """
    column_mapping should be a dict like:
    {
        'serial': 'serial_column_id',
        'part': 'part_column_id', 
        'person': 'person_column_id',
        'motive': 'motive_column_id'
    }
    """
    column_values = {}
    
    if obj_register._serial and 'serial' in column_mapping:
        column_values[column_mapping['serial']] = obj_register._serial
    if obj_register._part and 'part' in column_mapping:
        column_values[column_mapping['part']] = obj_register._part
    if 'person' in column_mapping:
        if person_override is not None:
            column_values[column_mapping['person']] = person_override
        elif obj_register._person:
            column_values[column_mapping['person']] = obj_register._person
    if 'motive' in column_mapping:
        if motive_override is not None:
            column_values[column_mapping['motive']] = motive_override
        elif obj_register._motive:
            column_values[column_mapping['motive']] = obj_register._motive

    create_query = '''
    mutation ($board_id: ID!, $item_name: String!, $column_values: JSON!) {
      create_item (
        board_id: $board_id,
        item_name: $item_name,
        column_values: $column_values
      ) {
        id
        name
      }
    }
    '''

    item_name = f"{obj_register._part} - {obj_register._person}" if obj_register._part and obj_register._person else "New Entry"

    create_variables = {
        "board_id": str(board_id),
        "item_name": item_name,
        "column_values": json.dumps(column_values)
    }
    
    response = requests.post(API_URL, json={"query": create_query, "variables": create_variables}, headers=headers)
    result = response.json()
    
    if 'errors' in result:
        print("Error creating item in checked board:", result['errors'])
        return None
    
    item_id = result['data']['create_item']['id']
    print(f"Item created in checked board with ID: {item_id}")
    return item_id

def process_checkout(inventory_board_id, checked_board_id, uid_value, person, motive, 
                    uid_column_id, serial_column_id, part_column_id, status_column_id,
                    checked_board_column_mapping):
    print(f"Starting checkout process for UID: {uid_value}")
    
    item_data = query_inventory_board_by_uid(inventory_board_id, uid_column_id, uid_value)
    
    if not item_data:
        print("Trying fallback query method...")
        item_data = query_inventory_board_by_uid_fallback(inventory_board_id, uid_column_id, uid_value)
    
    if not item_data:
        return False
    
    obj_register = extract_item_data(item_data, serial_column_id, part_column_id, status_column_id)
    obj_register.set_uid(uid_value)
    obj_register.set_person(person)
    obj_register.set_motive(motive)
    
    print(f"Found item: {obj_register}")
    
    if not check_status_not_checked_out(obj_register.get_status()):
        print(f"Item is already Checked Out (status: {obj_register.get_status()})")
        return False

    if not update_item_status(inventory_board_id, item_data['item_id'], status_column_id):
        return False
    
    checked_board_item_id = create_item_checked_board(checked_board_id, obj_register, checked_board_column_mapping, person_override=person, motive_override=motive)
    
    if checked_board_item_id:
        print("Checkout process completed successfully!")
        return True
    else:
        print("Failed to create item in checked board")
        return False

if __name__ == "__main__":
    INVENTORY_BOARD_ID = "9233233911" 
    
    # Column IDs for inventory board
    UID_COLUMN_ID = "text_mkrabj2m"
    SERIAL_COLUMN_ID = "text_mkrabj2m"
    PART_COLUMN_ID = "text_mkra6xgc"
    STATUS_COLUMN_ID = "color_mkrdamvf"
    
    # Test values (ya no se usan en producción, solo para pruebas manuales)
    test_uid = "121800074"
    test_person = "ivanovich"
    test_motive = "Demo"
    
    print(f"Testing inventory board query and object creation for UID: {test_uid}")
    print("=" * 50)
    
    print("Step 1: Querying inventory board...")
    item_data = query_inventory_board_by_uid(INVENTORY_BOARD_ID, UID_COLUMN_ID, test_uid)
    
    if not item_data:
        print("Trying fallback query method...")
        item_data = query_inventory_board_by_uid_fallback(INVENTORY_BOARD_ID, UID_COLUMN_ID, test_uid)
    
    if not item_data:
        print("No item found with that UID")
    else:
        print("Item found!")
        print(f"Item ID: {item_data['item_id']}")
        print(f"Item Name: {item_data['item_name']}")

        print("\nStep 2: Creating Register object...")
        obj_register = extract_item_data(item_data, SERIAL_COLUMN_ID, PART_COLUMN_ID, STATUS_COLUMN_ID)
        obj_register.set_uid(test_uid)
        obj_register.set_person(test_person)
        obj_register.set_motive(test_motive)

        print("Register object created successfully!")
        print(f"Register object: {obj_register}")

        print(f"\nStep 3: Checking status...")
        print(f"Current status: '{obj_register.get_status()}'")
        can_checkout = check_status_not_checked_out(obj_register.get_status())
        if can_checkout:
            print("Item can be Checked Out (status is not 'Checked Out')")

            print("\nStep 4: Changing status to 'Checked Out' in Inventory board...")
            updated = update_item_status(INVENTORY_BOARD_ID, item_data['item_id'], STATUS_COLUMN_ID)
            if updated:
                print("Status updated to 'Checked Out' successfully!")

                print("\nStep 5: Adding data to checked board...")
                CHECKED_BOARD_ID = "9900506946"
                CHECKED_BOARD_COLUMN_MAPPING = {
                    'serial': 'text_mkv6yqsc', 
                    'part': 'text_mkv6k92e',
                    'person': 'text_mkv5g3a2',
                    'motive': 'text_mkv632ex'
                }
                checked_board_item_id = create_item_checked_board(CHECKED_BOARD_ID, obj_register, CHECKED_BOARD_COLUMN_MAPPING)
                if checked_board_item_id:
                    print(f"Item added to checked board with ID: {checked_board_item_id}")
                else:
                    print("Failed to add item to checked board.")
            else:
                print("Failed to update status.")
        else:
            print("Item cannot be Checked Out (status is 'checked')")

        # Step 5: Test status-only query
        print(f"\nStep 5: Testing status-only query...")
        status_only = get_item_status_by_uid(INVENTORY_BOARD_ID, UID_COLUMN_ID, test_uid, STATUS_COLUMN_ID)
        print(f"Status from dedicated function: '{status_only}'")

        print("\n" + "=" * 50)
        print("Test completed!")