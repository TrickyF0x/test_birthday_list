import pytest
import requests
import datetime as DT
from datetime import datetime
import calendar

basic_url = "http://129.146.247.102:5000/"
users_list_url = basic_url + "users"
hello_requests_url = basic_url + "hello/"

default_username = "smarthostagelover"
incorrect_username_num = "123456"
incorrect_username_symbols = r"*\&^(%"
incorrect_username_def_with_numbers = "a1b2c3d4e5"
incorrect_username_def_with_symbols = "=_anton_="

default_birthdate = '1977-07-07'
default_birthdate_2012 = '2012-12-30'
incorrect_birthdate_format = '1 january 2013'
incorrect_birthdate_not_exists = '2020-06-52'
incorrect_birthdate_letters = '123456'
incorrect_birthdate_fake_leap_year = '2019-02-29'
incorrect_birthdate_future_date = '2045-11-30'

OK_USER_ADDED = b"New user '" + bytes(default_username, 'utf-8') + b"' was added successfully."
HAPPY_BIRTHDAY = b"Hello, " + bytes(default_username, 'utf-8') + b"! Happy birthday!"
HAPPY_BIRTHDAY_NOT_TODAY_LEAP = b"Hello," + bytes(default_username, 'utf-8') + b"! Your birthday is in 6 day(s)."
HAPPY_BIRTHDAY_NOT_TODAY_DEFAULT = b"Hello," + bytes(default_username, 'utf-8') + b"! Your birthday is in 5 day(s)."
DELETE_SUCCESSFULLY = b"User '" + bytes(default_username, 'utf-8') + b"' was deleted successfully."
ERROR_USERNAME_WRONG_FORMAT = b"Username must be a string containing only letters."
ERROR_USER_ALREADY_EXISTS = b"User already exists. Use 'PUT' method for updating the date of birth."
ERROR_USER_DOES_NOT_EXISTS = b"User with username '" + bytes(default_username, 'utf-8') + b"' does not exist."
ERROR_BIRTHDATE_WRONG_FORMAT = b"JSON field 'dateOfBirth' is missing or value not in 'YYYY-MM-DD' format."
ERROR_BIRTHDATE_WRONG_FORMAT_FUTURE = b"Date of birth must be a date before the today date."


def remove_user(username):
    response = requests.get(users_list_url)
    response_body = response.json()
    for item in response_body['users']:
        if username in item['username']:
            requests.delete(hello_requests_url + default_username)


def create_user(url, username, birthdate):
    return requests.post(url + username,
                         json={"dateOfBirth": birthdate})


def correct_user_created(username, birthdate):
    response = requests.get(users_list_url)
    response_body = response.json()
    for item in response_body['users']:
        if username in item['username']:
            if birthdate in item['dateOfBirth']:
                return True
            else:
                return False
    return False


def user_exists_not_changed_and_alone(username, newdate):
    user_count = 0
    response = requests.get(users_list_url)
    response_body = response.json()
    for item in response_body['users']:
        if username in item['username']:
            user_count += 1
    if user_count == 1:
        for item in response_body['users']:
            if username in item['username']:
                if newdate not in item['dateOfBirth']:
                    return True
                else:
                    return False
        return False
    else:
        return False


def user_exists_changed_and_alone(username, newdate):
    user_count = 0
    response = requests.get(users_list_url)
    response_body = response.json()
    for item in response_body['users']:
        if username in item['username']:
            user_count += 1
    if user_count == 1:
        for item in response_body['users']:
            if username in item['username']:
                if newdate in item['dateOfBirth']:
                    return True
                else:
                    return False
        return False
    else:
        return False


def user_not_in_base(username):
    response = requests.get(users_list_url)
    response_body = response.json()
    for item in response_body['users']:
        if username in item['username']:
            return False
    return True


class TestGetUsersBirthdayList:
    def test_get_users_list(self):
        response = requests.get(users_list_url)
        response_body = response.json()
        if response.status_code == 200:
            assert "userName", "dateOfBirth" in response_body.keys()


