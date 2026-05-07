from sqlalchemy import String, text, Text # type: ignore
from sqlalchemy_serializer import SerializerMixin # type: ignore
from sqlalchemy.sql import func # type: ignore
from config.extensions import db


class Roles(db.Model, SerializerMixin):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False, unique=True)
    
    users = db.relationship('Users', backref='role', lazy=True)

    def __repr__(self):
        return f"<Role '{self.name}'>"

class Departments(db.Model, SerializerMixin):
    __tablename__ = "departments"
    id = db.Column(db.Integer, primary_key=True)
    dept_name = db.Column(db.String(50), nullable=False, unique=True)

    users = db.relationship("Users", back_populates="department")

class Users(db.Model, SerializerMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50),nullable=False)
    lastname = db.Column(db.String(50),nullable=False)
    email = db.Column(db.String(100),nullable=False, unique=True)
    mobile = db.Column(db.String(32))
    username = db.Column(db.String(50, collation='utf8mb4_bin'), nullable=False, unique=True)    
    password = db.Column(db.String(200),nullable=False)
    isactivated = db.Column(db.Integer, server_default=text("1"))
    isblocked = db.Column(db.Integer, server_default=text("0"))
    mailtoken = db.Column(db.Integer, server_default=text("0"))
    userpic = db.Column(String(100), nullable=True)    
    secret = db.Column(db.Text(length=60), nullable=True)
    qrcodeurl = db.Column(db.Text, nullable=True)   

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id", ondelete="SET NULL"))
    department = db.relationship("Departments", back_populates="users")
    # role = db.relationship('Roles', back_populates='users')

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
        
    def to_dict(self, secret=None, qrcodeurl=None):
        return {
            'id': self.id,
            'role': self.role.name,
            'department': self.department.dept_name,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'email': self.email,
            'mobile': self.mobile,            
            'username': self.username,
            'isactivated': self.isactivated,
            'iblocked': self.isblocked,
            'mailtoken': self.mailtoken,
            'userpic': self.userpic,
            'secret': self.secret if self.secret else None,                      
            'secret': self.qrcodeurl if self.qrcodeurl else None,
        }

    def __repr__(self):
        return f"<Users '{self.id}','{self.firstname}','{self.lastname}'>"
    
