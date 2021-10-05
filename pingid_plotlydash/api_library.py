import requests
import json
import time
import operator

from starlette.routing import request_response

from env import BACKEND_TOKEN

# backend configuration
backend_url = 'http://localhost:8000/'

# converts path to API URL endpoint
def url(path):
    return backend_url + path

# converts json to dictionary output
def generate_run_output(res_json):
    output = {}
    output['id'] = res_json['id']
    output['name'] = res_json['name']
    output['timestamp'] = res_json['timestamp']

    # split parameters into parameters and parameters_intermediate
    output['parameters'] = res_json['parameters'][0:5]
    output['parameters_intermediate'] = list()
    output['parameters_intermediate'].append(res_json['parameters'][5])

    # split variables into variables, objectives
    output['variables'] = list()
    output['objectives'] = list()
    output['system_state'] = list()
    for variable in res_json['variables']:
        if variable['type'] == 'independent':
            output['variables'].append(variable)
        elif variable['type'] == 'info':
            output['system_state'].append(variable)
        else:
            output['objectives'].append(variable)
    output['variables'].sort(key=operator.itemgetter('column'))
    
    output['info'] = res_json['info']
    output['settings'] = res_json['settings']
    return output

# converts dictionary input to json
def generate_run_input(user_input):
    input = {}
    input['id'] = 0
    input['name'] = user_input['name']
    input['timestamp'] = user_input['timestamp']
    input['parameters'] = user_input['parameters']
    input['parameters'].append(user_input['parameters_intermediate'][0])

    # merge variables, objectives into variables
    input['variables'] = user_input['variables']
    for line in user_input['objectives']:
        input['variables'].append(line)
    for line in user_input['system_state']:
        input['variables'].append(line)

    input['settings'] = user_input['settings']
    input['info'] = user_input['info']
    return input

# write method input to log file
def log_input(input):
    with open('environment/logs/method.input.json', 'w') as f:
        print(json.dumps(input, indent = 2), file=f)

# write method input to log file
def log_output(res_json):
    with open('environment/logs/method.output.json', 'w') as f:
        print(json.dumps(res_json, indent=2), file=f)

# checks for valid response code api call
def response_validility(res):
    if res.status_code == 200:
        res_json = res.json()
        log_output(res_json)

        return generate_run_output(res_json)
    else:
        message = 'An exception occurred with http repsponse code {} and message {}'.format(res.status_code, res.text)
        raise Exception(message)

# calls /app_users/{email}
def get_user_by_email(email: str):
    res = requests.get(url(f'app_users/{email}'), headers={'Authorization': f'Bearer {BACKEND_TOKEN}'})

    # throw exception if user not found
    if res.status_code != 200:
        message = 'An exception occurred with http repsponse code {} and message {}'.format(res.status_code, res.text)
        raise Exception(message)

    return res

# calls API /runs/
def api_runs():
    res = requests.get(url('runs/efficient/'), headers={'Authorization': f'Bearer {BACKEND_TOKEN}'}).json()
    return res

# filters runs columns to display on UI
def api_runs_cols():
    return {'id', 'name', 'timestamp', 'time_created'}

# calls API /runs/{id}
def api_run(id):
    res = requests.get(url(f"runs/{id}"), headers = {'Authorization': f'Bearer {BACKEND_TOKEN}'})
    return response_validility(res)

# calls DELETE API /runs/{id}
def api_run_delete(id):
    res = requests.delete(url(f"runs/{id}/"), headers = {'Authorization': f'Bearer {BACKEND_TOKEN}'})

    # throw exception if deletion went wrong
    if res.status_code != 200:
        message = 'An exception occurred with http repsponse code {} and message {}'.format(res.status_code, res.text)
        raise Exception(message)

# calls API /runs/{timestamp}
def api_timestamp(user_input):
    # generate input
    input = generate_run_input(user_input)
    log_input(input)

    # generate output
    res = requests.get(url('runs/timestamp/'), json=input, headers={'Authorization': f'Bearer {BACKEND_TOKEN}'})
    return response_validility(res)

# calls API algorithm using several api methods
def api_optimizer(user_input):
    # generate input
    input = generate_run_input(user_input)
    log_input(input)

    # submit run for optimization. 
    res = requests.post(url('optimizer/submit'), json=input, headers={'Authorization': f'Bearer {BACKEND_TOKEN}'})

    # retreved status code is 201, which stands for created
    if res.status_code == 201:
        res_job_id = res.json()        
    else:
        message = generate_error_msg(res)
        raise Exception(message)

    # every 5 seconds it is checked whether the run is finished and an error is raised in case something goes wrong. 
    status_pending=True
    start_time=time.time()
    while status_pending:
        if time.time()-start_time > 600: # It is checked that a run doesn't take more than 10 minutes (600 seconds). Otherwise it is canceled. 
            message = 'Run takes more than 10 minutes, which it is not supposed to do so it is canceled.'
            raise Exception(message)  

        res = requests.get(url(f'optimizer/check_status/{res_job_id}'), json=input, headers={'Authorization': f'Bearer {BACKEND_TOKEN}'})  
        if res.json() == 'PENDING':
            time.sleep(5)
        elif res.json() == 'SUCCESS':
            status_pending=False
        else:
            message = generate_error_msg(res)
            raise Exception(message)  

    # run is retrieved in case it was successfull
    res = requests.get(url(f'optimizer/get_result/{res_job_id}'), json=input, headers={'Authorization': f'Bearer {BACKEND_TOKEN}'})
    response = response_validility(res)

    # store the result in the database
    res = requests.post(url(f'runs/create_complete_run'), json=res.json(), headers={'Authorization': f'Bearer {BACKEND_TOKEN}'})
    
    return response

def generate_error_msg(res):
    return f'An exception occurred with http response code: {res.status_code}, message: {res.text} and reason: {res.reason}'
