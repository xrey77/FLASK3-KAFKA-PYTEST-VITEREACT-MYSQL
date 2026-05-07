import os
import math
from sqlalchemy import func # type: ignore
from config.extensions import db
from app.models.user import Users, Roles, Departments
from flask_bcrypt import Bcrypt # type: ignore
from werkzeug.utils import secure_filename # type: ignore

bcrypt = Bcrypt()
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
IMAGES_DIR = os.path.join(os.path.abspath('static'), 'users')

class UserService:

    @staticmethod
    def get_user_by_id(user_id):
        user = db.get_or_404(Users, user_id)
        
        role = Roles.query.filter_by(id=user.role_id).first()    
        department = Departments.query.filter_by(id=user.department_id).first()

        # Logic for formatting data
        return {
            'id': user.id,
            'firstname': user.firstname,
            'lastname': user.lastname,
            'email': user.email,
            'mobile': user.mobile,
            'role': role.name,
            'department': department.dept_name,
            'userpic': user.userpic,
            'secret': str(user.secret) if user.secret else None,
            'qrcodeurl': str(user.qrcodeurl) if user.qrcodeurl else None
        }

@staticmethod
def get_users_paginated(page):
    per_page = 5
    
    # db.paginate handles the count query and math for you
    pagination = db.paginate(
        db.select(Users).order_by(Users.id), 
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return {
        "users": [user.to_dict() for user in pagination.items],
        "total_pages": pagination.pages,  # Access built-in attribute
        "total_records": pagination.total # Access built-in attribute
    }



@staticmethod
def update_user_profile(user_id, data):
    user = db.get_or_404(Users, user_id)
    
    # Update fields
    user.firstname = data.get("firstname")
    user.lastname = data.get("lastname")
    user.mobile = data.get("mobile")
    
    db.session.commit()
    return user

@staticmethod
def update_user_password(user_id, new_password):
    user = db.get_or_404(Users, user_id)
    
    # Logic: Hash and Save
    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    user.password = hashed_password
    
    db.session.commit()
    return user



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def update_profile_picture(user_id, file):
    if not file or file.filename == '':
        return {"error": "No selected image."}, 400

    if not allowed_file(file.filename):
        return {"error": "File type not allowed."}, 400

    # Prepare file names
    ext = os.path.splitext(secure_filename(file.filename))[1]
    new_filename = f"00{user_id}{ext}"
    upload_path = os.path.join(IMAGES_DIR, new_filename)

    user = db.get_or_404(Users, user_id)

    # Cleanup old file
    if user.userpic:
        old_filename = user.userpic.split('/')[-1]
        if old_filename != "pix.png":
            old_path = os.path.join(IMAGES_DIR, old_filename)
            if os.path.exists(old_path):
                os.remove(old_path)

    # Save new file and update DB
    file.save(upload_path)
    user.userpic = new_filename
    db.session.commit()

    return {"userpic": user.userpic, "message": "Success!"}, 200