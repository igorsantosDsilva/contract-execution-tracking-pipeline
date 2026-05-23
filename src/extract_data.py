import requests
import logging
import json

from pathlib import Path

# Configure logging format and level
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def save_data(file_name, json_data):
    output_path = "data/"+ file_name + ".json"
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
     
    with open(output_path, 'w') as f:
        json.dump(json_data, f, indent=4)
          
    logging.info(f"Data saved to {output_path}")
     
def extract_token(endpoint_db:str, login:str, password:str):
    """
        Authenticate user and retrieve access token for subsequent requests.
        
        Args: 
            endpoint_db (str): GraphQL endpoint URL for authentication.
            login (str): User login name.
            password (str): User password.
        Returns:
            str: Access token if authentication is successful, None otherwise.
    """
    headers = {
        'content-type': 'application/json'
    }

    json_data = {
        'operationName': 'LoginMutation',
        'variables': {
            'input': {
                'username': login,
                'password': password,
            },
        },
        
        'query': '''
        mutation LoginMutation($input: LoginInput!) {
            login(input: $input) {
                access_token
            }
        }
    '''
    }
    try:
        response = requests.post(
            endpoint_db, 
            headers=headers, 
            json=json_data,
            timeout=5
            )
        response.raise_for_status()
        response_json = response.json()
        
        if 'errors' in response_json:
            logging.error(f'Error: {response_json['errors']}')
            return None
        
        token = response_json.get('data', {}).get('login', {}).get('access_token')  
        
        if not token:
            logging.warning('Token not found')
            return None

        logging.info('Token extracted successfully')
        return token
    
    except requests.exceptions.RequestException as e:
        logging.error(f'Error in request: {e}')
        return None

def bronze_customers (token:str, operation_name:str, endpoint_db:str):
    """
       Extract raw customers data from API into bronze layer
       
       Args: 
              token (str): Access token for authentication.
              operation_name (str): Name of the GraphQL operation to execute.
              endpoint_db (str): GraphQL endpoint URL for data extraction.
        Returns:
              dict: Extracted customers data if successful, None otherwise.
    """
    headers = {
        'content-type': 'application/json',
        'authorization': f'Bearer {token}',
    }
        
    json_data = {
        'query': f'''
        query {operation_name} {{
            clients {{
               id
               name
               initials
               alias
               email
               logo 
            }}
        }}
        '''          
    }
    
    try:
        response = requests.post(
            endpoint_db,
            headers= headers,
            json= json_data,
            timeout=10
        )
        
        response.raise_for_status()
        response_json = response.json()
        
        if 'errors' in response_json:
            logging.error(f"Error GraphQL: {response_json['errors']}")
            return None
        
        response_json = response_json.get('data', {})
        save_data("customers", response_json)
        
        logging.info('Bronze customers table successfuly extracted')
        return response_json
    
    except requests.exceptions.RequestException as e:
        logging.error(f'Error in request: {e}')
        return None
    
def bronze_providers(token:str, operation_name:str, endpoint_db:str):
    """
        Extract raw providers data from API into bronze layer
        Args: 
              token (str): Access token for authentication.
              operation_name (str): Name of the GraphQL operation to execute.
              endpoint_db (str): GraphQL endpoint URL for data extraction.
        Returns:
              dict: Extracted providers data if successful, None otherwise.
    """
    headers = {
        'content-type': 'application/json',
        'authorization': f'Bearer {token}'
    }
    
    json_data ={
    "query": f"""
    query {operation_name} {{
        providers {{
            client {{
                id
                name
                __typename
            }}
            id
            taxid
            name
            fantasy
            phone
            email
            cell_phone
            dap_number
            contact
            responsible
            street
            number
            district
            complement
            state
            zipcode
            city
            dap_number
            __typename
        }}
    }}
    """
    }
    
    try:
        response = requests.post(
            endpoint_db,
            headers=headers,
            json=json_data, 
            timeout=10
        )
        
        response.raise_for_status()
        response_json = response.json()
        
        if 'errors' in response_json:
            logging.error(f'Error GraphQL: {response_json["errors"]}')
            return None
        
        response_json = response_json.get('data', {})
        save_data("providers", response_json)
        
        logging.info(f'Bronze providers table successfully extracted')
        return response_json
    
    except requests.exceptions.RequestException as e:
        logging.error(f'Error in request: {e}')
        return None
    
