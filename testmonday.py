API_KEY = 'eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjU1NDA3NDAxNywiYWFpIjoxMSwidWlkIjo3NDgwODgyOCwiaWFkIjoiMjAyNS0wOC0yNVQxNDoyMTo1MS4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6OTExMTQ5MCwicmduIjoidXNlMSJ9.thTm9sSH1hy_a5MPKa6BDhAbTGqDxbtMz71w3cwtqSI'
import requests
import datetime
import json

API_URL = "https://api.monday.com/v2"

headers = {
    "Authorization": API_KEY,
    "Content-Type": "application/json"
}

def create_item(board_id, item_name, column_values):
    # create item, returns id
    create_query = '''
    mutation ($board_id: ID!, $item_name: String!, $column_values: JSON!) {
      create_item (
        board_id: $board_id,
        item_name: $item_name,
        column_values: $column_values
      ) {
        id
        name
        column_values {
          id
          text
          value
        }
      }
    }
    '''

    create_variables = {
        "board_id": str(board_id),
        "item_name": item_name,
        "column_values": json.dumps(column_values)
    }

    response = requests.post(API_URL, json={"query": create_query, "variables": create_variables}, headers=headers)
    result = response.json()

    if 'errors' in result:
        print("Error creating item:", result['errors'])
        return None

    item_id = result['data']['create_item']['id']
    print(f"Item created with ID: {item_id}")
    return item_id

def update_item_status(board_id, item_id, status_column_id, status_label_id):
    # update status
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
        column_values {
          id
          text
        }
      }
    }
    '''

    status_variables = {
        "board_id": str(board_id),
        "item_id": str(item_id),
        "column_id": status_column_id,
        "value": json.dumps({"label": str(status_label_id)})
    }

    response = requests.post(API_URL, json={"query": status_query, "variables": status_variables}, headers=headers)
    result = response.json()

    if 'errors' in result:
        print("Error updating status:", result['errors'])
        return False

    print("Status updated successfully")
    return True



item_name = "Ejemplo"
status = 'Done'

column_values = {
    "persona_column_id": "Ivanovich Chiu",
    "status": status,
    "motivo_column_id": "OK"
}

board_id = 9891069732
status_column_id = "color_mkv58fw5"
status_label_id = "Stuck"

item_id = create_item(board_id, item_name, column_values)


if item_id:
    update_item_status(board_id, item_id, status_column_id, status_label_id)