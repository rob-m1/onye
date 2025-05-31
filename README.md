# Onye - Full-Stack Engineer Code Test

Setup Instructions:

First, clone the project repository from GitHub:

```bash
git clone https://github.com/rob-m1/onye.git
```

Create a virtual environment

```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

Now do the following:
```bash
cd django_app

pip install -r requirements.txt

# Apply database migrations
python manage.py makemigrations
python manage.py migrate

# Create a Superuser
python manage.py createsuperuser

# Run the Development Server
python manage.py runserver
```
You can now access the application in your web browser at http://127.0.0.1:8000/

---

Feature Overview:

User Management & Authentication
* User Registration: New users can sign up for an account.
* User Login/Logout: Secure authentication system for users to access their accounts. (Password hashing)
* Custom User Model: Utilizes a custom User model rather than get_user_model().
* Password Validation: Enforces strong password policies during registration.

Blog Post Management
* Post Creation: Authenticated users can create new blog posts.
* Post Editing: Authors can edit their own posts.
* Post Deletion: Authors can delete their own posts.
* Category Association: Posts can be associated with one or more categories.
* Comments: Anyone can post a comment, but only authenticated users can edit and delete them.

Content Discovery
* Homepage Feed: Displays a paginated list of all blog posts, 5 per page.
* Search and Category Filtering: Users can filter blog posts by specific categories and by querying for the title or content,does not require full page reloads.
