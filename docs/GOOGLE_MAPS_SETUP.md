# Google Maps API — Step 5

This project uses **Google Maps JavaScript API** (map display) and **Geocoding API** (address → coordinates). You need a free API key.

---

## 1. Get an API key

1. Go to **[Google Cloud Console](https://console.cloud.google.com/)** and sign in.
2. Create a project (or select one):
   - Click the project dropdown at the top → **New Project**.
   - Name it e.g. `Lost Found Pets` → **Create**.
3. Enable the APIs:
   - **APIs & Services** → **Library**.
   - Search for **Maps JavaScript API** → open it → **Enable**.
   - Search for **Geocoding API** → open it → **Enable**.
4. Create the key:
   - **APIs & Services** → **Credentials** → **Create Credentials** → **API key**.
   - Copy the key (you can restrict it later: HTTP referrers for your site, or leave unrestricted for localhost).

---

## 2. Add the key to the project

1. In the project folder, create a file named **`.env`** (if it doesn’t exist).
2. Add this line (replace with your real key):

   ```
   GOOGLE_MAPS_API_KEY=AIza...your-key-here
   ```

3. **Do not commit `.env`** to git (it should be in `.gitignore`). Use `.env.example` as a template without real keys.

---

## 3. Restart and test

1. Restart the dev server:
   ```bat
   python manage.py runserver
   ```
2. **Create or edit a report** → enter an address → click **Geocode address to map** → the map should move and the marker should appear.
3. **Report detail** (with lat/lng) → the map with a marker should load.
4. **Shelter directory** → if shelters have coordinates, the map with markers should load.

If the key is missing or wrong, maps will not load and the browser console may show errors about the Maps API.
