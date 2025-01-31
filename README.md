# 🎵 Streamlytics - Billboard 100 Analyzer

A **Streamlit** web application that enables users to **fetch, analyze, and visualize Billboard Top 100 charts** using Spotify and Cover Art data. This tool provides a seamless way to:
- Fetch & enrich Billboard data from a given week.
- Download cover art for the Billboard songs.
- Generate posters from album cover art.
- Authenticate and interact with Spotify.

Additionally, the app includes **analytics, playback tracking, and cover art visualization**.

---

## 📌 Features

✔ **Billboard Data Processing** - Fetches Billboard Top 100 data for a given week.  
✔ **Spotify Enrichment** - Adds Spotify metadata like album cover art, track ID, and audio features.  
✔ **Cover Art Download** - Saves high-quality cover art for the Billboard songs.  
✔ **Poster Creation** - Generates beautiful collages and posters from the collected cover art.  
✔ **Spotify Authentication** - Allows users to connect their Spotify account.  
✔ **Analytics & Trends** - Provides **detailed insights into playback history, downloads, and streaming statistics**.  
✔ **Playlist Cover Art** - Generates and customizes cover images using Spotify album covers.  
✔ **Interactive UI** - Built with **Streamlit** for an easy-to-use interface.  

---

## 🚀 Installation

### **1. Clone the Repository**
```sh
git clone https://github.com/your-username/streamlytics.git
cd streamlytics
```

### **2. Create a Virtual Environment (Recommended)**
```sh
python -m venv venv
source venv/bin/activate  # On MacOS/Linux
venv\Scripts\activate   # On Windows
```

### **3. Install Dependencies**
```sh
pip install -r requirements.txt
```

### **4. Set Up Spotify API Credentials**
You need **Spotify API credentials** to fetch metadata and cover art.

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
2. Create an application.
3. Get your **Client ID** and **Client Secret**.
4. Create a `.env` file in the root directory and add:
    ```sh
    SPOTIPY_CLIENT_ID="your-client-id"
    SPOTIPY_CLIENT_SECRET="your-client-secret"
    SPOTIPY_REDIRECT_URI="http://localhost:8888/callback"
    ```

### **5. Run the Streamlit App**
```sh
streamlit run streamlytics/pages/4_Billboard_100.py
```

---

## 📂 File Structure
```
streamlytics/
│-- pages/
│   ├── 1_Analytics.py            # Analytics dashboard
│   ├── 2_Playback.py             # Playback tracking and insights
│   ├── 3_Download_Statistics.py   # Download statistics visualization
│   ├── 4_Billboard_100.py        # Billboard Top 100 fetching and enrichment
│   ├── 5_Playlist_Cover_Art.py   # Playlist cover art generator
│   ├── 6_Top_Tracks_Cover_Art.py # Top track cover art visualization
│-- data/                         # Contains Billboard Parquet files
│-- json/                         # Stores JSON outputs
│-- fonts/                        # Font files for posters
│-- coverArt.py                   # Handles fetching Billboard data
│-- spotify_cover_art.py          # Manages Spotify authentication and cover art retrieval
│-- image_processing.py           # Processes images, creates posters
│-- utils.py                      # Utility functions
│-- requirements.txt              # Python dependencies
│-- README.md                     # This file
```

---

## 🎨 Page Descriptions

### 📊 **1_Analytics.py**  
_Provides analytics and insights on streaming data, visualizing trends, and usage patterns._

### 🎶 **2_Playback.py**  
_Manages playback statistics, allowing users to analyze their listening history._

### 📥 **3_Download_Statistics.py**  
_Displays download statistics for various songs and albums, showing trends over time._

### 🎼 **4_Billboard_100.py**  
_Fetches and enriches Billboard Top 100 chart data, allowing users to view rankings and create posters._

### 🎨 **5_Playlist_Cover_Art.py**  
_Generates and customizes cover art for playlists using album images and user preferences._

### 🖼 **6_Top_Tracks_Cover_Art.py**  
_Creates collages and visualizations using the top tracks' cover art._

---

## 🛠 Troubleshooting

### **1. Spotify Authentication Error**
- Ensure you have added the **correct redirect URI** in the Spotify Developer Dashboard.
- Make sure your **client ID and secret** are correct in the `.env` file.

### **2. Streamlit App Won’t Run**
- Ensure you have activated the virtual environment (`venv`).
- Run `pip install -r requirements.txt` to install missing dependencies.

### **3. Cover Art Not Downloading**
- Ensure the **JSON file exists** before downloading cover art.
- Try running the fetch step again to regenerate the JSON.

---

## 📜 License
This project is **open-source** under the MIT License. Feel free to contribute and improve it!

---

## 🤝 Contributing
We welcome contributions! Feel free to submit a pull request or open an issue.

1. **Fork** the repository.
2. **Create a branch** (`git checkout -b feature-branch`).
3. **Commit your changes** (`git commit -m "Add new feature"`).
4. **Push to your fork** (`git push origin feature-branch`).
5. **Submit a pull request**!

---

## 🌟 Acknowledgments
Special thanks to **Billboard, Spotify, and Streamlit** for the inspiration behind this project! 🎶

---

## 📧 Contact
For any inquiries or suggestions, feel free to reach out via GitHub Issues.

---
