import requests
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_token(endpoint_db:str, login:str, password:str):
    headers = {
        'content-type': 'application/json',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36',
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