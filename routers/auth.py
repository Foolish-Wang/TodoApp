# 导入所需的库和模块
from datetime import datetime, timedelta, timezone  # 用于处理日期和时间
from fastapi.templating import Jinja2Templates  # 用于渲染HTML模板
from fastapi.responses import HTMLResponse  # 用于返回HTML响应
from jose import jwt, JWTError  # 用于JWT（JSON Web Token）的编码和解码
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer  # 用于OAuth2密码认证
from database import SessionLocal, engine  # 数据库会话和引擎
from sqlalchemy.orm import Session  # SQLAlchemy的会话对象
from passlib.context import CryptContext  # 用于密码哈希和验证
import models  # 数据库模型
from typing import Optional  # 用于类型注解
from pydantic import BaseModel  # 用于数据验证和设置
from fastapi import Depends, HTTPException, status, APIRouter, Request, Response, Form  # FastAPI的核心功能
from starlette.responses import RedirectResponse  # 用于重定向响应
import sys
sys.path.append("..")  # 将上级目录添加到系统路径，以便导入模块

# 设置JWT的密钥和算法
SECRET_KEY = "KlgH6AzYDeZeGwD288to79I3vTHT8wp7"
ALGORITHM = "HS256"

# 初始化Jinja2模板引擎，指定模板目录
templates = Jinja2Templates(directory="templates")

# 初始化密码哈希上下文，使用bcrypt算法
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 创建数据库表（如果尚未创建）
models.Base.metadata.create_all(bind=engine)

# 初始化OAuth2密码认证，指定token的URL
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

# 创建APIRouter实例，设置前缀和标签
router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401: {"user": "Not authorized"}}  # 文档中显示的401响应
)

# 定义LoginForm类，用于处理登录表单数据


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    # 从请求中提取表单数据
    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get("email")
        self.password = form.get("password")

# 获取数据库会话的函数


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# 生成密码哈希


def get_password_hash(password):
    return bcrypt_context.hash(password)

# 验证密码是否匹配


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)

# 验证用户是否存在且密码正确


def authenticate_user(username: str, password: str, db):
    user = db.query(models.Users)\
        .filter(models.Users.username == username)\
        .first()

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# 创建JWT访问令牌


def create_access_token(username: str, user_id: int,
                        expires_delta: Optional[timedelta] = None):

    encode = {"sub": username, "id": user_id}  # JWT的payload
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=60)  # 60分钟过期
    encode.update({"exp": expire})  # 添加过期时间
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)  # 编码生成JWT

# 获取当前用户信息


async def get_current_user(request: Request):
    try:
        token = request.cookies.get("access_token")  # 从cookie中获取token
        if token is None:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[
                             ALGORITHM])  # 解码JWT
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            logout(request)  # 如果token无效，执行登出
        return {"username": username, "id": user_id}
    except JWTError:
        # 如果JWT解码失败，抛出404错误
        raise HTTPException(status_code=404, detail="Not found")

# 登录并生成访问令牌


@router.post("/token")
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):
    user = authenticate_user(
        form_data.username, form_data.password, db)  # 验证用户
    if not user:
        return False  # 如果用户验证失败，返回False
    token_expires = timedelta(minutes=60)  # 设置token过期时间为60分钟
    token = create_access_token(user.username,
                                user.id,
                                expires_delta=token_expires)  # 创建JWT

    response.set_cookie(key="access_token", value=token,
                        httponly=True)  # 将token设置为cookie

    return True  # 返回True表示登录成功

# 返回登录页面


@router.get("/", response_class=HTMLResponse)
async def authentication_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# 处理登录请求


@router.post("/", response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    try:
        form = LoginForm(request)
        await form.create_oauth_form()  # 提取表单数据
        response = RedirectResponse(
            url="/todos", status_code=status.HTTP_302_FOUND)  # 重定向到/todos页面

        # 验证用户并生成token
        validate_user_cookie = await login_for_access_token(response=response, form_data=form, db=db)

        if not validate_user_cookie:
            msg = "Incorrect Username or Password"  # 如果验证失败，返回错误消息
            return templates.TemplateResponse("login.html", {"request": request, "msg": msg})
        return response  # 如果验证成功，重定向到/todos页面
    except HTTPException:
        msg = "Unknown Error"  # 如果发生未知错误，返回错误消息
        return templates.TemplateResponse("login.html", {"request": request, "msg": msg})

# 处理登出请求


@router.get("/logout")
async def logout(request: Request):
    msg = "Logout Successful"  # 登出成功消息
    response = templates.TemplateResponse(
        "login.html", {"request": request, "msg": msg})  # 返回登录页面
    response.delete_cookie(key="access_token")  # 删除access_token cookie
    return response

# 返回注册页面


@router.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# 处理用户注册请求


@router.post("/register", response_class=HTMLResponse)
async def register_user(request: Request, email: str = Form(...), username: str = Form(...),
                        firstname: str = Form(...), lastname: str = Form(...),
                        password: str = Form(...), password2: str = Form(...),
                        db: Session = Depends(get_db)):

    validation1 = db.query(models.Users).filter(
        models.Users.username == username).first()  # 检查用户名是否已存在

    validation2 = db.query(models.Users).filter(
        models.Users.email == email).first()  # 检查邮箱是否已存在

    if password != password2 or validation1 is not None or validation2 is not None:
        msg = "Invalid registration request"  # 如果密码不匹配或用户名/邮箱已存在，返回错误消息
        return templates.TemplateResponse("register.html", {"request": request, "msg": msg})

    user_model = models.Users()  # 创建用户模型实例
    user_model.username = username
    user_model.email = email
    user_model.first_name = firstname
    user_model.last_name = lastname

    hash_password = get_password_hash(password)  # 生成密码哈希
    user_model.hashed_password = hash_password
    user_model.is_active = True

    db.add(user_model)  # 添加用户到数据库
    db.commit()  # 提交事务

    msg = "User successfully created"  # 注册成功消息
    # 返回登录页面
    return templates.TemplateResponse("login.html", {"request": request, "msg": msg})
