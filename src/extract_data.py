import requests
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# function to extract token session
def extract_token(endpoint_db:str, login:str, password:str):
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

# customers table
def bronze_customers (token:str, operation_name:str, endpoint_db:str):
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