def bronze_orders(token:str, operation_name:str, endpoint_db:str):
    """
        Extract raw orders data from API into bronze layer
        Args: 
              token (str): Access token for authentication.
              operation_name (str): Name of the GraphQL operation to execute.
              endpoint_db (str): GraphQL endpoint URL for data extraction.
        Returns:
              dict: Extracted orders data if successful, None otherwise.
    """
    headers = {
        'content-type': 'application/json',
        'authorization': f'Bearer {token}'
    }

    json_data = {
        "variables": {
            "year": None
        },
        "query": f"""
        query {operation_name} ($year: Int) {{
            ordersQuery(year: $year) {{
                id
                number
                year
                document_label
                order_date
                total_amount_items
                term_id
                document
                type
                provider
                entity
                entity_id
                entity_initials
                user
                modality
                issuer
                blocked_period
                source
                status
                __typename
            }}
        }}
        """
    }
    try:
        response = requests.post(
            endpoint_db,
            headers=headers,
            json=json_data, 
            timeout=10
        )
        
        response.raise_for_status()
        response_json = response.json()
        
        if 'errors' in response_json:
            logging.error(f'Error GraphQL: {response_json["errors"]}')
            return None
        
        response_json = response_json.get('data', {})
        save_data("orders", response_json)
        
        logging.info(f'Bronze orders table successfully extracted')
        return response_json
    
    except requests.exceptions.RequestException as e:
        logging.error(f'Error in request: {e}')
        return None

def bronze_items (token:str, operation_name:str, endpoint_db:str):
    """
        Extract raw items data from API into bronze layer
        Args: 
              token (str): Access token for authentication.
              operation_name (str): Name of the GraphQL operation to execute.
              endpoint_db (str): GraphQL endpoint URL for data extraction.
        Returns:
              dict: Extracted items data if successful, None otherwise.
    """
    headers = {
        'content-type': 'application/json',
        'authorization': f'Bearer {token}'
    }

    json_data = {
        'query': f'''
        query {operation_name} {{
            all_items {{
                id
                quantity  
                quantity_item   
                quantity_unit_item  
                unit_price
                amount
                number
                brand
                unit_measure
                details
                percentage
                fractioned
                estimated_value
                decrease
                type
                utilized_amount
                balance
                query_provider
                document_number
                document_object
                identification
                __typename
            }}
        }}
        '''          
    }
    try:
        response = requests.post(
            endpoint_db, 
            headers=headers, 
            json=json_data, 
            timeout=10
        )
        
        response.raise_for_status()
        response_json = response.json()
        
        if 'errors' in response_json:
            logging.error(f'Error GraphQL: {response_json['errors']}')
            return None
        
        response_json = response_json.get('data', {})
        save_data("items", response_json)
        
        logging.info('Bronze items table successfully extracted')
        return response_json
    
    except requests.exceptions.RequestException as e:
        logging.error(f'Error in request: {e}')
        return None
    
def bronze_doc_providers(token: str, operation_name:str, endpoint_db:str):
    """
        Extract raw doc_providers data from API into bronze layer
        Args: 
              token (str): Access token for authentication.
              operation_name (str): Name of the GraphQL operation to execute.
              endpoint_db (str): GraphQL endpoint URL for data extraction.
        Returns:
              dict: Extracted doc_providers data if successful, None otherwise.
    """
    
    headers = {
        'content-type': 'application/json',
        'authorization': f'Bearer {token}'
    }
    

    json_data = {
        "query": f"""
        query {operation_name}($id: ID, $status: [ID], $type: Int) {{
            {operation_name}(id: $id, status: $status, type: $type) {{
                id
                balance
                balance_used
                balance_used_implantation
                amount
                label
                number_document

                trading {{
                    id
                    description
                    __typename
                }}

                term {{
                    id
                    number
                    year
                    initial
                    final
                    type
                    is_in_the_period

                    status {{
                        id
                        description
                        __typename
                    }}

                    __typename
                }}

                providers {{
                    id
                    name
                    total_items
                    balance_used
                    total_balance
                    balance_used_implantation

                    document_items {{
                        id
                        details
                        unit_price
                        quantity
                        balance
                        amount
                        __typename
                    }}

                    __typename
                }}

                __typename
            }}
            }}
            """
    }
    
    try:
        response = requests.post(
            endpoint_db,
            headers=headers,
            json=json_data, 
            timeout=10
        )
        
        response.raise_for_status()
        response_json = response.json()
        
        if 'errors' in response_json:
            logging.error(f'Error GraphQL: {response_json["errors"]}')
            return None
        
        response_json = response_json.get('data', {})
        save_data("doc_providers", response_json)
        
        logging.info(f'Bronze doc_providers table successfully extracted')
        return response_json
    except requests.exceptions.RequestException as e:
        logging.error(f'Error in request: {e}')
        return None