class TestSaveUserToBirthdayList:
    @pytest.mark.parametrize("args, expected_result", [
        pytest.param(default_username, OK_USER_ADDED,
                     id="User created with correct username format", )
    ])
    def test_correct_create_user(self, args, expected_result):
        errors = []
        remove_user(default_username)
        response = create_user(hello_requests_url, default_username, default_birthdate)
        if not response.status_code == 201:
            errors.append(f"Wrong status code, response code is {response.status_code}")
        if expected_result not in response.content:
            errors.append(f"Not expected result, result is {response.content}")
        assert not errors, "Errors occured:\n{}".format("\n".join(errors))

    @pytest.mark.parametrize("args, expected_result", [
        pytest.param(incorrect_username_num, ERROR_USERNAME_WRONG_FORMAT,
                     id="Numeric username incorrect format", ),
        pytest.param(incorrect_username_symbols, ERROR_USERNAME_WRONG_FORMAT,
                     id="Symbolic username incorrect format", ),
        pytest.param(incorrect_username_def_with_numbers, ERROR_USERNAME_WRONG_FORMAT,
                     id="Username with numbers incorrect format", ),
        pytest.param(incorrect_username_def_with_symbols, ERROR_USERNAME_WRONG_FORMAT,
                     id="Username with symbols incorrect format", )
    ])
    def test_incorrect_create_user_username_variants(self, args, expected_result):
        errors = []
        response = create_user(hello_requests_url, args, default_birthdate)
        if not response.status_code == 400:
            errors.append(f"Wrong status code, response code is {response.status_code}")
        if expected_result not in response.content:
            errors.append(f"Not expected result, result is {response.content}")
        if not user_not_in_base(args):
            errors.append("ERROR, incorrect user added to base")
        assert not errors, "Errors occured:\n{}".format("\n".join(errors))

    def test_try_to_save_already_existing_user(self):
        errors = []
        remove_user(default_username)
        create_user(hello_requests_url, default_username, default_birthdate)
        response = create_user(hello_requests_url, default_username, default_birthdate)
        if not response.status_code == 409:
            errors.append(f"Wrong status code, response code is {response.status_code}")
        if ERROR_USER_ALREADY_EXISTS not in response.content:
            errors.append(f"Not expected result, result is {response.content}")
        response = create_user(hello_requests_url, default_username, default_birthdate_2012)
        if not response.status_code == 409:
            errors.append(f"Wrong status code, response code is {response.status_code}")
        if ERROR_USER_ALREADY_EXISTS not in response.content:
            errors.append(f"Not expected result, result is {response.content}")
        if not user_exists_not_changed_and_alone(default_username, default_birthdate_2012):
            errors.append(f"User birthdate changed, result is {response.content}")
        assert not errors, "Errors occured:\n{}".format("\n".join(errors))

    @pytest.mark.parametrize("args, expected_result", [
        pytest.param(incorrect_birthdate_format, ERROR_BIRTHDATE_WRONG_FORMAT,
                     id="Incorrect birthdate format to save", ),
        pytest.param(incorrect_birthdate_not_exists, ERROR_BIRTHDATE_WRONG_FORMAT,
                     id="Not existing date incorrect format to save", ),
        pytest.param(incorrect_birthdate_letters, ERROR_BIRTHDATE_WRONG_FORMAT,
                     id="Random numerics date incorrect format to save", ),
        pytest.param(incorrect_birthdate_fake_leap_year, ERROR_BIRTHDATE_WRONG_FORMAT,
                     id="Fake leap date incorrect format to save", ),
        pytest.param(incorrect_birthdate_future_date, ERROR_BIRTHDATE_WRONG_FORMAT_FUTURE,
                     id="Future date incorrect format to save", )
    ])
    def test_save_user_with_incorrect_birthdate_format(self, args, expected_result):
        errors = []
        remove_user(default_username)
        response = create_user(hello_requests_url, default_username, args)
        if not args == incorrect_birthdate_future_date:
            if not response.status_code == 400:
                errors.append(f"Wrong status code, response code is {response.status_code}")
        else:
            if not response.status_code == 422:
                errors.append(f"Wrong status code, response code is {response.status_code}")
        if expected_result not in response.content:
            errors.append(f"Not expected result, result is {response.content}")
        if not user_not_in_base(default_username):
            errors.append(f"User birthdate changed, result is {response.content}")
        assert not errors, "Errors occured:\n{}".format("\n".join(errors))


