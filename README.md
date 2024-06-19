# Hope for Wildlife Dispatch Service Developer Documentation

## Installation

This application is a standard Django application with dependencies on Twilio and Google Maps API. Follow the steps below to set up and run the application.

### Prerequisites

Ensure you have the following installed:

- Python 3.x
- Django
- pip (Python package installer)
- PostgreSQL (or any other database supported by Django)

### Dependencies

- `twilio`: For sending SMS notifications.
- `requests`: For making HTTP requests to external APIs.
- `python-dotenv`: For loading environment variables from a `.env` file.

### Setup

1. **Clone the repository:**

    ```bash
    git clone https://github.com/your-repo/hope-for-wildlife.git
    cd hope-for-wildlife
    ```

2. **Create and activate a virtual environment:**

    ```bash
    python -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    ```

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables:**

    Create a `.env` file in the root directory of your project and add the following variables:

    ```env
    TWILIO_ACCOUNT_SID=your_twilio_account_sid
    TWILIO_AUTH_TOKEN=your_twilio_auth_token
    TWILIO_PHONE_NUMBER=your_twilio_phone_number
    GOOGLE_MAPS_API_KEY=your_google_maps_api_key
    SECRET_KEY=xxx
    ```

5. **Run database migrations:**

    ```bash
    python manage.py migrate
    ```

6. **Create a superuser:**

    ```bash
    python manage.py createsuperuser
    ```

7. **Run the development server:**

    ```bash
    python manage.py runserver
    ```

## Views and Templates

### `views.py`

#### Helper Functions

- **`geocode_address(address)`**:
  - Sends a request to the Google Maps Geocoding API to convert an address into geographic coordinates.

- **`clean_number(phone_string)`**:
  - Cleans and returns a string containing only the numeric characters from a phone number.

#### Decorators

- **`conditional_superuser_required(view_func)`**:
  - Ensures the user is a superuser if `id` is None. If not, redirects to a specified URL or default URL.

#### Views

- **`index(request)`**:
  - Renders the homepage.

- **`report(request, id=None)`**:
  - Handles the reporting of animal cases. 
  - Retrieves or creates a `Case` object based on the presence of an `id`.
  - Sends notifications to nearby volunteers using Twilio.

- **`map_view(request)`**:
  - Displays a map with recent cases and logged-in dispatch users.
  - Filters cases based on the user's travel distance.

- **`log(request)`**:
  - Displays a log of all cases.

- **`case(request, id)`**:
  - Displays and updates a specific case.
  - Logs updates with the user's information and status.

- **`register(request, mobile_phone=None)`**:
  - Handles user registration. 
  - Uses Google Maps Geocoding API to fetch and save home coordinates.

- **`forgot_password(request)`**:
  - Handles the forgot password functionality. 
  - Sends a password reset link to the user's mobile phone using Twilio.

- **`set_password(request, uidb64, token)`**:
  - Handles setting a new password for the user.

### `map_.html`

This template is used for displaying the map with cases and user data.

#### Template Variables

- **`cases`**:
  - List of filtered cases within the user's travel distance.

- **`map_data`**:
  - JSON encoded data containing case coordinates, status, and animal type for rendering on the map.

- **`GOOGLE_MAPS_API_KEY`**:
  - Google Maps API key for rendering the map.

- **`user_data`**:
  - JSON encoded data containing logged-in dispatch users and their coordinates.


# Hope for Wildlife Dispatch Service Volunteer Documentation

## 1. Register

Volunteers use this form to register a new account.

1. New users text "REGISTER" to 902-907-3016 and receive a text with a registration link.
    - We can treat the keyword, "REGISTER" like a shared password for registration purposes. It can be changed to a secret if necessary.
2. Click on the link to open the registration page at [hfw.tbat.io/register](https://hfw.tbat.io/register). The phone number field will be pre-populated.
3. Fill in your first and last name, a valid email, and full home address (including city and province). This is used to calculate your maximum travel radius.
4. Enter the maximum one-way distance you are willing to travel from home.
5. Create a password, confirm it, and then click the 'Register' button.
6. After successful registration, you'll be directed to the app's homepage with a message to watch for texts from 902-907-3016.

**Video:** [Registration Process](https://photos.app.goo.gl/2QiStsJ5nFsVJAWT7)

---

## 2. Report

This form is for reporting pickup requests, usable by both the public and volunteers.

1. Go to [hfw.tbat.io/report](https://hfw.tbat.io/report).
2. Select an animal type from the dropdown menu.
3. Enter your name and phone number.
4. Optionally, add a note describing the situation.
5. Scroll down and adjust the map marker to the exact location of the animal. Note: The location accuracy is higher on mobile phones than on desktops.
6. Press 'Submit'.
    - The system will notify nearby volunteers via text with a link to the report.
7. The page redirects to the login/register page.

**Video:** [Report Process](https://photos.app.goo.gl/Y7mRRFbhRVA3baoD9)

---

## 3. Update Case

This section details every update made on a case, including the contact information of the updater.

1. Volunteers will receive a text if they are within the specified radius of the animal.
2. Open the text and click the link. If you're logged in, the case page appears; if not, log in first.
3. The map displays the volunteer's current location, the patient's location, and the nearest Hope for Wildlife facility, with a suggested route.
4. To update the case, click one of the colored buttons below the animal type:
    - **Pick-up:** Enter your username and click 'Confirm'.
    - **Relay:** Fill out a new report form linked to the case, including relay location and details in the notes. Submitting this form notifies a new set of volunteers.
    - **In-transit:** Indicates that the patient has been picked up. Enter your username and click 'Confirm'.
    - **Delivered:** Indicates that the patient has reached the Hope for Wildlife facility. Enter your username and click 'Confirm'.

All updates are recorded below the map on the case page.

**Video:** [Update Case Process](https://photos.app.goo.gl/hJNNrgEfdEX8EUQ27)

---

## 4. Map

This feature is for admins to overview and manage cases.

- The left side of the screen lists recent cases chronologically by the last update.
- The map shows the current locations of all patients with a color-coded status.
- Clicking the 'Focus' button on a case card zooms in on the corresponding map marker.
- Clicking 'Details' opens the corresponding case page.

**Map Link:** [hfw.tbat.io/map](https://hfw.tbat.io/map/)

---

## 5. Admin

This page is for user management and database maintenance.

- Admins can reset user names or passwords by updating the corresponding record.
- Currently, [batten.tyler@gmail.com](mailto:batten.tyler@gmail.com) is the only admin. Please inform me of any additional users requiring admin access.

**Admin Link:** [hfw.tbat.io/admin](https://hfw.tbat.io/admin/)

---

