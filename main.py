import numpy as np
import re
import datetime
import os
import json


def validate_datetime(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD HH:mm:ss")
    return date_text


def validate_payment(pay, fee):
    if pay >= fee:
        print("Thanks for your choice\n")
        return pay
    else:
        raise ValueError("Your payment amount must greater or equal the fee!")


def validate_identity(identity):
    x = re.findall("\d{2}[a-zA-Z]-\d{5}$", identity)
    if x:
        return identity
    else:
        raise ValueError("Incorrect data format, should be format like this 59C-12345")


def park_choice():
    car_identity = validate_identity(input('Car identity: '))
    is_exist = find_file('carpark', car_identity)
    if is_exist:
        print('Your car was parked here')
        print()
        return
    else:
        date_text = validate_datetime(input('Arrival time: '))
        output_file = open(os.path.join('carpark', car_identity), "w")
        output_file.write(date_text)
        output_file.close()
        print("We have recorded your parking information")
        print("===========================")


def find_file(path, name):
    return os.path.exists(os.path.join(path, name))


def convert_to_dist(lst):
    res_dct = {lst[i]: lst[i + 1] for i in range(0, len(lst), 2)}
    return res_dct


def payment_bill(fee, discount):
    total_fee = np.round_(np.float32(fee - fee * discount), decimals=2)
    print("========= PAYMENT =========")
    print("Your parking fee: ", np.round_(fee, decimals=2))
    print('Discount: {}%'.format(np.float32(discount * 100)))
    print("Total: ", total_fee)
    print("===========================")
    return np.float32(total_fee)


def load_parking_fee(date_text):
    with open('parking_fee.json') as json_file:
        day_of_week_text = datetime.datetime.strptime(date_text, '%Y-%m-%d %H:%M:%S').strftime('%A')
        park_time_text = datetime.datetime.strptime(date_text, '%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S')
        park_time_split = park_time_text.split(':')

        def convert_list_string_to_int(list_convert):
            map_object = map(int, list_convert)
            return list(map_object)

        park_time_list = convert_list_string_to_int(park_time_split)
        session_of_day = None
        if 0 <= park_time_list[0] <= 7:
            session_of_day = "Night"
        elif 8 <= park_time_list[0] <= 16:
            session_of_day = "Morning"
        elif 17 <= park_time_list[0] <= 23:
            session_of_day = "Evening"

        input_data = json.load(json_file)
        data = input_data['data']
        day_fee_text = next((item for item in data if item["dayOfWeek"] == day_of_week_text), None)
        session_of_date = day_fee_text['priceParking']
        session_fee_data = next((item for item in session_of_date if item["sessionOfDay"] == session_of_day), None)

        def get_sec(time_str):
            """Get seconds from time."""
            h, m, s = time_str.split(':')
            return int(h) * 3600 + int(m) * 60 + int(s)

        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        current_time_in_second = get_sec(current_time)
        park_time_in_second = get_sec(park_time_text)
        parked_time_in_second = abs(int(current_time_in_second) - int(park_time_in_second))

        def convert_second_to_hour(seconds_input):
            return seconds_input / 3600

        time_parked = convert_second_to_hour(parked_time_in_second)
        extend_stay = int(session_fee_data["maxStayInHour"]) - time_parked
        if session_of_day != "Night":
            fee = np.float32(time_parked * int(session_fee_data["maxStayInHour"]))
            if extend_stay < 0:
                fee += np.float32(abs(extend_stay) * int(session_fee_data["maxStayInHour"]) * 2)
        else:
            fee = 20.00
        if session_of_day != "Evening":
            discount = np.float32(0.1)
        else:
            discount = np.float32(0.5)
        return payment_bill(fee, discount), current_time


def write_history(car_identity, fee, payment, park_date, time_payment):
    file_name = car_identity + '.txt'
    is_exist = find_file('history', file_name)
    remain_credit = (np.round_(np.float32(payment - fee), decimals=2))
    dateout = park_date + ' - ' + time_payment
    if is_exist:
        with open(os.path.join('history', file_name), 'r') as json_file:
            dict_temp = json.load(json_file)
            dict_temp['Total payment'] += str(fee)
            dict_temp['Available credits'] = str(np.float32(dict_temp['Available credits']) + remain_credit)
            dict_temp['Parked Dates'].append(dateout)
            with open(os.path.join('history', file_name), 'w') as output_file:
                output_file.write(json.dumps(dict_temp))
    else:
        dict_temp = {
            "Total payment": str(fee),
            "Available credits": str(remain_credit),
            "Parked Dates": [dateout]
        }
        with open(os.path.join('history', car_identity + '.txt'), 'w') as output_file:
            output_file.write(json.dumps(dict_temp))


def pickup_choice():
    car_identity = validate_identity(input('Car identity: '))
    is_exist = find_file('carpark', car_identity)
    if is_exist:
        input_file = open(os.path.join('carpark', car_identity), "r")
        date_text = input_file.read()
        fee, time_payment = load_parking_fee(date_text)
        pay_fee = validate_payment(int(input("Payment money: ")), fee)
        write_history(car_identity, fee, pay_fee, date_text, time_payment)
        os.remove(os.path.join('carpark', car_identity))
    else:
        raise FileNotFoundError("Your car is not park here!")


def history_choice():
    car_identity = validate_identity(input('Car identity: '))
    file_name = car_identity + '.txt'
    is_exist = find_file('history', file_name)
    if is_exist:
        with open(os.path.join('history', file_name), 'r') as json_file:
            dict_temp = json.load(json_file)
            print("========= HISTORY =========")
            print('Total Payment: ', dict_temp['Total payment'])
            print('Available credits: ', dict_temp['Available credits'])
            print('Parked Dates:\n', '\n '.join(dict_temp['Parked Dates']))
            print("===========================")


def menu_option():
    while True:
        print('Hello, Please select option below:')
        print('1. PARK')
        print('2. PICKUP')
        print('3. HISTORY')
        print('0. EXIT')
        try:
            choice = int(input('Your choice is: '))
        except ValueError:
            raise ValueError("Incorrect data format, should be Integer")
        if choice == 0:
            break
        elif choice == 1:
            park_choice()
        elif choice == 2:
            pickup_choice()
        elif choice == 3:
            history_choice()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    menu_option()
