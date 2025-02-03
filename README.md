# Digital Closet

## About The Project

**Digital Closet** is a web application that helps users organize their wardrobe by adding, tracking, and managing clothing items. Users can log their daily outfits, track wear frequency, and analyze wardrobe usage with built-in statistics.

### Key Features

- **Add Clothing Items**: Users can input clothing details such as brand, color, price, and upload images.
- **Wear Tracking Calendar**: Log outfits worn on specific days using a dynamic calendar.
- **Track Wear Frequency**: Each clothing item has a **wear count** that updates automatically.
- **Cost Per Wear Analysis**: Helps users understand how much value they get from each clothing item.
- **Filter and Sort**: Organize wardrobe by brand, category, color, and wear frequency.
- **AWS S3 Image Storage**: Securely store and retrieve images from the cloud.
- **Multi-User Support**: Each user has a separate closet and wear history.

### Built With

- [Django](https://www.djangoproject.com/)
- [AWS S3](https://aws.amazon.com/s3/)
- [FullCalendar](https://fullcalendar.io/)

---

## Getting Started

### Preface

This application is currently designed to run **locally** on your machine. You must run the server on your local environment and access it via `127.0.0.1:8000`. At this stage, the app is not publicly accessible online. However, future updates will include **Docker deployment**.

### Installation

Follow these steps to set up the application:

1. **Clone the Repository**

   ```sh
   git clone https://github.com/liamp1/digital_closet.git
   ```

2. **Install Dependencies**

   ```sh
   pip install -r requirements.txt
   ```

3. **Run the Application**

   ```sh
   python manage.py runserver
   ```

4. **Access the Application**

   - Open `http://127.0.0.1:8000/` in your browser.

---

## Usage

### 1. Adding Items to Your Closet

- Navigate to the **Closet** page.
- Click **Add Item**.
- Enter the item's **name, brand, category, color, and price**.
- Upload an image.
- Click **Save** to add the item to your closet.

### 2. Logging Outfits in the Calendar

- Navigate to the **Calendar** page.
- Click on a date to log an outfit.
- Select items from your closet.
- Click **Log Items**.
- The items appear in the selected date on the calendar.

### 3. Editing and Deleting Items

- Click an item in the closet to **edit or replace** its details.
- To delete an item, click **Remove Item**.
- Replacing an image **removes the old one from AWS S3 automatically**.

### 4. Viewing Outfit Statistics

- On the **Calendar** page, view the **Total Outfits This Month**.
- See the **Most Worn Item** dynamically update as you log outfits.
- Click an item to check **Cost Per Wear** based on price and wear count.

---
