from app.database import get_db
from app.auth.schemas import UserRegister,UserLogin,UserResponse,TokenResponse,RefreshToken
from fastapi import APIRouter,Response,HTTPException,Request,Depends
from sqlalchemy.orm import Session
from app.auth.models import User
from app.core.security import hash_pwd,verify_pwd,verify_token,create_access_token,create_refresh_token
from app.core.oauth import oauth
from app.core.rate_limit import limiter
from app.core.dependencies import oauth2_scheme
from app.core.security import verify_token
from app.services.token_blacklist import blacklist_token,is_blacklisted
from app.services.pkce import generate_pkce_pair

router=APIRouter(prefix="/auth",tags=["Authentication"])

@router.post("/register",response_model=UserResponse)
@limiter.limit("3/minute;5/day")
def register(request:Request,response:Response,info:UserRegister,db:Session=Depends(get_db)):
    existing_user=db.query(User).filter(User.email==info.email).first()
    if existing_user:
        raise HTTPException(status_code=401,detail="User already exists!")
    hashed=hash_pwd(info.password)
    new_user=User(email=info.email,password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(request: Request,response:Response, info: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == info.email).first()

    if not user or not verify_pwd(info.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    return {
        "access_token": create_access_token({"sub": str(user.id)}),
        "refresh_token": create_refresh_token({"sub": str(user.id)}),
        "token_type": "bearer",
    }

@router.post("/logout")
def logout_user(data:RefreshToken,token:str=Depends(oauth2_scheme)):
    access_payload=verify_token(token,expected_type="access")
    refresh_payload=verify_token(data.refresh_token,expected_type="refresh")
    blacklist_token(access_payload)
    blacklist_token(refresh_payload)
    return {"message":"Logged out successfully"}
    


@router.post("/refresh")
def refresh_token(data:RefreshToken):
    payload=verify_token(token=data.refresh_token,expected_type="refresh")

    if is_blacklisted(payload["jti"]):
        raise HTTPException(status_code=401,detail="token revoked!")

    blacklist_token(payload=payload)
    return {
        "access_token":create_access_token({"sub":payload["sub"]}),
        "refresh_token":create_refresh_token({"sub":payload["sub"]})
    }

@router.get("/google/login")
async def google_login(request:Request):
    code_verifier,code_challenge=generate_pkce_pair()
    request.session["pkce_verifier"]=code_verifier
    redirect_uri=request.url_for("google_callback")
    return await oauth.google.authorize_redirect(
        request,redirect_uri,
        code_challenge=code_challenge,
        code_challenge_method="S256"
        )

@router.get("/google/callback")
async def google_callback(request:Request,db:Session=Depends(get_db)):
    code_verifier=request.session.get("pkce_verifier")
    if not code_verifier:
        return HTTPException(status_code=400,detail="missing pkce verifier")
    try:
        token= await oauth.google.authorize_access_token(request,code_verifier=code_verifier)
    except Exception as e:
        print("exception ",repr(e))
        raise HTTPException(status_code=400,detail="Google authentication failed")

    user_info=token.get("userinfo")
    print(user_info)
    if not user_info or not user_info.get("email"):
        raise HTTPException(status_code=400,detail="could not fetch user information from google")

    email=user_info["email"]

    user=db.query(User).filter(User.email==email).first()
    if not user:
        user=User(email=email,password=None)
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token=create_access_token({"sub":str(user.id)})
    refresh_token=create_refresh_token({"sub":str(user.id)})

    return{
        "access_token":access_token,
        "refresh_token":refresh_token,
        "token_type":"bearer"
    }

