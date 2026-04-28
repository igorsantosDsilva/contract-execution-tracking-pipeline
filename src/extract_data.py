import requests
import logging

# Configure logging format and level
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        response_json = response.json().get('data', {})
        
        if 'errors' in response_json:
            logging.error(f"Error GraphQL: {response_json['errors']}")
            return None
        
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
        response_json = response.json().get('data', {})
        
        if 'errors' in response_json:
            logging.error(f'Error GraphQL: {response_json["errors"]}')
            return None

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
        "operationName": operation_name,
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
        response_json = response.json().get('data', {})
        
        if 'errors' in response_json:
            logging.error(f'Error GraphQL: {response_json["errors"]}')
            return None
        
        logging.info(f'Bronze orders table successfully extracted')
        return response_json
    
    except requests.exceptions.RequestException as e:
        logging.error(f'Error in request: {e}')
        return None
    
