import pyotp # type: ignore
import qrcode # type: ignore
import base64
import io
from config.extensions import db
from app.models.user import Users, Roles, Departments
from flask_bcrypt import Bcrypt, check_password_hash # type: ignore
from flask_jwt_extended import create_access_token # type: ignore
from werkzeug.exceptions import NotFound, BadRequest # type: ignore

bcrypt = Bcrypt()

def register_user(data):
    # 1. Validation Logic
    if Users.query.filter_by(email=data.get("email")).first():
        raise ValueError("Email Address is already taken.")
    
    if Users.query.filter_by(username=data.get("username")).first():
        raise ValueError("Username is already taken.")

    # 2. Data Preparation
    hashed_pw = bcrypt.generate_password_hash(data.get("password")).decode('utf-8')
    
    user = Users(
        firstname=data.get("firstname"),
        lastname=data.get("lastname"),
        email=data.get("email"),
        role_id=2,
        department_id=1,
        userpic="pix.png",
        mobile=data.get("mobile"),
        username=data.get("username"),
        password=hashed_pw
    )

    # 3. Database Operation
    db.session.add(user)
    db.session.commit()
    return user



def authenticate_user(username, password):
    user = Users.query.filter_by(username=username).first()

    if not user:
        return {"error": "Username does not exist, please register.", "status": 400}, None

    if not check_password_hash(user.password, password):
        return {"error": "Invalid Password, please try again.", "status": 404}, None

    role = Roles.query.filter_by(id=user.role_id).first()    
    department = Departments.query.filter_by(id=user.department_id).first()
    
    token = create_access_token(identity=user.username)
    user_data = {
        'id': user.id,
        'firstname': user.firstname,
        'lastname': user.lastname,
        'username': user.username,
        'email': user.email,
        'mobile': user.mobile,
        'role': role.name,
        'department': department.dept_name,
        'isactivated': user.isactivated,
        'isblocked': user.isblocked,
        'userpic': user.userpic,
        'qrcodeurl': user.qrcodeurl,
        'token': token,
        "message": "Login Successfully."
    }

    return None, user_data    


def mfa_activation(user_id, enable):
    user = db.get_or_404(Users, user_id)

    if enable:
        secret = pyotp.random_base32()
        uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.email, 
            issuer_name="BARCLAYS BANK"
        )

        # Generate QR Code
        img = qrcode.make(uri)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        user.qrcodeurl = f"data:image/png;base64,{img_base64}"
        user.secret = secret
        db.session.commit()
        
        return {"qrcodeurl": f"data:image/png;base64,{img_base64}", "enabled": True}
    
    else:
        user.qrcodeurl = None
        user.secret = None
        db.session.commit()
        return {"enabled": False}
    
def verify_user_totp(user_id, otp_code):
    # Fetch user or automatically trigger 404
    user = db.get_or_404(Users, user_id)
    
    totp = pyotp.TOTP(user.secret)
    
    if totp.verify(otp_code):
        return {
            "username": user.username,
            "message": "OTP code has been verified successfully."
        }
    
    raise BadRequest("Invalid OTP code, please try again.")
