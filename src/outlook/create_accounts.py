from botasaurus.decorators_utils import create_directory_if_not_exists
import traceback
from botasaurus import *
from .create_accounts_utils import *
from botasaurus.create_stealth_driver import create_stealth_driver
from botasaurus.utils import relative_path

def createTempProfile(username, cookies):
    foldername = f"profiles/{username}/"
    create_directory_if_not_exists(foldername)
    pathjson = foldername + "profile.json"
    bt.write_json(cookies, pathjson, False)

def convert_cookie_format(cookie):
    default_attributes = {
        "domain": "",
        "expires": None,
        "httpOnly": False,
        "name": "",
        "path": "/",
        "priority": "Medium",
        "sameParty": False,
        "sameSite": "None",
        "secure": True,
        "session": False,
        "size": 0,
        "sourcePort": 443,
        "sourceScheme": "Secure",
        "value": ""
    }
    # Update default attributes with the input cookie attributes
    transformed_cookie = default_attributes.copy()

    expires = cookie.get("expiry", cookie.get("expires", None))
    transformed_cookie.update({
        "domain": cookie.pop("domain", ""),
        "expires": cookie.pop("expiry", None),
        "httpOnly": cookie.get("httpOnly", False),
        "name": cookie.pop("name", ""),
        "path": cookie.pop("path", "/"),
        "sameSite": cookie.pop("sameSite", "None"),
        "secure": cookie.pop("secure", True),
        "value": cookie.get("value", ""),
        "size": len(cookie.pop("value", "")) + 4 if cookie.get("httpOnly", False) else len(cookie.pop("value", "")) + 4
    })
    if expires:
        transformed_cookie['expires'] = expires

    updated_cookie = {**transformed_cookie, **cookie}  # Merge with priority to original cookie values
    if transformed_cookie['expires'] is None:
        # Session Cookies...
        return None
    return updated_cookie

def convert_cookie_formats(cookies):
    return bt.remove_nones([convert_cookie_format(cookie) for cookie in cookies])

def get_default_config_paths():
    extension_path = relative_path('capsolver/assets/config.js', 0)
    return [
        relative_path("capsolver/aws-recognition.js", 0),
        relative_path("capsolver/funcaptcha-recognition.js", 0),
        relative_path("capsolver/hcaptcha-recognition.js", 0),
        relative_path("capsolver/image-to-text.js", 0),
        relative_path("capsolver/my-content-script.js", 0),
        relative_path("capsolver/recaptcha-recognition.js", 0),
        relative_path("capsolver/www/assets/index.80d9cc3d.js", 0),
        relative_path("capsolver/background.js", 0),
    ]

def get_extension_config_path():
    extension_path = relative_path('./capsolver/assets/config.js', 0)
    return extension_path

def get_extension_path():
    # extension_path = relative_path('../../Downloads/capsolver', 0)
    extension_path = relative_path('./capsolver', 0)
    return extension_path

def add_arguments(data, options):
    if data.get('capsolver_apikey'):
        extension_path = get_extension_path()
        options.add_argument(f'--load-extension={extension_path}')

@browser(
    add_arguments=add_arguments,
    create_driver=create_stealth_driver(start_url=None, wait=None),
    output=None,
    profile=lambda data: data.get('account')['username'],
    tiny_profile=True,
    proxy=lambda data: data.get('proxy'),
    # user_agent=bt.UserAgent.REAL,
    window_size=bt.WindowSize.REAL,
)
def create_accounts(driver: AntiDetectDriver, data):
    proxy = data['proxy']
    captcha = data.get('captcha')
    capsolver_apikey = data.get('capsolver_apikey')
    account = data.get('account')
    # create_user(proxy)

    first_name = account['first_name']
    last_name = account['last_name']
    username = account['username']
    password = account['password']
    dob_year = str(account['dob']['year'])
    dob_day = str(account['dob']['day'])
    dob_month = str(account['dob']['month'])
    account['email'] = username + '@hotmail.com'
    email = account['email']

    def sign_up():
        type_email(driver, email)
        press_next_btn(driver)
        verify_username_is_unique(driver)
        type_password(driver, password)
        press_next_btn(driver)
        type_first_name(driver, first_name)
        type_last_name(driver, last_name)
        press_next_btn(driver)
        type_birth_month(driver, dob_month)
        type_birth_year(driver, dob_year)
        enter_birth_day(driver, dob_day)

        if captcha:
            driver.execute_file("spy-token.js")

        press_next_btn(driver)

        rst = check_for_phone_verification_or_captcha(driver)
        if rst:
            return rst

        if captcha:
            rst = solvecaptcha_with_captcha_solver(driver, proxy, captcha, capsolver_apikey)
        else:
            rst = waitforretryorsolved(driver, )

        if rst:
            return rst

        give_consent(driver)

    try:
        driver.organic_get('https://signup.live.com/')
        wait_till_signup_page(driver)

        if is_bot_detected(driver):
            print('Bot is Blocked by Microsoft. Possibly because Microsoft has flagged the IP.')
            return DETECTED

        rst = sign_up()

        if rst:
            if rst == PHONE_VERIFICATION:
                print('Skipping Account Creation due to phone verification.')
            if rst == RETRY:
                print('Retrying Account Creation.')
            if rst == DETECTED:
                print('Skipping Account Creation due to Detection.')

            return rst

        # links = [
        #     'https://signup.live.com/',
        #     'https://login.live.com/'
        # ]
        # unique_cookies = convert_cookie_formats(get_unique_cookies(driver, links))

        # createTempProfile(username, unique_cookies)

        prevprofile = bt.Profile.profile

        bt.Profile.profile = username
        bt.Profile.set_profile(account)

        bt.Profile.profile = prevprofile

        print(f"Created Account for {username}")
        return account

    except Exception:
        if has_username_error(driver):
            print("Username is already taken. Retrying with new Account.")
            return RETRY

        traceback.print_exc()
        return None
