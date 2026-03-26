# Notely 🚀
**A Smart Project Management Tool**

## 🌟 Overview
Notely is a collaborative project management application designed to streamline task tracking and project organization. This branch focuses on enhancing the user experience through automated media integration and high-performance database indexing.

## 🛠️ My Key Contributions & Advanced Features

### 1. Automated Media Integration (Unsplash API)
- **Problem:** Users often leave project covers blank, leading to a visually unappealing dashboard.
- **Solution:** Integrated the **Unsplash REST API**. If a user submits a project without an image, the backend triggers an automated fetch based on the project title.
- **Technical Detail:** Utilized Python's `urllib` and `json` libraries for asynchronous-style processing within the `create_project` view, ensuring high-quality `ContentFile` objects are saved directly to the Django `media` root.

### 2. Database & Query Optimization
- **N+1 Query Resolution:** Refactored the dashboard view using `.select_related('owner')`. This reduced database hits from $O(N)$ to $O(1)$ by utilizing a SQL `JOIN` instead of multiple individual queries.
- **Data Integrity:** Implemented `get_or_create` logic for UserProfiles to prevent application crashes during edge-case authentications (e.g., admin-side user creation).

### 3. Advanced Testing & Quality Assurance
- **Unit Mocking:** Leveraged `unittest.mock.patch` to simulate API responses. This allows the test suite to run without an internet connection and prevents hitting API rate limits during CI/CD.
- **Coverage:** Achieved comprehensive coverage across models, views, and AJAX endpoints.

## 🏗️ Technical Architecture

The project follows the **Django MVT (Model-View-Template)** pattern:
- **Models:** Defined relationships for Projects, Tasks, and UserProfiles.
- **Views:** Handled complex logic for AJAX status updates and API fetching.
- **Templates:** Utilized Bootstrap 5 and custom CSS for a responsive, mobile-first UI.

## 🚀 Installation & Setup
1. **Clone the repo:** `git clone <repo-url>`
2. **Setup Venv:** `python -m venv venv` and `venv\Scripts\activate` (Windows)
3. **Install Dependencies:** `pip install -r requirements.txt`
4. **Environment Variables:** Create a `.env` file in the root directory:
   ```env
   SECRET_KEY=your_django_key
   UNSPLASH_ACCESS_KEY=your_api_key
   DEBUG=True