class TestUpdateUser:
    def test_basic_user_date_updating(self):
        errors = []
        remove_user(default_username)
        create_user(hello_requests_url, default_username, default_birthdate)
        if user_not_in_base(default_username):
            errors.append("ERROR, user not created")
        response = requests.put(hello_requests_url+default_username,
                                json={'dateOfBirth': default_birthdate_2012})
        if not response.status_code == 204:
            errors.append(f"Wrong status code, response code is {response.status_code}")
        if not user_exists_changed_and_alone(default_username, default_birthdate_2012):
            errors.append("Error, user doesnt exist or not updated")
        assert not errors, "Errors occured:\n{}".format("\n".join(errors))

    def test_update_not_existing_user(self):
        errors = []
        remove_user(default_username)
        response = requests.put(hello_requests_url + default_username,
                                json={'dateOfBirth': default_birthdate})
        if not response.status_code == 201:
            errors.append(f"Wrong status code, response code is {response.status_code}")
        if not correct_user_created(default_username, default_birthdate):
            errors.append("Error, user doesnt exist or not updated")
        assert not errors, "Errors occured:\n{}".format("\n".join(errors))

    @pytest.mark.parametrize("args, expected_result", [
        pytest.param(incorrect_birthdate_format, ERROR_BIRTHDATE_WRONG_FORMAT,
                     id="Incorrect birthdate format to update", ),
        pytest.param(incorrect_birthdate_not_exists, ERROR_BIRTHDATE_WRONG_FORMAT,
                     id="Not existing date incorrect format to update", ),
        pytest.param(incorrect_birthdate_letters, ERROR_BIRTHDATE_WRONG_FORMAT,
                     id="Random numerics date incorrect format to update", ),
        pytest.param(incorrect_birthdate_fake_leap_year, ERROR_BIRTHDATE_WRONG_FORMAT,
                     id="Fake leap date incorrect format to update", ),
        pytest.param(incorrect_birthdate_future_date, ERROR_BIRTHDATE_WRONG_FORMAT_FUTURE,
                     id="Future date incorrect format to update", )
    ])
    def test_update_not_exist_user_with_incorrect_birthdate_format(self, args, expected_result):
        errors = []
        remove_user(default_username)
        response = requests.put(hello_requests_url + default_username,
                                json={"dateOfBirth": args})
        if not args == incorrect_birthdate_future_date:
            if not response.status_code == 400:
                errors.append(f"Wrong status code, response code is {response.status_code}")
        else:
            if not response.status_code == 422:
                errors.append(f"Wrong status code, response code is {response.status_code}")
        if expected_result not in response.content:
            errors.append(f"Not expected result, result is {response.content}")
        if not user_not_in_base(default_username):
            errors.append(f"User birthdate changed, result is {response.content}")
        assert not errors, "Errors occured:\n{}".format("\n".join(errors))

    @pytest.mark.parametrize("args, expected_result", [
        pytest.param(incorrect_birthdate_format, ERROR_BIRTHDATE_WRONG_FORMAT,
                     id="Incorrect birthdate format to update", ),
        pytest.param(incorrect_birthdate_not_exists, ERROR_BIRTHDATE_WRONG_FORMAT,
                     id="Not existing date incorrect format to update", ),
        pytest.param(incorrect_birthdate_letters, ERROR_BIRTHDATE_WRONG_FORMAT,
                     id="Random numerics date incorrect format to update", ),
        pytest.param(incorrect_birthdate_fake_leap_year, ERROR_BIRTHDATE_WRONG_FORMAT,
                     id="Fake leap date incorrect format to update", ),
        pytest.param(incorrect_birthdate_future_date, ERROR_BIRTHDATE_WRONG_FORMAT_FUTURE,
                     id="Future date incorrect format to update", )
    ])
    def test_update_exists_user_with_incorrect_birthdate_format(self, args, expected_result):
        errors = []
        remove_user(default_username)
        create_user(hello_requests_url, default_username, default_birthdate)
        response = requests.put(hello_requests_url + default_username,
                                json={"dateOfBirth": args})
        if not args == incorrect_birthdate_future_date:
            if not response.status_code == 400:
                errors.append(f"Wrong status code, response code is {response.status_code}")
        else:
            if not response.status_code == 422:
                errors.append(f"Wrong status code, response code is {response.status_code}")
        if expected_result not in response.content:
            errors.append(f"Not expected result, result is {response.content}")
        if not user_exists_not_changed_and_alone(default_username, args):
            errors.append(f"User birthdate changed, result is {response.content}")
        assert not errors, "Errors occured:\n{}".format("\n".join(errors))


