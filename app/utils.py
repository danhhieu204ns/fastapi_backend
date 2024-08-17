from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])

def hash(password: str):
    return pwd_context.hash(password)

def verify(plain_password, hassed_password):
    return pwd_context.verify(plain_password, hassed_password)

def calculate_age(birth_date, current_date):
    
    age = current_date.year - birth_date.year
    
    if (current_date.month, current_date.day) < (birth_date.month, birth_date.day):
        age -= 1
    
    return age