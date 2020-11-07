import requests
import time
import datetime

def get_input(text) :
    verified = False
    while not verified :
        response = input(f"{text}: ")
        verification = input(f"Please confirm: {response}. Y/n? ")
        while verification.lower().replace(' ', '') not in ['y', 'n'] :
            print("Did not understand. Confirmation required.")
            verification = input(f"Please confirm: {response}. Y/n? ")
        if verification.lower().replace(' ', '') == 'y' :
            verified = True
    return(response)

def get_search_data() :
    search_data = {}
    for key in ['postcode', 'latitude', 'longitude', 'account_id', 'email'] :
        search_data[key] = get_input(key)
    return(search_data)

def generate_json(data) :
    today = datetime.datetime.today().date()
    start_date = today.strftime('%Y-%m-%dT%H:%M:%S')
    end_date = (today + datetime.timedelta(days=14)).strftime('%Y-%m-%dT%H:%M:%S')

    json_data = {"requestorigin" : "gi",
                    "data" : {"service_info" : {"fulfillment_type" : "DELIVERY",
                                                "enable_express" : 'false'},
                            "start_date" : start_date,
                            "end_date" : end_date,
                            "reserved_slot_id" : "",
                            "service_address" : {"postcode" : data['postcode'],
                                                    "latitude" : data['latitude'],
                                                    "longitude" : data['longitude']},
                                "customer_info" : {"account_id" : data['account_id']},
                                "order_info" : {"order_id" : "20983571638",
                                                "restricted_item_types" : [],
                                                "volume" : 0,"weight" : 0,
                                                "sub_total_amount" : 0,
                                                "line_item_count" : 0,
                                                "total_quantity" : 0}}}
    
    return(json_data)

def get_asda_data(json) :
    url = 'https://groceries.asda.com/api/v3/slot/view'
    r = requests.post(url, json=json)
    return(r.json())

def get_slot_data(asda_data) :
    slot_data = {}
    for slot_day in asda_data['data']['slot_days'] :
        for slot in slot_day['slots'] :
            slot_time = slot['slot_info']['start_time']
            slot_time = datetime.datetime.strptime(slot_time, '%Y-%m-%dT%H:%M:%SZ')
            slot_status = slot['slot_info']['status']
            slot_data[slot_time.strftime('%H:%M:%S %d-%m-%Y')] = slot_status
    return(slot_data)

data = get_search_data()
json_data = generate_json(data)

while True :
    try :
        asda_data = get_asda_data(json_data)
    except :
        print("Unfortunately the request did not work.")
        continue
    slot_data = get_slot_data(asda_data)

    if set(slot_data.values()) != {'UNAVAILABLE'} :
        print('There is an available slot! See below:')
        available_slots = [time for time, availability in slot_data.items() if availability != 'UNAVAILABLE']
        print(available_slots)
    else :
        print(f'There are currently no available slots.')

    time.sleep(60*0.5)