class TestHappyBirthDay:
    def test_happy_birthday_today(self):
        errors = []
        today_date = datetime.date(datetime.now())
        today_date = today_date.strftime("%Y-%m-%d")
        remove_user(default_username)
        create_user(hello_requests_url, default_username, today_date)
        response = requests.get(hello_requests_url + default_username)
        if not response.status_code == 200:
            errors.append(f"Wrong status code, response code is {response.status_code}")
        if HAPPY_BIRTHDAY not in response.content:
            errors.append(f"Not expected result, result is {response.content}")
        assert not errors, "Errors occured:\n{}".format("\n".join(errors))

    def test_happy_birthday_not_today(self):
        errors = []
        today_date = datetime.date(datetime.now())
        delta = today_date - DT.timedelta(days=360)
        time_ago = delta.strftime("%Y-%m-%d")
        remove_user(default_username)
        create_user(hello_requests_url, default_username, time_ago)
        response = requests.get(hello_requests_url + default_username)
        year = today_date.strftime("%Y")
        if not response.status_code == 200:
            errors.append(f"Wrong status code, response code is {response.status_code}")
        if calendar.isleap(int(year)):
            if HAPPY_BIRTHDAY_NOT_TODAY_LEAP not in response.content:
                errors.append(f"Not expected result, result is {response.content}")
            else:
                if HAPPY_BIRTHDAY_NOT_TODAY_DEFAULT not in response.content:
                    errors.append(f"Not expected result, result is {response.content}")
        assert not errors, "Errors occured:\n{}".format("\n".join(errors))

    def test_happy_birthday_to_not_exists_user(self):
        errors = []
        remove_user(default_username)
        response = requests.get(hello_requests_url + default_username)
        if not response.status_code == 404:
            errors.append(f"Wrong status code, response code is {response.status_code}")
        if ERROR_USER_DOES_NOT_EXISTS not in response.content:
            errors.append(f"Not expected result, result is {response.content}")
        assert not errors, "Errors occured:\n{}".format("\n".join(errors))


class TestDeleteUser:
    def test_delete_existing_user(self):
        errors = []
        create_user(hello_requests_url, default_username, default_birthdate)
        response = requests.delete(hello_requests_url + default_username)
        if not response.status_code == 200:
            errors.append(f"Wrong status code, response code is {response.status_code}")
        if DELETE_SUCCESSFULLY not in response.content:
            errors.append(f"Not expected result, result is {response.content}")
        if not user_not_in_base(default_username):
            errors.append("User not deleted")
        assert not errors, "Errors occured:\n{}".format("\n".join(errors))

    def test_delete_not_existing_user(self):
        errors = []
        remove_user(default_username)
        response = requests.delete(hello_requests_url + default_username)
        if not response.status_code == 404:
            errors.append(f"Wrong status code, response code is {response.status_code}")
        if ERROR_USER_DOES_NOT_EXISTS not in response.content:
            errors.append(f"Not expected result, result is {response.content}")
        if not user_not_in_base(default_username):
            errors.append("User not deleted")
        assert not errors, "Errors occured:\n{}".format("\n".join(errors))

    def test_clean_changes(self):
        remove_user(default_username)
